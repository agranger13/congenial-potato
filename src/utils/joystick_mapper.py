"""
Logique de mapping des valeurs joystick.
Convertit les entrées brutes (-1.0 à 1.0) vers les valeurs de commande drone.
"""
from typing import Tuple
from constants import (
    JOYSTICK_CENTER,
    JOYSTICK_MIN,
    JOYSTICK_MAX,
    DEADZONE,
    THROTTLE_MIN,
    THROTTLE_MAX,
    THROTTLE_DEADZONE,
    MAX_ROLL_PITCH_DEGREES,
    MAX_YAW_RATE,
    THROTTLE_LOW_THRESHOLD,
    THROTTLE_HIGH_THRESHOLD,
    COLOR_THROTTLE_LOW,
    COLOR_THROTTLE_MEDIUM,
    COLOR_THROTTLE_HIGH,
    Color
)


class JoystickMapper:
    """
    Classe pour mapper les valeurs du joystick vers les commandes drone.

    Le joystick renvoie des valeurs entre -1.0 et 1.0.
    Le drone attend des valeurs entre 0 et 1023 (sauf throttle: 0-200).
    """

    def __init__(self, deadzone: int = DEADZONE):
        """
        Initialise le mapper avec une zone morte configurable.

        Args:
            deadzone: Valeur de zone morte autour du centre (défaut: 20)
        """
        self.deadzone = deadzone

    def map_axis(self, pad_value: float) -> int:
        """
        Convertit une valeur de pad (-1.0 à 1.0) vers une valeur joystick (0-1023)
        avec zone morte appliquée.

        Args:
            pad_value: Valeur du pad entre -1.0 et 1.0

        Returns:
            Valeur entière entre 0 et 1023
        """
        # Convertir de [-1, 1] vers [0, 1023]
        joystick_value = int((pad_value + 1.0) * 511.5)

        # Appliquer la zone morte autour du centre (512)
        if abs(joystick_value - JOYSTICK_CENTER) <= self.deadzone:
            joystick_value = JOYSTICK_CENTER

        # Limiter les valeurs
        return max(JOYSTICK_MIN, min(JOYSTICK_MAX, joystick_value))

    def map_throttle(self, pad_y: float) -> int:
        """
        Mapping spécial pour le throttle.
        -1.0 (bas) = 0, +1.0 (haut) = 200

        Args:
            pad_y: Valeur Y du pad entre -1.0 et 1.0

        Returns:
            Valeur throttle entre 0 et 200
        """
        throttle_value = int((pad_y + 1.0) * 100)  # [-1, 1] -> [0, 200]

        # Zone morte en bas pour le throttle
        if throttle_value <= THROTTLE_DEADZONE:
            throttle_value = THROTTLE_MIN

        return max(THROTTLE_MIN, min(THROTTLE_MAX, throttle_value))

    @staticmethod
    def joystick_to_degrees(joystick_value: int, max_degrees: int = MAX_ROLL_PITCH_DEGREES) -> int:
        """
        Convertit une valeur joystick (0-1023) en degrés.

        Args:
            joystick_value: Valeur entre 0 et 1023
            max_degrees: Angle maximum (défaut: 30°)

        Returns:
            Angle en degrés (positif ou négatif)
        """
        return int((joystick_value - JOYSTICK_CENTER) * max_degrees / 511)

    @staticmethod
    def joystick_to_yaw_rate(joystick_value: int) -> int:
        """
        Convertit une valeur joystick X (0-1023) en vitesse de rotation yaw.

        Args:
            joystick_value: Valeur entre 0 et 1023

        Returns:
            Vitesse de rotation en degrés/seconde
        """
        return int((joystick_value - JOYSTICK_CENTER) * MAX_YAW_RATE / 511)

    @staticmethod
    def throttle_to_percent(throttle_value: int) -> int:
        """
        Convertit une valeur throttle (0-200) en pourcentage.

        Args:
            throttle_value: Valeur entre 0 et 200

        Returns:
            Pourcentage entre 0 et 100
        """
        return int(throttle_value * 100 / THROTTLE_MAX)

    @staticmethod
    def get_throttle_color(throttle_percent: int) -> Color:
        """
        Retourne la couleur appropriée selon le niveau de throttle.

        Args:
            throttle_percent: Pourcentage de throttle (0-100)

        Returns:
            Tuple RGBA de couleur
        """
        if throttle_percent > THROTTLE_HIGH_THRESHOLD:
            return COLOR_THROTTLE_HIGH
        elif throttle_percent > THROTTLE_LOW_THRESHOLD:
            return COLOR_THROTTLE_MEDIUM
        else:
            return COLOR_THROTTLE_LOW

    def map_left_joystick(self, pad_x: float, pad_y: float) -> Tuple[int, int, int, int]:
        """
        Mappe le joystick gauche (Roll/Pitch).

        Args:
            pad_x: Valeur X du pad (-1.0 à 1.0)
            pad_y: Valeur Y du pad (-1.0 à 1.0)

        Returns:
            Tuple (left_x, left_y, roll_degrees, pitch_degrees)
        """
        left_x = self.map_axis(pad_x)
        left_y = self.map_axis(pad_y)
        roll_degrees = self.joystick_to_degrees(left_x)
        pitch_degrees = self.joystick_to_degrees(left_y)

        return left_x, left_y, roll_degrees, pitch_degrees

    def map_right_joystick(self, pad_x: float, pad_y: float) -> Tuple[int, int, int, int, Color]:
        """
        Mappe le joystick droit (Yaw/Throttle).

        Args:
            pad_x: Valeur X du pad (-1.0 à 1.0)
            pad_y: Valeur Y du pad (-1.0 à 1.0)

        Returns:
            Tuple (right_x, right_y, yaw_rate, throttle_percent, throttle_color)
        """
        right_x = self.map_axis(pad_x)
        right_y = self.map_throttle(pad_y)
        yaw_rate = self.joystick_to_yaw_rate(right_x)
        throttle_percent = self.throttle_to_percent(right_y)
        throttle_color = self.get_throttle_color(throttle_percent)

        return right_x, right_y, yaw_rate, throttle_percent, throttle_color
