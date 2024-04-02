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
            send_command_to_board('commandx')
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
            send_command_to_board('command0')

            wait_response_from_board(event_board_get_command)

            send_file_over_udp(names.request_options_file_path)

            wait_response_from_board('waiting signal from board that it finished managing options file')

            data_files_string = ''

            while(True):
                print('waiting loop signal')
                loop_signal_bytes, addr = udp_handler.pc_socket.recvfrom(16)
                loop_signal = loop_signal_bytes.decode()
                if(loop_signal == 'BREAK'):
                    print('loop signal: %s'%(loop_signal))
                    break
                elif(loop_signal == 'CONTINUE'):
                    print('loop singal: %s'%(loop_signal))
                    # send_response_to_board('pc get continue signal')
                else:
                    print("ERROR! wrong signal to file handling loop")
                    print('(error loop signal): %s'%(loop_signal))
                    continue


                file_buffer = receive_file_over_udp()
                print('data from pc:\n====\n%s\n====\n'%(file_buffer))

                # TODO две строчки ниже - костыль, чтобы состыковать с тем, что имеется. Можно передеделать.
                file_buffer += 'END_FILE\n'
                data_files_string += file_buffer

            #     # TODO Бывает ошибка, когда send_response_to_board почему-то не попадает на файл

                send_response_to_board('pc can read next file')

            send_response_to_board('finish working with files')

            # spiffs_max_files = 15
            # spiffs_max_file_size = 5512

            # # get string with responses data from board
            # print('Waiting responses from port %i'(udp_handler.PC_PORT))
            # data_files_string = udp_handler.pc_socket.recvfrom(spiffs_max_files * spiffs_max_file_size)

            # parse string of responses from board to corresponding files
            udp_text_handler.parse_data_files_string_create_files(data_files_string)

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
                    if not line in ['\n', '\r\n'] and not line.startswith('//'):
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

            free_space_size  =  total_value - used_value

            for file in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + file
                files_sized_in_pc += os.path.getsize(file_path)
            
            for file in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file
                files_sized_in_pc += os.path.getsize(file_path)
            
            if free_space_size < files_sized_in_pc:
                print('ОСТОРОЖНО! %i байт в папках %s и %s не поместятся в свободное пространство из %i байт в spiffs'%(
                    files_sized_in_pc,
                    names.commands_dir_name,
                    names.responses_dir_name,
                    free_space_size
                ))
                return
            else:
                print(text_border_top)
                print('При отправке файлов будет записано %i байт в spiffs, свободное место есть'%(
                    files_sized_in_pc), end='\n\n')

            print('Статистика по spiffs:')
            print('Использовано места (байт): {:>}'.format(str(used_value)))
            print('Всего места в spiffs (байт): {:>}'.format(str(total_value)))
            print('Осталось свободного места (байт): {:>}'.format(str(free_space_size)))

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
                    if not line in ['\n', '\r\n'] and not line.startswith('//'):
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
            send_command_to_board('command1')
            wait_response_from_board("board get command")
            send_response_to_board("ready to get info about free space in spiffs")
            # read size that we already have (and check if there is enough space in spiffs for data)
            # free_space_line = serial_port.readline()
            free_space_string, addr = udp_handler.pc_socket.recvfrom(128)
            print('\ngot info about free space from\n')
            print(addr)

            free_space_size = int(free_space_string.decode().split('=')[1].strip('\n'))

            # compare sizes
            pc_files_size = 0
            for file_pass in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file_pass
                pc_files_size += os.path.getsize(file_path)

            for command_file_txt in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + command_file_txt
                pc_files_size += os.path.getsize(file_path)

            if free_space_size < pc_files_size:
                print('ОШИБКА! Недостаточно места в spiffs для записи, освободите его перед записью файлов')
                wait_response_from_board('wait until board ends performs command')
                return

            send_response_to_board('python finished working with info data')
            wait_response_from_board('python can start uploading files with data to board')

            for file_pass in os.listdir(names.responses_dir_path):
                udp_handler.board_socket.sendto('CONTINUE'.encode(), udp_handler.board_socket_pair)
                file_path = names.responses_dir_path + '/' + file_pass
                send_file_over_udp(file_path)
                wait_response_from_board('new file ready')
            
            for command_file_txt in os.listdir(names.commands_dir_path):
                udp_handler.board_socket.sendto('CONTINUE'.encode(), udp_handler.board_socket_pair)
                file_path = names.commands_dir_path + '/' + command_file_txt
                send_file_over_udp(file_path)
                wait_response_from_board('new file ready')
            
            udp_handler.board_socket.sendto('BREAK'.encode(), udp_handler.board_socket_pair)

            wait_response_from_board('board finished working with files')
            wait_response_from_board(event_board_finish_action)

        elif(command == command_stop):
            print('ПРОГРАММА ОСТАНОВЛЕНА . . .', end='\n\n')
            return
        else:
            print()
            print("НЕВЕРНАЯ КОМАНДА!")
            print()

def receive_file_over_udp():
    wait_response_from_board('wait signal from board that it ready to send file')

    empty_data_buffer = ''

    start_file_buffer_binary = b''
    while(start_file_buffer_binary.decode() != 'START_FILE'):
        start_file_buffer_binary, addr = udp_handler.pc_socket.recvfrom(len('START_FILE'))
    print('get START_FILE from %s:%i'%(addr))

    send_response_to_board('pc can start reading data chunks')

    used_bytes = 0
    while(True):
        data_chunk_byte, addr = udp_handler.pc_socket.recvfrom(1024)
        data_chunk = data_chunk_byte.decode()
        print('received {0} bytes from {1}:{2}'.format(len(data_chunk), addr[0], addr[1]))
        if(data_chunk == 'END_FILE'):
            print('data chunk finished')
            break

        empty_data_buffer += data_chunk
        used_bytes += len(data_chunk)

        send_response_to_board('ready to get new chunk')

    print('finish file handle with size %i'%(used_bytes))
    return empty_data_buffer

def send_file_over_udp(file_path):

    file_data_string = ''
    file_data_list = []
    with open(file_path, 'r') as file:
        for data_line in file:
            if not data_line in ['\n', '\r\n'] and not data_line.startswith('//'):
                if not data_line.endswith('\n'):
                    data_line += '\n'
                file_data_list.append(data_line)
                file_data_string += data_line

    if not file_data_list or not file_data_string:
        print('data from %s is empty, transmission impossible')
        return
    
    print('(test print) data from file:\n====\n%s\n====\n'%(file_data_string))

    send_response_to_board('ready to send file')

    sent_bytes_test = udp_handler.board_socket.sendto('START_FILE'.encode(), udp_handler.board_socket_pair)
    print('START_FILE sent, size %i bytes'%(sent_bytes_test))

    wait_response_from_board('board start getting file chunks')

    sent_package_size = 0
    file_data_length = len(file_data_string)
    start_chunk_index = 0 
    while(file_data_length > 0):
        end_chunk_index = start_chunk_index + 512
        if end_chunk_index > len(file_data_string):
            end_chunk_index = len(file_data_string)
        data_chunk_string = file_data_string[start_chunk_index:end_chunk_index]
        start_chunk_index = end_chunk_index

        sent_bytes_by_chunk = udp_handler.board_socket.sendto(data_chunk_string.encode(), udp_handler.board_socket_pair)
        file_data_length -= sent_bytes_by_chunk
        sent_package_size += sent_bytes_by_chunk

        wait_response_from_board('wait info about reading new chunk')

    udp_handler.board_socket.sendto('END_FILE'.encode(), udp_handler.board_socket_pair)

    print('message sent, size: %i bytes'%(sent_package_size))

def send_response_to_board(send_event):
    # time.sleep(10)

    print('send event: %s'%(send_event))

    response = 'response1'
    response_binary = response.encode()
    sent_bytes = udp_handler.board_socket.sendto(response_binary, udp_handler.board_socket_pair)
    print('message %s sent, size %i bytes'%(response, sent_bytes))

def wait_response_from_board(waiting_event):
    print('wait event: %s'%(waiting_event))
    response = b''
    while(response.decode() != 'response0'):
        print('waiting data from port %i'%(udp_handler.BOARD_PORT))
        response, addr = udp_handler.pc_socket.recvfrom(16)
        print('received response: %s from %s'%(response.decode(), addr))

def send_command_to_board(command_text):
    if len(command_text) != len('commandx'):
        print('ERROR! Wrong format of command')
        return

    command_binary = command_text.encode()
    sent_bytes = udp_handler.board_socket.sendto(command_binary, udp_handler.board_socket_pair)
    print('\ncommand %s sent, size: %i bytes\n'%(command_binary, sent_bytes))