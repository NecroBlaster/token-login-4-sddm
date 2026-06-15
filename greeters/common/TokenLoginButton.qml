import QtQuick
import QtQuick.Controls as QQC2

QQC2.Button {
    id: tokenButton
    property string username: ""
    property int sessionIndex: 0
    text: "Log in with USB token"
    enabled: username.length > 0
    onClicked: {
        sddm.loginToken(username, sessionIndex)
    }
}
