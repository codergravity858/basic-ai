#include <iostream>
#include <string>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#def VERBOSE_CONNECTION
int main() {
    const char* SERVER_IP = "127.0.0.1";
    const int SERVER_PORT = 49153;

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return -1;

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        #ifdef VERBOSE_CONNECTION
        std::cerr << "Connection failed!" << std::endl;
        #endif
        close(sock);
        return -1;
    }
#ifdef VERBOSE_CONNECTION
    std::cout << "Connected to Active Learning AI Engine.\n" << std::endl;
#endif
    std::string user_input;
    char buffer[1024];

    while (true) {
        std::cout << "[You]: ";
        std::getline(std::cin, user_input);

        if (user_input.empty()) continue;
        if (user_input == "exit") break;

        // 1. Send the actual question
        send(sock, user_input.c_str(), user_input.length(), 0);

        // 2. Receive the AI response
        std::memset(buffer, 0, sizeof(buffer));
        int bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
        
        if (bytes_received > 0) {
            std::cout << "[AI]: " << buffer << std::endl;
            
            // 3. Prompt user for dynamic training feedback
            std::string feedback;
            std::cout << "--> Was this helpful? (/good to train model, /skip to pass): ";
            std::getline(std::cin, feedback);
            
            if (feedback == "/good") {
                send(sock, "/commit", 7, 0);
                std::memset(buffer, 0, sizeof(buffer));
                recv(sock, buffer, sizeof(buffer) - 1, 0); // Wait for sync confirmation
                std::cout << "[System]: " << buffer << std::endl;
            } else {
                send(sock, "/skip", 5, 0);
            }
            std::cout << "..." << std::endl;
        } else {
            break;
        }
    }

    close(sock);
    return 0;
}
