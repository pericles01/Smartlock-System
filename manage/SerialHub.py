import time
import serial

STX = "02"
ETX = "03"
class SerialHub():
    def __init__(self):
        print("Starting serial connection...")

    def _compute_command(self, hub_addr, hub_cmd):
        SUM = hex(int(STX, 16) + int(hub_addr, 16) + int(hub_cmd, 16) + int(ETX, 16))[-2:]
        return STX + hub_addr + hub_cmd + ETX + SUM

    def send_status_command(self, hub_addr:str ="00"):
        #status_command = "0200300335"
        hub_cmd = "30"
        command = self._compute_command(hub_addr, hub_cmd)

        return self._send_command2Hub(command, "status")

    def send_open_command(self, door_pos:int):
        assert isinstance(door_pos, int) and door_pos in range(1, 17, 1), \
            f"door position must be an integer from 1 to 16, got {door_pos}"
        hub_cmd = "31"
        hub_addr = "0" + hex(door_pos-1)[-1]
        command = self._compute_command(hub_addr, hub_cmd)

        return self._send_command2Hub(command, "open")

    def _send_command2Hub(self, hub_command:str, c_type:str ) -> dict[str, str]|bool:
        """
        :param hub_command: The string must contain two hexadecimal digits per byte,
        with ASCII whitespace being ignored.
        :param c_type: type of the command to send. Options ["status", "open"]
        :return: list of doors`status for a status command or true by successful open command
        """
        with serial.Serial('/dev/ttyUSB0', baudrate=19200, timeout=2,
                           rtscts=True,
                           dsrdtr=True,
                           ) as ser:
            print(f"! send {c_type} command: {hub_command} to Hub device: {ser.name}")
            print(' ')
            encoded_command = bytes.fromhex(hub_command)
            ser.write(encoded_command)
            response = ser.read(9) # read 9 bytes from serial connection
        if c_type == "status":
            if response:
                sequences = response.hex("-").split("-") # list of bytes sequences
                assert len(sequences) == 9, "unknown response's length"
                DATA1, DATA2 = sequences[3:5]

                int_DATA1 = int(DATA1, 16)
                int_DATA2 = int(DATA2, 16)
                door_pos_info = dict()
                cnt = 0
                for i in range(16):
                    pos = i + 1
                    door_pos = str(pos)
                    if door_pos not in door_pos_info.keys():
                        door_pos_info[door_pos] = ""
                    if pos < 9:  # 0 to 8
                        door_pos_info[door_pos] = "open" if (int_DATA1 >> i) & 1 == 0 else "closed"
                    else:  # 9 to 16
                        door_pos_info[door_pos] = "open" if (int_DATA2 >> cnt) & 1 == 0 else "closed"
                        cnt += 1

                return door_pos_info
            else:
                raise ValueError("No response from Hub")
        else:
            return True

    def open_all_doors(self)-> bool | tuple[bool, str]:
        cnt = 0
        try:
            for i in range(16):
                self.send_open_command(i + 1)
                time.sleep(1)
        except serial.SerialException as e:
            return False, "Please make sure that the Hub device is connected correctly"

        # verify status of all doors
        doors_info = self.send_status_command()
        for k in doors_info.keys():
            if doors_info[k] == "closed":
                cnt += 1
        if not cnt:
            # if one door is still closed, try again
            self.open_all_doors()

        return True

    def get_position_connected_doors(self, door_info:dict) -> list[int]:
        """
        :param door_info: dict of the door infos
        :return: list of the position of the closed doors. Need for mapping in order to access every door respectively
        """
        #door_info = self.send_status_command()
        list_position = list()
        for key in door_info.keys():
            if door_info[key] == "closed":
                list_position.append(int(key))
        return list_position

