import text_handler
import command_sender

serial_port = text_handler.initialize_port()
command_sender.command_handler(serial_port)
serial_port.close()