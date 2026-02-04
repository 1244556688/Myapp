from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

import threading
import subprocess
import os
import webbrowser

# plyer 用於手機選資料夾
from plyer import filechooser

# 設定視窗大小（模擬桌面，可刪除手機使用）
Window.size = (800, 750)

download_folder = ""
download_queue = []

class YTDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=5, **kwargs)

        # URL 輸入
        self.add_widget(Label(text="輸入影片網址（每行一個）:", size_hint_y=None, height=30))
        self.url_text = TextInput(size_hint_y=None, height=100, multiline=True)
        self.add_widget(self.url_text)

        # 按鈕
        btn_layout = GridLayout(cols=2, size_hint_y=None, height=40, spacing=5)
        self.add_btn = Button(text="加入隊列")
        self.add_btn.bind(on_release=self.add_to_queue)
        btn_layout.add_widget(self.add_btn)

        self.remove_btn = Button(text="移除隊列")
        self.remove_btn.bind(on_release=self.remove_from_queue)
        btn_layout.add_widget(self.remove_btn)
        self.add_widget(btn_layout)

        # 下載隊列顯示
        self.queue_text = TextInput(size_hint_y=None, height=100, readonly=True)
        self.add_widget(self.queue_text)

        # 選資料夾
        folder_layout = GridLayout(cols=2, size_hint_y=None, height=40, spacing=5)
        self.select_folder_btn = Button(text="選擇下載資料夾")
        self.select_folder_btn.bind(on_release=self.select_folder)
        folder_layout.add_widget(self.select_folder_btn)
        self.folder_label = Label(text="下載資料夾: 未選擇")
        folder_layout.add_widget(self.folder_label)
        self.add_widget(folder_layout)

        # 選單：下載模式
        mode_layout = GridLayout(cols=2, size_hint_y=None, height=40, spacing=5)
        mode_layout.add_widget(Label(text="下載模式:"))
        from kivy.uix.spinner import Spinner
        self.mode_spinner = Spinner(text="單支影片", values=["單支影片", "整個播放清單"])
        mode_layout.add_widget(self.mode_spinner)
        self.add_widget(mode_layout)

        # 選單：檔案格式
        format_layout = GridLayout(cols=2, size_hint_y=None, height=40, spacing=5)
        format_layout.add_widget(Label(text="檔案格式:"))
        self.format_spinner = Spinner(text="MP4", values=["WebM", "MP4", "MP3"])
        format_layout.add_widget(self.format_spinner)
        self.add_widget(format_layout)

        # 下載按鈕
        self.download_btn = Button(text="開始下載隊列", size_hint_y=None, height=50, background_color=(0.12,0.42,0.65,1))
        self.download_btn.bind(on_release=self.download_queue_func)
        self.add_widget(self.download_btn)

        # 進度條
        self.progress_bar = ProgressBar(max=1.0, value=0.0, size_hint_y=None, height=30)
        self.add_widget(self.progress_bar)

        # 文字區域（顯示下載狀態）
        self.scroll = ScrollView()
        self.output_text = TextInput(readonly=True, size_hint_y=None, height=300)
        self.scroll.add_widget(self.output_text)
        self.add_widget(self.scroll)

    def select_folder(self, instance):
        global download_folder
        path = filechooser.choose_dir()
        if path:
            download_folder = path[0]
            self.folder_label.text = f"下載資料夾: {download_folder}"

    def add_to_queue(self, instance):
        urls_text = self.url_text.text.strip()
        if not urls_text:
            self.output_text.text += "請輸入至少一個網址\n"
            return
        lines = [line.strip() for line in urls_text.splitlines() if line.strip()]
        for url in lines:
            download_queue.append(url)
            self.queue_text.text += url + "\n"
        self.url_text.text = ""

    def remove_from_queue(self, instance):
        lines = self.queue_text.text.strip().splitlines()
        download_queue.clear()
        self.queue_text.text = ""

    def download_queue_func(self, instance):
        if not download_queue:
            self.output_text.text += "下載隊列為空\n"
            return
        if not download_folder:
            self.output_text.text += "請選擇下載資料夾\n"
            return

        def download_worker():
            for url in download_queue:
                try:
                    self.output_text.text += f"開始下載: {url}\n"
                    output_path = os.path.join(download_folder, "%(title)s.%(ext)s")
                    cmd = ["yt-dlp", "-o", output_path, "--newline", url]

                    if self.mode_spinner.text == "單支影片":
                        cmd.insert(1, "--no-playlist")
                    if self.format_spinner.text == "MP4":
                        cmd.insert(1, "-f")
                        cmd.insert(2, "bestvideo+bestaudio")
                        cmd.insert(3, "--merge-output-format")
                        cmd.insert(4, "mp4")
                    elif self.format_spinner.text == "MP3":
                        cmd.insert(1, "-x")
                        cmd.insert(2, "--audio-format")
                        cmd.insert(3, "mp3")

                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                    for line in process.stdout:
                        self.output_text.text += line
                        self.output_text.cursor = (0, len(self.output_text.text))
                        if "[download]" in line and "%" in line:
                            percent = line.split("%")[0].split()[-1]
                            try:
                                Clock.schedule_once(lambda dt, p=float(percent)/100: setattr(self.progress_bar, 'value', p))
                            except:
                                pass
                    process.wait()
                    self.output_text.text += "下載完成！\n\n"
                    Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0))
                    webbrowser.open(download_folder)
                except Exception as e:
                    self.output_text.text += f"錯誤: {str(e)}\n"

        threading.Thread(target=download_worker).start()


class YTApp(App):
    def build(self):
        return YTDownloader()


if __name__ == "__main__":
    YTApp().run()
