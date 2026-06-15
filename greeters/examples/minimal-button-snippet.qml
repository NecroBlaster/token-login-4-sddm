// Minimal example. Adapt username and sessionIndex to the target greeter.
Button {
    text: "Log in with USB token"
    enabled: username.length > 0
    onClicked: sddm.loginToken(username, sessionIndex)
}
