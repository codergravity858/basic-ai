import os
import socket
import torch
from sentence_transformers import SentenceTransformer, util

class ActiveLearningBot:
    def __init__(self, transcripts_dir="./transcripts"):
        print("[AI] Initializing PyTorch Transformer Model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.transcripts_dir = transcripts_dir
        self.phrases = []       
        self.responses = []     
        self.embeddings = None  
        
        # Ensure the transcripts directory exists
        os.makedirs(self.transcripts_dir, exist_ok=True)

    def load_transcripts(self):
        """Parses all .trans files and vectorizes them into PyTorch memory."""
        self.phrases.clear()
        self.responses.clear()
        file_count = 0
        
        for filename in os.listdir(self.transcripts_dir):
            if filename.endswith(".trans"):
                file_count += 1
                current_user = None
                with open(os.path.join(self.transcripts_dir, filename), 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("User:"):
                            current_user = line[5:].strip()
                        elif line.startswith("AI:") and current_user:
                            self.phrases.append(current_user)
                            self.responses.append(line[3:].strip())
                            current_user = None

        if not self.phrases:
            # Seed with a default pair if directory is completely empty
            self.phrases.append("hello")
            self.responses.append("Hello! I am ready to learn.")

        # Re-generate the PyTorch Tensor Embeddings
        self.embeddings = self.model.encode(self.phrases, convert_to_tensor=True)
        print(f"[Engine] Vectorized {len(self.phrases)} phrases across {file_count} file(s).")

    def append_to_transcript(self, user_msg, ai_msg):
        """Permanently saves a new interaction to a dedicated dynamic learning file."""
        dynamic_file = os.path.join(self.transcripts_dir, "dynamic_learning.trans")
        
        try:
            with open(dynamic_file, "a", encoding="utf-8") as f:
                f.write(f"\nUser: {user_msg}\n")
                f.write(f"AI: {ai_msg}\n")
            print(f"[Learning] Logged new memory to {dynamic_file}")
            
            # Re-index immediately so the model learns it for the next turn
            self.load_transcripts()
        except Exception as e:
            print(f"[Error] Failed to write to transcript: {e}")

    def process_and_learn(self, user_message):
        """Evaluates input, returns answer, and updates knowledge base if contextually novel."""
        user_message_clean = user_message.strip()
        
        # 1. Inference via Tensor Cosine Similarity Matrix
        user_embedding = self.model.encode(user_message_clean, convert_to_tensor=True)
        cos_scores = util.cos_sim(user_embedding, self.embeddings)[0]
        best_match_idx = torch.argmax(cos_scores).item()
        highest_score = cos_scores[best_match_idx].item()

        print(f"[Inference] Best Match Score: {highest_score:.4f}")

        # 2. Adaptive Logic Decision
        if highest_score > 0.75:
            # High confidence: return existing known answer
            return self.responses[best_match_idx]
        
        elif 0.40 <= highest_score <= 0.75:
            # Medium confidence: adapt the existing response, then save the new phrasing variant
            adapted_response = self.responses[best_match_idx]
            print(f"[Learning Loop] Adapting known response to a new phrasing variation.")
            self.append_to_transcript(user_message_clean, adapted_response)
            return adapted_response
        
        else:
            # Low confidence: fallback default response
            fallback_response = "I haven't encountered that concept before. I've logged it to study later!"
            # Log the unknown prompt with the fallback so a trainer can modify the AI line later
            self.append_to_transcript(user_message_clean, "Hello! Let's update this response manually.")
            return fallback_response

def start_server():
    host = '127.0.0.1'
    port = 12345
    
    bot = ActiveLearningBot()
    bot.load_transcripts() 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"[Network] Server listening on {host}:{port}")
    
    while True:
        conn, addr = server_socket.accept()
        print(f"[Network] Connection from {addr}")
        
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data or data.strip().lower() == 'exit':
                    break
                
                # Dynamic inference and internal learning execution
                response = bot.process_and_learn(data)
                conn.send(response.encode('utf-8'))
            except ConnectionResetError:
                break
        conn.close()

if __name__ == "__main__":
    start_server()
