from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from screens.home import HomePage
from screens.settings import SettingsPage
from screens.controls import ControlsPage
from components.bottom_navigation import BottomNavigation
from kivy.logger import Logger, LOG_LEVELS

class MyScreenManager(ScreenManager):
    pass

class MyApp(MDApp):
    def build(self):
        screen_manager = MyScreenManager()
        
        screen_manager.add_widget(ControlsPage(name='controls'))
        screen_manager.add_widget(HomePage(name='home'))
        screen_manager.add_widget(SettingsPage(name='settings'))

        bottom_navigation = BottomNavigation(screen_manager=screen_manager)

        layout = MDBoxLayout(orientation='vertical')
        layout.add_widget(screen_manager)
        layout.add_widget(bottom_navigation)

        return layout

if __name__ == '__main__':
    Logger.setLevel(LOG_LEVELS["debug"])
    MyApp().run()
