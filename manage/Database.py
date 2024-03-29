import sqlite3
import os

class Database:
    def __init__(self):
        self.__user_list = list()
        self.__db_connection = None
        self.__cursor = None

    def db_init(self, refresh:bool=False)->None:
        """
        create a connection to an existing database or create and configure a nwe one
        :param refresh: refresh an existing database to get new modifications
        :return: None
        """
        path = os.path.join(os.getcwd(), ".cache/user.db")
        self.__db_connection = sqlite3.connect(path)
        self.__cursor = self.__db_connection.cursor()
        if not refresh:
            try:
                self.__cursor.execute("CREATE TABLE users(firstname, lastname, rfid_code, door_number, description, password, qr_code, face_id)"
                )

                self.__cursor.execute("CREATE TABLE admins(id, username, password)")
                admins = [(1, "admin", "admin"), (2, "tech", "setup"), (3, "urgency_uid", "CD0566AE")]
                self.__cursor.executemany("INSERT INTO admins(id, username, password) VALUES (?, ?, ?)", admins)
                self.__db_connection.commit()

                print("Table Users created")
                print(f"Content: {self.show_users_table(full=True)}")

                print("Table Admins created")
                print(f"Content: {self.show_admin_table()}")

            except sqlite3.OperationalError as e:
                print(e)

    def close_db_connection(self):
        self.__db_connection.close()

    def add_users(self, users_list: list) -> bool:
        """
        Method used in AdminMembershipView to directly insert users' data coming from a .csv file or a form into the database users table
        :param users_list: users list in the form [[user1_firstname, user1_lastname, user1_rfid_code, user1_door_number, user1_description],
        ...]
        :return: bool: if the insertion was successful or not
        """
        try:
            self.db_init(refresh=True)
            content = self.show_users_table()
            if content:
                found = False
                for user in users_list:
                    for user_db in content:
                        if user == list(user_db):
                            # user already in the database, ignore him
                            found = True
                            break
                    if found:
                        found = False  # reset for next iteration
                    else:
                        found = False
                        self.__cursor.execute(f"INSERT INTO users (firstname, lastname, rfid_code, door_number, description) VALUES (?, ?, ?, ?, ?)" , user)
            else:
                self.__cursor.executemany(
                    "INSERT INTO users (firstname, lastname, rfid_code, door_number, description) VALUES (?, ?, ?, ?, ?)", users_list
                )

            self.__db_connection.commit()
            return True

        except sqlite3.OperationalError as e:
            print(e)
            return False

    def show_users_table(self, full:bool=False)->list:
        """
        Show the content of the users table
        :param full: if true, show the full infos else show only the basics
        :return: a list of the table's content
        """
        if full:
            res = self.__cursor.execute(
                "SELECT * FROM users ORDER BY firstname"
            )
        else:
            res = self.__cursor.execute(
                "SELECT firstname, lastname, rfid_code, door_number, description FROM users ORDER BY firstname"
            )
        return res.fetchall()

    def show_admin_table(self) -> list:
        res = self.__cursor.execute("SELECT * FROM admins ORDER BY id")
        return res.fetchall()

    def update_user_basic_infos(self, user_info:list, new_infos:list):
        """
        Method used in AdminMembershipView to update user information such as firstname, lastname, rfid, door_number, description
        :param user_info: list of length 3 with actual user info [firstname, lastname, rfid]
        :param new_infos: list of length 5 with the new infos to update [firstname, lastname, rfid_code, door_number, description]
        :return: bool: if the update was successful or not
        """
        try:
            assert len(user_info) == 3 and len(new_infos)==5, "the first param must have a length of 3 and the second 5. Please read the method docu"
            new_infos.extend(user_info)
            end_list = list()
            end_list.extend(new_infos)
            command = "UPDATE users SET firstname=?, lastname=?, rfid_code=?, door_number=?, description=? WHERE firstname=? AND lastname=? AND rfid_code=?"
            self.__cursor.execute(command, end_list)
            self.__db_connection.commit()
            return True
        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False

    def update_user_admin_credentials(self, new_admin_credentials:list, old_admin_credentials) -> bool:
        try:
            assert len(new_admin_credentials)==2 and len(old_admin_credentials)==2, "New and old admin credentials list must have a length 2: new username, new password"
            end_list = list()
            end_list.extend(new_admin_credentials)
            end_list.extend(old_admin_credentials)
            command = "UPDATE admins SET username=?, password=? WHERE username=? AND password=?"
            self.__cursor.execute(command, end_list)
            self.__db_connection.commit()
            return True
        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False

    def update_urgency_uid(self, new_uid):
        try:
            end_list = list()
            end_list.append(new_uid)
            end_list.append("urgency_uid")
            command = "UPDATE admins SET password=? WHERE username=?"
            self.__cursor.execute(command, end_list)
            self.__db_connection.commit()
            return True
        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False


    def delete_user(self, user_info)->bool:
        """
        Methode to remove/delete a user from the table
        :param user_info: list of length 3 with actual user info [firstname, lastname, rfid]
        :return: bool: if the removing was successful or not
        """

        try:
            assert len(user_info) == 3, "the user_info list must have a length of 3. Please read the method docu"
            command = "DELETE FROM users WHERE firstname=? AND lastname=? AND rfid_code=?"
            self.__cursor.execute(command, user_info)
            self.__db_connection.commit()
            return True
        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False

    def get_user_by_password(self, password:str) -> tuple|None:
        """
        Get a use from the data base by the input password
        :param password: input password
        :return: list a user infos if found or None
        """
        command = f"SELECT firstname, lastname, door_number FROM users WHERE password=?"
        password_list = list()
        password_list.append(password)
        res = self.__cursor.execute(command, password_list).fetchall()
        print(res)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def get_user_by_rfid(self, rfid:str) -> tuple|None:
        """
        Get a user from the data base by the input rfid
        :param rfid: input rfid
        :return: tuple of user infos if found or None
        """
        command = "SELECT firstname, lastname, door_number FROM users WHERE rfid_code=?"
        uid = list()
        uid.append(rfid)
        res = self.__cursor.execute(command, uid).fetchall()
        print(uid)
        print(res)
        if len(res)>0:
            return res[0]
        else:
            return None

    def update_user_password(self, user_info, new_user_password:str) -> bool:
        """
        Method used in UserMembership to update the user's PIN
        :param user_info: tuple of user's info in order to find him in the database
        :param new_user_password: new PIN
        :return: bool: if the updated processed successfully or not
        """

        try:
            assert len(user_info) == 3 and isinstance(new_user_password, str), "New user PIN must be am integer and user_info must have a length of 3"
            end_list = list()
            end_list.append(new_user_password)
            end_list.extend(user_info)
            command = f"UPDATE users SET password=? WHERE firstname=? AND lastname=? AND door_number=?"
            self.__cursor.execute(command, end_list)
            self.__db_connection.commit()
            return True

        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False

    def update_qr_code(self, user_info, path:str) -> bool:
        """
        Method used in UserMembership to update the user's QR Code
        :param user_info: tuple of user's info in order to find him in the database
        :return: bool: if the updated processed successfully or not
        """

        try:
            assert len(user_info) == 3 and isinstance(path, str), "Path must be a os.path like string and user_info must have a length of 3"
            end_list = list()
            end_list.append(path)
            end_list.extend(user_info)
            command = f"UPDATE users SET qr_code=? WHERE firstname=? AND lastname=? AND door_number=?"
            self.__cursor.execute(command, end_list)
            self.__db_connection.commit()
            return True

        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False

    def update_face_id(self, user_info, path:str) -> bool:
        """
        Method used in UserMembership to update the user's Face Id
        :param user_info: tuple of user's info in order to find him in the database
        :return: bool: if the updated processed successfully or not
        """
        try:
            assert len(user_info) == 3 and isinstance(path, str), "Path must be a os.path like string and user_info must have a length of 3"
            end_list = list()
            end_list.append(path)
            end_list.extend(user_info)
            command = f"UPDATE users SET face_id=? WHERE firstname=? AND lastname=? AND door_number=?"
            self.__cursor.execute(command, end_list)
            self.__db_connection.commit()
            return True

        except (AssertionError, sqlite3.OperationalError) as e:
            print(e)
            return False

    def get_user_password(self, user_info) -> str|None:
        """

        :param user_info:
        :return:
        """
        command = "SELECT password FROM users WHERE firstname=? AND lastname=? AND door_number=?"
        res = self.__cursor.execute(command, user_info).fetchall()
        if res[0][0]:
            return res[0][0]
        else:
            return None

    def get_db_password_list(self) -> list:
        """
        Get a list of all passwords in the database
        :return:
        """
        pass_list = list()
        command = "SELECT password FROM users"
        res = self.__cursor.execute(command).fetchall()
        for password_col in res:
            pass_list.append(password_col[0])
        return pass_list

    def get_user_qr_img_path(self, user_info) -> str|None:
        """
        Get the path of the saved qrcode
        :param user_info:
        :return: str path if path found else None
        """
        command = "SELECT qr_code FROM users WHERE firstname=? AND lastname=? AND door_number=?"
        res = self.__cursor.execute(command, user_info).fetchall()
        if res[0][0]:
            return res[0][0]
        else:
            return None

    def is_in_db(self, user_info:list)-> bool:
        """
        Check if the user is in the database
        :param user_info:
        :return: bool
        """

        command = "SELECT * FROM users WHERE firstname=? AND lastname=? AND door_number=?"
        res = self.__cursor.execute(command, user_info).fetchall()
        print(f"User infos: {user_info}, result: {res}")
        if len(res)>0:
            return True
        else:
            return False







