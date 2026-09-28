import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../../"
import "../../reusables"
import "../"

Notification {
    id: faceRoot

    fullSummary: model ? (model.summary || "Update Available") : "Update Available"
    fullBody: model && model.body !== "" ? model.body : "A new version of Serpantinum is available."
    accentColor: ThemeBackend.green
    overrideClick: true

    onCardClicked: {
        NativeState.action("notificationAction", JSON.stringify({uid:model.uid, action:"default"}));
    }

    iconArea: [
        Item {
            anchors.fill: parent

            Rectangle {
                anchors.fill: parent
                radius: width / 2
                color: Qt.alpha(ThemeBackend.green, 0.15)
            }

            Text {
                anchors.centerIn: parent
                text: "󰚰"
                font.family: ThemeBackend.fontFamily
                font.pixelSize: s(22)
                color: ThemeBackend.green
            }
        }
    ]

    headerArea: [
        Text {
            Layout.fillWidth: true
            text: model ? (model.displayName || model.appName || "Serpantinum Updater") : "Serpantinum Updater"
            font.family: ThemeBackend.fontFamily
            font.weight: Font.Bold
            font.pixelSize: s(11)
            color: ThemeBackend.subtext0
            elide: Text.ElideRight
        }
    ]
}
