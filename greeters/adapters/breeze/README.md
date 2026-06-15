# Breeze greeter adapter

This adapter is intended for Breeze-like SDDM QML themes.

It is not a universal QML patcher. Always inspect the resulting theme before restarting SDDM.

Usage:

```bash
sudo python3 patch-breeze-token-button.py --theme-dir /path/to/theme
```

The script expects the theme directory to contain:

```text
Login.qml
Main.qml
```

It adds:

- a token login signal in `Login.qml`;
- a visible "Log in with USB token" button;
- an `onTokenLoginRequest` handler in `Main.qml` that calls `sddm.loginToken()`.
