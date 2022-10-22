# Generate key using openssl:
# To install openssl on windows x64, see here https://github.com/wayne931121/https_client
# Step:
# 1. Install Msys2 Shell
# 2. Install Gcc in mingw64
# 3. Download Source Code from https://github.com/openssl/openssl release
# 4. Run ./Configure
# 5. Finish
# Generate certificate and private key:
# https://www.xolphin.com/support/OpenSSL/Frequently_used_OpenSSL_Commands
# https://stackoverflow.com/questions/60030906/self-signed-certificate-only-works-with-localhost-not-127-0-0-1 # (net::ERR_CERT_COMMON_NAME_INVALID))
# https://helpcenter.gsx.com/hc/en-us/articles/115015960428-How-to-Generate-a-Self-Signed-Certificate-and-Private-Key-using-OpenSSL
# openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -keyout privateKey.key -out certificate.crt -config req.cnf
# Check the Private Key and Certificate:
# openssl x509 -in certificate.crt -text
# openssl rsa -in privateKey.key -check
## if browser say "not private connection", install "certificate.crt" in your device.
## (Like Windows10, install certificate to "受信任的根憑證授權單位 Trusted Root Certification Authorities").
## To Delete certificate in windows, use Window+R, and type certmgr.msc.

import os
import re
import ssl
import sys
import time
import socket
import signal
import argparse
import datetime
import threading

#Handle User Argument
parser = argparse.ArgumentParser(description="Get website source code. http/https client. (The url in Windows cmd must be \"text...\", not text...)")
parser.add_argument("-https", "-s", help="use https, need crt and key.", action="store_true")
args = parser.parse_args()
usessl = args.https

def url_decoder(b):
# https://zh.wikipedia.org/zh-tw/%E7%99%BE%E5%88%86%E5%8F%B7%E7%BC%96%E7%A0%81
# %21 mean 21hex, => int("21",16) => 33 => chr(33) => "!", result: "!"
    if type(b)==bytes:
        b = b.decode("utf-8") #byte can't insert utf8 charater
    result = bytearray()
    enter_hex_unicode_mode = 0
    hex_tmp = ""
    now_index = 0
    for i in b:
        if i=='%': #like %51%52, have entered mode, continue appending bytearray
            enter_hex_unicode_mode = 1
            continue
        if enter_hex_unicode_mode:
            hex_tmp += i
            now_index += 1
            if now_index==2: #%51%5F len("51")=2 len("5F")=2
                result.append(int(hex_tmp, 16) )
                hex_tmp = ""
                now_index = 0
                enter_hex_unicode_mode = 0
            continue
        result.append(ord(i))
    result = result.decode(encoding="utf-8")
    return result

class HTTP_SERVER():
    def __init__(self):
        print("HTTP SERVER START.\n Please visit https://127.0.0.1.\n Press Ctrl+C to Stop.")
        self.format = {"html":"text/html; charset=UTF-8",
                       "jpg": "image/jpeg",
                       "png": "image/png",
                       "js":  "application/javascript; charset=utf-8"}
        self.HTML_ROOT_FOLDER = "html_server_root"
        self.crt = os.path.join("certificate/certificate.crt")
        self.key = os.path.join("certificate/privateKey.key")
        self.ip = "127.0.0.1"
        self.port = 443 if usessl else 80
        self.BufferSize = "fff" #send to client size per each #4095
        self.replace = re.compile("%(?P<hex>[\dA-Fa-f]{2})")
        self.BufferDSize = int(self.BufferSize, 16)
        start_server = threading.Thread(target=self.main)
        start_server.setDaemon(True)
        start_server.start()
        while 1:
            time.sleep(0.01)
            signal.signal(signal.SIGINT, self.signal_handler)
        return 0                
    def main(self):       
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        if usessl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.crt, self.key)
            sock = context.wrap_socket(sock, server_side=True)
        sock.bind((self.ip, self.port))
        sock.listen(5)
        while 1:
            try:
                conn, addr = sock.accept()
                process_conn = threading.Thread(target=self.processer, args = (conn, addr))
                process_conn.setDaemon(True)
                process_conn.start()
            except Exception as e:
                print(e)
        return 0
    def processer(self, conn, addr):
        request = conn.recv(1024)
        self.sendf(conn, self.path(request))
        conn.shutdown(socket.SHUT_WR)
        conn.close()
        print("Request:")
        print(request)
        print(addr, end="\n\n")
    def sendf(self, conn, filepath):
        if filepath.split('.')[-1] in self.format:
            typ = self.format[filepath.split('.')[-1]]
        else:
            typ = self.format["html"]
        content_length = ""
        if typ!=self.format["html"]:
            with open(filepath,"rb") as doc:
                data = doc.read()
                headers = ["HTTP/1.1 200 OK",
                         "Content-Type: %s"%typ,
                         "Content-Length: %d"%len(data),
                         "Server: Windows/10",
                         "Age: 0%s",
                         datetime.datetime.now(datetime.timezone.utc).strftime("Date: %a, %d %b %Y %H:%M:%S GMT"),
                         "Cache-Control: max-age=0, private, must-revalidate"]
                header = bytes("\r\n".join(headers)+"\r\n\r\n", encoding="utf-8")
                conn.send(header)
                conn.send(data)
        else:                
            headers = ["HTTP/1.1 200 OK",
                     "Content-Type: %s"%typ,
                     "Server: Windows/10",
                     "Age: 0%s",
                     datetime.datetime.now(datetime.timezone.utc).strftime("Date: %a, %d %b %Y %H:%M:%S GMT"),
                     "Transfer-Encoding: chunked",
                     "Cache-Control: max-age=0, private, must-revalidate"]
            header = bytes("\r\n".join(headers)+"\r\n\r\n", encoding="utf-8")
            # print(header)
            conn.send(header)
            with open(filepath,"rb") as doc:
                while 1:
                    data_tmp = doc.read(self.BufferDSize)
                    if not data_tmp: break
                    chunk = bytes(hex(len(data_tmp))[2:]+"\r\n", encoding="utf-8")
                    conn.send(chunk)
                    conn.send(data_tmp.strip())
                    conn.send(b"\r\n")
            conn.send(b"0\r\n\r\n")
    def path(self, request): # request: b'GET /open/index.html?name=123&range=456-789 HTTP/1.1\r\nHost: 127.0.0.1\r\n...'
        tmp = request.split(b' ')[1].split(b'?') #["/open/index.html", "name=123&range=456-789"]
        #if len(tmp)>1:
        #    tmp[1] = tmp[1].split(b'&')
        #    arg = [item.split(b'=') for item in tmp[1]]
        filepath = tmp[0][1:]
        filepath = filepath.decode(encoding="utf-8")
        filepath = "index.html" if not filepath else "error.html" if not os.path.exists(os.path.join(self.HTML_ROOT_FOLDER, filepath)) else filepath
        filepath = os.path.join(self.HTML_ROOT_FOLDER, filepath)
        return filepath
    def signal_handler(self, sig, frame):
        print('Server is Stopped.')
        sys.exit(0)
HTTP_SERVER()