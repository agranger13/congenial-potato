"""
Barre de navigation inférieure pour l'application.
Permet de naviguer entre les différentes pages.
"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.uix.screenmanager import SlideTransition

from constants import (
    NAV_HEIGHT_RATIO,
    NAV_SPACING,
    TRANSITION_DURATION,
    COLOR_ICON_ACTIVE,
    COLOR_NAV_INACTIVE,
)


# Configuration des écrans et leurs positions relatives
SCREEN_ORDER = ['controls', 'home', 'settings']


class BottomNavigation(MDBoxLayout):
    """
    Barre de navigation avec 3 boutons icônes.

    Gère les transitions animées entre les écrans.
    """

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, NAV_HEIGHT_RATIO)
        self.spacing = NAV_SPACING

        self._screen_manager = screen_manager
        self._current_screen = 'home'
        self._buttons = {}

        # Créer les boutons de navigation
        self._create_buttons()
        self._set_active_button('home')

    def _create_buttons(self):
        """Crée les boutons de navigation."""
        nav_items = [
            ('controls', 'gamepad'),
            ('home', 'home'),
            ('settings', 'cog'),
        ]

        for screen_name, icon_name in nav_items:
            button = MDIconButton(
                icon=icon_name,
                on_release=lambda x, name=screen_name: self._change_screen(name),
                theme_text_color="Custom",
                text_color=COLOR_NAV_INACTIVE,
                size_hint=(1, 1)
            )
            self.add_widget(button)
            self._buttons[screen_name] = button

    def _change_screen(self, target: str):
        """
        Change d'écran avec animation de transition.

        Args:
            target: Nom de l'écran cible
        """
        source = self._current_screen
        if source == target:
            return

        # Déterminer la direction de la transition
        direction = self._get_transition_direction(source, target)

        # Appliquer la transition
        self._screen_manager.transition = SlideTransition(
            direction=direction,
            duration=TRANSITION_DURATION
        )
        self._screen_manager.current = target
        self._current_screen = target
        self._set_active_button(target)

    def _get_transition_direction(self, source: str, target: str) -> str:
        """
        Détermine la direction de transition entre deux écrans.

        Args:
            source: Écran source
            target: Écran cible

        Returns:
            Direction ('left' ou 'right')
        """
        try:
            source_idx = SCREEN_ORDER.index(source)
            target_idx = SCREEN_ORDER.index(target)
            return 'left' if target_idx > source_idx else 'right'
        except ValueError:
            return 'left'

    def _set_active_button(self, active_name: str):
        """
        Met en surbrillance le bouton actif.

        Args:
            active_name: Nom de l'écran actif
        """
        for name, button in self._buttons.items():
            button.text_color = (
                COLOR_ICON_ACTIVE if name == active_name else COLOR_NAV_INACTIVE
            )
