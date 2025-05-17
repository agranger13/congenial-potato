from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

class ConnectDialogContent(BoxLayout):
    def __init__(self, ssid, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height="100dp", **kwargs)

        self.ssid_label = MDLabel(text=f"Connect to: {ssid}", halign='center')
        self.add_widget(self.ssid_label)

        self.password_field = MDTextField(
            hint_text="Password",
            password=True,
            size_hint=(1, None),
            height='40dp'
        )
        self.add_widget(self.password_field)

    def get_password(self):
        return self.password_field.text
