from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class UserMembershipView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserMembershipView, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.found_user = MDApp.get_running_app().found_user
        print(f"Welcome {self.found_user[0]}, {self.found_user[1]} !")
        self.ids.topbar.title = f"Welcome {self.found_user[0]}, {self.found_user[1]} !"
        self.ids.user_welcome_screen.found_user = self.found_user
        self.ids.manager.current = "home" # reload the page to trigger his on_pre_enter event


