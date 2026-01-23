"""
Configuration du drone avec pattern Singleton.
Utilise l'abstraction plateforme pour le stockage des préférences.
"""
from typing import Dict
from kivy.logger import Logger

from constants import DEFAULT_DRONE_IP, DEFAULT_DRONE_PORT
from platform_support import get_preferences_manager


class DroneConfig:
    """
    Classe singleton pour gérer la configuration du drone.

    Attributes:
        ip: Adresse IP du drone
        port: Port de communication
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DroneConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._prefs = get_preferences_manager()
            self.ip = DEFAULT_DRONE_IP
            self.port = DEFAULT_DRONE_PORT
            DroneConfig._initialized = True
            self._load_config()

    def _load_config(self) -> None:
        """Charge la configuration depuis les préférences."""
        try:
            self.ip = self._prefs.get_string("drone_ip", self.ip)
            self.port = self._prefs.get_string("drone_port", self.port)
            Logger.info(f"DroneConfig: Chargé IP={self.ip}, Port={self.port}")
        except Exception as e:
            Logger.warning(f"DroneConfig: Erreur chargement - {e}")

    def _save_config(self) -> None:
        """Sauvegarde la configuration dans les préférences."""
        try:
            self._prefs.put_string("drone_ip", self.ip)
            self._prefs.put_string("drone_port", self.port)
            Logger.info(f"DroneConfig: Sauvegardé IP={self.ip}, Port={self.port}")
        except Exception as e:
            Logger.warning(f"DroneConfig: Erreur sauvegarde - {e}")

    def get_config(self) -> Dict[str, str]:
        """
        Retourne la configuration actuelle.

        Returns:
            Dictionnaire avec les clés 'ip' et 'port'
        """
        return {'ip': self.ip, 'port': self.port}

    def set_config(self, ip: str, port: str) -> None:
        """
        Met à jour la configuration.

        Args:
            ip: Nouvelle adresse IP
            port: Nouveau port
        """
        self.ip = ip
        self.port = port
        self._save_config()
