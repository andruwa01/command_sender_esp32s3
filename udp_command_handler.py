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

                send_response_to_board('pc can read next file')

            send_response_to_board('finish working with files')

            udp_text_handler.parse_data_files_string_create_files(data_files_string)

            wait_response_from_board(event_board_finish_action)

        elif(command == command_clear_all_spiffs):
            command_binary = 'clean all'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            wait_response_from_board(serial_port, 'spiffs files erased')

        elif(command == command_clear_spiffs):
            send_command_to_board('command3')
            wait_response_from_board(event_board_get_command)

            wait_response_from_board('board ready to get list of satellites')

            sat_ids_str = ''
            with open(names.request_options_file_path, 'r') as options_file:
                for option in options_file:
                    if not option in ['\n', '\r\n'] and not option.startswith('//'):
                        sat_id_str = option.split('=')[1]
                        if not sat_id_str.endswith('\n'):
                            sat_id_str += '\n'
                        sat_ids_str += sat_id_str

            # print(sat_ids_str)
            send_msg_over_udp(sat_ids_str)

            # sended_bytes = 0

            # # create list of command_names
            # list_of_names = []

            # # wait_response_from_board(serial_port, 'wait signal that board ready to read data')

            # send_response_to_board(serial_port, 'signal to board that it can read sended data')

            # with open(names.request_options_file_path, 'r') as file_pass:
            #     for line in file_pass:
            #         if not line in ['\n', '\r\n'] and not line.startswith('//'):
            #             sat_id = line.split('=')[1]

            #             if not sat_id.endswith('\n'):
            #                 sat_id += '\n'

            #             data_bytes_by_file_name = serial_port.write(sat_id.encode())
            #             list_of_names.append(sat_id)
            #             sended_bytes += data_bytes_by_file_name

            # print("data: %s sent, size: %i bytes"%(list_of_names, sended_bytes))


            # serial_port.reset_output_buffer()
            # serial_port.cancel_write()

            # send_response_to_board(serial_port, 'finish sending list of satellites')
            wait_response_from_board(event_board_finish_action)
        
        elif(command == command_get_spiffs_info):
            send_command_to_board('command2')

            wait_response_from_board(event_board_get_command)
            send_response_to_board("ready to get info about free space in spiffs")

            # get info about spiffs size 
            spiffs_space_str = receive_msg_over_udp()

            # free_space_str format: 'total=%i\nused=%i\n' 
            total_value      = int(spiffs_space_str.split('\n')[0].split('=')[1])
            used_value       = int(spiffs_space_str.split('\n')[1].split('=')[1])
            free_space_value = total_value - used_value

            wait_response_from_board("wait when board finish sending general spiffs info")
            send_response_to_board("ready to read information about files")

            # Реализовать отправку собщений, которое затем можно интегрировать в отправку файлов, но тогад нужно сделать такое и на плате
            print('read info about files')
            spiffs_files_info = receive_msg_over_udp()

            files_sized_in_pc = 0
            for file in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + file
                files_sized_in_pc += os.path.getsize(file_path)
            
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

            spiffs_files_info_lines = spiffs_files_info.split('\n')
            if spiffs_files_info:
                for info_line in spiffs_files_info_lines:
                    print(info_line)
            else:
                print('SPIFFS пуст! Не найдена информация ни по одному из файлов')

            # print('\nКонец статистики', end='\n')
            print(text_border_bottom)

            send_response_to_board("send signal that we finished working with files")

            wait_response_from_board(event_board_finish_action)
        
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
            wait_response_from_board(event_board_get_command)
            send_response_to_board("ready to get info about free space in spiffs")
            # read size that we already have (and check if there is enough space in spiffs for data)
            
            spiffs_space_str = receive_msg_over_udp()

            spiffs_info_sizes = int(spiffs_space_str.split('=')[1].strip('\n'))

            # compare sizes
            pc_files_size = 0
            for file_pass in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file_pass
                pc_files_size += os.path.getsize(file_path)

            for command_file_txt in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + command_file_txt
                pc_files_size += os.path.getsize(file_path)

            if spiffs_info_sizes < pc_files_size:
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
    file_data = receive_msg_over_udp()
    return file_data

def receive_msg_over_udp():
    wait_response_from_board('wait signal from board that it ready to send message')

    data_buffer_str = ''

    start_msg_buffer_binary = b''
    while(start_msg_buffer_binary.decode() != 'START_MSG'):
        start_msg_buffer_binary, addr = udp_handler.pc_socket.recvfrom(len('START_MSG'))
    print('get START_MSG from %s:%i'%(addr))

    send_response_to_board('pc can start reading data chunks')

    used_bytes = 0
    while(True):
        data_chunk_byte, addr = udp_handler.pc_socket.recvfrom(1024)
        data_chunk = data_chunk_byte.decode()
        print('received {0} bytes from {1}:{2}'.format(len(data_chunk), addr[0], addr[1]))
        if(data_chunk == 'END_MSG'):
            print('data chunk finished')
            break

        data_buffer_str += data_chunk
        used_bytes += len(data_chunk)

        send_response_to_board('ready to get new chunk')

    print('finish handle message with size %i'%(used_bytes))
    return data_buffer_str

def send_msg_over_udp(msg_buf_str):
    send_response_to_board('ready to send message')

    sent_bytes_test = udp_handler.board_socket.sendto('START_MSG'.encode(), udp_handler.board_socket_pair)
    print('START_FILE sent, size %i bytes'%(sent_bytes_test))

    wait_response_from_board('board start getting message chunks')

    sent_package_size = 0
    msg_data_length = len(msg_buf_str)
    start_chunk_index = 0 
    while(msg_data_length > 0):
        end_chunk_index = start_chunk_index + 512
        if end_chunk_index > len(msg_buf_str):
            end_chunk_index = len(msg_buf_str)
        data_chunk_string = msg_buf_str[start_chunk_index:end_chunk_index]
        start_chunk_index = end_chunk_index

        sent_bytes_by_chunk = udp_handler.board_socket.sendto(data_chunk_string.encode(), udp_handler.board_socket_pair)
        msg_data_length -= sent_bytes_by_chunk
        sent_package_size += sent_bytes_by_chunk

        wait_response_from_board('wait info about reading new chunk')

    udp_handler.board_socket.sendto('END_MSG'.encode(), udp_handler.board_socket_pair)

    print('message sent, size: %i bytes'%(sent_package_size))   

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

    send_msg_over_udp(file_data_string)

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