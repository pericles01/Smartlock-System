import pandas as pd
import json
import os

usecols = ["firstname", "lastname", "rfid", "door number", "description"]
df = pd.read_csv("ressources/user-list.csv", usecols=usecols)
df.sort_values(by=['firstname'], ascending=True, inplace=True)
np_data = df.to_numpy()
for item in np_data:
    text = f"User: {item[0]} | {item[1]} | {item[2]} | {item[3]}"
    split = text.split("|")
    isEmpty = str(item[4]) != 'nan'
    print(f"| {item[4] if str(item[4]) != 'nan' else ''}")
    print(" ")


path = os.path.join(os.getcwd(), ".cache/door_pos_info.json")
with open(path, "r") as f:
    door_data = json.load(f)
    size = len(door_data)
    print(size)



