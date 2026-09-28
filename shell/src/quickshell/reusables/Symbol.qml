// Vector controls with the original glyph as fallback for brands and special symbols.
import QtQuick
import QtQuick.Window
import "Icons.js" as Icons

Item {
    id: root
    property string glyph: ""
    readonly property string iconName: Icons.names[glyph] || ""
    property font font: Qt.font({family: "Iosevka Nerd Font", pixelSize: 18})
    property color color: "white"
    property int horizontalAlignment: Text.AlignHCenter
    property int verticalAlignment: Text.AlignVCenter
    implicitWidth: iconName ? font.pixelSize : fallback.implicitWidth
    implicitHeight: iconName ? font.pixelSize : fallback.implicitHeight

    Text {
        id: fallback
        anchors.fill: parent
        text: root.iconName ? "" : root.glyph
        font: root.font
        color: root.color
        horizontalAlignment: root.horizontalAlignment
        verticalAlignment: root.verticalAlignment
    }

    Image {
        anchors.centerIn: parent
        width: root.font.pixelSize
        height: width
        visible: root.iconName !== ""
        source: visible ? "data:image/svg+xml;utf8," + encodeURIComponent(Icons.svg[root.iconName].replace(/currentColor/g, Qt.rgba(root.color.r, root.color.g, root.color.b, 1).toString())) : ""
        opacity: root.color.a
        sourceSize: Qt.size(width * Screen.devicePixelRatio, height * Screen.devicePixelRatio)
    }
}
