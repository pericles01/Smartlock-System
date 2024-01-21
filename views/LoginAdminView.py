from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
import os
from kivymd.toast import toast
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from manage.Database import Database


class LoginAdminCard(MDCard):
    login_image = StringProperty()
    def __init__(self, **kwargs):
        super(LoginAdminCard, self).__init__(**kwargs)
        self.login_image = os.path.join(os.getcwd(), "ressources/galaxy.jpg")
        self.__db = Database()

    def login(self, manager) -> None:

        try:
            if self.ids.username_field.text.strip() and self.ids.password_widget.ids.password_field.text.strip():
                self.__db.db_init(refresh=True)
                admins = self.__db.show_admin_table()
                print(f"Admins list: {admins}")
                if self.ids.username_field.text.strip() == admins[1][1] and self.ids.password_widget.ids.password_field.text.strip() == admins[1][2]:
                    manager.push("technician_membership")
                    # clear the fields
                    self.ids.username_field.text = ""
                    self.ids.password_widget.ids.password_field.text = ""
                    self.login_successful = True
                    toast(f"Successfully logged in technician membership",
                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                          )
                elif self.ids.username_field.text.strip() == admins[0][1] and self.ids.password_widget.ids.password_field.text.strip() == admins[0][2]:
                    manager.push("admin_membership")
                    # clear the fields
                    self.ids.username_field.text = ""
                    self.ids.password_widget.ids.password_field.text = ""
                    toast(f"Successfully logged in admin membership",
                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                          )
                else:
                    self.ids.error_label.text = "Wrong login credentials. Please try again!!"
            else:
                self.ids.error_label.text = "Please fill required fields!"
        except Exception as e:
            print(e)
