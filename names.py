import datetime
import os


now_time = datetime.datetime.now()
formatted_now_time = now_time.strftime('%Y-%m-%d_%H:%M:%S')
# print(formatted_now_time)
last_time_updated_postfix = '_updated_%s'%(formatted_now_time)
# print(last_time_updated_postfix)

satellites_dir_name      = 'satellites_info'
responses_dir_name       = 'responses' 
commands_dir_name        = 'commands'  
responses_board_dir_name = 'board_responses' 
commands_board_dir_name  = 'board_commands'

board_data_dir_prefix    = 'board_data'

response_postfix         = '_response'
command_postfix          = '_command'
command_temp_postfix     = '_command_temp'
response_board_postfix   = '_board_response' 
command_board_postfix    = '_board_command'

request_options_file_name  = 'requests_input_options'
# request_input_options_file_path    = './' + satellites_dir_name + '/' + input_options_file_name + '.txt'  
# test

satellites_dir_local_path = './%s'%(satellites_dir_name)

# if not os.path.isdir(satellites_dir_local_path):
#     os.mkdir(satellites_dir_local_path)


satellites_dir_path = os.path.abspath(satellites_dir_local_path)

# request_options_file_path = ''
# responses_dir_path = ''
# commands_dir_path = ''
# responses_board_dir_path = ''
# commands_board_dir_path = ''

request_options_file_path = '%s/%s.txt'%(
    satellites_dir_path,
    request_options_file_name
)
responses_dir_path = '%s/%s'%(
    satellites_dir_path,
    responses_dir_name
)
commands_dir_path = '%s/%s'%(
    satellites_dir_path,
    commands_dir_name
)
responses_board_dir_path = './' + satellites_dir_name + '/' + responses_board_dir_name
responses_board_dir_path = '%s/%s'%(
    satellites_dir_path,
    responses_board_dir_name
)
commands_board_dir_path = '%s/%s'%(
    satellites_dir_path,
    commands_board_dir_name
)

if not os.path.isdir(satellites_dir_path):
    os.mkdir(satellites_dir_path)

if not os.path.isdir(responses_dir_path):
        os.mkdir(responses_dir_path)
    # commands_dir_path = './' + names.satellites_dir + '/' + names.commands_dir_name
if not os.path.isdir(commands_dir_path):
    os.mkdir(commands_dir_path)

if not os.path.exists(request_options_file_path):
    with open(request_options_file_path, 'w') as file:
        file.write('norbi=46494\n')
        file.write('2023-091t=57183\n')
        file.write('cstp-1.1=57202\n')
        file.write('cstp-1.2=57186\n')
        file.write('fees_sat=48082\n')

def update_names(request_options_file_name_new):
    if(request_options_file_name_new == ''):
        print('Недопустимое имя файла')
        return
    
    global request_options_file_name
    global request_options_file_path
    global responses_dir_path
    global commands_dir_path
    global responses_board_dir_path
    global commands_board_dir_path

    request_options_file_name = request_options_file_name_new 

    request_options_file_path = '%s/%s.txt'%(
        satellites_dir_path,
        request_options_file_name
    )
    responses_dir_path = '%s/%s'%(
        satellites_dir_path,
        responses_dir_name
    )
    commands_dir_path = '%s/%s'%(
        satellites_dir_path,
        commands_dir_name
    )
    responses_board_dir_path = './' + satellites_dir_name + '/' + responses_board_dir_name
    responses_board_dir_path = '%s/%s'%(
        satellites_dir_path,
        responses_board_dir_name
    )
    commands_board_dir_path = '%s/%s'%(
        satellites_dir_path,
        commands_board_dir_name
    )