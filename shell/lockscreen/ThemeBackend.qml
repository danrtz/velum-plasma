pragma Singleton
import QtQuick
import "."
Item {
readonly property color base: (NativeState.snapshot.theme || {}).base || "#1e1e2e"
readonly property color mantle: (NativeState.snapshot.theme || {}).mantle || "#181825"
readonly property color crust: (NativeState.snapshot.theme || {}).crust || "#11111b"
readonly property color text: (NativeState.snapshot.theme || {}).text || "#cdd6f4"
readonly property color subtext0: (NativeState.snapshot.theme || {}).subtext0 || "#a6adc8"
readonly property color subtext1: (NativeState.snapshot.theme || {}).subtext1 || "#bac2de"
readonly property color surface0: (NativeState.snapshot.theme || {}).surface0 || "#313244"
readonly property color surface1: (NativeState.snapshot.theme || {}).surface1 || "#45475a"
readonly property color surface2: (NativeState.snapshot.theme || {}).surface2 || "#585b70"
readonly property color overlay0: (NativeState.snapshot.theme || {}).overlay0 || "#6c7086"
readonly property color overlay1: (NativeState.snapshot.theme || {}).overlay1 || "#7f849c"
readonly property color overlay2: (NativeState.snapshot.theme || {}).overlay2 || "#9399b2"
readonly property color blue: (NativeState.snapshot.theme || {}).blue || "#89b4fa"
readonly property color sapphire: (NativeState.snapshot.theme || {}).sapphire || "#74c7ec"
readonly property color peach: (NativeState.snapshot.theme || {}).peach || "#fab387"
readonly property color green: (NativeState.snapshot.theme || {}).green || "#a6e3a1"
readonly property color red: (NativeState.snapshot.theme || {}).red || "#f38ba8"
readonly property color mauve: (NativeState.snapshot.theme || {}).mauve || "#cba6f7"
readonly property color pink: (NativeState.snapshot.theme || {}).pink || "#f5c2e7"
readonly property color yellow: (NativeState.snapshot.theme || {}).yellow || "#f9e2af"
readonly property color maroon: (NativeState.snapshot.theme || {}).maroon || "#eba0ac"
readonly property color teal: (NativeState.snapshot.theme || {}).teal || "#94e2d5"
readonly property string fontFamily:(NativeState.snapshot.theme||{}).fontFamily||"monospace"
readonly property int borderRadius:(NativeState.snapshot.theme||{}).borderRadius??10
readonly property int clampedBorderRadius:(NativeState.snapshot.theme||{}).clampedBorderRadius??10
FontLoader{source:(NativeState.snapshot.theme||{}).activeFontPath?"file://"+NativeState.snapshot.theme.activeFontPath:""}
}
