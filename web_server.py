import os
import socket
import sys
import threading

PORT = 8080
SERVER_NAME = 'Python-webserver'

if len(sys.argv) != 4:
    print('python3 {} <document root> <backlog> <threads>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', PORT))
server_socket.listen(int(sys.argv[2]))

print('Startup ' + SERVER_NAME)


def exchange_connection(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    request = request[0:request.find('\r\n')].split()

    if len(request) != 3 or not request[2].startswith('HTTP/'):
        client_socket.close()
        return

    is_get = request[0] == 'GET'
    if not (is_get or request[0] == 'HEAD'):
        client_socket.close()
        return

    if request[1].endswith('/'):
        request[1] += 'index.html'

    file_path = sys.argv[1] + request[1]
    if os.access(file_path, os.R_OK):
        client_socket.send(('HTTP/1.0 200 OK\r\n'
                            'Server: ' +
                            SERVER_NAME +
                            '\r\n'
                            'Connection: Close\r\n'
                            'Content-Length: ' +
                            str(os.path.getsize(file_path)) +
                            '\r\n\r\n').encode('utf-8'))
        if is_get:
            client_socket.sendfile(open(file_path, 'rb'))
    else:
        client_socket.send(('HTTP/1.0 404 Not Found\r\n'
                            'Server: ' +
                            SERVER_NAME +
                            '\r\n'
                            'Connection: Close\r\n'
                            'Content-Length: 80\r\n\r\n' +
                            '<html><head><title>404 Not Found</title></head>'
                            '<body>404 Not Found</body></html>').encode('utf-8'))
    client_socket.close()


def thread_doing():
    while True:
        exchange_connection(server_socket.accept()[0])


t = None
for i in range(int(sys.argv[3])):
    t = threading.Thread(target=thread_doing)
    t.start()
t.join()
