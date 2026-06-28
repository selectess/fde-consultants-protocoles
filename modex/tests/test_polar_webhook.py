"""Tests for the secure Polar webhook handler (signature + minting + fail-closed)."""
import base64
import hashlib
import hmac
import json
import time

from modex.polar_webhook import verify_signature, handle_order_paid

SECRET = "whsec_" + base64.b64encode(b"super-secret-key-bytes-0123456789").decode()


def _sign(secret, wid, wts, body):
    key = secret.split("_", 1)[1] if secret.startswith("whsec_") else secret
    key_bytes = base64.b64decode(key)
    signed = f"{wid}.{wts}.{body.decode()}".encode()
    return "v1," + base64.b64encode(hmac.new(key_bytes, signed, hashlib.sha256).digest()).decode()


def _headers(secret, body, ts=None):
    wid, wts = "msg_test", str(int(ts or time.time()))
    return {"webhook-id": wid, "webhook-timestamp": wts,
            "webhook-signature": _sign(secret, wid, wts, body)}


def test_valid_signature_accepted():
    body = b'{"type":"order.paid"}'
    assert verify_signature(SECRET, _headers(SECRET, body), body) is True


def test_tampered_body_rejected():
    body = b'{"type":"order.paid"}'
    headers = _headers(SECRET, body)
    assert verify_signature(SECRET, headers, b'{"type":"order.paid","x":1}') is False


def test_missing_secret_is_fail_closed():
    body = b"{}"
    assert verify_signature("", _headers(SECRET, body), body) is False


def test_stale_timestamp_rejected():
    body = b"{}"
    assert verify_signature(SECRET, _headers(SECRET, body, ts=time.time() - 3600), body) is False


def test_founding_order_mints_plugin_license(tmp_path):
    store = tmp_path / "licenses.jsonl"
    ev = {"type": "order.paid", "data": {"id": "ord_1",
          "product": {"name": "Modex — Founding License"}, "customer": {"email": "a@b.com"}}}
    lic = handle_order_paid(ev, store_path=store)
    assert lic and lic["tier"] == "plugin" and lic["email"] == "a@b.com"
    assert lic["signature"].startswith("ed25519:") and lic["stripe_payment_id"] == "ord_1"
    # fulfillment ran: license persisted + audited, delivery deferred (no SMTP)
    rec = json.loads(store.read_text().splitlines()[0])
    assert rec["event"] == "fulfilled" and rec["order_id"] == "ord_1"
    assert rec["license_id"] == lic["license_id"]
    assert rec["delivery"]["status"] == "deferred"


def test_collective_order_mints_collective_license(tmp_path):
    ev = {"type": "order.paid", "data": {"id": "ord_2",
          "product": {"name": "Modex Collective"}, "customer": {"email": "c@d.com"}}}
    lic = handle_order_paid(ev, store_path=tmp_path / "licenses.jsonl")
    assert lic and lic["tier"] == "collective"


def test_retried_webhook_returns_same_license(tmp_path):
    store = tmp_path / "licenses.jsonl"
    ev = {"type": "order.paid", "data": {"id": "ord_dup",
          "product": {"name": "Modex — Founding License"}, "customer": {"email": "a@b.com"}}}
    first = handle_order_paid(ev, store_path=store)
    second = handle_order_paid(ev, store_path=store)  # Polar retry
    assert first and second
    assert second["license_id"] == first["license_id"]  # same license, not re-minted
    issuances = [l for l in store.read_text().splitlines()
                 if json.loads(l)["event"] == "fulfilled"]
    assert len(issuances) == 1  # no double issue


def test_subscription_product_mints_no_license(tmp_path):
    ev = {"type": "order.paid", "data": {"id": "ord_3",
          "product": {"name": "MCP Cloud — Starter"}, "customer": {"email": "e@f.com"}}}
    assert handle_order_paid(ev, store_path=tmp_path / "licenses.jsonl") is None
