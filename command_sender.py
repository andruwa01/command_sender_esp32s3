# Компанды , которые нужно сделать (чтобы работать с spiffs):

# -[x] Получить данные для всех спутников и записать их в соответствующие файлы
# -[] Получить данные по id спутника и записать их в файл 
# -[] Получить список спутников с соответствующими id из spiffs
# -[] *Вести данные (изменения) в spiffs*
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

    # print(data_from_command_file)

    data_from_command_file_binary = []

    for item in data_from_command_file:
        data_from_command_file_binary.append(item.encode())

    # print(data_from_command_file_binary)

    # data_example_string = 'name: NORBI\nsatid: 0000\n'
    # data_example_string_binary = data_example_string.encode()

    # send content from one file to uart tx
    data_bytes = 0
    for data_element in data_from_command_file_binary:
        data_bytes_element = serial_port.write(data_element)
        data_bytes += data_bytes_element

    print("data: %s sent, size: %i bytes"%(data_from_command_file_binary, data_bytes))

    # serial_port.cancel_write()
    # serial_port.reset_output_buffer()

    # wait_response_from_board(serial_port)
    # time.sleep(5)



def wait_response_from_board(serial_port):
    if(serial_port.is_open):
        print('Wait response from board . . .')

        response = ''
        while(response != 'NEXT_ACTION\n'):
            response = serial_port.readline().decode()
            print('uart get something...')
        
        print('Got response!')
        # serial_port.reset_input_buffer()
        # serial_port.reset_output_buffer()
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

                wait_response_from_board(serial_port)
            
            elif(command == command_push_command_files):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sent, size: %i bytes:'%(command_binary, number_of_bytes))

                # give a time to UART RX of ESP32 to read command. 
                # else command and data is mixed and on the ESP32 side reads inproper way
                time.sleep(1)

                # clear buffer because we don't want send command with data (mix them)
                serial_port.reset_output_buffer()

                #send data for all satellites
                # passes_full_folder_path = "./satellites/passes_full"
                passes_user_input_folder_path = "./satellites/passes_user_input"

                # for file in os.listdir(passes_user_input_folder_path):

                file_name_1 = "OBJECT AR_commands.txt"
                send_command_file(passes_user_input_folder_path, file_name_1, serial_port)
                # file_name_2 = "JILIN-01 GAOFEN 2F_commands.txt"
                # send_command_file(passes_user_input_folder_path, file_name_2, serial_port)

                # give time to board to divide two messages
                time.sleep(1)

                serial_port.write('END FILES TRANSMISSION'.encode())
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