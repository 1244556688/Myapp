
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.card import MDCard
import os

# 設定視窗比例 (手機尺寸)
Window.size = (360, 680)

KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition

MDScreen:
    md_bg_color: 0.05, 0.05, 0.07, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "20dp"

        # --- 頂部標題 ---
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            MDLabel:
                text: "NEON PLAYER"
                font_style: "Button"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.4, 0.7, 1, 1
            MDIconButton:
                icon: "cog-outline"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.6, 1

        # --- 專輯封面區域 ---
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            padding: "20dp"
            
            MDCard:
                id: album_art
                size_hint: None, None
                size: "240dp", "240dp"
                pos_hint: {"center_x": .5, "center_y": .5}
                radius: [dp(120), ]
                md_bg_color: 0.1, 0.1, 0.15, 1
                elevation: 4
                line_color: 0.4, 0.7, 1, 0.3
                line_width: 2
                
                MDIcon:
                    icon: "music-note"
                    font_size: "80sp"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.7, 1, 0.8
                    pos_hint: {"center_x": .5, "center_y": .5}

        # --- 歌曲資訊 ---
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: "80dp"
            spacing: "4dp"
            MDLabel:
                text: app.current_title
                font_style: "H5"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
            MDLabel:
                text: app.current_artist
                font_style: "Subtitle2"
                halign: "center"
                theme_text_color: "Hint"

        # --- 進度條 ---
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: "40dp"
            padding: ["10dp", 0]
            MDSlider:
                id: progress_slider
                min: 0
                max: app.song_length
                value: app.current_pos
                color: 0.4, 0.7, 1, 1
                hint: False
                on_touch_up: if self.collide_point(*args[1].pos): app.seek_song(self.value)
            MDBoxLayout:
                MDLabel:
                    text: app.current_time_str
                    font_style: "Caption"
                    theme_text_color: "Hint"
                MDLabel:
                    text: app.total_time_str
                    font_style: "Caption"
                    halign: "right"
                    theme_text_color: "Hint"

        # --- 控制按鈕 ---
        MDBoxLayout:
            size_hint_y: None
            height: "100dp"
            padding: ["20dp", 0]
            spacing: "20dp"
            
            MDIconButton:
                icon: "skip-previous"
                user_font_size: "32sp"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.prev_song()
                pos_hint: {"center_y": .5}
                
            MDIconButton:
                id: play_btn
                icon: "play-circle"
                user_font_size: "64sp"
                theme_text_color: "Custom"
                text_color: 0.4, 0.7, 1, 1
                on_release: app.toggle_play()
                pos_hint: {"center_y": .5}
                
            MDIconButton:
                icon: "skip-next"
                user_font_size: "32sp"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.next_song()
                pos_hint: {"center_y": .5}

        # --- 底部標籤 ---
        MDLabel:
            text: f"Playlist: {len(app.playlist)} songs found"
            font_style: "Overline"
            halign: "center"
            theme_text_color: "Hint"
'''

class MusicPlayerApp(MDApp):
    current_title = StringProperty("No Media Selected")
    current_artist = StringProperty("Scan for MP3 files in app folder")
    song_length = NumericProperty(100)
    current_pos = NumericProperty(0)
    current_time_str = StringProperty("00:00")
    total_time_str = StringProperty("00:00")
    
    playlist = ListProperty([])
    current_index = NumericProperty(0)
    sound = None
    is_playing = BooleanProperty(False)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        self.scan_music()
        # 定時更新進度條
        Clock.schedule_interval(self.update_progress, 0.5)

    def scan_music(self):
        """自動掃描當前資料夾的 MP3 檔案"""
        files = [f for f in os.listdir('.') if f.endswith('.mp3')]
        if files:
            self.playlist = files
            self.load_song(0)
        else:
            self.current_title = "Empty Library"
            self.current_artist = "Drop .mp3 files here"

    def load_song(self, index):
        """讀取歌曲"""
        if not self.playlist: return
        
        if self.sound:
            self.sound.stop()
            self.sound.unload()
        
        filename = self.playlist[index]
        self.current_title = filename.replace('.mp3', '')
        self.current_artist = "Local Audio"
        
        self.sound = SoundLoader.load(filename)
        if self.sound:
            self.song_length = self.sound.length
            self.total_time_str = self.format_time(self.sound.length)
            self.current_pos = 0
            
    def toggle_play(self):
        if not self.sound: return
        
        if self.is_playing:
            self.sound.stop()
            self.root.ids.play_btn.icon = "play-circle"
            self.stop_visual_anim()
        else:
            self.sound.play()
            self.root.ids.play_btn.icon = "pause-circle"
            self.start_visual_anim()
            
        self.is_playing = not self.is_playing

    def next_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.load_song(self.current_index)
        if self.is_playing:
            self.sound.play()

    def prev_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.load_song(self.current_index)
        if self.is_playing:
            self.sound.play()

    def update_progress(self, dt):
        if self.sound and self.is_playing:
            self.current_pos = self.sound.get_pos()
            self.current_time_str = self.format_time(self.current_pos)
            
            # 自動連播邏輯
            if self.current_pos >= self.sound.length - 0.5:
                self.next_song()

    def seek_song(self, value):
        if self.sound:
            self.sound.seek(value)

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def start_visual_anim(self):
        """專輯封面縮放動畫"""
        anim = Animation(size=(dp(260), dp(260)), duration=0.8, t='in_out_quad') + \
               Animation(size=(dp(240), dp(240)), duration=0.8, t='in_out_quad')
        anim.repeat = True
        anim.start(self.root.ids.album_art)

    def stop_visual_anim(self):
        Animation.stop_all(self.root.ids.album_art)
        Animation(size=(dp(240), dp(240)), duration=0.3).start(self.root.ids.album_art)

if __name__ == "__main__":
    MusicPlayerApp().run()
