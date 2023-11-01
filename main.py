from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty
#from kivy.metrics import dp

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


    def pop(self):

        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.transition.direction = "right"
            self.current = screen_name


class SmartlockApp(MDApp):
    manager = ObjectProperty(None)

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.load_all_kv_files("./views")
        self.manager = NavigationScreenManager()
        return self.manager #Builder.load_file("smartlock.kv")



if __name__ == '__main__':
    SmartlockApp().run()