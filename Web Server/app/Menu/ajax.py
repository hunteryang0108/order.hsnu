import sqlite3
import json

def handle(request):
    if request.method in ('GET', 'HEAD'):
        path = request.pop_path()
        if not path:
            CONTENT = open('./app/Menu/html/content.html', 'r', encoding='UTF-8').read()
            STYLE = open('./app/Menu/html/style.html', 'r', encoding='UTF-8').read()
            SCRIPT = open('./app/Menu/html/script.html', 'r', encoding='UTF-8').read()
            response = json.dumps({'style': STYLE, 'script': SCRIPT, 'html': CONTENT}).encode('UTF-8')
        elif path == 'meals':
            db = sqlite3.connect("./db/meals.db")
            cursor = db.execute('SELECT * FROM meals')
            meals = cursor.fetchall()
            response = {'meals': []}
            for i in meals:
                data = json.loads(i[1])
                data.update({'id': i[0]})
                response['meals'].append(data)
            response = json.dumps(response).encode('UTF-8')
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(response)})
        request.send_header(200)
        if request.method == 'GET':
            request.connection.sendall(response)
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')