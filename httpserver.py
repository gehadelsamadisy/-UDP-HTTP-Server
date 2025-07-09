from rudp import ReliableUDP
import os

class HTTPServer:
    def __init__(self, ip, port, loss_prob=0.0, corrupt_prob=0.0):
        self.rudp = ReliableUDP(ip, port, loss_prob=loss_prob, corrupt_prob=corrupt_prob)

    def start(self):
        print("[HTTP SERVER] Listening for HTTP requests...")
        
        while True:
            try:
                # Accept new connection
                self.rudp.accept()
                print("[HTTP SERVER] New client connected!")

                # Handle client requests
                while True:
                    data = self.rudp.receive_stop_and_wait()
                    if not data:
                        print("[HTTP SERVER] Client closed connection.")
                        break

                    request = data.decode()
                    print("[HTTP SERVER] Request received:")
                    print(request)

                    response = self.handle_request(request)
                    self.rudp.send_stop_and_wait(response.encode())

            except Exception as e:
                print(f"[HTTP SERVER] Error: {str(e)}")
                continue
            finally:
                # Clean up connection
                if self.rudp.connected:
                    self.rudp.disconnect()
                print("[HTTP SERVER] Ready for next connection...")

    def handle_request(self, request: str) -> str:
        lines = request.splitlines()
        if not lines:
            return "HTTP/1.0 400 Bad Request\r\n\r\n"

        method, path, _ = lines[0].split()
        path = path.lstrip("/")  # Remove leading slash

        if method == "GET":
            if os.path.exists(path):
                with open(path, 'r') as f:
                    body = f.read()
                return f"HTTP/1.0 200 OK\r\n\r\n{body}"
            else:
                return "HTTP/1.0 404 Not Found\r\n\r\nFile not found."
        elif method == "POST":
            try:
                body_index = request.index("\r\n\r\n") + 4
                body = request[body_index:]
                print(f"[HTTP SERVER] POST body:\n{body}")
                return "HTTP/1.0 200 OK\r\n\r\nPOST received successfully."
            except:
                return "HTTP/1.0 400 Bad Request\r\n\r\nInvalid POST request."
        return "HTTP/1.0 405 Method Not Allowed\r\n\r\nOnly GET supported."

if __name__ == "__main__":
    server = HTTPServer("127.0.0.1", 10000)
    server.start()
