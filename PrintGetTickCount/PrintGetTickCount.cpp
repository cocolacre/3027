// PrintGetTickCount.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <windows.h>

int main()
{
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
    // ��� ��� ������ � ��������, ��� ������� ������� �� 0, � ���� �� � �������, �� ���
    // ������ ��� � ��������� LASTINPUTINFO ���� �������� ������ ����������, ������� �� �������� � ����������.

    Sleep(3000);

    if (GetLastInputInfo(&lii))
    {
        // ��������� �� ��������� LASTINPUTINFO ���-�� ����������� (�� ������ ������� �� ���������� ������� ���������� (�����) ������������ (� �������� �������� ���������).
        DWORD dwLastInputTickCount = lii.dwTime;
        std::cout << "lii.dwTime = " << lii.dwTime << std::endl;
        
        // ������ ������ ������� tick count, � ������ �� ���� dwLastInputTickCount, ��� �� �������� 
        // ���-�� ����������� ��������� � ���������� user-input (���� � ����������) �������.
        DWORD dwIdleTime = dwTickCount - dwLastInputTickCount;
        std::cout << "dwIdleTime = (�����������)" << dwIdleTime << std::endl;
        std::cout << "dwIdleTime = (������)" << dwIdleTime / 1000 << std::endl;
        // Print the tick count since the last input event

    }
    else
    {
        // ���� �� GetLastInputInfo ������� 0, �� ������� ��������� �� ������.
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
