# main.py
import random
import json
from urllib.request import urlopen

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle

API_KEY = "43e88925721feb045a1d893028d3dda2"
CITY = "Taichung"


class WeatherAppUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.weather_type = "clear"
        self.raindrops = []
        self.snowflakes = []
        self.clouds = []

        # ===== 背景 & 天氣動畫層（不會遮字）=====
        with self.canvas.before:
            Color(0.6, 0.8, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)

        # ===== UI（一定在最上層）=====
        self.weather_label = Label(
            text="Loading weather...",
            font_size="24sp",
            pos_hint={"center_x": 0.5, "top": 0.95},
            size_hint=(None, None),
        )
        self.add_widget(self.weather_label)

        self.icon = AsyncImage(
            size=(100, 100),
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "top": 0.85},
        )
        self.add_widget(self.icon)

        Clock.schedule_once(self.fetch_weather, 1)
        Clock.schedule_interval(self.update_animation, 1 / 30)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def fetch_weather(self, dt):
        try:
            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?q={CITY},TW&appid={API_KEY}&units=metric"
            )
            with urlopen(url, timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))

            desc = data["weather"][0]["main"].lower()
            temp = int(data["main"]["temp"])
            icon = data["weather"][0]["icon"]

            self.weather_label.text = f"{CITY}  {temp}°C  {desc.capitalize()}"
            self.icon.source = f"https://openweathermap.org/img/wn/{icon}@2x.png"
            self.weather_type = self.map_weather(desc)

        except:
            self.use_fake_weather()

    def map_weather(self, desc):
        if "rain" in desc:
            return "rain"
        if "snow" in desc:
            return "snow"
        if "cloud" in desc:
            return "cloud"
        return "clear"

    def use_fake_weather(self):
        fake = random.choice(["clear", "cloud", "rain", "snow"])
        self.weather_type = fake
        self.weather_label.text = f"{CITY}  Demo Mode ({fake.capitalize()})"
        self.icon.source = ""

    def update_animation(self, dt):
        self.canvas.before.clear()

        with self.canvas.before:
            # 背景色
            Color(0.6, 0.8, 1)
            Rectangle(size=self.size, pos=self.pos)

            if self.weather_type == "rain":
                Color(0.4, 0.6, 1)
                for _ in range(5):
                    self.raindrops.append(
                        [random.randint(0, int(self.width)), self.height]
                    )
                for d in self.raindrops:
                    d[1] -= 18
                    Ellipse(pos=d, size=(3, 12))
                self.raindrops = [d for d in self.raindrops if d[1] > 0]

            elif self.weather_type == "snow":
                Color(1, 1, 1)
                for _ in range(3):
                    self.snowflakes.append(
                        [random.randint(0, int(self.width)), self.height]
                    )
                for f in self.snowflakes:
                    f[1] -= 4
                    Ellipse(pos=f, size=(6, 6))
                self.snowflakes = [f for f in self.snowflakes if f[1] > 0]

            elif self.weather_type == "cloud":
                Color(0.9, 0.9, 0.9)
                for _ in range(1):
                    self.clouds.append(
                        [-200, random.randint(int(self.height * 0.6), int(self.height * 0.85))]
                    )
                for c in self.clouds:
                    c[0] += 0.6
                    Ellipse(pos=c, size=(180, 60))
                self.clouds = [c for c in self.clouds if c[0] < self.width + 200]


class WeatherApp(App):
    def build(self):
        return WeatherAppUI()


if __name__ == "__main__":
    WeatherApp().run()
