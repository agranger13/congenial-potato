"""
Widget joystick virtuel pour le contrôle du drone.
Fournit une interface tactile avec retour visuel.
"""
from math import atan2, cos, sin, sqrt
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color, Line
from kivy.properties import NumericProperty
from kivy.clock import Clock

from constants import (
    JOYSTICK_WIDGET_SIZE,
    KNOB_RADIUS,
    BORDER_WIDTH,
    GRAPHICS_UPDATE_DELAY,
    COLOR_JOYSTICK_BASE,
    COLOR_JOYSTICK_BORDER,
    COLOR_JOYSTICK_KNOB,
)


class SimpleJoystick(Widget):
    """
    Widget joystick virtuel avec retour tactile.

    Propriétés:
        pad_x: Position X normalisée (-1.0 à 1.0)
        pad_y: Position Y normalisée (-1.0 à 1.0)
    """

    pad_x = NumericProperty(0)
    pad_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = JOYSTICK_WIDGET_SIZE
        self._knob_radius = KNOB_RADIUS

        self._draw_graphics()
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        Clock.schedule_once(lambda dt: self._update_graphics(), GRAPHICS_UPDATE_DELAY)

    def _draw_graphics(self):
        """Dessine les éléments graphiques du joystick."""
        with self.canvas:
            # Base remplie gris clair
            Color(*COLOR_JOYSTICK_BASE)
            self._base = Ellipse(pos=self.pos, size=self.size)

            # Contour de la base
            Color(*COLOR_JOYSTICK_BORDER)
            self._border = Line(
                circle=(self.center_x, self.center_y, self.width / 2),
                width=BORDER_WIDTH
            )

            # Knob (bouton central)
            Color(*COLOR_JOYSTICK_KNOB)
            self._knob = Ellipse(
                size=(self._knob_radius * 2, self._knob_radius * 2),
                pos=(0, 0)
            )

    def _update_graphics(self, *args):
        """Met à jour la position des éléments graphiques."""
        cx, cy = self.center_x, self.center_y
        radius = self.size[0] / 2

        self._base.pos = self.pos
        self._base.size = self.size
        self._border.circle = (cx, cy, radius)

        # Centrer le knob si au repos
        if self.pad_x == 0 and self.pad_y == 0:
            self._knob.pos = (cx - self._knob_radius, cy - self._knob_radius)

    def on_touch_move(self, touch):
        """Gère le mouvement tactile."""
        if not self.collide_point(*touch.pos):
            return super().on_touch_move(touch)

        cx, cy = self.center_x, self.center_y
        dx, dy = touch.x - cx, touch.y - cy

        # Limiter au rayon maximum (moins le rayon du knob)
        max_radius = (self.width / 2) - self._knob_radius
        distance = min(sqrt(dx ** 2 + dy ** 2), max_radius)
        angle = atan2(dy, dx)

        # Calculer les valeurs normalisées (-1 à 1)
        self.pad_x = round(distance * cos(angle) / max_radius, 2)
        self.pad_y = round(distance * sin(angle) / max_radius, 2)

        # Mettre à jour la position du knob
        knob_x = cx + distance * cos(angle) - self._knob_radius
        knob_y = cy + distance * sin(angle) - self._knob_radius
        self._knob.pos = (knob_x, knob_y)

        # Mettre à jour le cercle de bordure
        self._border.circle = (cx, cy, self.width / 2)

        return True

    def on_touch_up(self, touch):
        """Gère le relâchement tactile (retour au centre)."""
        if not self.collide_point(*touch.pos):
            return super().on_touch_up(touch)

        # Reset au centre
        self.pad_x = 0
        self.pad_y = 0
        self._knob.pos = (
            self.center_x - self._knob_radius,
            self.center_y - self._knob_radius
        )

        return True
