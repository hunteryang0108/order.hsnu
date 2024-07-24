import base64
import json
import os
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime as dt

google_login = 'https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/userinfo.email&response_type=code&prompt=select_account&client_id=520762632376-43mm1eq5qve33gr6960ccc2isanp2k2a.apps.googleusercontent.com&redirect_uri=http://localhost:8080/Login/Oauth/Oauth&hd=gs.hs.ntnu.edu.tw'

def load_template(content, script, style):
    TEMPLATE_PAGE = open('./app/Template/html/template.html', 'r', encoding='UTF-8').read()
    page = TEMPLATE_PAGE.format(**locals())
    return ' '.join(page.replace('\n', '').split()).encode('UTF-8')

def gen_id(db, table, length):
    while True:
        id = base64.urlsafe_b64encode(os.urandom(length)).rstrip(b'=').decode('UTF-8')
        cursor = db.execute(f'SELECT * FROM {table} WHERE id = ?', (id, ))
        if not cursor.fetchone():
            return id

def student(request):
    if request.method in ('GET', 'HEAD'):
        request.initialize_response_header()
        request.response_header.update({'Location': google_login})
        request.send_header(302)
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')

def restaurant(request):
    if request.method in ('GET', 'HEAD'):
        CONTENT = open('./app/Login/html/Restaurant/content.html', 'r', encoding='UTF-8').read()
        STYLE = open('./app/Login/html/Restaurant/style.html', 'r', encoding='UTF-8').read()
        SCRIPT = open('./app/Login/html/Restaurant/script.html', 'r', encoding='UTF-8').read()
        page = load_template(CONTENT, STYLE, SCRIPT)
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'text/html; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(page)})
        request.send_header(200)
        if request.method == 'GET':
            request.connection.sendall(page)
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')

def oauth(request):
    try:
        code =  {i.split('=', 1)[0]: i.split('=', 1)[1] for i in request.path.split('?', 1)[1].split('&')}['code']
        data = {
            'code': urllib.parse.unquote(code),
            'client_id': '520762632376-43mm1eq5qve33gr6960ccc2isanp2k2a.apps.googleusercontent.com',
            'client_secret': '',
            'redirect_uri': 'http://localhost:8080/Login/Oauth/Oauth',
            'grant_type': 'authorization_code'
        }
        auth = urllib.request.Request('https://www.googleapis.com/oauth2/v3/token', data=urllib.parse.urlencode(data).encode('UTF-8'), headers={'Content-Type':'application/x-www-form-urlencoded'}, method='POST')
        token = json.loads(urllib.request.urlopen(auth).read().decode("UTF-8"))["access_token"]
        api = urllib.request.Request(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}')
        mail = json.loads(urllib.request.urlopen(api).read().decode("UTF-8"))['email']
        user = mail.split('@', 1)[0]
        studentdb = sqlite3.connect('./db/student.db')
        cursor = studentdb.execute('SELECT id FROM account WHERE id=?', (user, ))
        if cursor.fetchone():
            session = sqlite3.connect('./db/session.db')
            id = gen_id(session, 'session', 15)
            session.execute('INSERT INTO session VALUES (?, ?)', (id, user))
            session.commit()
        else:
            request.send_error(404, f'Account Not Registered: {user}')
            return
        request.initialize_response_header()
        request.response_header.update({'Location': '/'})
        request.response_header.update({'Set-Cookie': f'session={id}; path=/; Expires={dt.utcnow().replace(month=dt.utcnow().month + 2).strftime("%a, %d %b %Y %H:%M:%S GMT")}; Secure'})
        request.send_header(302)
    except Exception as e:
        print(e)
        request.send_error(404, 'Page Not Found')

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
