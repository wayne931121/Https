import ssl
import socket
print("TYPE A URL:")
url = input().split("/")
hostname = url[2]
webpage = "/"+"/".join(url[3:])
protocol = url[0][:-1]
port = ""
port = "443" if protocol=="https" else "80"
request = bytes("GET %s HTTP/1.1\r\nHost: %s:%s\r\nConnection: Close\r\n\r\n"%(webpage, hostname, port), encoding = "utf-8")
if protocol=="https":
    ### https://stackoverflow.com/questions/54976051/how-to-accept-self-signed-certificate-from-e-mail-server-via-smtplib-tsl/57333670#57333670
    context = ssl._create_unverified_context() #ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
else:
    conn = socket.socket(socket.AF_INET)
conn.connect((hostname, int(port)))
conn.sendall(request)
recive = b""
print("Request:\n %s\n"%request)
while 1:
    recive_tmp = conn.recv(1024)
    if not recive_tmp: break #recive_tmp = b''
    recive += recive_tmp
with open("result.html", "wb") as html:
    html.write(recive)
print("Successfully Write Content to result.html")