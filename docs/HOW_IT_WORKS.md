# How it works

This is technical background. For installation and usage, see the [README](../README.md).

## What “240p” means here

Both patches make the PS2 emit a non-interlaced video mode with **224 active picture lines**. It is normal for such a mode to be called *240p*; it does **not** mean all 240 original source-image rows are shown. This prerelease deliberately does not alter framebuffers to display all 240 source rows.

## Ibara (SLPM-66301): final-pass resampling

The original port uses a final textured pass that maps a 240-line image into a 224-line display area. A 240-to-224 reduction is non-integer and can introduce sampling/scrolling artifacts.

The patch:

1. Disables interlace in the graphics initialization and holds the game's field-state flags at zero.
2. Changes the final texture filter from bilinear to nearest-neighbor.
3. Changes three mode-specific UV rectangles from 0..240 to **8..232**, making a 224-line source window map to 224 output lines.
4. Moves four final-quad vertical coordinates by half a GS pixel, an experimental alignment adjustment.

**Consequence:** Exactly 16 source lines are excluded, approximately 8 at each edge. Minor vertical/diagonal shimmer remains. Earlier field-lock experiments sometimes worsened shimmer; therefore this recipe is a *beta* rather than a finished graphics fix, and users should compare it against an unpatched ISO.

## Mushihimesama (SLPM-66056): upstream non-integer scale

GS captures revealed a different pipeline: portions of the arcade-derived artwork were first scaled from 240 texels to approximately 432 intermediate pixels (**1.8×**). The original compositor then reduced a 448-line target to 224 output lines (**2:1**).

Changing only the final-pass filter or trying half-pixel/UV shifts did not remove the observed horizontal bands. The promising change was to replace four float-constant constructions of **1.8** (`0x3FE66666`) with **2.0** (`0x40000000`), retaining an exact 2:1 final reduction. The user observed substantially reduced or apparently eliminated scrolling shimmer in PCSX2.

The prerelease also:

1. Disables interlace at the verified ResetGraph and SetGsCrt sites and locks the game's field-state flags.
2. Changes the compositor's texture filter to nearest-neighbor.
3. Repositions the intermediate scene using the tested **Center 12** XYOFFSET templates, with matching clear-rectangle coordinates.

The output continues sampling a 448-line area into a 224-line image, so the 480-line logical scene created by the 2× scale is not fully displayed. The approximate effective crop is **3 source lines at one edge and 13 at the other** (16 total). The actual picture edge depends on the game's TATE orientation and subpixel positioning.

## Why the full-frame expansion is not included

An experimental expansion branch investigated a 480-line intermediate framebuffer, a 480-line viewport, clamping beyond source row 447, and a future 480→240 compositor. A GS-replay clamp change corrected repeated bottom rows; however, live Stage 5 ISO experiments still showed black bars and reintroduced horizontal stripes when compressing 480 lines to 224. The prerelease therefore remains on the tested 448→224 final path and its limited picture crop.

A true 240-line restoration will require coordinated changes to live gameplay scissor generation, framebuffer/depth-buffer allocation and any conflicting texture destinations, final UV and output geometry, display registers and field state. Enlarging one component independently is insufficient.

## Shared code versus shared fixes

The two games share parts of their PS2 graphics initialization and supporting code, likely including SDK-related routines. Their **rendering errors are not identical**: Ibara is principally improved by a final 240→224 crop; Mushihimesama is improved by changing an upstream 1.8× scale to 2×. The shared patcher reuses file handling and verification; it does *not* apply one game's offsets to the other.
