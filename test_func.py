import pandas as pd
import json
import os
from manage.Database import Database

if __name__ == '__main__':
    db = Database()
    db.db_init()
    usecols = ["firstname", "lastname", "rfid", "door number", "description"]
    df = pd.read_csv("ressources/user-list.csv", usecols=usecols)
    df.sort_values(by=['firstname'], ascending=True, inplace=True)
    users_data = df.to_numpy()
    for item in users_data:
        #text = f"User: {item[0]} | {item[1]} | {item[2]} | {item[3]}"
        #split = text.split("|")
        item[4] = item[4] if str(item[4]) != 'nan' else 'No Description'

    # add users coming from a .csv file. Existing datas must be avoided
    # if not db.add_users(users_data.tolist()):
    #     print("Insertion not successful")

    # add a single user, coming from a form
    # user = [('John', 'Wick', 9150, 13, 'No Description')]
    # if not db.add_users(user):
    #     print("Insertion not successful")

    # Update a user's infos
    # current_user_data = ['John', 'Wick', 9150]
    # new_user_data = ['John', 'Wick', 9150, 15, 'Update Test']
    # db.update_user_basic_infos(current_user_data, new_user_data)

    # Delete a user
    user2delete = ('John', 'Wick', 9150)
    db.delete_user(user2delete)

    content = db.show_users_table()
    print(f"Table content length: {len(content)}")
    print("Content:")
    print(f"{content}")


# path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
# with open(path, "r") as f:
#     door_data = json.load(f)
#     size = len(door_data)
#     print(size)



