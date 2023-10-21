import serial
import argparse


def send_command2Hub(hub_command:str) -> list:
    """
    :param hub_command: The string must contain two hexadecimal digits per byte,
    with ASCII whitespace being ignored.
    :return: A list, which contains the door's status
    """
    with serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=2) as ser:
        print(f"send command: {hub_command} to Hub device: {ser.name}")
        encoded_command = bytes.fromhex(hub_command)
        print(f"encoded_command: {encoded_command}")
        ser.write(encoded_command)
        #ser.flush()
        while ser.in_waiting():
            response = ser.read() # read 9 bytes from serial connection
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
    parser.add_argument("-s", "--status", action="store_true", help="send status command to Hub")
    args = parser.parse_args()
    status_command = "0200300335"
    open_command = "0200310336"
    command = status_command if args.status else open_command
    try:
        status = send_command2Hub(command)
    except (ValueError, AssertionError):
        # try again
        status = send_command2Hub(command)

    print(''.join(status))

    # test_response = '02003500000000033A'
    # encoded_response = bytes.fromhex(test_response)
    #
    # sum = hex(0x02 + 0x00 + 0x31 + 0x03)
    # seq = encoded_response.hex("-").split("-")
    # length = len(seq)
    # door_data = seq[3:5]
    # str_data = ''.join(door_data)




