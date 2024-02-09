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
from manage.SerialHub import SerialHub
from views.GlobalComponents import ConfirmationDialogContent


class AdminMembershipView(MDScreen):
    def __init__(self, **kwargs):
        super(AdminMembershipView, self).__init__(**kwargs)

        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path, selector="file", ext=[".csv", ".json"]
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

        self.urgency_open_dialog = Popup(title="Urgency door open", title_align="center", title_size="20sp",
                                      size_hint=(0.8, 0.5), auto_dismiss=True)
        self.urgency_open_dialog_content = UrgencyDoorOpen()

        # set later in add user form
        self.firstname = None
        self.lastname = None
        self.rfid_code = None
        self.user_description = None
        # set later in add users with file
        self.user_data = None
        self._door_pos = int()
        self._hub = SerialHub()
        self.__time_out = int()
        self._db = Database()

    def on_pre_enter(self, *args):
        """
        automatically update the users preview with the database content by entering the admmin membership view
        :param args:
        :return:
        """
        self._db.db_init(refresh=True)
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
                        "edit_item": self.edit_item_callback,
                        "urgency_open": self.urgency_open_callback
                    }
                )
            self.ids.rv.data = rv_data

    def edit_item_callback(self, instance):
        self.show_user_info_dialog(instance)

    def file_manager_open(self):
        #self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        self.file_manager.show_disks()
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        :param path: path to the selected directory or file;
        '''
        try:
            # ToDo verify that only the given format is loaded
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
                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
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
                        "edit_item": self.edit_item_callback,
                        "urgency_open": self.urgency_open_callback
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
                rfid_code = self.userform_content.ids.rfid_field.text.strip()
                door_number = int(self.userform_content.ids.door_number_field.text.strip())
                user_description = self.userform_content.ids.description_field.text.strip() if self.userform_content.ids.description_field.text.strip() != "" else "No Description"
                toast(f"Successfully added user {firstname}, {lastname}",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
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
                                "edit_item": self.edit_item_callback,
                                "urgency_open": self.urgency_open_callback
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
                self.userform_content.ids.error_label.text = "Door number must be a numeric number"

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
                    rfid_code = self.user_info_content.ids.rfid_field.text.strip()
                    door_number = int(self.user_info_content.ids.door_number_field.text.strip())
                    user_description = self.user_info_content.ids.description_field.text.strip()

                    old_user_infos = [start_info[0][0].strip(), start_info[0][1].strip(), start_info[0][2].strip()]
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
                                    "edit_item": self.edit_item_callback,
                                    "urgency_open": self.urgency_open_callback
                                }
                            )
                        self.ids.rv.data = rv_data
                        toast(f"Successfully edited user {firstname}, {lastname}",
                              background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                              )
                        print(" ")
                        print("--------------")
                        print("Update User test")
                        print("--------------")
                        print(f"Old User Info: {old_user_infos}")
                        print(f"New User Info: {new_user_info}")
                        print(f"Table content length: {len(self.user_data)}")
                        print("Content:")
                        print(f"{self.user_data}")
                        self.user_info_dialog.dismiss()
                    else:
                        toast(f"Error while updating, please try again",
                              background=get_color_from_hex(colors["Red"]["500"]), duration=3
                              )

                except ValueError as e:
                    self.user_info_content.ids.error_label.text = "Door number must be a numeric number"
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
        user_info = (instance.text.split('|'), instance.description)

        user2delete = (user_info[0][0].strip(), user_info[0][1].strip(), user_info[0][2].strip())
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
                        "edit_item": self.edit_item_callback,
                        "urgency_open": self.urgency_open_callback
                    }
                )
            self.ids.rv.data = rv_data
            toast(f"Successfully deleted user {user_info[0][0]}, {user_info[0][1]}",
                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                  )
            print(" ")
            print("--------------")
            print("Delete User test")
            print("--------------")
            print(f"User to delete: {user2delete}")
            print(f"Table content length: {len(self.user_data)}")
            print("Content:")
            print(f"{self.user_data}")
            self.delete_confirmation_dialog.dismiss()
        else:
            toast(f"Error while deleting, {user_info[0][0]}, {user_info[0][1]} please try again",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=3
                  )


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


    def _urgency_dialog_dismiss_callback(self, instance):
        self.urgency_open_dialog_content.ids.urgency_card_field.text = ""
        self.urgency_open_dialog_content.ids.urgency_card_field.focus = False
        self._door_pos = 0

    def _verify_uid_code(self, instance):

        # activate the serial reader and get the uid
        urgency_uid = self.urgency_open_dialog_content.ids.urgency_card_field.text.strip()
        db_urgency_uid = self._db.show_admin_table()[2]
        if urgency_uid == db_urgency_uid[2]:
            if self._hub.send_open_command(self._door_pos):
                self.urgency_open_dialog.dismiss()
                toast(f"Successfully opened user door!!",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=5
                      )
        else:
            self.urgency_open_dialog.dismiss()
            toast(f"Wrong Urgency card detected, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )


    def urgency_open_callback(self, instance):
        text = instance.text.split("|")
        door_number = int(text[3].strip())

        path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
        with open(path, "r") as f:
            door_pos_mapping = json.load(f)
            self._door_pos = int(door_pos_mapping[str(door_number)])

        print(f"User Door Number: {door_number}, door position: {self._door_pos}")

        self.urgency_open_dialog_content.ids.user_info_label.text = "User: " + text[0] + ", " + text[1]
        self.urgency_open_dialog_content.ids.urgency_card_field.bind(on_text_validate=self._verify_uid_code)
        self.urgency_open_dialog_content.ids.urgency_card_field.focus = True
        self.urgency_open_dialog.content = self.urgency_open_dialog_content
        self.urgency_open_dialog.bind(on_dismiss=self._urgency_dialog_dismiss_callback)
        self.urgency_open_dialog.open()



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
    urgency_open = ObjectProperty()


class UrgencyDoorOpen(RelativeLayout):
    def __init__(self, **kwargs):
        super(UrgencyDoorOpen, self).__init__(**kwargs)

class UpdateCredentialView(MDScreen):
    def __init__(self, **kwargs):
        super(UpdateCredentialView, self).__init__(**kwargs)
        self._db = Database()

    def update_credentials(self):

        if self.ids.new_username_field.text.strip() and self.ids.new_password_widget.ids.password_field.text.strip() \
            and self.ids.new_password_widget_confirmation.ids.password_field.text.strip():

            if self.ids.new_password_widget.ids.password_field.text.strip() == self.ids.new_password_widget_confirmation.ids.password_field.text.strip():
                # get old admin credentials
                self._db.db_init(refresh=True)
                old_admin_credentials = self._db.show_admin_table()[0]
                print(f"Old Credentials: {old_admin_credentials}")
                new_admin_credentials = [self.ids.new_username_field.text.strip(), self.ids.new_password_widget_confirmation.ids.password_field.text.strip()]
                if self._db.update_user_admin_credentials(new_admin_credentials, old_admin_credentials):
                    toast(f"Successfully updated admin credentials",
                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                          )
                    self.reset()
                    print("----------------")
                    print("Test Update")
                    print(f"New Credentials: {self._db.show_admin_table()[0]}")
            else:
                self.ids.error_label.text = "New password must be equal to confirmation password"
        else:
            self.ids.error_label.text = "Please fill all required fields"

    def reset(self):
        self.ids.error_label.text = '* required fields'
        self.ids.new_username_field.text = ""
        self.ids.new_password_widget.ids.password_field.text = ""
        self.ids.new_password_widget_confirmation.ids.password_field.text = ""

    def on_leave(self, *args):
        self.reset()






