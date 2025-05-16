from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton

class BottomNavigation(MDBoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super(BottomNavigation, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, 0.1)
        self.spacing = '10dp'  # Espacement entre les boutons

        # Bouton pour la page d'accueil avec icône FontAwesome
        self.home_button = MDIconButton(
            icon="home",
            on_release=lambda x: self.change_screen('home')
        )
        self.home_button.size_hint = (1, 1)  # Prendre tout l'espace horizontal
        self.add_widget(self.home_button)

        # Bouton pour la page des paramètres avec icône FontAwesome
        self.settings_button = MDIconButton(
            icon="cog",
            on_release=lambda x: self.change_screen('settings')
        )
        self.settings_button.size_hint = (1, 1)  # Prendre tout l'espace horizontal
        self.add_widget(self.settings_button)

        # Bouton pour la page de contrôles avec icône FontAwesome
        self.controls_button = MDIconButton(
            icon="gamepad",  # Remplacez par une icône appropriée pour les contrôles
            on_release=lambda x: self.change_screen('controls')
        )
        self.controls_button.size_hint = (1, 1)  # Prendre tout l'espace horizontal
        self.add_widget(self.controls_button)

        self.screen_manager = screen_manager

    def change_screen(self, screen_name):
        self.screen_manager.current = screen_name
