from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from manage.Database import Database
from views.GlobalComponents import ConfirmationDialogContent

class TechnicianMembershipView(MDScreen):
    def __init__(self, **kwargs):
        super(TechnicianMembershipView, self).__init__(**kwargs)


    def on_pre_enter(self, *args):
        self.ids.manager.current = "setup"

class UpdateEmergencyUIDView(MDScreen):
    def __init__(self, **kwargs):
        super(UpdateEmergencyUIDView, self).__init__(**kwargs)
        self._db = Database()
        self.update_confirmation_dialog = Popup(title="Update confirmation", title_align="center", title_size="20sp",
                                                size_hint=(0.6, 0.4), auto_dismiss=False)
        self.update_confirmation_dialog_content = ConfirmationDialogContent()
        

    def on_pre_enter(self, *args):
        self.ids.emergency_uid_field.focus = True
        self._db.db_init(refresh=True)

    def on_leave(self, *args):
        self.ids.emergency_uid_field.focus = False
        self.ids.emergency_uid_field.text = ""

    def update_emergency_uid(self, instance):
        new_uid = self.ids.emergency_uid_field.text.strip()
        if new_uid:
            if self._db.update_urgency_uid(new_uid):
                toast(f"Successfully updated new emergency uid",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=1
                      )
                print(self._db.show_admin_table())
            else:
                toast(f"Emergency uid update failed, please try again!",
                      background=get_color_from_hex(colors["Red"]["500"]), duration=1
                      )
        else:
            toast(f"Please scan the new emergency uid and try again!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=1
                  )

        self.ids.emergency_uid_field.text = ""
        self.update_confirmation_dialog.dismiss()

    def show_update_confirmation_dialog(self):
        self.update_confirmation_dialog_content.ids.label.text = "Do you want to update the emergency UID?"
        self.update_confirmation_dialog_content.ids.label.theme_text_color = "Error"
        self.update_confirmation_dialog_content.ids.yes_button.bind(on_release=self.update_emergency_uid)
        self.update_confirmation_dialog_content.ids.no_button.bind(on_release=self.update_confirmation_dialog.dismiss)
        self.update_confirmation_dialog.content = self.update_confirmation_dialog_content
        self.update_confirmation_dialog.bind(on_dismiss=self.confirmation_dialog_dismiss_callback)
        self.update_confirmation_dialog.open()

    def _refresh_update_screen(self, *args):
        self.ids.emergency_uid_field.focus = True
    def confirmation_dialog_dismiss_callback(self, instance):
        Clock.schedule_once(self._refresh_update_screen, 2)
