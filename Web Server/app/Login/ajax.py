import base64
import json
import os
import sqlite3
import hashlib
from datetime import datetime as dt

def gen_id(db, table, length):
    while True:
        id = base64.urlsafe_b64encode(os.urandom(length)).rstrip(b'=').decode('UTF-8')
        cursor = db.execute(f'SELECT * FROM {table} WHERE id = ?', (id, ))
        if not cursor.fetchone():
            return id

def student(request):
    if request.method in ('GET', 'HEAD'):
        CONTENT = open('./app/Login/html/Student/content.html', 'r', encoding='UTF-8').read()
        STYLE = open('./app/Login/html/Student/style.html', 'r', encoding='UTF-8').read()
        SCRIPT = open('./app/Login/html/Student/script.html', 'r', encoding='UTF-8').read()
        page = json.dumps({'style': STYLE, 'script': SCRIPT, 'html': CONTENT}).encode('UTF-8')
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(page)})
        request.send_header(200)
        if request.method == 'GET':
            request.connection.sendall(page)

def restaurant(request):
    if request.method in ('GET', 'HEAD'):
        CONTENT = open('./app/Login/html/Restaurant/content.html', 'r', encoding='UTF-8').read()
        STYLE = open('./app/Login/html/Restaurant/style.html', 'r', encoding='UTF-8').read()
        SCRIPT = open('./app/Login/html/Restaurant/script.html', 'r', encoding='UTF-8').read()
        page = json.dumps({'style': STYLE, 'script': SCRIPT, 'html': CONTENT}).encode('UTF-8')
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(page)})
        request.send_header(200)
        if request.method == 'GET':
            request.connection.sendall(page)
    elif request.method == 'POST':
        request.initialize_response_header()
        data = request.sread.read(int(request.headers['content-length'])).decode('UTF-8')
        try:
            data = json.loads(data)
            username = data.get('username', None)
            password = data.get('password', None)
            sha = hashlib.sha256()
            sha.update(password.encode('UTF-8'))
            passwordhash = sha.hexdigest()
            if username and password:
                account = sqlite3.connect("./db/restaurant.db")
                cursor = account.execute('SELECT username FROM account WHERE username = ? AND password = ?', (username, passwordhash))
                if cursor.fetchone():
                    session = sqlite3.connect("./db/session.db")
                    id = gen_id(session, 'session', 15)
                    session.execute('INSERT INTO session VALUES (?, ?)', (id, username))
                    session.commit()
                    response = json.dumps({'status': 'success'}).encode('UTF-8')
                    request.response_header.update({'Set-Cookie': f'session={id}; path=/; Expires={dt.utcnow().replace(month=dt.utcnow().month + 2).strftime("%a, %d %b %Y %H:%M:%S GMT")}; Secure'})
                else:
                    response = json.dumps({'status': 'error', 'msg': '帳號或密碼錯誤'}).encode('UTF-8')
            else:
                raise ValueError
        except:
            response = json.dumps({'status': 'error', 'msg': '格式錯誤'}).encode('UTF-8')
        request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(response)})
        request.send_header(200)
        request.connection.sendall(response)
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')

def handle(request):
    path = request.pop_path()
    if not path or path == 'Student':
        student(request)
    elif path == 'Restaurant':
        restaurant(request)
    elif path == 'Oauth':
        oauth(request)
    else:
        request.send_error(404, 'Page Not Found')
