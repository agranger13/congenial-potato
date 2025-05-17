import socket
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from garden.joystick.joystick import Joystick

class ControlsPage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Connexion UDP à l'hôte
        self.server_ip = '192.168.1.42'
        self.server_port = 5000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        layout = MDBoxLayout(orientation='horizontal', spacing='20dp', padding='20dp')

        # --- Joystick Hauteur (gauche) ---
        self.height_label = MDLabel(text='Height: 0', halign='center', size_hint=(1, 0.1))
        self.joystick_height = Joystick(size_hint=(1, 1))
        self.joystick_height.bind(pad=self.on_height_move)

        left_layout = MDBoxLayout(orientation='vertical')
        left_layout.add_widget(self.height_label)
        left_layout.add_widget(self.joystick_height)

        # --- Joystick Direction (droite) ---
        self.direction_label = MDLabel(text='Direction: 0.0, 0.0', halign='center', size_hint=(1, 0.1))
        self.joystick_direction = Joystick(size_hint=(1, 1))
        self.joystick_direction.bind(pad=self.on_direction_move)

        right_layout = MDBoxLayout(orientation='vertical')
        right_layout.add_widget(self.direction_label)
        right_layout.add_widget(self.joystick_direction)

        layout.add_widget(left_layout)
        layout.add_widget(right_layout)
        self.add_widget(layout)

    def on_height_move(self, instance, pad):
        y = round(pad[1], 2)
        self.height_label.text = f"Height: {y}"
        self.send_data(x=0, y=y, origin="height")  # Pour test

    def on_direction_move(self, instance, pad):
        x = round(pad[0], 2)
        y = round(pad[1], 2)
        self.direction_label.text = f"Direction: {x}, {y}"
        self.send_data(x, y)

    def send_data(self, x, y, origin="direction"):
        try:
            message = f"{origin}:{x},{y}"
            self.sock.sendto(message.encode('utf-8'), (self.server_ip, self.server_port))
        except Exception as e:
            print(f"[ERROR] Failed to send data: {e}")
