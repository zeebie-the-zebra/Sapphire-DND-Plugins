#!/usr/bin/env python3
"""
verify_plugin.py - Verify a signed plugin locally before shipping.

Usage:
  python verify_plugin.py path/to/plugin
  python verify_plugin.py                   # verifies all subfolders

Requires public_key.pem in the same directory.
"""

import base64
import hashlib
import json
import sys
from pathlib import Path
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

PUBLIC_KEY_FILE = Path("public_key.pem")
SIGNABLE_EXTENSIONS = {".py", ".json", ".js", ".css", ".html", ".md"}


def load_public_key():
    if not PUBLIC_KEY_FILE.exists():
        print("public_key.pem not found.")
        sys.exit(1)
    return load_pem_public_key(PUBLIC_KEY_FILE.read_bytes())


def hash_file(path: Path) -> str:
    """SHA256 hex digest, CRLF-normalized, with sha256: prefix to match Sapphire."""
    content = path.read_bytes().replace(b'\r\n', b'\n')
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def verify_plugin(plugin_dir: Path, public_key) -> bool:
    sig_path = plugin_dir / "plugin.sig"
    if not sig_path.exists():
        print(f"UNSIGNED — no plugin.sig found: {plugin_dir}")
        return False

    try:
        sig_data = json.loads(sig_path.read_text())
        manifest: dict = sig_data["files"]
        signature = base64.b64decode(sig_data["signature"])
    except Exception as e:
        print(f"CORRUPT sig file in {plugin_dir}: {e}")
        return False

    # Re-verify signature over payload (everything except signature field)
    payload = {k: v for k, v in sig_data.items() if k != "signature"}
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    try:
        public_key.verify(signature, payload_bytes)
    except InvalidSignature:
        print(f"TAMPERED — signature invalid: {plugin_dir}")
        return False

    # Check every file in the manifest still matches
    for rel_path, expected_hash in manifest.items():
        file_path = plugin_dir / rel_path
        if not file_path.exists():
            print(f"TAMPERED — missing file: {rel_path} in {plugin_dir}")
            return False
        if hash_file(file_path) != expected_hash:
            print(f"TAMPERED — file modified: {rel_path} in {plugin_dir}")
            return False

    # Check for extra signable files not in the manifest
    for file_path in sorted(plugin_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.name == "plugin.sig":
            continue
        if "__pycache__" in file_path.parts:
            continue
        if file_path.suffix.lower() in SIGNABLE_EXTENSIONS:
            rel = file_path.relative_to(plugin_dir).as_posix()
            if rel not in manifest:
                print(f"TAMPERED — unlisted file found: {rel} in {plugin_dir}")
                return False

    print(f"VALID — {len(manifest)} files verified: {plugin_dir}")
    return True


def main():
    public_key = load_public_key()

    if len(sys.argv) > 1:
        targets = [Path(arg) for arg in sys.argv[1:]]
    else:
        targets = sorted(p for p in Path(".").iterdir() if p.is_dir() and not p.name.startswith("."))
        if not targets:
            print("No plugin folders found.")
            sys.exit(1)

    passed = sum(verify_plugin(t, public_key) for t in targets)
    print(f"\n{passed}/{len(targets)} plugin(s) verified successfully.")


if __name__ == "__main__":
    main()
