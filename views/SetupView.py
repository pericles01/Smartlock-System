from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.color_definitions import colors


class SetupView(RelativeLayout):
    dialog = ObjectProperty()
    isSetup = BooleanProperty()
    def __init__(self, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self.dialog = OkDialog()

    def show_ok_dialog(self):
        #self.dialog.open()
        self.ids.locker_number_label.text = '10'
        self.ids.technician_label.text = "Opening all the doors..."

        if not self.ids.start_number_field.text:
            self.dialog.set_text("Start number is required")
            self.dialog.open()
        else:
            try:
                start_number = int(self.ids.start_number_field.text)
                self.ids.technician_label.text = str(start_number)
            except ValueError:
                self.dialog.set_text("Start number must be an integer")
                self.dialog.open()


class OkDialog(MDDialog):
    def __init__(self, **kwargs):
        super(OkDialog, self).__init__(**kwargs)
        self.radius = [dp(6), dp(6), dp(6), dp(6)]
        self.type = "alert"
        self.md_bg_color = "8D6E63" #colors["LightBlue"]["600"]

    def set_text(self, text:str):
        self.text = text