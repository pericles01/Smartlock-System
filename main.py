import sys
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty
from manage.SerialHub import SerialHub
from manage.Database import Database
import serial

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

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.load_all_kv_files("./views")
        self.manager = NavigationScreenManager()
        return self.manager

    def on_start(self):
        hub = SerialHub()

        try:
            _ = hub.send_status_command()
        except (serial.SerialException, ValueError) as e:
            print(e)
            print("Please make sure that the Hub device is connected correctly")
            #print("Exiting...")
            #sys.exit(1)

        db = Database()
        db.db_init()

        self.root.ids.welcome_view.ids.pin_field.ids.password_field.hint_text = "Enter your PIN"
        for i in range(1, 10):
            btn = Button(text=f"{i}")
            btn.bind(on_release=self.root.ids.welcome_view.on_release_num_btn_callback)
            self.root.ids.welcome_view.ids.numpad.add_widget(btn)

        zero_btn = Button(text=str(0))
        zero_btn.bind(on_release=self.root.ids.welcome_view.on_release_num_btn_callback)
        self.root.ids.welcome_view.ids.numpad.add_widget(zero_btn)

        del_btn = Button(text="Del")
        del_btn.bind(on_release=self.root.ids.welcome_view.on_release_del_btn_callback)
        self.root.ids.welcome_view.ids.numpad.add_widget(del_btn)

        #self.root.ids.welcome_view.ids.pin_field.ids.password_field.bind(focus=self.root.ids.welcome_view.on_focus)
        self.manager.push("welcome")



if __name__ == '__main__':
    SmartlockApp().run()