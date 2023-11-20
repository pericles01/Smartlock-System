from kivy.properties import ObjectProperty
from kivymd.uix.floatlayout import MDFloatLayout


class UserMembershipView(MDFloatLayout):
    user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserMembershipView, self).__init__(**kwargs)


