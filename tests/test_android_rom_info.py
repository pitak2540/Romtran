import hashlib
import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "android_app"))

from rom_info import analyze_stream, format_report  # noqa: E402


def make_rom(title=b"0X TEST ROM\x00", size=0x2000):
    data = bytearray(b"\xff" * size)
    data[0xA0:0xAC] = title.ljust(12, b"\x00")
    data[0xAC:0xB0] = b"AXVE"
    data[0xB0:0xB2] = b"01"
    data[0xBC] = 1
    data[0xBD] = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    return bytes(data)


def test_reads_header_and_hash():
    rom = make_rom()
    info = analyze_stream(io.BytesIO(rom), "test.gba")
    # Titles starting with "0" or "x" must not lose characters.
    assert info["title"] == "0X TEST ROM"
    assert info["game_code"] == "AXVE"
    assert info["maker_code"] == "01"
    assert info["size"] == len(rom)
    assert info["checksum_valid"] is True
    assert info["sha256"] == hashlib.sha256(rom).hexdigest()


def test_report_uses_real_newlines():
    report = format_report(analyze_stream(io.BytesIO(make_rom()), "test.gba"))
    assert "\\n" not in report
    assert report.count("\n") >= 8
    assert "ไฟล์: test.gba" in report


def test_rejects_short_file():
    with pytest.raises(ValueError):
        analyze_stream(io.BytesIO(b"\x00" * 16))
