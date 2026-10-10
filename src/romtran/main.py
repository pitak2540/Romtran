"""Initial GUI for ROM Translator — GBA Edition."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox,
    QPushButton, QPlainTextEdit, QVBoxLayout, QWidget,
)

from .rom_analysis import analyze_rom_file, find_ff_free_space


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ROM Translator — GBA Edition")
        self.resize(820, 600)
        self.status = QLabel("เลือกไฟล์ ROM สำหรับตรวจสอบ (โหมดอ่านอย่างเดียว)")
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.open_button = QPushButton("เปิดไฟล์ ROM…")
        self.open_button.clicked.connect(self.open_rom)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.open_button)
        layout.addWidget(self.output)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def open_rom(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "เลือก ROM", "", "ROM files (*.gba *.bin *.rom);;All files (*)"
        )
        if not filename:
            return
        try:
            info = analyze_rom_file(filename)
            data = Path(filename).read_bytes()
            free_runs = find_ff_free_space(data, min_length=0x100, limit=20)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "เปิด ROM ไม่สำเร็จ", str(exc))
            return

        lines = [
            f"ไฟล์: {info.path}",
            f"ขนาด: {info.size_bytes:,} bytes ({info.size_bytes / 1024 / 1024:.2f} MiB)",
            f"ชื่อเกม: {info.title or '(ไม่พบชื่อ)'}",
            f"Game code: {info.game_code}",
            f"Maker code: {info.maker_code}",
            f"ROM version: {info.version}",
            f"Header checksum: 0x{info.header_checksum:02X} — {'ผ่าน' if info.checksum_valid else 'ไม่ตรง'}",
            "",
            "ช่วง 0xFF ที่อาจว่าง (เป็นการคัดกรองเบื้องต้น ไม่ยืนยันว่าปลอดภัยสำหรับเขียนข้อมูล):",
        ]
        if free_runs:
            lines.extend(
                f"  Offset 0x{offset:08X} | {length:,} bytes (0x{length:X})"
                for offset, length in free_runs
            )
        else:
            lines.append("  ไม่พบช่วง 0xFF ตามขนาดขั้นต่ำที่กำหนด")
        self.output.setPlainText("\n".join(lines))
        self.status.setText("ตรวจสอบเสร็จแล้ว — ต้นฉบับไม่ได้ถูกแก้ไข")


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
