from http.server import HTTPServer, SimpleHTTPRequestHandler

print("Webサーバー起動...")
print("アクセス: http://<IPアドレス>:8000/test.jpg")
print("停止: Ctrl+C")

server = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
server.serve_forever()

