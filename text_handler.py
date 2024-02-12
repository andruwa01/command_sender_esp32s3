import time
import serial
import os

def initialize_port(timeout_s):
    port_instance = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    bytesize=8,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_EVEN,
    timeout=timeout_s,
    )
    return port_instance

# creating file, if it does not exist and write to it
def create_file_by_list(list_for_file):
    if(len(list_for_file) == 0 or list_for_file[0] == 'END_OF_THE_FILE\n'):
        print('ERROR! YOU TRY TO CREATE FILE FROM EMPTY STRING')
        return
    string_with_name = list_for_file[1]
    sat_name = string_with_name.split(' ', 1)[1].strip('\n')
    file_name = './satellites/' + str(sat_name) + '.txt'
    with open(file_name, 'w') as file:
        for line in list_for_file:
            file.write(line)
    print('%s was created with size: %i bytes' %(file_name, os.path.getsize(file_name)))

def get_decoded_list_of_satellites_data(serial_port): 
    print('Start getting list of satellites data')

    input_list_binary = []
    input_list_decoded = []

    if(serial_port.is_open):
        input_list_binary = serial_port.readlines()
        
        for element in input_list_binary:
            input_list_decoded.append(element.decode())

        # print(input_list_decoded)
        print('Get list via HTTP')
        return input_list_decoded
    else:
        print("WARNING! Port IS NOT opened or no data in RX (input) buffer")
        return


def parse_list_create_files(decoded_satellite_list):
    satellite_list = []
    # create files for each satellite in input_list :
    start_index = 0
    for element_index in range(0, len(decoded_satellite_list)):
        if (decoded_satellite_list[element_index] == 'END_OF_THE_FILE\n'): 
            last_index = element_index
            satellite_list = decoded_satellite_list[start_index:last_index]
            # print(satellite_list)
            create_file_by_list(satellite_list)
            start_index = last_index + 1
    print('List parsed, files created')