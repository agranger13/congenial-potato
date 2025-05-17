from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.uix.screenmanager import SlideTransition

class BottomNavigation(MDBoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super(BottomNavigation, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, 0.1)
        self.spacing = '10dp'

        self.screen_manager = screen_manager
        self.current_screen = 'home'

        self.buttons = {}

        self.controls_button = self.create_button("controls", "gamepad")
        self.home_button = self.create_button("home", "home")
        self.settings_button = self.create_button("settings", "cog")



        self.set_active_button("home")

    def create_button(self, screen_name, icon_name):
        button = MDIconButton(
            icon=icon_name,
            on_release=lambda x: self.change_screen(screen_name),
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1)
        )
        button.size_hint = (1, 1)
        self.add_widget(button)
        self.buttons[screen_name] = button
        return button

    def change_screen(self, target):
        source = self.current_screen

        # Définir la direction selon la logique demandée
        direction = 'left'  # par défaut
        if source == 'home' and target == 'settings':
            direction = 'left'
        elif source == 'settings' and target == 'home':
            direction = 'right'
        elif source == 'home' and target == 'controls':
            direction = 'right'
        elif source == 'controls' and target == 'home':
            direction = 'left'
        elif source == 'settings' and target == 'controls':
            direction = 'right'
        elif source == 'controls' and target == 'settings':
            direction = 'left'

        # Appliquer la transition et changer d'écran
        self.screen_manager.transition = SlideTransition(direction=direction, duration=0.3)
        self.screen_manager.current = target
        self.current_screen = target
        self.set_active_button(target)

    def set_active_button(self, active_name):
        for name, button in self.buttons.items():
            button.text_color = (1, 0.5, 0, 1) if name == active_name else (0.5, 0.5, 0.5, 1)
