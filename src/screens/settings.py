from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from jnius import autoclass, cast
import platform

from components.connect_dialog_content import ConnectDialogContent
from controlers.drone_config import DroneConfig

class SettingsPage(MDScreen):
    def __init__(self, **kwargs):
        super(SettingsPage, self).__init__(**kwargs)
        self.current_activity = self._get_current_activity()
        self.wifi_manager = self._get_wifi_manager()
        
        # Instance de configuration du drone
        self.drone_config = DroneConfig()
        
        layout = MDBoxLayout(orientation='vertical', spacing='15dp', padding='20dp')

        # Section Wi-Fi
        wifi_card = MDCard(
            size_hint_y=None,
            height="200dp",
            padding="15dp",
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

        self.scan_button = MDRectangleFlatButton(
            text='Scan Wi-Fi Networks',
            pos_hint={'center_x': 0.5},
            on_release=self.scan_wifi_networks
        )
        wifi_layout.add_widget(self.scan_button)
        
        wifi_card.add_widget(wifi_layout)
        layout.add_widget(wifi_card)

        # Section Configuration Drone
        drone_card = MDCard(
            size_hint_y=None,
            height="220dp",
            padding="15dp",
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
            text=f'Drone IP: {self.drone_config.ip}',
            halign='left'
        )
        drone_layout.add_widget(self.drone_ip_label)

        self.drone_port_label = MDLabel(
            text=f'Drone Port: {self.drone_config.port}',
            halign='left'
        )
        drone_layout.add_widget(self.drone_port_label)

        self.config_drone_button = MDRectangleFlatButton(
            text='Configure Drone Connection',
            pos_hint={'center_x': 0.5},
            on_release=self.show_drone_config_dialog
        )
        drone_layout.add_widget(self.config_drone_button)
        
        drone_card.add_widget(drone_layout)
        layout.add_widget(drone_card)

        self.add_widget(layout)
        Clock.schedule_once(self.update_current_ssid, 0.5)

    def get_drone_config(self):
        """Retourne la configuration actuelle du drone"""
        return self.drone_config.get_config()

    def show_drone_config_dialog(self, instance):
        """Affiche le dialog de configuration du drone"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing='10dp',
            size_hint_y=None,
            height="150dp"
        )

        self.ip_field = MDTextField(
            hint_text="IP Address",
            text=self.drone_config.ip,
            mode="rectangle"
        )
        content.add_widget(self.ip_field)

        self.port_field = MDTextField(
            hint_text="Port",
            text=self.drone_config.port,
            mode="rectangle"
        )
        content.add_widget(self.port_field)

        self.drone_config_dialog = MDDialog(
            title="Configure Drone Connection",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.drone_config_dialog.dismiss()
                ),
                MDRectangleFlatButton(
                    text="SAVE",
                    on_release=self.save_drone_config_dialog
                )
            ]
        )
        self.drone_config_dialog.open()

    def save_drone_config_dialog(self, instance):
        """Sauvegarde la nouvelle configuration du drone"""
        new_ip = self.ip_field.text.strip()
        new_port = self.port_field.text.strip()

        # Validation basique
        if not new_ip or not new_port:
            self.show_dialog("Please fill in both IP and Port fields.")
            return

        try:
            # Validation du port
            port_int = int(new_port)
            if port_int < 1 or port_int > 65535:
                self.show_dialog("Port must be between 1 and 65535.")
                return
        except ValueError:
            self.show_dialog("Port must be a valid number.")
            return

        # Sauvegarde via le singleton
        self.drone_config.set_config(new_ip, new_port)

        # Mise à jour des labels
        self.drone_ip_label.text = f'Drone IP: {self.drone_config.ip}'
        self.drone_port_label.text = f'Drone Port: {self.drone_config.port}'

        self.drone_config_dialog.dismiss()
        self.show_dialog(f"Drone configuration saved:\nIP: {self.drone_config.ip}\nPort: {self.drone_config.port}")

    def update_current_ssid(self, dt):
        if platform.system() == "Windows":
            ssid = "Test_Network"
        else:
            info = self.wifi_manager.getConnectionInfo()
            ssid = info.getSSID()
            if ssid.startswith('"') and ssid.endswith('"'):
                ssid = ssid[1:-1]  # Nettoie les guillemets

        self.ssid_label.text = f"Current SSID: {ssid}"

    def scan_wifi_networks(self, instance):
        try:
            networks = self.get_wifi_networks()
            if networks:
                self.show_wifi_list(networks)
            else:
                self.show_dialog("No Wi-Fi networks found.")
        except Exception as e:
            self.show_dialog(f"Error: {str(e)}")

    def _get_current_activity(self):
        if platform.system() == "Windows":
            return None
        python_activity = autoclass('org.kivy.android.PythonActivity')
        return cast('android.app.Activity', python_activity.mActivity)

    def _get_wifi_manager(self):
        if platform.system() == "Windows":
            return None
        return cast(
            'android.net.wifi.WifiManager',
            self.current_activity.getSystemService(autoclass('android.content.Context').WIFI_SERVICE)
        )

    def get_wifi_networks(self):
        if platform.system() == "Windows":
            return [f"WIFI_NAME_{i}" for i in range(10)]

        permissions = [
            "android.permission.ACCESS_WIFI_STATE",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.CHANGE_WIFI_STATE",
        ]

        for permission in permissions:
            if self.current_activity.checkSelfPermission(permission) != 0:
                self.current_activity.requestPermissions([permission], 1)
                return []

        if not self.wifi_manager.isWifiEnabled():
            self.wifi_manager.setWifiEnabled(True)

        success = self.wifi_manager.startScan()
        if not success:
            return []

        scan_results = self.wifi_manager.getScanResults()
        networks = [result.SSID for result in scan_results if result.SSID]
        return networks

    def show_wifi_list(self, networks):
        # Conteneur principal
        container = MDBoxLayout(orientation='vertical', size_hint_y=None, height="300dp")

        scroll = MDScrollView()
        list_view = MDList()

        for net in networks:
            item = OneLineListItem(text=net)
            item.bind(on_release=self._on_network_selected(net))
            list_view.add_widget(item)

        scroll.add_widget(list_view)
        container.add_widget(scroll)

        self.network_dialog = MDDialog(
            title="Available Wi-Fi Networks",
            type="custom",
            content_cls=container,
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.network_dialog.dismiss()
                )
            ]
        )
        self.network_dialog.open()

    def _on_network_selected(self, ssid):
        def callback(instance):
            self.network_dialog.dismiss()
            self.show_connect_dialog(ssid)
        return callback

    def show_connect_dialog(self, ssid):
        self.connect_content = ConnectDialogContent(ssid)

        self.connect_dialog = MDDialog(
            title="Connect to Wi-Fi",
            type="custom",
            content_cls=self.connect_content,
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.connect_dialog.dismiss()
                ),
                MDRectangleFlatButton(
                    text="CONNECT",
                    on_release=lambda x: self._connect_to_wifi(ssid, self.connect_content.get_password())
                )
            ]
        )
        self.connect_dialog.open()

    def _connect_to_wifi(self, ssid, password):
        self.connect_dialog.dismiss()
        self.show_dialog(f"Connecting to {ssid} with password: {password}")
        WifiConfiguration = autoclass('android.net.wifi.WifiConfiguration')
        wifi_config = WifiConfiguration()
        wifi_config.SSID = f'"{ssid}"'
        wifi_config.preSharedKey = f'"{password}"'

        self.wifi_manager.addNetwork(wifi_config)
        self.wifi_manager.enableNetwork(wifi_config.networkId, True)

    def show_dialog(self, message):
        info_dialog = MDDialog(
            title="Information",
            text=message,
            buttons=[
                MDRectangleFlatButton(
                    text="OK",
                    on_release=lambda x: info_dialog.dismiss()
                )
            ]
        )
        info_dialog.open()