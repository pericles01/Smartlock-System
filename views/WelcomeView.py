from kivy.properties import  StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.color_definitions import colors
from kivy.lang import Builder

Builder.load_file("views/WelcomeView.kv")

class AdminLoginButton(MDFillRoundFlatIconButton):
    def __init__(self, **kwargs):
        super(AdminLoginButton, self).__init__(**kwargs)

    def login(self, widget): print(widget.text)


class LoginOptionCard(MDCard):
    text_option = StringProperty()
    icon_name = StringProperty()
    def __init__(self, **kwargs):
        super(LoginOptionCard, self).__init__(**kwargs)
        self.style = "filled" #"outlined"
        self.line_color = (0.2, 0.2, 0.2, 0.8)
        self.shadow_offset = (0, -1)
    def show_func(self, name:str):
        print(f"{name}")
        print("------------")