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
        elif self.path.startswith('/files/'):
            self.serve_file()
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def list_files(self):
        file_list = os.listdir('./files')
        response = '<html><body><h1>Files:</h1><ul>'
        for file_name in file_list:
            response += f'<li><a href="/files/{file_name}">{file_name}</a></li>'
        response += '</ul></body></html>'
        return response

    def serve_file(self):
        file_path = self.path[len('/files/'):]
        full_path = os.path.join(os.getcwd(), 'files', file_path)

        if not os.path.isfile(full_path):
            self.send_error(404, 'File Not Found: %s' % self.path)
            return

        try:
            file_size = os.path.getsize(full_path)
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            if "Range" in self.headers:
                range_header = self.headers['Range']
                range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                    if end >= file_size:
                        end = file_size - 1

                    self.send_response(206)
                    self.send_header("Content-type", mime_type)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(end - start + 1))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()

                    with open(full_path, 'rb') as file:
                        file.seek(start)
                        self.wfile.write(file.read(end - start + 1))
                    return

            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Content-Disposition', 'inline')
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
        except BrokenPipeError:
            print("Broken pipe error: Client disconnected.")

if __name__ == '__main__':
    HOST = "IP"
    PORT = 8000
    httpd = HTTPServer((HOST, PORT), Serv)
    print("Server is running on {}:{}...".format(HOST, PORT))
    httpd.serve_forever()
