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
import ssl
import sys
import time
import socket
import signal
import datetime
import threading

class SSL_SERVER():
    def __init__(self):
        print("SSL SERVER START.\n Please visit https://127.0.0.1.")
        self.format = {"html":"text/html; charset=UTF-8", "jpg": "image/jpeg", "png": "image/png"}
        self.HTML_ROOT_FOLDER = "html_server_root"
        self.crt = os.path.join("certificate/certificate.crt")
        self.key = os.path.join("certificate/privateKey.key")
        self.ip = "127.0.0.1"
        self.port = 443
        start_server = threading.Thread(target=self.main)
        start_server.setDaemon(True)
        start_server.start()
        while 1:
            time.sleep(0.01)
            signal.signal(signal.SIGINT, self.signal_handler)
        return 0
    def main(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.crt, self.key)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((self.ip, self.port))
            sock.listen(5)
            with context.wrap_socket(sock, server_side=True) as ssock:
                while 1:
                    #try:
                        conn, addr = ssock.accept()
                        process_conn = threading.Thread(target=self.processer, args = (conn, addr))
                        process_conn.setDaemon(True)
                        process_conn.start()
                    #except Exception as e:
                     #   print(e)
        return 0
    def processer(self, conn, addr):
        request = conn.recv(1024)
        self.sendf(conn, self.path(request))
        conn.close()
        print("Request:")
        print(request)
        print(addr, end="\n\n")
    def sendf(self, conn, filepath):
        if filepath.split('.')[-1] in self.format:
            typ = self.format[filepath.split('.')[-1]]
        else:
            typ = self.format["html"]
        datas = ["HTTP/1.1 200 OK",
                 "Content-Type: %s"%typ,
                 "Server: Windows/10",
                 "Age: 0",
                 datetime.datetime.now(datetime.timezone.utc).strftime("Date: %a, %d %b %Y %H:%M:%S GMT"),
                 "Cache-Control: max-age=0, private, must-revalidate"]
        data = bytes("\r\n".join(datas)+"\r\n\r\n", encoding="utf-8")
        # print(data)
        conn.send(data)
        with open(filepath,"rb") as doc:
            while 1:
                data_tmp = doc.read(1024)
                if not data_tmp: break
                conn.send(data_tmp)
    def path(self, request): # request: b'GET /open/index.html?name=123&range=456-789 HTTP/1.1\r\nHost: 127.0.0.1\r\n...'
        tmp = request.split(b' ')[1].split(b'?') #["/open/index.html", "name=123&range=456-789"]
        #if len(tmp)>1:
        #    tmp[1] = tmp[1].split(b'&')
        #    arg = [item.split(b'=') for item in tmp[1]]
        filepath = tmp[0][1:]
        filepath = "index.html" if not filepath else "error.html" if not os.path.exists(filepath) else filepath.decode(encoding="utf-8")
        filepath = os.path.join(self.HTML_ROOT_FOLDER, filepath)
        return filepath
    def signal_handler(self, sig, frame):
        print('Server is Stopped.')
        sys.exit(0)
SSL_SERVER()