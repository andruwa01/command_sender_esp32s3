# Компанды , которые нужно сделать (чтобы работать с spiffs):

# -[x] Получить данные для всех спутников и записать их в соответствующие файлы
# -[] Получить данные по id спутника и записать их в файл 
# -[] Получить список спутников с соответствующими id из spiffs
# -[x] *Вести данные (изменения) в spiffs*
# -[x] Обновить содержимое файлов всех спутников в spiffs

import os
import time
import text_handler
import https_req
import names
import serial

time_to_wait_s = 5
print('Program starts . . . wait %i seconds'%(time_to_wait_s))
# wait 5 seconds before board will be ready for action
time.sleep(time_to_wait_s)

def init_command_handler(serial_port):

    command_help =                      'help'
    command_change_options_file =       'change options'
    command_update_shedule =            'update shedule'
    command_get_spiffs_data =           'spiffs get data'
    command_clear_spiffs =              'spiffs clear'
    command_clear_all_spiffs =          'spiffs clear all'    
    command_get_spiffs_info =           'spiffs get info' 
    command_load_data_to_spiffs =       'spiffs load'
    command_stop =                      'stop'

    names.update_names(names.request_options_file_name)

    while True:
        serial_port.reset_input_buffer()
        serial_port.reset_output_buffer()

        print('Текущее имя файла настроек: %s'%(
            names.request_options_file_name
        ))
        print("{:20s} -> показать список доступных команд".format(command_help))
        command = str(input("ВВЕДИТЕ КОМАНДУ: "))
        # command_binary = command.encode()

        if(command == command_help):
            print('\n<========================================================================>', end='\n')
            print('СПИСОК ДОСТУПНЫХ КОМАНД:', end='\n\n')
            print("{:25s} -> обновить имя файла с настройками".format(
                command_change_options_file
            ))
            print("{:25s} -> обновить данные о прогнозах (в папках %s и %s) по имеющемуся файлу настроек %s".format(command_update_shedule)%(
                names.responses_dir_name,
                names.commands_dir_name,
                names.request_options_file_name
            ))
            print("{:25s} -> очистить файлы spiffs в соответствии с файлом настроек %s в esp32 (иначе может произойти переполнение памяти)".format(command_clear_spiffs)%(
                names.request_options_file_name
            ))
            print("{:25s} -> очистить ВСЕ файлы, которые есть в spiffs на данный момент".format(command_clear_all_spiffs))
            # print("{:25s} -> (для всех спутников) сделать запросы на сервер за новыми данными, запись их в spiffs".format(command_get_requests))
            print("{:25s} -> (для всех спутников) получить данные из spiffs, записать их в соответствующие файлы для текующей даты".format(command_get_spiffs_data))
            # print("{:25s} -> создать файлы с данными по текущему имеющемуся буферу".format(command_parse_buffer_create_files))
            # print("{:25s} -> отправить список настроек из файла в spiffs, записать файлы в spiffs".format(command_push_command_files))
            print("{:25s} -> получить данные о заполненности spiffs, проверить, поместятся ли полученные данные при их отправке туда".format(command_get_spiffs_info))
            print("{:25s} -> загрузить данные о прогнозах в spiffs из папок %s и %s".format(command_load_data_to_spiffs)%(
                names.responses_dir_name,
                names.commands_dir_name,
            ))
            print("{:25s} -> выйти из программы".format(command_stop))
            print('<========================================================================>', end='\n\n')

        elif(command == command_change_options_file):
            old_options_name = names.request_options_file_name
            file_options_name_txt = str(input('Имя файла настроек: '))
            names.update_names(file_options_name_txt)
            print('Файл с настройками был изменён с файла %s\nна файл %s'%(
                old_options_name,
                names.request_options_file_name
            ))

        elif(command == command_get_spiffs_data):
            command_binary = 'give spiffs data to pc'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            # wait signal from board that it got command 
            wait_response_from_board(serial_port)

            send_file_over_uart(names.request_options_file_path, serial_port)

            # wait signal from board that it read input_options.txt file
            wait_response_from_board(serial_port)

            serial_port.write('END FILES TRANSMISSION'.encode())
            print('END FILE TRANSMISSION')

            # wait response from board that it got finished managing file
            wait_response_from_board(serial_port)

            # get list of responses from board
            responses_list = text_handler.get_decoded_list_of_satellites_data(serial_port)

            # parse list of responses from board to corresponding files
            text_handler.parse_list_create_files(responses_list)

            wait_response_from_board(serial_port) 

        elif(command == command_clear_all_spiffs):
            command_binary = 'clean all'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            wait_response_from_board(serial_port)

        elif(command == command_clear_spiffs):
            command_binary = 'clean spiffs'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            # wait response from board about readiness of waiting list of satellites
            wait_response_from_board(serial_port)

            sended_bytes = 0

            # create list of command_names
            list_of_names = []

            with open(names.request_options_file_path, 'r') as file_pass:
                for line in file_pass:
                    sat_id = line.split('=')[1]
                    data_bytes_by_file_name = serial_port.write(sat_id.encode())
                    list_of_names.append(sat_id)
                    sended_bytes += data_bytes_by_file_name

            print("data: %s sent, size: %i bytes"%(list_of_names, sended_bytes))

            wait_response_from_board(serial_port)
        
        elif(command == command_get_spiffs_info):
            files_sized_in_pc = 0

            command_binary = 'get spiffs info'.encode()
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            # get data from uart
            spiffs_general_info = serial_port.readline().decode()

            # continue working only if board finished sending first part of spiffs statistics
            wait_response_from_board(serial_port)

            print("start waiting files stats. . .")
            # spiffs_files_info = serial_port.read_until('end') 
            spiffs_files_info = serial_port.readlines()
            print(spiffs_files_info)

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
                print('\nПри отправке файлов будет записано %i байт в spiffs, свободное место есть'%(files_sized_in_pc))

            print('\nСтатистика по spiffs:')
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

            print('Конец статистики', end='\n\n')

            # wait_response_from_board(serial_port)
        
        elif(command == command_update_shedule):
            # perform requests
            https_req.update_data_create_files(names.request_options_file_path)

        elif(command == command_load_data_to_spiffs):

            command_binary = 'load spiffs data to pc'.encode()
            # write command to uart buffer
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size %i bytes'%(command_binary, number_of_bytes))

            # wait response from board that it read command correctly
            wait_response_from_board(serial_port)
            
            # read size that we already have (and check if there is enough space in spiffs for data)
            free_space_line = serial_port.readline()
            free_space_value = int(free_space_line.decode().split('=')[1].strip('\n'))

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
                wait_response_from_board(serial_port)
                return

            # test print
            # print('free space value: %i'%free_space_value)

            # wait signal that python can continue work 
            wait_response_from_board(serial_port)

            for file_pass in os.listdir(names.responses_dir_path):
                file_path = names.responses_dir_path + '/' + file_pass
                print(file_path)
                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port)
            
            for user_param in os.listdir(names.commands_dir_path):
                file_path = names.commands_dir_path + '/' + user_param
                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port)

            serial_port.write('END FILES TRANSMISSION'.encode())

            wait_response_from_board(serial_port)

        elif(command == command_stop):
            print('ПРОГРАММА ОСТАНОВЛЕНА . . .', end='\n\n')
            return
        else:
            print()
            print("НЕВЕРНАЯ КОМАНДА!")
            print()

def send_file_over_uart(file_path, serial_port):
    # send data for one satellite
    data_from_file = []
    with open(file_path, 'r') as command_file:
        data_from_file = command_file.readlines()

    # clean input buffer 
    serial_port.reset_input_buffer()

    data_from_file_binary = []

    for item in data_from_file:
        data_from_file_binary.append(item.encode())

    # sended bytes counter
    data_bytes = 0

    # send content from one file to uart tx
    start_bytes = serial_port.write('START_FILE\n'.encode())
    data_bytes += start_bytes

    for data_element in data_from_file_binary:
        data_bytes_element = serial_port.write(data_element)
        data_bytes += data_bytes_element

    end_bytes = serial_port.write('END_FILE\n'.encode())
    data_bytes += end_bytes

    print("data: %s sent, size: %i bytes"%(data_from_file_binary, data_bytes))

   # clear data form buffer (to not mix data)
    serial_port.reset_output_buffer()

def send_response_to_board(serial_port):
    if(serial_port.is_open):
        print('Sending response to board . . .')
        response_encoded = 'RESPONSE FROM PC'.encode()
        sended_bytes = serial_port.write(response_encoded)
        print("data: %s sent, size: %i bytes"%(response_encoded, sended_bytes))
    else:
        print("ERROR! Port is not opened")
        return

def wait_response_from_board(serial_port):
    if(serial_port.is_open):
        print('Wait response from board . . .')

        response = ''
        while(response != 'NEXT_ACTION\n'):
            response = serial_port.readline().decode()
            print('uart get something...')
        
        print('Got response!')

        # erase response from input buffer
        serial_port.reset_input_buffer()
        # erase output buffer commands
        serial_port.reset_output_buffer()
    else:
        print("ERROR! Port is not opened")
        return