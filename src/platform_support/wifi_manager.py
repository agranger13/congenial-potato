"""
Abstraction de la gestion WiFi pour Android et Windows.
Permet de scanner, connecter et gérer les réseaux WiFi de manière uniforme.
"""
import platform
from abc import ABC, abstractmethod
from typing import List, Optional
from kivy.logger import Logger

from constants import WIFI_PERMISSIONS


class WifiManager(ABC):
    """Interface abstraite pour la gestion WiFi."""

    @abstractmethod
    def get_current_ssid(self) -> str:
        """
        Retourne le SSID du réseau WiFi actuellement connecté.

        Returns:
            Nom du réseau ou "Unknown" si non connecté
        """
        pass

    @abstractmethod
    def scan_networks(self) -> List[str]:
        """
        Scanne les réseaux WiFi disponibles.

        Returns:
            Liste des SSID des réseaux trouvés
        """
        pass

    @abstractmethod
    def connect(self, ssid: str, password: str) -> bool:
        """
        Connecte au réseau WiFi spécifié.

        Args:
            ssid: Nom du réseau
            password: Mot de passe

        Returns:
            True si la connexion a réussi, False sinon
        """
        pass

    @abstractmethod
    def is_wifi_enabled(self) -> bool:
        """Vérifie si le WiFi est activé."""
        pass

    @abstractmethod
    def enable_wifi(self) -> bool:
        """Active le WiFi."""
        pass


class AndroidWifiManager(WifiManager):
    """Implémentation WiFi pour Android utilisant pyjnius."""

    def __init__(self):
        """Initialise le manager WiFi Android."""
        from jnius import autoclass, cast

        self._autoclass = autoclass
        self._cast = cast

        # Obtenir l'activité et le service WiFi
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self._activity = cast('android.app.Activity', PythonActivity.mActivity)
        self._context = cast('android.content.Context', self._activity)

        Context = autoclass('android.content.Context')
        self._wifi_manager = cast(
            'android.net.wifi.WifiManager',
            self._activity.getSystemService(Context.WIFI_SERVICE)
        )

        Logger.info("AndroidWifiManager: Initialisé")

    def get_current_ssid(self) -> str:
        """Retourne le SSID actuel sur Android."""
        try:
            info = self._wifi_manager.getConnectionInfo()
            ssid = info.getSSID()
            # Nettoie les guillemets
            if ssid.startswith('"') and ssid.endswith('"'):
                ssid = ssid[1:-1]
            return ssid
        except Exception as e:
            Logger.warning(f"AndroidWifiManager: Erreur get SSID - {e}")
            return "Unknown"

    def scan_networks(self) -> List[str]:
        """Scanne les réseaux WiFi sur Android."""
        # Vérifier les permissions
        for permission in WIFI_PERMISSIONS:
            if self._activity.checkSelfPermission(permission) != 0:
                self._activity.requestPermissions([permission], 1)
                Logger.warning(f"AndroidWifiManager: Permission manquante - {permission}")
                return []

        # Activer WiFi si nécessaire
        if not self._wifi_manager.isWifiEnabled():
            self._wifi_manager.setWifiEnabled(True)

        # Lancer le scan
        success = self._wifi_manager.startScan()
        if not success:
            Logger.warning("AndroidWifiManager: Échec du scan WiFi")
            return []

        # Récupérer les résultats
        scan_results = self._wifi_manager.getScanResults()
        networks = [result.SSID for result in scan_results if result.SSID]

        Logger.info(f"AndroidWifiManager: {len(networks)} réseaux trouvés")
        return networks

    def connect(self, ssid: str, password: str) -> bool:
        """Connecte au réseau WiFi sur Android."""
        try:
            WifiConfiguration = self._autoclass('android.net.wifi.WifiConfiguration')
            wifi_config = WifiConfiguration()
            wifi_config.SSID = f'"{ssid}"'
            wifi_config.preSharedKey = f'"{password}"'

            network_id = self._wifi_manager.addNetwork(wifi_config)
            if network_id == -1:
                Logger.error(f"AndroidWifiManager: Échec ajout réseau {ssid}")
                return False

            self._wifi_manager.enableNetwork(network_id, True)
            Logger.info(f"AndroidWifiManager: Connexion à {ssid}")
            return True

        except Exception as e:
            Logger.error(f"AndroidWifiManager: Erreur connexion - {e}")
            return False

    def is_wifi_enabled(self) -> bool:
        """Vérifie si le WiFi est activé sur Android."""
        return self._wifi_manager.isWifiEnabled()

    def enable_wifi(self) -> bool:
        """Active le WiFi sur Android."""
        try:
            return self._wifi_manager.setWifiEnabled(True)
        except Exception as e:
            Logger.error(f"AndroidWifiManager: Erreur activation WiFi - {e}")
            return False


class WindowsWifiManager(WifiManager):
    """
    Implémentation WiFi mock pour Windows (développement/test).
    Simule les fonctionnalités WiFi pour permettre le développement sur PC.
    """

    def __init__(self):
        """Initialise le manager WiFi Windows (mock)."""
        self._connected_ssid = "Test_Network"
        self._wifi_enabled = True
        Logger.info("WindowsWifiManager: Mode simulation activé")

    def get_current_ssid(self) -> str:
        """Retourne un SSID de test."""
        return self._connected_ssid

    def scan_networks(self) -> List[str]:
        """Retourne une liste de réseaux de test."""
        return [f"WIFI_NAME_{i}" for i in range(10)]

    def connect(self, ssid: str, password: str) -> bool:
        """Simule une connexion."""
        Logger.info(f"WindowsWifiManager: Simulation connexion à {ssid}")
        self._connected_ssid = ssid
        return True

    def is_wifi_enabled(self) -> bool:
        """Retourne l'état WiFi simulé."""
        return self._wifi_enabled

    def enable_wifi(self) -> bool:
        """Simule l'activation WiFi."""
        self._wifi_enabled = True
        return True


def get_wifi_manager() -> WifiManager:
    """
    Factory pour obtenir le manager WiFi approprié à la plateforme.

    Returns:
        Instance de WifiManager pour la plateforme courante
    """
    if platform.system() == "Windows":
        return WindowsWifiManager()
    else:
        return AndroidWifiManager()
