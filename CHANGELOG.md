# Changelog

## v0.1.0-beta.1 — prerelease (2026-11-19)

- Initial combined Cave/Taito PS2 progressive-scan patcher for original Japanese Ibara and Mushihimesama ISOs.
- Preserved the shared-script default Ibara profile (field state, final filter, 8+8 crop, experimental half-pixel quad alignment).
- Made Mushihimesama **Center 12** the fixed default, retaining exact 2× vertical scaling and the original 224-line final output.
- Added automatic detection of `Ibara (Japan).iso` and `Mushihimesama (Japan).iso` when invoked without paths.
- Adopted deterministic versioned output ISO filenames and fail-closed ELF SHA-256 checks.
- Added read-only verification utility, tests and separate technical documentation.
- Documented the goal of greater parity with Arika's Cave PS2 ports while preserving each Taito port's unique options.
- Included three original off-screen Sony PVM-14M4U photographs in `screenshots/` and displayed them in the README.
- Added FAQ entries for water shimmer in Ibara, crop limits, and Mushihimesama's lack of native optical S/PDIF audio (future compatibility investigation planned).
- Known limitations: partial source image crop in both games; minor Ibara shimmer (including water); no full-frame Mushihimesama expansion; optical audio missing on original Mushihimesama in tested setup.
