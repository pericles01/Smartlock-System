import os
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import pandas as pd
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.toast import toast
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
import json


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

        self.user_info_dialog = Popup(title="User's informations", title_align="center", title_size="20sp",
                                      size_hint=(0.8, 0.9), auto_dismiss=False)
        self.user_info_content = UserInfoForm()
        # set later in add user form
        self.firstname = None
        self.lastname = None
        self.rfid_code = None
        self.user_description = None
        # set later in add users with file
        self.user_data = None

    def remove_item_callback(self, instance):
        self.ids.md_list.remove_widget(instance)
        user_info = instance.text.split('|')
        toast(f"Successfully deleted user {user_info[0]}, {user_info[1]}",
              background=get_color_from_hex(colors["Blue"]["500"]), duration=3
              )
        # ToDo remove it from the database

    def edit_item_callback(self, instance):
        self.show_user_info_dialog(instance)

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        #self.file_manager.show_disks()
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        :param path: path to the selected directory or file;
        '''
        try:
            usecols = ["firstname", "lastname", "rfid", "door number", "description"]
            df = pd.read_csv(path, usecols=usecols)
            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
            with open(path, "r") as f:
                door_data = json.load(f)
            # verify that the number of users matches with the number of set up doors
            assert len(door_data) == len(df.to_numpy())
            df.sort_values(by=['firstname'], ascending=True, inplace=True)
            self.user_data = df.to_numpy()
            toast(f"Successfully loaded: {os.path.basename(path)}",
                  background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                  )
            for user in self.user_data:
                self.ids.md_list.add_widget(
                    SwipeToEditItem(text=f"{user[0]} | {user[1]} | {user[2]}",
                                    description=f"{user[4] if str(user[4]) != 'nan' else 'No description'}",
                                    remove_item=self.remove_item_callback, edit_item=self.edit_item_callback)
                    )
            # ToDo Save user_data into database

        except Exception:
            toast(f"Failed to load: {os.path.basename(path)}. Please load a file with the preferred format",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )

        self.exit_manager()

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

    def _on_dismiss_user_info_callback(self, instance):
        pass

    def _verify_input_userform_callback(self, instance):
        if not (self.userform_content.ids.firstname_field.text.strip() and self.userform_content.ids.lastname_field.text.strip()
                and self.userform_content.ids.rfid_field.text.strip()):
            self.userform_content.ids.error_label.text = "Please fill all the required fields"
        else:
            try:
                firstname = self.userform_content.ids.firstname_field.text.strip()
                lastname = self.userform_content.ids.lastname_field.text.strip()
                rfid_code = int(self.userform_content.ids.rfid_field.text.strip())
                user_description = self.userform_content.ids.description_field.text.strip()
                toast(f"Successfully added user {firstname}, {lastname}",
                      background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                )
                # ToDo Save it into database
                self.userform_dialog.dismiss()
            except ValueError:
                self.userform_content.ids.error_label.text = "RFID Code must be an integer"

    def _verify_input_user_info_callback(self, instance):
        if not (self.user_info_content.ids.firstname_field.text.strip() and self.user_info_content.ids.lastname_field.text.strip()
                and self.user_info_content.ids.rfid_field.text.strip()):
            self.user_info_content.ids.error_label.text = "Please fill all the required fields"
        else:
            start_info = (self.user_info_content.swipe_instance.text.split('|'),
                          self.user_info_content.swipe_instance.description)
            if (self.user_info_content.ids.firstname_field.text.strip() != start_info[0][0].strip() or
                self.user_info_content.ids.lastname_field.text.strip() != start_info[0][1].strip() or
                self.user_info_content.ids.rfid_field.text.strip() != start_info[0][2].strip() or
                self.user_info_content.ids.description_field.text.strip() != start_info[1].strip()):
                try:
                    firstname = self.user_info_content.ids.firstname_field.text.strip()
                    lastname = self.user_info_content.ids.lastname_field.text.strip()
                    rfid_code = int(self.user_info_content.ids.rfid_field.text.strip())
                    user_description = self.user_info_content.ids.description_field.text.strip()
                    toast(f"Successfully edited user {firstname}, {lastname}",
                          background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                    )
                    # ToDo Save it into database
                    self.user_info_dialog.dismiss()
                except ValueError:
                    self.user_info_content.ids.error_label.text = "RFID Code must be an integer"
            else:
                self.user_info_content.ids.error_label.text = "No changes in user's informations"

    def show_userform_dialog(self):
        self.userform_content.ids.save_button.bind(on_press=self._verify_input_userform_callback)
        self.userform_content.ids.exit_button.bind(on_press=self.userform_dialog.dismiss)

        self.userform_dialog.content = self.userform_content
        self.userform_dialog.bind(on_dismiss=self._on_dismiss_userform_callback)
        self.userform_dialog.open()

    def show_user_info_dialog(self, instance):
        """
        :param instance: SwipeToEditItem
        :return: None
        This method retrieve the user's infos from instance object and show the in the popup content
        """
        user_info = instance.text.split('|')
        self.user_info_content.ids.firstname_field.text = user_info[0].strip()
        self.user_info_content.ids.lastname_field.text = user_info[1].strip()
        self.user_info_content.ids.rfid_field.text = user_info[2].strip()
        self.user_info_content.ids.description_field.text = instance.description.strip()
        self.user_info_content.swipe_instance = instance

        self.user_info_content.ids.save_button.bind(on_press=self._verify_input_user_info_callback)
        self.user_info_content.ids.exit_button.bind(on_press=self.user_info_dialog.dismiss)

        self.user_info_dialog.content = self.user_info_content
        self.user_info_dialog.bind(on_dismiss=self._on_dismiss_user_info_callback)
        self.user_info_dialog.open()


class AddUserForm(RelativeLayout):
    def __init__(self, **kwargs):
        super(AddUserForm, self).__init__(**kwargs)

class UserInfoForm(RelativeLayout):
    swipe_instance = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserInfoForm, self).__init__(**kwargs)


class SwipeToEditItem(MDCardSwipe):
    '''Card with `swipe-to-edit` behavior.'''

    text = StringProperty()
    description = StringProperty()
    remove_item = ObjectProperty()
    edit_item = ObjectProperty()
    edited = BooleanProperty()