import socket
import random
from packet import serialize_packet, deserialize_packet, SYN, ACK, FIN

class ReliableUDP:
    def __init__(self, local_ip, local_port, remote_ip=None, remote_port=None, loss_prob=0.0, corrupt_prob=0.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((local_ip, local_port))
        self.sock.settimeout(2.0)

        self.loss_prob = loss_prob
        self.corrupt_prob = corrupt_prob

        self.remote_addr = (remote_ip, remote_port) if remote_ip and remote_port else None

        self.connected = False
        self.seq_num = 0
        self.ack_num = 0

    def set_remote(self, ip, port):
        self.remote_addr = (ip, port)

    def should_drop(self):
        return random.random() < self.loss_prob

    def should_corrupt(self):
        return random.random() < self.corrupt_prob

    def send(self, payload: bytes, seq=0, ack=0, flags=0):
        if not self.remote_addr:
            raise ValueError("Remote address not set")

        if self.should_drop():
            print("[SIMULATION] Dropping outgoing packet")
            return

        raw_data = serialize_packet(seq, ack, flags, payload)

        if self.should_corrupt():
            raw_data = bytearray(raw_data)
            raw_data[-1] ^= 0xFF
            raw_data = bytes(raw_data)
            print("[SIMULATION] Corrupted outgoing packet")

        self.sock.sendto(raw_data, self.remote_addr)
        print(f"[SEND] Packet sent: seq={seq}, ack={ack}, flags={flags}")

    def receive(self) -> tuple:
        try:
            data, addr = self.sock.recvfrom(5000)

            if self.should_drop():
                print("[SIMULATION] Dropping incoming packet")
                return None, addr

            try:
                packet = deserialize_packet(data)
            except ValueError:
                print("[RECV] Corrupt packet dropped.")
                return None, addr

            print(f"[RECV] Packet received: seq={packet['seq_num']}, flags={packet['flags']}")
            return packet, addr

        except socket.timeout:
            print("[RECV] Timeout.")
            return None, None

    def connect(self):
        if not self.remote_addr:
            raise ValueError("Remote address not set")

        self.seq_num = random.randint(0, 1000)
        max_retries = 5
        retry_count = 0
        timeout = 2.0
        max_timeout = 8.0

        while retry_count < max_retries:
            try:
                self.sock.settimeout(timeout)
                self.send(b'', seq=self.seq_num, flags=SYN)

                while True:
                    packet, addr = self.receive()
                    if packet is None:
                        raise TimeoutError()

                    if packet['flags'] & SYN and packet['flags'] & ACK:
                        self.ack_num = packet['seq_num'] + 1
                        self.send(b'', seq=self.seq_num + 1, ack=self.ack_num, flags=ACK)
                        self.connected = True
                        self.sock.settimeout(2.0)
                        print("[CONN] Connection established")
                        return

            except TimeoutError:
                print(f"[CONN] Timeout waiting for SYN-ACK (timeout={timeout}s). Retrying...")
                retry_count += 1
                timeout = min(timeout * 2, max_timeout)

        raise TimeoutError("Connection failed after maximum retries")

    def accept(self):
        print("[SERVER] Waiting for SYN...")
        while True:
            packet, addr = self.receive()
            if packet is None:
                continue

            if packet['flags'] & SYN:
                print(f"[SERVER] Received SYN(seq={packet['seq_num']}) from {addr}")
                self.set_remote(*addr)

                self.seq_num = random.randint(0, 1000)
                self.ack_num = packet['seq_num'] + 1

                self.send(b'', seq=self.seq_num, ack=self.ack_num, flags=SYN | ACK)
                print(f"[SERVER] Sent SYN-ACK(seq={self.seq_num}, ack={self.ack_num})")

                while True:
                    packet2, _ = self.receive()
                    if packet2 and (packet2['flags'] & ACK) and packet2['ack_num'] == self.seq_num + 1:
                        self.connected = True
                        self.seq_num += 1
                        print("[SERVER] Handshake complete, connection established")
                        return

    def disconnect(self):
        if not self.connected:
            return

        self.send(b'', seq=self.seq_num, flags=FIN)

        while True:
            packet, addr = self.receive()
            if packet is None:
                print("[DISC] Timeout waiting for ACK. Retrying...")
                self.send(b'', seq=self.seq_num, flags=FIN)
                continue

            if packet['flags'] & ACK:
                self.connected = False
                print("[DISC] Connection closed")
                break

    def send_stop_and_wait(self, payload: bytes):
        if not self.connected:
            self.connect()

        seq = self.seq_num
        max_retries = 5
        retry_count = 0
        timeout = 2.0
        max_timeout = 8.0

        while retry_count < max_retries:
            try:
                self.sock.settimeout(timeout)
                self.send(payload, seq=seq, flags=0)

                while True:
                    packet, addr = self.receive()
                    if packet is None:
                        raise TimeoutError()

                    if packet['flags'] & ACK and packet['ack_num'] == seq + 1:
                        print(f"[ACK RECEIVED] ack={packet['ack_num']}")
                        self.seq_num = seq + 1
                        self.sock.settimeout(2.0)
                        return

            except TimeoutError:
                print(f"[SEND] Timeout waiting for ACK (timeout={timeout}s). Retrying...")
                retry_count += 1
                timeout = min(timeout * 2, max_timeout)

        raise TimeoutError("Send failed after maximum retries")

    def receive_stop_and_wait(self):
        last_seq = -1
        max_retries = 5
        retry_count = 0
        timeout = 2.0
        max_timeout = 8.0

        while retry_count < max_retries:
            try:
                self.sock.settimeout(timeout)
                packet, addr = self.receive()
                if packet is None:
                    raise TimeoutError()

                self.set_remote(*addr)
                seq = packet['seq_num']

                if packet['flags'] & FIN:
                    print("[RECV] FIN received. Sending ACK and closing.")
                    self.send(b'', seq=0, ack=seq + 1, flags=ACK)
                    self.connected = False
                    return None

                if seq == last_seq:
                    print(f"[DUPLICATE PACKET] seq={seq}. Resending ACK.")
                    self.send(b'', seq=0, ack=seq + 1, flags=ACK)
                    continue

                print(f"[NEW PACKET] seq={seq}")
                last_seq = seq
                self.send(b'', seq=0, ack=seq + 1, flags=ACK)
                self.sock.settimeout(2.0)
                return packet['payload']

            except TimeoutError:
                print(f"[RECV] Timeout waiting for packet (timeout={timeout}s). Retrying...")
                retry_count += 1
                timeout = min(timeout * 2, max_timeout)

        raise TimeoutError("Receive failed after maximum retries")

    def close(self):
        if self.connected:
            self.disconnect()
        self.sock.close()
