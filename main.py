# main.py
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

        self.background = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)
        with self.canvas.before:
            Color(0.6, 0.8, 1)
            self.bg_color = Rectangle(size=self.size, pos=self.pos)

        self.weather_label = Label(text="Loading...", font_size='24sp', size_hint=(None, None),
                                   pos_hint={'center_x':0.5, 'top':0.95})
        self.add_widget(self.weather_label)

        self.icon = AsyncImage(source="", size_hint=(None, None), size=(100, 100),
                               pos_hint={'center_x':0.5, 'top':0.85})
        self.add_widget(self.icon)

        Clock.schedule_once(lambda dt: self.fetch_weather(), 1)
        Clock.schedule_interval(self.update_animation, 1/30)

    def update_bg(self, *args):
        self.bg_color.size = self.size
        self.bg_color.pos = self.pos

    def fetch_weather(self):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            desc = data['weather'][0]['main'].lower()
            temp = data['main']['temp']
            self.weather_label.text = f"{CITY}: {desc.capitalize()}, {temp}°C"
            icon_code = data['weather'][0]['icon']
            self.icon.source = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            if "rain" in desc:
                self.weather_type = "rain"
            elif "snow" in desc:
                self.weather_type = "snow"
            elif "cloud" in desc:
                self.weather_type = "cloud"
            else:
                self.weather_type = "clear"
        except Exception as e:
            self.weather_label.text = "Failed to load weather"

    def update_animation(self, dt):
        self.canvas.clear()
        with self.canvas:
            if self.weather_type == "rain":
                Color(0.4, 0.6, 1)
                if len(self.raindrops) < 100:
                    for _ in range(5):
                        x = random.randint(0, self.width)
                        y = self.height
                        self.raindrops.append([x, y, random.randint(2, 4)])
                new_raindrops = []
                for drop in self.raindrops:
                    drop[1] -= drop[2]
                    Ellipse(pos=(drop[0], drop[1]), size=(2, 10))
                    if drop[1] > 0:
                        new_raindrops.append(drop)
                self.raindrops = new_raindrops
            elif self.weather_type == "snow":
                Color(1, 1, 1)
                if len(self.snowflakes) < 100:
                    for _ in range(3):
                        x = random.randint(0, self.width)
                        y = self.height
                        self.snowflakes.append([x, y, random.uniform(1, 2)])
                new_snow = []
                for flake in self.snowflakes:
                    flake[1] -= flake[2]
                    Ellipse(pos=(flake[0], flake[1]), size=(5, 5))
                    if flake[1] > 0:
                        new_snow.append(flake)
                self.snowflakes = new_snow
            elif self.weather_type == "cloud":
                Color(0.8, 0.8, 0.8)
                if len(self.clouds) < 5:
                    for _ in range(1):
                        x = -200
                        y = random.randint(int(self.height*0.6), int(self.height*0.9))
                        self.clouds.append([x, y, random.randint(100, 200)])
                new_clouds = []
                for cloud in self.clouds:
                    cloud[0] += 1
                    Ellipse(pos=(cloud[0], cloud[1]), size=(cloud[2], 60))
                    if cloud[0] < self.width:
                        new_clouds.append(cloud)
                self.clouds = new_clouds
            else:
                Color(0.6, 0.8, 1)
                Rectangle(size=self.size, pos=self.pos)

class WeatherApp(App):
    def build(self):
        return WeatherAppUI()

if __name__ == "__main__":
    WeatherApp().run()
