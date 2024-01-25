from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.toast import toast
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from manage.Database import Database
import qrcode
from random import choice
import io

try:
    from picamera2 import Picamera2
except ImportError:
    pass

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
        self.ids.update_password_screen.found_user = self.found_user
        self.ids.user_qr_code_screen.found_user = self.found_user
        self.ids.face_recon_screen.found_user = self.found_user
        self.ids.manager.current = "home" # reload the page to trigger his on_pre_enter event
    
    def on_leave(self, *args):
        self.ids.manager.current = "password"



class UpdateUserPasswordView(MDScreen):
    found_user = ObjectProperty()
    def __init__(self, **kwargs):
        super(UpdateUserPasswordView, self).__init__(**kwargs)
        self.__db = Database()

    def on_enter(self, *args):

        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)
            password = self.__db.get_user_password(self.found_user)
            if password:
                self.ids.user_password_field.text = str(password)
            else:
                self.ids.user_password_field.text = "No Password set yet"

    def _verify_input_password(self, password:str) -> bool:
        """
        Verify if the password meets the rules:
        at least 6 characters with at least 2 numeric numbers within it
        :param password:
        :return:
        """
        cnt = 0
        if len(password) >= 6:
            for char in password:
                try:
                    _ = int(char)
                    cnt += 1
                except ValueError:
                    continue
            if cnt >=2:
                return True
            else:
                return False
        else:
            return False

    def update_password(self):
        if self.ids.new_password.ids.password_field.text.strip() and self.ids.confirm_password.ids.password_field.text.strip():
            new_password = self.ids.new_password.ids.password_field.text.strip()
            confirm_password = self.ids.confirm_password.ids.password_field.text.strip()
            if new_password == confirm_password:
                if self._verify_input_password(confirm_password):
                    if confirm_password not in self.__db.get_db_password_list():
                        if self.__db.update_user_password(list(self.found_user), confirm_password):
                            self.ids.user_password_field.text = confirm_password
                            toast(f"Password Successfully updated",
                                  background=get_color_from_hex(colors["LightGreen"]["500"]), duration=3
                                  )
                            # reset
                            self.ids.new_password.ids.password_field.text = ""
                            self.ids.confirm_password.ids.password_field.text = ""
                            self.ids.error_label.text = "* required fields, Password must have at least 6 characters with a least 2 numeric numbers within it"
                            print("---------")
                            print("Test Update")
                            print("---------")
                            print(self.__db.show_users_table(full=True))
                        else:
                            toast(f"Error occurred when updating Password, please try again!",
                                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                                  )
                            # reset
                            self.ids.new_password.ids.password_field.text = ""
                            self.ids.confirm_password.ids.password_field.text = ""
                    else:
                        toast(f"Invalid password, please try another one!",
                              background=get_color_from_hex(colors["Red"]["500"]), duration=5
                              )
                        # reset
                        self.ids.new_password.ids.password_field.text = ""
                        self.ids.confirm_password.ids.password_field.text = ""
                else:
                    self.ids.error_label.text = "Password must have at least 6 characters with a least 2 numeric numbers within it"
            else:
                self.ids.error_label.text = "New Password must be equal to confirmation Password"

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
            if os.path.exists(qr_path):
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
        self._is_rpi = self.is_raspberrypi()
        self._picam2 = None
        self._cv_cam = None
        self._no_face_img_path = os.path.join(os.getcwd(), ".cache", "video_stream.png")
        self.confidentiality_confirmation_dialog = Popup(title="Confidentiality confirmation", title_align="center", title_size="20sp",
                                      size_hint=(0.7, 0.8), auto_dismiss=False)
        self.confidentiality_confirmation_content = ConfidentialityConfirmationContent()

    def on_enter(self, *args):
        if self.found_user:
            print(f"User: {self.found_user}")
            self.__db.db_init(refresh=True)

    def is_raspberrypi(self):
        try:
            with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
                if 'raspberry pi' in m.read().lower(): return True
        except Exception: pass
        return False
    
    def snap_save(self, *args):
        if self._is_rpi:
            if MDApp.get_running_app().rpi_cam:
                return self._rpi_cam_snap()
            else:
                return self._webcam_snap()
        else:
            return self._webcam_snap()

    def _show_on_snap_dialog(self, _image):
        cv2.imwrite(self._no_face_img_path, _image)
        self.snapshot_dialog_content.ids.image.source = self._no_face_img_path
        self.snapshot_dialog_content.ids.image.reload() 

    def _rpi_cam_snap(self):
        if self._picam2 is None:
            self._picam2 = Picamera2()
            config = self._picam2.create_still_configuration({"size": (400, 400), "format": "RGB888"})
            self._picam2.configure(config)
        self._picam2.start(show_preview=False)
        image = self._picam2.capture_array()
        face_locations = face_recognition.face_locations(image)
        self._show_on_snap_dialog(image)
        if face_locations:

            if self.__time_out % 2 == 0: #skip 2 frames/iterations
                self.__cnt += 1
                path = os.path.join(self.__save_snapshot_path, str(self.__cnt)+".png")
                cv2.imwrite(path, image)
                self.snapshot_dialog_content.ids.image.source = path
                self.snapshot_dialog_content.ids.image.reload()
                if self.__cnt == 5:
                    if self.__db.update_face_id(self.found_user, self.__save_snapshot_path):
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
            toast(f"Timeout reached! No face detected for face id, please try again!!",
                    background=get_color_from_hex(colors["Red"]["500"]), duration=5
                    )
            return False
        else:
            self.__time_out += 1
    
    def _webcam_snap(self):
        if self._cv_cam is None:
            self._cv_cam = cv2.VideoCapture(0)
        if self._cv_cam.isOpened():
            result, image = self._cv_cam.read()
            if result:
                face_locations = face_recognition.face_locations(image)
                self._show_on_snap_dialog(image)
                if face_locations:
                    if self.__time_out % 2 == 0:
                        self.__cnt += 1
                        path = os.path.join(self.__save_snapshot_path, str(self.__cnt)+".png")
                        cv2.imwrite(path, image)
                        self.snapshot_dialog_content.ids.image.source = path
                        self.snapshot_dialog_content.ids.image.reload()
                        if self.__cnt == 5:
                            if self.__db.update_face_id(self.found_user, self.__save_snapshot_path):
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
                    toast(f"Timeout reached! No face detected for face id, please try again!!",
                          background=get_color_from_hex(colors["Red"]["500"]), duration=5
                          )
                    return False
                else:
                    self.__time_out += 1

        else:
            toast(f"Error while opening the camera, please try again!!",
                  background=get_color_from_hex(colors["Red"]["500"]), duration=5
                  )
            self.snapshot_dialog.dismiss()
            return False

    def _snapshot_dismiss_callback(self, instance):
        image = np.zeros((600, 600, 3), dtype='uint8')
        self._show_on_snap_dialog(image)
        self.__time_out = 0
        self.__cnt = 0
        if MDApp.get_running_app().rpi_cam:
            self._picam2.stop_preview()
            self._picam2.stop()
        else:
            self._cv_cam.release()
            self._cv_cam = None

    def open_snapshot_dialog(self):
        self.snapshot_dialog_content.ids.image.source = self._no_face_img_path
        self.snapshot_dialog_content.ids.image.reload()
        self.snapshot_dialog.content = self.snapshot_dialog_content
        self.snapshot_dialog.bind(on_dismiss=self._snapshot_dismiss_callback)
        self.snapshot_dialog.open()
        dir_path = os.path.join(os.getcwd(), ".cache", "face_recon")
        self.__save_snapshot_path = os.path.join(dir_path, "_".join([str(x) for x in self.found_user]))
        os.makedirs(self.__save_snapshot_path, exist_ok=True)
        Clock.schedule_interval(self.snap_save, 0.2)

    def _go2snapshot_dialog(self, instance):
        self.confidentiality_confirmation_dialog.dismiss()
        self.open_snapshot_dialog()

    def open_confidentiality_confirmation_dialog(self):

        self.confidentiality_confirmation_content.ids.label.text = """
            To enable face ID recognition, we need to store some of your facial images locally on your device. Please read and agree to the following terms and conditions before proceeding.
            
            1. Confidentiality and Security
            
            We take your privacy very seriously and will only use your facial images for the purpose of face ID recognition. We will not share your facial images with any third parties without your explicit consent. Your facial images will be stored securely on the smartlocker device and will be deleted 
            if you deactivate this feature later.
            
            2. Image Capture
            
            To train the face ID recognition model, we need to capture several facial images of you. The images will be used to create a unique facial representation of you. This representation will be used to identify you when you use the face ID recognition feature.
            
            3. Image Access
            
            You can access and delete your facial images at any time. To do this, go to the settings menu of the app.
            
            4. Consent
            
            By clicking "Agree," you agree to the terms and conditions set forth above. You also agree to allow us to store and use your facial images for the purpose of face ID recognition.
            
            5. Continued Use
            
            If you do not agree to the terms and conditions, you will not be able to use the face ID recognition feature.
            
            6. Review and Changes
            
            We may update these terms and conditions from time to time. You will be notified of any changes by email or through the app. You agree to review these terms and conditions periodically and to be bound by the latest version.
        """
        self.confidentiality_confirmation_content.ids.yes_button.text = "I agree"
        self.confidentiality_confirmation_content.ids.yes_button.bind(on_release=self._go2snapshot_dialog)
        self.confidentiality_confirmation_content.ids.no_button.text = "I disagree"
        self.confidentiality_confirmation_content.ids.no_button.bind(on_release=self.confidentiality_confirmation_dialog.dismiss)
        self.confidentiality_confirmation_dialog.content = self.confidentiality_confirmation_content
        self.confidentiality_confirmation_dialog.open()

class SnapshotDialogContent(MDFloatLayout):
    def __init__(self, **kwargs):
        super(SnapshotDialogContent, self).__init__(**kwargs)

class ConfidentialityConfirmationContent(RelativeLayout):
    def __init__(self, **kwargs):
        super(ConfidentialityConfirmationContent, self).__init__(**kwargs)

