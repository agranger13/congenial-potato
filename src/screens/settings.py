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
from kivy.clock import Clock
from jnius import autoclass, cast
import platform

from components.connect_dialog_content import ConnectDialogContent

class SettingsPage(MDScreen):
    def __init__(self, **kwargs):
        super(SettingsPage, self).__init__(**kwargs)
        self.current_activity = self._get_current_activity()
        self.wifi_manager = self._get_wifi_manager()
        
        
        layout = MDBoxLayout(orientation='vertical', spacing='10dp', padding='10dp')

        self.ssid_label = MDLabel(text='Current SSID: Unknown', halign='center')
        layout.add_widget(self.ssid_label)

        self.scan_button = MDRectangleFlatButton(
            text='Scan Wi-Fi Networks',
            pos_hint={'center_x': 0.5},
            on_release=self.scan_wifi_networks
        )
        layout.add_widget(self.scan_button)

        self.add_widget(layout)
        Clock.schedule_once(self.update_current_ssid, 0.5)

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
