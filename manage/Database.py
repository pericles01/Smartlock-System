import sqlite3
import os
from manage.User import User

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
                self.__cursor.execute("CREATE TABLE users(firstname, lastname, rfid_code, door_number, description, pin_code, qr_code, face_id)"
                )
                print("Table created")
            except sqlite3.OperationalError as e:
                print(e)

    def add_users(self, users_list: list) -> bool:
        """
        Method used to directly insert users' data coming from a .csv file or a form into the database users table
        :param users_list: users list in the form [[user1_firstname, user1_lastname, user1_rfid_code, user1_door_number, user1_description],
        ...]
        :return: bool: if the insertion was successful or not
        """
        try:
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

    def update_user_basic_infos(self, user_info:list, new_infos:list):
        """
        Method used to update user information such as firstname, lastname, rfid, door_number, description
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







