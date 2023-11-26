import os
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import pandas as pd
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.toast import toast
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.filemanager import MDFileManager
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
import json
from functools import partial

from kivymd.uix.screen import MDScreen

from manage.Database import Database
from views.GlobalComponents import ConfirmationDialogContent


class AdminMembershipView(MDScreen):
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

        self.delete_confirmation_dialog = Popup(title="Delete confirmation", title_align="center", title_size="20sp",
                                      size_hint=(0.6, 0.4), auto_dismiss=False)
        self.delete_confirmation_dialog_content = ConfirmationDialogContent()

        # set later in add user form
        self.firstname = None
        self.lastname = None
        self.rfid_code = None
        self.user_description = None
        # set later in add users with file
        self.user_data = None
        self._db = Database()
        self._db.db_init()

    def on_pre_enter(self, *args):
        """
        automatically update the users preview with the database content by entering the admmin membership view
        :param args:
        :return:
        """
        db_content = self._db.show_users_table()
        if db_content:
            self.user_data = db_content
            rv_data = list()
            for user in self.user_data:
                rv_data.append(
                    {
                        "text": f"{user[0]} | {user[1]} | {user[2]} | {user[3]}",
                        "description": f"{user[4]}",
                        "remove_item_confirmation": self.show_delete_confirmation_dialog,
                        "edit_item": self.edit_item_callback
                    }
                )
            self.ids.rv.data = rv_data


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
            self.user_data = df.to_numpy().tolist()
            toast(f"Successfully loaded: {os.path.basename(path)}",
                  background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                  )
            for user in self.user_data:
                user[4] = user[4] if str(user[4]) != 'nan' else 'No Description'

        except ValueError:
            toast(f"Failed to load: {os.path.basename(path)}. Please load a file with the preferred format",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )

        if self._db.add_users(self.user_data):
            self.user_data = self._db.show_users_table()
            rv_data = list()
            for user in self.user_data:
                rv_data.append(
                    {
                        "text": f"{user[0]} | {user[1]} | {user[2]} | {user[3]}",
                        "description": f"{user[4]}",
                        "remove_item_confirmation": self.show_delete_confirmation_dialog,
                        "edit_item": self.edit_item_callback
                    }
                )
            self.ids.rv.data = rv_data
            self.exit_manager()
            print(" ")
            print("--------------")
            print("Add User test")
            print("--------------")
            print(f"Table content length: {len(self.user_data)}")
            print("Content:")
            print(f"{self.user_data}")

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
                and self.userform_content.ids.rfid_field.text.strip() and self.userform_content.ids.door_number_field.text.strip()):
            self.userform_content.ids.error_label.text = "Please fill all the required fields"
        else:
            try:
                firstname = self.userform_content.ids.firstname_field.text.strip()
                lastname = self.userform_content.ids.lastname_field.text.strip()
                rfid_code = int(self.userform_content.ids.rfid_field.text.strip())
                door_number = int(self.userform_content.ids.door_number_field.text.strip())
                user_description = self.userform_content.ids.description_field.text.strip() if self.userform_content.ids.description_field.text.strip() != "" else "No Description"
                toast(f"Successfully added user {firstname}, {lastname}",
                      background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                )
                self._db.db_init(refresh=True)
                if self._db.add_users([(firstname, lastname, rfid_code, door_number, user_description)]):
                    self.user_data = self._db.show_users_table()
                    rv_data = list()
                    for user in self.user_data:
                        rv_data.append(
                            {
                                "text": f"{user[0]} | {user[1]} | {user[2]} | {user[3]}",
                                "description": f"{user[4]}",
                                "remove_item_confirmation": self.show_delete_confirmation_dialog,
                                "edit_item": self.edit_item_callback
                            }
                        )
                    self.ids.rv.data = rv_data
                    print(" ")
                    print("--------------")
                    print("Add User test")
                    print("--------------")
                    print(f"Table content length: {len(self.user_data)}")
                    print("Content:")
                    print(f"{self.user_data}")
                    self.userform_dialog.dismiss()
            except ValueError:
                self.userform_content.ids.error_label.text = "RFID Code and door number must be a numeric number"

    def _verify_input_user_info_callback(self, instance):
        if not (self.user_info_content.ids.firstname_field.text.strip() and self.user_info_content.ids.lastname_field.text.strip()
                and self.user_info_content.ids.rfid_field.text.strip() and self.user_info_content.ids.door_number_field.text.strip()):
            self.user_info_content.ids.error_label.text = "Please fill all the required fields"
        else:
            start_info = (self.user_info_content.swipe_instance.text.split('|'),
                          self.user_info_content.swipe_instance.description)
            # if there are modifications
            if (self.user_info_content.ids.firstname_field.text.strip() != start_info[0][0].strip() or
                self.user_info_content.ids.lastname_field.text.strip() != start_info[0][1].strip() or
                self.user_info_content.ids.rfid_field.text.strip() != start_info[0][2].strip() or
                self.user_info_content.ids.door_number_field.text.strip() != start_info[0][3].strip() or
                self.user_info_content.ids.description_field.text.strip() != start_info[1].strip()):
                try:
                    firstname = self.user_info_content.ids.firstname_field.text.strip()
                    lastname = self.user_info_content.ids.lastname_field.text.strip()
                    rfid_code = int(self.user_info_content.ids.rfid_field.text.strip())
                    door_number = int(self.user_info_content.ids.door_number_field.text.strip())
                    user_description = self.user_info_content.ids.description_field.text.strip()
                    toast(f"Successfully edited user {firstname}, {lastname}",
                          background=get_color_from_hex(colors["Blue"]["500"]), duration=3
                    )

                    old_user_infos = [start_info[0][0].strip(), start_info[0][1].strip(), int(start_info[0][2].strip())]
                    new_user_info = [firstname, lastname, rfid_code, door_number, user_description]
                    self._db.db_init(refresh=True)
                    if self._db.update_user_basic_infos(old_user_infos, new_user_info):
                        self.user_data = self._db.show_users_table()
                        rv_data = list()
                        for user in self.user_data:
                            rv_data.append(
                                {
                                    "text": f"{user[0]} | {user[1]} | {user[2]} | {user[3]}",
                                    "description": f"{user[4]}",
                                    "remove_item_confirmation": self.show_delete_confirmation_dialog,
                                    "edit_item": self.edit_item_callback
                                }
                            )
                        self.ids.rv.data = rv_data
                        print(" ")
                        print("--------------")
                        print("Update User test")
                        print("--------------")
                        print(f"Old User Info: {old_user_infos}")
                        print(f"New User Info: {new_user_info}")
                        print(f"Table content length: {len(self.user_data)}")
                        print("Content:")
                        print(f"{self.user_data}")
                        # ToDo Update Swipe View
                        self.user_info_dialog.dismiss()

                except ValueError:
                    self.user_info_content.ids.error_label.text = "RFID Code and door number must be a numeric number"
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
        self.user_info_content.ids.door_number_field.text = user_info[3].strip()
        self.user_info_content.ids.description_field.text = instance.description.strip()
        self.user_info_content.swipe_instance = instance

        self.user_info_content.ids.save_button.bind(on_press=self._verify_input_user_info_callback)
        self.user_info_content.ids.exit_button.bind(on_press=self.user_info_dialog.dismiss)

        self.user_info_dialog.content = self.user_info_content
        self.user_info_dialog.bind(on_dismiss=self._on_dismiss_user_info_callback)
        self.user_info_dialog.open()


    def remove_item_callback(self, instance, *args):
        #self.ids.md_list.remove_widget(instance)
        user_info = (instance.text.split('|'), instance.description)
        toast(f"Successfully deleted user {user_info[0][0]}, {user_info[0][1]}",
              background=get_color_from_hex(colors["Blue"]["500"]), duration=3
              )
        user2delete = (user_info[0][0].strip(), user_info[0][1].strip(), int(user_info[0][2].strip()))
        self._db.db_init(refresh=True)
        if self._db.delete_user(user2delete):
            # auto update the view
            self.user_data = self._db.show_users_table()
            rv_data = list()
            for user in self.user_data:
                rv_data.append(
                    {
                        "text": f"{user[0]} | {user[1]} | {user[2]} | {user[3]}",
                        "description": f"{user[4]}",
                        "remove_item_confirmation": self.show_delete_confirmation_dialog,
                        "edit_item": self.edit_item_callback
                    }
                )
            self.ids.rv.data = rv_data
            print(" ")
            print("--------------")
            print("Delete User test")
            print("--------------")
            print(f"User to delete: {user2delete}")
            print(f"Table content length: {len(self.user_data)}")
            print("Content:")
            print(f"{self.user_data}")
            self.delete_confirmation_dialog.dismiss()


    def show_delete_confirmation_dialog(self, instance):

        self.delete_confirmation_dialog_content.ids.label.text = "Do you want to delete this user?"
        self.delete_confirmation_dialog_content.ids.yes_button.bind(
            on_press=partial(self.remove_item_callback, instance)
        )
        self.delete_confirmation_dialog_content.ids.no_button.bind(
            on_press=self.delete_confirmation_dialog.dismiss
        )
        self.delete_confirmation_dialog.content = self.delete_confirmation_dialog_content
        self.delete_confirmation_dialog.open()


class AddUserForm(RelativeLayout):
    def __init__(self, **kwargs):
        super(AddUserForm, self).__init__(**kwargs)

class UserInfoForm(RelativeLayout):
    swipe_instance = ObjectProperty() # used to verify modifications in user info form
    def __init__(self, **kwargs):
        super(UserInfoForm, self).__init__(**kwargs)


class SwipeToEditItem(MDCardSwipe):
    '''Card with `swipe-to-edit` behavior.'''

    text = StringProperty()
    description = StringProperty()
    remove_item_confirmation = ObjectProperty()
    edit_item = ObjectProperty()
    edited = BooleanProperty()