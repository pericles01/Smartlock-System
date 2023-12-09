import cv2
import face_recognition
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from manage.Database import Database
import qrcode
from random import choice
import os
import string
from manage.rpi_face_recon import *
from kivy.clock import Clock

class UserMembershipView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserMembershipView, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.found_user = MDApp.get_running_app().found_user
        print(f"Welcome {self.found_user[0]}, {self.found_user[1]} !")
        self.ids.topbar.title = f"Welcome {self.found_user[0]}, {self.found_user[1]} !"
        self.ids.user_welcome_screen.found_user = self.found_user
        self.ids.update_pin_screen.found_user = self.found_user
        self.ids.user_qr_code_screen.found_user = self.found_user
        self.ids.face_recon_screen.found_user = self.found_user
        self.ids.manager.current = "home" # reload the page to trigger his on_pre_enter event
    
    def on_leave(self, *args):
        self.ids.manager.current = "pin"



class UpdateUserPinView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UpdateUserPinView, self).__init__(**kwargs)
        self.__db = Database()

    def on_enter(self, *args):

        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)
            pin = self.__db.get_user_pin(self.found_user)
            if pin:
                self.ids.user_pin_field.text = str(pin)
            else:
                self.ids.user_pin_field.text = "No PIN set yet"

    def update_pin(self):
        if self.ids.new_pin.ids.password_field.text.strip() and self.ids.confirm_pin.ids.password_field.text.strip():
            try:
                new_pin = int(self.ids.new_pin.ids.password_field.text.strip())
                confirm_pin = int(self.ids.confirm_pin.ids.password_field.text.strip())
                if new_pin == confirm_pin:
                    if len(str(new_pin)) == 6 and len(str(confirm_pin)) == 6:
                        if self.__db.update_user_pin(list(self.found_user), confirm_pin):
                            toast(f"PIN Successfully updated",
                                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                                  )
                            # reset
                            self.ids.new_pin.ids.password_field.text = ""
                            self.ids.confirm_pin.ids.password_field.text = ""
                            self.ids.error_label.text = "* required fields, PIN must have 6 digits"
                            print("---------")
                            print("Test Update")
                            print("---------")
                            print(self.__db.show_users_table(full=True))
                        else:
                            toast(f"Error occurred when updating PIN, please try again!",
                                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                                  )
                    else:
                        self.ids.error_label.text = "PIN must have 6 digits"
                else:
                    self.ids.error_label.text = "New PIN must be equal to confirmation PIN"
            except ValueError:
                self.ids.error_label.text = "New PIN and Confirmation PIN must be numeric numbers"

        else:
            self.ids.error_label.text = "Please fill required fields"


class GenerateQRCodeView(MDScreen):
    found_user = ObjectProperty()

    def __init__(self, **kwargs):
        super(GenerateQRCodeView, self).__init__(**kwargs)
        self.__db = Database()

    def on_enter(self, *args):

        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)
            qr_path = self.__db.get_user_qr_img_path(self.found_user)
            if qr_path:
                self.ids.image.source = qr_path


    def generate_qr_code(self):
        # Find & delete old path
        qr_path = self.__db.get_user_qr_img_path(self.found_user)
        if qr_path:
            os.remove(qr_path)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        data = "|".join([str(x) for x in self.found_user])
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        length = 10
        characters = string.ascii_letters + string.digits
        random_string = ''
        for i in range(length):
            random_character = choice(characters)
            random_string += random_character

        dir_path = os.path.join(os.getcwd(), ".cache", "qr_codes")
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, random_string+"_qr_code.png")
        print(path)
        img.save(path)
        self.ids.image.source = path
        if self.__db.update_qr_code(self.found_user, path):
            toast(f"QR Code Successfully updated",
                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                  )
        else:
            toast(f"Error occurred when saving generated QR Code, please try again!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )

class RegisterFaceReconView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(RegisterFaceReconView, self).__init__(**kwargs)
        self.__save_snapshot_path = None
        self.snapshot_dialog = Popup(title="Video capture", title_align="center", title_size="20sp",
                                     size_hint=(0.8, 0.9), auto_dismiss=False)
        self.snapshot_dialog_content = SnapshotDialogContent()
        self.__time_out = 0
        self.__cnt = 0
        self.__db = Database()

    def on_enter(self, *args):
        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)

    def snap_save(self, *args):
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            result, image = cam.read()
            if result:
                face_locations = face_recognition.face_locations(image)
                if face_locations:

                    if self.__time_out % 2 == 0:
                        self.__cnt += 1
                        path = os.path.join(self.__save_snapshot_path, str(self.__cnt)+".png")
                        cv2.imwrite(path, image)
                        self.snapshot_dialog_content.ids.image.source = path
                        self.snapshot_dialog_content.ids.image.reload()
                        if self.__cnt == 5:
                            if self.__db.update_face_id(self.found_user, self.__save_snapshot_path):
                                self.__cnt = 0
                                self.__time_out = 0
                                cam.release()
                                self.snapshot_dialog.dismiss()
                                print("** Test Face Id **")
                                print(f"{self.__db.show_users_table(full=True)}")
                                toast(f"Successfully Registered face id",
                                      background=get_color_from_hex(colors["LightGreen"]["500"]), duration=5)
                                print("Training KNN classifier...")
                                path = os.path.join(os.getcwd(), ".cache/face_recon")
                                save_path = os.path.join(os.getcwd(), ".cache/trained_knn_model.clf")
                                if train(path, model_save_path=save_path, n_neighbors=2):
                                    print("Training complete!")
                                    return False


                if self.__time_out == 15:

                    self.snapshot_dialog.dismiss()
                    self.__time_out = 0
                    toast(f"Timeout reached! No face detected for face id, please try again!!",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=5
                          )
                    cam.release()
                    return False
                else:
                    self.__time_out += 1

        else:
            toast(f"Error while opening the camera, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )
            self.snapshot_dialog.dismiss()
            cam.release()
            return False

    def open_snapshot_dialog(self):
        self.snapshot_dialog_content.ids.image.source = os.path.join(os.getcwd(), ".cache", "video_stream.png")
        self.snapshot_dialog.content = self.snapshot_dialog_content
        self.snapshot_dialog.open()
        dir_path = os.path.join(os.getcwd(), ".cache", "face_recon")
        self.__save_snapshot_path = os.path.join(dir_path, self.found_user[0] + "_" + self.found_user[1])
        os.makedirs(self.__save_snapshot_path, exist_ok=True)
        Clock.schedule_interval(self.snap_save, 0.2)

class SnapshotDialogContent(MDFloatLayout):
    def __init__(self, **kwargs):
        super(SnapshotDialogContent, self).__init__(**kwargs)

