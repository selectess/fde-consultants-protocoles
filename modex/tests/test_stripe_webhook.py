"""Tests for the Stripe reference webhook — mint + fulfill + idempotency."""
import json

from modex.stripe_webhook import handle_payment_intent_succeeded


def _event(payment_id="pi_1", email="buyer@x.com", tier="plugin"):
    return {"type": "payment_intent.succeeded",
            "data": {"object": {"id": payment_id, "receipt_email": email,
                                "metadata": {"tier": tier}}}}


def test_payment_mints_and_fulfills(tmp_path):
    store = tmp_path / "licenses.jsonl"
    lic = handle_payment_intent_succeeded(_event(), store_path=store)
    assert lic["tier"] == "plugin" and lic["email"] == "buyer@x.com"
    assert lic["signature"].startswith("ed25519:") and lic["stripe_payment_id"] == "pi_1"
    rec = json.loads(store.read_text().splitlines()[0])
    assert rec["event"] == "fulfilled" and rec["order_id"] == "pi_1"
    assert rec["delivery"]["status"] == "deferred"  # no SMTP in tests


def test_retried_payment_returns_same_license(tmp_path):
    store = tmp_path / "licenses.jsonl"
    first = handle_payment_intent_succeeded(_event(), store_path=store)
    second = handle_payment_intent_succeeded(_event(), store_path=store)  # Stripe retry
    assert second["license_id"] == first["license_id"]
    issuances = [l for l in store.read_text().splitlines()
                 if json.loads(l)["event"] == "fulfilled"]
    assert len(issuances) == 1


def test_missing_email_raises(tmp_path):
    ev = {"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_2"}}}
    try:
        handle_payment_intent_succeeded(ev, store_path=tmp_path / "l.jsonl")
        assert False, "expected ValueError"
    except ValueError:
        pass
