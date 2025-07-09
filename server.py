from rudp import ReliableUDP

def main():
    server = ReliableUDP("127.0.0.1", 10000)
    print("[SERVER] Listening on 127.0.0.1:10000")

    try:
        while True:
            # Accept connection (3-way handshake)
            server.accept()
            print("[SERVER] Client connected!")

            while True:
                data = server.receive_stop_and_wait()
                if data is None:
                    print("[SERVER] Client closed connection.")
                    break
                print("[SERVER] Received:", data.decode())

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
