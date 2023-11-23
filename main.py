import sys
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, NumericProperty
#import cProfile
from manage.SerialHub import SerialHub
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
            #MDApp.get_running_app().user = None # reset or logout the user


    def pop(self):

        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.transition.direction = "right"
            self.current = screen_name


class SmartlockApp(MDApp):
    manager = ObjectProperty(None)
    connected_doors = NumericProperty()
    found_user = ObjectProperty()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.load_all_kv_files("./views")
        self.manager = NavigationScreenManager()
        return self.manager

    def on_start(self):
        #self.profile = cProfile.Profile()
        #self.profile.enable()
        cnt = 0
        hub = SerialHub()

        try:
            door_pos_info = hub.send_status_command()
            for key in door_pos_info.keys():
                if door_pos_info[key] == "closed":
                    cnt +=1
            self.connected_doors = cnt
        except (serial.SerialException, ValueError) as e:
            print(e)
            print("Please make sure that the Hub device is connected correctly")
            #print("Exiting...")
            #sys.exit(1)
            self.connected_doors = 8


    #def on_stop(self):
        #self.profile.disable()
        #self.profile.dump_stats('SmartlockApp.profile')



if __name__ == '__main__':
    SmartlockApp().run()