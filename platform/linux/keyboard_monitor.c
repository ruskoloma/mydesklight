/*
 * mydesklight - Linux Keyboard Monitor
 * Monitors keyboard layout changes and sends UDP commands to Govee devices
 * Supports both X11 and Wayland
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <time.h>
#include <pthread.h>

#ifdef HAVE_X11
#include <X11/Xlib.h>
#include <X11/XKBlib.h>
#endif

// Configuration
#define GOVEE_PORT 4003
#define KEEPALIVE_INTERVAL 20  // seconds
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
static int udpSocket = -1;
static struct sockaddr_in goveeAddr;
static char currentLayout[256] = "";
static volatile int running = 1;
static pthread_t keepaliveThread;

// Function prototypes
void sendUDPCommand(const char* json);
void sendColorCommand(int r, int g, int b, int isKeepalive);
void sendTurnOffCommand(void);
int isEnglishLayout(const char* layout);
void* keepaliveThreadFunc(void* arg);
void signalHandler(int sig);

#ifdef HAVE_X11
void monitorX11(void);
const char* getCurrentLayoutX11(Display* display);
#endif

void monitorGeneric(void);
const char* getCurrentLayoutGeneric(void);

// Send UDP command to Govee device
void sendUDPCommand(const char* json) {
    for (int i = 0; i < UDP_REPEAT; i++) {
        ssize_t result = sendto(udpSocket, json, strlen(json), 0,
                               (struct sockaddr*)&goveeAddr, sizeof(goveeAddr));
        
        if (result < 0) {
            perror("ERROR: sendto failed");
        }
        
        if (i < UDP_REPEAT - 1) {
            usleep(UDP_DELAY_MS * 1000);
        }
    }
}

// Send color command
void sendColorCommand(int r, int g, int b, int isKeepalive) {
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
void sendTurnOffCommand(void) {
    const char* json = "{\"msg\":{\"cmd\":\"turn\",\"data\":{\"value\":0}}}";
    printf("Turning off lights\n");
    sendUDPCommand(json);
}

// Check if layout is English
int isEnglishLayout(const char* layout) {
    return (strstr(layout, "us") != NULL) ||
           (strstr(layout, "en") != NULL) ||
           (strstr(layout, "English") != NULL) ||
           (strcmp(layout, "ABC") == 0);
}

// Keepalive thread
void* keepaliveThreadFunc(void* arg) {
    while (running) {
        sleep(KEEPALIVE_INTERVAL);
        
        if (running && strlen(currentLayout) > 0) {
            printf("Keepalive: sending current layout (%s)\n", currentLayout);
            
            if (isEnglishLayout(currentLayout)) {
                sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, 1);
            } else {
                sendColorCommand(OTHER_R, OTHER_G, OTHER_B, 1);
            }
        }
    }
    return NULL;
}

// Signal handler for clean shutdown
void signalHandler(int sig) {
    printf("\nShutting down...\n");
    running = 0;
}

#ifdef HAVE_X11
// Get current keyboard layout (X11)
const char* getCurrentLayoutX11(Display* display) {
    static char layoutName[256];
    
    XkbStateRec state;
    XkbGetState(display, XkbUseCoreKbd, &state);
    
    XkbDescPtr desc = XkbGetKeyboard(display, XkbAllComponentsMask, XkbUseCoreKbd);
    if (!desc) {
        return "unknown";
    }
    
    Atom atom = desc->names->groups[state.group];
    if (atom != None) {
        char* name = XGetAtomName(display, atom);
        if (name) {
            strncpy(layoutName, name, sizeof(layoutName) - 1);
            layoutName[sizeof(layoutName) - 1] = '\0';
            XFree(name);
            XkbFreeKeyboard(desc, 0, True);
            return layoutName;
        }
    }
    
    XkbFreeKeyboard(desc, 0, True);
    return "unknown";
}

// Monitor keyboard layout changes (X11)
void monitorX11(void) {
    Display* display = XOpenDisplay(NULL);
    if (!display) {
        fprintf(stderr, "ERROR: Cannot open X11 display\n");
        exit(1);
    }
    
    // Enable XKB extension
    int xkbEventType;
    if (!XkbQueryExtension(display, NULL, &xkbEventType, NULL, NULL, NULL)) {
        fprintf(stderr, "ERROR: XKB extension not available\n");
        XCloseDisplay(display);
        exit(1);
    }
    
    // Select XKB events
    XkbSelectEvents(display, XkbUseCoreKbd, XkbStateNotifyMask, XkbStateNotifyMask);
    
    // Get initial layout
    const char* layout = getCurrentLayoutX11(display);
    strncpy(currentLayout, layout, sizeof(currentLayout) - 1);
    printf("Current layout: %s\n", currentLayout);
    
    // Send initial color
    if (isEnglishLayout(currentLayout)) {
        sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, 0);
    } else {
        sendColorCommand(OTHER_R, OTHER_G, OTHER_B, 0);
    }
    
    printf("Subscribed to keyboard layout events (X11)\n");
    
    // Event loop
    XEvent event;
    while (running) {
        if (XPending(display) > 0) {
            XNextEvent(display, &event);
            
            if (event.type == xkbEventType) {
                XkbEvent* xkbEvent = (XkbEvent*)&event;
                if (xkbEvent->any.xkb_type == XkbStateNotify) {
                    layout = getCurrentLayoutX11(display);
                    
                    if (strcmp(layout, currentLayout) != 0) {
                        printf("Layout changed: %s -> %s\n", currentLayout, layout);
                        strncpy(currentLayout, layout, sizeof(currentLayout) - 1);
                        
                        if (isEnglishLayout(currentLayout)) {
                            printf("English layout detected\n");
                            sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, 0);
                        } else {
                            printf("Other layout detected\n");
                            sendColorCommand(OTHER_R, OTHER_G, OTHER_B, 0);
                        }
                    }
                }
            }
        } else {
            usleep(100000);  // 100ms
        }
    }
    
    XCloseDisplay(display);
}
#endif

// Get current keyboard layout (generic - using setxkbmap)
const char* getCurrentLayoutGeneric(void) {
    static char layoutName[256];
    FILE* fp = popen("setxkbmap -query | grep layout | awk '{print $2}'", "r");
    
    if (fp) {
        if (fgets(layoutName, sizeof(layoutName), fp)) {
            // Remove newline
            layoutName[strcspn(layoutName, "\n")] = 0;
            pclose(fp);
            return layoutName;
        }
        pclose(fp);
    }
    
    return "unknown";
}

// Monitor keyboard layout changes (generic - polling)
void monitorGeneric(void) {
    printf("Using generic layout detection (polling every 2 seconds)\n");
    printf("Note: For better performance, compile with X11 support\n");
    
    // Get initial layout
    const char* layout = getCurrentLayoutGeneric();
    strncpy(currentLayout, layout, sizeof(currentLayout) - 1);
    printf("Current layout: %s\n", currentLayout);
    
    // Send initial color
    if (isEnglishLayout(currentLayout)) {
        sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, 0);
    } else {
        sendColorCommand(OTHER_R, OTHER_G, OTHER_B, 0);
    }
    
    // Poll for changes
    while (running) {
        sleep(2);
        
        layout = getCurrentLayoutGeneric();
        
        if (strcmp(layout, currentLayout) != 0) {
            printf("Layout changed: %s -> %s\n", currentLayout, layout);
            strncpy(currentLayout, layout, sizeof(currentLayout) - 1);
            
            if (isEnglishLayout(currentLayout)) {
                printf("English layout detected\n");
                sendColorCommand(ENGLISH_R, ENGLISH_G, ENGLISH_B, 0);
            } else {
                printf("Other layout detected\n");
                sendColorCommand(OTHER_R, OTHER_G, OTHER_B, 0);
            }
        }
    }
}

int main(int argc, char* argv[]) {
    printf("mydesklight - Linux Keyboard Monitor\n");
    printf("=====================================\n");
    
    // Check arguments
    if (argc < 2) {
        printf("ERROR: IP address not specified\n");
        printf("Usage: ./keyboard_monitor <IP_ADDRESS>\n");
        return 1;
    }
    
    const char* goveeIP = argv[1];
    printf("Govee IP: %s:%d\n", goveeIP, GOVEE_PORT);
    
    // Setup signal handlers
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    // Create UDP socket
    udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (udpSocket < 0) {
        perror("ERROR: socket creation failed");
        return 1;
    }
    
    // Setup Govee address
    memset(&goveeAddr, 0, sizeof(goveeAddr));
    goveeAddr.sin_family = AF_INET;
    goveeAddr.sin_port = htons(GOVEE_PORT);
    
    if (inet_pton(AF_INET, goveeIP, &goveeAddr.sin_addr) <= 0) {
        fprintf(stderr, "ERROR: Invalid IP address\n");
        close(udpSocket);
        return 1;
    }
    
    // Start keepalive thread
    if (pthread_create(&keepaliveThread, NULL, keepaliveThreadFunc, NULL) != 0) {
        perror("ERROR: Failed to create keepalive thread");
        close(udpSocket);
        return 1;
    }
    
    printf("Keepalive timer started (every 20 sec)\n");
    
    // Start monitoring based on available features
#ifdef HAVE_X11
    monitorX11();
#else
    monitorGeneric();
#endif
    
    // Cleanup
    pthread_join(keepaliveThread, NULL);
    close(udpSocket);
    
    return 0;
}
