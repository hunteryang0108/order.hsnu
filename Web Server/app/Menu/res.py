import mimetypes
import os
import sqlite3

RES_PATH = './app/Menu/res/'

def handle(request):
    path = request.target.strip('/').split('/')[2:]
    if len(path) == 1:
        if request.method in ('GET', 'HEAD'):
            target = os.path.join(RES_PATH, request.target.strip('/').split('/')[-1])
            if os.path.isfile(target):
                file = open(target, 'rb').read()
                request.initialize_response_header()
                request.response_header.update({'Content-Type': f'{mimetypes.guess_type(target)[0]}'})
                request.response_header.update({'Content-Length': len(file)})
                request.send_header(200)
                if request.method == 'GET':
                    request.connection.sendall(file)
            else:
                request.send_error(404, f'File Not Found: {request.target}')
        else:
            request.send_error(405, f'Request Method Not Supported: {request.method}')
    elif path[0] == 'image':
        if request.method in ('GET', 'HEAD'):
            db = sqlite3.connect("./db/meals.db")
            cursor = db.execute('SELECT data FROM photo WHERE id = ?', (path[1][:-4], ))
            image = cursor.fetchone()[0]
            if image:
                request.initialize_response_header()
                request.response_header.update({'Content-Type': 'image/jpg'})
                request.response_header.update({'Content-Length': len(image)})
                request.send_header(200)
                if request.method == 'GET':
                    request.connection.sendall(image)
            else:
                request.send_error(404, f'File Not Found: {request.target}')
        else:
            request.send_error(405, f'Request Method Not Supported: {request.method}')
        