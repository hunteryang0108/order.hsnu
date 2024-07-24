import mimetypes
import os

RES_PATH = './app/Template/res'

def handle(request):
    if request.method in ('GET', 'HEAD'):
        target = os.path.join(RES_PATH, request.target.strip('/').split('/')[-1])
        if os.path.isfile(target):
            file = open(target, 'rb').read()
            request.initialize_response_header()
            request.response_header.update({'Content-Type': f'{mimetypes.guess_type(target)[0]}; charset=UTF-8'})
            request.response_header.update({'Content-Length': len(file)})
            request.send_header(200)
            if request.method == 'GET':
                request.connection.sendall(file)
        else:
            request.send_error(404, f'File Not Found: {request.target}')
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')