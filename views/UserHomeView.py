from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
import os
import json
from manage.SerialHub import SerialHub
import serial


class UserHomeView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserHomeView, self).__init__(**kwargs)
        self.__hub = SerialHub()
        self.door_pos = int()
        self.status = ""


    def open_user_door(self):

        try:

            if self.status == "open":
                toast(f"Door is already open",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                      )
            else:
                if self.__hub.send_open_command(self.door_pos):
                    # ToDo buffer peep
                    # make sure the status changed
                    doors_status = self.__hub.send_status_command()
                    status = doors_status[str(self.door_pos)]

                    if status == self.status:
                        toast(f"Could not open the door, check for any mechanical problem and try again",
                            background=get_color_from_hex(colors["Red"]["500"]), duration=3
                            )
                    else:
                        self.ids.user_door_status.text = status
                        toast(f"Door opened",
                            background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                            )
                

        except (serial.SerialException, ValueError) as e:
            toast("Could not open the door. Please make sure that the Hub device is connected correctly and try again",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )

    def on_pre_enter(self, *args):
        if self.found_user:
            # retrieve door position
            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
            door_number = self.found_user[2]
            with open(path, "r") as f:
                door_pos_mapping = json.load(f)
                self.door_pos = int(door_pos_mapping[str(door_number)])
                print(f"User door number: {door_number}, mapping position: {self.door_pos}")
            # retrieve door position status
            try:
                doors_status = self.__hub.send_status_command()
                self.status = doors_status[str(self.door_pos)]
                self.ids.user_door_status.text = self.status

            except (serial.SerialException, ValueError) as e:
                self.ids.user_door_status.text = "No Door Connected"

    def on_leave(self, *args):
        self.door_pos = int()
        self.status = ""

