#!/usr/bin/env python3
"""Call EHunt data APIs with a user-owned AI API key.

The key is read from EHUNT_AI_KEY or supplied with --api-key. It is never
written to disk by this script.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://ehunt.ai"
ENDPOINTS = {
    "products": "/api/agent/data/products/list",
    "shops": "/api/agent/data/shops/list",
    "keywords": "/api/agent/data/keywords/research",
}


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.json and args.json_file:
        raise ValueError("Use either --json or --json-file, not both")
    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    elif args.json:
        payload = json.loads(args.json)
    else:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("Provide request JSON with --json, --json-file, or stdin")
        payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Request JSON must be an object")
    return payload


def call_api(
    resource: str,
    payload: dict[str, Any],
    api_key: str,
    base_url: str,
    timeout: float,
) -> dict[str, Any]:
    if resource not in ENDPOINTS:
        raise ValueError("Unsupported resource: {}".format(resource))
    if not api_key.startswith("eh_ai_"):
        raise ValueError("EHunt AI API key must start with eh_ai_")

    url = base_url.rstrip("/") + ENDPOINTS[resource]
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-EHUNT-AI-KEY": api_key,
            "User-Agent": "ehunt-ai-skills/1.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
            message = body.get("message") or body.get("detail") or raw
        except json.JSONDecodeError:
            message = raw or "HTTP {}".format(exc.code)
        raise RuntimeError("EHunt API request failed (HTTP {}): {}".format(exc.code, message)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("EHunt API request failed: {}".format(exc.reason)) from exc

    try:
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("EHunt API returned non-JSON content") from exc
    if not isinstance(body, dict):
        raise RuntimeError("EHunt API returned an unexpected response")
    if body.get("code") != 200:
        raise RuntimeError(
            "EHunt API error {}: {}".format(
                body.get("code", "unknown"),
                body.get("message", "request failed"),
            )
        )
    return body


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query EHunt products, shops, or keywords")
    parser.add_argument("resource", choices=sorted(ENDPOINTS))
    parser.add_argument("--json", help="Request JSON object")
    parser.add_argument("--json-file", help="Path to a UTF-8 JSON request file")
    parser.add_argument("--api-key", help="EHunt AI API key; defaults to EHUNT_AI_KEY")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("EHUNT_API_BASE_URL", DEFAULT_BASE_URL),
        help="EHunt site base URL",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--compact", action="store_true", help="Print compact JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = load_payload(args)
        api_key = (args.api_key or os.environ.get("EHUNT_AI_KEY", "")).strip()
        if not api_key:
            raise ValueError("Set EHUNT_AI_KEY or pass --api-key")
        result = call_api(args.resource, payload, api_key, args.base_url, args.timeout)
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.compact:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
