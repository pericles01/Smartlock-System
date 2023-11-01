from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.relativelayout import MDRelativeLayout
import os


class LoginAdminCard(MDCard):
    login_image = StringProperty()
    def __init__(self, **kwargs):
        super(LoginAdminCard, self).__init__(**kwargs)
        self.login_image = os.path.normpath("/home/peri/Desktop/Studium/Masterarbeit/Smartlock-System/ressources/monkeywillkommen1.png")

    def login(self, manager):
        if self.ids.username_field.text:
            if self.ids.password_widget.ids.password_field.text:
                manager.push("technician_membership")
                # clear the fields
                self.ids.username_field.text = ""
                self.ids.password_widget.ids.password_field.text = ""
