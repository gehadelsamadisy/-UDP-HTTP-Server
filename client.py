from rudp import ReliableUDP

def main():
    client = ReliableUDP("127.0.0.1", 10001, "127.0.0.1", 10000)
    client.connect()
    print("[CLIENT] Connected to server")

    client.send_stop_and_wait(b"Hello, server!")
    client.send_stop_and_wait(b"This is the second message.")
    client.send_stop_and_wait(b"Final message. Bye!")

    client.close()
    print("[CLIENT] Connection closed")

if __name__ == "__main__":
    main()
