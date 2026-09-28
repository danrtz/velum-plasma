# Development-machine tuning

These settings record the checked desktop configuration. They are not automatically applied by the installer and should not be treated as portable hardware defaults.

## Window rounding and spacing

Tiling defaults now use inner gap 2 and outer gap 4, with a 12-pixel border radius. Existing installations preserve their chosen settings. The bar reserves its own height rather than stacking another top gap.

Actual window clipping uses the optional [KDE Rounded Corners](https://github.com/matinlotfali/KDE-Rounded-Corners) native effect, tested at commit `c1178d94ff2ec0db8d4d9a9782a3eb06aec13ce6`. This is upstream code, not a Velum implementation. Build/install it according to its upstream instructions against the current KWin version. The checked `kwinrc` preset is:

```ini
[Plugins]
kwin4_effect_shapecornersEnabled=true

[Round-Corners]
Size=12
InactiveCornerRadius=12
UseSquircleShape=false
IncludeDialogs=true
IncludeNormalWindows=true
DisableRoundFullScreen=false
DisableRoundMaximize=false
DisableRoundTile=false
Exclusions=quickshell
OutlineThickness=0
OuterOutlineThickness=0
SecondOutlineThickness=0
InactiveOutlineThickness=0
InactiveOuterOutlineThickness=0
InactiveSecondOutlineThickness=0
ShadowSize=0
InactiveShadowSize=0
```

Excluding Quickshell preserves its own rounded surfaces. Removing duplicate outlines and shadows avoids the doubled corner appearance. Fullscreen/maximized rounding is a visual preference; disable it if desired. Native effects need compatibility checks after KWin upgrades.

## Resize behavior

The [input pacer](../shell/kde/resize-pacer) reduced excess resize work and the user confirmed smoother interaction. It remains optional, with `MaxRate=0` (display rate). The separately installed [GPU-preview experiment](../experiments/gpu-resize) improved Firefox's fan behavior; ChatGPT's remaining resize heat is unresolved. The rejected stretch-until-release mode and additional ChatGPT throttling are disabled. No CPU boost limits were applied.

## Ridge case fans

On the tested ASRock B850I Lightning WiFi, NCT6686D board controller and RX 7900 XT, the Fractal Ridge case fans beside the GPU were mapped to CHA_FAN1 (`fan4/pwm4`). CoolerControl 5.0.1 and nct6687d `r246.5f12dd1` supplied writable control; the CPU cooler and pump remained under firmware control, and GPU built-in fan control was untouched.

After checking channel mapping, a temporary speed-change/firmware-return test passed. The saved GPU-edge curve is 35% through 45°C, 45% at 55°C, 60% at 65°C, 85% at 75°C and 100% at 85°C. Downward changes use a five-second delay, 2°C threshold and five-percentage-point maximum step; upward changes are immediate. A service hook restores that chassis header to firmware control on CoolerControl start/stop/failure. Stop/start verification passed; reboot, suspend and sustained gaming thermals still need validation.

This motherboard-specific setup is documented rather than installed by Velum. Fan channel numbers and alternate kernel drivers are not portable: another PC must identify and test its own controller and fallback before adopting a curve. Personal device IDs, authentication tokens, raw daemon configuration and hardware-control installers are not included. Case-fan temperature selection does not fix CPU work while resizing.
