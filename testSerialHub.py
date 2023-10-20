import serial
import binascii

if __name__ == "__main__":

    with serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=2) as ser:
        print(ser.name)
        command = b"0200300335"
        # binascii.unhexlify("0200300335")
        print(f"Send command to hub: {binascii.hexlify(command)}")
        print(f"encoded command: {command}")
        ser.write(command)
        ser.flush()
        response = binascii.hexlify(ser.read(9))
        print(f"Response Hub: {response}")
