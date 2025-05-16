from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

class ControlsPage(MDScreen):
    def __init__(self, **kwargs):
        super(ControlsPage, self).__init__(**kwargs)
        self.add_widget(MDLabel(text='Profile Page', halign='center'))
