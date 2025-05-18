from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color, Line
from kivy.properties import NumericProperty
from kivy.clock import Clock
import socket
from math import atan2, cos, sin, sqrt

class SimpleJoystick(Widget):
    pad_x = NumericProperty(0)
    pad_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 300)
        self.knob_radius = 45  # moitié de la taille knob (90x90)

        with self.canvas:
            # Base remplie gris clair
            Color(0.7, 0.7, 0.7, 0.3)
            self.base = Ellipse(pos=self.pos, size=self.size)
            # Contour de la base
            Color(0.5, 0.5, 0.5, 1.0)
            self.border = Line(circle=(self.center_x, self.center_y, self.width/2), width=2)
            # Knob gris foncé
            Color(0.4, 0.4, 0.4, 1.0)
            self.knob =  Ellipse(size=(self.knob_radius * 2, self.knob_radius * 2), pos=(0, 0))

        self.bind(pos=self.update_graphics, size=self.update_graphics)
        Clock.schedule_once(lambda dt: self.update_graphics(), 0.2)

    def update_graphics(self, *args):
        cx, cy = self.center_x, self.center_y
        r = self.width / 2
        self.base.pos = self.pos
        self.base.size = self.size
        self.border.circle = (cx, cy, r)
        if self.pad_x == 0 and self.pad_y == 0:
            # Centrer knob parfaitement
            self.knob.pos = (cx - self.knob_radius, cy - self.knob_radius)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            cx, cy = self.center_x, self.center_y
            r = self.width / 2
            dx, dy = touch.x - cx, touch.y - cy
            maxr = (self.width / 2) - self.knob_radius
            dist = min(sqrt(dx ** 2 + dy ** 2), maxr)
            angle = atan2(dy, dx)
            self.pad_x = round(dist * cos(angle) / maxr, 2)
            self.pad_y = round(dist * sin(angle) / maxr, 2)
            # Position knob centré sur dx, dy
            self.knob.pos = (cx + dist * cos(angle) - self.knob_radius,
                             cy + dist * sin(angle) - self.knob_radius)
            self.border.circle = (cx, cy, r)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.pad_x, self.pad_y = 0, 0
            self.knob.pos = (self.center_x - self.knob_radius, self.center_y - self.knob_radius)
            return True
        return super().on_touch_up(touch)