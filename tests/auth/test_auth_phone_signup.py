import os
import sys
import argparse
import requests
from typing import Optional

# Configure API base URL (override with API_BASE_URL env var)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
AUTH_PREFIX = "/api/v1/auth"


def send_client_signup_otp(phone: str, api_base_url: Optional[str] = None) -> dict:
    """Trigger client phone signup to send OTP"""
    base = api_base_url or API_BASE_URL
    url = f"{base}{AUTH_PREFIX}/client/signup"
    payload = {"phone": phone}
    resp = requests.post(url, json=payload, timeout=30)
    try:
        data = resp.json()
    except Exception:
        data = {"text": resp.text}
    return {"status": resp.status_code, "data": data}


def verify_client_otp(phone: str, token: str, api_base_url: Optional[str] = None) -> dict:
    """Verify client OTP to complete auth flow and get tokens"""
    base = api_base_url or API_BASE_URL
    url = f"{base}{AUTH_PREFIX}/client/verify-otp"
    payload = {"phone": phone, "token": token}
    resp = requests.post(url, json=payload, timeout=30)
    try:
        data = resp.json()
    except Exception:
        data = {"text": resp.text}
    return {"status": resp.status_code, "data": data}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Test client phone signup OTP flow")
    sub = parser.add_subparsers(dest="command", required=True)

    s1 = sub.add_parser("send-otp", help="Send OTP to a phone number")
    s1.add_argument("phone", help="E.164 phone number, e.g. +12345550123")

    s2 = sub.add_parser("verify-otp", help="Verify an OTP code for a phone number")
    s2.add_argument("phone", help="E.164 phone number, e.g. +12345550123")
    s2.add_argument("token", help="OTP code received via SMS")

    args = parser.parse_args(argv)

    if args.command == "send-otp":
        result = send_client_signup_otp(args.phone)
    else:
        result = verify_client_otp(args.phone, args.token)

    status = result.get("status")
    print(f"HTTP {status}")
    print(result.get("data"))

    # Return non-zero on failure
    return 0 if 200 <= (status or 500) < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
