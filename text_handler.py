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

# creating file (and corresponding directories) by list of data in special format, if it does not exist and write to it
# TODO rename file to create_command_file_by_list
def create_shedule_pass_files_by_pass_list(list_for_file):
    if(len(list_for_file) == 0 or list_for_file[0] == 'END_OF_THE_FILE\n'):
        print('ERROR! YOU TRY TO CREATE FILE FROM EMPTY STRING')
        return

    satellites_folder_name = 'satellites'
    # passes_info_folder_name = 'passes_full'
    passes_input_folder_name = 'params_shedule'
    # check if folder /satellites exists else create one
    if not os.path.isdir(satellites_folder_name):
        os.mkdir(satellites_folder_name)
    # check if folder ./satellites/passes_data 
    # passes_info_path = './' + satellites_folder_name + '/' + passes_info_folder_name
    # if not os.path.isdir(passes_info_path):
    #     os.mkdir(passes_info_path)
    # check if folder ./satellites/user_input_data
    passes_input_path = './' + satellites_folder_name + '/' + passes_input_folder_name
    if not os.path.isdir(passes_input_path):
        os.mkdir(passes_input_path)

    string_witd_sat_id = list_for_file[0]
    string_with_name = list_for_file[1]
    sat_id = string_witd_sat_id.split(' ', 1)[1].strip('\n')
    sat_name = string_with_name.split(' ', 1)[1].strip('\n')

    user_input_forecast_path = passes_input_path + '/' + str(sat_id) + '_commands' + '.txt'
    temp_file_path = passes_input_path + '/' + str(sat_id) + '_commands_temp' + '.txt'
    # passes_file_path = passes_info_path + '/' + str(sat_name) + '.txt'

    # if no file 
    if(not os.path.isfile(user_input_forecast_path)):
        with open(user_input_forecast_path, 'w') as file:
            file.write('norad=%s\n'%(sat_id))
            file.write('name=%s\n'%(sat_name))
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

    with open(user_input_forecast_path, 'r') as default_file, open(temp_file_path, 'w+') as temp_file:
        # save user input values to list
        for line in default_file:

            line_divided = line.split('=')

            for value in template_values:
                if(line_divided[0] == value): 
                    default_lines.append(line)
        
        # write default lines (with suer input info)
        temp_file.writelines(default_lines)

        # edd empty line delimiter between next data line symbols (as need by task)
        temp_file.write('\n')
       
        # write info about time of passes
        # date_pass_counter = 0
        for element in list_for_file: 
            if element[0] == '#':
                # if date_pass_counter < 9:
                #     temp_file.write(element[0] + '0' + element[1:])
                #     date_pass_counter += 1
                # else:
                temp_file.write(element)

    os.remove(user_input_forecast_path)
    os.rename(temp_file_path, user_input_forecast_path)

    print('file %s was created with size: %i bytes\n'%(user_input_forecast_path, os.path.getsize(user_input_forecast_path)))

    # with open(passes_file_path, 'w') as file:
    #     for line in list_for_file:
    #         file.write(line)

    # print('%s was created with size: %i bytes'%(passes_file_path, os.path.getsize(passes_file_path)))

def create_passes_files(passes_list):
    passes_folder = './satellites/passes_from_board'
    if not os.path.isdir(passes_folder):
        os.mkdir(passes_folder)

    sat_id = passes_list[0].split(' ', 1)[1].strip('\n')
    
    passes_file_path = passes_folder + '/' + sat_id + '_board_pass' + '.txt'

    with open(passes_file_path, 'w') as file:
        for line in passes_list:
            file.write(line)
    

def create_shedule_files(shedules_list):
    shedules_folder = './satellites/shedules_from_board'
    if not os.path.isdir(shedules_folder):
        os.mkdir(shedules_folder)
    
    sat_id = shedules_list[0].split('=', 1)[1].strip('\n')

    shedules_file_path = shedules_folder + '/' + sat_id + '_board_shedule' + '.txt'

    with open(shedules_file_path, 'w') as file:
        for line in shedules_list:
            file.write(line)


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
            create_shedule_pass_files_by_pass_list(satellite_list)
            start_index = last_index + 1
    print('List parsed, files created')