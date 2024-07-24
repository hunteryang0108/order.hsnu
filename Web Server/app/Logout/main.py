import sqlite3
import json
from datetime import datetime as dt

def load_template(content, script, style):
    TEMPLATE_PAGE = open('./app/Template/html/template.html', 'r', encoding='UTF-8').read()
    page = TEMPLATE_PAGE.format(**locals())
    return ' '.join(page.replace('\n', '').split()).encode('UTF-8')

def handle(request):
    try:
        cookies = request.headers.get('cookie').replace(' ', '').split(';')
        cookie = {i.split('=')[0]: i.split('=')[1] for i in cookies}
        id = cookie.get('session')
        if not id:
            raise ValueError
        session = sqlite3.connect("./db/session.db")
        cursor = session.execute('SELECT account FROM session WHERE id = ?', (id,))
        account = cursor.fetchone()
        if not account:
            raise ValueError
        session.execute('DELETE FROM session WHERE id = ?', (id,))
        session.commit()
        if request.method in ('GET', 'HEAD'):
            request.initialize_response_header()
            request.response_header.update({'Set-Cookie': f'session=; path=/; Expires={dt.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}; HttpOnly'})
            request.response_header.update({'Location': '/'})
            request.send_header(302)
            if request.method == 'GET':
                request.connection.sendall(page)
        else:
            request.send_error(405, f'Request Method Not Supported: {request.method}')
    except:
        request.initialize_response_header()
        request.response_header.update({'Location': '/'})
        request.send_header(302)
