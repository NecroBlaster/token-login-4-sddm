# Recovery

## Switch to TTY

If the graphical login screen breaks:

```text
Ctrl + Alt + F3
```

Log in using the normal user account.

## Restore SDDM binaries

```bash
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm /usr/bin/sddm
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-greeter /usr/bin/sddm-greeter
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-greeter-qt6 /usr/bin/sddm-greeter-qt6
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-helper /usr/lib/sddm/sddm-helper
sudo systemctl restart sddm.service
```

## Restore a theme backup

```bash
sudo rm -rf /path/to/theme
sudo cp -a /path/to/theme.backup /path/to/theme
sudo systemctl restart sddm.service
```

## Keyboard layout issue

If the slash character `/` is not available in the TTY layout, move through directories step by step:

```bash
cd
cd ..
cd ..
cd usr
cd local
cd share
cd sddm
cd themes
```

The Unicode input sequence for `/` is often:

```text
Ctrl + Shift + U, then 2f, then Enter
```
