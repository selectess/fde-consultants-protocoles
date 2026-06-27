#!/usr/bin/env python3
"""Stripe webhook handler for Modex Plugin license generation.

In production, this would be deployed to a serverless function (Cloud Run,
Lambda, etc.) and exposed via HTTPS.

Usage:
    python -m modex.stripe_webhook
    # or import and call: handle_payment_intent_succeeded(event)

This handler:
1. Receives a Stripe webhook (payment_intent.succeeded)
2. Generates a license.json with ed25519 signature
3. Stores the license in a database (TODO: production)
4. Emails the license to the customer (TODO: production)

For local development:
    python -m modex.stripe_webhook --simulate stripe
    # Simulates a payment_intent.succeeded event with test data
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

# Optional: Stripe SDK (recommended for production)
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

# Local imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from modex.license import generate_license


# Configuration (set via environment in production)
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "sk_test_PLACEHOLDER")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_PLACEHOLDER")
PRIVATE_KEY_PATH = Path(os.environ.get(
    "MODEX_PRIVATE_KEY_PATH",
    str(REPO_ROOT / "modex" / ".keys" / "modex_private.key")
))
PORT = int(os.environ.get("PORT", "8080"))


def handle_payment_intent_succeeded(event_data: dict) -> dict:
    """Handle a Stripe payment_intent.succeeded event.

    Args:
        event_data: Stripe event dict with payment_intent, customer, etc.

    Returns:
        dict with the generated license.
    """
    payment_intent = event_data.get("data", {}).get("object", {})
    payment_id = payment_intent.get("id")
    customer_email = payment_intent.get("receipt_email") or payment_intent.get(
        "metadata", {}
    ).get("email")
    if not customer_email:
        raise ValueError("No customer email in payment_intent")
    tier = payment_intent.get("metadata", {}).get("tier", "plugin")
    license_obj = generate_license(
        email=customer_email,
        tier=tier,
        stripe_payment_id=payment_id,
        private_key_path=PRIVATE_KEY_PATH if PRIVATE_KEY_PATH.exists() else None,
    )
    # TODO (production):
    # 1. Store license in database (PostgreSQL)
    # 2. Email license to customer via SendGrid/Postmark
    # 3. Log to audit trail (CloudWatch, Stackdriver)
    return license_obj


class StripeWebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for Stripe webhook events."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            event = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid JSON"}')
            return
        # Verify webhook signature (in production)
        # stripe.Webhook.construct_event(body, sig_header, STRIPE_WEBHOOK_SECRET)
        event_type = event.get("type")
        try:
            if event_type == "payment_intent.succeeded":
                license_obj = handle_payment_intent_succeeded(event)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "license_id": license_obj["license_id"]}).encode())
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ignored", "event_type": event_type}).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "modex-stripe-webhook"}).encode())


def main():
    """CLI: start the webhook server or simulate an event."""
    import argparse
    parser = argparse.ArgumentParser(description="Modex Stripe webhook")
    parser.add_argument("--simulate", default=None, help="Simulate event (stripe)")
    parser.add_argument("--server", action="store_true", help="Start HTTP server")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    if args.simulate == "stripe":
        # Simulate a Stripe payment_intent.succeeded event
        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_simulated_123",
                    "receipt_email": "test@example.com",
                    "metadata": {"tier": "plugin"},
                }
            },
        }
        try:
            license_obj = handle_payment_intent_succeeded(event)
            print(json.dumps(license_obj, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.server:
        server = HTTPServer(("0.0.0.0", args.port), StripeWebhookHandler)
        print(f"Modex Stripe webhook listening on port {args.port}")
        print(f"POST / for Stripe events")
        print(f"GET / for health check")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()