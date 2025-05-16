from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

class HomePage(MDScreen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        self.add_widget(MDLabel(text='Home Page', halign='center'))
