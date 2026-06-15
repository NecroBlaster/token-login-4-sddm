#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/etc/ed25519-token-auth"
PRIVATE_KEY="$INSTALL_DIR/private.key"
PUBLIC_KEY="$INSTALL_DIR/public.key"

if [[ -e "$PRIVATE_KEY" ]]; then
    echo "Refusing to overwrite existing private key: $PRIVATE_KEY" >&2
    exit 1
fi

sudo mkdir -p "$INSTALL_DIR"

python3 - <<'PY'
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

install_dir = Path('/etc/ed25519-token-auth')
private_path = install_dir / 'private.key'
public_path = install_dir / 'public.key'

key = Ed25519PrivateKey.generate()
private_bytes = key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
)
public_bytes = key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)

private_path.write_bytes(private_bytes)
public_path.write_bytes(public_bytes)
PY

sudo chown root:root "$PUBLIC_KEY"
sudo chmod 0644 "$PUBLIC_KEY"

if id edtoken >/dev/null 2>&1; then
    sudo chown edtoken:edtoken "$PRIVATE_KEY"
else
    sudo chown root:root "$PRIVATE_KEY"
fi
sudo chmod 0400 "$PRIVATE_KEY"

echo "Created $PRIVATE_KEY and $PUBLIC_KEY"
