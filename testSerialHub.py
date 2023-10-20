import serial
import binascii

if __name__ == "__main__":

    STX = 0x02
    ADDR = 0x00
    CMD = 0x30
    ETX = 0x03

    SUM = hex(STX + ADDR + CMD + ETX)[:-2]

    with serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=2) as ser:
        print(ser.name)
        command = b'\x02\x00\x30\x03\x35'
        #print(f"Send command to hub: {binascii.hexlify(command)}")
        print(f"encoded command: {command}")
        ser.write(command)
        ser.flush()
        response = ser.read(9)
        print(f"Response Hub: {response}")
