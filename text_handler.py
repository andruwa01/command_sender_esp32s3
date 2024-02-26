import serial
import os
import time

def initialize_port(timeout_s):
    port_instance = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    bytesize=8,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_EVEN,
    timeout=timeout_s,
    )

    port_instance.reset_input_buffer()
    port_instance.reset_output_buffer()

    return port_instance

# creating file (and corresponding directories), if it does not exist and write to it
def create_file_by_list(list_for_file):

    if(len(list_for_file) == 0 or list_for_file[0] == 'END_OF_THE_FILE\n'):
        print('ERROR! YOU TRY TO CREATE FILE FROM EMPTY STRING')
        return

    satellites_folder_name = 'satellites'
    passes_info_folder_name = 'passes_full'
    passes_input_folder_name = 'passes_user_input'

    # check if folder /satellites exists else create one
    if not os.path.isdir(satellites_folder_name):
        os.mkdir(satellites_folder_name)

    # check if folder ./satellites/passes_data 
    passes_info_path = './' + satellites_folder_name + '/' + passes_info_folder_name
    if not os.path.isdir(passes_info_path):
        os.mkdir(passes_info_path)

    # check if folder ./satellites/user_input_data
    passes_input_path = './' + satellites_folder_name + '/' + passes_input_folder_name
    if not os.path.isdir(passes_input_path):
        os.mkdir(passes_input_path)

    string_with_name = list_for_file[1]
    string_witd_sat_id = list_for_file[0]

    sat_name = string_with_name.split(' ', 1)[1].strip('\n')
    sat_id = string_witd_sat_id.split(' ', 1)[1].strip('\n')

    commands_default_file_path = passes_input_path + '/' + str(sat_name) + '_commands' + '.txt'
    temp_file_path = passes_input_path + '/' + str(sat_name) + '_commands_temp' + '.txt'

    passes_file_path = passes_info_path + '/' + str(sat_name) + '.txt'

    # if no file 
    if(not os.path.isfile(commands_default_file_path)):
        with open(commands_default_file_path, 'w') as file:
            file.write('name=%s\n'%(sat_name))
            file.write('norad=%s\n'%(sat_id))
            file.write('freq=\n')
            file.write('bw=\n')
            file.write('sf=\n')
            file.write('cr=\n')
            file.write('sw=\n')
            file.write('pl=\n')
    
    # buffer for lines with values to save 
    default_lines = []

    # buffer for values to compare with
    template_values = ['name', 'norad', 'freq', 'bw', 'sf', 'cr', 'sw', 'pl', '']

    with open(commands_default_file_path, 'r') as default_file, open(temp_file_path, 'w+') as temp_file:
        # save user input values to list
        for line in default_file:

            line_divided = line.split('=')

            for value in template_values:
                if(line_divided[0] == value): 
                    default_lines.append(line)
        
        # write default lines (with suer input info)
        temp_file.writelines(default_lines)

        # edd empty line delimiter between next data line symbols (as need)
        temp_file.write('\n')
       
        # write info about time of passes
        date_pass_counter = 0
        for element in list_for_file: 
            if element[0] == '#':
                if date_pass_counter < 9:
                    temp_file.write(element[0] + '0' + element[1:])
                    date_pass_counter += 1
                else:
                    temp_file.write(element)

    os.remove(commands_default_file_path)
    os.rename(temp_file_path, commands_default_file_path)

    print('%s was created with size: %i bytes'%(commands_default_file_path, os.path.getsize(commands_default_file_path)))

    with open(passes_file_path, 'w') as file:
        for line in list_for_file:
            file.write(line)

    print('%s was created with size: %i bytes'%(passes_file_path, os.path.getsize(passes_file_path)))


def get_decoded_list_of_satellites_data(serial_port): 
    print('Start getting list of satellites data')

    input_list_binary = []
    input_list_decoded = []

    if(serial_port.is_open):
        input_list_binary = serial_port.readlines()
        
        for element in input_list_binary:
            input_list_decoded.append(element.decode())

        print('list from uart: %s\n'%input_list_decoded)

        print('Got list from spiffs')
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
            create_file_by_list(satellite_list)
            start_index = last_index + 1
    print('List parsed, files created')