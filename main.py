from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import mimetypes
import re

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
            response += f'<li><a href="/files/{file_name}">{file_name}</a></li>'
        response += '</ul></body></html>'
        return response

    def serve_file(self):
        file_path = self.path[1:]  # убираем начальный слеш
        if not os.path.isfile(file_path):
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        
        try:
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if "Range" in self.headers:
                range_header = self.headers['Range']
                range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                    if end >= file_size:
                        end = file_size - 1

                    self.send_response(206)
                    self.send_header("Content-type", mime_type)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(end - start + 1))
                    self.end_headers()
                    
                    with open(file_path, 'rb') as file:
                        file.seek(start)
                        self.wfile.write(file.read(end - start + 1))
                    return
            
            self.send_response(200)
            self.send_header('Content-type', mime_type if mime_type else 'application/octet-stream')
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
        except BrokenPipeError:
            print("Broken pipe error: Client disconnected.")

HOST = "0.0.0.0"  # слушаем все интерфейсы
PORT = 8000
httpd = HTTPServer((HOST, PORT), Serv)
print("Server is running on {}:{}...".format(HOST, PORT))
httpd.serve_forever()
