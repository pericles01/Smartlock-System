from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
import json
from manage.SerialHub import SerialHub
import os
from kivy.clock import Clock
from functools import partial
import  serial
import random

class SetupView(RelativeLayout):
    isSetup = BooleanProperty()
    start_number = 0
    is_dialog_dismissed = False
    def __init__(self, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self.dialog = Popup(title="Alert", title_align="center", title_size="20sp", size_hint=(0.5, 0.5),
                            auto_dismiss=False)
        # will come in handy later
        self._skip_door_pos = list()
        self._cnt = int()
        self._door_info_pos = dict()
        self._num2pos = dict()
        self._number_connected_door = int()
        self._is_all_doors_opened = False
        self._door_position = 1

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

    def test_setup(self):
        num2pos = dict()
        number_connected_door = int(self.ids.locker_number_label.text)
        guessed_pos_list = list()
        start_number = self.start_number
        cnt = 0
        guessed_pos = 0
        while 1:
            door_number = str(start_number + cnt)
            self.ids.technician_label.text = "Please close door number: " + door_number
            number = random.randint(0, number_connected_door)
            if guessed_pos == number:
                continue  # skip
            if number not in guessed_pos_list and number != 0:  # skip
                guessed_pos = number  # update
                guessed_pos_list.append(guessed_pos)
                num2pos[door_number] = guessed_pos
                cnt += 1
                if cnt == int(number_connected_door):
                    print("fertig")
                    break

        path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
        with open(path, mode='w') as f:
            json.dump(num2pos, f, indent=2)

    def _setup(self, _hub):

        door_number = str(self.start_number + self._cnt)
        self.ids.technician_label.text ="Please close door number: " + door_number

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
                        if self._cnt == self._number_connected_door:
                            # save the mapping dict for future use
                            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
                            with open(path, mode='w') as f:
                                json.dump(self._num2pos, f, indent=2)
                            return False

    def _open_door_clock(self, *args):
        try:
            hub = SerialHub()
            self._door_position = 1
            if hub.send_open_command(self._door_position):
                self._door_position += 1

            if self._door_position == 17:
                self._door_position = 1
                self._is_all_doors_opened = True
                self.ids.technician_label.text = "All doors are open"
                return False # stop clock
        except serial.SerialException as e:
            self.ids.technician_label.text = "No Hub detected!! Please verify if the hub is connected"
            return False  # stop clock

    def open_all_doors(self):
        Clock.schedule_interval(self._open_door_clock, 1)

    def show_ok_dialog(self):

        if not self.ids.start_number_field.text:
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
                    Clock.schedule_interval(partial(self._setup, hub), 10)

                else:
                    self.ids.technician_label.text = "Please click on the open all doors button"

                #self.test_setup()
            except ValueError:
                self._open_alert_dialog(text="Start number must be an integer")





class OkDialogContent(FloatLayout):
    def __init__(self, **kwargs):
        super(OkDialogContent, self).__init__(**kwargs)
