import base64
import json
import os
import sqlite3
from io import BytesIO
from PIL import Image

def crop_image(image):
    width, height = image.size
    if width == height:
        return image
    offset = int(abs(height - width) / 2)
    if width > height:
        image = image.crop([offset, 0, width - offset, height])
    else:
        image = image.crop([0, offset, width, height - offset])
    width, height = image.size
    if width > 512:
        image = image.resize((512, 512), Image.ANTIALIAS)
    return image

def gen_id(db, table):
    while True:
        id = base64.urlsafe_b64encode(os.urandom(7)).rstrip(b'=').decode('UTF-8')
        cursor = db.execute(f'SELECT * FROM {table} WHERE id = ?', (id, ))
        if not cursor.fetchone():
            return id

def handle(request):
    try:
        cookies = request.headers.get('cookie').replace(' ', '').split(';')
        cookie = {i.split('=')[0]: i.split('=')[1] for i in cookies}
        id = cookie.get('session')
        if not id:
            raise ValueError
        session = sqlite3.connect('./db/session.db')
        cursor = session.execute('SELECT account FROM session WHERE id = ?', (id,))
        account = cursor.fetchone()
        if not account:
            raise ValueError
        restaurant = sqlite3.connect('./db/restaurant.db')
        cursor = restaurant.execute('SELECT username FROM account WHERE username = ?', (account[0],))
        user =  cursor.fetchone()
        if not user:
            raise ValueError
        if request.method in ('GET', 'HEAD'):
            CONTENT = open('./app/DishEdit/html/content.html', 'r', encoding='UTF-8').read()
            STYLE = open('./app/DishEdit/html/style.html', 'r', encoding='UTF-8').read()
            SCRIPT = open('./app/DishEdit/html/script.html', 'r', encoding='UTF-8').read()
            page = json.dumps({'style': STYLE, 'script': SCRIPT, 'html': CONTENT}).encode('UTF-8')
            request.initialize_response_header()
            request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
            request.response_header.update({'Content-Length': len(page)})
            request.send_header(200)
            if request.method == 'GET':
                request.connection.sendall(page)
        elif request.method == 'POST':
            path = request.pop_path()
            data = request.sread.read(int(request.headers['content-length'])).decode('UTF-8')
            if path == 'image':
                url_image = data.split(',', 1)
                try:
                    b64img = BytesIO(base64.b64decode(url_image[1]))
                    Image.open(b64img).verify()
                    img = Image.open(b64img)
                    if img.format in ('PNG', 'JPEG'):
                        img = crop_image(img).convert('RGB')
                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", optimize=True, quality=30)
                    else:
                        raise ValueError
                    image = buffer.getvalue()
                    db = sqlite3.connect("./db/meals.db")
                    id = gen_id(db, 'photo')
                    db.execute('INSERT INTO photo VALUES (?, ?)', (id, image))
                    db.commit()
                    response = json.dumps({'status': 'success', 'id': id}).encode('UTF-8')
                except:
                    response = json.dumps({'status': 'error', 'msg': '圖片解析失敗'}).encode('UTF-8')
            elif path == 'save':
                try:
                    meals = json.loads(data)
                    id = meals.pop('id', False)
                    if id:
                        db = sqlite3.connect("./db/meals.db")
                        cursor = db.execute(f'SELECT * FROM photo WHERE id = ?', (id, ))
                        if not cursor.fetchone():
                            raise ValueError
                        db.execute('INSERT INTO meals VALUES (?, ?)', (id, json.dumps(meals)))
                        db.commit()
                        response = json.dumps({'status': 'success'}).encode('UTF-8')
                    else:
                        raise ValueError
                except:
                    response = json.dumps({'status': 'error', 'msg': '儲存失敗'}).encode('UTF-8')
            else:
                response = json.dumps({'status': 'error', 'msg': 'Error'}).encode('UTF-8')
            request.initialize_response_header()
            request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
            request.response_header.update({'Content-Length': len(response)})
            request.send_header(200)
            request.connection.sendall(response)
        else:
            request.send_error(405, f'Request Method Not Supported: {request.method}')
    except:
        response = json.dumps({'html': '<a href="/Login/Restaurant">請先登入餐廳帳號</a>'}).encode('UTF-8')
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'application/json; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(response)})
        request.send_header(200)
        request.connection.sendall(response)
