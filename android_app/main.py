import os
from pathlib import Path

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.text import DEFAULT_FONT, LabelBase
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.utils import platform

from rom_info import analyze_stream, format_report

# Kivy's built-in font has no Thai glyphs, so ship one and make it the default.
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
LabelBase.register(
    DEFAULT_FONT,
    fn_regular=os.path.join(FONT_DIR, "Sarabun-Regular.ttf"),
    fn_bold=os.path.join(FONT_DIR, "Sarabun-Bold.ttf"),
)

PICK_ROM_REQUEST = 4201

if platform == "android":
    from android import activity as android_activity
    from jnius import autoclass

    Intent = autoclass("android.content.Intent")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")

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
    selected_path = None  # desktop: filesystem path
    selected_uri = None  # Android: content:// Uri from the system picker
    selected_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform == "android":
            android_activity.bind(on_activity_result=self._on_activity_result)

    # ---- choosing a file -------------------------------------------------
    def open_picker(self):
        if platform == "android":
            self._open_android_picker()
        else:
            self._open_desktop_picker()

    def _open_android_picker(self):
        # The system document picker needs no storage permission and works on
        # every Android version, including the Download folder on Android 13+.
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("*/*")
        try:
            PythonActivity.mActivity.startActivityForResult(intent, PICK_ROM_REQUEST)
        except Exception as e:
            self.ids.output.text = f"เปิดตัวเลือกไฟล์ไม่สำเร็จ: {e}"

    def _on_activity_result(self, request_code, result_code, intent):
        if request_code != PICK_ROM_REQUEST:
            return
        if result_code != -1 or intent is None:  # -1 == Activity.RESULT_OK
            return
        uri = intent.getData()
        if uri is None:
            return
        self._set_android_selection(uri, self._display_name(uri))

    @mainthread
    def _set_android_selection(self, uri, name):
        self.selected_uri = uri
        self.selected_path = None
        self._show_selected(name)

    @staticmethod
    def _display_name(uri):
        try:
            resolver = PythonActivity.mActivity.getContentResolver()
            cursor = resolver.query(uri, None, None, None, None)
            if cursor is not None:
                try:
                    index = cursor.getColumnIndex("_display_name")
                    if index >= 0 and cursor.moveToFirst():
                        name = cursor.getString(index)
                        if name:
                            return name
                finally:
                    cursor.close()
        except Exception:
            pass
        return uri.getLastPathSegment() or "ROM"

    def _open_desktop_picker(self):
        chooser = FileChooserListView(
            path=str(Path.home()), filters=["*.gba", "*.GBA", "*.bin", "*.BIN"]
        )
        box = BoxLayout(orientation="vertical", spacing="8dp", padding="8dp")
        box.add_widget(chooser)
        row = BoxLayout(size_hint_y=None, height="46dp", spacing="8dp")
        popup = Popup(title="เลือกไฟล์ ROM", content=box, size_hint=(0.95, 0.9))
        cancel = Button(text="ยกเลิก")
        choose = Button(text="เลือกไฟล์")
        cancel.bind(on_release=popup.dismiss)

        def selected(*_):
            if chooser.selection:
                self.selected_path = chooser.selection[0]
                self.selected_uri = None
                self._show_selected(Path(self.selected_path).name)
                popup.dismiss()

        choose.bind(on_release=selected)
        row.add_widget(cancel)
        row.add_widget(choose)
        box.add_widget(row)
        popup.open()

    def _show_selected(self, name):
        self.selected_name = name
        self.ids.file_label.text = name
        self.ids.output.text = "เลือกไฟล์แล้ว กดวิเคราะห์ ROM"

    # ---- analysing -------------------------------------------------------
    def _open_selected(self):
        if self.selected_uri is not None:
            resolver = PythonActivity.mActivity.getContentResolver()
            pfd = resolver.openFileDescriptor(self.selected_uri, "r")
            return os.fdopen(pfd.detachFd(), "rb")
        return open(self.selected_path, "rb")

    def analyze_rom(self):
        if self.selected_uri is None and not self.selected_path:
            self.ids.output.text = "กรุณาเลือกไฟล์ ROM ก่อน"
            return
        try:
            with self._open_selected() as stream:
                info = analyze_stream(stream, self.selected_name or "ROM")
            self.ids.output.text = format_report(info)
        except Exception as e:
            self.ids.output.text = f"อ่านไฟล์ไม่สำเร็จ: {e}"


class RomtranApp(App):
    def build(self):
        Builder.load_string(KV)
        self.title = "Romtran GBA Edition"
        return RootUI()


if __name__ == "__main__":
    RomtranApp().run()
