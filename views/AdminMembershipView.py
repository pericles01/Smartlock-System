import os
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors


class AdminMembershipView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(AdminMembershipView, self).__init__(**kwargs)

        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path, selector="file", ext=[".csv", ".json"]#,preview=True
        )

        self.userform_dialog = Popup(title="User Form", title_align="center", title_size="20sp", size_hint=(0.8, 0.9),
                            auto_dismiss=False)
        self.userform_content = AddUserForm()

        # will be set later
        self.firstname = None
        self.lastname = None
        self.rfid_code = None
        self.user_description = None


    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        #self.file_manager.show_disks()
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        toast(f"Successfully loaded: {os.path.basename(path)}",
              background=get_color_from_hex(colors["Blue"]["500"]), duration=3
        )

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def _on_dismiss_userform_callback(self, instance):
        # clear
        self.userform_content.ids.firstname_field.text = ""
        self.userform_content.ids.lastname_field.text = ""
        self.userform_content.ids.rfid_field.text = ""
        self.userform_content.ids.description_field.text = ""
        self.userform_content.ids.error_label.text = "* required fields"

    def _verify_input_userform_callback(self, instance):
        if not (self.userform_content.ids.firstname_field.text and self.userform_content.ids.lastname_field.text
                and self.userform_content.ids.rfid_field.text):
            self.userform_content.ids.error_label.text = "Please fill all the required fields"
        else:
            try:
                self.firstname = self.userform_content.ids.firstname_field.text
                self.lastname = self.userform_content.ids.lastname_field.text
                self.rfid_code = int(self.userform_content.ids.rfid_field.text)
                self.user_description = self.userform_content.ids.description_field.text
                toast(f"Successfully added user {self.firstname}, {self.lastname}",
                      background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                )
                self.userform_dialog.dismiss()
            except ValueError:
                self.userform_content.ids.error_label.text = "RFID Code must be an integer"

    def show_userform_dialog(self):
        self.userform_content.ids.save_button.bind(on_press=self._verify_input_userform_callback)
        self.userform_content.ids.exit_button.bind(on_press=self.userform_dialog.dismiss)

        self.userform_dialog.content = self.userform_content
        self.userform_dialog.bind(on_dismiss=self._on_dismiss_userform_callback)
        self.userform_dialog.open()


class AddUserForm(RelativeLayout):
    def __init__(self, **kwargs):
        super(AddUserForm, self).__init__(**kwargs)