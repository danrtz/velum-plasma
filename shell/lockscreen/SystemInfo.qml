pragma Singleton
import QtQuick
import "."
QtObject {readonly property string username:(NativeState.snapshot.user||{}).username||kscreenlocker_userName;readonly property string avatarPath:(NativeState.snapshot.user||{}).avatarPath||kscreenlocker_userImage}
