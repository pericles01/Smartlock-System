from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from manage.Database import Database


class UserMembershipView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserMembershipView, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.found_user = MDApp.get_running_app().found_user
        print(f"Welcome {self.found_user[0]}, {self.found_user[1]} !")
        self.ids.topbar.title = f"Welcome {self.found_user[0]}, {self.found_user[1]} !"
        self.ids.user_welcome_screen.found_user = self.found_user
        self.ids.update_pin_screen.found_user = self.found_user
        self.ids.manager.current = "home" # reload the page to trigger his on_pre_enter event


class UpdateUserPinView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UpdateUserPinView, self).__init__(**kwargs)
        self.__db = Database()

    def on_enter(self, *args):

        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)

    def update_pin(self):
        if self.ids.new_pin.ids.password_field.text.strip() and self.ids.confirm_pin.ids.password_field.text.strip():
            try:
                new_pin = int(self.ids.new_pin.ids.password_field.text.strip())
                confirm_pin = int(self.ids.confirm_pin.ids.password_field.text.strip())
                if new_pin == confirm_pin:
                    if len(str(new_pin)) == 6 and len(str(confirm_pin)) == 6:
                        if self.__db.update_user_pin(list(self.found_user), confirm_pin):
                            toast(f"PIN Successfully updated",
                                  background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                                  )
                            # reset
                            self.ids.new_pin.ids.password_field.text = ""
                            self.ids.confirm_pin.ids.password_field.text = ""
                            self.ids.error_label.text = "* required fields, PIN must have 6 digits"
                            print("---------")
                            print("Test Update")
                            print("---------")
                            print(self.__db.show_users_table(full=True))
                        else:
                            self.ids.error_label.text = "Error by updating PIN, please try again"
                    else:
                        self.ids.error_label.text = "PIN must have 6 digits"
                else:
                    self.ids.error_label.text = "New PIN must be equal to confirmation PIN"
            except ValueError:
                self.ids.error_label.text = "New PIN and Confirmation PIN must be numeric numbers"

        else:
            self.ids.error_label.text = "Please fill required fields"



