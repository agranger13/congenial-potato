"""
Constantes centralisées pour l'application DroneDelivery.
Toutes les valeurs magiques, couleurs et configurations sont définies ici.
"""
from typing import Tuple

# =============================================================================
# CONFIGURATION DRONE
# =============================================================================

DEFAULT_DRONE_IP = "192.168.4.1"
DEFAULT_DRONE_PORT = "4210"  # Doit correspondre au port UDP du firmware
PREFERENCES_NAME = "DroneSettings"

# =============================================================================
# VALEURS JOYSTICK
# =============================================================================

JOYSTICK_CENTER = 512
JOYSTICK_MIN = 0
JOYSTICK_MAX = 1023
JOYSTICK_RANGE = JOYSTICK_MAX - JOYSTICK_MIN

# Zone morte
DEADZONE = 20

# Throttle
# Le firmware traite les 4 axes sur la même échelle 0-1023 :
# il calcule rightY / 1023 avant de multiplier par son propre MAX_THROTTLE.
# Envoyer le throttle sur une échelle plus courte briderait la puissance.
THROTTLE_MIN = 0
THROTTLE_MAX = JOYSTICK_MAX
THROTTLE_DEFAULT = 0  # Gaz à zéro au démarrage
THROTTLE_DEADZONE = 50  # ~5% de la plage, comme avant le passage à 0-1023

# Conversion angles
MAX_ROLL_PITCH_DEGREES = 30
MAX_YAW_RATE = 180  # degrés/seconde

# =============================================================================
# TIMING
# =============================================================================

HEARTBEAT_INTERVAL = 0.1  # secondes (100ms)
SAFETY_TIMEOUT = 5.0  # secondes avant désarmement automatique
EMERGENCY_RESET_DELAY = 1.0  # secondes
UI_SETUP_DELAY = 0.5  # secondes
SSID_UPDATE_DELAY = 0.5  # secondes
GRAPHICS_UPDATE_DELAY = 0.2  # secondes
BUTTON_FLASH_DURATION = 0.1  # secondes
TRANSITION_DURATION = 0.3  # secondes

# =============================================================================
# COULEURS (RGBA)
# =============================================================================

# Couleurs de base
Color = Tuple[float, float, float, float]

COLOR_WHITE: Color = (1, 1, 1, 1)
COLOR_BLACK: Color = (0, 0, 0, 1)
COLOR_TRANSPARENT: Color = (0, 0, 0, 0)

# Couleurs de statut
COLOR_SUCCESS: Color = (0.3, 1, 0.3, 1)  # Vert clair
COLOR_ERROR: Color = (1, 0.3, 0.3, 1)  # Rouge clair
COLOR_WARNING: Color = (1, 0.5, 0, 1)  # Orange
COLOR_DANGER: Color = (1, 0, 0, 1)  # Rouge vif

# Couleurs des boutons
COLOR_BUTTON_ARM: Color = (0.2, 0.7, 0.2, 1)  # Vert
COLOR_BUTTON_DISARM: Color = (0.9, 0.3, 0.3, 1)  # Rouge
COLOR_BUTTON_EMERGENCY: Color = (0.9, 0.1, 0.1, 1)  # Rouge vif
COLOR_BUTTON_FLASH: Color = (1, 1, 1, 1)  # Blanc (flash)

# Couleurs des cards
COLOR_CARD_DARK: Color = (0.1, 0.1, 0.1, 0.2)  # Fond sombre semi-transparent
COLOR_CARD_LEFT_JOYSTICK: Color = (0.05, 0.05, 0.15, 0.7)  # Bleu très sombre
COLOR_CARD_RIGHT_JOYSTICK: Color = (0.15, 0.05, 0.05, 0.7)  # Rouge très sombre

# Couleurs des labels joystick
COLOR_LABEL_LEFT: Color = (0.8, 0.9, 1, 1)  # Bleu clair
COLOR_LABEL_RIGHT: Color = (1, 0.9, 0.8, 1)  # Orange clair

# Couleurs des icônes
COLOR_ICON_INACTIVE: Color = (0.7, 0.7, 0.7, 1)  # Gris
COLOR_ICON_ACTIVE: Color = (1, 0.5, 0, 1)  # Orange
COLOR_NAV_INACTIVE: Color = (0.5, 0.5, 0.5, 1)  # Gris navigation

# Couleurs du throttle
COLOR_THROTTLE_LOW: Color = (0.3, 1, 0.3, 1)  # Vert (< 30%)
COLOR_THROTTLE_MEDIUM: Color = (1, 0.8, 0.3, 1)  # Orange (30-70%)
COLOR_THROTTLE_HIGH: Color = (1, 0.3, 0.3, 1)  # Rouge (> 70%)

# Seuils throttle (en pourcentage)
THROTTLE_LOW_THRESHOLD = 30
THROTTLE_HIGH_THRESHOLD = 70

# Couleurs du joystick widget
COLOR_JOYSTICK_BASE: Color = (0.7, 0.7, 0.7, 0.3)  # Gris clair transparent
COLOR_JOYSTICK_BORDER: Color = (0.5, 0.5, 0.5, 1.0)  # Gris
COLOR_JOYSTICK_KNOB: Color = (0.4, 0.4, 0.4, 1.0)  # Gris foncé

# =============================================================================
# DIMENSIONS UI
# =============================================================================

# Joystick
JOYSTICK_SIZE = (280, 280)
JOYSTICK_WIDGET_SIZE = (500, 500)
KNOB_RADIUS = 45
BORDER_WIDTH = 2

# Boutons
BUTTON_SIZE = ("180dp", "60dp")
BUTTON_HEIGHT = "60dp"
INFO_BUTTON_HEIGHT = "40dp"
ICON_SIZE = "25dp"

# Cards
CARD_RADIUS = [5, 5, 5, 5]
STATUS_CARD_HEIGHT_RATIO = 0.2
JOYSTICK_CARD_HEIGHT_RATIO = 0.8
WIFI_CARD_HEIGHT = "200dp"
DRONE_CARD_HEIGHT = "220dp"
DIALOG_LIST_HEIGHT = "300dp"
DIALOG_CONTENT_HEIGHT = "150dp"
CONNECT_DIALOG_HEIGHT = "100dp"

# Spacing & Padding
LAYOUT_SPACING = 15
CARD_SPACING = 10
CARD_PADDING = 15
BUTTON_SPACING = 25
NAV_SPACING = "10dp"
SCREEN_PADDING = "20dp"

# Navigation
NAV_HEIGHT_RATIO = 0.1

# =============================================================================
# TAILLES DE POLICE
# =============================================================================

FONT_SIZE_BUTTON = "16sp"
FONT_SIZE_LABEL = "14sp"

# =============================================================================
# CONSTANTES RÉSEAU
# =============================================================================

UDP_SOCKET_TYPE = "SOCK_DGRAM"
WIFI_PERMISSIONS = [
    "android.permission.ACCESS_WIFI_STATE",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.CHANGE_WIFI_STATE",
]

# =============================================================================
# ÉTATS
# =============================================================================

ARM_STATE_DISARMED = 0
ARM_STATE_ARMED = 1
EMERGENCY_STATE_NORMAL = 0
EMERGENCY_STATE_ACTIVE = 1

# =============================================================================
# MESSAGES UI
# =============================================================================

MSG_DISARMED = "DÉSARMÉ"
MSG_ARMED = "ARMÉ"
MSG_EMERGENCY = "URGENCE!"
MSG_TIMEOUT = "TIMEOUT - DÉSARMÉ"
MSG_CONNECTION_ERROR = "ERREUR CONNEXION"
MSG_NO_WIFI = "No Wi-Fi networks found."
