
/*
參考資料
https://www.rfc-editor.org/rfc/rfc2616
https://stackoverflow.com/questions/32510218/warning-comparison-between-pointer-and-integer
https://www.binarytides.com/winsock-socket-programming-tutorial/
https://stackoverflow.com/questions/34384803/c-undefined-reference-to-wsastartup8
https://stackoverflow.com/questions/41229601/openssl-in-c-socket-connection-https-client
https://developer.ibm.com/tutorials/l-openssl/
https://opensource.com/article/19/6/cryptography-basics-openssl-part-1
https://beej-zhtw-gitbook.netdpi.net/jin_jie_ji_shu/selectff1a_tong_bu_i__o_duo_gong
*/

/*
    Windows Github C:\Program Files\Git\usr\bin Include OpenSSL
	openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
*/

#ifdef WIN32
#include<stdio.h>
#include <winsock2.h>
#else
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <cstdlib>
#include <iostream>
#endif

# include <time.h>
# include  <openssl/bio.h>
# include  <openssl/ssl.h>
# include  <openssl/err.h>
#define BuffSize 1024

#pragma comment(lib,"ws2_32.lib") //Winsock Library

int main(int argc , char *argv[])
{
	char hostname[BuffSize] = "www.w3schools.com";
	char *hostname_tmp = hostname;
	char name[BuffSize];
	char request[BuffSize];
	char response[BuffSize];
	char ip[100];
	int port = 443;
	int i;
	int recive;
	struct hostent *he;
	struct in_addr **addr_list;
	SSL_load_error_strings();
	ERR_load_BIO_strings();
	OpenSSL_add_all_algorithms();
	WSADATA wsa;
	
	
	
	////////////////////////////////////////////
	//////////GET TARGET WEBSITE IP/////////////
	///////////////////////////////////////////
	
	printf("\nInitialising Winsock...");
	if (WSAStartup(MAKEWORD(2,2),&wsa) != 0)
	{
		printf("Failed. Error Code : %d",WSAGetLastError());
		return 1;
	}
	printf("Initialised.\n");
	
	if ((he = gethostbyname(hostname_tmp)) == NULL) 
	{
		printf("gethostbyname failed : %d" , WSAGetLastError());
		return 1;
	}
	
	//Cast the h_addr_list to in_addr , since h_addr_list also has the ip address in long format only
	addr_list = (struct in_addr **) he->h_addr_list;
	
	for(i = 0; addr_list[i] != NULL; i++) 
	{
		//Return the first one;
		strcpy(ip , inet_ntoa(*addr_list[i]) );
	}
	
	printf("%s resolved to : %s\n" , hostname , ip);
	
	////////////////////////////////////////////////
	///////////////WEBSITE IP GOT///////////////////
	////////////////////////////////////////////////
	
	
	/////////////////////////////////////////////////
	////////Create A SOCKET, CONNECT TO SERVER///////
	/////////////////////////////////////////////////
	
	int s;
	struct sockaddr_in sa;
	
	//Connecting to server
	s = socket(AF_INET, SOCK_STREAM, 0);
	if (s < 0) printf("Sock failed");
    memset (&sa, 0, sizeof(sa));
    sa.sin_family      = AF_INET;
    sa.sin_addr.s_addr = inet_addr(ip); // address of google.ru
    sa.sin_port        = htons(port); 

    if (connect(s, (struct sockaddr *)&sa, sizeof(sa))){
        printf("Error connecting to server.\n");
        return 1;
    }
    
	/////////////////////////////////////////////////
	////////////WRAP SOCKET WITH SSL/////////////////
	/////////////////////////////////////////////////
	
    const SSL_METHOD* method = TLSv1_2_client_method();
    if (NULL == method) printf("TLSv1_2_client_method...");
    
    SSL_CTX* ctx = SSL_CTX_new(method);
    if (NULL == ctx) printf("SSL_CTX_new...");
	
    SSL *ssl;	
	ssl = SSL_new (ctx);
    if (!ssl) {
        printf("Error creating SSL.\n");
        return 1;
    }
	
    SSL_get_fd(ssl);
    SSL_set_fd(ssl, s);
	
    int err = SSL_connect(ssl);
    if (err <= 0) {
        printf("Error creating SSL connection.  err=%x\n", err);
		return 1;
    }
	
	//////////////////////////////////////////////////////////////////////////////////////
	///////// SENDING HTTPS REQUEST TO SERVER, RECIVING RESPONSE FROM SERVER//////////////
	//////////////////////////////////////////////////////////////////////////////////////
	
	///////// "GET /c/c_intro.php HTTP/1.1\r\nHost: www.w3schools.com:443\r\nConnection: Close\r\n\r\n" ///////
	///////// "GET / HTTP/1.1\r\nHost: www.w3schools.com:443\r\nConnection: Close\r\n\r\n" ////////////////////
	///////// "/c/c_intro.php" mean "https://www.w3schools.com/c/c_intro.php" in here. ////////////////////////
	sprintf(hostname, "%s:%d", hostname, 443);
	sprintf(request,
	"GET /c/c_intro.php HTTP/1.1\r\nHost: %s\r\nConnection: Close\r\n\r\n",
	hostname
	);
	
	int send = SSL_write(ssl, request, strlen(request));
	if (send<0) printf("Sending Failed.");
	
	//setbuf(stdout, NULL); //no cache
	char* filename = "result.html";
	{
	FILE* html = fopen(filename, "w");
	fprintf(html, "");
	fclose(html);
	}
	FILE* html = fopen(filename, "a");
	
	while (1) {
	//puts("mes start");
    memset(response, '\0', sizeof(response));
	//puts("read start");
    recive = SSL_read(ssl, response, BuffSize);
	//printf("\nLINE:\n");
    puts(response);
	fprintf(html, "%s", response);
	//printf("%d", sizeof(response));
	if(recive <= 0) { break;}
	}
    
	// fflush(stdout);
    SSL_CTX_free(ctx);
	fclose(html);
	return 0;
}