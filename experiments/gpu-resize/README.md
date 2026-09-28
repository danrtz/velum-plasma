# Optional KWin GPU resize experiment

This is a development experiment for **Arch KWin 6.7.5-1, Qt 6.11.2-3 and kdecoration 6.7.5-1**. It is not installed by Velum's normal installer and is not a general fix for application performance. It leaves HyprKwin as the tiler. Source changes use GPL-2.0-or-later; see `../../LICENSES/KWin-resize` and KWin's original file notices.

The patch lets the compositor draw a window at its requested size while combining Wayland client size requests at about 30 Hz. The optional [input pacer](../../shell/kde/resize-pacer) separately limits pointer-driven resize work to the display refresh rate. The GPU preview can briefly scale content between app commits. It is not an exact port of Hyprland.

`addon/` marks preview-transformed windows for transformed clipping; it **must accompany the core patch** or shrinking windows can show a black strip. Its historical ChatGPT-only pacing controls remain available for reproducibility, but both are off by default: `RedrawDivisor=1`, `DeferUntilRelease=false`. The latter's stretch-until-release appearance was rejected and must not be enabled by installation.

## Evidence and limits

Validated on one 3440×1440, approximately 144 Hz, scale-1 AMD desktop:

- A disposable 60 Hz compositor processed 948 fixture resize events without pacing, 171 with input pacing and 86–87 with input pacing plus GPU preview. Release reached exactly 633 pixels; Escape restored 600 pixels. A deliberately stalled fixture stayed visually at its requested size and committed that size after resuming.
- Isolated HyprKwin retile/shared-divider checks passed. Pixel checks caught and verified the clipping correction; final neighboring geometry retained the expected gap.
- Two isolated Firefox windows used about 27% less combined compositor/browser CPU in a short layout workload. The user subsequently reported no fan ramping while rapidly resizing their real Firefox windows.
- ChatGPT still heated the CPU with live reflow. An additional 15 Hz trial reached 77.75°C and 1,694 CPU-fan RPM; it did not solve the problem. Holding all app resizes until release limited a later roughly 28-second trial to 66°C, but the user rejected the stretching. That trial is **not an accepted fix**.
- These are sequential observations, not a controlled thermal benchmark. They suggest app-specific resize work remains, but do not identify a ChatGPT bug or establish its root cause. Raw process captures and private desktop screenshots are not published.

Mixed DPI, multiple physical outputs, unusual subsurfaces and long-term stability need further testing. XWayland clients only receive the input-pacer benefit; this core patch paces xdg-shell clients. No power, CPU boost or fan policies are changed.

## Build and stage

Use a clean [KWin 6.7.5 source archive](https://download.kde.org/stable/plasma/6.7.5/kwin-6.7.5.tar.xz) with its normal build dependencies and matching development packages. Review the patch first. From this directory, with the extracted source named `kwin-6.7.5`:

```sh
python3 patch.py
cmake -S kwin-6.7.5 -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_TESTING=OFF
cmake --build build --target kwin_wayland -j2
cmake -S addon -B addon/build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build addon/build -j2
python3 stage.py build
```

Staging uses CMake and `readelf`, and only accepts the package versions above. Build dependencies include the matching Plasma Wayland protocols; supply `CMAKE_PREFIX_PATH` if these are installed in a private prefix. Staging creates a relocatable executable, its matching libkwin and the addon in `deploy/runtime`, plus a local package manifest. No binaries or build output are committed.

Before installing, test in a **private D-Bus session and a virtual KWin display**. Do not run automated resize input against your real desktop. Required checks are final geometry, Escape, stalled-client recovery, shrinking-window clipping, shared-divider alignment, and stock fallback. Test scaffolding and results from the original investigation are summarized above; this directory is not a distribution package.

## Optional first installation and rollback

`python3 install.py` installs only into the user's home, saves a backup, copies the existing HyprKwin build with a three-line border-position adaptation, and selects the custom KWin for the **next login**. It requires an existing HyprKwin build and refuses to replace an existing installation. Save work and log out yourself when ready; the script does not restart the desktop. Review the script before using it.

The selector retains KDE's stock wrapper and uses stock KWin when its version manifest changes, the bundle is incomplete, a `disabled` marker exists, or the wrapper is recovering after a compositor crash. The addon is confined to the custom executable's plugin directory, so stock KWin does not discover it there. Inspect selection without starting KWin:

```sh
~/.local/lib/velum-kwin-resize/bin/kwin_wayland --velum-check
```

To select stock KWin for the next login:

```sh
~/.local/lib/velum-kwin-resize/disable
```

Rollback restores the previous HyprKwin build if the experiment still owns the selected build, removes its service override and disables preview borders. It does not close applications. The separate input pacer has its own disable instructions.
