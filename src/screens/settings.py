"""
Page de configuration de l'application.
Gère la connexion WiFi et la configuration du drone.
"""
from typing import Dict
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock

from components.connect_dialog_content import ConnectDialogContent
from controlers.drone_config import DroneConfig
from platform_support import get_wifi_manager, WifiManager
from utils.dialog_helper import DialogHelper
from constants import (
    SSID_UPDATE_DELAY,
    WIFI_CARD_HEIGHT,
    DRONE_CARD_HEIGHT,
    CARD_PADDING,
    SCREEN_PADDING,
    MSG_NO_WIFI,
)


class SettingsPage(MDScreen):
    """
    Page de configuration avec deux sections:
    - Configuration WiFi (scan et connexion)
    - Configuration Drone (IP et port)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialiser le manager WiFi (abstraction plateforme)
        self._wifi_manager: WifiManager = get_wifi_manager()

        # Instance de configuration du drone
        self._drone_config = DroneConfig()

        # Construire l'interface
        self._build_ui()

        # Mettre à jour le SSID après un court délai
        Clock.schedule_once(self._update_current_ssid, SSID_UPDATE_DELAY)

    def _build_ui(self):
        """Construit l'interface utilisateur."""
        layout = MDBoxLayout(
            orientation='vertical',
            spacing='15dp',
            padding=SCREEN_PADDING
        )

        # Section Wi-Fi
        wifi_card = self._create_wifi_card()
        layout.add_widget(wifi_card)

        # Section Configuration Drone
        drone_card = self._create_drone_card()
        layout.add_widget(drone_card)

        self.add_widget(layout)

    def _create_wifi_card(self) -> MDCard:
        """Crée la card de configuration WiFi."""
        wifi_card = MDCard(
            size_hint_y=None,
            height=WIFI_CARD_HEIGHT,
            padding=CARD_PADDING,
            elevation=2
        )

        wifi_layout = MDBoxLayout(orientation='vertical', spacing='10dp')

        wifi_title = MDLabel(
            text='Wi-Fi Configuration',
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="40dp"
        )
        wifi_layout.add_widget(wifi_title)

        self.ssid_label = MDLabel(text='Current SSID: Unknown', halign='left')
        wifi_layout.add_widget(self.ssid_label)

        scan_button = MDRectangleFlatButton(
            text='Scan Wi-Fi Networks',
            pos_hint={'center_x': 0.5},
            on_release=self._on_scan_wifi
        )
        wifi_layout.add_widget(scan_button)

        wifi_card.add_widget(wifi_layout)
        return wifi_card

    def _create_drone_card(self) -> MDCard:
        """Crée la card de configuration du drone."""
        drone_card = MDCard(
            size_hint_y=None,
            height=DRONE_CARD_HEIGHT,
            padding=CARD_PADDING,
            elevation=2
        )

        drone_layout = MDBoxLayout(orientation='vertical', spacing='10dp')

        drone_title = MDLabel(
            text='Drone Configuration',
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="40dp"
        )
        drone_layout.add_widget(drone_title)

        self.drone_ip_label = MDLabel(
            text=f'Drone IP: {self._drone_config.ip}',
            halign='left'
        )
        drone_layout.add_widget(self.drone_ip_label)

        self.drone_port_label = MDLabel(
            text=f'Drone Port: {self._drone_config.port}',
            halign='left'
        )
        drone_layout.add_widget(self.drone_port_label)

        config_button = MDRectangleFlatButton(
            text='Configure Drone Connection',
            pos_hint={'center_x': 0.5},
            on_release=self._on_configure_drone
        )
        drone_layout.add_widget(config_button)

        drone_card.add_widget(drone_layout)
        return drone_card

    def _update_current_ssid(self, dt=None):
        """Met à jour l'affichage du SSID actuel."""
        ssid = self._wifi_manager.get_current_ssid()
        self.ssid_label.text = f"Current SSID: {ssid}"

    def _on_scan_wifi(self, instance):
        """Gère le clic sur le bouton de scan WiFi."""
        try:
            networks = self._wifi_manager.scan_networks()
            if networks:
                self._show_wifi_list(networks)
            else:
                DialogHelper.show_info("Information", MSG_NO_WIFI)
        except Exception as e:
            DialogHelper.show_info("Error", str(e))

    def _show_wifi_list(self, networks: list):
        """Affiche la liste des réseaux WiFi disponibles."""
        DialogHelper.show_list_selection(
            title="Available Wi-Fi Networks",
            items=networks,
            on_select=self._on_network_selected
        )

    def _on_network_selected(self, ssid: str):
        """Gère la sélection d'un réseau WiFi."""
        self._show_connect_dialog(ssid)

    def _show_connect_dialog(self, ssid: str):
        """Affiche le dialog de connexion WiFi."""
        connect_content = ConnectDialogContent(ssid)

        def on_connect(dialog):
            password = connect_content.get_password()
            dialog.dismiss()
            self._connect_to_wifi(ssid, password)

        DialogHelper.show_custom(
            title="Connect to Wi-Fi",
            content=connect_content,
            buttons=[
                ("CANCEL", None),
                ("CONNECT", on_connect)
            ]
        )

    def _connect_to_wifi(self, ssid: str, password: str):
        """Connecte au réseau WiFi sélectionné."""
        success = self._wifi_manager.connect(ssid, password)
        if success:
            DialogHelper.show_info(
                "Information",
                f"Connecting to {ssid}..."
            )
            # Mettre à jour le SSID après un délai
            Clock.schedule_once(self._update_current_ssid, 2.0)
        else:
            DialogHelper.show_info(
                "Error",
                f"Failed to connect to {ssid}"
            )

    def _on_configure_drone(self, instance):
        """Affiche le dialog de configuration du drone."""
        fields = [
            {'name': 'ip', 'hint': 'IP Address', 'value': self._drone_config.ip},
            {'name': 'port', 'hint': 'Port', 'value': self._drone_config.port}
        ]

        DialogHelper.show_input(
            title="Configure Drone Connection",
            fields=fields,
            on_save=self._save_drone_config
        )

    def _save_drone_config(self, values: Dict[str, str], dialog):
        """Sauvegarde la configuration du drone."""
        ip = values.get('ip', '').strip()
        port = values.get('port', '').strip()

        # Validation
        if not ip or not port:
            DialogHelper.show_info("Error", "Please fill in both IP and Port fields.")
            return

        try:
            port_int = int(port)
            if port_int < 1 or port_int > 65535:
                DialogHelper.show_info("Error", "Port must be between 1 and 65535.")
                return
        except ValueError:
            DialogHelper.show_info("Error", "Port must be a valid number.")
            return

        # Sauvegarde
        self._drone_config.set_config(ip, port)

        # Mise à jour de l'UI
        self.drone_ip_label.text = f'Drone IP: {self._drone_config.ip}'
        self.drone_port_label.text = f'Drone Port: {self._drone_config.port}'

        dialog.dismiss()
        DialogHelper.show_info(
            "Success",
            f"Drone configuration saved:\nIP: {ip}\nPort: {port}"
        )

    def get_drone_config(self) -> Dict[str, str]:
        """Retourne la configuration actuelle du drone."""
        return self._drone_config.get_config()
