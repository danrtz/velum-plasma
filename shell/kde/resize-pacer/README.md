# Resize pacing

A small native KWin extension that coalesces pointer-driven interactive resize updates to the output refresh rate. KWin's pointer position is updated before the filter runs, so normal pointer tracking remains unchanged. The latest pending geometry is delivered on a trailing timer and before button release; Escape discards it before KWin cancels. Moving windows, normal application input, and keyboard resizing retain KWin's handlers. HyprKwin remains the tiler.

This addresses excess resize processing, not every source of missed presentation frames. The extension does not render or animate window contents, change display refresh rate, or change power/fan settings.

## Build and install

Build against the installed KWin development headers, Qt 6 (including private headers), ECM, and KF6 CoreAddons:

```sh
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
```

Install `build/plugins/kwin/effects/plugins/velum_resize_pacer_v2.so` into the system Qt 6 plugin directory's `kwin/effects/plugins` directory (on Arch: `/usr/lib/qt6/plugins/kwin/effects/plugins/`). Then enable it:

```sh
kwriteconfig6 --file kwinrc --group Plugins --key velum_resize_pacer_v2Enabled true
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect velum_resize_pacer_v2
```

No compositor restart is required. KWin's native plugin API is version-specific: rebuild after updating KWin; its factory version check rejects an incompatible plugin. This optional extension is not automatically installed by Velum's main installer.

To disable immediately and at future logins:

```sh
kwriteconfig6 --file kwinrc --group Plugins --key velum_resize_pacer_v2Enabled false
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect velum_resize_pacer_v2
```

## Validation on 2026-09-28

KWin 6.7.5 / Qt 6.11.2 / AMD RX 7900 XT / Ryzen 9800X3D.

In a separate virtual 60 Hz compositor, a 1,501-motion resize sequence produced 951 client resize events without pacing and 171 with pacing. Both ended at exactly the same 633×400 geometry. Escape restored the original 600×400 geometry; unloading restored the original resize path. Final pending count was zero.

On the actual 3440×1440 143.975 Hz desktop with HyprKwin and two disposable tiled Qt windows, matched three-second sequences measured:

| Metric | Original | Paced |
| --- | ---: | ---: |
| KWin CPU, percent of one core | 75.7 | 44.1 |
| Test client CPU, percent of one core | 80.6 | 43.1 |
| First / second window repaints | 736 / 718 | 404 / 404 |
| Input motion events | 881 | 888 |

Live Meta+left-drag still retiles windows; Meta+right-drag still adjusts neighboring tiles. These checks establish reduced work and preserved controls, not a guaranteed temperature or universally smooth application rendering. The user confirmed that resizing Firefox or ChatGPT feels noticeably smoother after enabling the extension. Reboot persistence and the previous 30-second / 83°C thermal condition have not yet been retested.


## Optional lower-workload resize rate

Revision 0.2 adds `MaxRate` in the `Effect-velum_resize_pacer` group of kwinrc. Zero (the default) follows display refresh; positive settings are clamped to 30–360 updates/second, never exceeding the display refresh. It applies only during pointer-driven interactive resize. The display refresh, normal pointer input, and applications outside resizing are unchanged.

The development machine briefly tested `MaxRate=90`, but has returned to `MaxRate=0`, with `velum_resize_pacer_v2Enabled=true` and the old extension disabled. Revision 0.2 has a new library filename so it can replace Qt's cached revision without restarting the session. Set `MaxRate=0` and reconfigure the effect to restore the display-rate behavior.

A confirmed rapid-resize comparison (two temporary tiled Qt windows, four seconds each) measured 44.8% compositor + 43.8% client CPU at display rate, versus 29.2% + 27.7% at the 90-update cap: about 36% less CPU work. Repaints per window dropped from 543 to 343. CPU temperature started at 61.25°C / 61.625°C and peaked at 63.375°C / 62.375°C, respectively. These short lightweight-client runs do not establish the user's sustained Firefox/ChatGPT temperature. An earlier run was interrupted by an administrator prompt and is invalid.

The user clarified that revision 0.1 resolved the visible stutter but rapid resizing still caused heat/fan spikes. The user reported continued fan ramping at the lower cap; the cap was reverted. Passive observation during the attempt captured CPU up to 78.625°C and CPU-fan speeds up to 1,724 RPM. This did not resolve the thermal complaint. No CPU boost limits, global power policy, or fan settings were changed in this revision.

After an approved logout/login the extension remained loaded at `MaxRate=0`. The later, separately installed [GPU preview experiment](../../../experiments/gpu-resize/README.md) improved Firefox's reported fan behavior. ChatGPT's remaining heat is unresolved. Both native extensions rebuilt during the publication audit; native plugins remain tied to their KWin/Qt build versions.
