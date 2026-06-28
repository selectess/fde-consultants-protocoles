"""License fulfillment — the last mile after a paid Polar order.

Takes a freshly minted ed25519 Modex license and:
  1. PERSISTS it to an append-only JSONL ledger, idempotently keyed on the
     Polar order id (Polar retries webhooks — an order is fulfilled once).
  2. DELIVERS it to the customer by email.
  3. Leaves an AUDIT trail — every ledger record IS an audit entry.

Design — mirrors polar_billing.py: INERT BY DEFAULT, activates via env, never
loses a license. With no MODEX_SMTP_HOST set, email delivery is DEFERRED
(recorded as pending, the license is already safely persisted) instead of
failing. Set the SMTP_* envs to turn on real delivery; no code change.

Env:
  MODEX_LICENSE_STORE   ledger path (default: modex/.data/licenses.jsonl)
  MODEX_SMTP_HOST       SMTP server — when unset, delivery is deferred
  MODEX_SMTP_PORT       default 587
  MODEX_SMTP_USER       optional auth user
  MODEX_SMTP_PASSWORD   optional auth password
  MODEX_SMTP_FROM       From: header (default: MODEX_SMTP_USER or no-reply@modex)
  MODEX_SMTP_STARTTLS   "false" to disable STARTTLS (default on)
"""
from __future__ import annotations

import json
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Union

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORE = REPO_ROOT / "modex" / ".data" / "licenses.jsonl"

PathLike = Union[str, Path]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _store_path(store_path: Optional[PathLike] = None) -> Path:
    return Path(store_path or os.environ.get("MODEX_LICENSE_STORE", str(DEFAULT_STORE)))


def find_by_order(order_id: Optional[str], store_path: Optional[PathLike] = None) -> Optional[dict]:
    """Return the first ledger record for `order_id`, or None.

    First match == the original issuance (the ledger is append-only and
    chronological), which is what idempotency keys on.
    """
    if not order_id:
        return None
    p = _store_path(store_path)
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("order_id") == order_id and rec.get("event") == "fulfilled":
            return rec
    return None


def _append(record: dict, store_path: Optional[PathLike] = None) -> None:
    p = _store_path(store_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def deliver_email(to_email: str, license_obj: dict) -> dict:
    """Email the license. Returns {"status", "detail"}.

    DEFERRED (never raises) when no SMTP host is configured, so an
    undeliverable license is queued for later — not lost. A transport error is
    reported as "failed" (and the caller keeps the persisted license), never
    crashing fulfillment.
    """
    host = os.environ.get("MODEX_SMTP_HOST", "")
    if not host:
        return {"status": "deferred", "detail": "no MODEX_SMTP_HOST configured"}
    tier = license_obj.get("tier", "plugin")
    msg = EmailMessage()
    msg["Subject"] = f"Your Modex {tier} license"
    msg["From"] = os.environ.get(
        "MODEX_SMTP_FROM", os.environ.get("MODEX_SMTP_USER", "no-reply@modex")
    )
    msg["To"] = to_email
    msg.set_content(
        "Thank you for supporting Modex.\n\n"
        f"Your {tier} license is below as license.json — save it where the "
        "plugin expects it to unlock your tier.\n\n"
        + json.dumps(license_obj, indent=2)
        + "\n"
    )
    try:
        port = int(os.environ.get("MODEX_SMTP_PORT", "587"))
        user = os.environ.get("MODEX_SMTP_USER", "")
        password = os.environ.get("MODEX_SMTP_PASSWORD", "")
        use_tls = os.environ.get("MODEX_SMTP_STARTTLS", "true").lower() != "false"
        with smtplib.SMTP(host, port, timeout=20) as server:
            if use_tls:
                server.starttls(context=ssl.create_default_context())
            if user:
                server.login(user, password)
            server.send_message(msg)
        return {"status": "sent", "detail": f"delivered to {to_email}"}
    except Exception as exc:  # delivery must never crash fulfillment
        return {"status": "failed", "detail": str(exc)}


def fulfill(
    license_obj: dict,
    *,
    order_id: Optional[str],
    email: str,
    tier: Optional[str] = None,
    store_path: Optional[PathLike] = None,
) -> dict:
    """Persist + deliver + audit a minted license. Idempotent on `order_id`.

    Returns the ledger record, plus an `idempotent` flag (True when this order
    was already fulfilled — no second issuance is written). When a prior
    delivery was deferred/failed and SMTP is now configured, a single
    redelivery is attempted and audited.
    """
    existing = find_by_order(order_id, store_path)
    if existing:
        prior = (existing.get("delivery") or {}).get("status")
        if prior in ("deferred", "failed"):
            redelivery = deliver_email(email, license_obj)
            if redelivery["status"] == "sent":
                _append(
                    {
                        "event": "redelivered",
                        "order_id": order_id,
                        "license_id": existing.get("license_id"),
                        "email": email,
                        "redelivered_at": _now(),
                        "delivery": redelivery,
                    },
                    store_path,
                )
                existing = {**existing, "delivery": redelivery}
        return {**existing, "idempotent": True}

    delivery = deliver_email(email, license_obj)
    record = {
        "event": "fulfilled",
        "order_id": order_id,
        "license_id": license_obj.get("license_id"),
        "email": email,
        "tier": tier or license_obj.get("tier"),
        "fulfilled_at": _now(),
        "license": license_obj,
        "delivery": delivery,
    }
    _append(record, store_path)
    return {**record, "idempotent": False}
