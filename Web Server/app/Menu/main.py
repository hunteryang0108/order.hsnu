def load_template(content, script, style):
    TEMPLATE_PAGE = open('./app/Template/html/template.html', 'r', encoding='UTF-8').read()
    page = TEMPLATE_PAGE.format(**locals())
    return ' '.join(page.replace('\n', '').split()).encode('UTF-8')

def handle(request):
    if request.method in ('GET', 'HEAD'):
        CONTENT = open('./app/Menu/html/content.html', 'r', encoding='UTF-8').read()
        STYLE = open('./app/Menu/html/style.html', 'r', encoding='UTF-8').read()
        SCRIPT = open('./app/Menu/html/script.html', 'r', encoding='UTF-8').read()
        page = load_template(CONTENT, SCRIPT, STYLE)
        request.initialize_response_header()
        request.response_header.update({'Content-Type': 'text/html; charset=UTF-8'})
        request.response_header.update({'Content-Length': len(page)})
        request.send_header(200)
        if request.method == 'GET':
            request.connection.sendall(page)
    else:
        request.send_error(405, f'Request Method Not Supported: {request.method}')