# 參考資料
### https://stackoverflow.com/questions/54976051/how-to-accept-self-signed-certificate-from-e-mail-server-via-smtplib-tsl/57333670#57333670
### https://stackoverflow.com/questions/16745409/what-does-pythons-socket-recv-return-for-non-blocking-sockets-if-no-data-is-r
import os, re, sys, ssl
import socket
import argparse
#from fake_useragent import UserAgent ## pip install fake-useragent

# We use this regex to see if the url form is correct
# ((?:https?:\/\/)?((?:[\w\d\-]+\.)+[\w\d\-]+)(?::(\d+))?((?:\/[^\/\"'\n?]*)*\/?(?:\?([^"'\r\n]*))?))
# 'Content-Length: (\d+)'
reg = '(?P<url>(?:(?P<protocol>https?):\\/\\/)?(?P<domain>(?:[\\w\\d\\-]+\\.)+[\\w\\d\\-]+)(?::(?P<port>\\d+))?(?P<path>(?:\\/[^\\/\\"\'\\n?]*)*\\/?(?:\\?(?P<arg>[^"\'\\r\\n]*))?))'
reg1 = b'Content-Length: (?P<length>\\d+)'
reg2 = b'(?P<hex_value>[\dabcdefABCDEF]+\\r\\n)'
reg3 = b'\\r\\n\\r\\n'
reg4 = b'0\\r\\n\\r\\n$' #or b'\r\n0\r\n\r\n'
url_finder = re.compile(reg)
content_finder = re.compile(reg1)
hex_finder = re.compile(reg2)
eof_finder = re.compile(reg3)
eof0_finder = re.compile(reg4)

#Handle User Argument
parser = argparse.ArgumentParser(description="Get website source code. http/https client. (The url in Windows cmd must be \"text...\", not text...)")
parser.add_argument("-url", "-u", help="type a url (must be \"http\" or \"https\" at the beginning of string.)", type=str, default="")
parser.add_argument("-format", "-f", help="type the output format you want (like html, js, css, jpg, png...)", type=str, default="")
parser.add_argument("-port", help="type the port you want (attention the port in the url is priority)", type=str, default="")
parser.add_argument("-ssl", help="use ssl or not (0 or 1), default auto judge", type=int, default=-1)
parser.add_argument("-print", "-p", help="print recive bytes in cmd", action="store_true")
args = parser.parse_args()
if not args.url: #if user not use url argument that they don't give a url to me.
    print("TYPE A URL:")
    args.url = input()
url_ = url_finder.search(args.url)
if not url_: #The url which user input has incorrect form.
    print("Error: URL FORM ERROR.")
    sys.exit(-1)
port_ = args.port
ssl_ = args.ssl
f = args.format


def client():
    prt = args.print #print in cmd or not
    url = url_["url"]
    port = url_["port"]
    webpage = url_["path"]
    hostname = url_["domain"]
    protocol = url_["protocol"]
    if not webpage: webpage = "/"
    if webpage=="/":
        filename = "result%s.html" if not f else "result%s."+f
    else:
        filetmp = webpage.split("?")[0].split("/")[-1].split(".")
        if len(filetmp)==1:
            filename = filetmp[0]+"%s"
            if f: filename+=".%s"%f
        else:
            filename =".".join(filetmp[:-1])+"%s."
            filename += filetmp[-1] if not f else f
    
    filename_ = ".".join(filename.split(".")[:-1]) if "." in filename else filename
    
    port =  port if port else port_ if port_ else "443" if protocol=="https" else "80" #1.if the port in url 2.if user define port 3.let me auto choice by protocol.
    # user_agent = UserAgent()['google chrome'] #generate a fake user_agent by using module.# pip install fake-useragent
    request_args = [webpage, hostname, port, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52"]
    request = bytes("GET %s HTTP/1.1\r\nHost: %s:%s\r\nConnection: keep-alive\r\nUser-Agent: %s\r\n\r\n"%(*request_args, ), encoding = "utf-8")
    
    if ssl_==1 or (ssl_==-1 and protocol=="https"): #use ssl (tls)
        context = ssl._create_unverified_context()  #ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
    else:
        conn = socket.socket(socket.AF_INET) #not use ssl (protocol http, port 80)
    
    conn.connect((hostname, int(port)))
    conn.sendall(request)
    conn.settimeout(3)
    recive = b"" # $recive <- All we recive
    recive_tmp = b""
    recive_content = b""
    recive_headers = b""
    eof_index = None
    print("Request:\n %s\n"%request) #print the request we sended to server.
    while 1:
        try:
            recive_tmp = conn.recv(1024) #first response will include headers. #Include content length(hex).
            recive += recive_tmp
            if prt:
                print(recive_tmp)
            if b"\r\n\r\n" in recive_tmp:
                eof_index = eof_finder.search(recive_tmp)
                recive_headers += recive_tmp[:eof_index.start(0)]
                break
            recive_headers += recive_tmp
        except socket.timeout as e:
            print("TIME OUT 3s")
    #The normal recive_tmp: "$headers\r\n\r\n" -> next recv
    #The fact recive_tmp: "$headers\r\n\r\n......some data after '\r\n\r\n'......" -> next recv
    #The eof_data is that some data after \r\n\r\n.
    #The length is the length in Content-Length Header Value
    eof_data = recive_tmp[eof_index.end(0):]
    length = content_finder.search(recive)
    if length:
        recive_all, recive_content = recive_file(conn, int(length["length"]), eof_data, prt)
    else:
        recive_all, recive_content = recive_transfer_encoding_chunked(conn, eof_data, prt)
    recive += recive_all
    with open(os.path.join(os.getcwd(), filename_%"_original.html"), "wb") as html:
        html.write(recive)
    with open(os.path.join(os.getcwd(), filename_%"_header.txt"), "wb") as html:
        html.write(recive_headers)
    with open(os.path.join(os.getcwd(), filename%""), "wb") as html:
        html.write(recive_content)
    print("Successfully Write Content to %s"%(filename%""))
    conn.shutdown(socket.SHUT_WR)
    conn.close()
    return 0

def recive_file(conn, length, eof_data, prt):
    i = 0 #i is now length of all data we have recv.
    i += len(eof_data)
    recive = b""
    recive_tmp = b""
    recive_content = eof_data
    while 1:
        try:
            recive_tmp = conn.recv(1024)
            i += len(recive_tmp)
            if prt:
                print()
                print(recive_tmp)
        except socket.timeout as e:
            print("TIME OUT 3s")
            break
        if i>=length :
            recive += recive_tmp[:length-i] if i>length else recive_tmp
            break
        if not recive_tmp: break #recive_tmp = b''
        recive += recive_tmp
    recive_content += recive
    return recive, recive_content
        
def recive_transfer_encoding_chunked(conn, eof_data, prt):
    length = 0 #now length
    total_length = 0
    have_length = 0 #-> True/False
    recive, recive_tmp, recive_content = [b"" for i in range(3)]
    ##############################################################################
    #####     0,            1,           2,      3,          4,              5 ###
    p = [length, total_length, have_length, recive, recive_tmp, recive_content]
    ##############################################################################
    p[4] = eof_data
    if p[4]: #p[4] != b''(no data)  #All the "line" in here is point to data that we recv.
        s = hex_finder.search(p[4]) #s be like b'120bcf\r\n'
        if not s: return b''        #not found the hex format in string, break
        hex = s["hex_value"]        #hex: $hex\r\n, be like: b"568FF\r\n".
        p[1] = int(hex, 16)         #568FF to decimal
        if not p[1]: return b''     #p[1]==0, end of line. s: 0\r\n\r\n
        p[0] = len(p[4])-len(hex)   # len(b"$hex\r\n......") - len(b"$hex\r\n") => len(b"......"), real content length. $hex\r\n be like: b"568FF\r\n".
        if p[0]>=p[1]:              #one line end, p[4]: $hex\r\n......\r\n.(Maybe=> p[0]: p[1]+2, due to "\r\n" in the end (len:2).) =>read next line
            p[5] += p[4][s.end("hex_value"):len(hex)+p[1]] # p[4]: "$hex\r\n......\r\n" p[5]+= "......", real content(bytes).
        else:                       #Line not end, continue to recv data and process. p[4]: "$hex\r\n......", p[5]+=".......".
            p[2] = 1                #have_length: True
            p[5] += p[4][s.end("hex_value"):]
    while 1:
        try:
            p[4] = conn.recv(1024) #p[4] be like b'120bcf\r\n........' or '......'
            p[3] += p[4]
            if prt:
                print()
                print(p[4])
            if not p[2]: #not have_length
                s = hex_finder.search(p[4]) #s be like b'120bcf\r\n'
                if not s: continue
                hex = s["hex_value"]
                p[1] = int(hex, 16)
                if not p[1]: break #p[1]==0, end of line. s: 0\r\n\r\n
                p[0] = len(p[4])-len(hex)
                if p[0]>=p[1]: #one line end, p[4]: ???\r\n......\r\n.(p[0]: p[1]+2 "\r\n") =>read next line
                    p[5] += p[4][s.end("hex_value"):len(hex)+p[1]]
                    continue
                else:
                    p[2] = 1
                    p[5] += p[4][s.end("hex_value"):]
                    continue
            eof = eof0_finder.search(p[4])
            if eof0_finder.search(p[4]): #end of line, p[4]: "......0\r\n\r\n......"
                p[5] += p[4][:eof.start(0)]
                break
            p[0] += len(p[4])
            if p[0]>=p[1]:
                p[5] += p[4][:p[1]-p[0]] if p[0]>p[1] else p[4] #p[1]-p[0] is Negative Value or Zero.
                p[2]=0
            else:
                p[5] += p[4]
            if not p[4]: break #p[4] = b''
        except socket.timeout as e:
            print("TIME OUT 3s")
            break
    length, total_length, have_length, recive, recive_tmp, recive_content = p
    return recive, recive_content
client()
