import serial
import argparse
import json

def send_command2Hub(hub_command:str) -> list:
    """
    :param hub_command: The string must contain two hexadecimal digits per byte,
    with ASCII whitespace being ignored.
    :return: A list, which contains the door's status
    """
    with serial.Serial('/dev/ttyUSB0', baudrate=19200, timeout=2,
                       rtscts=True,
                       dsrdtr=True
                       ) as ser:
        print(f"send command: {hub_command} to Hub device: {ser.name}")
        encoded_command = bytes.fromhex(hub_command)
        print(f"encoded_command: {encoded_command}")
        ser.write(encoded_command)
        #ser.flush()
        response = ser.read(9) # read 9 bytes from serial connection
        print(f"Response Hub: {response}")

    if response:
        sequences = response.hex("-").split("-") # list of bytes sequences
        assert len(sequences) == 9, "unknown response's length"
        door_status = sequences[3:5]
        print(f"Door Status: {door_status}")
        return door_status
    else:
        raise ValueError("No response from Hub")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--open", action="store_true", help="send status command to Hub")
    parser.add_argument("-pos", "--position", type=int, default=None, help="send status command to Hub")
    args = parser.parse_args()

    position = args.position
    if args.open:
        assert position, "Please specify the number between 1 and 16 of the door to open"
        if position:
            assert isinstance(position, int) and position in range(1, 17, 1), "door position must be an integer from 1 to 16"

    # status_command = "0200300335"
    # open_command = "0200310336"
    STX = "02"
    ADDR = "00" if not position else "0" + hex(position-1)[-1]
    CMD = "31" if args.open else "30"
    ETX = "03"
    SUM = hex(int(STX, 16) + int(ADDR, 16) + int(CMD, 16) + int(ETX, 16))[-2:]

    command = STX + ADDR + CMD + ETX + SUM
    command_type = "open" if args.open else "status"

    try:
        data1, data2 = send_command2Hub(command)
    except (ValueError, AssertionError):
        # try again
        data1, data2 = send_command2Hub(command)

    if data1 is not None and data2 is not None:
        door_info = dict()
        cnt=0
        for i in range(16):
            pos = i+1
            door_pos = "door " + str(pos)
            if door_pos not in door_info.keys():
                    door_info[door_pos] = ""

            if pos<9: #0 to 8
                door_info[door_pos] = "open" if (data1 >> i) & 1 == 0 else "closed"
            else: # 9 to 16
                door_info[door_pos] = "open" if (data2 >> cnt) & 1 == 0 else "closed"
                cnt+=1

        with open("doors_info.json", mode='w') as f:
            json.dump(door_info, f, indent=2)

        print("-----------* Doors info *-------------")
        print(door_info)
        print("-------------------------------------")
        print(' ')
        




