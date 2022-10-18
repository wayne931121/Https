import os
import sys
import time
import socket
import signal
import datetime
import threading

class HTTP_SERVER():
    def __init__(self):
        print("HTTP SERVER START.\n Please visit http://127.0.0.1.\n Press Ctrl+C to Stop.")
        self.format = {"html":"text/html; charset=UTF-8",
                       "jpg": "image/jpeg",
                       "png": "image/png",
                       "js":  "application/javascript; charset=utf-8"}
        self.HTML_ROOT_FOLDER = "html_server_root"
        self.ip = "127.0.0.1"
        self.port = 80
        start_server = threading.Thread(target=self.main)
        start_server.setDaemon(True)
        start_server.start()
        while 1:
            time.sleep(0.01)
            signal.signal(signal.SIGINT, self.signal_handler)
        return None
    def main(self):    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
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
        filepath = filepath.decode(encoding="utf-8")
        filepath = "index.html" if not filepath else "error.html" if not os.path.exists(os.path.join(self.HTML_ROOT_FOLDER, filepath)) else filepath
        filepath = os.path.join(self.HTML_ROOT_FOLDER, filepath)
        return filepath
    def signal_handler(self, sig, frame):
        print('Server is Stopped.')
        sys.exit(0)
HTTP_SERVER()