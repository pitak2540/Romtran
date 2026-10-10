"""Read-only helpers for inspecting Game Boy Advance ROM images."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RomInfo:
    path: str
    size_bytes: int
    title: str
    game_code: str
    maker_code: str
    version: int
    header_checksum: int
    checksum_valid: bool


def analyze_rom_bytes(data: bytes, path: str = "<memory>") -> RomInfo:
    """Read basic GBA header fields. This function never modifies ROM data."""
    if len(data) < 0xC0:
        raise ValueError("ไฟล์สั้นเกินไป: ROM GBA ต้องมีข้อมูลอย่างน้อย 0xC0 ไบต์")

    title = data[0xA0:0xAC].split(b"\x00", 1)[0].decode("ascii", errors="replace").strip()
    game_code = data[0xAC:0xB0].decode("ascii", errors="replace")
    maker_code = data[0xB0:0xB2].decode("ascii", errors="replace")
    version = data[0xBC]
    header_checksum = data[0xBD]
    expected = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF

    return RomInfo(
        path=path,
        size_bytes=len(data),
        title=title,
        game_code=game_code,
        maker_code=maker_code,
        version=version,
        header_checksum=header_checksum,
        checksum_valid=(header_checksum == expected),
    )


def analyze_rom_file(path: str | Path) -> RomInfo:
    rom_path = Path(path)
    return analyze_rom_bytes(rom_path.read_bytes(), str(rom_path))


def find_ff_free_space(data: bytes, min_length: int = 0x100, limit: int = 50) -> list[tuple[int, int]]:
    """Return (offset, length) for long 0xFF runs; heuristic only."""
    if min_length < 1:
        raise ValueError("min_length ต้องมากกว่า 0")
    if limit < 1:
        return []

    matches: list[tuple[int, int]] = []
    index = 0
    while index < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        start = index
        while index < len(data) and data[index] == 0xFF:
            index += 1
        length = index - start
        if length >= min_length:
            matches.append((start, length))
    matches.sort(key=lambda item: item[1], reverse=True)
    return matches[:limit]
