import sqlite3
import json

def handle(request):
    if request.method == 'GET':
        classes = dict()
        db = sqlite3.connect('./db/orders.db')
        data = db.execute('SELECT class FROM orders WHERE meal="o3oGBcOrFg"').fetchall()
        for i in data:
            if i[0] in classes:
                classes[i[0]] += 1
            else:
                classes[i[0]] = 1
        response = json.dumps(classes).encode('UTF-8')
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(response)})
        request.send_header(200)
        request.connection.sendall(response)
    elif request.method == 'POST':
        try:
            cookies = request.headers.get('cookie').replace(' ', '').split(';')
            cookie = {i.split('=')[0]: i.split('=')[1] for i in cookies}
            id = cookie.get('session')
            if not id:
                raise ValueError
            session = sqlite3.connect('./db/session.db')
            account = session.execute('SELECT account FROM session WHERE id = ?', (id,)).fetchone()
            if not account:
                raise ValueError
            studentdb = sqlite3.connect('./db/student.db')
            user = studentdb.execute('SELECT id, class FROM account WHERE id = ?', (account[0],)).fetchone()
            if not user:
                raise ValueError
            meal = request.sread.read(int(request.headers['content-length'])).decode('UTF-8')
            meals = sqlite3.connect('./db/meals.db')
            mealid = meals.execute('SELECT * FROM meals WHERE id = ?', (meal,)).fetchone()
            if not mealid:
                raise ValueError
            orderdb = sqlite3.connect('./db/orders.db')
            if not orderdb.execute('SELECT id FROM orders WHERE id = ?', (user[0],)).fetchone():
                orderdb.execute('INSERT INTO orders VALUES (?, ?, ?)', (user[0], user[1], meal))
                orderdb.commit()
            response = "success".encode('UTF-8')
            request.initialize_response_header()
            request.response_header.update({'Content-Type': 'text/plain; charset=UTF-8'})
            request.response_header.update({'Content-Length': len(response)})
            request.send_header(200)
            request.connection.sendall(response)
        except:
            response = "error".encode('UTF-8')
            request.initialize_response_header()
            request.response_header.update({'Content-Type': 'text/plain; charset=UTF-8'})
            request.response_header.update({'Content-Length': len(response)})
            request.send_header(400)
            request.connection.sendall(response)
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')