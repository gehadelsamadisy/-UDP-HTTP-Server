from httpclient import HTTPClient

def main():
    print("=" * 50)
    print("RUNNING TEST: Loss + Corruption")
    print("Loss Probability: 0.2, Corruption Probability: 0.2")
    print("=" * 50)

    try:
        client = HTTPClient(
            local_port=10001,
            server_ip="127.0.0.1",
            server_port=10000,
            loss_prob=0.2,
            corrupt_prob=0.2
        )

        response = client.send_get("index.html")
        print(f"Response received: {response}")
        print("[Loss + Corruption Test] Complete.\n\n")
    except Exception as e:
        print(f"Error in test: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main() 