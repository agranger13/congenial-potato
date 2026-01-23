"""
Abstraction pour le stockage des préférences.
Android utilise SharedPreferences, Windows utilise un fichier JSON.
"""
import json
import platform
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
from kivy.logger import Logger

from constants import PREFERENCES_NAME, DEFAULT_DRONE_IP, DEFAULT_DRONE_PORT


class PreferencesManager(ABC):
    """Interface abstraite pour la gestion des préférences."""

    @abstractmethod
    def get_string(self, key: str, default: str = "") -> str:
        """Récupère une valeur string."""
        pass

    @abstractmethod
    def put_string(self, key: str, value: str) -> None:
        """Enregistre une valeur string."""
        pass

    @abstractmethod
    def get_int(self, key: str, default: int = 0) -> int:
        """Récupère une valeur int."""
        pass

    @abstractmethod
    def put_int(self, key: str, value: int) -> None:
        """Enregistre une valeur int."""
        pass

    @abstractmethod
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Récupère une valeur bool."""
        pass

    @abstractmethod
    def put_bool(self, key: str, value: bool) -> None:
        """Enregistre une valeur bool."""
        pass


class AndroidPreferencesManager(PreferencesManager):
    """Implémentation des préférences pour Android (SharedPreferences)."""

    def __init__(self, name: str = PREFERENCES_NAME):
        """
        Initialise le manager de préférences Android.

        Args:
            name: Nom du fichier SharedPreferences
        """
        from jnius import autoclass, cast

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        context = cast('android.content.Context', activity)

        self._prefs = context.getSharedPreferences(name, 0)
        Logger.info(f"AndroidPreferencesManager: Initialisé ({name})")

    def get_string(self, key: str, default: str = "") -> str:
        return self._prefs.getString(key, default)

    def put_string(self, key: str, value: str) -> None:
        editor = self._prefs.edit()
        editor.putString(key, value)
        editor.apply()

    def get_int(self, key: str, default: int = 0) -> int:
        return self._prefs.getInt(key, default)

    def put_int(self, key: str, value: int) -> None:
        editor = self._prefs.edit()
        editor.putInt(key, value)
        editor.apply()

    def get_bool(self, key: str, default: bool = False) -> bool:
        return self._prefs.getBoolean(key, default)

    def put_bool(self, key: str, value: bool) -> None:
        editor = self._prefs.edit()
        editor.putBoolean(key, value)
        editor.apply()


class WindowsPreferencesManager(PreferencesManager):
    """
    Implémentation des préférences pour Windows (fichier JSON).
    Utilisé pour le développement/test.
    """

    def __init__(self, name: str = PREFERENCES_NAME):
        """
        Initialise le manager de préférences Windows.

        Args:
            name: Nom du fichier de préférences (sans extension)
        """
        self._file_path = Path.home() / f".{name}.json"
        self._data: dict = {}
        self._load()
        Logger.info(f"WindowsPreferencesManager: Initialisé ({self._file_path})")

    def _load(self) -> None:
        """Charge les préférences depuis le fichier."""
        if self._file_path.exists():
            try:
                with open(self._file_path, 'r') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                Logger.warning(f"WindowsPreferencesManager: Erreur chargement - {e}")
                self._data = {}

    def _save(self) -> None:
        """Sauvegarde les préférences dans le fichier."""
        try:
            with open(self._file_path, 'w') as f:
                json.dump(self._data, f, indent=2)
        except IOError as e:
            Logger.error(f"WindowsPreferencesManager: Erreur sauvegarde - {e}")

    def get_string(self, key: str, default: str = "") -> str:
        return str(self._data.get(key, default))

    def put_string(self, key: str, value: str) -> None:
        self._data[key] = value
        self._save()

    def get_int(self, key: str, default: int = 0) -> int:
        return int(self._data.get(key, default))

    def put_int(self, key: str, value: int) -> None:
        self._data[key] = value
        self._save()

    def get_bool(self, key: str, default: bool = False) -> bool:
        return bool(self._data.get(key, default))

    def put_bool(self, key: str, value: bool) -> None:
        self._data[key] = value
        self._save()


def get_preferences_manager(name: str = PREFERENCES_NAME) -> PreferencesManager:
    """
    Factory pour obtenir le manager de préférences approprié à la plateforme.

    Args:
        name: Nom des préférences

    Returns:
        Instance de PreferencesManager pour la plateforme courante
    """
    if platform.system() == "Windows":
        return WindowsPreferencesManager(name)
    else:
        return AndroidPreferencesManager(name)
