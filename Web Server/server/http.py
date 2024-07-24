import html
import os
import socket
import ssl
import sys
import threading
from datetime import datetime as dt
from server import apps
from server.settings import *

class HttpServer:

    def __init__(self, addr):
        self.address = addr
        #self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #self.context.load_verify_locations('./cert/ca.crt')
        #self.context.load_cert_chain(CERTFILE, KEYFILE)
        self.server_bind()

    def server_bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(MAXIMUM_CONNECTION)
        #self.socket = self.context.wrap_socket(self.socket, server_side=True)

    def run(self):
        while True:
            try:
                client, addr = self.socket.accept()
            except:
                continue
            print(f'[*] Accepted from: {addr[0]}:{addr[1]}')
            HandleRequest(client, addr).start()


class HandleRequest(threading.Thread):

    def __init__(self, client, addr):
        threading.Thread.__init__(self)
        self.connection = client
        self.addr = addr
        self.sread = client.makefile('rb')

    def parse_request(self):
        request_line = self.sread.readline(MAXIMUM_REQUESTLINE + 1).rstrip()
        request_line = request_line.decode('UTF-8')
        if request_line:
            if len(request_line) > MAXIMUM_REQUESTLINE:
                self.send_error(414, f'Request URI Too Long: {request_line}')
                return False
            request = request_line.split()
            if len(request) == 2:
                self.keep_alive = False
                self.connection.sendall(b'HTTP/0.9 Version Not Supported')
                return False
            elif len(request) == 3:
                try:
                    method, target, version = request
                    if not version.startswith('HTTP/'):
                        raise ValueError
                    version_number = version[5:].split('.', 1)
                    if len(version_number) != 2:
                        raise ValueError
                    version_number = tuple(map(int, version_number))
                except ValueError:
                    self.send_error(400, f'Invalid HTTP Version: {version}')
                    return False
                if version_number == (1, 1):
                    self.keep_alive = True
                else:
                    self.send_error(505, f'HTTP Version Not Supported: {version}')
                    return False
                self.method = method
                self.target = target
                self.version = version
            else:
                self.send_error(400, f'Invalid Request Syntax: {request_line}')
                return False
        else:
            raise socket.timeout
        return True

    def parse_header(self):
        headers = dict()
        while True:
            header_line = self.sread.readline(MAXIMUM_REQUESTLINE + 1).rstrip()
            if len(header_line):
                header_line = header_line.decode('UTF-8')
                if len(header_line) > MAXIMUM_REQUESTLINE:
                    self.send_error(431, f'Request Header Too Long: {header_line}')
                    return False
                try:
                    header = [i.strip() for i in header_line.split(':', 1)]
                    if len(header) == 2:
                        if 0 in map(len, header):
                            raise ValueError
                        else:
                            if header[0].lower() in headers.keys():
                                raise ValueError
                            else:
                                headers.update({header[0].lower(): header[1]})
                            if len(headers) > MAXIMUM_HEADERS:
                                self.send_error(431, f'Maximum Headers: {MAXIMUM_HEADERS}')
                                return False
                    else:
                        raise ValueError
                except:
                    self.send_error(400, f'Invalid Header Syntax: {header_line}')
                    return False
            else:
                break
        host = headers.pop('host', '')
        if host.split(':', 1)[0] != HOST:
            self.send_error(400, f'Invalid Host: {host}')
            return False
        user_agent = headers.pop('user-agent', '')
        if 'Trident' in user_agent:
            self.send_error(200, f'IE不支援です')
            return False
        connection = headers.pop('connection', '')
        if connection.lower() == 'keep-alive':
            self.keep_alive = True
        elif connection.lower() == 'close':
            self.keep_alive = False
        expect_continue = headers.pop('except', '')
        if expect_continue.lower() == '100-continue' :
            self.expect_continue = True
        else:
            self.expect_continue = False
        self.headers = headers
        return True

    def start_app(self):
        self.path = self.target
        if self.path == '/':
            apps.index.handle(self)
        elif self.path == '/favicon.ico':
            with open('./server/res/favicon.ico', 'rb') as f:
                response = f.read()
            self.initialize_response_header()
            self.response_header.update({'Content-Type': 'image/x-icon'})
            self.response_header.update({'Content-Length': len(response)})
            self.send_header(200)
            self.connection.sendall(response)
        else:
            self.path = self.path.lstrip('/')
            target = self.pop_path()
            if target in apps.APIs:
                api = apps.APIs.get(target)
                app = api.get(self.pop_path())
            else:
                app = apps.WSGI.get(target)
            if app:
                app.handle(self)
            else:
                self.send_error(404, 'Page Not Found')
                return False
        return True

    def handle(self):
        try:
            if not self.parse_request():
                return
            if not self.parse_header():
                return
            if not self.start_app():
                return
        except:
            self.keep_alive = False
            self.connection.close()
            return

    def html_format(self, path, render=None):
        page = open(path, 'r', encoding='UTF-8').read()
        if render:
            page = page.format(**render)
        return ' '.join(page.replace('\n', '').split()).encode('UTF-8')

    def chunked_transfer(self, path):
        eof = os.path.getsize(path)
        with open(path, 'rb') as f:
            while True:
                chunk = f.readline(255)
                self.connection.sendall((hex(len(chunk))[2:].upper() + '\r\n').encode('UTF-8'))
                if not chunk.endswith(b'\r\n'):
                    chunk += b'\r\n'
                self.connection.sendall(chunk + b'\r\n')
                if f.tell() == eof:
                    break
        self.connection.sendall('0\r\n\r\n'.encode('UTF-8'))

    def pop_path(self):
        path = self.path.split('/', 1)
        if len(path) != 2:
            path.append('')
        target, self.path = path
        return target
        
    def initialize_response_header(self):
        self.response_header = dict()
        self.response_header.update({'Date': dt.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')})
        self.response_header.update({'Server': 'Python/' + sys.version.split(None, 1)[0]})
        self.response_header.update({'Connection': 'Close'})

    def send_header(self, code):
        header = f'{HTTP_VERSION} {code} {STATUS_CODE[code]}\r\n'
        for i in self.response_header:
            header += f'{i}: {self.response_header[i]}\r\n'
        header += '\r\n'
        self.connection.sendall(header.encode('UTF-8'))

    def send_error(self, code, explain):
        message = STATUS_CODE[code]
        explain = html.escape(explain)
        page = self.html_format(ERROR_PAGE, locals())
        self.initialize_response_header()
        self.response_header.update({'Content-Type': 'text/html; charset=UTF-8'})
        self.response_header.update({'Content-Length': len(page)})
        self.send_header(code)
        self.connection.sendall(page)

    def run(self):
        self.keep_alive = False
        self.handle()
