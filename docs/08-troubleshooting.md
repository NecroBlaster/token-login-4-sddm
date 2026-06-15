# Troubleshooting

## `/dev/ed25519-token` does not exist

Check USB detection:

```bash
lsusb
ls -l /dev/ttyACM*
```

Check the udev rule:

```bash
udevadm info -a -n /dev/ttyACM0 | less
```

Reload udev:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## PAM helper fails

Run it through the PAM test service first:

```bash
sudo /tmp/test-pam-service sddm-token example_user
```

Check configuration:

```bash
cat /etc/ed25519-token-auth/host.conf
ls -l /etc/ed25519-token-auth/keys/
```

## Token refuses the user

Check the token-side allowed users file:

```bash
cat /etc/ed25519-token-auth/allowed-users
```

Restart the token daemon after changing it:

```bash
sudo systemctl restart ed25519-token-daemon.service
```

## SDDM greeter does not show the button

Confirm which theme SDDM actually loaded:

```bash
journalctl -u sddm.service --no-pager --since "10 minutes ago" | grep -Ei 'theme|greeter|qml|error'
```

Check that the theme contains `loginToken`:

```bash
grep -RIn 'loginToken\|Token' /path/to/theme
```

## `loginToken` is not defined

The SDDM greeter binary may not be the patched one. Confirm:

```bash
strings /usr/lib/sddm/sddm-helper | grep -E 'pam-service|sddm-token'
```

Rebuild and reinstall the patched SDDM if required.
