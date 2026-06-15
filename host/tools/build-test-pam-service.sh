#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
gcc "$SCRIPT_DIR/test-pam-service.c" -o /tmp/test-pam-service -lpam

echo "Built /tmp/test-pam-service"
echo "Example: sudo /tmp/test-pam-service sddm-token example_user"
