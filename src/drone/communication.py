"""
Module de communication UDP avec le drone.
Gère l'envoi des commandes et le heartbeat.
"""
import socket
from dataclasses import dataclass
from typing import Callable, Optional
from kivy.logger import Logger

from constants import (
    ARM_STATE_DISARMED,
    ARM_STATE_ARMED,
    EMERGENCY_STATE_NORMAL,
    EMERGENCY_STATE_ACTIVE,
    JOYSTICK_CENTER,
    THROTTLE_DEFAULT
)


@dataclass
class DroneCommand:
    """
    Structure de commande à envoyer au drone.

    Format CSV: leftX,leftY,rightX,rightY,armed,emergency
    Exemple: 512,480,500,100,1,0
    """
    left_x: int = JOYSTICK_CENTER    # Roll
    left_y: int = JOYSTICK_CENTER    # Pitch
    right_x: int = JOYSTICK_CENTER   # Yaw
    right_y: int = THROTTLE_DEFAULT  # Throttle
    armed: int = ARM_STATE_DISARMED
    emergency: int = EMERGENCY_STATE_NORMAL

    def to_csv(self) -> str:
        """Convertit la commande en format CSV pour transmission."""
        return f"{self.left_x},{self.left_y},{self.right_x},{self.right_y},{self.armed},{self.emergency}"

    def reset_to_safe(self) -> None:
        """Remet la commande en état sécurisé (désarmé, throttle bas)."""
        self.armed = ARM_STATE_DISARMED
        self.right_y = 0  # Throttle à zéro

    def toggle_armed(self) -> bool:
        """
        Bascule l'état d'armement.

        Returns:
            True si armé après le toggle, False sinon
        """
        self.armed = ARM_STATE_ARMED if self.armed == ARM_STATE_DISARMED else ARM_STATE_DISARMED
        return self.armed == ARM_STATE_ARMED

    def trigger_emergency(self) -> None:
        """Active l'état d'urgence et désarme."""
        self.emergency = EMERGENCY_STATE_ACTIVE
        self.armed = ARM_STATE_DISARMED
        self.right_y = 0  # Throttle à zéro

    def clear_emergency(self) -> None:
        """Réinitialise l'état d'urgence."""
        self.emergency = EMERGENCY_STATE_NORMAL


class DroneConnection:
    """
    Gère la connexion UDP avec le drone.

    Attributes:
        ip: Adresse IP du drone
        port: Port UDP du drone
        on_error: Callback optionnel appelé en cas d'erreur
    """

    def __init__(
        self,
        ip: str,
        port: int,
        on_error: Optional[Callable[[str], None]] = None
    ):
        """
        Initialise la connexion au drone.

        Args:
            ip: Adresse IP du drone
            port: Port UDP du drone
            on_error: Callback optionnel pour les erreurs
        """
        self.ip = ip
        self.port = port
        self.on_error = on_error
        self._socket: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> bool:
        """
        Crée le socket UDP.

        Returns:
            True si la connexion est établie, False sinon
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._connected = True
            Logger.info(f"DroneConnection: Socket créé pour {self.ip}:{self.port}")
            return True
        except OSError as e:
            self._handle_error(f"Erreur création socket: {e}")
            return False

    def disconnect(self) -> None:
        """Ferme le socket proprement."""
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
            self._connected = False
            Logger.info("DroneConnection: Socket fermé")

    def send_command(self, command: DroneCommand) -> bool:
        """
        Envoie une commande au drone.

        Args:
            command: Instance de DroneCommand à envoyer

        Returns:
            True si l'envoi a réussi, False sinon
        """
        if not self._socket:
            self._handle_error("Socket non initialisé")
            return False

        try:
            message = command.to_csv()
            self._socket.sendto(message.encode(), (self.ip, self.port))

            # Log uniquement si armé ou urgence
            if command.armed or command.emergency:
                Logger.info(f"Drone CMD: {message}")

            return True

        except OSError as e:
            self._handle_error(f"Erreur envoi commande: {e}")
            return False

    def update_address(self, ip: str, port: int) -> None:
        """
        Met à jour l'adresse du drone.

        Args:
            ip: Nouvelle adresse IP
            port: Nouveau port
        """
        self.ip = ip
        self.port = port
        Logger.info(f"DroneConnection: Adresse mise à jour - {ip}:{port}")

    @property
    def is_connected(self) -> bool:
        """Retourne l'état de connexion."""
        return self._connected

    @property
    def address(self) -> str:
        """Retourne l'adresse formatée."""
        return f"{self.ip}:{self.port}"

    def _handle_error(self, message: str) -> None:
        """
        Gère les erreurs de communication.

        Args:
            message: Message d'erreur
        """
        Logger.error(f"DroneConnection: {message}")
        if self.on_error:
            self.on_error(message)
