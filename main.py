from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.list_files().encode())
        else:
            self.serve_file()

    def list_files(self):
        file_list = os.listdir('./files')
        response = '<html><body><h1>Files:</h1><ul>'
        for file_name in file_list:
            response += f'<li><a href="/{file_name}" download>{file_name}</a></li>'
        response += '</ul></body></html>'
        return response

    def serve_file(self):
        try:
            file_path = self.path[1:]  # убираем начальный слеш
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                self.end_headers()
                self.wfile.write(file.read())
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

HOST = "192.168.0.7"
PORT = 8000
httpd = HTTPServer((HOST, PORT), Serv)
print("Server is running on {}:{}...".format(HOST, PORT))
httpd.serve_forever()
