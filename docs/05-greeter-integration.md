# Greeter integration

The SDDM backend patch is generic, but the visual integration is greeter-specific.

Any QML greeter can use token login if it can call:

```qml
sddm.loginToken(username, sessionIndex)
```

## Required values

The greeter must provide:

| Value | Meaning |
|---|---|
| `username` | Account name to authenticate. |
| `sessionIndex` | Selected session index. Use `0` if the theme does not expose session selection. |

## Generic button component

See:

```text
greeters/common/TokenLoginButton.qml
```

## Breeze-like themes

Use:

```bash
sudo python3 greeters/adapters/breeze/patch-breeze-token-button.py --theme-dir /path/to/theme
```

The adapter is a convenience script, not a universal QML patcher. Always inspect the theme after applying it.

## Notes

Do not disable major theme components such as wallpaper faders, stacks, or footer items unless you understand the QML state machine. Greeter themes often use opacity to show and hide the login form.
