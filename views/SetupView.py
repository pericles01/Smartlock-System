from kivy.properties import BooleanProperty #, StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
import json
from manage.SerialHub import SerialHub
import os
import threading
import time
import random

class SetupView(RelativeLayout):
    isSetup = BooleanProperty()
    start_number = 0
    is_dialog_dismissed = False
    def __init__(self, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self.dialog = Popup(title="Alert", title_align="center", title_size="20sp", size_hint=(0.5, 0.5),
                            auto_dismiss=False)

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

    def _setup(self):

        hub = SerialHub()
        is_opened = hub.open_all_doors()
        time.sleep(2)
        if isinstance(is_opened, bool):
            self.ids.technician_label.text = "All doors are open"
            skip_door_pos = list()
            num2pos = dict()
            number_connected_door = int(self.ids.locker_number_label.text)
            cnt = 0
            door_info_pos = hub.send_status_command()

            while 1:
                door_number = str(self.start_number + cnt)
                self.ids.technician_label.text ="Please close door number: " + door_number

                if door_info_pos == hub.send_status_command(): # no change, door not locked yet then skip this iteration
                    continue
                # door closed
                door_info_pos = hub.send_status_command() # retrieve current status & update
                # guess the position of the closed door & map the door number to the guessed position
                for k in door_info_pos.keys():
                    if door_info_pos[k] == "closed":
                        if k not in skip_door_pos:
                            num2pos[door_number] = int(k)
                            skip_door_pos.append(k)
                            cnt += 1
                            if cnt == number_connected_door:
                                break

            # save the mapping dict for future use
            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
            with open(path, mode='w') as f:
                json.dump(num2pos, f, indent=2)
        else:
            self.ids.technician_label.text = is_opened[1]


    def show_ok_dialog(self):

        if not self.ids.start_number_field.text:
            self._open_alert_dialog(text="Start number is required")

        else:
            try:
                self.start_number = int(self.ids.start_number_field.text)
                self.ids.technician_label.text = "Setup beginning..."
                x = threading.Thread(target=self._setup(), daemon=True)
                x.start()
                #self.test_setup()
            except ValueError:
                self._open_alert_dialog(text="Start number must be an integer")





class OkDialogContent(FloatLayout):
    def __init__(self, **kwargs):
        super(OkDialogContent, self).__init__(**kwargs)