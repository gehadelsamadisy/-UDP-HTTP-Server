# http_client.py

from rudp import ReliableUDP

class HTTPClient:
    def __init__(self, local_port=10001, server_ip='127.0.0.1', server_port=10000, loss_prob=0.0, corrupt_prob=0.0):
        self.rudp = ReliableUDP(
            local_ip='127.0.0.1',
            local_port=local_port,
            remote_ip=server_ip,
            remote_port=server_port,
            loss_prob=loss_prob,
            corrupt_prob=corrupt_prob
        )

    def connect(self):
        self.rudp.connect()

    def send_get(self, path):
        request = f"GET /{path} HTTP/1.0\r\n\r\n"
        self.rudp.connect()
        self.rudp.send_stop_and_wait(request.encode())
        response = self.rudp.receive_stop_and_wait()
        print("[HTTP CLIENT] Response:\n", response.decode(errors='replace'))
        self.rudp.disconnect()
        return response.decode(errors='replace') if response else None

    def send_post(self, path, data):
        request = f"POST /{path} HTTP/1.0\r\n\r\n{data}"
        self.rudp.connect()
        self.rudp.send_stop_and_wait(request.encode())
        response = self.rudp.receive_stop_and_wait()
        print("[HTTP CLIENT] Response:\n", response.decode(errors='replace'))
        self.rudp.disconnect()
        return response.decode(errors='replace') if response else None

    def close(self):
        self.rudp.close()

if __name__ == "__main__":
    client = HTTPClient("127.0.0.1", 10001, "127.0.0.1", 10000)
    # client.send_get("index.html")
    # client.send_post("UPLOAD", "This is a test message!")
    

