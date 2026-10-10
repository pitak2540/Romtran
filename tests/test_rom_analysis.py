from romtran.rom_analysis import analyze_rom_bytes, find_ff_free_space


def make_test_rom() -> bytes:
    data = bytearray(0x400)
    data[0xA0:0xAC] = b"TEST GAME   "
    data[0xAC:0xB0] = b"ABCD"
    data[0xB0:0xB2] = b"01"
    data[0xBC] = 0
    data[0xBD] = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    data[0x200:0x300] = b"\xFF" * 0x100
    return bytes(data)


def test_reads_gba_header_and_checksum():
    info = analyze_rom_bytes(make_test_rom())
    assert info.title == "TEST GAME"
    assert info.game_code == "ABCD"
    assert info.checksum_valid


def test_rejects_too_short_input():
    try:
        analyze_rom_bytes(b"short")
    except ValueError as exc:
        assert "สั้นเกินไป" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_finds_ff_run():
    assert (0x200, 0x100) in find_ff_free_space(make_test_rom(), min_length=0x100)
