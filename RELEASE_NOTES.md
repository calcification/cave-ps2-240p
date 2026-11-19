# v0.1.0-beta.1 — Cave/Taito PS2 240p (prerelease)

A prerelease focused on bringing these Taito-developed Cave PS2 ports closer to the CRT-friendly, arcade-style presentation of Arika's Cave PS2 ports, while keeping their unique PS2 modes and options accessible. Full Arika-level parity has **not** been reached.

Initial combined patcher for the Japanese PS2 releases of **Ibara** (SLPM-66301) and **Mushihimesama** (SLPM-66056).

**How to use:** Download or clone the repository, put `Ibara (Japan).iso` and/or `Mushihimesama (Japan).iso` alongside `cave_ps2_progressive.py`, then run `python3 cave_ps2_progressive.py`. The script verifies each original executable and writes separate, versioned ISOs. See the README for details.

**Known prerelease limitations:**

- **Ibara:** crops 8 of 240 source rows at each edge (224 shown); minor residual vertical/diagonal shimmer remains, **including shimmering water**; requires further investigation.
- **Mushihimesama:** exact 2× vertical scale plus tested Center 12 positioning; 224 of 240 source rows visible (approximately 3 at one edge and 13 at the opposite edge are cropped). Full-frame expansion is not included. The original PS2 game does **not** supply sound over optical S/PDIF in the tested setup, independent of this patch. Use analog stereo; an optical compatibility fix is planned for future investigation.
- Hardware and display compatibility are not fully validated; use with caution.

Three user-supplied **off-screen photographs of a Sony PVM-14M4U** are included under `screenshots/` and embedded in the README.

No ISOs or game executables are distributed. This is marked a **prerelease**, not a stable 1.0.