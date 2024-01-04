from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivy.uix.popup import Popup
import json
from manage.SerialHub import SerialHub
import os
from kivy.clock import Clock
from functools import partial
import serial
from gpiozero import Buzzer

class SetupView(MDScreen):
    isSetup = BooleanProperty()
    start_number = 0
    is_dialog_dismissed = False
    def __init__(self, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self.dialog = Popup(title="Alert", title_align="center", title_size="20sp", size_hint=(0.5, 0.3),
                            auto_dismiss=False)
        # will come in handy later
        self._skip_door_pos = list()
        self._cnt = int()
        self._door_info_pos = dict()
        self._num2pos = dict()
        self._number_connected_door = int()
        self._is_all_doors_opened = False
        self._door_position = 1
        self._hub = SerialHub()
        self._buzzer = Buzzer(18)

    def on_pre_enter(self, *args):
        try:
            cnt = 0
            door_infos = self._hub.send_status_command()
            for k in door_infos.keys():
                if door_infos[k] == "closed": # if there is still a door closed
                    cnt += 1
            self.ids.locker_number_label.text = str(cnt)

        except serial.SerialException as e:
            self.ids.locker_number_label.text = "0"


    def _on_dismiss_callback(self, instance):
        print("dialog dismissed")
        self.is_dialog_dismissed = True

    def _open_alert_dialog(self, text):
        content = OkDialogContent()
        content.ids.text_label.text = text
        content.ids.ok_button.bind(on_press=self.dialog.dismiss)

        self.dialog.content = content
        self.dialog.bind(on_dismiss=self._on_dismiss_callback)
        self.is_dialog_dismissed = False # reset
        self.dialog.open()


    def _setup(self, _hub, *args):

        door_number = str(self.start_number + self._cnt)
        self.ids.technician_label.text ="Please close door number: " + door_number
        self._buzzer.off()

        if self._door_info_pos != _hub.send_status_command(): # by status change
            # door closed
            self._door_info_pos = _hub.send_status_command() # retrieve current status & update
            # guess the position of the closed door & map the door number to the guessed position
            for k in self._door_info_pos.keys():
                if self._door_info_pos[k] == "closed":
                    if k not in self._skip_door_pos:
                        self._num2pos[door_number] = int(k)
                        self._skip_door_pos.append(k)
                        self._cnt += 1
                        self._buzzer.on()
                            
                        if self._cnt == self._number_connected_door:
                            # save the mapping dict for future use
                            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
                            with open(path, mode='w') as f:
                                json.dump(self._num2pos, f, indent=2)
                            
                            self.ids.technician_label.text ="Setup finished"
                            self._open_alert_dialog(text = "Setup finished")
                            self.ids.start_number_field.text = ""
                            self._buzzer.off()
                            return False
                        

    def _open_door_clock(self, *args):
        try:
            hub = SerialHub()
            self.ids.technician_label.text = "Opening all doors..."
            if hub.send_open_command(self._door_position):
                self._door_position += 1

            if self._door_position == 17:
                cnt = 0
                doors_info = self._hub.send_status_command()
                for k in doors_info.keys():
                    if doors_info[k] == "closed": # if there is still a door closed
                        cnt += 1
                if not cnt:
                    self._is_all_doors_opened = True
                    self._open_alert_dialog(text = "All doors are open")
                    self.ids.technician_label.text = "All doors are open. The setup can now begin!"
                else:
                    self._open_alert_dialog(text = "All doors are not open. Please check for any mechanic problem on closed doors and rebegin!")

                self._door_position = 1
                return False # stop clock
            
        except serial.SerialException as e:
            self._open_alert_dialog(text= "No Hub detected!! Please verify if the hub is connected")
            return False  # stop clock

    def open_all_doors(self):
        if int(self.ids.locker_number_label.text.strip()) > 0:
            Clock.schedule_interval(self._open_door_clock, .01)
        else:
            toast(f"Please connect doors and try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5)

    def show_ok_dialog(self):

        if not self.ids.start_number_field.text.strip():
            self._open_alert_dialog(text="Start number is required")

        else:
            try:
                self.start_number = int(self.ids.start_number_field.text.strip())
                self.ids.technician_label.text = "Setup beginning..."

                if self._is_all_doors_opened:
                    Clock.max_iteration = 30
                    hub = SerialHub()
                    self._number_connected_door = int(self.ids.locker_number_label.text.strip())
                    self._cnt = 0
                    self._door_info_pos = hub.send_status_command()
                    self._skip_door_pos = list()
                    self._num2pos = dict()
                    Clock.schedule_interval(partial(self._setup, hub), 1)

                else:
                    self.ids.technician_label.text = "Please click on the open all doors button"

                #self.test_setup()
            except ValueError:
                self._open_alert_dialog(text="Start number must be an integer")


class OkDialogContent(FloatLayout):
    def __init__(self, **kwargs):
        super(OkDialogContent, self).__init__(**kwargs)
