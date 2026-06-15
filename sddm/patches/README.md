# Static patch notes

This repository currently provides `sddm/scripts/apply-token-patch.py` as the primary patching method.

A static `.patch` file should be generated after testing against a specific SDDM source version:

```bash
python3 /path/to/sddm/scripts/apply-token-patch.py
git diff > sddm-login-token.patch
```

The generated patch should then be reviewed and committed with the exact SDDM version documented.
