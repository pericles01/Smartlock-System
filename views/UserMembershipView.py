from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from manage.Database import Database
import qrcode
from random import choice
import os
import string
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
        self.ids.user_qr_code_screen.found_user = self.found_user
        self.ids.manager.current = "home" # reload the page to trigger his on_pre_enter event
    
    def on_leave(self, *args):
        self.ids.manager.current = "pin"



class UpdateUserPinView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UpdateUserPinView, self).__init__(**kwargs)
        self.__db = Database()

    def on_enter(self, *args):

        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)
            pin = self.__db.get_user_pin(self.found_user)
            if pin:
                self.ids.user_pin_field.text = str(pin)
            else:
                self.ids.user_pin_field.text = "No PIN set yet"

    def update_pin(self):
        if self.ids.new_pin.ids.password_field.text.strip() and self.ids.confirm_pin.ids.password_field.text.strip():
            try:
                new_pin = int(self.ids.new_pin.ids.password_field.text.strip())
                confirm_pin = int(self.ids.confirm_pin.ids.password_field.text.strip())
                if new_pin == confirm_pin:
                    if len(str(new_pin)) == 6 and len(str(confirm_pin)) == 6:
                        if self.__db.update_user_pin(list(self.found_user), confirm_pin):
                            toast(f"PIN Successfully updated",
                                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
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
                            toast(f"Error occurred when updating PIN, please try again!",
                                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                                  )
                    else:
                        self.ids.error_label.text = "PIN must have 6 digits"
                else:
                    self.ids.error_label.text = "New PIN must be equal to confirmation PIN"
            except ValueError:
                self.ids.error_label.text = "New PIN and Confirmation PIN must be numeric numbers"

        else:
            self.ids.error_label.text = "Please fill required fields"


class GenerateQRCodeView(MDScreen):
    found_user = ObjectProperty()

    def __init__(self, **kwargs):
        super(GenerateQRCodeView, self).__init__(**kwargs)
        self.__db = Database()

    def on_enter(self, *args):

        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)
            qr_path = self.__db.get_user_qr_img_path(self.found_user)
            if qr_path:
                self.ids.image.source = qr_path


    def generate_qr_code(self):
        # Find & delete old path
        qr_path = self.__db.get_user_qr_img_path(self.found_user)
        if qr_path:
            os.remove(qr_path)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        data = "|".join([str(x) for x in self.found_user])
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        length = 10
        characters = string.ascii_letters + string.digits
        random_string = ''
        for i in range(length):
            random_character = choice(characters)
            random_string += random_character

        dir_path = os.path.join(os.getcwd(), ".cache", "qr_codes")
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, random_string+"_qr_code.png")
        print(path)
        img.save(path)
        self.ids.image.source = path
        if self.__db.update_qr_code(self.found_user, path):
            toast(f"QR Code Successfully updated",
                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                  )
        else:
            toast(f"Error occurred when saving generated QR Code, please try again!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )





