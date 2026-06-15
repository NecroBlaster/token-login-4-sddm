# Linux USB gadget token device

This document describes the reference token implementation for Linux USB gadget devices.

## Requirements

- Linux device mode support;
- `dwc2` or equivalent USB device controller driver;
- `libcomposite`;
- Python 3;
- Python `serial` module;
- Python `cryptography` module.

## Install files

```bash
sudo install -m 0755 device/linux-gadget/ed25519-token-gadget /usr/local/sbin/ed25519-token-gadget
sudo install -m 0755 device/linux-gadget/ed25519-token-daemon /usr/local/libexec/ed25519-token-daemon
```

## Install configuration

```bash
sudo mkdir -p /etc/ed25519-token-auth
sudo install -m 0644 device/config/allowed-users.example /etc/ed25519-token-auth/allowed-users
sudo install -m 0644 device/config/device.conf.example /etc/ed25519-token-auth/device.conf
```

## Set a unique token serial

Edit the device configuration before starting the gadget:

```bash
sudo nano /etc/ed25519-token-auth/device.conf
```

Replace:

```ini
serial = CHANGE_ME_TOKEN_SERIAL
```

with a unique value for this token.

## Generate keypair

```bash
sudo device/tools/init-token-keys.sh
```

The token private key remains on the token device.

## Start services

```bash
sudo install -m 0644 device/linux-gadget/systemd/ed25519-token-gadget.service /etc/systemd/system/ed25519-token-gadget.service
sudo install -m 0644 device/linux-gadget/systemd/ed25519-token-daemon.service /etc/systemd/system/ed25519-token-daemon.service
sudo systemctl daemon-reload
sudo systemctl enable --now ed25519-token-gadget.service
sudo systemctl enable --now ed25519-token-daemon.service
```
