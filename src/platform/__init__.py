"""
Module d'abstraction plateforme.
Fournit des interfaces unifiées pour les fonctionnalités spécifiques à chaque OS.
"""
import platform as _platform
from .wifi_manager import WifiManager, get_wifi_manager
from .preferences import PreferencesManager, get_preferences_manager

# Détection de la plateforme courante
IS_ANDROID = _platform.system() != "Windows"
IS_WINDOWS = _platform.system() == "Windows"
PLATFORM_NAME = "Android" if IS_ANDROID else "Windows"
