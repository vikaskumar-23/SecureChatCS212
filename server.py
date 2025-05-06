import socket
import threading
import struct

HOST = '0.0.0.0'
PORT = 12345
MAX_BUFFER = 4096

clients = []
clients_lock = threading.Lock()

def send_framed(conn: socket.socket, header: bytes, payload: bytes):
    packet = header + payload
    length = struct.pack('!I', len(packet))
    conn.sendall(length + packet)

def broadcast(header: bytes, payload: bytes, sender_conn: socket.socket):
    with clients_lock:
        for conn, _ in clients:
            if conn is not sender_conn:
                try:
                    send_framed(conn, header, payload)
                except Exception:
                    pass

def handle_client(conn: socket.socket, addr):
    try:
        raw = conn.recv(MAX_BUFFER)
        username = raw.decode().strip()
        with clients_lock:
            clients.append((conn, username))
        print(f"[+] {username} connected from {addr}")

        header = b"system||"
        payload = f"** {username} has joined the chat **".encode()
        broadcast(header, payload, conn)

        while True:
            length_bytes = conn.recv(4)
            if not length_bytes:
                break
            msg_len = struct.unpack('!I', length_bytes)[0]

            data = b''
            while len(data) < msg_len:
                chunk = conn.recv(min(MAX_BUFFER, msg_len - len(data)))
                if not chunk:
                    break
                data += chunk
            if not data:
                break

            header = username.encode() + b"||"
            broadcast(header, data, conn)

    except ConnectionResetError:
        pass
    finally:
        with clients_lock:
            clients[:] = [(c,u) for c,u in clients if c is not conn]
        print(f"[-] {username} disconnected")
        header = b"system||"
        payload = f"** {username} has left the chat **".encode()
        broadcast(header, payload, conn)
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down")
    finally:
        server.close()

if __name__ == "__main__":
    main()
