from socket import *
import subprocess
import os
import sys


def test_serv(port_num):
    port = port_num
    transfer_port = port + 69
    server_socket = None
    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('', port))
    except (ValueError, Exception):
        print('FAILURE: cannot open socket.')
        print('Closing server.')
        exit()

    server_socket.listen(1)
    print('The server is ready to receive.')
    connection_socket, addr = server_socket.accept()
    while 1:
        tmp_buffer, _ = recv_byte(connection_socket)
        tokens = tmp_buffer.decode().split()

        if tmp_buffer:
            print('\nClient\'s command: ', tmp_buffer.decode())

        if tokens[0].lower() == 'ls':
            try:
                ls_serv(connection_socket, tokens)
            except (ValueError, Exception):
                print('FAILURE: ls')

        if tokens[0].lower() == 'put':
            try:
                put_serv(connection_socket, tokens[1], transfer_port)
            except (ValueError, Exception):
                print('FAILURE: put')

        if tokens[0].lower() == 'get':
            try:
                get_serv(connection_socket, tokens[1], transfer_port)
            except (ValueError, Exception):
                print('FAILURE: get')

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
    try:
        file_socket.bind(('', file_port))
    except (ValueError, Exception):
        send_byte(_socket, b'500')  # Server error
        print('FAILURE: put - cannot open transfer port')
        return
    file_socket.listen(1)
    send_byte(_socket, b'200')  # tell client that the server is ready
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
    try:
        file_socket.bind(('', file_port))
    except (ValueError, Exception):
        send_byte(_socket, b'500')  # Server error
        print('FAILURE: get - cannot open transfer port')
        return
    file_socket.listen(1)
    send_byte(_socket, b'200')  # tell client that the server is ready
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
port_number = 0
try:
    port_number = int(sys.argv[1])
except (ValueError, Exception):
    print('Failure: Invalid port number.')
    exit()
if port_number < 0:
    print('Failure: Negative port number.')
    exit()
print('Port number: ', port_number)

# create upload folder if not exist
if not os.path.exists('upload'):
    os.mkdir('upload')
test_serv(port_number)
