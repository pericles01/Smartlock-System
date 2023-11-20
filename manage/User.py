

class User:
    def __init__(self, firstname, lastname, door_number, description, rfid_code):
        # user characteristics
        self.__firstname = firstname
        self.__lastname = lastname
        self.__door_number = door_number
        self.__description = description
        # unlock methods
        self.__rfid_code = rfid_code
        self.__pin_code = None
        self.__qr_code = None
        self.__face_id = None

    def get_firstname(self):
        return self.__firstname

    def set_firstname(self, new_firstname):
        self.__firstname = new_firstname

    def get_lastname(self):
        return self.__lastname

    def set_lastname(self, new_lastname):
        self.__lastname = new_lastname

    def get_door_number(self):
        return self.__door_number

    def set_door_number(self, new_door_number):
        self.__door_number = new_door_number

    def get_description(self):
        return self.__description

    def set_description(self, new_description):
        self.__description = new_description

    def get_rfid_code(self):
        return self.__rfid_code

    def set_rfid_code(self, new_rfid_code):
        self.__rfid_code = new_rfid_code

    def get_qr_code(self):
        return self.__qr_code

    def set_qr_code(self, new_qr_code):
        self.__qr_code = new_qr_code

    def get_pin_code(self):
        return self.__pin_code

    def set_pin_code(self, new_pin_code):
        self.__pin_code = new_pin_code

    def get_face_id(self):
        return self.__face_id

    def set_face_id(self, new_face_id):
        self.__face_id = new_face_id

