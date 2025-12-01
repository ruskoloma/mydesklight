import Foundation
import Carbon
import Network

class KeyboardMonitor {
    private var currentLayout: String?
    private let udpConnection: NWConnection
    private let goveeIP: String
    private let goveePort: UInt16
    private var keepaliveTimer: Timer?
    private var isScreenLocked: Bool = false
    
    // Colors for different layouts
    private let englishColor = (r: 255, g: 180, b: 110)
    private let otherColor = (r: 120, g: 180, b: 255)
    
    init(goveeIP: String, goveePort: UInt16 = 4003) {
        self.goveeIP = goveeIP
        self.goveePort = goveePort
        
        // Create UDP connection
        let host = NWEndpoint.Host(goveeIP)
        let port = NWEndpoint.Port(rawValue: goveePort)!
        self.udpConnection = NWConnection(host: host, port: port, using: .udp)
        
        // Start connection
        udpConnection.start(queue: .global())
        
        print("Keyboard Monitor started")
        print("UDP: \(goveeIP):\(goveePort)")
    }
    
    func start() {
        // Get initial layout
        currentLayout = getCurrentLayout()
        if let layout = currentLayout {
            print("Current layout: \(layout)")
            sendColorCommand(for: layout)
        }
        
        // Subscribe to layout change notifications
        DistributedNotificationCenter.default().addObserver(
            self,
            selector: #selector(layoutChanged),
            name: NSNotification.Name(rawValue: kTISNotifySelectedKeyboardInputSourceChanged as String),
            object: nil
        )
        
        print("Subscribed to layout change events")
        
        // Subscribe to screen lock/unlock notifications
        DistributedNotificationCenter.default().addObserver(
            self,
            selector: #selector(screenLocked),
            name: NSNotification.Name("com.apple.screenIsLocked"),
            object: nil
        )
        
        DistributedNotificationCenter.default().addObserver(
            self,
            selector: #selector(screenUnlocked),
            name: NSNotification.Name("com.apple.screenIsUnlocked"),
            object: nil
        )
        
        print("Subscribed to screen lock/unlock events")
        
        // Start keepalive timer (every 20 seconds)
        startKeepaliveTimer()
        
        // Run event loop
        RunLoop.current.run()
    }
    
    private func startKeepaliveTimer() {
        keepaliveTimer = Timer.scheduledTimer(withTimeInterval: 20.0, repeats: true) { [weak self] _ in
            self?.sendKeepalive()
        }
        print("Keepalive timer started (every 20 sec)")
    }
    
    private func stopKeepaliveTimer() {
        keepaliveTimer?.invalidate()
        keepaliveTimer = nil
        print("Keepalive timer stopped")
    }
    
    @objc private func screenLocked() {
        print("Screen locked - turning off lamps")
        isScreenLocked = true
        stopKeepaliveTimer()
        sendTurnOffCommand()
    }
    
    @objc private func screenUnlocked() {
        print("Screen unlocked - restoring lamp color")
        isScreenLocked = false
        
        // Restore current layout color
        if let layout = currentLayout {
            sendColorCommand(for: layout)
        }
        
        // Restart keepalive timer
        startKeepaliveTimer()
    }
    
    @objc private func sendKeepalive() {
        if !isScreenLocked, let layout = currentLayout {
            print("Keepalive: sending current layout (\(layout))")
            sendColorCommand(for: layout, isKeepalive: true)
        }
    }
    
    @objc private func layoutChanged() {
        let newLayout = getCurrentLayout()
        
        if newLayout != currentLayout {
            if let layout = newLayout {
                print("Layout changed: \(currentLayout ?? "nil") -> \(layout)")
                currentLayout = layout
                
                // Only send color command if screen is not locked
                if !isScreenLocked {
                    sendColorCommand(for: layout)
                }
            }
        }
    }
    
    private func getCurrentLayout() -> String? {
        guard let source = TISCopyCurrentKeyboardInputSource()?.takeRetainedValue() else {
            return nil
        }
        
        guard let sourceID = TISGetInputSourceProperty(source, kTISPropertyInputSourceID) else {
            return nil
        }
        
        let id = Unmanaged<CFString>.fromOpaque(sourceID).takeUnretainedValue() as String
        
        // Extract layout name (e.g., "com.apple.keylayout.ABC" -> "ABC")
        return id.components(separatedBy: ".").last
    }
    
    private func sendTurnOffCommand() {
        let command: [String: Any] = [
            "msg": [
                "cmd": "turn",
                "data": [
                    "value": 0
                ]
            ]
        ]
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: command, options: [])
            
            // Send turn off command 3 times for reliability
            for i in 1...3 {
                udpConnection.send(content: jsonData, completion: .contentProcessed { error in
                    if let error = error {
                        print("ERROR sending turn off command (attempt \(i)/3): \(error)")
                    } else if i == 1 {
                        print("Turn off command sent (x3 for reliability)")
                    }
                })
                
                if i < 3 {
                    usleep(10_000)
                }
            }
        } catch {
            print("ERROR creating turn off JSON: \(error)")
        }
    }
    
    private func sendColorCommand(for layout: String, isKeepalive: Bool = false) {
        // Check if this is ABC (English layout)
        // Everything else (Russian, Russian-Phonetic, Ukrainian, etc.) is non-English
        let isEnglish = layout.uppercased() == "ABC" || layout.uppercased() == "US"
        
        let color: (r: Int, g: Int, b: Int)
        let colorTemp: Int
        
        if isEnglish {
            color = englishColor
            colorTemp = 0
            if !isKeepalive {
                print("English layout -> RGB(\(color.r), \(color.g), \(color.b)), Temp: \(colorTemp)K")
            }
        } else {
            color = otherColor
            colorTemp = 0
            if !isKeepalive {
                print("Other layout -> RGB(\(color.r), \(color.g), \(color.b)), Temp: \(colorTemp)K")
            }
        }
        
        // Build JSON command
        let command: [String: Any] = [
            "msg": [
                "cmd": "colorwc",
                "data": [
                    "color": [
                        "r": color.r,
                        "g": color.g,
                        "b": color.b
                    ],
                    "colorTemInKelvin": colorTemp
                ]
            ]
        ]
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: command, options: [])
            
            // Send UDP packet 3 times for reliability (UDP can lose packets)
            for i in 1...3 {
                udpConnection.send(content: jsonData, completion: .contentProcessed { error in
                    if let error = error {
                        print("ERROR sending UDP (attempt \(i)/3): \(error)")
                    } else if !isKeepalive && i == 1 {
                        print("UDP packet sent (x3 for reliability)")
                    }
                })
                
                // Small delay between sends (10ms)
                if i < 3 {
                    usleep(10_000)
                }
            }
        } catch {
            print("ERROR creating JSON: \(error)")
        }
    }
    
    deinit {
        keepaliveTimer?.invalidate()
        udpConnection.cancel()
        DistributedNotificationCenter.default().removeObserver(self)
    }
}

// MARK: - Main Entry Point

print("Govee Keyboard Layout Monitor")
print("================================")

// Read IP from arguments
let goveeIP: String
if CommandLine.arguments.count > 1 {
    goveeIP = CommandLine.arguments[1]
} else {
    print("ERROR: IP address not specified, usage: ./KeyboardMonitor <IP_ADDRESS>")
    print("Example: ./KeyboardMonitor 192.168.1.100")
    exit(1)
}

let monitor = KeyboardMonitor(goveeIP: goveeIP)
monitor.start()

