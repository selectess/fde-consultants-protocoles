"""Polar webhook handler — mints a signed ed25519 Modex license on a paid order.

Secure by construction: verifies the Standard Webhooks signature that Polar sends
BEFORE acting, and is fail-closed — if POLAR_WEBHOOK_SECRET is unset or the
signature is invalid, every event is rejected with 401 and no license is minted.

This is the production-ready counterpart to the Stripe reference handler
(stripe_webhook.py). Our live checkout runs on Polar, so this is the one to deploy.

Deployment (chef, after Polar KYC):
  1. Polar -> Settings -> Webhooks -> add endpoint, copy the signing secret.
  2. Run with POLAR_WEBHOOK_SECRET=<secret> MODEX_PRIVATE_KEY_PATH=<key> on a host.
  3. A paid $6 (Founding -> plugin) or $260 (Collective -> collective) order then
     auto-mints, persists, emails and audits the license (see modex.fulfillment).
     Email stays DEFERRED until MODEX_SMTP_HOST is set — the license is always
     persisted first, never lost.
"""
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from modex.license import generate_license  # noqa: E402
from modex.fulfillment import fulfill as fulfill_license, find_by_order  # noqa: E402

POLAR_WEBHOOK_SECRET = os.environ.get("POLAR_WEBHOOK_SECRET", "")
PRIVATE_KEY_PATH = Path(os.environ.get(
    "MODEX_PRIVATE_KEY_PATH",
    str(REPO_ROOT / "modex" / ".keys" / "modex_private.key"),
))
PORT = int(os.environ.get("PORT", "8081"))
TOLERANCE_SECONDS = 5 * 60

# Polar product name -> Modex offline-license tier.
# Subscriptions (MCP Cloud) are access grants, not offline licenses -> not here.
PRODUCT_TIER = {
    "Modex — Founding License": "plugin",
    "Modex Collective": "collective",
}


def verify_signature(secret: str, headers, body: bytes) -> bool:
    """Verify a Standard Webhooks (Polar) signature. Fail-closed on anything off."""
    if not secret:
        return False
    wid = headers.get("webhook-id")
    wts = headers.get("webhook-timestamp")
    wsig = headers.get("webhook-signature")
    if not (wid and wts and wsig):
        return False
    try:
        if abs(time.time() - int(wts)) > TOLERANCE_SECONDS:
            return False  # replay-window guard
    except (ValueError, TypeError):
        return False
    key = secret.split("_", 1)[1] if secret.startswith("whsec_") else secret
    try:
        key_bytes = base64.b64decode(key)
    except Exception:
        key_bytes = key.encode()
    signed = f"{wid}.{wts}.{body.decode('utf-8')}".encode("utf-8")
    expected = base64.b64encode(
        hmac.new(key_bytes, signed, hashlib.sha256).digest()
    ).decode("utf-8")
    for part in wsig.split():
        candidate = part.split(",", 1)[-1]  # parts look like "v1,<base64>"
        if hmac.compare_digest(candidate, expected):
            return True
    return False


def handle_order_paid(event: dict, store_path=None) -> Optional[dict]:
    """On a paid order for a license product, mint, fulfill, and return the license.

    Fulfillment (persist + email + audit) runs as a side effect via
    modex.fulfillment.fulfill — idempotent on the Polar order id, so a retried
    webhook never double-issues. The pristine signed license dict is returned
    unchanged (so its ed25519 signature still verifies).
    """
    data = event.get("data", {})
    product = data.get("product") or {}
    product_name = product.get("name") or data.get("product_name", "")
    customer = data.get("customer") or {}
    email = customer.get("email") or data.get("customer_email")
    order_id = data.get("id")
    tier = PRODUCT_TIER.get(product_name)
    if tier is None:
        return None  # subscription / cloud / unknown -> no offline license
    if not email:
        raise ValueError("paid order has no customer email")
    # Idempotency: a retried webhook returns the SAME already-issued license,
    # never a freshly minted throwaway (minting generates a new id each call).
    prior = find_by_order(order_id, store_path)
    if prior and prior.get("license"):
        return prior["license"]
    license_obj = generate_license(
        email=email,
        tier=tier,
        stripe_payment_id=order_id,
        private_key_path=PRIVATE_KEY_PATH if PRIVATE_KEY_PATH.exists() else None,
    )
    # Last mile: persist the license, email it to `email`, write an audit record.
    fulfill_license(license_obj, order_id=order_id, email=email, tier=tier, store_path=store_path)
    return license_obj


class PolarWebhookHandler(BaseHTTPRequestHandler):
    """Fail-closed HTTP handler for Polar webhook events."""

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if not verify_signature(POLAR_WEBHOOK_SECRET, self.headers, body):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid or missing signature"}')
            return
        try:
            event = json.loads(body)
            result = (
                handle_order_paid(event)
                if event.get("type") in ("order.paid", "order.updated")
                else None
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "license_id": result.get("license_id") if result else None,
            }).encode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))

    def log_message(self, format, *args):  # noqa: A002 — silence default stderr logging
        pass


def main():
    if not POLAR_WEBHOOK_SECRET:
        print(
            "WARNING: POLAR_WEBHOOK_SECRET unset — handler rejects every event "
            "(fail-closed). Set it from Polar -> Settings -> Webhooks.",
            file=sys.stderr,
        )
    HTTPServer(("", PORT), PolarWebhookHandler).serve_forever()


if __name__ == "__main__":
    main()
