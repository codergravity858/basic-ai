#include <iostream>
#include <string>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

int main() {
    const char* SERVER_IP = "127.0.0.1";
    const int SERVER_PORT = 49153;

    // 1. Create socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cerr << "Error creating socket." << std::endl;
        return -1;
    }

    // 2. Define server address
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

    // 3. Connect to Python server
    std::cout << "Connecting to AI server..." << std::endl;
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Connection failed! Make sure server.py is running." << std::endl;
        close(sock);
        return -1;
    }

    std::cout << "Connected! Type your message (type 'exit' to quit):\n" << std::endl;

    std::string user_input;
    char buffer[1024];

    // 4. Chat Loop
    while (true) {
        std::cout << "[You]: ";
        std::getline(std::cin, user_input);

        if (user_input.empty()) continue;

        // Send to Python server
        send(sock, user_input.c_str(), user_input.length(), 0);

        if (user_input == "exit" || user_input == "bye") {
            break;
        }

        // Receive response from Python server
        std::memset(buffer, 0, sizeof(buffer));
        int bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
        
        if (bytes_received > 0) {
            std::cout << "[AI]: " << buffer << std::endl;
        } else {
            std::cout << "[System]: Server disconnected." << std::endl;
            break;
        }
    }

    // 5. Cleanup
    close(sock);
    std::cout << "Chat session ended." << std::endl;
    return 0;
}
