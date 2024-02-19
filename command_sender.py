# Компанды , которые нужно сделать (чтобы работать с spiffs):

# -[x] Получить данные для всех спутников и записать их в соответствующие файлы
# -[] Получить данные по id спутника и записать их в файл 
# -[] Получить список спутников с соответствующими id из spiffs
# -[x] *Вести данные (изменения) в spiffs*
# -[x] Обновить содержимое файлов всех спутников в spiffs

import text_handler
import time
import os

def send_command_file(passes_user_input_folder_path, file_name,serial_port):
    file_path = passes_user_input_folder_path + '/' + file_name 

    # send data for one satellite
    data_from_command_file = []
    command_file = open(file_path, 'r')
    data_from_command_file = command_file.readlines()

    # clean input buffer 
    serial_port.reset_input_buffer()

    data_from_command_file_binary = []

    for item in data_from_command_file:
        data_from_command_file_binary.append(item.encode())

    data_bytes = 0

    # send content from one file to uart tx
    start_bytes = serial_port.write('START_FILE\n'.encode())
    data_bytes += start_bytes

    for data_element in data_from_command_file_binary:
        data_bytes_element = serial_port.write(data_element)
        data_bytes += data_bytes_element

    end_bytes = serial_port.write('END_FILE\n'.encode())
    data_bytes += end_bytes

    print("data: %s sent, size: %i bytes"%(data_from_command_file_binary, data_bytes))

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


def command_handler(serial_port):

    command_help =                      'help'
    command_update_buffer =             'update buffer'
    command_get_requests =              'get all'
    command_push_command_files =        'push command files'
    command_parse_buffer_create_files = 'parse buffer'
    command_clear_spiffs =              'clear spiffs'
    command_get_spiffs_data =           'get spiffs info' 
    command_stop =                      'stop'

    if(serial_port.is_open):

        satellites_decoded_list = ""

        while True:
            serial_port.reset_input_buffer()
            serial_port.reset_output_buffer()

            print("{:20s} -> показать список доступных команд".format(command_help))
            command = str(input("ВВЕДИТЕ КОМАНДУ: "))
            command_binary = command.encode()

            if(command == command_help):
                print('\n<========================================================================>', end='\n')
                print('СПИСОК ДОСТУПНЫХ КОМАНД:', end='\n\n')
                print("{:20s} -> очистить файлы spiffs в esp32 (иначе произойдёт переполнение памяти)".format(command_clear_spiffs))
                print("{:20s} -> (для всех спутников) сделать запросы на сервер за новыми данными, запись их в spiffs".format(command_get_requests))
                print("{:20s} -> (для всех спутников) получить данные из spiffs, записать их в буфер".format(command_update_buffer))
                print("{:20s} -> создать файлы с данными по текущему имеющемуся буферу".format(command_parse_buffer_create_files))
                print("{:20s} -> отправить данные с указанными параметрами в esp32, затем записать их в spiffs".format(command_push_command_files))
                print("{:20s} -> выйти из программы".format(command_stop))
                print("{:20s} -> получить данные о заполненности spiffs".format(command_get_spiffs_data))
                print('<========================================================================>', end='\n\n')

            elif(command == command_get_requests):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

                wait_response_from_board(serial_port)

            elif(command == command_update_buffer):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))
                satellites_decoded_list = text_handler.get_decoded_list_of_satellites_data(serial_port)

                wait_response_from_board(serial_port) 

            elif(command == command_parse_buffer_create_files):
                text_handler.parse_list_create_files(satellites_decoded_list)
                satellites_decoded_list = ""

            elif(command == command_clear_spiffs):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

                # wait response from board about readiness of waiting list of satellites
                wait_response_from_board(serial_port)

                data_bytes = 0

                # create list of command_names
                list_of_satellite_command_names = []

                # send list over uart
                passes_user_input_folder_path = "./satellites/passes_user_input"
                for file_name in os.listdir(passes_user_input_folder_path):
                    file_name += '\n'
                    data_bytes_by_file_name = serial_port.write(file_name.encode())
                    list_of_satellite_command_names.append(file_name)
                    data_bytes += data_bytes_by_file_name

                print("data: %s sent, size: %i bytes"%(list_of_satellite_command_names, data_bytes))

                # serial_port.reset_output_buffer()
                # serial_port.send_break(1)

                # time.sleep(5)

                # send_response_to_board(serial_port)

                wait_response_from_board(serial_port)
            
            elif(command == command_push_command_files):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sent, size: %i bytes:'%(command_binary, number_of_bytes))

                serial_port.reset_output_buffer()
                wait_response_from_board(serial_port)

                # clear buffer because we don't want send command with data (mix them)
                # serial_port.reset_output_buffer()
                
                # todo send files with full data after get requetst from python
                # passes_full_folder_path = "./satellites/passes_full"
                passes_user_input_folder_path = "./satellites/passes_user_input"

                for file_name in os.listdir(passes_user_input_folder_path):
                    send_command_file(passes_user_input_folder_path, file_name, serial_port)
                    wait_response_from_board(serial_port)

                serial_port.write('END FILES TRANSMISSION'.encode())

                wait_response_from_board(serial_port)
            
            elif(command == command_get_spiffs_data):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sent, size: %i bytes:'%(command_binary, number_of_bytes))

                # get data from uart
                spiffs_info = serial_port.readline().decode()

                print('\nданные о spiffs: ' + spiffs_info)

                wait_response_from_board(serial_port)

            elif(command == command_stop):
                print('ПРОГРАММА ОСТАНОВЛЕНА . . .', end='\n\n')
                return
            else:
                print()
                print("НЕВЕРНАЯ КОМАНДА!")
                print()
    else:
        print("ОШИБКА! UART ЗАКРЫТ, РАБОТА НЕВОЗМОЖНА! НАСТРОЙТЕ UART")
        return