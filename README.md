## Https Client/Server

[C Client](#c_https_client)

[Python Client/Server](#Python-Https-Client)

## Python Https Client

```
C:\Users\$Username\Downloads> python https_client.py -h
usage: https_client.py [-h] [-url URL] [-format FORMAT] [-port PORT] [-ssl SSL] [-print]

Get website source code. http/https client. (The url in Windows cmd must be "text...", not
text...)

optional arguments:
  -h, --help            show this help message and exit
  -url URL, -u URL      type a url (must be "http" or "https" at the beginning of string.)
  -format FORMAT, -f FORMAT
                        type the output format you want (like html, js, css, jpg, png...)
  -port PORT            type the port you want (attention the port in the url is priority)
  -ssl SSL              use ssl or not (0 or 1), default auto judge
  -print, -p            print recive bytes in cmd
```
```
python https_client.py -url "https://www.example.com/" -f html -p
```
```
python https_client_simple.py
```

## Python Http Server

    # -https use ssl or not
    
    python https_server.py -https
    python https_server.py

## Python Http Server

    python http_server.py

## C_Https_Client

### Run In Windows Msys2 Mingw64 x64
### To Install OpenSSL and find <openssl/ssl.h> <openssl/opensslconf.h>.
### Download MSYS2 RUN Mingw64

Run "pacman -S mingw-w64-x86_64-toolchain", and install gcc.

Run "pacman -S make".

Download Source Code From https://github.com/openssl/openssl

cd to folder where "config" file is.

change the prefix and openssldir to what you want.

This command "./config --prefix=/home/ssl --openssldir=/home/ossl shared zlib"

= "./Configure --prefix=/home/ssl --openssldir=/home/ossl shared zlib"

    ./config --prefix=/home/ssl --openssldir=/home/ossl shared zlib
    make
    make install

### change c file to your file (In here is tls.c)
### This c file include "#include <openssl/ssl.h>" line.
### Currect path "C:/msys64/home/ssl/include/openssl/ssl.h" in this example.
### Currect path "C:/msys64/home/ssl/bin/libcrypto-3-x64.dll" in this example.
### Currect path "C:/msys64/home/ssl/bin/libssl-3-x64.dll" in this example.
### Add "C:/msys64/home/ssl/bin"(dll path) to environment path or copy dll file to the path "tls.c"

    gcc tls.c -I"C:/msys64/home/ssl/include/" -L"C:/msys64/home/ssl/bin" -lws2_32 -llibssl-3-x64 -llibcrypto-3-x64

### Add "C:/msys64/home/ssl/bin"(dll path) to environment path or Copy dll file to the path where the ".exe" is. (a.exe)

    ./a

### When you run exe in cmd not in msys2 shell, you need C:\msys64\mingw64\bin\zlib1.dll.
### Copy it to exe path or set C:\msys64\mingw64\bin\ to environment path.

    a
