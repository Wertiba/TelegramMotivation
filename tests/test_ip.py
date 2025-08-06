from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<h1>Hello World!</h1>".encode("utf-8"))

# 0.0.0.0 — слушать на всех интерфейсах
server = ThreadingHTTPServer(("0.0.0.0", 80), SimpleHandler)
# server = HTTPServer(("0.0.0.0", 80), SimpleHandler)
server.serve_forever()
