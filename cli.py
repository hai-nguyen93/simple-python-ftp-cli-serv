from socket import *
import sys
import os


def show_help():
    print('------------------------------')
    print('commands help:')
    print('ls : list files on the server')
    print('push <filename> : upload <filename> to the server')
    print('get <filename> : download <filename> from the server')
    print('help : show help')
    print('quit : disconnect from the server and quit the application')
    print('------------------------------')


def send_cmd(_socket, _cmd):
    # prepend 10 bytes containing the size of cmd
    size = str(len(_cmd))
    while len(size) < 10:
        size = '0' + size
    temp_cmd = size + _cmd

    # send cmd
    num_sent = 0
    while num_sent < len(temp_cmd):
        num_sent += _socket.send(temp_cmd.encode()[num_sent:])


def put_cli(_socket, filename, file_port):
    file = open(filename, 'rb')
    if not file:
        print('Error: File not found!')
        return

    # get server response code on opening transfer port
    code, _ = recv_byte(_socket)
    if code.decode() == '500':
        print('FAILURE: error in server')
        return

    # code == 200: server is ready
    # connect to new port
    file_socket = socket(AF_INET, SOCK_STREAM)
    file_socket.connect((_socket.getsockname()[0], file_port))

    # send file
    data = file.read()
    byte_sent = send_byte(file_socket, data)
    print('Sent: ', filename)
    print('File size: {} bytes'.format(os.path.getsize(filename)))
    print('Total bytes sent: {} bytes'.format(byte_sent))
    file_socket.close()
    print('SUCCESS: put')
    return


def get_cli(_socket, filename, file_port):
    file = 'download/' + filename

    # check server response code on file existence
    code, _ = recv_byte(_socket)
    if code.decode() == '404':
        print('Error: file {} not found on server.'.format(filename))
        return

    # code == 200, found file to download

    # get server response code on opening transfer port
    code, _ = recv_byte(_socket)
    if code.decode() == '500':
        print('FAILURE: error in server')
        return

    # code == 200: server is ready
    # connect to new port
    file_socket = socket(AF_INET, SOCK_STREAM)
    file_socket.connect((_socket.getsockname()[0], file_port))

    # receive file
    data, byte_recv = recv_byte(file_socket)
    f = open(file, 'wb')
    f.write(data)
    f.close()
    file_socket.close()
    print('Received: ', filename)
    print("File size: {} bytes".format(os.path.getsize(file)))
    print("Total bytes received: {} bytes".format(byte_recv))
    print('SUCCESS: get')
    return


def ls_cli(_socket, _cmd):
    # get result from server
    result, _ = recv_byte(_socket)
    print(result.decode())
    print('SUCCESS: ls')
    return


def send_byte(_socket, data):
    size = str(len(data))
    while len(size) < 10:
        size = '0' + size
    temp_data = size.encode() + data

    num_sent = 0
    while num_sent < len(temp_data):
        num_sent += _socket.send(temp_data[num_sent:])
    return num_sent


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


# ---------main--------
if len(sys.argv) != 3:
    print('Usage: cli.py <host> <port number>')
    exit()

# create download folder if not exists
if not os.path.exists('download'):
    os.mkdir('download')

# set up socket, port
server_name = sys.argv[1]
port = 0
try:
    port = int(sys.argv[2])
except (ValueError, Exception):
    print('Failure: Invalid port number.')
    exit()
if port < 0:
    print('Failure: Negative port number.')
    exit()
print('Server: ', server_name)
print('Port number: ', port)
transfer_port = port + 69  # port for transferring file

# connect to server
client_socket = None
try:
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, port))
except (ValueError, Exception):
    print('Cannot connect to server.')
    print('Closing client.')
    exit()

# client is ready to get input
print('\nWelcome to FTP client:')
show_help()

while 1:
    cmd = input('\nftp> ')
    tokens = cmd.split()
    # print(cmd)

    if tokens[0] == 'ls':
        try:
            send_cmd(client_socket, cmd)
            ls_cli(client_socket, tokens)
        except (ValueError, Exception):
            print('FAILURE: ls')

    if tokens[0] == 'put':
        if not os.path.exists(tokens[1]):
            print('Error: file {} not found'.format(tokens[1]))
            continue

        try:
            send_cmd(client_socket, cmd)
            put_cli(client_socket, tokens[1], transfer_port)
        except (ValueError, Exception):
            print('FAILURE: put')

    if tokens[0] == 'get':
        try:
            send_cmd(client_socket, cmd)
            get_cli(client_socket, tokens[1], transfer_port)
        except (ValueError, Exception):
            print('FAILURE: get')

    if tokens[0] == 'quit':
        try:
            send_cmd(client_socket, cmd)
        except (ValueError, Exception):
            print('FAILURE: quit')
        break

    if tokens[0] == 'help':
        show_help()

client_socket.close()
