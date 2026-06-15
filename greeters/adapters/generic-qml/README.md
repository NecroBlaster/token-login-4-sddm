# Generic QML greeter integration

The minimum required call is:

```qml
sddm.loginToken(username, sessionIndex)
```

If the greeter does not expose a session selector, use `0`:

```qml
sddm.loginToken(username, 0)
```

A greeter-specific button must identify where the username is stored. Common examples:

```qml
userNameInput.text
userList.selectedUser
root.selectedUser
```

The backend patch is generic. The visual placement of the button is theme-specific.
