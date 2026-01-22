/*
 * mydesklight - Windows Keyboard Monitor
 * Monitors keyboard layout changes and sends UDP commands to Govee devices
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#pragma comment(lib, "ws2_32.lib")

// Configuration
#define GOVEE_PORT 4003
#define KEEPALIVE_INTERVAL 20000  // 20 seconds in milliseconds
#define UDP_REPEAT 3
#define UDP_DELAY_MS 10

// Colors
#define ENGLISH_R 255
#define ENGLISH_G 180
#define ENGLISH_B 110

#define OTHER_R 120
#define OTHER_G 180
#define OTHER_B 255

// Global state
static SOCKET udpSocket = INVALID_SOCKET;
static struct sockaddr_in goveeAddr;
static char currentLayout[256] = "";
static BOOL isScreenLocked = FALSE;
static UINT_PTR keepaliveTimer = 0;

// Function prototypes
void sendUDPCommand(const char* json);
void sendColorCommand(int r, int g, int b, BOOL isKeepalive);
void sendTurnOffCommand();
void updateLayoutColor();
const char* getCurrentLayout();
BOOL isEnglishLayout(const char* layout);
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
void CALLBACK KeepaliveTimerProc(HWND hwnd, UINT uMsg, UINT_PTR idEvent, DWORD dwTime);

// Send UDP command to Govee device
void sendUDPCommand(const char* json) {
    for (int i = 0; i < UDP_REPEAT; i++) {
        int result = sendto(udpSocket, json, (int)strlen(json), 0,
                           (struct sockaddr*)&goveeAddr, sizeof(goveeAddr));
        
        if (result == SOCKET_ERROR) {
            printf("ERROR: sendto failed with error: %d\n", WSAGetLastError());
        }
        
        if (i < UDP_REPEAT - 1) {
            Sleep(UDP_DELAY_MS);
        }
    }
}

// Send color command
void sendColorCommand(int r, int g, int b, BOOL isKeepalive) {
    char json[512];
    snprintf(json, sizeof(json),
             "{\"msg\":{\"cmd\":\"colorwc\",\"data\":{\"color\":{\"r\":%d,\"g\":%d,\"b\":%d},\"colorTemInKelvin\":0}}}",
             r, g, b);
    
    if (!isKeepalive) {
        printf("Setting color: RGB(%d, %d, %d)\n", r, g, b);
    }
    
    sendUDPCommand(json);
}

// Send turn off command
void sendTurnOffCommand() {
    const char* json = "{\"msg\":{\"cmd\":\"turn\",\"data\":{\"value\":0}}}";
    printf("Turning off lights\n");
    sendUDPCommand(json);
}

// Get current keyboard layout name
const char* getCurrentLayout() {
    static char layoutName[KL_NAMELENGTH];
    HKL hkl = GetKeyboardLayout(0);
    
    // Get layout ID
    LANGID langId = LOWORD(hkl);
    
    // Get language name
    GetLocaleInfoA(MAKELCID(langId, SORT_DEFAULT), LOCALE_SENGLANGUAGE,
                   layoutName, sizeof(layoutName));
    
    return layoutName;
}

// Check if layout is English
BOOL isEnglishLayout(const char* layout) {
    return (strstr(layout, "English") != NULL) ||
           (strcmp(layout, "US") == 0) ||
           (strcmp(layout, "ABC") == 0);
}

// Update color based on current layout
void updateLayoutColor() {
    const char* layout = getCurrentLayout();
    
    if (strcmp(layout, currentLayout) != 0) {
        printf("Layout changed: %s -> %s\n", currentLayout, layout);
        strncpy(currentLayout, layout, sizeof(currentLayout) - 1);
        
        if (!isScreenLocked) {
            if (isEnglishLayout(layout)) {
                printf("English layout detected\n");
                sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, FALSE);
            } else {
                printf("Other layout detected\n");
                sendColorCommand(OTHER_R, OTHER_G, OTHER_B, FALSE);
            }
        }
    }
}

// Keepalive timer callback
void CALLBACK KeepaliveTimerProc(HWND hwnd, UINT uMsg, UINT_PTR idEvent, DWORD dwTime) {
    if (!isScreenLocked && strlen(currentLayout) > 0) {
        printf("Keepalive: sending current layout (%s)\n", currentLayout);
        
        if (isEnglishLayout(currentLayout)) {
            sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, TRUE);
        } else {
            sendColorCommand(OTHER_R, OTHER_G, OTHER_B, TRUE);
        }
    }
}

// Window procedure for handling messages
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_INPUTLANGCHANGE:
            updateLayoutColor();
            return 0;
        
        case WM_WTSSESSION_CHANGE:
            if (wParam == WTS_SESSION_LOCK) {
                printf("Screen locked - turning off lamps\n");
                isScreenLocked = TRUE;
                if (keepaliveTimer) {
                    KillTimer(hwnd, keepaliveTimer);
                    keepaliveTimer = 0;
                }
                sendTurnOffCommand();
            } else if (wParam == WTS_SESSION_UNLOCK) {
                printf("Screen unlocked - restoring lamp color\n");
                isScreenLocked = FALSE;
                updateLayoutColor();
                keepaliveTimer = SetTimer(hwnd, 1, KEEPALIVE_INTERVAL, KeepaliveTimerProc);
            }
            return 0;
        
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
    }
    
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

int main(int argc, char* argv[]) {
    printf("mydesklight - Windows Keyboard Monitor\n");
    printf("=======================================\n");
    
    // Check arguments
    if (argc < 2) {
        printf("ERROR: IP address not specified\n");
        printf("Usage: KeyboardMonitor.exe <IP_ADDRESS>\n");
        return 1;
    }
    
    const char* goveeIP = argv[1];
    printf("Govee IP: %s:%d\n", goveeIP, GOVEE_PORT);
    
    // Initialize Winsock
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        printf("ERROR: WSAStartup failed: %d\n", result);
        return 1;
    }
    
    // Create UDP socket
    udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket == INVALID_SOCKET) {
        printf("ERROR: socket failed: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
    
    // Setup Govee address
    memset(&goveeAddr, 0, sizeof(goveeAddr));
    goveeAddr.sin_family = AF_INET;
    goveeAddr.sin_port = htons(GOVEE_PORT);
    inet_pton(AF_INET, goveeIP, &goveeAddr.sin_addr);
    
    // Get initial layout
    const char* layout = getCurrentLayout();
    strncpy(currentLayout, layout, sizeof(currentLayout) - 1);
    printf("Current layout: %s\n", currentLayout);
    
    // Send initial color
    if (isEnglishLayout(currentLayout)) {
        sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, FALSE);
    } else {
        sendColorCommand(OTHER_R, OTHER_G, OTHER_B, FALSE);
    }
    
    // Register window class
    WNDCLASSA wc = {0};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = GetModuleHandle(NULL);
    wc.lpszClassName = "MyDeskLightMonitor";
    
    if (!RegisterClassA(&wc)) {
        printf("ERROR: RegisterClass failed\n");
        closesocket(udpSocket);
        WSACleanup();
        return 1;
    }
    
    // Create hidden window for message processing
    HWND hwnd = CreateWindowExA(
        0, "MyDeskLightMonitor", "MyDeskLight Monitor",
        0, 0, 0, 0, 0, HWND_MESSAGE, NULL,
        GetModuleHandle(NULL), NULL
    );
    
    if (!hwnd) {
        printf("ERROR: CreateWindow failed\n");
        closesocket(udpSocket);
        WSACleanup();
        return 1;
    }
    
    // Register for session change notifications
    WTSRegisterSessionNotification(hwnd, NOTIFY_FOR_THIS_SESSION);
    
    // Start keepalive timer
    keepaliveTimer = SetTimer(hwnd, 1, KEEPALIVE_INTERVAL, KeepaliveTimerProc);
    printf("Keepalive timer started (every 20 sec)\n");
    printf("Subscribed to keyboard layout and session events\n");
    
    // Message loop
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    // Cleanup
    if (keepaliveTimer) {
        KillTimer(hwnd, keepaliveTimer);
    }
    WTSUnRegisterSessionNotification(hwnd);
    closesocket(udpSocket);
    WSACleanup();
    
    return 0;
}
