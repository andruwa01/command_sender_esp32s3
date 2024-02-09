# Компанды , которые нужно сделать (чтобы работать с spiffs):

# -[] Получить данные для всех спутников и записать их в соответствующие файлы
# -[] Получить данные по id спутника и записать их в файл 
# -[] Получить список спутников с соответствующими id из spiffs
# -[] *Вести данные в spiffs*
# -[] Обновить содержимое файлов всех спутников в spiffs
# -[] Обновить содержимое всех спутников в spiffs

import text_handler

def wait_response_from_board(serial_port):
    if(serial_port.is_open):
        print('Wait response from board . . .')

        response = ''
        while(response != 'NEXT_ACTION\n'):
            response = serial_port.readline().decode()
            print('uart get something...')
        
        print('Got response!')

        serial_port.reset_input_buffer()
        serial_port.reset_output_buffer()
        return response
    else:
        print("ERROR! Port is not opened")
        return


def command_handler(serial_port):

    command_help = 'help'
    command_update_buffer = 'update buffer'
    command_get_requests = 'get all'
    command_parse_buffer_create_files = 'parse buffer'
    command_stop = 'stop'

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
                print("{:20s} -> (для всех спутников) сделать запросы на сервер за новыми данными, запись их в spiffs".format(command_get_requests))
                print("{:20s} -> (для всех спутников) получить данные из spiffs, записать их в буфер".format(command_update_buffer))
                print("{:20s} -> создать файлы с данными по текущему имеющемуся буферу".format(command_parse_buffer_create_files))
                print("{:20s} -> выйти из программы".format(command_stop))

                print('<========================================================================>', end='\n\n')
            elif(command == command_get_requests):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sended, size: %i bytes'%(command_binary, number_of_bytes))

                wait_response_from_board(serial_port)

            elif(command == command_update_buffer):
                number_of_bytes = serial_port.write(command_binary)
                print('command %s sended, size: %i bytes'%(command_binary, number_of_bytes))
                
                satellites_decoded_list = text_handler.get_decoded_list_of_satellites_data(serial_port)

                wait_response_from_board(serial_port) 
            elif(command == command_parse_buffer_create_files):
                text_handler.parse_list_create_files(satellites_decoded_list)
                satellites_decoded_list = ""

            elif(command == command_stop):
                print('Program stopped . . .', end='\n\n')
                return
            else:
                print()
                print("Wrong command!")
                print()
    else:
        print("ERROR! Port is not opened")
        return