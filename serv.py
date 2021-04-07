from socket import *
import subprocess
import os
import sys


def test_serv(port_num):
    server_socket = socket(AF_INET, SOCK_STREAM)
    port = port_num
    transfer_port = port + 69
    server_socket.bind(('', port))

    server_socket.listen(1)
    print('The server is ready to receive.')
    connection_socket, addr = server_socket.accept()
    while 1:
        tmp_buffer, _ = recv_byte(connection_socket)
        tokens = tmp_buffer.decode().split()

        if tmp_buffer:
            print('Client\'s command: ', tmp_buffer.decode())

        if tokens[0].lower() == 'ls':
            ls_serv(connection_socket, tokens)

        if tokens[0].lower() == 'put':
            put_serv(connection_socket, tokens[1], transfer_port)

        if tokens[0].lower() == 'get':
            get_serv(connection_socket, tokens[1], transfer_port)

        if tokens[0].lower() == 'quit':
            break

    connection_socket.close()
    print('Server closed.')


def ls_serv(_socket, cmd):
    # run ls command and save result to result.txt
    subprocess.run(['dir', 'upload', '/n', '>', 'result.txt'], shell=True)

    # send result to client
    f = open('result.txt', 'rb')
    data = f.read()
    send_byte(_socket, data)
    f.close()
    print('SUCCESS: ls')
    return


def put_serv(_socket, filename, file_port):
    # prepare transfer port
    file = 'upload/' + os.path.basename(filename)
    file_socket = socket(AF_INET, SOCK_STREAM)
    file_socket.bind(('', file_port))
    file_socket.listen(1)
    connection_socket, addr = file_socket.accept()

    # receive file
    data, byte_recv = recv_byte(connection_socket)

    # write buffer to file
    f = open(file, 'wb')
    f.write(data)
    f.close()
    connection_socket.close()
    print("Received: {}".format(filename))
    print("File size: {} bytes".format(os.path.getsize(file)))
    print("Total bytes received: {} bytes".format(byte_recv))
    print('SUCCESS: put')
    return


def get_serv(_socket, filename, file_port):
    # check file exist
    file = 'upload/' + filename
    if not os.path.exists(file):
        send_byte(_socket, b'404')  # file not found
        print('File {} not found on server.'.format(filename))
        print('FAILURE: get')
        return

    # prepare file transfer port
    send_byte(_socket, b'200')  # file found, prepare to transfer
    file_socket = socket(AF_INET, SOCK_STREAM)
    file_socket.bind(('', file_port))
    file_socket.listen(1)
    connection_socket, addr = file_socket.accept()

    # send file
    f = open(file, 'rb')
    data = f.read()
    byte_sent = send_byte(connection_socket, data)
    f.close()
    connection_socket.close()
    print('Sent file: ', filename)
    print('File size: {} bytes'.format(os.path.getsize(file)))
    print('Total bytes sent: {} bytes'.format(byte_sent))
    print('SUCCESS: get')
    return


def recv_byte(_socket):
    num_recv = 0
    recv_buff = b''
    size = _socket.recv(10)
    num_recv += len(size)
    size = int(size.decode())

    # Keep receiving till all is received
    while len(recv_buff) < size:

        # Attempt to receive bytes
        tmp_buff = _socket.recv(size)

        # The other side has closed the socket
        if not tmp_buff:
            break

        # Add the received bytes to the buffer
        recv_buff += tmp_buff
        num_recv += len(tmp_buff)

    return recv_buff, num_recv


def send_byte(_socket, data):
    size = str(len(data))
    while len(size) < 10:
        size = '0' + size
    temp_data = size.encode() + data

    num_sent = 0
    while num_sent < len(temp_data):
        num_sent += _socket.send(temp_data[num_sent:])
    return num_sent


# -------------- main-------------
if len(sys.argv) != 2:
    print('Usage: serv.py <port number>')
    exit()
port_number = int(sys.argv[1])
print('Port number: ', port_number)
test_serv(port_number)
