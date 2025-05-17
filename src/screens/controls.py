from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.garden.Joystick import Joystick
from kivy.clock import Clock

class ControlsPage(MDScreen):
    def __init__(self, **kwargs):
        super(ControlsPage, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='horizontal', spacing='20dp', padding='20dp')

        # --- Joystick Gauche (Hauteur) ---
        self.height_label = MDLabel(text='Height: 0', halign='center', size_hint=(1, 0.1))
        self.joystick_height = Joystick(size_hint=(1, 1))
        self.joystick_height.bind(pad=self.on_height_move)

        left_layout = MDBoxLayout(orientation='vertical')
        left_layout.add_widget(self.height_label)
        left_layout.add_widget(self.joystick_height)

        # --- Joystick Droit (Direction) ---
        self.direction_label = MDLabel(text='Direction: 0', halign='center', size_hint=(1, 0.1))
        self.joystick_direction = Joystick(size_hint=(1, 1))
        self.joystick_direction.bind(pad=self.on_direction_move)

        right_layout = MDBoxLayout(orientation='vertical')
        right_layout.add_widget(self.direction_label)
        right_layout.add_widget(self.joystick_direction)

        # --- Assemblage final ---
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)
        self.add_widget(layout)

    def on_height_move(self, instance, pad):
        # pad[1] = Y axis (-1.0 to 1.0)
        height_value = round(pad[1], 2)
        self.height_label.text = f"Height: {height_value}"

    def on_direction_move(self, instance, pad):
        # pad[0] = X axis (-1.0 to 1.0)
        direction_value = round(pad[0], 2)
        self.direction_label.text = f"Direction: {direction_value}"
