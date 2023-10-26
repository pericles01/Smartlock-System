import serial
import argparse
import json


def send_command2Hub(hub_command:str, c_type:str ) -> tuple|None:
    """
    :param hub_command: The string must contain two hexadecimal digits per byte,
    with ASCII whitespace being ignored.
    :return: A tuple of length 2 containing the door's status in the form door_status = [DATA1, DATA2]
    DATA1 & DATA2 are hexadecimal status of the doors. DATA1 represents the status from door 1 to door 8
    and DATA2 represents the status from door 9 to door 16
    """
    with serial.Serial('/dev/ttyUSB0', baudrate=19200, timeout=2,
                       rtscts=True,
                       dsrdtr=True,
                       ) as ser:
        print(f"! send {c_type} command: {hub_command} to Hub device: {ser.name}")
        print(' ')
        encoded_command = bytes.fromhex(hub_command)
        # print(f"encoded_command: {encoded_command}")
        ser.write(encoded_command)
        response = ser.read(9) # read 9 bytes from serial connection

    if c_type == "status":
        # print(f"Response Hub: {response}")
        if response:
            sequences = response.hex("-").split("-") # list of bytes sequences
            # print(f"! Response Hub hex sequence: {sequences}")
            assert len(sequences) == 9, "unknown response's length"
            DATA1, DATA2 = sequences[3:5]
            int_DATA1 = int(DATA1, 16)
            int_DATA2 = int(DATA2, 16)

            # print("* Door Status")
            # print(f"! Data1: {bin(int_DATA1)}")
            # print(f"! Data2: {bin(int_DATA2)}")
            return int_DATA1, int_DATA2
        else:
            raise ValueError("No response from Hub")
    else:
        print("-------------------------------------")
        print("! Check door status after opening...")
        print("-------------------------------------")
        print(' ')
        return send_command2Hub("0200300335", "status")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--open", action="store_true", help="send open command to Hub")
    parser.add_argument("-p", "--position", type=int, default=None, help="enter the position of the door you want to open")
    args = parser.parse_args()
    position = args.position
    pos2addr = dict()
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
        data1, data2 = send_command2Hub(command, command_type)
    except (ValueError, AssertionError):
        # try again
        data1, data2 = send_command2Hub(command, command_type)
    
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
        




