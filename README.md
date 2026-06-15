# SDDM Ed25519 Token Auth

<p align="center">
  <img src="cover.png" alt="Project Cover" width="600">
</p>

SDDM Ed25519 Token Auth adds a separate token-based login path to SDDM using an external Ed25519 challenge-response token.

The normal password login path is kept intact. The token path uses a dedicated PAM service called `sddm-token`, so password authentication and token authentication remain separated.

The Raspberry Pi Zero 2 W is used as the reference token device, but the design is not Raspberry Pi-specific. Any device can be used if it exposes a USB serial interface and implements the JSON challenge-response protocol described in `docs/01-protocol.md`.

## Security warning

This is an experimental authentication project. Test it in a VM, spare machine, or recoverable environment before using it on a daily system.

Before restarting SDDM, always make sure that:

- you can access a TTY with `Ctrl` + `Alt` + `F3`;
- the normal password login still works;
- you have backups of the original SDDM binaries and greeter theme;
- no private key has been copied to the host or committed to Git.

Never publish:

- token private keys;
- real user public keys if you consider them sensitive;
- real SDDM logs;
- screenshots containing usernames, hostnames, IP addresses, serial numbers, or personal details.

## Architecture

Normal password login:

```text
sddm.login(user, password, sessionIndex)
    -> /etc/pam.d/sddm
```

Token login:

```text
sddm.loginToken(user, sessionIndex)
    -> sddm-helper --pam-service sddm-token
    -> /etc/pam.d/sddm-token
    -> pam-ed25519-token
    -> /dev/ed25519-token
    -> external token signs a challenge
    -> host verifies the Ed25519 signature
```

The token never sends a password to the host. It signs a short-lived challenge that is bound to the user, PAM service, and protocol prefix.

## Requirements

### Host system

A Linux system using SDDM.

Reference environment:

- Arch Linux;
- SDDM 0.21.x-style source tree;
- Qt 6 SDDM greeter;
- Python 3;
- `python-pyserial`;
- `python-cryptography`;
- PAM development headers for the optional PAM test tool.

### Token device

Reference device:

- Raspberry Pi Zero 2 W;
- Linux USB gadget support;
- `dwc2`;
- `libcomposite`;
- USB CDC ACM serial function.

Other devices are possible if they implement the same protocol over USB serial.

## Step-by-step installation

The commands below use generic names. Replace placeholders such as `example_user`, `token-device.local`, and `CHANGE_ME_TOKEN_SERIAL` with values that match your environment.

### Step 1 — Prepare the token device

On the token device, install the runtime dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-serial python3-cryptography
```

Create a restricted service user:

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin edtoken
```

Install the token configuration directory:

```bash
sudo mkdir -p /etc/ed25519-token-auth
sudo install -m 0644 device/config/allowed-users.example /etc/ed25519-token-auth/allowed-users
sudo install -m 0644 device/config/device.conf.example /etc/ed25519-token-auth/device.conf
```

Edit the device configuration and set a unique USB serial:

```bash
sudo nano /etc/ed25519-token-auth/device.conf
```

At minimum, replace:

```ini
serial = CHANGE_ME_TOKEN_SERIAL
```

Then edit the allowed users file:

```bash
sudo nano /etc/ed25519-token-auth/allowed-users
```

Example:

```text
example_user
```

Generate the token keypair:

```bash
sudo device/tools/init-token-keys.sh
```

Install the Linux gadget scripts:

```bash
sudo install -m 0755 device/linux-gadget/ed25519-token-gadget /usr/local/sbin/ed25519-token-gadget
sudo install -m 0755 device/linux-gadget/ed25519-token-daemon /usr/local/libexec/ed25519-token-daemon
```

Install the systemd services:

```bash
sudo install -m 0644 device/linux-gadget/systemd/ed25519-token-gadget.service /etc/systemd/system/ed25519-token-gadget.service
sudo install -m 0644 device/linux-gadget/systemd/ed25519-token-daemon.service /etc/systemd/system/ed25519-token-daemon.service
sudo systemctl daemon-reload
sudo systemctl enable --now ed25519-token-gadget.service
sudo systemctl enable --now ed25519-token-daemon.service
```

For Raspberry Pi Zero / Zero W / Zero 2 W devices, also read:

```text
docs/06-raspberry-pi-zero-2w-reference.md
```

### Step 2 — Export the public key from the token

From the host machine:

```bash
scp pi@token-device.local:/etc/ed25519-token-auth/public.key /tmp/example_user.pub
```

Use the correct SSH user and hostname for your token device.

### Step 3 — Install the host dependencies

On the host system:

```bash
sudo pacman -S --needed python python-pyserial python-cryptography gcc pam
```

For non-Arch distributions, install equivalent Python, serial, cryptography, PAM, and compiler packages.

### Step 4 — Install the host PAM helper

```bash
sudo mkdir -p /usr/local/libexec
sudo install -m 0755 host/pam-helper/pam-ed25519-token /usr/local/libexec/pam-ed25519-token
```

Install the host configuration:

```bash
sudo mkdir -p /etc/ed25519-token-auth/keys
sudo install -m 0644 host/config/host.conf.example /etc/ed25519-token-auth/host.conf
```

Install the user's public key:

```bash
sudo install -m 0644 /tmp/example_user.pub /etc/ed25519-token-auth/keys/example_user.pub
sudo chown root:root /etc/ed25519-token-auth/keys/example_user.pub
```

The public key filename must match the Linux username:

```text
/etc/ed25519-token-auth/keys/<username>.pub
```

### Step 5 — Install the udev rule

Copy the example rule:

```bash
sudo cp host/udev/70-ed25519-token.rules.example /etc/udev/rules.d/70-ed25519-token.rules
```

Edit it and replace `CHANGE_ME_TOKEN_SERIAL` with the USB serial configured on the token:

```bash
sudo nano /etc/udev/rules.d/70-ed25519-token.rules
```

Reload udev:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the token and check:

```bash
ls -l /dev/ed25519-token
```

### Step 6 — Install the dedicated PAM service

```bash
sudo install -m 0644 host/pam/sddm-token.arch /etc/pam.d/sddm-token
```

Do not replace `/etc/pam.d/sddm`. The normal SDDM password path must remain available.

### Step 7 — Test PAM without the graphical greeter

Build the test tool:

```bash
host/tools/build-test-pam-service.sh
```

Run a test:

```bash
sudo /tmp/test-pam-service sddm-token example_user
```

Expected result:

```text
PAM OK
```

If this fails, do not patch or restart SDDM yet. See `docs/08-troubleshooting.md`.

### Step 8 — Patch and build SDDM

Clone SDDM:

```bash
git clone https://github.com/sddm/sddm.git
cd sddm
```

Apply the patch script from this repository:

```bash
python3 /path/to/sddm-ed25519-token-auth/sddm/scripts/apply-token-patch.py
```

Build SDDM:

```bash
cmake -B build -S . \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DCMAKE_INSTALL_LIBEXECDIR=lib/sddm \
  -DBUILD_WITH_QT6=ON \
  -DBUILD_MAN_PAGES=OFF

cmake --build build -j"$(nproc)"
```

Back up the installed SDDM binaries before installing the patched build:

```bash
sudo mkdir -p /root/sddm-backup-before-ed25519-token
sudo cp -a /usr/bin/sddm \
           /usr/bin/sddm-greeter \
           /usr/bin/sddm-greeter-qt6 \
           /usr/lib/sddm/sddm-helper \
           /root/sddm-backup-before-ed25519-token/
```

Install the patched build:

```bash
sudo cmake --install build
```

Confirm that the helper contains the new argument:

```bash
strings /usr/lib/sddm/sddm-helper | grep -E 'pam-service|sddm-token'
```

### Step 9 — Add a token button to a greeter

The backend patch is generic. The visual integration depends on the greeter QML theme.

Any SDDM greeter can be adapted if it can call:

```qml
sddm.loginToken(username, sessionIndex)
```

For Breeze-like themes, use:

```bash
sudo python3 greeters/adapters/breeze/patch-breeze-token-button.py --theme-dir /path/to/theme
```

Example:

```bash
sudo python3 greeters/adapters/breeze/patch-breeze-token-button.py --theme-dir /path/to/sddm-theme
```

Before restarting SDDM, preview the theme if your environment supports test mode:

```bash
sddm-greeter-qt6 --test-mode --theme /path/to/theme
```

### Step 10 — Test login

Restarting SDDM will end the graphical session:

```bash
sudo systemctl restart sddm.service
```

Test in this order:

1. normal password login;
2. logout;
3. token login;
4. logout;
5. unplug the token;
6. confirm that token login fails;
7. confirm that normal password login still works.

## Recovery

If the greeter breaks, switch to a TTY:

```text
Ctrl + Alt + F3
```

Restore SDDM binaries:

```bash
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm /usr/bin/sddm
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-greeter /usr/bin/sddm-greeter
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-greeter-qt6 /usr/bin/sddm-greeter-qt6
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-helper /usr/lib/sddm/sddm-helper
sudo systemctl restart sddm.service
```

For more recovery procedures, see:

```text
docs/07-recovery.md
```

## Repository structure glossary

| Path | Purpose |
|---|---|
| `host/` | Files installed on the Linux machine running SDDM. |
| `host/pam-helper/` | PAM helper that talks to the external token and verifies Ed25519 signatures. |
| `host/pam/` | PAM service definition for `sddm-token`. |
| `host/udev/` | udev rules used to create `/dev/ed25519-token`. |
| `host/config/` | Host-side configuration examples. |
| `host/tools/` | Test tools for validating PAM without using the graphical login screen. |
| `device/` | Token-side implementations. |
| `device/linux-gadget/` | Reference implementation for Linux USB gadget devices. |
| `device/config/` | Device-side configuration examples. |
| `device/profiles/` | Hardware-specific configuration examples. |
| `sddm/` | SDDM patching and build helper files. |
| `greeters/` | QML components and greeter-specific integration notes. |
| `docs/` | Detailed technical documentation. |
| `examples/` | Example configuration snippets and naming conventions. |

## Current limitations

- The SDDM patch is version-sensitive and should be reviewed against the target SDDM source tree before installation.
- Greeter integration is not visually universal; each QML theme may require a small adapter.
- The reference token device uses USB CDC ACM serial only.
- This is an alternative login path, not a complete multi-factor authentication solution by itself.
- Token theft may allow token login for authorised users unless additional local policy is added.

## Licence

This project is distributed under the GPL-2.0-or-later licence. See `LICENSE`.
