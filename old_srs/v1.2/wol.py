from secrets import SECRET_MAC_ADDRESS

mac_address = SECRET_MAC_ADDRESS.replace(':', '').replace('-', '').lower()
mac_address_bytes = b''.join(bytes([int(mac_address[i:i+2], 16)]) for i in range(0, len(mac_address), 2))
magic_packet = b'\xFF' * 6 + mac_address_bytes * 16
del mac_address, mac_address_bytes

def wol():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(magic_packet, ('255.255.255.255', 9))
    sock.close()
