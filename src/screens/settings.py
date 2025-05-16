from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.logger import Logger
from jnius import autoclass, cast
import subprocess
import platform

class SettingsPage(MDScreen):
    def __init__(self, **kwargs):
        super(SettingsPage, self).__init__(**kwargs)

        layout = MDBoxLayout(orientation='vertical', spacing='10dp', padding='10dp')

        self.label = MDLabel(text='Available Wi-Fi Networks:', halign='center')
        layout.add_widget(self.label)

        self.scan_button = MDRectangleFlatButton(
            text='Scan Wi-Fi Networks',
            pos_hint={'center_x': 0.5},
            on_release=self.scan_wifi_networks
        )
        layout.add_widget(self.scan_button)

        self.add_widget(layout)

    def scan_wifi_networks(self, instance):
        try:
            networks = self.get_wifi_networks()
            if networks:
                self.show_wifi_list(networks)
            else:
                self.show_dialog("No Wi-Fi networks found.")
        except Exception as e:
            self.show_dialog(f"Error: {str(e)}")

    def get_wifi_networks(self):
        system = platform.system()
        Logger.info("Plateforme actuelle : " + system)
        if system == "Windows":
            result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], capture_output=True, text=True)
            output = result.stdout
            print("Résultat brut du listing des wifi : ", output)
            networks = []
            for line in output.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":")[1].strip()
                    networks.append(ssid)
            return networks
        elif system == "Linux":
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi', 'list'], capture_output=True, text=True)
            output = result.stdout
            Logger.info("Résultat brut du listing des wifi : ", system)
            networks = output.split('\n')
            return networks
        else:
            # Cas pour Android
            try:
                # Utiliser pyjnius pour accéder aux API Android
                Context = autoclass('android.content.Context')
                Activity = autoclass('android.app.Activity')
                Intent = autoclass('android.content.Intent')
                String = autoclass('java.lang.String')

                current_activity = cast('android.app.Activity', autoclass('org.kivy.android.PythonActivity').mActivity)

                # Demander les permissions nécessaires
                permissions = [
                    "android.permission.ACCESS_WIFI_STATE",
                    "android.permission.ACCESS_FINE_LOCATION",
                    "android.permission.CHANGE_WIFI_STATE"
                ]

                for permission in permissions:
                    if current_activity.checkSelfPermission(permission) != 0:  # 0 means PERMISSION_GRANTED
                        current_activity.requestPermissions([permission], 1)

                # Utiliser WifiManager pour scanner les réseaux Wi-Fi
                WifiManager = autoclass('android.net.wifi.WifiManager')
                wifi_manager = cast('android.net.wifi.WifiManager',
                                   current_activity.getSystemService(Context.WIFI_SERVICE))

                # Activer le Wi-Fi
                if not wifi_manager.isWifiEnabled():
                    wifi_manager.setWifiEnabled(True)

                # Scanner les réseaux Wi-Fi
                wifi_manager.startScan()

                # Obtenir les résultats du scan
                scan_results = wifi_manager.getScanResults()

                networks = []
                for result in scan_results:
                    networks.append(result.SSID)

                return networks
            except Exception as e:
                Logger.error(f"Error accessing Wi-Fi on Android: {str(e)}")
                return []

    def show_wifi_list(self, networks):
        items = [OneLineListItem(text=network, on_release=lambda x, ssid=network: self.show_connect_dialog(ssid)) for network in networks]

        self.dialog = MDDialog(
            title="Available Wi-Fi Networks",
            type="confirmation",
            items=items,
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def show_connect_dialog(self, ssid):
        self.dialog.dismiss()

        connect_layout = MDBoxLayout(orientation='vertical', spacing='10dp', padding='10dp')

        self.ssid_label = MDLabel(text=f"Connect to: {ssid}", halign='center')
        connect_layout.add_widget(self.ssid_label)

        self.password_field = MDTextField(
            hint_text="Password",
            password=True,
            size_hint=(1, None),
            height='40dp'
        )
        connect_layout.add_widget(self.password_field)

        self.connect_button = MDRectangleFlatButton(
            text='Connect',
            pos_hint={'center_x': 0.5},
            on_release=lambda x: self.connect_to_wifi(ssid, self.password_field.text)
        )
        connect_layout.add_widget(self.connect_button)

        self.connect_dialog = MDDialog(
            title="Connect to Wi-Fi",
            type="custom",
            content_cls=connect_layout,
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.connect_dialog.dismiss()
                )
            ]
        )
        self.connect_dialog.open()

    def connect_to_wifi(self, ssid, password):
        # Ici, vous pouvez ajouter le code pour vous connecter au réseau Wi-Fi
        self.show_dialog(f"Connecting to {ssid} with password: {password}")
        self.connect_dialog.dismiss()

    def show_dialog(self, message):
        self.dialog = MDDialog(
            title="Information",
            text=message,
            buttons=[
                MDRectangleFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
