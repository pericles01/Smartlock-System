import face_recognition
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from manage.SerialHub import SerialHub
import serial
from manage.Database import Database
from kivymd.app import MDApp
from kivy.clock import Clock
from functools import partial
import json
import os
import io
import cv2
try:
    from picamera2 import Picamera2
except ImportError:
    pass
import numpy as np

from manage.rpi_face_recon import predict


class LoginOptionCard(MDCard):
    text_option = StringProperty()
    icon_name = StringProperty()
    press_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(LoginOptionCard, self).__init__(**kwargs)
        self.shadow_offset = (0, 1)


class WelcomeView(MDScreen):
    def __init__(self, **kwargs):
        super(WelcomeView, self).__init__(**kwargs)

        self.snapshot_dialog = Popup(title="Video capture", title_align="center", title_size="20sp",
                                     size_hint=(0.8, 0.9),
                                     auto_dismiss=False)
        self.snapshot_dialog_content = SnapshotDialogContent()
        self.__time_out = 0
        Clock.max_iteration = 20
        self.__save_snapshot_path = os.path.join(os.getcwd(), ".cache", "video_stream.png")
        self.found_user = None
        self._db = Database()
        self._is_rpi = self.is_raspberrypi()
        self._picam2 = None
        self._cv_cam = None
        self._cnt = int()

    def _on_text_validate(self, instance):
        uid = instance.text.strip()
        print(f"Text: {uid} validated")
        self.ids.pin_field.ids.password_field.text = ""
        self.ids.pin_field.ids.password_field.focus = True
        self.login_rfid(uid)

    def on_pre_enter(self, *args):
        self._db.db_init(refresh=True)
        self.ids.pin_field.ids.password_field.focus = True
        self.ids.error_label.text = "* required field"
        self.ids.pin_field.ids.password_field.bind(on_text_validate=self._on_text_validate)
        self.ids.go2membership.active = False

    def on_release_num_btn_callback(self, instance):
        old_pin_text = self.ids.pin_field.ids.password_field.text
        self.ids.pin_field.ids.password_field.text = old_pin_text + instance.text

    def on_release_del_btn_callback(self, instance):
        old_pin_text = self.ids.pin_field.ids.password_field.text
        if len(old_pin_text) > 0:
            self.ids.pin_field.ids.password_field.text = old_pin_text[:-1]

    def on_release_login_btn_callback(self):
        if self.ids.go2membership.active:
            print("Log in into membership...")
        else:
            print("Opening door...")

    def is_raspberrypi(self):
        try:
            with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
                if 'raspberry pi' in m.read().lower(): return True
        except Exception:
            pass
        return False

    def _refresh_welcome_screen(self, *args):
        self.ids.pin_field.ids.password_field.focus = True
        self.ids.go2membership.active = False

    def _go2user_membership(self):
        MDApp.get_running_app().found_user = self.found_user
        MDApp.get_running_app().manager.push("user_membership")

    def login_rfid(self, rfid_code):
        # reset
        self.found_user = None

        user = self._db.get_user_by_rfid(rfid_code)
        if user:
            self.found_user = user
            if self.ids.go2membership.active:
                self._go2user_membership()
                toast(f"Successfully login into your membership",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                      )
            else:
                self._open_door_callback(self.found_user[2])
                Clock.schedule_once(self._refresh_welcome_screen, 3)

        else:
            toast(f"User not found, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=2)
            Clock.schedule_once(self._refresh_welcome_screen, 3)

    def login_pin(self):
        # reset
        self.found_user = None

        if self.ids.pin_field.ids.password_field.text.strip():
            try:
                pin = int(self.ids.pin_field.ids.password_field.text.strip())
                # search PIN in the database
                user = self._db.get_user_by_pin(pin)

                if user:
                    self.found_user = user
                    if self.ids.go2membership.active:
                        self._go2user_membership()
                        toast(f"Successfully login into your membership",
                              background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                              )
                    else:
                        self._open_door_callback(self.found_user[2])
                        Clock.schedule_once(self._refresh_welcome_screen, 3)
                else:
                    self.ids.error_label.text = "User not found, please verify your PIN input"
                    toast(f"User not found, please try again!!",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                    Clock.schedule_once(self._refresh_welcome_screen, 3)
                self.ids.pin_field.ids.password_field.text = ""
            except ValueError as e:
                self.ids.error_label.text = "PIN must be a numeric number"
                print(e)
        else:
            self.ids.error_label.text = "Please enter your numeric PIN"

    def login_qr_code_reader(self, reader_data:str):
        # reset
        self.found_user = None

        try:
            found_user = reader_data.split("'")
            found_user = [found_user[0], found_user[1], int(found_user[2])]
            print(f"Reader Data: {found_user}")

            if self._db.is_in_db(found_user):
                self.found_user = found_user
                toast(f"Successfully found User: {self.found_user[0]}, {self.found_user[1]}",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2)
                if self.ids.go2membership.active:
                    self._go2user_membership()
                    toast(f"Successfully login into your membership",
                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                          )
                else:
                    self._open_door_callback(self.found_user[2])
                    Clock.schedule_once(self._refresh_welcome_screen, 3)
            else:
                toast(f"User not found, please try again!!",
                      background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                Clock.schedule_once(self._refresh_welcome_screen, 3)
        except Exception as e:
            print(e)
            toast(f"User not found, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=2)
            Clock.schedule_once(self._refresh_welcome_screen, 3)

    def login_qr_code_cam(self):
        self.snapshot_dialog_content.ids.label.text = "Please place your QR Code on the camera"

        self.snapshot_dialog_content.ids.image.source = self.__save_snapshot_path
        self.snapshot_dialog_content.ids.image.reload()
        self.snapshot_dialog.content = self.snapshot_dialog_content
        self.snapshot_dialog.bind(on_dismiss=self._snapshot_dialog_dismiss_callback)
        self.snapshot_dialog.open()
        Clock.schedule_interval(self.snap_save, 0.2)  # 5 fps

    def login_face_id(self):
        self.snapshot_dialog_content.ids.label.text = "Please place your Face at the camera"

        self.snapshot_dialog_content.ids.image.source = self.__save_snapshot_path
        self.snapshot_dialog_content.ids.image.reload()
        self.snapshot_dialog.content = self.snapshot_dialog_content
        self.snapshot_dialog.bind(on_dismiss=self._snapshot_dialog_dismiss_callback)
        self.snapshot_dialog.open()
        Clock.schedule_interval(partial(self.snap_save, False), 0.2)  # 5 fps

    def snap_save(self, for_qr_code=True, *args):
        if self._is_rpi:
            if MDApp.get_running_app().rpi_cam:
                return self._rpi_cam_snap(for_qr_code)
            else:
                return self._webcam_snap(for_qr_code)
        else:
            return self._webcam_snap(for_qr_code)

    def _rpi_cam_snap(self, _for_qr_code=True):
        # reset
        self.found_user = None

        if self._picam2 is None:
            self._picam2 = Picamera2()
            config = self._picam2.create_still_configuration({"size": (400, 400), "format": "RGB888"})
            self._picam2.configure(config)
        self._picam2.start(show_preview=False)

        self._picam2.capture_file(self.__save_snapshot_path)
        image = self._picam2.capture_array()
        found_user = None
        if _for_qr_code:
            qr_detector = cv2.QRCodeDetector()
            data, bbox, _ = qr_detector.detectAndDecode(image)
            if bbox is not None:
                for points_array in bbox:
                    if data:
                        print(f"Detected QR Code Data: {data}")
                        found_user = data
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)
                        print("QR Code data can't be detected")

                    cv2.polylines(image, [points_array.astype(int)], isClosed=True, color=color,
                                  thickness=2)
            else:
                print("No QR Code detected")

            cv2.imwrite(self.__save_snapshot_path, image)
            self.snapshot_dialog_content.ids.image.reload()
            if found_user is not None:
                self.snapshot_dialog.dismiss()
                try:
                    found_user = found_user.split("|")
                    found_user = [found_user[0], found_user[1], int(found_user[2])]

                    if self._db.is_in_db(found_user):
                        toast(f"Successfully found User: {self.found_user[0]}, {self.found_user[1]}",
                              background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2)
                        self.found_user = found_user

                        if self.ids.go2membership.active:
                            self._go2user_membership()
                            toast(f"Successfully login into your membership",
                                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                                  )
                        else:
                            self._open_door_callback(self.found_user[2])
                            Clock.schedule_once(self._refresh_welcome_screen, 3)
                    else:
                        toast(f"User not found, please try again!!",
                              background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                except Exception as e:
                    print(e)
                    toast(f"User not found, please try again!!",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=2)

                return False

        else:  # for face_id
            cv2.imwrite(self.__save_snapshot_path, image)
            self.snapshot_dialog_content.ids.image.reload()
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                save_path = os.path.join(os.getcwd(), ".cache/trained_knn_model.clf")
                predictions = predict(image, model_path=save_path)
                name = predictions[0][0]

                self.snapshot_dialog.dismiss()

                if name == "unknown":
                    toast(f"User not found, please try again!!",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=5)
                else:
                    try:
                        found_user = name.split("_")
                        found_user = [found_user[0], found_user[1], int(found_user[2])]
                        if self._db.is_in_db(found_user):
                            toast(f"Successfully found User: {found_user[0]}, {found_user[1]}",
                                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2)
                            self.found_user = found_user

                            if self.ids.go2membership.active:
                                self._go2user_membership()
                                toast(f"Successfully login into your membership",
                                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                                      )
                            else:
                                self._open_door_callback(self.found_user[2])
                                Clock.schedule_once(self._refresh_welcome_screen, 3)
                        else:
                            toast(f"User not found, please try again!!",
                                  background=get_color_from_hex(colors["Red"]["500"]), duration=2)

                    except Exception as e:
                        print(e)
                        toast(f"User not found, please try again!!",
                              background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                        Clock.schedule_once(self._refresh_welcome_screen, 3)

                return False

        if self.__time_out == 15:  # 10 seconds

            self.snapshot_dialog.dismiss()
            toast(f"Timeout reached! No user found, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=2
                  )
            Clock.schedule_once(self._refresh_welcome_screen, 3)
            return False
        else:
            self.__time_out += 1

    def _webcam_snap(self, _for_qr_code=True):
        # reset
        self.found_user = None

        if self._cv_cam is None:
            self._cv_cam = cv2.VideoCapture(0)
        if self._cv_cam.isOpened():
            result, image = self._cv_cam.read()
            found_user = None
            if result:
                if _for_qr_code:
                    qr_detector = cv2.QRCodeDetector()
                    data, bbox, _ = qr_detector.detectAndDecode(image)
                    if bbox is not None:
                        for points_array in bbox:
                            if data:
                                found_user = data
                                print(f"Detected QR Code Data: {data}")
                                color = (0, 255, 0)
                            else:
                                color = (0, 0, 255)

                            cv2.polylines(image, [points_array.astype(int)], isClosed=True, color=color,
                                          thickness=2)

                    cv2.imwrite(self.__save_snapshot_path, image)
                    self.snapshot_dialog_content.ids.image.reload()
                    if found_user is not None:
                        self.snapshot_dialog.dismiss()
                        try:
                            found_user = found_user.split("|")
                            found_user = [found_user[0], found_user[1], int(found_user[2])]

                            if self._db.is_in_db(found_user):
                                toast(f"Successfully found User: {found_user[0]}, {found_user[1]}",
                                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2)
                                self.found_user = found_user
                                if self.ids.go2membership.active:
                                    self._go2user_membership()
                                    toast(f"Successfully login into your membership",
                                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                                          )
                                else:
                                    self._open_door_callback(self.found_user[2])
                                    Clock.schedule_once(self._refresh_welcome_screen, 3)
                            else:
                                toast(f"User not found, please try again!!",
                                      background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                        except Exception as e:
                            print(e)
                            toast(f"User not found, please try again!!",
                                  background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                            Clock.schedule_once(self._refresh_welcome_screen, 3)

                        return False

                else:  # for face_id
                    cv2.imwrite(self.__save_snapshot_path, image)
                    self.snapshot_dialog_content.ids.image.reload()
                    face_locations = face_recognition.face_locations(image)
                    if face_locations:
                        save_path = os.path.join(os.getcwd(), ".cache/trained_knn_model.clf")
                        predictions = predict(image, model_path=save_path)
                        name = predictions[0][0]
                        self.snapshot_dialog.dismiss()

                        if name == "unknown":
                            toast(f"User not found, please try again!!",
                                  background=get_color_from_hex(colors["Red"]["500"]), duration=5)
                        else:
                            try:
                                found_user = name.split("_")
                                found_user = [found_user[0], found_user[1], int(found_user[2])]
                                if self._db.is_in_db(found_user):
                                    toast(f"Successfully found User: {found_user[0]}, {found_user[1]}",
                                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2)
                                    self.found_user = found_user

                                    if self.ids.go2membership.active:
                                        self._go2user_membership()
                                        toast(f"Successfully login into your membership",
                                              background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                                              )
                                    else:
                                        self._open_door_callback(self.found_user[2])
                                        Clock.schedule_once(self._refresh_welcome_screen, 3)
                                else:
                                    toast(f"User not found, please try again!!",
                                          background=get_color_from_hex(colors["Red"]["500"]), duration=2)

                            except Exception as e:
                                print(e)
                                toast(f"User not found, please try again!!",
                                      background=get_color_from_hex(colors["Red"]["500"]), duration=2)
                                Clock.schedule_once(self._refresh_welcome_screen, 3)

                        return False

            if self.__time_out == 15:  # 10 seconds

                self.snapshot_dialog.dismiss()
                toast(f"Timeout reached! No user found, please try again!!",
                      background=get_color_from_hex(colors["Red"]["500"]), duration=2
                      )
                Clock.schedule_once(self._refresh_welcome_screen, 3)

                return False
            else:
                self.__time_out += 1

        else:
            toast(f"Error while opening the camera, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=2
                  )
            self.snapshot_dialog.dismiss()
            Clock.schedule_once(self._refresh_welcome_screen, 3)
            return False

    def _snapshot_dialog_dismiss_callback(self, instance):
        image = np.zeros((600, 600, 3), dtype='uint8')
        cv2.imwrite(self.__save_snapshot_path, image)
        self.snapshot_dialog_content.ids.image.reload()
        self.__time_out = 0
        if MDApp.get_running_app().rpi_cam:
            self._picam2.stop_preview()
            self._picam2.stop()
        else:
            self._cv_cam.release()
            self._cv_cam = None

    def _open_door_callback(self, door_number: int, *args):
        hub = SerialHub()
        try:
            # retrieve door position
            path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
            with open(path, "r") as f:
                door_pos_mapping = json.load(f)
                door_pos = int(door_pos_mapping[str(door_number)])
                print(f"User door number: {door_number}, mapping position: {door_pos}")
            # retrieve door position status
            doors_status = hub.send_status_command()
            status = doors_status[str(door_pos)]
            if status == "open":
                toast(f"Door is already open",
                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2
                      )
            else:
                if hub.send_open_command(door_pos):
                    # ToDo buffer peep
                    toast(f"Door opened",
                          background=get_color_from_hex(colors["LightGreen"]["500"]), duration=2
                          )
                # make sure the status changed
                if doors_status == hub.send_status_command():
                    toast(f"Could not open the door, try again",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=2
                          )

        except (serial.SerialException, ValueError) as e:
            toast("Could not open the door. Please make sure that the Hub device is connected correctly and try again",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=2
                  )


class SnapshotDialogContent(RelativeLayout):
    snapshot = StringProperty()
    def __init__(self, **kwargs):
        super(SnapshotDialogContent, self).__init__(**kwargs)
