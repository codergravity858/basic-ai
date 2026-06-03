# Recompile the client
g++ -std=c++11 client.cpp -o chatbot_client

# Run the backend first
python3 server.py

# Run the client in a separate terminal
./chatbot_client
