# import serial
#
# while 1:
#     with serial.Serial('/dev/ttyUSB1', baudrate=9600, timeout=2,
#                         rtscts=True,
#                         dsrdtr=True
#                         ) as ser:
#         response = ser.read()
#         print(f"Response Reader: {response.hex()}")
#         if response:
#             break

import sys
import os

while 1:
    # Get the last line of the previous code
    last_line = sys.stdin.readline().strip()
    #os.system('clear')
    # Print the last line of the previous code
    print(f"Received data: {last_line}")
