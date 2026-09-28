# Port coverage and verification

Base: Serpantinum `fc327946b5ee8697bddaae1021fe3db5e378deb0` (2.1.10), AGPL-3.0-or-later. The original QML and assets are included; this is not the earlier Plasma-applet imitation. All work is local and unpublished.

## Interface and features

| Area | KDE port and validation |
| --- | --- |
| Bar and sidebar | Original modules, grouping, arrangement editor, four positions, styles, animation, and settings. All four positions loaded and persisted. |
| Workspaces and focus | KWin event bridge; workspace switch and return tested. No compositor polling loop. Window activation, minimization, restoration, and close exercised during preview/recovery checks. |
| Launcher | Original application search, categories, ranking, and keyboard-driven UI; global shortcut launches it. |
| Clipboard | Original UI with isolated cliphist database. Capture, list, decode, pin/unpin, and removal passed; prior clipboard restored. |
| Quick settings and notifications | Original combined panel, network, Bluetooth, audio, power, calendar, weather, history, DND, and media surfaces. Pages opened and visually checked. Notification service ownership and delivery verified. |
| Widgets | All 23 original styles instantiated. Every widget type passed add, move, save, reload, and removal checks. Original layout restored. |
| Dock | Original application picker, arrangement, position, sizing, autohide and fullscreen behavior retained; workspace/fullscreen inputs now come from KWin. |
| Themes | Original presets, fonts, sounds, wallpaper transitions, and theme pages. Static and image-based Matugen generation passed, including matching KDE application colors. Previous palette restored. |
| Wallpaper | Original picker, per-screen paths, history and video engine. Generic search returned 83 image results. Static wallpaper persists across shell restarts. Animated wallpaper produced distinct frames and passed pause/play commands; original wallpaper restored. |
| Quick actions | Original drawing, system usage, timer, stopwatch, and Pomodoro. Timer modes passed start/pause checks; drawing commit/undo/redo passed in isolated QML tests. |
| Wellbeing | Original dashboard, limits/settings and charts. Daemon records app IDs from the KWin bridge; local database and query responses verified. Window titles are not stored in usage history. |
| Brightness | Native KDE ScreenBrightness service; one-step change and restoration passed. |
| Night Light | Native KDE state and configuration notifications. Enable/temperature/mode and restoration passed. It is global across monitors, matching KDE’s model. |
| Display settings | Original display/widget pages retained; native KDE display configuration is available for HDR, refresh rate, scaling and arrangement. Existing output configuration remained unchanged. |
| Screenshot | Original region/recording overlay with KDE capture backend. Full desktop and cropped region captures passed. Annotation uses Satty; QR recognition uses zbar. |
| Recording | KWin/PipeWire hardware H.264 video plus optional independently mixed desktop/mic audio. Silent and desktop-audio recording passed. Final still-frame duration is preserved without re-encoding. |
| Secure lock | Original lock visuals adapted to KScreenLocker. Clock and expanded dashboard rendered, including a real notification. Notification cards/actions/read/dismiss/mute and hold-button sound APIs are connected. Native mute round-trip and sound start/stop passed. KDE owns password checking and the successful-unlock result. |
| Polkit | Original prompt owns the agent slot while Velum runs. A real authorization request appeared and was canceled without entering credentials. |
| Persistence and recovery | All four services active after target restart. Stop restores both native desktop and polkit services; start returns to Velum. Recovery uses a short precise timer to avoid rapidly starting/stopping Plasma during a Velum restart. |
| Installation | Native helpers rebuilt. A second installation preserved the initial rollback baseline and shortcuts. No remote is configured and nothing has been published. |

## Architecture

- `shell/src/quickshell`: original interface, with `KdeBackend.qml` supplying workspace, active-window and monitor data.
- `shell/kde/observer.js` and `bridge.py`: KWin signals → private atomic runtime snapshot and explicit window/workspace commands.
- `shell/kde/brightness.py`, `nightlight.py`, `displays.py`: native KDE control adapters.
- `shell/kde/capture.py`, `recorder`, `record.py`: Spectacle capture and KWin/PipeWire recording.
- `shell/lockscreen`: original lock visuals using KDE’s authenticator. A small native QML plugin reads the private snapshot and forwards a limited set of desktop actions. Passwords never enter that snapshot or IPC bridge.
- `shell/kde/install.py`, `session.sh`, `recover.sh`: local build/install, KDE-only login start, desktop ownership and rollback.

Configuration, clipboard, history and runtime state use `velum` directories, separate from the original Serpantinum installation. The first rollback baseline is retained across upgrades. The native greeter package includes the installed stock Plasma shell files so native recovery remains usable.

## Test boundaries and differences

- Testing used one 3440×1440 display at approximately 144 Hz with HDR enabled. Physical multi-monitor hotplug, mixed DPI and screen rotation remain hardware checks. KWin uses shared virtual desktops and global Night Light; the UI reflects those semantics.
- Secure greeter test mode and rendering were checked. Real password unlock, logout, reboot, shutdown, hibernate and suspend were not triggered during the active user session. Those actions call the native services and retain their authorization behavior.
- Desktop audio recording was tested; microphone capture was deliberately not exercised. Every Bluetooth pairing, Wi-Fi credential flow and notification action from third-party apps has not been exhaustively tested.
- The lock entrance uses the current wallpaper rather than a captured image of private application windows. Its original clock/dashboard layouts, transitions and exit animation are preserved.
- The port has no published release endpoint. Its About page identifies the local KDE build; the upstream installer cannot overwrite the KDE port.
- The original interface has continuous visual animations. A 40-second idle sample used about 10–11% of one CPU core for the shell, while bridge, clipboard and wellbeing used approximately 0%, 0%, and 0.03%. Shell memory after a fresh start and settings inspection was about 524 MiB; loading all widget/font pages raises Qt’s caches. This is not a zero-resource theme.

Python compilation, 40 shell syntax checks, native CMake builds, page loading, real-session integration tests, and restoration checks were performed. Added adapter code passes whitespace checks; imported upstream formatting is retained. No actual password, personal history, location settings, or application-window screenshot is included in this repository.

The icon refresh uses Papirus-Dark for KDE application icons and a bundled Lucide subset for shared shell controls. Unmapped symbols retain their original glyphs; custom canvas animations stay intact. DND has been restored to off with explicit approval.
The shared controls, launcher fallback icons, live bar/settings and native lock preview loaded successfully after the refresh. Qt reports Papirus-Dark as its icon theme. Output/HDR settings remain byte-for-byte unchanged. The lock snapshot also copies explicit notification-group fields to avoid serializing model objects.

Control consistency check: Win+D and Win+Space both open the launcher. The six assigned combinations (launcher twice, clipboard, settings, quick settings, screenshot) each resolve to exactly one active global action. All five action handlers were exercised, including opening and dismissing the screenshot overlay. The Win+D reassignment is saved in KDE’s shortcut configuration and the previous Show Desktop binding is included in rollback. The bar reserves its height and lets KWin supply the 4-pixel tile gap. Occupied inactive desktops use a subtle accent tint in the horizontal and vertical number/pill styles; active desktops keep their stronger highlight. Desktop counts include existing KWin desktops.

Automatic tiling now uses HyprKwin 0.12.2 with its animation effect, preserved Dwindle splits and game/shell exclusions. HyprKwin is the only bundled tiler. It rearranges dragged windows on release; shared-boundary resizing is live. Its animation effect supplies 250 ms tile transitions. This is not exact Hyprland behavior.

Controls remain Win+arrows for focus, Win+Ctrl+arrows for swaps, Win+Shift+arrows for resize, Win+Shift+F for floating, Win+Q for closing, and Win+1–9/0 for desktops (with Shift to move/follow). Win+Ctrl+Space rotates splits and Win+Shift+E cycles layouts. The installer bundles the pinned script and effect, assigns the preset before activation, and preserves user settings on repeat installation. Older tiler packages are excluded from the project.

The bridge selects KDE's sole existing activity if login starts with no current activity, preserving existing selections and leaving multiple activities alone. This startup guard and the replacement tiler still need a fresh-reboot check.

Native desktop-slide, scale, squash, maximize, fullscreen and popup effects are enabled. Window scale uses 200 ms; popup entrance/exit uses 180/140 ms. The installer applies this preset once and preserves later adjustments. HyprKwin separately animates tiling reflows. Multi-monitor mouse movement remains a hardware check.

Launcher and dock applications now launch through KDE kstart, outside the shell service lifecycle. During validation, a shell reload exposed that direct launches could be terminated with the shell; Cider was reopened independently.

Final alignment check: modular bar ends measured 9 pixels from each screen edge before removing duplicate content padding, and 4 pixels afterward, matching tiled window margins. The occupied inactive desktop tint was visually checked with another desktop active. All 36 workspace/tiling key combinations resolve to their expected KWin actions in the live session. A temporary registered desktop entry launched through kstart in its own app service; the entry and process were removed afterward. Cider remained running across subsequent shell reloads.

HyprKwin passed 76 upstream unit tests, isolated window/divider animation tests, live Win-drag retile-on-release and shared-boundary resizing, and live focus/swaps, float/re-tile, desktop move/follow, minimize/fullscreen/maximize restoration, split rotation and close/reflow. All 42 intended shortcuts have the correct owner. Host KWin retained PID 1147. Reboot and multi-monitor checks remain outstanding.

Fixed the lock wallpaper startup race: image loading waits for the native snapshot cache path, and the fallback retains a reactive binding. KDE's greeter testing mode rendered the blurred wallpaper successfully; the next real lock remains a user check. Authentication code was unchanged. No publishing was performed.
