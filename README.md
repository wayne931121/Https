### c_https_client

###Window Msys2 Mingw64 x64
### To Install OpenSSL and find <openssl/ssl.h> <openssl/opensslconf.h>.
### Download MSYS2 RUN Mingw64
###Run "pacman -S mingw-w64-x86_64-toolchain", and install gcc.
###Download Source Code From https://github.com/openssl/openssl
###cd to folder where "config" file is.
###change the prefix and openssldir to what you want.
### this command = "./Configure --prefix=/home/ssl --openssldir=/home/ossl shared zlib"
./config --prefix=/home/ssl --openssldir=/home/ossl shared zlib
make
make install
### change c file to your file
### This c file include "#include <openssl/ssl.h>" line.
### Currect path "C:/msys64/home/ssl/include/openssl/ssl.h" in this example.
### Currect path "C:/msys64/home/ssl/bin/libcrypto-3-x64.dll" in this example.
### Currect path "C:/msys64/home/ssl/bin/libssl-3-x64.dll" in this example.
### Add "C:/msys64/home/ssl/bin"(dll path) to environment path or copy dll file to the path "tls.c"
gcc tls.c -I"C:/msys64/home/ssl/include/" -L"C:/msys64/home/ssl/bin" -lws2_32 -llibssl-3-x64 -llibcrypto-3-x64
### Add "C:/msys64/home/ssl/bin"(dll path) to environment path or copy dll file to the path where the ".exe" is.
./a
### When you run exe in cmd not in msys2 shell, you need C:\msys64\mingw64\bin\zlib1.dll.
### Copy it to exe path or set C:\msys64\mingw64\bin\ to environment path.
