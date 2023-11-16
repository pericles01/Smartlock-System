from kivy.properties import  StringProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout


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

    def show_dialog(self, instance: str):
        if instance.text_option == "Login with PIN":
            self.pin_dialog_content.ids.exit_button.bind(on_press=self.pin_dialog.dismiss)
            self.pin_dialog.content = self.pin_dialog_content
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

class PinDialogContent(RelativeLayout):
    def __init__(self, **kwargs):
        super(PinDialogContent, self).__init__(**kwargs)