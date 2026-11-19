# Patch specification — `v0.1.0-beta.1`

This is a byte-level reference for the combined patcher. **Do not apply RAM addresses from one game to the other.**

All edited instructions are little-endian 32-bit MIPS words. For both supplied original executables:

```text
ELF file offset = 0x80 + (EE RAM address - 0x00100000)
```

The ELF SHA-256, edit-word validation, output SHA-256 and XOR checksum are checked before the patcher writes a new ISO.

## Ibara

- Original ELF SHA-256: `263d3079dee66af82815219351553075340a4d9f42aceaa7bb8ef2bfb812ffac`
- Expected patched ELF SHA-256: `fdf8a518107fe19abdd2a673a2d525827c01f5137157847cb565d3bbd483afa6`
- Patched ELF XOR checksum / PCSX2 CRC: `420F7FCA`
- Original ELF size: `2,329,648` bytes

| EE RAM | ELF offset | Original | Patched | Purpose |
|---|---|---|---|---|
| `0x001AD250` | `0xAD2D0` | `24050001` | `24050000` | noninterlaced ResetGraph |
| `0x001AF11C` | `0xAF19C` | `24040060` | `24040000` | nearest-neighbor final pass |
| `0x001B29D4` | `0xB2A54` | `AF829574` | `AF809574` | field-state initialization |
| `0x001B2A60` | `0xB2AE0` | `AF839550` | `AF809550` | vblank field-state update |
| `0x001B2A80` | `0xB2B00` | `AF829574` | `AF809574` | vblank field-state update |
| `0x001DD1C0` | `0xDD240` | `00000000` | `00000008` | final-pass UV starting edge |
| `0x001DD1C8` | `0xDD248` | `00000000` | `00000008` | final-pass UV starting edge |
| `0x001DD1D0` | `0xDD250` | `000000F0` | `000000E8` | final-pass UV ending edge |
| `0x001DD1D8` | `0xDD258` | `000000F0` | `000000E8` | final-pass UV ending edge |
| `0x001DD200` | `0xDD280` | `00000000` | `00000008` | final-pass UV starting edge |
| `0x001DD208` | `0xDD288` | `00000000` | `00000008` | final-pass UV starting edge |
| `0x001DD210` | `0xDD290` | `000000F0` | `000000E8` | final-pass UV ending edge |
| `0x001DD218` | `0xDD298` | `000000F0` | `000000E8` | final-pass UV ending edge |
| `0x001DD240` | `0xDD2C0` | `00000000` | `00000008` | final-pass UV starting edge |
| `0x001DD248` | `0xDD2C8` | `00000000` | `00000008` | final-pass UV starting edge |
| `0x001DD250` | `0xDD2D0` | `000000F0` | `000000E8` | final-pass UV ending edge |
| `0x001DD258` | `0xDD2D8` | `000000F0` | `000000E8` | final-pass UV ending edge |
| `0x001AECD4` | `0xAED54` | `24AA7900` | `24AA78F8` | final-quad half-pixel alignment |
| `0x001AED3C` | `0xAEDBC` | `26527900` | `265278F8` | final-quad half-pixel alignment |
| `0x001AED88` | `0xAEE08` | `24427900` | `244278F8` | final-quad half-pixel alignment |
| `0x001AEDD4` | `0xAEE54` | `24427900` | `244278F8` | final-quad half-pixel alignment |

### Ibara source UV geometry

- Three mode-specific final-pass UV tables each change `0..240` to `8..232` (8 source rows cropped from each edge).
- Half-pixel quad alignment is included, along with three field-state instructions. These are experimental and do not remove all shimmer.

## Mushihimesama

- Original ELF SHA-256: `98279df72756d3aa29b45c5fc0b5a5d86acee0c96723a0aac1995ebd9817a77a`
- Expected patched ELF SHA-256: `c3cd8f3eab5c2d1ca9e84aafc12a0e1d9a2497cea1cacc3437a726d772e82f78`
- Patched ELF XOR checksum / PCSX2 CRC: `F4C14BD0`
- Original ELF size: `2,427,312` bytes

| EE RAM | ELF offset | Original | Patched | Purpose |
|---|---|---|---|---|
| `0x0029CEF8` | `0x19CF78` | `24050001` | `24050000` | noninterlaced ResetGraph |
| `0x0010BD28` | `0xBDA8` | `32240001` | `20040000` | SetGsCrt interlace (call 1) |
| `0x0010BD84` | `0xBE04` | `32240001` | `24040000` | SetGsCrt interlace (call 2) |
| `0x002A2C84` | `0x1A2D04` | `AF82866C` | `AF80866C` | field-state initialization |
| `0x002A2D14` | `0x1A2D94` | `AF83864C` | `AF80864C` | vblank field-state update |
| `0x002A2D34` | `0x1A2DB4` | `AF82866C` | `AF80866C` | vblank field-state update |
| `0x0029EDF4` | `0x19EE74` | `24040060` | `24040000` | nearest-neighbor final pass |
| `0x0013003C` | `0x300BC` | `3C033FE6` | `3C034000` | 1.8f -> 2.0f (part 1) |
| `0x00130044` | `0x300C4` | `34636666` | `34630000` | 1.8f -> 2.0f (part 2) |
| `0x00134A40` | `0x34AC0` | `3C023FE6` | `3C024000` | 1.8f -> 2.0f (part 1) |
| `0x00134A48` | `0x34AC8` | `34446666` | `34440000` | 1.8f -> 2.0f (part 2) |
| `0x00136E48` | `0x36EC8` | `3C063FE6` | `3C064000` | 1.8f -> 2.0f (part 1) |
| `0x00136E50` | `0x36ED0` | `34C66666` | `34C60000` | 1.8f -> 2.0f (part 2) |
| `0x00136F08` | `0x36F88` | `3C063FE6` | `3C064000` | 1.8f -> 2.0f (part 1) |
| `0x00136F0C` | `0x36F8C` | `34C86666` | `34C80000` | 1.8f -> 2.0f (part 2) |

### Center-12 GS data changes

- Two `XYOFFSET_1` templates at ELF offsets `0x244974` and `0x24B5A4`: origin OFY `0x7200 → 0x72C0` (12 intermediate pixels).
- One 10-strip framebuffer clear packet at ELF offset `0x244660`: all 20 vertex-Y halfwords shift up by 12 intermediate pixels in GS output-space.
- The result matches the previously tested Center-12 ELF hash exactly. The 480-line expansion experiments are **not** included.
- The progressive patch intentionally leaves the offscreen-to-output compositor at 448→224 (exact 2:1).

## Original binaries are not distributed

The executable SHA-256 values above were calculated from the original game executables supplied for investigation. Neither executable nor any patched binary is included in this repository.
