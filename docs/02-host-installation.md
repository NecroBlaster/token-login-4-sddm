# Host installation

The host is the Linux machine running SDDM.

## Install dependencies on Arch Linux

```bash
sudo pacman -S --needed python python-pyserial python-cryptography gcc pam
```

## Install the PAM helper

```bash
sudo install -m 0755 host/pam-helper/pam-ed25519-token /usr/local/libexec/pam-ed25519-token
```

## Install host configuration

```bash
sudo mkdir -p /etc/ed25519-token-auth/keys
sudo install -m 0644 host/config/host.conf.example /etc/ed25519-token-auth/host.conf
```

## Install the user's public key

```bash
sudo install -m 0644 example_user.pub /etc/ed25519-token-auth/keys/example_user.pub
sudo chown root:root /etc/ed25519-token-auth/keys/example_user.pub
sudo chmod 0644 /etc/ed25519-token-auth/keys/example_user.pub
```

The filename must match the Linux user account:

```text
/etc/ed25519-token-auth/keys/<username>.pub
```

## Install the udev rule

```bash
sudo cp host/udev/70-ed25519-token.rules.example /etc/udev/rules.d/70-ed25519-token.rules
sudo nano /etc/udev/rules.d/70-ed25519-token.rules
```

Replace `CHANGE_ME_TOKEN_SERIAL` with the actual token USB serial.

Reload udev:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the token and check:

```bash
ls -l /dev/ed25519-token
```

## Install the PAM service

```bash
sudo install -m 0644 host/pam/sddm-token.arch /etc/pam.d/sddm-token
```

Do not modify `/etc/pam.d/sddm` during initial testing.
