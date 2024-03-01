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

request_options_file_path = './%s/%s.txt'%(
    satellites_dir_name,
    request_options_file_name
)

# satellites_dir_path       = './' + satellites_dir_name  
satellites_dir_path = './%s'%(satellites_dir_name)
# responses_dir_path  = './' + satellites_dir_name     + '/' + responses_dir_name
responses_dir_path = './%s/%s'%(
    satellites_dir_name,
    responses_dir_name
)
# commands_dir_path  = './' + satellites_dir_name     + '/' + commands_dir_name
commands_dir_path = './%s/%s'%(
    satellites_dir_name,
    commands_dir_name
)
# responses_board_dir_path = './' + satellites_dir_name     + '/' + responses_board_dir_name + last_time_updated_postfix 
# test
# responses_board_dir_path = './' + satellites_dir_name + '/' + responses_board_dir_name
responses_board_dir_path = './%s/%s'%(
    satellites_dir_name,
    responses_board_dir_name
)
# commands_board_dir_path  = './' + commands_board_dir_name + '/' + commands_board_dir_name  + last_time_updated_postfix
# test
# commands_board_dir_path = './' + satellites_dir_name + '/' + commands_board_dir_name
commands_board_dir_path = './%s/%s'%(
    satellites_dir_name,
    commands_board_dir_name
)