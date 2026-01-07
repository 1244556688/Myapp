import random
import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle

API_KEY = "43e88925721feb045a1d893028d3dda2"
CITY = "Taipei"

class WeatherAppUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.weather_type = "clear"
        self.raindrops = []
        self.snowflakes = []
        self.clouds = []

        # 背景（不會被清掉）
        with self.canvas.before:
            Color(0.6, 0.8, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        # UI 元件
        self.weather_label = Label(
            text="Loading...",
            font_size='24sp',
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(None, None)
        )
        self.add_widget(self.weather_label)

        self.icon = AsyncImage(
            size=(100, 100),
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        self.add_widget(self.icon)

        Clock.schedule_once(self.fetch_weather, 1)
        Clock.schedule_interval(self.update_animation, 1 / 30)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def fetch_weather(self, dt):
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={CITY}&appid={API_KEY}&units=metric"
            )
            data = requests.get(url, timeout=5).json()

            desc = data['weather'][0]['main'].lower()
            temp = data['main']['temp']
            icon_code = data['weather'][0]['icon']

            self.weather_label.text = f"{CITY}: {desc.capitalize()}, {temp}°C"
            self.icon.source = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            if "rain" in desc:
                self.weather_type = "rain"
            elif "snow" in desc:
                self.weather_type = "snow"
            elif "cloud" in desc:
                self.weather_type = "cloud"
            else:
                self.weather_type = "clear"

        except:
            self.weather_label.text = "Weather load failed"

    def update_animation(self, dt):
        self.canvas.after.clear()

        with self.canvas.after:
            if self.weather_type == "rain":
                Color(0.4, 0.6, 1)
                for _ in range(5):
                    self.raindrops.append([
                        random.randint(0, int(self.width)),
                        self.height,
                        random.randint(5, 8)
                    ])

                new_drops = []
                for x, y, s in self.raindrops:
                    y -= s
                    Ellipse(pos=(x, y), size=(2, 12))
                    if y > 0:
                        new_drops.append([x, y, s])
                self.raindrops = new_drops

            elif self.weather_type == "snow":
                Color(1, 1, 1)
                for _ in range(3):
                    self.snowflakes.append([
                        random.randint(0, int(self.width)),
                        self.height,
                        random.uniform(1, 2)
                    ])

                new_snow = []
                for x, y, s in self.snowflakes:
                    y -= s
                    Ellipse(pos=(x, y), size=(5, 5))
                    if y > 0:
                        new_snow.append([x, y, s])
                self.snowflakes = new_snow

            elif self.weather_type == "cloud":
                Color(0.85, 0.85, 0.85)
                if len(self.clouds) < 4:
                    self.clouds.append([
                        -200,
                        random.randint(int(self.height * 0.6), int(self.height * 0.85)),
                        random.randint(120, 200)
                    ])

                new_clouds = []
                for x, y, w in self.clouds:
                    x += 0.5
                    Ellipse(pos=(x, y), size=(w, 60))
                    if x < self.width:
                        new_clouds.append([x, y, w])
                self.clouds = new_clouds

class WeatherApp(App):
    def build(self):
        return WeatherAppUI()

if __name__ == "__main__":
    WeatherApp().run()
