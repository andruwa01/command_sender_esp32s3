import socket
import time

response_message = 'commandx'.encode()
# SERVER_IP_ADDRESS_PC = "192.168.63.112"

PC_IP_WIFI     = "172.20.10.11"
BOARD_IP_WIFI  = "172.20.10.9"
PC_PORT = 3333
BOARD_PORT = 4444

pc_socket_pair = (PC_IP_WIFI, PC_PORT)
board_socket_pair = (BOARD_IP_WIFI, BOARD_PORT)

pc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('pc socket created!')
pc_socket.bind(pc_socket_pair)
print('pc socket binded to %s port'%(PC_PORT))

board_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('board socket created!')
# board_socket.bind(board_socket_pair)
# print('board socket binded to %s port'%(BOARD_PORT))

# while True:
#     send data to board
#     sent_bytes = board_socket.sendto(response_message, board_socket_pair)
#     print('message %s sent, size %i bytes'%(response_message, sent_bytes))

#     time.sleep(5)

#     # get data from board
#     print('Waiting data from port %i'%(PC_PORT))
#     data, addr = pc_socket.recvfrom(128)
#     print('Received message: %s\n'%(data.decode()))

#     time.sleep(1)