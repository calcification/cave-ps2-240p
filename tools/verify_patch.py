#!/usr/bin/env python3
"""Read-only SHA-256/CRC verification for Cave/Taito patched or original ISOs."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cave_ps2_progressive import GAMES, elf_xor_crc, find_boot_elf, sha256  # noqa: E402


def inspect(path: Path) -> int:
    if not path.is_file():
        print(f"Not found: {path}", file=sys.stderr)
        return 1
    with path.open("rb") as f:
        for game in GAMES.values():
            try:
                base, size = find_boot_elf(f, game)
            except ValueError:
                continue
            f.seek(base)
            elf = f.read(size)
            digest = sha256(elf)
            if digest == game["original_sha256"]:
                profile = "unmodified original"
            elif digest == game["patched_sha256"]:
                profile = "verified v0.1.0-beta.1 prerelease patch"
            else:
                print(f"{game['title']}: found executable but UNKNOWN SHA-256 {digest}")
                return 1
            print(f"Game: {game['title']}")
            print(f"Profile: {profile}")
            print(f"ELF SHA-256: {digest}")
            print(f"ELF XOR CRC: {elf_xor_crc(elf):08X}")
            print("Verified ELF bytes, not entire ISO contents or runtime compatibility.")
            return 0
    print("No supported boot ELF found", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("iso", type=Path)
    args = ap.parse_args()
    return inspect(args.iso)


if __name__ == "__main__":
    sys.exit(main())
