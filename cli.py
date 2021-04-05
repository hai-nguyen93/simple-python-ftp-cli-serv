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

    # check server response code
    code, _ = recv_byte(_socket)
    if code.decode() == '404':
        print('Error: file {} not found on server.'.format(filename))
        return

    # code == 200, found file to download
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

server_name = sys.argv[1]
server_port = int(sys.argv[2])
print('Server: ', server_name)
print('Port number: ', server_port)
transfer_port = server_port + 69
client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect((server_name, server_port))
except error:
    print('Cannot connect to server.')
    print('Closing program.')
    exit()

print('\nWelcome to FTP client:')
show_help()

while 1:
    cmd = input('ftp> ')
    tokens = cmd.split()
    # print(cmd)

    if tokens[0] == 'ls':
        send_cmd(client_socket, cmd)
        ls_cli(client_socket, tokens)

    if tokens[0] == 'put':
        if not os.path.exists(tokens[1]):
            print('Error: file {} not found'.format(tokens[1]))
            continue

        send_cmd(client_socket, cmd)
        put_cli(client_socket, tokens[1], transfer_port)

    if tokens[0] == 'get':
        send_cmd(client_socket, cmd)
        get_cli(client_socket, tokens[1], transfer_port)

    if tokens[0] == 'quit':
        send_cmd(client_socket, cmd)
        break

    if tokens[0] == 'help':
        show_help()

client_socket.close()
