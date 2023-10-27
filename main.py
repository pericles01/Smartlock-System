from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.color_definitions import colors
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, StringProperty
#from kivymd.uix.button import MDFillRoundFlatIconButton
#from kivy.metrics import dp
#from kivy.lang import Builder

class NavigationScreenManager(MDScreenManager):
    screen_stack = []

    def push(self, screen_name):

        if screen_name not in self.screen_stack:
            self.screen_stack.append(self.current)
            self.transition.direction = "left"
            self.current = screen_name

    def pop(self):

        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.transition.direction = "right"
            self.current = screen_name

class LoginOptionButton(MDCard):
    text_option = StringProperty()
    icon_name = StringProperty()
    def __init__(self, **kwargs):
        super(LoginOptionButton, self).__init__(**kwargs)
        self.md_bg_color: colors["LightBlue"]['300']
        self.style = "filled"
        self.line_color = (0.2, 0.2, 0.2, 0.8)




class SmartlockApp(MDApp):
    manager = ObjectProperty(None)

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.manager = NavigationScreenManager()

        return self.manager #Builder.load_file("smartlock.kv")



if __name__ == '__main__':
    SmartlockApp().run()