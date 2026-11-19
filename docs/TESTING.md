# Testing status and how to report bugs

## Current beta status

| Game | PCSX2 | Original PS2 | Known limitation |
|---|---|---|---|
| Ibara SLPM-66301 | Investigated with original ELF, patches and GS dumps; visibly improved, minor residual shimmer, including water | Some earlier hardware observation; complete testing of this release profile is **not confirmed** | Cropped 8+8 source lines; residual shimmer, including water |
| Mushihimesama SLPM-66056 | Exact 2× + Center 12 observed usable; extra expansion variants produced artifacts | Current Center 12 release profile **not confirmed** | Cropped approximately 3+13 source lines; original game optical S/PDIF silent; analog stereo recommended |

## What to test

1. Launch the title screen, enter gameplay, and let the game scroll continuously for at least a minute.
2. Observe vertically moving fine detail and horizontal stripes; check for jitter, rolling, tearing and bottom-edge black bars.
3. Visit game over, rankings, menus, credits and transitions, where the renderer may use different drawing paths.
4. With Mushihimesama, use **analog stereo** for audio; the original game does not produce optical S/PDIF sound in the tested setup. A future compatibility fix is planned but unverified.
5. If available, compare PCSX2 software and hardware renderer results and test a compatible CRT on a real PS2.

## Include in a bug report

- Game and printed patch version (`v0.1.0-beta.1`)
- Exact ISO input source and whether it passed hash verification (do not upload game data)
- Emulator version or PS2 model and method of loading the legally owned backup
- Video connection and display/scaler; audio connection separately
- Repro steps and whether the same issue appears in the unmodified ISO
- Screenshot or short video, and optionally an emulator GS dump (make sure you are permitted to share it)

Do not file reports containing copyrighted ISOs, extracted game executables, or other game assets.

## CRT photographs in the README

The three `screenshots/*.jpg` images are user-supplied **off-screen photographs of a Sony PVM-14M4U CRT**, not emulator captures. Scanlines and camera artifacts should not be treated as definitive evidence of the patch's pixel-sampling behavior.