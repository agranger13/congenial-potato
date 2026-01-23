"""
Page de contrôle du drone avec joysticks virtuels.
Gère l'interface utilisateur et la communication avec le drone.
"""
import time
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.config import Config
from kivy.logger import Logger

from components.simple_joystick import SimpleJoystick
from controlers.drone_config import DroneConfig
from drone.communication import DroneConnection, DroneCommand
from utils.joystick_mapper import JoystickMapper
from constants import (
    # Timing
    HEARTBEAT_INTERVAL,
    SAFETY_TIMEOUT,
    EMERGENCY_RESET_DELAY,
    UI_SETUP_DELAY,
    BUTTON_FLASH_DURATION,
    # Couleurs
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_BUTTON_ARM,
    COLOR_BUTTON_DISARM,
    COLOR_BUTTON_EMERGENCY,
    COLOR_BUTTON_FLASH,
    COLOR_CARD_DARK,
    COLOR_CARD_LEFT_JOYSTICK,
    COLOR_CARD_RIGHT_JOYSTICK,
    COLOR_LABEL_LEFT,
    COLOR_LABEL_RIGHT,
    COLOR_ICON_INACTIVE,
    # Dimensions
    JOYSTICK_SIZE,
    BUTTON_SIZE,
    BUTTON_HEIGHT,
    INFO_BUTTON_HEIGHT,
    ICON_SIZE,
    CARD_RADIUS,
    STATUS_CARD_HEIGHT_RATIO,
    JOYSTICK_CARD_HEIGHT_RATIO,
    LAYOUT_SPACING,
    CARD_SPACING,
    CARD_PADDING,
    BUTTON_SPACING,
    # Tailles de police
    FONT_SIZE_BUTTON,
    # États
    ARM_STATE_ARMED,
    # Messages
    MSG_DISARMED,
    MSG_ARMED,
    MSG_EMERGENCY,
    MSG_TIMEOUT,
)


class ControlsPage(MDScreen):
    """
    Page principale de contrôle du drone.

    Contient deux joysticks virtuels:
    - Gauche: Roll (X) et Pitch (Y)
    - Droit: Yaw (X) et Throttle (Y)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal
        self.layout = MDBoxLayout(
            orientation='vertical',
            spacing=LAYOUT_SPACING,
            size_hint=(1, 1),
            padding=20
        )
        self.add_widget(self.layout)

        # Charger la configuration
        config = DroneConfig().get_config()

        # Initialiser la connexion drone
        self._connection = DroneConnection(
            ip=config["ip"],
            port=int(config["port"]),
            on_error=self._on_connection_error
        )
        self._connection.connect()

        # Initialiser la commande et le mapper
        self._command = DroneCommand()
        self._mapper = JoystickMapper()

        # Timer pour timeout de sécurité
        self._last_command_time = time.time()

        # Planifier l'initialisation de l'UI et le heartbeat
        Clock.schedule_once(self._setup_ui, UI_SETUP_DELAY)
        Clock.schedule_interval(self._send_heartbeat, HEARTBEAT_INTERVAL)

    def on_enter(self):
        """Appelé quand on entre dans la page."""
        Config.set('graphics', 'rotation', 90)

    def _setup_ui(self, dt):
        """Configure l'interface utilisateur."""
        # Card de statut
        status_card = self._create_status_card()

        # Container pour les joysticks
        joystick_container = MDBoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(1, JOYSTICK_CARD_HEIGHT_RATIO)
        )

        # Cards joystick gauche et droite
        left_card = self._create_left_joystick_card()
        right_card = self._create_right_joystick_card()

        joystick_container.add_widget(left_card)
        joystick_container.add_widget(right_card)

        # Assemblage final
        self.layout.clear_widgets()
        self.layout.add_widget(status_card)
        self.layout.add_widget(joystick_container)

    def _create_status_card(self) -> MDCard:
        """Crée la card de statut avec les boutons de contrôle."""
        status_card = MDCard(
            orientation='vertical',
            size_hint=(1, STATUS_CARD_HEIGHT_RATIO),
            padding=CARD_PADDING,
            spacing=CARD_SPACING,
            md_bg_color=COLOR_CARD_DARK,
            radius=CARD_RADIUS
        )

        # Label de statut
        self.status_label = MDLabel(
            text=f"🔗 {self._connection.address} | 🔒 {MSG_DISARMED}",
            halign='center',
            font_style="H6",
            theme_text_color="Custom",
            text_color=COLOR_ERROR,
            bold=True
        )

        # Boutons d'info
        info_layout = self._create_info_buttons()

        # Boutons principaux (Arm/Emergency)
        button_container = self._create_main_buttons()

        status_card.add_widget(self.status_label)
        status_card.add_widget(info_layout)
        status_card.add_widget(button_container)

        return status_card

    def _create_info_buttons(self) -> MDBoxLayout:
        """Crée les boutons d'information."""
        info_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=CARD_SPACING,
            size_hint=(1, None),
            height=INFO_BUTTON_HEIGHT
        )

        info_button = MDIconButton(
            icon="information-outline",
            theme_icon_color="Custom",
            icon_color=COLOR_ICON_INACTIVE,
            icon_size=ICON_SIZE
        )

        settings_button = MDIconButton(
            icon="cog-outline",
            theme_icon_color="Custom",
            icon_color=COLOR_ICON_INACTIVE,
            icon_size=ICON_SIZE
        )

        info_layout.add_widget(info_button)
        info_layout.add_widget(Widget())  # Spacer
        info_layout.add_widget(settings_button)

        return info_layout

    def _create_main_buttons(self) -> AnchorLayout:
        """Crée les boutons ARM et URGENCE."""
        button_container = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            size_hint=(1, None),
            height="80dp"
        )

        main_buttons_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=BUTTON_SPACING,
            size_hint=(None, None),
            height=BUTTON_HEIGHT,
            adaptive_width=True
        )

        # Bouton ARM/DISARM
        self.arm_button = MDRaisedButton(
            text="🛡️ ARMER",
            size_hint=(None, None),
            size=BUTTON_SIZE,
            md_bg_color=COLOR_BUTTON_ARM,
            text_color=(1, 1, 1, 1),
            theme_text_color="Custom",
            font_size=FONT_SIZE_BUTTON,
            on_release=self._toggle_arm
        )

        # Bouton d'urgence
        self.emergency_button = MDRaisedButton(
            text="🚨 URGENCE",
            size_hint=(None, None),
            size=BUTTON_SIZE,
            md_bg_color=COLOR_BUTTON_EMERGENCY,
            text_color=(1, 1, 1, 1),
            theme_text_color="Custom",
            font_size=FONT_SIZE_BUTTON,
            on_release=self._emergency_stop
        )

        main_buttons_layout.add_widget(self.arm_button)
        main_buttons_layout.add_widget(self.emergency_button)
        button_container.add_widget(main_buttons_layout)

        return button_container

    def _create_left_joystick_card(self) -> MDCard:
        """Crée la card du joystick gauche (Roll/Pitch)."""
        left_card = MDCard(
            orientation='vertical',
            size_hint=(0.5, 1),
            padding=20,
            spacing=CARD_PADDING,
            md_bg_color=COLOR_CARD_LEFT_JOYSTICK,
            radius=CARD_RADIUS
        )

        self.left_label = MDLabel(
            text="🎯 Roll: 0° | Pitch: 0°",
            halign='center',
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=COLOR_LABEL_LEFT,
            bold=True,
            size_hint=(1, 0.15)
        )

        self.joystick_left = SimpleJoystick(size_hint=(None, None), size=JOYSTICK_SIZE)
        self.joystick_left.bind(pad_x=self._on_left_move, pad_y=self._on_left_move)

        left_card.add_widget(self.left_label)

        left_anchor = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            size_hint=(1, 0.85)
        )
        left_anchor.add_widget(self.joystick_left)
        left_card.add_widget(left_anchor)

        return left_card

    def _create_right_joystick_card(self) -> MDCard:
        """Crée la card du joystick droit (Yaw/Throttle)."""
        right_card = MDCard(
            orientation='vertical',
            size_hint=(0.5, 1),
            padding=20,
            spacing=CARD_PADDING,
            md_bg_color=COLOR_CARD_RIGHT_JOYSTICK,
            radius=CARD_RADIUS
        )

        self.right_label = MDLabel(
            text="🔄 Yaw: 0°/s | ⚡ Throttle: 0%",
            halign='center',
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=COLOR_LABEL_RIGHT,
            bold=True,
            size_hint=(1, 0.15)
        )

        self.joystick_right = SimpleJoystick(size_hint=(None, None), size=JOYSTICK_SIZE)
        self.joystick_right.bind(pad_x=self._on_right_move, pad_y=self._on_right_move)

        right_card.add_widget(self.right_label)

        right_anchor = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            size_hint=(1, 0.85)
        )
        right_anchor.add_widget(self.joystick_right)
        right_card.add_widget(right_anchor)

        return right_card

    def _on_left_move(self, instance, value):
        """Gère le mouvement du joystick gauche (Roll/Pitch)."""
        left_x, left_y, roll_deg, pitch_deg = self._mapper.map_left_joystick(
            self.joystick_left.pad_x,
            self.joystick_left.pad_y
        )

        self._command.left_x = left_x
        self._command.left_y = left_y
        self.left_label.text = f"🎯 Roll: {roll_deg}° | Pitch: {pitch_deg}°"
        self._update_command_time()

    def _on_right_move(self, instance, value):
        """Gère le mouvement du joystick droit (Yaw/Throttle)."""
        right_x, right_y, yaw_rate, throttle_pct, throttle_color = self._mapper.map_right_joystick(
            self.joystick_right.pad_x,
            self.joystick_right.pad_y
        )

        self._command.right_x = right_x
        self._command.right_y = right_y
        self.right_label.text_color = throttle_color
        self.right_label.text = f"🔄 Yaw: {yaw_rate}°/s | ⚡ Throttle: {throttle_pct}%"
        self._update_command_time()

    def _toggle_arm(self, instance):
        """Bascule l'état d'armement."""
        is_armed = self._command.toggle_armed()

        if is_armed:
            self.arm_button.text = "🛡️ DÉSARMER"
            self.arm_button.md_bg_color = COLOR_BUTTON_DISARM
            self.status_label.text = f"🔗 {self._connection.address} | ✅ {MSG_ARMED}"
            self.status_label.text_color = COLOR_SUCCESS
        else:
            self.arm_button.text = "🛡️ ARMER"
            self.arm_button.md_bg_color = COLOR_BUTTON_ARM
            self.status_label.text = f"🔗 {self._connection.address} | 🔒 {MSG_DISARMED}"
            self.status_label.text_color = COLOR_ERROR

        self._update_command_time()

    def _emergency_stop(self, instance):
        """Déclenche l'arrêt d'urgence."""
        self._command.trigger_emergency()

        # Animation flash du bouton
        self.emergency_button.md_bg_color = COLOR_BUTTON_FLASH
        Clock.schedule_once(
            lambda dt: setattr(self.emergency_button, 'md_bg_color', COLOR_BUTTON_EMERGENCY),
            BUTTON_FLASH_DURATION
        )

        # Reset UI
        self.arm_button.text = "🛡️ ARMER"
        self.arm_button.md_bg_color = COLOR_BUTTON_ARM
        self.status_label.text = f"🔗 {self._connection.address} | ❌ {MSG_EMERGENCY}"
        self.status_label.text_color = COLOR_DANGER

        # Envoyer commande d'urgence immédiatement
        self._connection.send_command(self._command)

        # Reset emergency après délai
        Clock.schedule_once(
            lambda dt: self._command.clear_emergency(),
            EMERGENCY_RESET_DELAY
        )
        self._update_command_time()

    def _update_command_time(self):
        """Met à jour le timestamp de la dernière commande."""
        self._last_command_time = time.time()

    def _send_heartbeat(self, dt):
        """Envoie régulier des commandes (heartbeat)."""
        current_time = time.time()

        # Vérifier le timeout de sécurité
        if current_time - self._last_command_time > SAFETY_TIMEOUT:
            if self._command.armed == ARM_STATE_ARMED:
                self._command.armed = 0
                self.arm_button.text = "🛡️ ARMER"
                self.arm_button.md_bg_color = COLOR_BUTTON_ARM
                self.status_label.text = f"🔗 {self._connection.address} | ⏰ {MSG_TIMEOUT}"
                self.status_label.text_color = COLOR_WARNING
                Logger.warning("Drone: Timeout détecté - désarmement automatique")

        self._connection.send_command(self._command)

    def _on_connection_error(self, message: str):
        """Gère les erreurs de connexion."""
        self.status_label.text = f"❌ {message}"
        self.status_label.text_color = COLOR_DANGER

    def on_leave(self):
        """Nettoyage en quittant la page."""
        self._command.trigger_emergency()
        self._connection.send_command(self._command)
        Clock.unschedule(self._send_heartbeat)
