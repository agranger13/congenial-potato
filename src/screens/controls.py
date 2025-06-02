from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivy.clock import Clock
import socket
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from components.simple_joystick import SimpleJoystick  
from kivy.config import Config
from kivy.logger import Logger
import time

from controlers.drone_config import DroneConfig

class ControlsPage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=15, size_hint=(1, 1), padding=20)
        self.add_widget(self.layout)
        config = DroneConfig().get_config()

        # Setup UDP socket
        self.server_ip = config["ip"]
        self.server_port = int(config["port"])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Valeurs joystick (centre = 512, plage 0-1023)
        self.left_x = 512    # Roll
        self.left_y = 512    # Pitch  
        self.right_x = 512   # Yaw
        self.right_y = 100   # Throttle (commence bas pour sécurité)
        self.armed = 0       # État armement
        self.emergency = 0   # Bouton d'urgence

        # Zone morte
        self.deadzone = 20

        # Timer pour timeout de sécurité
        self.last_command_time = time.time()
        self.timeout_event = None

        Clock.schedule_once(self.setup_ui, 0.5)
        Clock.schedule_interval(self.send_heartbeat, 0.1)  # Envoie toutes les 100ms

    def on_enter(self):
        Config.set('graphics', 'rotation', 90)

    def setup_ui(self, dt):
        # Card principale pour le statut
        status_card = MDCard(
            orientation='vertical',
            size_hint=(1, 0.2),
            padding=15,
            spacing=10,
            md_bg_color=(0.1, 0.1, 0.1, 0.2),  # Fond sombre semi-transparent
            radius=[5, 5, 5, 5]
        )
        
        # Label de statut avec style amélioré
        self.status_label = MDLabel(
            text=f"🔗 {self.server_ip}:{self.server_port} | 🔒 DÉSARMÉ", 
            halign='center',
            font_style="H6",
            theme_text_color="Custom",
            text_color=(1, 0.3, 0.3, 1),  # Rouge
            bold=True
        )
        
        # Conteneur principal pour les boutons avec centrage parfait
        button_container = AnchorLayout(
            anchor_x='center', 
            anchor_y='center',
            size_hint=(1, None),
            height="80dp"
        )
        
        # Layout horizontal pour les boutons principaux
        main_buttons_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=25,
            size_hint=(None, None),
            height="60dp",
            adaptive_width=True
        )
        
        # Bouton ARM/DISARM avec style moderne
        self.arm_button = MDRaisedButton(
            text="🛡️ ARMER",
            size_hint=(None, None),
            size=("180dp", "60dp"),
            md_bg_color=(0.2, 0.7, 0.2, 1),  # Vert
            text_color=(1, 1, 1, 1),
            theme_text_color="Custom",
            font_size="16sp",
            on_release=self.toggle_arm
        )
        
        # Bouton d'urgence avec style alarmant
        self.emergency_button = MDRaisedButton(
            text="🚨 URGENCE",
            size_hint=(None, None),
            size=("180dp", "60dp"),
            md_bg_color=(0.9, 0.1, 0.1, 1),  # Rouge vif
            text_color=(1, 1, 1, 1),
            theme_text_color="Custom",
            font_size="16sp",
            on_release=self.emergency_stop
        )
        
        # Ajouter les boutons principaux au layout
        main_buttons_layout.add_widget(self.arm_button)
        main_buttons_layout.add_widget(self.emergency_button)
        
        # Centrer le layout des boutons principaux
        button_container.add_widget(main_buttons_layout)
        
        # Layout pour les boutons d'info (optionnel, en haut)
        info_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, None),
            height="40dp"
        )
        
        info_button = MDIconButton(
            icon="information-outline",
            theme_icon_color="Custom",
            icon_color=(0.7, 0.7, 0.7, 1),
            icon_size="25dp"
        )
        
        settings_button = MDIconButton(
            icon="cog-outline",
            theme_icon_color="Custom",
            icon_color=(0.7, 0.7, 0.7, 1),
            icon_size="25dp"
        )
        
        # Espacer les boutons d'info sur les côtés
        info_layout.add_widget(info_button)
        info_layout.add_widget(Widget())  # Spacer
        info_layout.add_widget(settings_button)
        
        status_card.add_widget(self.status_label)
        status_card.add_widget(info_layout)
        status_card.add_widget(button_container)

        # Cards pour les joysticks
        joystick_container = MDBoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.8))

        # Left Joystick Card (Roll/Pitch)
        left_card = MDCard(
            orientation='vertical',
            size_hint=(0.5, 1),
            padding=20,
            spacing=15,
            md_bg_color=(0.05, 0.05, 0.15, 0.7),  # Bleu très sombre
            radius=[5, 5, 5, 5]
        )
        
        self.left_label = MDLabel(
            text="🎯 Roll: 0° | Pitch: 0°", 
            halign='center',
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0.8, 0.9, 1, 1),  # Bleu clair
            bold=True,
            size_hint=(1, 0.15)
        )
        
        self.joystick_left = SimpleJoystick(size_hint=(None, None), size=(280, 280))
        self.joystick_left.bind(pad_x=self.on_left_move, pad_y=self.on_left_move)

        left_card.add_widget(self.left_label)
        left_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.85))
        left_anchor.add_widget(self.joystick_left)
        left_card.add_widget(left_anchor)

        # Right Joystick Card (Yaw/Throttle)
        right_card = MDCard(
            orientation='vertical',
            size_hint=(0.5, 1),
            padding=20,
            spacing=15,
            md_bg_color=(0.15, 0.05, 0.05, 0.7),  # Rouge très sombre
            radius=[5, 5, 5, 5]
        )
        
        self.right_label = MDLabel(
            text="🔄 Yaw: 0°/s | ⚡ Throttle: 0%", 
            halign='center',
            font_style="Subtitle1", 
            theme_text_color="Custom",
            text_color=(1, 0.9, 0.8, 1),  # Orange clair
            bold=True,
            size_hint=(1, 0.15)
        )
        
        self.joystick_right = SimpleJoystick(size_hint=(None, None), size=(280, 280))
        self.joystick_right.bind(pad_x=self.on_right_move, pad_y=self.on_right_move)

        right_card.add_widget(self.right_label)
        right_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.85))
        right_anchor.add_widget(self.joystick_right)
        right_card.add_widget(right_anchor)

        joystick_container.add_widget(left_card)
        joystick_container.add_widget(right_card)

        # Assemblage final
        self.layout.clear_widgets()
        self.layout.add_widget(status_card)
        self.layout.add_widget(joystick_container)

    def map_value_to_joystick(self, pad_value):
        """
        Convertit la valeur du pad (-1.0 à 1.0) vers les valeurs joystick (0-1023)
        avec zone morte appliquée
        """
        # Convertir de -1,1 vers 0-1023
        joystick_value = int((pad_value + 1.0) * 511.5)
        
        # Appliquer la zone morte autour du centre (512)
        center = 512
        if abs(joystick_value - center) <= self.deadzone:
            joystick_value = center
            
        # Limiter les valeurs
        return max(0, min(1023, joystick_value))

    def map_throttle(self, pad_y):
        """
        Mapping spécial pour le throttle : -1.0 (bas) = 0, +1.0 (haut) = 200
        """
        throttle_value = int((pad_y + 1.0) * 100)  # -1,1 -> 0,200
        
        # Zone morte pour le throttle
        if throttle_value <= 10:  # Zone morte en bas
            throttle_value = 0
            
        return max(0, min(200, throttle_value))

    def on_left_move(self, instance, value):
        """Left stick: Roll (X) et Pitch (Y)"""
        self.left_x = self.map_value_to_joystick(self.joystick_left.pad_x)
        self.left_y = self.map_value_to_joystick(self.joystick_left.pad_y)
        
        # Conversion en degrés pour affichage (-30° à +30°)
        roll_degrees = int((self.left_x - 512) * 30 / 511)
        pitch_degrees = int((self.left_y - 512) * 30 / 511)
        
        self.left_label.text = f"🎯 Roll: {roll_degrees}° | Pitch: {pitch_degrees}°"
        self.update_command_time()

    def on_right_move(self, instance, value):
        """Right stick: Yaw (X) et Throttle (Y)"""
        self.right_x = self.map_value_to_joystick(self.joystick_right.pad_x)
        self.right_y = self.map_throttle(self.joystick_right.pad_y)
        
        # Conversion pour affichage
        yaw_rate = int((self.right_x - 512) * 180 / 511)  # -180°/s à +180°/s
        throttle_percent = int(self.right_y * 100 / 200)   # 0-100%
        
        # Couleur dynamique pour le throttle
        if throttle_percent > 70:
            throttle_color = (1, 0.3, 0.3, 1)  # Rouge pour throttle élevé
        elif throttle_percent > 30:
            throttle_color = (1, 0.8, 0.3, 1)  # Orange pour throttle moyen
        else:
            throttle_color = (0.3, 1, 0.3, 1)  # Vert pour throttle bas
            
        self.right_label.text_color = throttle_color
        self.right_label.text = f"🔄 Yaw: {yaw_rate}°/s | ⚡ Throttle: {throttle_percent}%"
        self.update_command_time()

    def toggle_arm(self, instance):
        """Basculer l'état d'armement"""
        self.armed = 1 - self.armed
        if self.armed:
            # État armé
            self.arm_button.text = "🛡️ DÉSARMER"
            self.arm_button.md_bg_color = (0.9, 0.3, 0.3, 1)  # Rouge
            self.status_label.text = f"🔗 {self.server_ip}:{self.server_port} | ✅ ARMÉ"
            self.status_label.text_color = (0.3, 1, 0.3, 1)  # Vert
        else:
            # État désarmé
            self.arm_button.text = "🛡️ ARMER"
            self.arm_button.md_bg_color = (0.2, 0.7, 0.2, 1)  # Vert
            self.status_label.text = f"🔗 {self.server_ip}:{self.server_port} | 🔒 DÉSARMÉ"
            self.status_label.text_color = (1, 0.3, 0.3, 1)  # Rouge
        
        self.update_command_time()

    def emergency_stop(self, instance):
        """Arrêt d'urgence"""
        self.emergency = 1
        self.armed = 0
        self.right_y = 0  # Throttle à 0
        
        # Animation du bouton d'urgence
        self.emergency_button.md_bg_color = (1, 1, 1, 1)  # Blanc pour effet flash
        Clock.schedule_once(lambda dt: setattr(self.emergency_button, 'md_bg_color', (0.9, 0.1, 0.1, 1)), 0.1)
        
        # Reset UI
        self.arm_button.text = "🛡️ ARMER"
        self.arm_button.md_bg_color = (0.2, 0.7, 0.2, 1)
        self.status_label.text = f"🔗 {self.server_ip}:{self.server_port} | ❌ URGENCE!"
        self.status_label.text_color = (1, 0, 0, 1)  # Rouge vif
        
        # Envoyer commande d'urgence
        self.send_command()
        
        # Reset emergency après 1 seconde
        Clock.schedule_once(lambda dt: setattr(self, 'emergency', 0), 1.0)
        self.update_command_time()

    def update_command_time(self):
        """Met à jour le timestamp de la dernière commande"""
        self.last_command_time = time.time()

    def send_heartbeat(self, dt):
        """Envoie régulier des commandes"""
        current_time = time.time()
        
        # Vérifier le timeout (5 secondes)
        if current_time - self.last_command_time > 5.0:
            # Timeout: désarmer automatiquement
            if self.armed:
                self.armed = 0
                self.arm_button.text = "🛡️ ARMER"
                self.arm_button.md_bg_color = (0.2, 0.7, 0.2, 1)
                self.status_label.text = f"🔗 {self.server_ip}:{self.server_port} | ⏰ TIMEOUT - DÉSARMÉ"
                self.status_label.text_color = (1, 0.5, 0, 1)  # Orange
                Logger.warning("Drone: Timeout détecté - désarmement automatique")

        self.send_command()

    def send_command(self):
        """
        Envoie la commande au format CSV: leftX,leftY,rightX,rightY,armed,emergency
        Exemple: 512,480,500,100,1,0
        """
        try:
            # Format CSV exact demandé
            message = f"{self.left_x},{self.left_y},{self.right_x},{self.right_y},{self.armed},{self.emergency}"
            self.sock.sendto(message.encode(), (self.server_ip, self.server_port))
            
            # Log pour debug (seulement si armed ou emergency)
            if self.armed or self.emergency:
                Logger.info(f"Drone CMD: {message}")
                
        except OSError as e:
            Logger.error(f"Erreur envoi commande: {e}")
            self.status_label.text = f"❌ ERREUR CONNEXION: {e}"
            self.status_label.text_color = (1, 0, 0, 1)

    def on_leave(self):
        """Nettoyage en quittant la page"""
        self.armed = 0
        self.emergency = 1
        self.send_command()  # Envoyer commande d'arrêt
        Clock.unschedule(self.send_heartbeat)