import serial
import names
import os
import time
import datetime

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
def create_files_by_response_list(response_list):
    # test print (what we have in one response over http(s))
    # print(response_list)

    if(len(response_list) == 0 or response_list[0] == 'END_OF_THE_FILE\n'):
        print('ERROR! YOU TRY TO CREATE FILE FROM EMPTY STRING')
        return

    # satellites_folder_name = 'satellites'
    # passes_info_folder_name = 'passes_full'
    # passes_input_folder_name = 'commands'

    # if not os.path.isdir(names.satellites_dir_path):
    #     os.mkdir(names.satellites_dir_path)
    # responses_dir_path = './' + names.satellites_dir + '/' + names.responses_dir_name
    # if not os.path.isdir(names.responses_dir_path):
    #     os.mkdir(names.responses_dir_path)
    # # commands_dir_path = './' + names.satellites_dir + '/' + names.commands_dir_name
    # if not os.path.isdir(names.commands_dir_path):
    #     os.mkdir(names.commands_dir_path)

    # test print
    # print(response_list)
    # time.sleep(5)

    string_with_sat_id = response_list[0]
    string_with_name   = response_list[1]
    sat_id             = string_with_sat_id.split(' ', 1)[1].strip('\n')
    sat_name           = string_with_name.split(' ', 1)[1].strip('\n')

    command_file_path      = names.commands_dir_path  + '/' + str(sat_id) + names.command_postfix      + '.txt'
    command_temp_file_path = names.commands_dir_path  + '/' + str(sat_id) + names.command_temp_postfix + '.txt'
    response_file_path     = names.responses_dir_path + '/' + str(sat_id) + names.response_postfix     + '.txt'
    # passes_file_path = passes_info_path + '/' + str(sat_name) + '.txt'

    # if no file 
    if not os.path.isfile(command_file_path):
        with open(command_file_path, 'w') as file:
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

    with open(command_file_path, 'r') as default_file, open(command_temp_file_path, 'w+') as temp_file:
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
        for element in response_list: 
            if element[0] == '#':
                # if date_pass_counter < 9:
                #     temp_file.write(element[0] + '0' + element[1:])
                #     date_pass_counter += 1
                # else:
                temp_file.write(element)

    os.remove(command_file_path)
    os.rename(command_temp_file_path, command_file_path)

    print('file %s was created with size: %i bytes'%(command_file_path, os.path.getsize(command_file_path)))

    with open(response_file_path, 'w') as file:
        for line in response_list:
            file.write(line)

    print('file %s was created with size: %i bytes'%(response_file_path, os.path.getsize(response_file_path)))

def create_responses_board_files(response_list, board_data_dir_path):
    # now_time = datetime.datetime.now()
    # formatted_now_time = now_time.strftime('%Y-%m-%d_%H:%M:%S')
    # # print(formatted_now_time)
    # last_time_updated_postfix = '_updated_%s'%(formatted_now_time)
    # # print(last_time_updated_postfix)

    # board_data_dir = names.board_data_dir_prefix + last_time_updated_postfix 
    # if not os.path.isdir(board_data_dir):
    #     os.mkdir(board_data_dir)

    # responses_dir_path = './satellites/passes_from_board'
    # responses_board_dir_path = './' + names.satellites_dir_name + '/' + names.responses_dir_name + names.last_time_updated_postfix 
    # responses_board_dir_path = names.responses_board_dir_path + last_time_updated_postfix 

    responses_board_dir_path = '%s/%s'%(
        board_data_dir_path,
        names.responses_board_dir_name
    )


    if not os.path.isdir(responses_board_dir_path):
        os.mkdir(responses_board_dir_path)

    sat_id = response_list[0].split(' ', 1)[1].strip('\n')

    # test
    response_board_file_path = '%s/%s%s.txt'%(
        responses_board_dir_path,
        sat_id,
        names.response_board_postfix,
    )
    
    # response_board_file_path = names.responses_board_dir_path + '/' + sat_id + names.response_board_postfix + last_time_updated_postfix + '.txt'

    with open(response_board_file_path, 'w') as file:
        for line in response_list:
            file.write(line)
    

def create_commands_board_files(command_list, board_data_dir_path):
    # now_time = datetime.datetime.now()
    # formatted_now_time = now_time.strftime('%Y-%m-%d_%H:%M:%S')
    # # print(formatted_now_time)
    # last_time_updated_postfix = '_updated_%s'%(formatted_now_time)
    # # print(last_time_updated_postfix)

    # shedules_folder = './satellites/shedules_from_board'
    # commands_dir_path = './' + names.satellites_dir_name + '/' + names.commands_board_dir_name + names.last_time_updated_postfix

    # commands_board_dir_path = names.commands_board_dir_path + last_time_updated_postfix 
    commands_board_dir_path = '%s/%s'%(
        board_data_dir_path,
        names.commands_board_dir_name
    )

    if not os.path.isdir(commands_board_dir_path):
        os.mkdir(commands_board_dir_path)
    
    sat_id = command_list[0].split('=', 1)[1].strip('\n')

    # test
    command_board_file_path = '%s/%s%s.txt'%(
        commands_board_dir_path,
        sat_id,
        names.command_board_postfix
    )
    # command_file_path = names.commands_board_dir_path + '/' + sat_id + names.postfix + '.txt'

    with open(command_board_file_path, 'w') as file:
        for line in command_list:
            # when 'pl' found - add '\n' after this line (just for visual)
            if line[0] + line[1] == 'pl': 
                file.write(line)
                file.write('\n')
                continue
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
    if not decoded_satellite_list:
        print('В spiffs отсутствуют данные!')
        return

    now_time = datetime.datetime.now()
    formatted_now_time = now_time.strftime(names.time_format)
    # print(formatted_now_time)
    last_time_updated_postfix = '_updated_%s'%(formatted_now_time)
    # print(last_time_updated_postfix)

    board_data_dir_path = '%s/%s%s'%(
        names.satellites_dir_path,
        names.board_data_dir_prefix,
        last_time_updated_postfix
    )

    if not os.path.isdir(board_data_dir_path):
        os.mkdir(board_data_dir_path)

    satellite_list = []
    # create files for each satellite in input_list :
    start_index = 0
    for element_index in range(0, len(decoded_satellite_list)):
        if (decoded_satellite_list[element_index] == 'END_OF_THE_FILE\n'): 
            last_index = element_index
            satellite_list = decoded_satellite_list[start_index:last_index]

            print(satellite_list[0].split('=')[0], end='\n')

            if satellite_list[0].split('=')[0] == 'norad':
                create_commands_board_files(satellite_list, board_data_dir_path)
            else:
                create_responses_board_files(satellite_list, board_data_dir_path)
            start_index = last_index + 1
    print('List parsed, files created')