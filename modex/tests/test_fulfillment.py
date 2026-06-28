"""Tests for license fulfillment — persist, deliver, audit, idempotent."""
import json

from modex import fulfillment
from modex.license import generate_license


def _license(email="buyer@x.com", tier="plugin"):
    # No private_key_path -> a fresh keypair is generated (fine for tests).
    return generate_license(email=email, tier=tier, stripe_payment_id="ord_x")


def test_fulfill_persists_and_audits(tmp_path):
    store = tmp_path / "licenses.jsonl"
    lic = _license()
    out = fulfillment.fulfill(lic, order_id="ord_1", email="buyer@x.com",
                              tier="plugin", store_path=store)
    assert out["idempotent"] is False
    assert out["event"] == "fulfilled" and out["order_id"] == "ord_1"
    # Persisted as a single ledger line that doubles as the audit record.
    lines = store.read_text().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["license"]["license_id"] == lic["license_id"]
    assert rec["delivery"]["status"] == "deferred"  # no SMTP configured


def test_fulfill_is_idempotent_on_order_id(tmp_path):
    store = tmp_path / "licenses.jsonl"
    lic = _license()
    first = fulfillment.fulfill(lic, order_id="ord_1", email="buyer@x.com", store_path=store)
    second = fulfillment.fulfill(lic, order_id="ord_1", email="buyer@x.com", store_path=store)
    assert first["idempotent"] is False
    assert second["idempotent"] is True
    # A retried webhook must NOT append a second issuance.
    issuances = [l for l in store.read_text().splitlines()
                 if json.loads(l)["event"] == "fulfilled"]
    assert len(issuances) == 1


def test_find_by_order(tmp_path):
    store = tmp_path / "licenses.jsonl"
    assert fulfillment.find_by_order("nope", store_path=store) is None
    lic = _license()
    fulfillment.fulfill(lic, order_id="ord_7", email="z@z.com", store_path=store)
    rec = fulfillment.find_by_order("ord_7", store_path=store)
    assert rec and rec["license_id"] == lic["license_id"]


def test_smtp_delivery_via_fake(tmp_path, monkeypatch):
    sent = {}

    class _FakeSMTP:
        def __init__(self, host, port, timeout=20):
            sent["host"] = host
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def starttls(self, context=None):
            sent["tls"] = True
        def login(self, user, password):
            sent["user"] = user
        def send_message(self, msg):
            sent["to"] = msg["To"]

    monkeypatch.setattr(fulfillment.smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setenv("MODEX_SMTP_HOST", "smtp.test")
    monkeypatch.setenv("MODEX_SMTP_USER", "u@test")
    monkeypatch.setenv("MODEX_SMTP_PASSWORD", "pw")

    store = tmp_path / "licenses.jsonl"
    out = fulfillment.fulfill(_license(), order_id="ord_9", email="buyer@x.com", store_path=store)
    assert out["delivery"]["status"] == "sent"
    assert sent["to"] == "buyer@x.com" and sent["host"] == "smtp.test"


def test_redelivery_when_smtp_added_later(tmp_path, monkeypatch):
    store = tmp_path / "licenses.jsonl"
    lic = _license()
    # First fulfillment with no SMTP -> deferred.
    first = fulfillment.fulfill(lic, order_id="ord_3", email="buyer@x.com", store_path=store)
    assert first["delivery"]["status"] == "deferred"

    # SMTP now configured: a repeat (retried webhook) re-attempts delivery once.
    monkeypatch.setattr(fulfillment, "deliver_email",
                        lambda to, lo: {"status": "sent", "detail": "ok"})
    second = fulfillment.fulfill(lic, order_id="ord_3", email="buyer@x.com", store_path=store)
    assert second["idempotent"] is True
    assert second["delivery"]["status"] == "sent"
    # The redelivery is audited as its own ledger line.
    events = [json.loads(l)["event"] for l in store.read_text().splitlines()]
    assert events == ["fulfilled", "redelivered"]


def test_deliver_email_deferred_without_host(monkeypatch):
    monkeypatch.delenv("MODEX_SMTP_HOST", raising=False)
    out = fulfillment.deliver_email("a@b.com", {"tier": "plugin"})
    assert out["status"] == "deferred"
