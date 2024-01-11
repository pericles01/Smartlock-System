import sys
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, BooleanProperty
from manage.SerialHub import SerialHub
from manage.Database import Database
import serial
import  cv2

class NavigationScreenManager(MDScreenManager):
    screen_stack = []

    def push(self, screen_name):

        if screen_name not in self.screen_stack:
            self.screen_stack.append(self.current)
            self.transition.direction = "left"
            self.current = screen_name
        if screen_name == "welcome":
            # empty the screen stack
            self.screen_stack.clear()
            self.current = screen_name
            toast(f"Logged out ...",
                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                  )


    def pop(self):

        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.transition.direction = "right"
            self.current = screen_name


class SmartlockApp(MDApp):
    manager = ObjectProperty(None)
    found_user = ObjectProperty()
    rpi_cam = BooleanProperty()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.load_all_kv_files("./views")
        self.manager = NavigationScreenManager()
        return self.manager

    def on_start(self):
        # test if the serial hub is connected
        hub = SerialHub()

        try:
            _ = hub.send_status_command()
        except (serial.SerialException, ValueError) as e:
            print(e)
            print("Please make sure that the Hub device is connected correctly")
            #print("Exiting...")
            #sys.exit(1)

        # create and configure the database if not existing
        db = Database()
        db.db_init()

        # guess the connected camera typ: webcam or rpi cam
        webcam = cv2.VideoCapture(0)
        if webcam.isOpened():
            result, _ = webcam.read()
            if result:
                print("webcam detected")
                self.rpi_cam = False
        else:
            print("rpi cam detected")
            self.rpi_cam = True
        webcam.release()

        self.root.ids.welcome_view.ids.password_field.ids.password_field.hint_text = "Enter password"

        self.manager.push("welcome")



if __name__ == '__main__':
    SmartlockApp().run()