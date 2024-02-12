import text_handler
import command_sender

number_of_satellites = 15
timeout_s = number_of_satellites + 5 # by default: for 15 satellites

serial_port = text_handler.initialize_port(timeout_s)
command_sender.command_handler(serial_port)
serial_port.close()