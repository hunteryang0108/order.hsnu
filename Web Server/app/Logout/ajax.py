import sqlite3
from datetime import datetime as dt

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
            request.response_header.update({'Location': '/ajax/Menu'})
            request.send_header(302)
        else:
            request.send_error(405, f'Request Method Not Supported: {request.method}')
    except:
        request.initialize_response_header()
        request.response_header.update({'Set-Cookie': f'session=; path=/; Expires={dt.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}; HttpOnly'})
        request.response_header.update({'Location': '/ajax/Menu'})
        request.send_header(302)
