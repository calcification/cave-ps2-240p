# Investigation and outstanding work

This records the state of the investigation for **v0.1.0-beta.1**. It is not an installation guide; see the [README](../README.md).

## Ibara

- The final-pass 240→224 mapping and bilinear filtering were identified as major contributors to poor image quality.
- Cropping source UVs to 8..232, selecting nearest filtering and progressive mode makes the result dramatically sharper than the original interlaced image.
- Field-locking and half-pixel adjustments were experimented with; some combinations caused worse shimmer. The published default is the verified output of the shared `cave_ps2_progressive.py` recipe (21 word edits), which still has **minor shimmer**, visibly including the water during movement; resolving water shimmer is planned for further investigation.
- Future work: compare the stable minimum-edit recipe and field/half-pixel variants during a controlled scrolling sequence on real hardware; trace how per-field texture and raster alignment changes during scrolling.

## Mushihimesama

- Rev 4 established non-interlaced output but left horizontal banding.
- Nearest-neighbor compositing, source-row parity tests and half-pixel shifts alone did not fix the stripes.
- The meaningful improvement was replacing the four active 1.8× vertical scale sites with 2.0× and keeping a 2:1 final reduction.
- A 12-intermediate-pixel upward origin shift (Center 12), with matching clear-rectangle compensation, appeared usable in PCSX2. Larger shifts exposed black bars.
- Expansion experiments widened the offscreen clear/scissor to 480 and corrected a final texture clamp initially limiting sampling to row 447. Corrected GS replays could sample rows above 447 without repeated-row streaks.
- Live Stage 5 ISO experiments still produced intermittent black bottom bars; reducing all 480 source rows into 224 output lines also brought back noninteger-scaling stripes.
- Full-frame restoration must preserve 2:1 scaling (480→240), not compress 480→224. It also needs an audited buffer layout and correct live viewport/clear coverage.
- **Optical audio:** missing on the unmodified ISO in the tested setup, independent of this patch. Analog stereo is the practical workaround. A possible future fix for optical S/PDIF initialization is planned for further investigation; no audio-driver edits are included and a successful fix is not yet established.

## Release policy

Experimental GS dumps, staged framebuffer expansions, modified executables, and ISOs are **not** in this repository. Only reproducible, baseline patch instructions are released. Any later expansion should get a new version and its own regression testing.