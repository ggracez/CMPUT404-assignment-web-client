#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Grace Zhu, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    def __str__(self):
        return f"HTTP/1.1 {self.code}\n{self.body}"

class HTTPClient(object):
    def get_host_port(self,url):
        o = urlparse(url)
        host = o.hostname
        port = o.port
        if port is None:
            port = 80
        return host, port
    
    def get_path(self, url):
        path = urlparse(url).path
        if path == "":
            path = "/"
        return path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        if data is None:
            return 500  # default server error code
        else:
            return int(data.split()[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def get_args(self, args):
        params = ""
        if args is not None:
            param_list = []
            for i in args.keys():
                param_list.append(i + "=" + args[i])
            params += "&".join(param_list)
        return params
        
    def GET(self, url, args=None):      
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        
        if urlparse(url).scheme != "http":
            return HTTPResponse(400)
        
        try:
            self.connect(host, port)
        except:
            # perhaps 500 is better here but this error also gets returned when the 
            # url does not exist (which is a part of the requirements) so i'll keep it like this
            return HTTPResponse(404)
        
        params = self.get_args(args)
        
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Connection: close\r\n"
        request += f"\r\n"
        request += f"{params}"
        self.sendall(request)
        
        data = self.recvall(self.socket)
        self.socket.close()
        
        code = self.get_code(data)
        body = self.get_body(data)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        
        if urlparse(url).scheme != "http":
            return HTTPResponse(400)
        
        try:
            self.connect(host, port)
        except:
            return HTTPResponse(404)
        
        params = self.get_args(args)
        
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Content-Type: application/x-www-form-urlencoded\r\n"
        request += f"Content-Length: {len(params)}\r\n"
        request += f"Connection: close\r\n"
        request += f"\r\n"
        request += f"{params}"
        self.sendall(request)
        
        data = self.recvall(self.socket)
        self.socket.close()
        
        code = self.get_code(data)
        body = self.get_body(data)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
