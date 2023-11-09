from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.card import MDCard
import os


class LoginAdminCard(MDCard):
    login_image = StringProperty()
    login_successful = BooleanProperty()
    def __init__(self, **kwargs):
        super(LoginAdminCard, self).__init__(**kwargs)
        self.login_image = os.path.join(os.getcwd(), "ressources/galaxy.jpg")

    def login(self, manager) -> None:
        if self.ids.username_field.text.strip() == "tech" and self.ids.password_widget.ids.password_field.text == "setup":
            manager.push("technician_membership")
            # clear the fields
            self.ids.username_field.text = ""
            self.ids.password_widget.ids.password_field.text = ""
            self.login_successful = True
        elif self.ids.username_field.text.strip() == "admin" and self.ids.password_widget.ids.password_field.text == "admin":
            manager.push("admin_membership")
            # clear the fields
            self.ids.username_field.text = ""
            self.ids.password_widget.ids.password_field.text = ""
        else:
            self.login_successful = False
