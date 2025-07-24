from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'message': 'Hello, this is a fake API response!'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        # Try to parse JSON body once, since many endpoints use it
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            data = {}

        if self.path == '/pulumi/account':
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'id': 5, 'data': data}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/pulumi/account/MCNTesting/organization':
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'id': 3, 'data': data}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path.startswith('/cloud/vpc'):
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "id": "vpc-123456",
                "message": "VPC created successfully",
                "data": data
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'🚀 Fake server running at http://localhost:{port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
