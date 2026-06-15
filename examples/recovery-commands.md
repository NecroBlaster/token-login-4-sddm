# Recovery commands

Restore SDDM binaries from backup:

```bash
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm /usr/bin/sddm
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-greeter /usr/bin/sddm-greeter
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-greeter-qt6 /usr/bin/sddm-greeter-qt6
sudo cp -a /root/sddm-backup-before-ed25519-token/sddm-helper /usr/lib/sddm/sddm-helper
sudo systemctl restart sddm.service
```
