from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.relativelayout import MDRelativeLayout
import os


class LoginAdminCard(MDCard):
    monkey_hello = StringProperty()
    monkey_hided_eyes = StringProperty()
    monkey_closed_mouth = StringProperty()
    def __init__(self, **kwargs):
        super(LoginAdminCard, self).__init__(**kwargs)
        self.monkey_hello = os.path.normpath("./ressources/monkeywillkommen1.png")
        self.monkey_hided_eyes = os.path.normpath("../ressources/monkeyhidedeyes.png")
        self.monkey_closed_mouth = os.path.normpath("../ressources/monkeymouthclosed.png")


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
