#!/usr/bin/env python3
"""Tests Dynatrace registry access for tenant qmp22335 using DT_TOKEN from .env.

Requires only the standard library. Never prints the token.
"""
import base64
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV_ID = "qmp22335"
HOST = f"{ENV_ID}.live.dynatrace.com"
BASE = f"https://{HOST}"

ACCEPT = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])
REPOS = [
    "linux/oneagent",
    "linux/oneagent-codemodules",
    "linux/oneagent-codemodules-musl",
    "linux/activegate",
]
CODEMODULE_TAGS = ["all", "java", "nodejs", "go", "apache", "nginx", "php", "dotnet"]


def load_token():
    """Read DT_TOKEN from .env next to this script, falling back to the environment."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, sep, value = line.partition("=")
            if sep and key.strip() == "DT_TOKEN":
                return value.strip().strip("'\"")
    elif "DT_TOKEN" not in os.environ:
        sys.exit("Missing .env. Create it with a line: DT_TOKEN=<token>  (then chmod 600 .env)")
    return os.environ.get("DT_TOKEN", "")


def request(path, auth, accept=None, timeout=30):
    """Return (status, headers). Raises URLError if the host is unreachable."""
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", "Basic " + auth)
    if accept:
        req.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers
    except urllib.error.HTTPError as e:
        return e.code, e.headers


def main():
    token = load_token()
    if not token:
        sys.exit("DT_TOKEN is empty in .env")
    auth = base64.b64encode(f"{ENV_ID}:{token}".encode()).decode()

    print(f"Registry: {HOST}")

    try:
        status, _ = request("/v2/", auth, timeout=20)
    except (urllib.error.URLError, OSError) as e:
        print(f"[FAIL] Cannot reach {HOST}: {e}")
        return 2
    if status == 200:
        print("[ OK ] Auth succeeded")
    elif status == 401:
        print("[FAIL] 401: token invalid/expired or missing PaaS (Installer download) scope")
        return 3
    else:
        print(f"[FAIL] HTTP {status} on /v2/")
        return 3
    print()

    for repo in REPOS:
        print(f"=== {repo} ===")
        tags = CODEMODULE_TAGS if "codemodules" in repo else ["latest"]
        for tag in tags:
            try:
                status, headers = request(f"/v2/{repo}/manifests/{tag}", auth, accept=ACCEPT)
            except (urllib.error.URLError, OSError):
                status, headers = None, {}
            if status == 200:
                print(f"  [ OK ] {tag:<10} {headers.get('Docker-Content-Digest', '')}")
            else:
                print(f"  [ -- ] {tag:<10} HTTP {status or '?'}")
        print()

    print(f"Pull: docker pull {HOST}/linux/oneagent-codemodules-musl:all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
