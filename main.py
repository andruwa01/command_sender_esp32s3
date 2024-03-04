import text_handler
import command_sender

# TODO count number of satellites from information about input_options 
number_of_satellites = 15            # number of satellites
timeout_s = number_of_satellites + 5 # we need this to synchronise python script and working board 

serial_port = text_handler.initialize_port(timeout_s)
if(serial_port.is_open):
    command_sender.init_command_handler(serial_port)
    serial_port.close()
else:
    print("ОШИБКА! UART ЗАКРЫТ, РАБОТА НЕВОЗМОЖНА! НАСТРОЙТЕ UART")