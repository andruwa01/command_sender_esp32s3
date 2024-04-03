import datetime
import names
import os

def parse_data_files_string_create_files(responses_string):
    if not responses_string:
        print(names.text_border_top)
        print('В SPIFFS отсутствуют какие-либо данные')
        print(names.text_border_bottom)
        return
    
    responses_string_list = responses_string.split('\n')

    now_time = datetime.datetime.now()
    formatted_now_time = now_time.strftime(names.time_format)
    last_time_updated_postfix = '_updated_%s'%(formatted_now_time)

    board_data_dir_path = '%s/%s%s'%(
        names.satellites_dir_path,
        names.board_data_dir_prefix,
        last_time_updated_postfix
    )

    if not os.path.isdir(board_data_dir_path):
        os.mkdir(board_data_dir_path)

    one_data_list = []

    index_begin_file = 0
    for element_index in range(0, len(responses_string_list)):
        if (responses_string_list[element_index] == 'END_FILE'): 
            index_end_file = element_index
            one_data_list = responses_string_list[index_begin_file:index_end_file]

            print(one_data_list[0].split('=')[0], end='\n')

            if one_data_list[0].split('=')[0] == 'norad':
                create_command_board_files(one_data_list, board_data_dir_path)
            else:
                create_response_board_files(one_data_list, board_data_dir_path)

            index_begin_file = index_end_file + 1
    print('List parsed, files created')

def create_command_board_files(data_list_command, board_data_dir_path):
    commands_board_dir_path = '%s/%s'%(
        board_data_dir_path,
        names.commands_board_dir_name
    )

    if not os.path.isdir(commands_board_dir_path):
        os.mkdir(commands_board_dir_path)
    
    sat_id = data_list_command[0].split('=', 1)[1]

    command_board_file_path_txt = '%s/%s%s.txt'%(
        commands_board_dir_path,
        sat_id,
        names.command_board_postfix
    )

    with open(command_board_file_path_txt, 'w') as file:
        for line in data_list_command:
            # when 'pl' found - add '\n' after this line (just for visual)
            if line[0] + line[1] == 'pl': 
                file.write(line + '\n')
                file.write('\n')
                continue
            file.write(line + '\n')


def create_response_board_files(data_list_response, board_data_dir_path):
    responses_board_dir_path = '%s/%s'%(
        board_data_dir_path,
        names.responses_board_dir_name
    )

    if not os.path.isdir(responses_board_dir_path):
        os.mkdir(responses_board_dir_path)

    sat_id = data_list_response[0].split(' ', 1)[1]
    response_board_file_path_txt = '%s/%s%s.txt'%(
        responses_board_dir_path,
        sat_id,
        names.response_board_postfix,
    )
    with open(response_board_file_path_txt, 'w') as file:
        for line in data_list_response:
            file.write(line + '\n')

def create_files_by_response_list(response_list):
    # test print (what we have in one response over http(s))
    # print(response_list)

    if(len(response_list) == 0 or response_list[0] == 'END_OF_THE_FILE\n'):
        print('ERROR! YOU TRY TO CREATE FILE FROM EMPTY STRING')
        return

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

