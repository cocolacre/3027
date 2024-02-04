// PrintGetTickCount.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
// stackoverflow.com/questions/33306922/winsock2-h-compilation-errors
#include <iostream>
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>
#include <stdio.h>

// stackoverflow.com/questions/33306922/winsock2-h-compilation-errors


#pragma comment(lib, "ws2_32.lib")

int main()
{

    // Initialize Winsock
    WSAData wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0)
    {
        std::cout << "WSAStartup failed with error code: " << iResult << std::endl;
        return 1;
    }
    else
    {
        std::cout << "Initialize Winsock (WSAStartup) succeded." << std::endl;
    }
    
    // Create a socket
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET)
    {
        std::cout << "socket failed with error code: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }
    else
    {
        std::cout << "Socket succesfully created. " << std::endl;
    }

    sockaddr_in serverInfo;
    serverInfo.sin_family = AF_INET;
    serverInfo.sin_port = htons(13337); // ??
    inet_pton(AF_INET, "127.0.0.1", &serverInfo.sin_addr);
    iResult = connect(sock, (SOCKADDR*)&serverInfo, sizeof(serverInfo));
    if (iResult == SOCKET_ERROR)
    {
        std::cout << "connect failed with error code: " << WSAGetLastError() << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }
    else
    {
        std::cout << "Succeded connecting to 127.0.0.1:13337." << std::endl;
    }

    // Send "hello from c++ client" to the server
    const char* message = "Hello from C++ client";
    iResult = send(sock, message, (int)strlen(message), 0);
    if (iResult == SOCKET_ERROR)
    {
        std::cout << "send failed with error code: " << WSAGetLastError() << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }
    else
    {
        std::cout << "Succeded sending 'hello world' to 127.0.0.1:13337." << std::endl;
    }

    // Close the socket
    iResult = closesocket(sock);
    if (iResult == SOCKET_ERROR)
    {
        std::cout << "closesocket failed with error code: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }
    else
    {
        std::cout << "Succeded in closing socket." << std::endl;
    }


    WSACleanup();


    // Get the current tick count
    DWORD dwTickCount = GetTickCount();

    // Print the number of milliseconds(seconds, hours) since the system was started
    std::cout << "Number of milliseconds since system startup: " << dwTickCount << std::endl;
    std::cout << "Number of seconds since system startup: " << dwTickCount / 1000 << std::endl;
    std::cout << "Number of hours since system startup: " << dwTickCount / (3600*1000) << std::endl;

    LASTINPUTINFO lii;
    lii.cbSize = sizeof(LASTINPUTINFO);
    std::cout << "lii.cbSize = " << lii.cbSize;

    // https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getlastinputinfo
    //GetLastInputInfo : "If the function succeeds, the return value is nonzero."
    // Так что начнём с проверки, что функция вернула не 0, и если всё в порядке, то это
    // значит что в структуру LASTINPUTINFO была записана нужная информация, которую мы извлечём и обработаем.

    //Sleep(3000);

    if (GetLastInputInfo(&lii))
    {
        // извлекаем из структуры LASTINPUTINFO кол-во миллисекунд (от старта системы до последнего события активности (ввода) пользователя (у которого запущена программа).
        DWORD dwLastInputTickCount = lii.dwTime;
        std::cout << "lii.dwTime = " << lii.dwTime << std::endl;
        
        // теперь возьмём текущий tick count, и вычтем из него dwLastInputTickCount, что бы получить 
        // кол-во миллисекунд прошедших с последнего user-input (мышь и клавиатура) события.
        DWORD dwIdleTime = dwTickCount - dwLastInputTickCount;
        std::cout << "dwIdleTime = (ms)" << dwIdleTime << std::endl;
        std::cout << "dwIdleTime = (seconds)" << dwIdleTime / 1000 << std::endl;
        // Print the tick count since the last input event

    }
    else
    {
        // если же GetLastInputInfo вернула 0, то выведем сообщение об ошибке.
        DWORD dwError = GetLastError();
        std::cout << "GetLastInputInfo left behind following error code: " << dwError << std::endl;
    }

    return 0;


}


// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
