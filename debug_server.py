from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

address = ('localhost', 8080)


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("-" * 120)
        print('[GET] path = {}'.format(self.path))

        parsed_path = urlparse(self.path)
        print('parsed: path = {}, query = {}'.format(parsed_path.path, parse_qs(parsed_path.query)))

        print('headers\r\n-----\r\n{}-----'.format(self.headers))

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_GET')

    def do_PUT(self):
        print("-" * 120)
        print('[PUT] path = {}'.format(self.path))

        parsed_path = urlparse(self.path)
        print('parsed: path = {}, query = {}'.format(parsed_path.path, parse_qs(parsed_path.query)))

        print('headers\r\n-----\r\n{}-----'.format(self.headers))

        content_length = int(self.headers['content-length'])

        print('body = {}'.format(self.rfile.read(content_length).decode('utf-8')))

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_POST')

    def do_POST(self):
        print("-" * 120)
        print('[POST] path = {}'.format(self.path))

        parsed_path = urlparse(self.path)
        print('parsed: path = {}, query = {}'.format(parsed_path.path, parse_qs(parsed_path.query)))

        print('headers\r\n-----\r\n{}-----'.format(self.headers))

        content_length = int(self.headers['content-length'])

        print('body = {}'.format(self.rfile.read(content_length).decode('utf-8')))

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_POST')


def main(*args, **kwargs):
    with HTTPServer(address, MyHTTPRequestHandler) as server:
        server.serve_forever()


def __entry_point():
    import argparse
    parser = argparse.ArgumentParser(
        description=u'',  # プログラムの説明
    )
    # parser.add_argument("args", nargs="*")
    # parser.add_argument("--some-option")
    # parser.add_argument("--int-value", type=int)
    # parser.add_argument('--move', choices=['rock', 'paper', 'scissors'])
    main(**dict(parser.parse_args()._get_kwargs()))


if __name__ == '__main__':
    __entry_point()
