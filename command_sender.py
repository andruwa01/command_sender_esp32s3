# Компанды , которые нужно сделать (чтобы работать с spiffs):

# -[x] Получить данные для всех спутников и записать их в соответствующие файлы
# -[] Получить данные по id спутника и записать их в файл 
# -[] Получить список спутников с соответствующими id из spiffs
# -[x] *Вести данные (изменения) в spiffs*
# -[x] Обновить содержимое файлов всех спутников в spiffs

import text_handler
import https_req
import os

# TODO change this function on 
def send_file_over_uart(file_path, serial_port):
# def send_file_over_uart(folder_of_file, file_name, serial_port):
    # file_path = folder_of_file + '/' + file_name 

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

def command_handler(serial_port):

    command_help =                      'help'
    command_update_buffer =             'update buffer'
    command_parse_buffer_create_files = 'parse buffer'
    command_get_requests =              'get all'
    command_push_command_files =        'push command files'
    command_clear_spiffs =              'clear spiffs'
    command_get_spiffs_data =           'get spiffs info' 
    command_update_pc_responses =       'update passes'
    command_load_passes_to_spiffs =     'load passes to spiffs'
    command_stop =                      'stop'

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
            print("{:25s} -> очистить файлы spiffs в esp32 (иначе произойдёт переполнение памяти)".format(command_clear_spiffs))
            print("{:25s} -> (для всех спутников) сделать запросы на сервер за новыми данными, запись их в spiffs".format(command_get_requests))
            print("{:25s} -> (для всех спутников) получить данные из spiffs, записать их в буфер".format(command_update_buffer))
            print("{:25s} -> создать файлы с данными по текущему имеющемуся буферу".format(command_parse_buffer_create_files))
            print("{:25s} -> отправить данные с указанными параметрами в esp32, затем записать их в spiffs".format(command_push_command_files))
            print("{:25s} -> выйти из программы".format(command_stop))
            print("{:25s} -> получить данные о заполненности spiffs".format(command_get_spiffs_data))
            print("{:25s} -> обновить данные о прогнозах по имеющемуся файлу настроек".format(command_update_pc_responses))
            print("{:25s} -> выгрузить данные о прогнозах в spiffs".format(command_load_passes_to_spiffs))
            print('<========================================================================>', end='\n\n')

        elif(command == command_get_requests):
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            wait_response_from_board(serial_port)

        elif(command == command_update_buffer):
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            # test block of code

            # wait signal from board that it got command 
            wait_response_from_board(serial_port)

            request_options_file_default = './satellites/requests_input_options.txt'           
            # TODO rewrite this part to work with it
            send_file_over_uart(request_options_file_default, serial_port)

            # wait signal from board that it read input_options.txt file
            wait_response_from_board(serial_port)

            serial_port.write('END FILES TRANSMISSION'.encode())
            print('END FILE TRANSMISSION')

            # wait response from board that it got finished managing file
            wait_response_from_board(serial_port)

            # end test block of code

            # get list of satellites names so we could work with it next
            satellites_decoded_list = text_handler.get_decoded_list_of_satellites_data(serial_port)

            # perform 

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
            list_of_names = []

            # send list over uart
            # passes_user_input_folder_path = "./satellites/passes_user_input"
            # passes_full_pc_responses = './satellites/passes_full_pc_responses'

            # for file_name in os.listdir(passes_user_input_folder_path):
            # for file in os.listdir(passes_full_pc_responses):
            #     file_name = file.strip('.txt') + '\n'
            #     data_bytes_by_file_name = serial_port.write(file_name.encode())
            #     list_of_satellite_command_names.append(file_name)
            #     data_bytes += data_bytes_by_file_name

            # TODO test function (clear spiffs by id from options file)
            request_options_file_default = './satellites/requests_input_options.txt'
            with open(request_options_file_default, 'r') as file_pass:
                for line in file_pass:
                    sat_id = line.split('=')[1]
                    data_bytes_by_file_name = serial_port.write(sat_id.encode())
                    list_of_names.append(sat_id)
                    data_bytes += data_bytes_by_file_name

            print("data: %s sent, size: %i bytes"%(list_of_names, data_bytes))

            # serial_port.reset_output_buffer()
            # serial_port.send_break(1)

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

            for file_pass in os.listdir(passes_user_input_folder_path):
                #TODO change this function
                file_path = passes_user_input_folder_path + '/' + file_pass
                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port)

            serial_port.write('END FILES TRANSMISSION'.encode())

            wait_response_from_board(serial_port)
        
        elif(command == command_get_spiffs_data):
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size: %i bytes'%(command_binary, number_of_bytes))

            # get data from uart
            spiffs_info = serial_port.readline().decode()

            print('\nданные о spiffs: ' + spiffs_info)

            wait_response_from_board(serial_port)
        
        elif(command == command_update_pc_responses):
            # perform requests
            request_options_file_default = './satellites/requests_input_options.txt'
            https_req.update_data(request_options_file_default)

        elif(command == command_load_passes_to_spiffs):
            # write command to uart buffer
            number_of_bytes = serial_port.write(command_binary)
            print('command %s sent, size %i bytes')

            # clear command from ring buffer
            serial_port.reset_output_buffer()

            # wait signal that we got command
            wait_response_from_board(serial_port)

            # folder with passes files (responses)
            passes_folder = './satellites/passes_data'
            user_params_dir = './satellites/params_shedule'

            # iterate over files
            # for file in os.listdir(passes_folder):
            #     # test if
            #     # if (file_name == 'FEES.txt' or file_name == 'FOSSASAT2E13.txt' or file_name == 'JILIN-01 GAOFEN 2F.txt'):
            #     print(file)
            #     #TODO change this function
            #     file_path = passes_folder + '/' + file
            #     send_file_over_uart(file_path, serial_port)
            #     wait_response_from_board(serial_port)

            # TODO test function: writing to uart with id (not name)
            # TODO make variable request_options_file_default global (for all places in this code file)
            for file_pass in os.listdir(passes_folder):
                file_path = passes_folder + '/' + file_pass
                print(file_path)
                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port)
            
            # test file sending
            # send_file_over_uart(passes_folder + '/' + '46494.txt', serial_port)
            # wait_response_from_board(serial_port)
            # send_file_over_uart(passes_folder + '/' + '48082.txt', serial_port)
            # wait_response_from_board(serial_port)
            
            # TODO write ineration over command files so everything will be ok
            for user_param in os.listdir(user_params_dir):
                file_path = user_params_dir + '/' + user_param
                send_file_over_uart(file_path, serial_port)
                wait_response_from_board(serial_port)

            # test file sending
            # send_file_over_uart(user_params_dir + '/' + '46494_commands.txt', serial_port)
            # wait_response_from_board(serial_port)
            # send_file_over_uart(user_params_dir + '/' + '48082_commands.txt', serial_port)
            # wait_response_from_board(serial_port)

            serial_port.write('END FILES TRANSMISSION'.encode())

            wait_response_from_board(serial_port)

        elif(command == command_stop):
            print('ПРОГРАММА ОСТАНОВЛЕНА . . .', end='\n\n')
            return
        else:
            print()
            print("НЕВЕРНАЯ КОМАНДА!")
            print()