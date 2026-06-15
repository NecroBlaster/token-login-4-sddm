#!/usr/bin/env python3
import argparse
from pathlib import Path

def patch_login_qml(path: Path) -> None:
    s = path.read_text()
    if 'signal tokenLoginRequest' not in s:
        s = s.replace('    signal loginRequest(string username, string password)\n', '    signal loginRequest(string username, string password)\n    signal tokenLoginRequest(string username)\n', 1)
    if 'function startTokenLogin()' not in s:
        marker = '''    function startLogin() {
        const username = showUsernamePrompt ? userNameInput.text : userList.selectedUser
        const password = passwordBox.text

        footer.enabled = false
        mainStack.enabled = false
        userListComponent.userList.opacity = 0.75

        loginButton.forceActiveFocus();
        loginRequest(username, password);
    }
'''
        insert = marker + '''
    function startTokenLogin() {
        const username = showUsernamePrompt ? userNameInput.text : userList.selectedUser
        if (!username || username.length === 0) {
            userNameInput.forceActiveFocus()
            return
        }
        footer.enabled = false
        mainStack.enabled = false
        userListComponent.userList.opacity = 0.75
        tokenLoginButton.forceActiveFocus()
        tokenLoginRequest(username)
    }
'''
        if marker not in s:
            raise SystemExit('Could not find the expected startLogin() block in Login.qml')
        s = s.replace(marker, insert, 1)
    if 'id: tokenLoginButton' not in s:
        insertion_point = s.rfind('\n}')
        if insertion_point < 0:
            raise SystemExit('Could not find end of Login.qml')
        button = '''

    PlasmaComponents3.Button {
        id: tokenLoginButton
        Layout.fillWidth: true
        text: "Log in with USB token"
        icon.name: "dialog-password"
        enabled: root.showUsernamePrompt ? userNameInput.text.length > 0 : userList.selectedUser.length > 0
        onClicked: startTokenLogin()
    }
'''
        s = s[:insertion_point] + button + s[insertion_point:]
    path.write_text(s)

def patch_main_qml(path: Path) -> None:
    s = path.read_text()
    if 'onTokenLoginRequest' not in s:
        old = '''                onLoginRequest: {
                    root.notificationMessage = ""
                    sddm.login(username, password, sessionButton.currentIndex)
                }
'''
        new = '''                onLoginRequest: {
                    root.notificationMessage = ""
                    sddm.login(username, password, sessionButton.currentIndex)
                }

                onTokenLoginRequest: {
                    root.notificationMessage = ""
                    sddm.loginToken(username, sessionButton.currentIndex)
                }
'''
        if old not in s:
            raise SystemExit('Could not find the expected onLoginRequest block in Main.qml')
        s = s.replace(old, new)
    path.write_text(s)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--theme-dir', required=True, help='Path to the SDDM QML theme directory')
    args = parser.parse_args()
    theme = Path(args.theme_dir)
    login = theme / 'Login.qml'
    main_qml = theme / 'Main.qml'
    if not login.exists() or not main_qml.exists():
        raise SystemExit('Theme directory must contain Login.qml and Main.qml')
    patch_login_qml(login)
    patch_main_qml(main_qml)
    print(f'Patched theme: {theme}')

if __name__ == '__main__':
    main()
