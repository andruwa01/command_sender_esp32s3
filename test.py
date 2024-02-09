import serial 
import os

serial_port = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    bytesize=8,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_EVEN,
    timeout=60,
)

print('Start getting list of satellites data')

lines = serial_port.readlines()
print(lines)