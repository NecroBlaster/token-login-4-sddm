// Example handler inside a greeter component.
signal tokenLoginRequest(string username)
onTokenLoginRequest: {
    root.notificationMessage = ""
    sddm.loginToken(username, sessionButton.currentIndex)
}
