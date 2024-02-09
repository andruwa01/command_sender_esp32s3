# Компанды , которые нужно сделать (чтобы работать с spiffs):

# -[] Получить данные для всех спутников и записать их в соответствующие файлы
# -[] Получить данные по id спутника и записать их в файл 
# -[] Получить список спутников с соответствующими id из spiffs
# -[] *Вести данные в spiffs*
# -[] Обновить содержимое файлов всех спутников в spiffs
# -[] Обновить содержимое всех спутников в spiffs

import text_handler
import time

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
    if(serial_port.is_open):
        satellites_decoded_list = ""

        handle_flag = True
        while handle_flag:
            serial_port.reset_input_buffer()
            serial_port.reset_output_buffer()

            print('\n')
            print("What command do you want to execute?")
            print("make_requtests   : сделать запросы на сервер за новыми данными")
            print("get_list         : получить данные спутников из spiffs")
            print("parse_list       : создать файлы спутников в соответствующих каталогах по полученному списку")
            print("stop             : прекратить ждать команды в esp32, дальше она не будет получать команды")
            print('\n')

            command = str(input("Enter command: "))
            command_binary = command.encode()

            match command:
                case 'make_requests':
                    number_of_bytes = serial_port.write(command_binary)
                    print('command %s sended, size: %i bytes'%(command_binary, number_of_bytes))

                    wait_response_from_board(serial_port)

                case 'get_list':
                    number_of_bytes = serial_port.write(command_binary)
                    print('command %s sended, size: %i bytes'%(command_binary, number_of_bytes))
                    
                    satellites_decoded_list = text_handler.get_decoded_list_of_satellites_data(serial_port)

                    wait_response_from_board(serial_port) 
                case 'parse_list':
                    # number_of_bytes = serial_port.write(command_binary)
                    print('command %s sended, size: %i bytes'%(command_binary, number_of_bytes))
                    text_handler.parse_list_create_files(satellites_decoded_list)
                    satellites_decoded_list = ""

                    # wait_response_from_board(serial_port)
                case _:
                    print("Wrong command!")
    else:
        print("ERROR! Port is not opened")
        return