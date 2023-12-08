import serial

while 1:
    with serial.Serial('/dev/ttyUSB1', baudrate=9600, timeout=2,
                        rtscts=True,
                        dsrdtr=True
                        ) as ser:
        response = ser.read()
        print(f"Response Reader: {response.hex()}")
        if response:
            break