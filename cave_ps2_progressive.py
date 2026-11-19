#!/usr/bin/env python3
"""Cave/Taito PS2 native 240p prerelease patcher (Ibara and Mushihimesama).

Default: search the current directory for exactly named original ISOs:
    Ibara (Japan).iso
    Mushihimesama (Japan).iso

Run:
    python3 cave_ps2_progressive.py
    python3 cave_ps2_progressive.py "Ibara (Japan).iso"
    python3 cave_ps2_progressive.py --dry-run

Outputs are always NEW ISOs. Original games, ELFs, and copyrighted assets are not included.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile

VERSION = "v0.1.0-beta.1"
SECTOR = 2048
RAM_BASE = 0x100000
ELF_LOAD_OFFSET = 0x80

# Entries: (EE RAM address, expected original u32, replacement u32, explanation)
IBARA_PATCHES = [
    (0x1AD250, 0x24050001, 0x24050000, "noninterlaced ResetGraph"),
    (0x1AF11C, 0x24040060, 0x24040000, "nearest-neighbor final pass"),
    (0x1B29D4, 0xAF829574, 0xAF809574, "field-state initialization"),
    (0x1B2A60, 0xAF839550, 0xAF809550, "vblank field-state update"),
    (0x1B2A80, 0xAF829574, 0xAF809574, "vblank field-state update"),
]
for _uv_table in (0x1DD1C0, 0x1DD200, 0x1DD240):
    IBARA_PATCHES.extend(( _uv_table + delta, old, new, desc)
        for delta, old, new, desc in (
            (0x00, 0, 8, "final-pass UV starting edge"),
            (0x08, 0, 8, "final-pass UV starting edge"),
            (0x10, 240, 232, "final-pass UV ending edge"),
            (0x18, 240, 232, "final-pass UV ending edge"),
        ))
IBARA_PATCHES.extend([
    (0x1AECD4, 0x24AA7900, 0x24AA78F8, "final-quad half-pixel alignment"),
    (0x1AED3C, 0x26527900, 0x265278F8, "final-quad half-pixel alignment"),
    (0x1AED88, 0x24427900, 0x244278F8, "final-quad half-pixel alignment"),
    (0x1AEDD4, 0x24427900, 0x244278F8, "final-quad half-pixel alignment"),
])

MUSHI_PATCHES = [
    (0x29CEF8, 0x24050001, 0x24050000, "noninterlaced ResetGraph"),
    (0x10BD28, 0x32240001, 0x20040000, "SetGsCrt interlace (call 1)"),
    (0x10BD84, 0x32240001, 0x24040000, "SetGsCrt interlace (call 2)"),
    (0x2A2C84, 0xAF82866C, 0xAF80866C, "field-state initialization"),
    (0x2A2D14, 0xAF83864C, 0xAF80864C, "vblank field-state update"),
    (0x2A2D34, 0xAF82866C, 0xAF80866C, "vblank field-state update"),
    (0x29EDF4, 0x24040060, 0x24040000, "nearest-neighbor final pass"),
    (0x13003C, 0x3C033FE6, 0x3C034000, "1.8f -> 2.0f (part 1)"),
    (0x130044, 0x34636666, 0x34630000, "1.8f -> 2.0f (part 2)"),
    (0x134A40, 0x3C023FE6, 0x3C024000, "1.8f -> 2.0f (part 1)"),
    (0x134A48, 0x34446666, 0x34440000, "1.8f -> 2.0f (part 2)"),
    (0x136E48, 0x3C063FE6, 0x3C064000, "1.8f -> 2.0f (part 1)"),
    (0x136E50, 0x34C66666, 0x34C60000, "1.8f -> 2.0f (part 2)"),
    (0x136F08, 0x3C063FE6, 0x3C064000, "1.8f -> 2.0f (part 1)"),
    (0x136F0C, 0x34C86666, 0x34C80000, "1.8f -> 2.0f (part 2)"),
]
# Fixed prerelease profile: the visually tested Center-12 setup only.
MUSHI_ORIGIN_SHIFT = 12
MUSHI_XYOFF_FILE_OFFSETS = (0x244974, 0x24B5A4)
MUSHI_CLEAR_PACKET_FILE_OFFSET = 0x244660
MUSHI_CLEAR_VERTEX_OFFSETS = tuple(range(0x20, 0x90, 8)) + tuple(range(0xA0, 0xD0, 8))

GAMES = {
    "ibara": {
        "title": "Ibara", "input_name": "Ibara (Japan).iso",
        "boot_names": (b"SLPM_663.01",),
        "elf_size": 2329648,
        "original_sha256": "263d3079dee66af82815219351553075340a4d9f42aceaa7bb8ef2bfb812ffac",
        "patched_sha256": "fdf8a518107fe19abdd2a673a2d525827c01f5137157847cb565d3bbd483afa6",
        "patched_crc": 0x420F7FCA,
        "output_name": f"SLPM_663.01.Ibara (240p {VERSION}).iso",
        "patches": IBARA_PATCHES,
    },
    "mushi": {
        "title": "Mushihimesama", "input_name": "Mushihimesama (Japan).iso",
        "boot_names": (b"SLPM_660.56", b"SLPM_660_1.56"),
        "elf_size": 2427312,
        "original_sha256": "98279df72756d3aa29b45c5fc0b5a5d86acee0c96723a0aac1995ebd9817a77a",
        "patched_sha256": "c3cd8f3eab5c2d1ca9e84aafc12a0e1d9a2497cea1cacc3437a726d772e82f78",
        "patched_crc": 0xF4C14BD0,
        "output_name": f"SLPM_660.56.Mushihimesama (240p {VERSION}).iso",
        "patches": MUSHI_PATCHES,
    },
}


def elf_offset(ram_address: int) -> int:
    return ELF_LOAD_OFFSET + ram_address - RAM_BASE


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def elf_xor_crc(data: bytes) -> int:
    if len(data) % 4:
        raise ValueError("ELF length is not a multiple of 4")
    crc = 0
    for (word,) in struct.iter_unpack("<I", data):
        crc ^= word
    return crc


def patch_elf(data: bytes, game: dict) -> bytes:
    if len(data) != game["elf_size"] or data[:4] != b"\x7fELF":
        raise ValueError(f"{game['title']}: not the expected boot ELF")
    if sha256(data) != game["original_sha256"]:
        raise ValueError(f"{game['title']}: unknown/revised/previously patched executable SHA-256. "
                         "Use the unmodified original Japanese release; refusing to patch.")
    out = bytearray(data)
    for addr, old, new, desc in game["patches"]:
        pos = elf_offset(addr)
        actual = struct.unpack_from("<I", out, pos)[0]
        if actual != old:
            raise ValueError(f"{game['title']}, {desc}, EE 0x{addr:X}: "
                             f"expected {old:08X}, found {actual:08X}")
        struct.pack_into("<I", out, pos, new)
    if game["title"] == "Mushihimesama":
        patch_mushi_center12(out)
    result = bytes(out)
    if sha256(result) != game["patched_sha256"] or elf_xor_crc(result) != game["patched_crc"]:
        raise ValueError(f"{game['title']}: output verification failed; no ISO will be written")
    return result


def patch_mushi_center12(out: bytearray) -> None:
    """Update the active XYOFFSET templates and the accompanying 10 clear rectangles."""
    shift16 = MUSHI_ORIGIN_SHIFT * 16
    for off in MUSHI_XYOFF_FILE_OFFSETS:
        if struct.unpack_from("<I", out, off - 4)[0] != 0x6C00 or \
           struct.unpack_from("<Q", out, off + 4)[0] != 0x18 or \
           struct.unpack_from("<I", out, off)[0] != 0x7200:
            raise ValueError(f"Mushihimesama: unexpected XYOFFSET template at 0x{off:X}")
        struct.pack_into("<I", out, off, 0x7200 + shift16)

    hdr = bytes.fromhex("01000000000000041055555555555555")
    hdr2 = bytes.fromhex("01800000000000645555550000000000")
    p = MUSHI_CLEAR_PACKET_FILE_OFFSET
    if bytes(out[p:p + 16]) != hdr or bytes(out[p + 0x90:p + 0xA0]) != hdr2:
        raise ValueError("Mushihimesama: unexpected GS clear-packet headers")
    for j, rel in enumerate(MUSHI_CLEAR_VERTEX_OFFSETS):
        pos = p + rel
        x, y, z = struct.unpack_from("<HHI", out, pos)
        expected_x = 0x6C00 + (j // 2 + j % 2) * 0x400
        expected_y = 0x7200 if j % 2 == 0 else 0x8E00
        if (x, y, z) != (expected_x, expected_y, 0):
            raise ValueError(f"Mushihimesama: unexpected clear vertex {j} at 0x{pos:X}")
        struct.pack_into("<H", out, pos + 2, y + shift16)


def _extent(rec: bytes) -> tuple[int, int]:
    if len(rec) < 34:
        raise ValueError("Malformed ISO9660 directory entry")
    if rec[1] or rec[26] or rec[27] or (rec[25] & 0x80):
        raise ValueError("Unsupported ISO9660 extent")
    lba = struct.unpack_from("<I", rec, 2)[0]
    size = struct.unpack_from("<I", rec, 10)[0]
    if lba != int.from_bytes(rec[6:10], "big") or size != int.from_bytes(rec[14:18], "big"):
        raise ValueError("Inconsistent ISO9660 extent")
    return lba * SECTOR, size


def find_boot_elf(f, game: dict) -> tuple[int, int]:
    """Locate the game's own boot ELF in a raw ISO9660 sector-2048 ISO file."""
    f.seek(16 * SECTOR)
    pvd = f.read(SECTOR)
    if len(pvd) != SECTOR or pvd[:7] != b"\x01CD001\x01":
        raise ValueError("Only raw 2048-byte-sector ISO9660 images are supported")
    if int.from_bytes(pvd[128:130], "little") != SECTOR:
        raise ValueError("ISO9660 logical block size is not 2048 bytes")
    root = pvd[156:190]
    root_at, root_len = _extent(root)
    pending = [(root_at, root_len)]
    seen = set()
    while pending:
        at, size = pending.pop()
        if at in seen:
            continue
        seen.add(at)
        if not 0 < size <= 16 * 1024 * 1024:
            raise ValueError("Unsupported ISO9660 directory size")
        f.seek(at)
        directory = f.read(size)
        if len(directory) != size:
            raise ValueError("Truncated ISO9660 directory")
        off = 0
        while off < size:
            n = directory[off]
            if n == 0:
                off = (off // SECTOR + 1) * SECTOR
                continue
            if off + n > size:
                raise ValueError("Truncated ISO9660 directory entry")
            rec = directory[off:off + n]
            if len(rec) < 34 or 33 + rec[32] > len(rec):
                raise ValueError("Malformed ISO9660 directory record")
            entry_name = rec[33:33 + rec[32]].split(b";", 1)[0].upper()
            is_dir = bool(rec[25] & 2)
            if entry_name not in (b"\x00", b"\x01"):
                pos, length = _extent(rec)
                if is_dir:
                    pending.append((pos, length))
                elif entry_name in game["boot_names"]:
                    if length != game["elf_size"]:
                        raise ValueError(f"Boot ELF has unexpected size {length}")
                    return pos, length
            off += n
    raise ValueError(f"{game['title']} boot ELF not found (wrong game/region or bad ISO)")


def identify_game(path: Path) -> tuple[str, dict]:
    """Identify the ISO by the actual disc executable, not just the filename."""
    with path.open("rb") as f:
        for key, game in GAMES.items():
            try:
                at, length = find_boot_elf(f, game)
            except ValueError:
                continue
            f.seek(at)
            if sha256(f.read(length)) == game["original_sha256"]:
                return key, game
            raise ValueError(f"{path.name}: found {game['title']}, but the ELF hash isn't the original Japanese release")
    raise ValueError(f"{path.name}: not a supported original Japanese Ibara/Mushihimesama ISO")


def patch_iso(source: Path, output_dir: Path, dry_run: bool) -> tuple[Path, str, str]:
    key, game = identify_game(source)
    dest = output_dir / game["output_name"]
    if source.resolve() == dest.resolve():
        raise ValueError("Input and output paths cannot be identical")
    with source.open("rb") as f:
        base, length = find_boot_elf(f, game)
        f.seek(base)
        original = f.read(length)
    patched = patch_elf(original, game)
    if dest.exists() and not dry_run:
        raise FileExistsError(f"Output already exists: {dest}; refusing to overwrite it")
    if dry_run:
        return dest, key, sha256(patched)

    output_dir.mkdir(parents=True, exist_ok=True)
    staging = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".cave240p-", suffix=".iso.tmp",
                                         dir=output_dir, delete=False) as tmp:
            staging = Path(tmp.name)
            with source.open("rb") as inp:
                shutil.copyfileobj(inp, tmp, 4 * 1024 * 1024)
            tmp.flush()
            os.fsync(tmp.fileno())
        with staging.open("r+b") as dst:
            dst.seek(base)
            if dst.read(length) != original:
                raise ValueError("ISO changed while copying; aborting")
            dst.seek(base)
            dst.write(patched)
            dst.flush()
            os.fsync(dst.fileno())
            dst.seek(base)
            if sha256(dst.read(length)) != game["patched_sha256"]:
                raise ValueError("Patched ISO read-back verification failed")
        # Final file created only if a copy of all bytes passed. Never overwrite.
        os.link(staging, dest)
    finally:
        if staging is not None:
            staging.unlink(missing_ok=True)
    return dest, key, sha256(patched)


def default_inputs(directory: Path) -> list[Path]:
    return [directory / game["input_name"] for game in GAMES.values()
            if (directory / game["input_name"]).is_file()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("isos", nargs="*", type=Path, help="Original game ISO(s). Omit to auto-discover both filenames.")
    ap.add_argument("--input-dir", type=Path, default=Path("."),
                    help="Directory searched for the exact default filenames (default: current directory)")
    ap.add_argument("--output-dir", type=Path, default=None,
                    help="Output directory (default: alongside each source ISO)")
    ap.add_argument("--dry-run", action="store_true", help="Verify patches, but do not create files")
    ap.add_argument("--version", action="version", version=VERSION)
    args = ap.parse_args(argv)
    sources = args.isos or default_inputs(args.input_dir)
    if not sources:
        ap.error('No ISOs found. Place "Ibara (Japan).iso" and/or "Mushihimesama (Japan).iso" '
                 'in the current directory, or supply the ISO path(s) explicitly.')
    had_error = False
    seen_games: set[str] = set()
    for path in sources:
        try:
            if not path.is_file():
                raise FileNotFoundError(f"Input ISO not found: {path}")
            key, game = identify_game(path)
            if key in seen_games:
                raise ValueError(f"Duplicate {game['title']} input; supply each game only once")
            seen_games.add(key)
            dest_dir = args.output_dir or path.parent
            output, _, elf_hash = patch_iso(path, dest_dir, args.dry_run)
            print(f"[{game['title']}] {path.name}")
            print(f"  ELF SHA-256: {elf_hash}")
            print(f"  PCSX2 ELF XOR CRC: {game['patched_crc']:08X}")
            print(f"  {'Would write' if args.dry_run else 'Wrote and verified'}: {output}")
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            had_error = True
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
