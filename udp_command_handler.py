import os
import time
import udp_text_handler
import udp_handler
import https_req
import names
from api_key import api_key

# time_to_wait_s = 5
# print('Program starts . . . wait %i seconds'%(time_to_wait_s))
# # wait 5 seconds before board will be ready for action
# time.sleep(time_to_wait_s)

# def init_command_handler(serial_port):
def init_command_handler():

    text_border_top =    '\n<==============================ВЫВОД=====================================>\n'
    text_border_bottom = '\n<============================КОНЕЦ ВЫВОДА================================>\n'

    event_board_finish_action      = 'python ready to send another command'
    event_board_get_command        = 'board get command' 

    command_help =                      'help'
    command_change_options_file =       'change options'
    command_update_shedule =            'update shedule'
    command_get_spiffs_data =           'spiffs get data'
    command_clear_spiffs =              'spiffs clear'
    command_clear_all_spiffs =          'spiffs clear all'    
    command_get_spiffs_info =           'spiffs get info' 
    command_load_data_to_spiffs =       'spiffs load'
    command_stop =                      'stop'
    command_test =                      'command test'

    names.update_names(names.request_options_file_name_txt)

    while True:
        # serial_port.reset_input_buffer()
        # serial_port.reset_output_buffer()

        print('\nТекущий файл настроек: %s'%(
            names.request_options_file_name_txt
        ))
        print("{:20s} -> показать список доступных команд".format(command_help))
        command = str(input("ВВЕДИТЕ КОМАНДУ: "))
        # command_binary = command.encode()

        if(command == command_help):
            print(text_border_top)

            print('СПИСОК ДОСТУПНЫХ КОМАНД:', end='\n\n')
            print("{:25s} -> тестовая команда (потом убрать)".format(command_test))
            print("{:25s} -> обновить имя файла с настройками, текущий файл %s".format(
                command_change_options_file
            )%(
                names.request_options_file_name_txt
            ))
            print("{:25s} -> обновить данные о прогнозах (в папках %s и %s) по имеющемуся файлу настроек %s\nи по имеющимся параметрам https запросов в файле %s".format(command_update_shedule)%(
                names.responses_dir_name,
                names.commands_dir_name,
                names.request_options_file_name_txt,
                names.https_requests_params_file_name_txt
            ))
            print("{:25s} -> очистить файлы spiffs в соответствии с файлом настроек %s в esp32 (иначе может произойти переполнение памяти)".format(command_clear_spiffs)%(
                names.request_options_file_name_txt
            ))
            print("{:25s} -> очистить ВСЕ файлы, которые есть в spiffs на данный момент".format(command_clear_all_spiffs))
            # print("{:25s} -> (для всех спутников) сделать запросы на сервер за новыми данными, запись их в spiffs".format(command_get_requests))
            print("{:25s} -> получить данные из spiffs в соответствии с файлом настроек %s, записать их в соответствующие файлы для текующей даты".format(command_get_spiffs_data)%(
                names.request_options_file_name_txt
            ))
            # print("{:25s} -> создать файлы с данными по текущему имеющемуся буферу".format(command_parse_buffer_create_files))
            # print("{:25s} -> отправить список настроек из файла в spiffs, записать файлы в spiffs".format(command_push_command_files))
            print("{:25s} -> получить данные о заполненности spiffs, проверить, поместятся файлы в папках %s и %s при их отправке туда".format(command_get_spiffs_info)%(
                names.responses_dir_name,
                names.commands_dir_name
            ))
            print("{:25s} -> загрузить файлы из папок %s и %s и загрузить их в spiffs".format(command_load_data_to_spiffs)%(
                names.responses_dir_name,
                names.commands_dir_name,
            ))
            print("{:25s} -> выйти из программы".format(command_stop))

            print(text_border_bottom)
        
        elif(command == command_test):
            command_binary = 'commandx'.encode()
            # send test command
            sent_bytes = udp_handler.board_socket.sendto(command_binary, udp_handler.board_socket_pair)
            print('command %s sent, size: %i bytes'%(command_binary, sent_bytes))

            wait_response_from_board(event_board_get_command)

            send_response_to_board('test responding 1')

            print('test action in board')
            time.sleep(5)

            send_response_to_board('test responding 2')

            wait_response_from_board(event_board_finish_action)

        elif(command == command_change_options_file):
            old_options_name = names.request_options_file_name_txt
            file_options_name_txt = str(input('Имя файла настроек (с .txt): '))
            names.update_names(file_options_name_txt)

            with open(names.request_options_file_path, 'r') as options_file:
                sat_counter = 0
                for line in options_file:
                    if not line in ['\n', '\r\n']:
                        sat_counter += 1
            port_settings = serial_port.get_settings()
            # change timeout value in settings of port to correctly read data when use realines() funciton
            port_settings['timeout'] = sat_counter
            print('Файл с настройками был изменён с файла %s.txt\nна файл %s.txt'%(
                old_options_name,
                names.request_options_file_name_txt
            ))

        elif(command == command_get_spiffs_data):
            command_binary = 'command0'.encode()
            # number_of_bytes = serial_port.write(command_binary)
            # send test command
            sent_bytes = udp_handler.board_socket.sendto(command_binary, udp_handler.board_socket_pair)
            print('command %s sent, size: %i bytes'%(command_binary, sent_bytes))
            wait_response_from_board(event_board_get_command)

            send_file_over_udp(names.request_options_file_path)
            wait_response_from_board('waiting signal from board that it finished managing file')

            # # get list of responses from board
            # responses_list = udp_text_handler.get_decoded_list_of_satellites_data(serial_port)

            # # parse list of responses from board to corresponding files
            # udp_text_handler.parse_list_create_files(responses_list)

            # send_response_to_board(serial_port, 'we finished handling file data (data files)')

            wait_response_from_board(event_board_finish_action)

        elif(command == command_clear_all_spiffs):
            command_binary = 'clean all'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            wait_response_from_board(serial_port, 'spiffs files erased')

        elif(command == command_clear_spiffs):
            command_binary = 'clean spiffs'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            wait_response_from_board(serial_port, 'board get command')

            wait_response_from_board(serial_port, 'board ready to wait list of satellites')

            sended_bytes = 0

            # create list of command_names
            list_of_names = []

            # wait_response_from_board(serial_port, 'wait signal that board ready to read data')

            send_response_to_board(serial_port, 'signal to board that it can read sended data')

            with open(names.request_options_file_path, 'r') as file_pass:
                for line in file_pass:
                    if not line in ['\n', '\r\n']:
                        sat_id = line.split('=')[1]

                        if not sat_id.endswith('\n'):
                            sat_id += '\n'

                        data_bytes_by_file_name = serial_port.write(sat_id.encode())
                        list_of_names.append(sat_id)
                        sended_bytes += data_bytes_by_file_name

            print("data: %s sent, size: %i bytes"%(list_of_names, sended_bytes))


            serial_port.reset_output_buffer()
            serial_port.cancel_write()

            # send_response_to_board(serial_port, 'finish sending list of satellites')
            wait_response_from_board(serial_port, event_board_finish_action)
        
        elif(command == command_get_spiffs_info):
            files_sized_in_pc = 0

            command_binary = 'get spiffs info'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            wait_response_from_board(serial_port, "wait info that board get command")
            send_response_to_board(serial_port, "ready to read data")

            # get data from uart
            spiffs_general_info = serial_port.readline().decode()

            # continue working only if board finished sending first part of spiffs statistics
            wait_response_from_board(serial_port, "wait when board finish sending first part of info")

            # send signal to board that we are ready to read informations about files
            send_response_to_board(serial_port, "ready to read information about files")

            # print("start waiting files stats. . .")
            # spiffs_files_info = serial_port.read_until('end') 
            spiffs_files_info = serial_port.readlines()
            # print(spiffs_files_info)

            # parse info values
            spiffs_info_values = spiffs_general_info[spiffs_general_info.index(' ') + 1:spiffs_general_info.index('\n')]
            spiffs_info_splitted_list = spiffs_info_values.split(' ')
            total_value = int(spiffs_info_splitted_list[0].split('=')[1])
            used_value  = int(spiffs_info_splitted_list[1].split('=')[1])

            free_space_value  =  total_value - used_value

            for file in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + file
                files_sized_in_pc += os.path.getsize(file_path)
                # print(os.path.getsize(file_path))
            
            for file in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file
                files_sized_in_pc += os.path.getsize(file_path)
            
            if free_space_value < files_sized_in_pc:
                print('ОСТОРОЖНО! %i байт в папках %s и %s не поместятся в свободное пространство из %i байт в spiffs'%(
                    files_sized_in_pc,
                    names.commands_dir_name,
                    names.responses_dir_name,
                    free_space_value
                ))
                return
            else:
                print(text_border_top)
                print('При отправке файлов будет записано %i байт в spiffs, свободное место есть'%(
                    files_sized_in_pc), end='\n\n')

            print('Статистика по spiffs:')
            print('Использовано места (байт): {:>}'.format(str(used_value)))
            print('Всего места в spiffs (байт): {:>}'.format(str(total_value)))
            print('Осталось свободного места (байт): {:>}'.format(str(free_space_value)))

            print('\nИнформация по каждому файлу в spiffs (размер в байтах):')

            if spiffs_files_info:
                for file_info_binary in spiffs_files_info:
                    file_info_decoded = file_info_binary.decode()
                    print(file_info_decoded.strip('\n'))
            else:
                print('SPIFFS пуст! Не найдена информация ни по одному из файлов')

            # print('\nКонец статистики', end='\n')
            print(text_border_bottom)

            send_response_to_board(serial_port, "send signal that we finished working with files")

            wait_response_from_board(serial_port, event_board_finish_action)
        
        elif(command == command_update_shedule):

            req_params_dict = {}

            with open(names.https_requests_params_file_path, 'r') as params_file:
                for line in params_file:
                    if not line in ['\n', '\r\n']:
                        if not line.endswith('\n'):
                            line += '\n'
                        parsed_line_list = line.strip('\n').split('=')
                        param_name  = parsed_line_list[0]
                        param_value_float = float(parsed_line_list[1])
                        req_params_dict[param_name] = param_value_float
            req_params_dict['api_key'] = api_key

            print('Текущие настройки параметров для https запросов:')
            print(req_params_dict)

            # perform requests
            https_req.update_data_create_files(names.request_options_file_path, req_params_dict)

        elif(command == command_load_data_to_spiffs):
            command_binary = 'load pc data to spiffs'.encode()

            # write command to uart buffer
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size %i bytes'%(command_binary, number_of_bytes))

            # continue when board get command
            wait_response_from_board(serial_port, "board get command")
            
            # send signal that we are ready to getting free_space info
            send_response_to_board(serial_port, "ready to get info about free space in spiffs")
            # read size that we already have (and check if there is enough space in spiffs for data)
            free_space_line = serial_port.readline()
            free_space_value = int(free_space_line.decode().split('=')[1].strip('\n'))

            # wait_response_from_board(serial_port)

            # compare sizes
            pc_files_size = 0
            for file_pass in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file_pass
                pc_files_size += os.path.getsize(file_path)

            for user_param in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + user_param
                pc_files_size += os.path.getsize(file_path)

            if free_space_value < pc_files_size:
                print('ОШИБКА! Недостаточно места в spiffs для записи, освободите его перед записью файлов')
                wait_response_from_board(serial_port, 'wait until board ends performs command')
                return

            # test print
            # print('free space value: %i'%free_space_value)

            # send signal to board that we finished working with info data
            send_response_to_board(serial_port, 'python finished working with info data')

            # wait signal that python can load files with data 
            wait_response_from_board(serial_port, 'python can loda files with data')

            for file_pass in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file_pass

                # test print
                print(file_path)

                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port, 'new file ready')
            
            for user_param in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + user_param
                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port, 'new file ready')

            serial_port.write('END FILES TRANSMISSION'.encode())

            # wait singnal that board finished working with files
            wait_response_from_board(serial_port, 'board finished working with files')

            # wait signal that we can read another command
            wait_response_from_board(serial_port, event_board_finish_action)

        elif(command == command_stop):
            print('ПРОГРАММА ОСТАНОВЛЕНА . . .', end='\n\n')
            return
        else:
            print()
            print("НЕВЕРНАЯ КОМАНДА!")
            print()

def send_file_over_udp(file_path):
    
    # TODO check if file is empty
    # TODO handle case when symbol of last string in options file is not ''

    # send data for one satellite
    data_from_file = []
    with open(file_path, 'r') as file:
        # TEST костыль
        for data_line in file:
            if not data_line in ['\n', '\r\n']:
                if not data_line.endswith('\n'):
                    data_line += '\n'
                data_from_file.append(data_line)
                
    print(data_from_file)

    data_from_file_binary = ''
    data_from_file_binary += 'START_FILE\n'
    for data_line in data_from_file:
        data_from_file_binary += data_line
    data_from_file_binary += 'END_FILE\n'

    print(data_from_file_binary)

    sent_bytes = udp_handler.board_socket.sendto(data_from_file_binary.encode(), udp_handler.board_socket_pair)
    print('message: %s sent, size: %i bytes'%(data_from_file_binary, sent_bytes))

def send_response_to_board(message_about_sending):
    print('sending event: %s'%(message_about_sending))

    response = 'response1'
    response_encoded = response.encode()
    sent_bytes = udp_handler.board_socket.sendto(response_encoded, udp_handler.board_socket_pair)
    print('message sent, size %i bytes'%(response, sent_bytes))

    # if(serial_port.is_open):
    #     # test sleep
    #     time.sleep(1)

    #     print('send event: %s'%(message_about_sending))

    #     response_encoded = 'NEXT_ACTION_BOARD'.encode()
    #     serial_port.write(response_encoded)

    #     # give a few seconds before next line of code in python script 
    #     time.sleep(1)

    #     serial_port.reset_output_buffer()
    #     serial_port.reset_input_buffer()
        
    # else:
    #     print("ERROR! Port is not opened")
    #     return

def wait_response_from_board(waiting_event):
    print('wait event: %s'%(waiting_event))

    # TODO check if it could be deleted
    # give a few seconds to read info in uart (to read it)
    # time.sleep(1)

    response = b''
    while(response.decode() != 'response0'):
        print('waiting data from port %i'%(udp_handler.BOARD_PORT))
        response, addr = udp_handler.pc_socket.recvfrom(16)
        print('received message: %s from %s\n'%(response.decode(), addr))

        time.sleep(1)

    # if(serial_port.is_open):
    #     # print('Wait response from board . . .')
    #     # print(waiting_event)
    #     print('wait event: %s'%(waiting_event))

    #     response = ''
    #     while(response != 'NEXT_ACTION\n'):
    #         response = serial_port.readline().decode()
    #         print('wrong line in UART. . .')
        
    #     # print('Got response!')

    #     # erase response from input buffer
    #     serial_port.reset_input_buffer()
    #     # erase output buffer commands
    #     serial_port.reset_output_buffer()

    #     # test sleep
    #     time.sleep(1)
    # else:
    #     print("ERROR! Port is not opened")
    #     return