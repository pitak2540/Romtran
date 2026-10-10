"""Read-only GBA ROM inspection that works on any binary stream.

Kept free of Kivy/Android imports so it can be tested on a desktop.
"""
import hashlib

HEADER_END = 0xC0
CHUNK = 1024 * 1024


def analyze_stream(stream, name="ROM"):
    """Read a ROM from a binary file object and return its basic facts.

    Never writes to the stream. Raises ValueError if the file is too short.
    """
    digest = hashlib.sha256()
    head = b""
    size = 0
    for chunk in iter(lambda: stream.read(CHUNK), b""):
        if len(head) < HEADER_END:
            head += chunk[: HEADER_END - len(head)]
        digest.update(chunk)
        size += len(chunk)
    if size < HEADER_END:
        raise ValueError("ไฟล์สั้นเกินไป ไม่ใช่ ROM ของ GBA")

    title = head[0xA0:0xAC].split(b"\x00", 1)[0].decode("ascii", "replace").strip()
    expected = (-sum(head[0xA0:0xBD]) - 0x19) & 0xFF
    return {
        "name": name,
        "size": size,
        "title": title,
        "game_code": head[0xAC:0xB0].decode("ascii", "replace"),
        "maker_code": head[0xB0:0xB2].decode("ascii", "replace"),
        "version": head[0xBC],
        "checksum_valid": head[0xBD] == expected,
        "sha256": digest.hexdigest(),
    }


def format_report(info):
    checksum = "ถูกต้อง" if info["checksum_valid"] else "ไม่ถูกต้อง (อาจไม่ใช่ ROM GBA หรือถูกแก้ไขมาแล้ว)"
    return "\n".join(
        [
            "วิเคราะห์แบบอ่านอย่างเดียว",
            f"ไฟล์: {info['name']}",
            f"ขนาด: {info['size']:,} bytes ({info['size'] / 1048576:.2f} MiB)",
            f"ชื่อเกม: {info['title'] or '(อ่านไม่ได้)'}",
            f"Game Code: {info['game_code']}",
            f"Maker Code: {info['maker_code']}",
            f"เวอร์ชัน: {info['version']}",
            f"Header checksum: {checksum}",
            f"SHA-256: {info['sha256']}",
            "",
            "พื้นที่ว่างและตารางอักขระยังไม่ได้รับการยืนยัน แอปยังไม่แก้ไข ROM",
        ]
    )
