import serial
import binascii

if __name__ == "__main__":

    STX = 0x02
    ADDR = 0x00
    CMD = 0x30
    ETX = 0x03
    SUM = 0x35
    #check_SUM = hex(STX + ADDR + CMD + ETX)[-2:]
    status_command = "0200300335" #serial.to_bytes([STX, ADDR, CMD, ETX, SUM])
    encoded_command = bytes.fromhex(status_command)
    print(f"encoded_command: {encoded_command}")
    sequences = encoded_command.hex("-").split("-")
    # a = hex(int(0x35))

    with serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=2) as ser:
        print(ser.name)
        ser.write(bytes.fromhex(status_command))
        ser.flush()
        response = ser.read(9)
        print(f"Response Hub: {response}")
