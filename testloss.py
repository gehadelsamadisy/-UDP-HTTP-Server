from httpclient import HTTPClient

def main():
    print("=" * 50)
    print("RUNNING TEST: Packet Loss Only")
    print("Loss Probability: 0.1, Corruption Probability: 0.0")
    print("=" * 50)

    try:
        client = HTTPClient(
            local_port=10001,
            server_ip="127.0.0.1",
            server_port=10000,
            loss_prob=0.1,
            corrupt_prob=0.0
        )

        response = client.send_get("index.html")
        print(f"Response received: {response}")
        print("[Packet Loss Test] Complete.\n\n")
    except Exception as e:
        print(f"Error in test: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
