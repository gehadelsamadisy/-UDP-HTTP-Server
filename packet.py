# Design the packet format with the following fields:

#     Sequence number

#     Acknowledgment number

#     Flags (SYN, ACK, FIN)

#     Payload (data)

#     Checksum

#     1.2 Define constants for packet    flags (e.g., SYN = 0x1, ACK = 0x2, etc.)


# | seq_num (4) | ack_num (4) | flags (1) | checksum (2) | payload_len (2) | payload (n bytes) |



# 1 - Constants and Imports:
import struct
import zlib

# Flag constants
SYN = 0x01
ACK = 0x02
FIN = 0x04


def calculate_checksum(seq_num, ack_num, flags, payload):
    """
    Calculate a 16-bit checksum using CRC32, truncated.
    """
    data = struct.pack('!IIBH', seq_num, ack_num, flags, len(payload)) + payload
    checksum = zlib.crc32(data) & 0xFFFF  # Only keep 16 bits
    return checksum

def serialize_packet(seq_num, ack_num, flags, payload):
    """
    Create a byte-encoded packet from fields.
    """
    # Structure: [seq(4 bytes), ack(4 bytes), flags(1 byte), payload, checksum(1 byte)]
    
    checksum = calculate_checksum(seq_num, ack_num, flags, payload)
    payload_len = len(payload)
    header = struct.pack('!IIBHH', seq_num, ack_num, flags, checksum, payload_len)
    return header + payload

def deserialize_packet(data):
    """
    Extract packet fields from byte stream. Verifies checksum.
    """
    if len(data) < 13:
        raise ValueError("Packet too short.")

    header = data[:13]
    seq_num, ack_num, flags, checksum, payload_len = struct.unpack('!IIBHH', header)
    payload = data[13:13 + payload_len]

    calc_checksum = calculate_checksum(seq_num, ack_num, flags, payload)
    if calc_checksum != checksum:
        raise ValueError("Checksum mismatch (packet corrupted).")

    return {
        'seq_num': seq_num,
        'ack_num': ack_num,
        'flags': flags,
        'checksum': checksum,
        'payload': payload
    }

# Simulated payload
payload = b"GET /index.html HTTP/1.0\r\n\r\n"

# Serialize
packet_bytes = serialize_packet(seq_num=1, ack_num=0, flags=SYN, payload=payload)

# Deserialize
try:
    packet = deserialize_packet(packet_bytes)
    print("Packet decoded successfully:", packet)
except ValueError as e:
    print("Error:", e)
