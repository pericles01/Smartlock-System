from kivy.properties import  StringProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from manage.SerialHub import SerialHub
import serial
from functools import partial
from manage.Database import Database
from kivymd.app import MDApp
import json
import os

class LoginOptionCard(MDCard):
    text_option = StringProperty()
    icon_name = StringProperty()
    press_callback = ObjectProperty()
    def __init__(self, **kwargs):
        super(LoginOptionCard, self).__init__(**kwargs)
        self.shadow_offset = (0, 1)


class WelcomeScreen(MDFloatLayout):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)

        self.pin_dialog = Popup(title="Login with PIN", title_align="center", title_size="20sp", size_hint=(0.6, 0.5),
                                     auto_dismiss=False)
        self.pin_dialog_content = PinDialogContent()
        self.membership_confirmation = Popup(title="Membership confirmation", title_align="center", title_size="20sp",
                                      size_hint=(0.6, 0.4), auto_dismiss=False)
        self.membership_confirmation_content = MembershipConfirmationContent()
        self.found_user = None

    def pin_dialog_dismiss_callback(self, instance):
        # clear / reset
        self.pin_dialog_content.ids.user_pin_login.ids.password_field.text = ""
        self.pin_dialog_content.ids.error_label.text = "* required field"

    def show_dialog(self, instance: str):
        if instance.text_option == "Login with PIN":
            self.pin_dialog_content.ids.login_button.bind(on_press=self._verify_input_pin)
            self.pin_dialog_content.ids.user_pin_login.ids.password_field.bind(on_text_validate=self._verify_input_pin)
            self.pin_dialog_content.ids.exit_button.bind(on_press=self.pin_dialog.dismiss)
            self.pin_dialog.content = self.pin_dialog_content
            self.pin_dialog.bind(on_dismiss=self.pin_dialog_dismiss_callback)
            self.pin_dialog.open()

        elif instance.text_option == "Login with RFID":
            print(f"{str(instance.icon_name)}")
            print("------------")
        elif instance.text_option == "Login with QR Code":
            print(f"{str(instance.icon_name)}")
            print("------------")
        else:
            print(f"{str(instance.icon_name)}")
            print("------------")

    def _on_membership_confirmation_dismiss(self, instance):
        # reset
        self.found_user = None
        print("User reset")

    def _open_door_callback(self, door_number:int, *args):
        hub = SerialHub()
        try:
            # retrieve door position
            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
            with open(path, "r") as f:
                door_pos_mapping = json.load(f)
                door_pos = int(door_pos_mapping[str(door_number)])
                print(f"User door number: {door_number}, mapping position: {door_pos}")
            # retrieve door position status
            doors_status = hub.send_status_command()
            status = doors_status[str(door_pos)]
            if status == "open":
                toast(f"Door is already open",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                )
            else:
                if hub.send_open_command(door_pos):
                    # ToDo buffer peep
                    toast(f"Door opened",
                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                    )
                # make sure the status changed
                if doors_status == hub.send_status_command():
                    toast(f"Could not open the door, try again",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=3
                          )

        except (serial.SerialException, ValueError) as e:
            toast("Could not open the door. Please make sure that the Hub device is connected correctly and try again",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )

        self.membership_confirmation.dismiss()

    def go_to_membership_callback(self, manager, *args):
        MDApp.get_running_app().found_user = self.found_user
        self.membership_confirmation.dismiss()
        manager.push("user_membership")
        # change screen
        toast(f"Successfully login into your membership",
              background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
              )


    def show_go_to_membership_dialog(self):

        self.membership_confirmation_content.ids.label.text = "Do you want to go to your user membership?"
        self.membership_confirmation_content.go2membership = self.go_to_membership_callback # go to membership when the yes button is triggered
        # retrive door_number
        door_number = self.found_user[2]
        # when the no button is triggered, then open directly the user's door
        self.membership_confirmation_content.ids.no_button.bind(
            on_press=partial(self._open_door_callback, door_number)
        )
        self.membership_confirmation.content = self.membership_confirmation_content
        self.membership_confirmation.bind(on_dismiss=self._on_membership_confirmation_dismiss)
        self.membership_confirmation.open()

    def _verify_input_pin(self, instance):
        if self.pin_dialog_content.ids.user_pin_login.ids.password_field.text.strip():
            try:
                pin = int(self.pin_dialog_content.ids.user_pin_login.ids.password_field.text.strip())
                # search PIN in the database
                db = Database()
                db.db_init(refresh=True)
                # user = db.get_user_by_pin(pin)
                user = db.get_user_by_rfid(pin)
                if user:
                    self.found_user = user
                    # If found show dialog
                    self.pin_dialog.dismiss()
                    self.show_go_to_membership_dialog()
                else:
                    self.pin_dialog_content.ids.error_label.text = "User not found, please verify your PIN input"
            except ValueError as e:
                self.pin_dialog_content.ids.error_label.text = "PIN must be a numeric number"
        else:
            self.pin_dialog_content.ids.error_label.text = "Please enter your numeric PIN"

class PinDialogContent(RelativeLayout):
    def __init__(self, **kwargs):
        super(PinDialogContent, self).__init__(**kwargs)

class MembershipConfirmationContent(RelativeLayout):
    go2membership = ObjectProperty()
    def __init__(self, **kwargs):
        super(MembershipConfirmationContent, self).__init__(**kwargs)