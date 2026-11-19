"""Standard-library tests. Optional IBARA_ELF / MUSHI_ELF can exercise real references."""
from __future__ import annotations

import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cave_ps2_progressive as patcher


def make_dir_rec(extent: int, length: int, name: bytes, flags: int = 0) -> bytes:
    rec_len = 33 + len(name) + (1 if len(name) % 2 == 0 else 0)
    rec = bytearray(rec_len)
    rec[0] = rec_len
    rec[1] = 0
    rec[2:6] = extent.to_bytes(4, "little")
    rec[6:10] = extent.to_bytes(4, "big")
    rec[10:14] = length.to_bytes(4, "little")
    rec[14:18] = length.to_bytes(4, "big")
    rec[25] = flags
    rec[28:30] = b"\x01\x00"
    rec[30:32] = b"\x00\x01"
    rec[32] = len(name)
    rec[33:33+len(name)] = name
    return bytes(rec)


def make_iso(elf: bytes, game: dict, target: Path) -> None:
    root_sector = 20
    elf_sector = 32
    count = elf_sector + (len(elf) + patcher.SECTOR - 1) // patcher.SECTOR
    with target.open("wb") as f:
        f.truncate(count * patcher.SECTOR)
        pvd = bytearray(patcher.SECTOR)
        pvd[:7] = b"\x01CD001\x01"
        pvd[128:130] = patcher.SECTOR.to_bytes(2, "little")
        pvd[130:132] = patcher.SECTOR.to_bytes(2, "big")
        pvd[156:190] = make_dir_rec(root_sector, patcher.SECTOR, b"\x00", 2)[:34]
        f.seek(16*patcher.SECTOR)
        f.write(pvd)
        dir_data = (make_dir_rec(root_sector, patcher.SECTOR, b"\x00", 2) +
                    make_dir_rec(root_sector, patcher.SECTOR, b"\x01", 2) +
                    make_dir_rec(elf_sector, len(elf), game["boot_names"][0] + b";1"))
        f.seek(root_sector*patcher.SECTOR)
        f.write(dir_data)
        f.seek(elf_sector*patcher.SECTOR)
        f.write(elf)


class PatchTests(unittest.TestCase):
    def test_proposed_release_names(self):
        self.assertEqual(patcher.GAMES["ibara"]["output_name"],
                         "SLPM_663.01.Ibara (240p v0.1.0-beta.1).iso")
        self.assertEqual(patcher.GAMES["mushi"]["output_name"],
                         "SLPM_660.56.Mushihimesama (240p v0.1.0-beta.1).iso")

    def test_crc(self):
        self.assertEqual(patcher.elf_xor_crc(b"\x01\x00\x00\x00\x02\x00\x00\x00"), 3)
        with self.assertRaises(ValueError):
            patcher.elf_xor_crc(b"\x01")

    def test_hash_rejection(self):
        for game in patcher.GAMES.values():
            with self.assertRaises(ValueError):
                patcher.patch_elf(b"\x7fELF" + bytes(game["elf_size"] - 4), game)

    def test_iso_scanner_and_unmodified_guard(self):
        game = patcher.GAMES["ibara"]
        fake_elf = b"\x7fELF" + bytes(game["elf_size"]-4)
        with tempfile.TemporaryDirectory() as td:
            iso = Path(td) / game["input_name"]
            make_iso(fake_elf, game, iso)
            with iso.open("rb") as f:
                at, size = patcher.find_boot_elf(f, game)
                self.assertEqual(size, len(fake_elf))
                f.seek(at)
                self.assertEqual(f.read(4), b"\x7fELF")
            with self.assertRaises(ValueError):
                patcher.identify_game(iso)
            self.assertEqual(patcher.default_inputs(Path(td)), [iso])

    def test_optional_real_elf_end_to_end(self):
        available = [(key, os.getenv("IBARA_ELF" if key == "ibara" else "MUSHI_ELF"))
                     for key in patcher.GAMES]
        if not all(path and Path(path).is_file() for _, path in available):
            self.skipTest("Set IBARA_ELF and MUSHI_ELF to test original game data locally")
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            baselines = {}
            for key, path in available:
                game = patcher.GAMES[key]
                data = Path(path).read_bytes()
                self.assertEqual(patcher.sha256(data), game["original_sha256"])
                iso = folder / game["input_name"]
                make_iso(data, game, iso)
                baselines[key] = iso.read_bytes()
            self.assertEqual(patcher.main(["--input-dir", str(folder), "--dry-run"]), 0)
            self.assertEqual(patcher.main(["--input-dir", str(folder)]), 0)
            for key, game in patcher.GAMES.items():
                source = folder / game["input_name"]
                dest = folder / game["output_name"]
                self.assertTrue(dest.exists())
                self.assertEqual(source.read_bytes(), baselines[key])
                with dest.open("rb") as f:
                    off, size = patcher.find_boot_elf(f, game)
                    f.seek(off)
                    self.assertEqual(patcher.sha256(f.read(size)), game["patched_sha256"])
                self.assertEqual(dest.stat().st_size, source.stat().st_size)
            # Fail closed: never clobber existing output files.
            self.assertEqual(patcher.main(["--input-dir", str(folder)]), 1)


if __name__ == "__main__":
    unittest.main()
