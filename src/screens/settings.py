from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivy.logger import Logger
from jnius import autoclass, cast
import platform

from components.connect_dialog_content import ConnectDialogContent

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
        if platform.system() == "Windows":
            # result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], capture_output=True, text=True)
            # output = result.stdout
            # print("Résultat brut du listing des wifi : ", output)
            # networks = []
            # for line in output.split('\n'):
            #     if "SSID" in line and "BSSID" not in line:
            #         ssid = line.split(":")[1].strip()
            #         networks.append(ssid)
            return [f"WIFI_NAME_{i}" for i in range(10)]
        else:
            try:
                # Accès au contexte Android
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                current_activity = cast('android.app.Activity', PythonActivity.mActivity)
                Context = autoclass('android.content.Context')

                # Gestion des permissions
                permissions = [
                    "android.permission.ACCESS_WIFI_STATE",
                    "android.permission.ACCESS_FINE_LOCATION",
                    "android.permission.CHANGE_WIFI_STATE"
                ]

                for permission in permissions:
                    if current_activity.checkSelfPermission(permission) != 0:  # PERMISSION_GRANTED = 0
                        Logger.warning(f"Permission not granted: {permission}")
                        current_activity.requestPermissions([permission], 1)
                        return []  # Sortir car les permissions ne sont pas encore accordées

                # Accès au service Wifi
                WifiManager = autoclass('android.net.wifi.WifiManager')
                wifi_service = current_activity.getSystemService(Context.WIFI_SERVICE)
                wifi_manager = cast('android.net.wifi.WifiManager', wifi_service)

                # Activer le Wi-Fi si désactivé
                if not wifi_manager.isWifiEnabled():
                    Logger.info("Wi-Fi désactivé, activation en cours...")
                    wifi_manager.setWifiEnabled(True)

                # Lancer un scan
                success = wifi_manager.startScan()
                if not success:
                    Logger.error("Échec du scan Wi-Fi.")
                    return []

                # Récupérer les résultats du scan
                scan_results = wifi_manager.getScanResults()
                networks = [result.SSID for result in scan_results if result.SSID]

                Logger.info(f"Wi-Fi networks trouvés : {networks}")
                return networks
            except Exception as e:
                Logger.error(f"Error accessing Wi-Fi on Android: {str(e)}")
                return []

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
