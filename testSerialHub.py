import serial
import binascii

if __name__ == "__main__":

    with serial.Serial('/dev/ttyUSB0') as ser:
        print(ser.name)
        command = "0200300335"
        print(f"Send command to hub: {command}")
        print(f"encoded command: {command.encode('utf-8')}")
        ser.write(command.encode('utf-8'))
        ser.flush()
        response = binascii.b2a_hex(ser.read(9))
        print(f"Response Hub: {response}")
