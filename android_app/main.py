from pathlib import Path
import hashlib
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.utils import platform

KV = """
<RootUI>:
    orientation: "vertical"
    padding: "14dp"
    spacing: "10dp"
    canvas.before:
        Color:
            rgba: (.05, .07, .12, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "[b]ROMTRAN[/b] [color=55d6be]GBA Edition[/color]"
        markup: True
        font_size: "25sp"
        size_hint_y: None
        height: "54dp"
    Label:
        text: "เครื่องมือวิเคราะห์ ROM และเตรียมแปลเกม"
        size_hint_y: None
        height: "32dp"
    Button:
        text: "เลือกไฟล์ ROM (.gba)"
        size_hint_y: None
        height: "50dp"
        on_release: root.open_picker()
    Label:
        id: file_label
        text: "ยังไม่ได้เลือกไฟล์"
        text_size: self.width, None
        halign: "left"
        size_hint_y: None
        height: "55dp"
    Button:
        text: "วิเคราะห์ ROM"
        size_hint_y: None
        height: "50dp"
        on_release: root.analyze_rom()
    TextInput:
        id: output
        text: "ผลการวิเคราะห์จะแสดงที่นี่"
        readonly: True
        multiline: True
    Label:
        text: "รุ่นเริ่มต้นอ่านอย่างเดียว ไม่เขียนทับ ROM"
        size_hint_y: None
        height: "36dp"
"""
class RootUI(BoxLayout):
    selected_path = None
    def open_picker(self):
        start = "/storage/emulated/0/Download" if platform == "android" else str(Path.home())
        chooser = FileChooserListView(path=start, filters=["*.gba", "*.GBA", "*.bin", "*.BIN"])
        box = BoxLayout(orientation="vertical", spacing="8dp", padding="8dp")
        box.add_widget(chooser)
        row = BoxLayout(size_hint_y=None, height="46dp", spacing="8dp")
        popup = Popup(title="เลือกไฟล์ ROM", content=box, size_hint=(.95,.9))
        cancel = Button(text="ยกเลิก")
        choose = Button(text="เลือกไฟล์")
        cancel.bind(on_release=popup.dismiss)
        def selected(*_):
            if chooser.selection:
                self.selected_path = chooser.selection[0]
                self.ids.file_label.text = self.selected_path
                self.ids.output.text = "เลือกไฟล์แล้ว กดวิเคราะห์ ROM"
                popup.dismiss()
        choose.bind(on_release=selected)
        row.add_widget(cancel); row.add_widget(choose); box.add_widget(row); popup.open()
    def analyze_rom(self):
        if not self.selected_path:
            self.ids.output.text = "กรุณาเลือกไฟล์ ROM ก่อน"
            return
        try:
            p=Path(self.selected_path); size=p.stat().st_size
            with p.open("rb") as f:
                f.seek(0xA0); h=f.read(0x20)
            title=h[:12].decode("ascii","replace").strip("\\x00 ")
            code=h[12:16].decode("ascii","replace")
            maker=h[16:18].decode("ascii","replace")
            digest=hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda:f.read(1024*1024),b""): digest.update(chunk)
            self.ids.output.text=(f"วิเคราะห์แบบอ่านอย่างเดียว\\nไฟล์: {p.name}\\nขนาด: {size:,} bytes ({size/1048576:.2f} MiB)\\n"
              f"ชื่อเกม: {title or '(อ่านไม่ได้)'}\\nGame Code: {code}\\nMaker Code: {maker}\\nSHA-256: {digest.hexdigest()}\\n\\n"
              "พื้นที่ว่างและตารางอักขระยังไม่ได้รับการยืนยัน แอปยังไม่แก้ไข ROM")
        except Exception as e: self.ids.output.text=f"อ่านไฟล์ไม่สำเร็จ: {e}"
class RomtranApp(App):
    def build(self):
        Builder.load_string(KV); self.title="Romtran GBA Edition"; return RootUI()
if __name__ == "__main__": RomtranApp().run()
