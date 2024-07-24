from server.http import HttpServer

addr = '0.0.0.0', 8080

def main():
    server = HttpServer(addr)
    print(f'[*] Serving on {addr[0]}:{addr[1]}')
    server.run()

if __name__ == '__main__':
    main()