from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import socket
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from components.simple_joystick import SimpleJoystick  

class ControlsPage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint=(1,1), padding=10)
        self.add_widget(self.layout)

        # Socket UDP
        self.server_ip = "192.168.1.100"
        self.server_port = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        Clock.schedule_once(self.setup_ui, 0.1)

    def setup_ui(self, dt):
        # Joystick Gauche
        left_box = MDBoxLayout(orientation='vertical', spacing=10, size_hint=(0.5, 1), padding=10)
        self.height_label = MDLabel(text="Height: 0", halign='center', size_hint=(1, 0.1))
        self.joystick_height = SimpleJoystick(size_hint=(None, None), size=(250, 250))
        self.joystick_height.bind(pad_y=self.on_height_move)

        left_box.add_widget(self.height_label)
        
        # AnchorLayout pour centrer verticalement le joystick
        left_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.9))
        left_anchor.add_widget(self.joystick_height)
        left_box.add_widget(left_anchor)

        # Joystick Droit
        right_box = MDBoxLayout(orientation='vertical', spacing=10, size_hint=(0.5, 1), padding=10)
        self.direction_label = MDLabel(text="Direction: 0, 0", halign='center', size_hint=(1, 0.1))
        self.joystick_direction = SimpleJoystick(size_hint=(None, None), size=(250, 250))
        self.joystick_direction.bind(pad_x=self.on_direction_move, pad_y=self.on_direction_move)

        right_box.add_widget(self.direction_label)

        right_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.9))
        right_anchor.add_widget(self.joystick_direction)
        right_box.add_widget(right_anchor)

        self.layout.clear_widgets()
        self.layout.add_widget(left_box)
        self.layout.add_widget(right_box)

    def on_height_move(self, instance, value):
        y = self.joystick_height.pad_y
        self.height_label.text = f"Height: {y}"
        self.send_data(0, y, "height")

    def on_direction_move(self, instance, value):
        x = self.joystick_direction.pad_x
        y = self.joystick_direction.pad_y
        self.direction_label.text = f"Direction: {x}, {y}"
        self.send_data(x, y, "direction")

    def send_data(self, x, y, origin):
        try:
            msg = f"{origin}:{x},{y}"
            self.sock.sendto(msg.encode('utf-8'), (self.server_ip, self.server_port))
        except Exception as e:
            print(f"[ERROR] Failed to send: {e}")
