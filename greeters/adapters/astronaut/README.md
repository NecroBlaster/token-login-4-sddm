# Astronaut greeter notes

The Astronaut SDDM theme can be adapted by adding a button that calls:

```qml
sddm.loginToken(username, sessionIndex)
```

The exact IDs used by the theme may differ between versions. Inspect the theme's QML files to identify:

- the selected username;
- the selected session index;
- the existing password login button.

Use `greeters/common/TokenLoginButton.qml` as a reference component.
