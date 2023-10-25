import serial
import argparse


def send_command2Hub(hub_command:str) -> list:
    """
    :param hub_command: The string must contain two hexadecimal digits per byte,
    with ASCII whitespace being ignored.
    :return: A list, which contains the door's status
    """
    with serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=2,
                       rtscts=True,
                       #dsrdtr=True
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
    if position:
        assert isinstance(position, int) and position in range(1, 17), "door number must be a integer between 1 and 16"

    STX = "02"
    ADDR = "00" if not position else "0" + hex(position-1)[-1]
    CMD = "31" if args.open else "30"
    ETX = "03"
    SUM = hex(int(STX, 16) + int(ADDR, 16) + int(CMD, 16) + int(ETX, 16))[-2:]
    status_command = "0200300335"
    open_command = "0200310336"
    command = STX + ADDR + CMD + ETX + SUM #status_command if args.status else open_command
    print(f"command: {command}")




