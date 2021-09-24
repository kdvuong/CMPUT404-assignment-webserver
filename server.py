#  coding: utf-8 
import socketserver
from os.path import abspath, splitext
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

extensions_map = {
    ".manifest": "text/cache-manifest",
	".html": "text/html",
    ".png": "image/png",
	".jpg": "image/jpg",
	".svg":	"image/svg+xml",
	".css":	"text/css",
	".js":	"application/x-javascript",
	"": "application/octet-stream", # Default
}

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        raw_data = self.request.recv(1024).strip()
        print(raw_data)

        if raw_data == b'':
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\nConnection: close \r\n\r\n", "utf-8"))
        else:
            self.parse_request(raw_data)

            if self.data["method"] == "GET":
                self.handle_get()
            else:
                self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\n", "utf-8"))
        
        self.request.close()

    def parse_request(self, raw_data):
        decoded = raw_data.decode()
        headers = decoded.split('\r\n\r\n')
        headers = headers[0].split('\r\n')
        method, path, _ = headers.pop(0).split(" ")
        data = {
            "method": method,
            "path": path
        }
        for header in headers:
            key, val = header.split(": ", 1)
            data[key.lower()] = val

        self.data = data

    def handle_get(self):
        host = self.data["host"]
        path_length = len(self.data["path"])
        temp_path = self.data["path"]
        path = f"{temp_path}index.html" if temp_path[path_length - 1] == "/" else temp_path
        file_path = f"./www{path}"

        # validate path is within ./wwww
        abs_path = abspath(file_path)
        if not abs_path.startswith(abspath("./www")):
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\nConnection: close \r\n\r\n", "utf-8"))
            return

        try:
            f = open(file_path)
            _, file_extension = splitext(path)
            self.request.sendall(bytearray(f"HTTP/1.1 200\r\nContent-Type: {extensions_map[file_extension]}\r\nConnection: close \r\n\r\n {f.read()}", "utf-8"))
        except IsADirectoryError:
            # redirect
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved\r\nLocation: http://{host}{path}/\r\nConnection: close \r\n\r\n", "utf-8"))
        except:
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\nConnection: close \r\n\r\n", "utf-8"))

        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
