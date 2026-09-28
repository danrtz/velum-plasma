# HyprKwin for Velum

Bundled from [DGBooth/HyprKwin](https://github.com/DGBooth/HyprKwin) 0.12.2, commit `89c3dd14d7389a38f63e750a2bf6609379efe60d`. `package/` and `package-effect/` contain unmodified upstream QML/JavaScript; the upstream shortcut helper is included under `package/contents/tools/`. The GPL-3.0 license is retained in `LICENSES/HyprKwin` at the repository root.

Velum's `settings.json` selects preserved Dwindle splits, compact gaps and shell/game exclusions. `shortcuts.json` lists every upstream action, with an empty string for unused bindings. The main installer registers these before starting HyprKwin so its default shortcuts cannot take the shell's keys. Animations use 250 ms transitions. Dragging retiles on release; shared-boundary resizing updates live.

The installer installs only HyprKwin and its companion effect, recording package ownership in `~/.local/state/velum-install/tiling.json`. Repeating installation preserves user settings. Rollback disables both and removes packages installed by Velum, then restores the shell's backed-up shortcuts and KDE configuration. Existing unmanaged HyprKwin installations are left untouched; competing tilers must be disabled first. A newly installed effect may require one logout/login if KWin has not discovered it yet. Velum does not restart KWin.

Validation includes the upstream engine tests and real isolated/live tiling and animation checks. `python3 tests/tiling-install.py /path/to/HyprKwin` exercises this installer's fresh package installation, shortcut assignment, tile area, repeat-install preservation and rollback in a private KWin session. It requires the pinned upstream test harness and its dependencies. Physical multi-monitor operation and fresh host reboot remain unverified.
