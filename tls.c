
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

/*
    Windows x64 Msys2 Mingw64
    gcc tls.c -I"C:/msys64/home/ssl/include/" -L"C:/msys64/home/ssl/bin" -lws2_32 -llibssl-3-x64 -llibcrypto-3-x64
*/

#ifdef WIN32
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
# include <stdio.h>
# include <string.h>
# include <stdlib.h>
# include <openssl/bio.h>
# include <openssl/ssl.h>
# include <openssl/err.h>
#define BuffSize 1024

#pragma comment(lib,"ws2_32.lib") //Winsock Library

int find(int **resultIndex, char string[], char reg[], int mutli){
	int regIndex, initIndex, i, resultIndexIndex, regLastIndex, howMany, onechr;
	size_t sint, nowSize;
	regIndex = initIndex = i = howMany = 0;
	resultIndexIndex = 1;
	sint = nowSize = sizeof(int);
	int notOneChr = (strlen(reg)!=1);
	regLastIndex = strlen(reg)-1;
	*resultIndex = (int*)malloc(sint);
	(*resultIndex)[0] = -1;
	int *resultIndexPtr = *resultIndex;
	if(strlen(reg)==0){return 1;}
	while(string[i]!='\0'){
		//printf("i %d initIndex %d regIndex %d resultIndexIndex %d\n", i, initIndex, regIndex, resultIndexIndex);
		if(string[i]==reg[regIndex]){
			if(regIndex==0 && notOneChr){
				initIndex = i;
			}else{
				if(regIndex==regLastIndex){
					howMany++;
					if(!mutli){
						if(!notOneChr){initIndex = i;}
					    (*resultIndex)[resultIndexIndex] = initIndex;
					    break;
					}else{
						if(!notOneChr){initIndex = i; i++;}
						nowSize = nowSize+sint;
						resultIndexPtr = (int*)realloc(*resultIndex, nowSize);
						if(!resultIndexPtr){puts("ERR");exit(-1);}
						(*resultIndex)[resultIndexIndex] = initIndex;
						resultIndexIndex++;
						initIndex = 0;
						regIndex = 0;
						continue;
					}
				}
			}
			regIndex++;
		}else{
			if(initIndex!=0){
				initIndex = 0;
				regIndex = 0;
			}
		}
		i++;
	}
	if(howMany>0){*resultIndex[0] = howMany;}
	return 0;
}

int URL(char (*hostname_)[BuffSize], char (*request_)[BuffSize]){
	// Get user input url, and process to http request
	//setvbuf(stdout, NULL, _IONBF, 0);
    char reg[]="/", url[10000];
	printf("TYPE HTTPS URL:\n");
	fflush(stdout);
	fgets(url, 10000, stdin);
	printf("\n");
	fflush(stdout);
	
	if(url[strlen(url)-1]=='\n'){
		url[strlen(url)-1]='\0';
	}
	
	int *search;
	int search_excute = find(&search, url, reg, 1);

	if(search[0]==2){
		url[strlen(url)] = '/';
		search_excute = find(&search, url, reg, 1);
	}
	
	if(search[0]<3){puts("URL ERROR."); fflush(stdin); exit(-1);}
	char port[] = ":443";
	char webpage[strlen(url)-search[3]+1];
	char hostname[search[3]-search[2]+4];
	char protocol[search[1]+2];
	char request[BuffSize];
	int index, i;
	//printf("%d \n", sizeof(webpage));
	webpage[sizeof(webpage)-1] = '\0';
	hostname[sizeof(hostname)-1] = '\0';
	protocol[sizeof(protocol)-1] = '\0';
	index=0;
	for(i=search[3]; i<strlen(url); i++){
		webpage[index] = url[i];
		//printf("Start %c Stop 1\n", url[i]);
		index++;
	}
	index=0;
	for(i=search[2]+1; i<search[3]; i++){
		//printf("Start %c Stop 2\n", url[i]);
		// Not *hostname_[index]
		(*hostname_)[index] = url[i];
		hostname[index] = url[i];
		index++;
	}
	(*hostname_)[index] = '\0';
	index=0;
	for(i=search[3]-search[2]-1; i<search[3]-search[2]+4; i++){
	    hostname[i] = port[index];
		index++;
	}
	index=0;
	for(i=0; i<search[1]-1; i++){
		//printf("Start %c Stop 3\n", url[i]);
		protocol[index] = url[i];
		index++;
	}
	sprintf(request,
	"GET %s HTTP/1.1\r\nHost: %s\r\nConnection: Close\r\n\r\n\0",
	webpage, hostname
	);
	//puts(request);
	strcpy(*request_, request);
    return 0;
} 

int main(int argc , char *argv[])
{
	char hostname[BuffSize];
	char *hostname_tmp;
	char name[BuffSize];
	char request[BuffSize];
	char response[BuffSize];
	char ip[100];
	int port = 443;
	int i;
	int recive, user_input;
	struct hostent *he;
	struct in_addr **addr_list;
	user_input = URL(&hostname, &request); //This line need to write before openssl and ws2_32 init
	printf("Request:\n%s", request);
	hostname_tmp = hostname;
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
	/*sprintf(hostname, "%s:%d", hostname, 443);
	sprintf(request,
	"GET /c/c_intro.php HTTP/1.1\r\nHost: %s\r\nConnection: Close\r\n\r\n",
	hostname
	);*/
	
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
    //puts(response);
	fprintf(html, "%s", response);
	//printf("%d", sizeof(response));
	if(recive <= 0) { break;}
	}
    
	// fflush(stdout);
    SSL_CTX_free(ctx);
	fclose(html);
	printf("Successfully Write Content to result.html");
	return 0;
}