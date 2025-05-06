import streamlit as st
import socket
import struct
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ── Byte-wise Shift Cipher Encryption ────────────────────────────────────────
class CustomEncryption:
    @staticmethod
    def get_shift_value(key: int) -> int:
        # Use full byte range
        return key % 256

    @staticmethod
    def encrypt_message(msg: str, key: int) -> bytes:
        shift = CustomEncryption.get_shift_value(key)
        data = msg.encode('utf-8')
        encrypted_bytes = bytes((b + shift) % 256 for b in data)
        return encrypted_bytes

    @staticmethod
    def decrypt_message(data: bytes, key: int) -> str:
        shift = CustomEncryption.get_shift_value(key)
        decrypted_bytes = bytes((b - shift + 256) % 256 for b in data)
        try:
            return decrypted_bytes.decode('utf-8', errors='replace')
        except Exception:
            return "[Decryption error]"

# ── Configuration ───────────────────────────────────────────────────────────
SERVER_HOST = "localhost"
SERVER_PORT = 12345
BUFFER_SIZE = 4096

# ── Session State Initialization ─────────────────────────────────────────────
if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.sock = None
    st.session_state.buffer = b''
    st.session_state.chat_log = []
    st.session_state.username = ""
    st.session_state.key = 0

# ── Helper to connect ─────────────────────────────────────────────────────────
def connect_to_server(username: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    sock.sendall(username.encode())
    sock.setblocking(False)
    return sock

# ── LOGIN FORM ───────────────────────────────────────────────────────────────
if not st.session_state.connected:
    st.title("🔒 SecureChat (Socket Edition)")
    with st.form("login", clear_on_submit=True):
        uname     = st.text_input("Username")
        key_str   = st.text_input("Encryption key (integer)")
        submitted = st.form_submit_button("Connect")
    if submitted:
        try:
            key  = int(key_str)
            sock = connect_to_server(uname)
            st.session_state.username  = uname
            st.session_state.key       = key
            st.session_state.sock      = sock
            st.session_state.connected = True
        except ValueError:
            st.error("Encryption key must be an integer.")
        except Exception as e:
            st.error(f"Connection failed: {e}")
    if not st.session_state.connected:
        st.stop()

# ── AUTO‑REFRESH EVERY 2 SECONDS ─────────────────────────────────────────────
_ = st_autorefresh(interval=2000, limit=None, key="auto_refresh")

# ── CHAT INTERFACE ───────────────────────────────────────────────────────────
st.sidebar.markdown(f"**User:** {st.session_state.username}")
st.sidebar.markdown(f"**Key:** {st.session_state.key}")
st.sidebar.warning("Keep your key secret!")
st.header("🌍 Chat Room")

# ── 1) Read & buffer incoming bytes, extract framed messages ─────────────────
try:
    while True:
        chunk = st.session_state.sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        st.session_state.buffer += chunk

        # Process all complete frames
        while len(st.session_state.buffer) >= 4:
            msg_len = struct.unpack('!I', st.session_state.buffer[:4])[0]
            if len(st.session_state.buffer) < 4 + msg_len:
                break
            packet = st.session_state.buffer[4:4+msg_len]
            st.session_state.buffer = st.session_state.buffer[4+msg_len:]

            # Split header vs. payload
            try:
                user_bytes, payload = packet.split(b"||", 1)
                user = user_bytes.decode()
            except ValueError:
                user    = None
                payload = packet

            # Timestamp
            ts = datetime.now().strftime("%H:%M:%S")
            if user == "system":
                text = payload.decode('utf-8', errors='ignore')
                st.session_state.chat_log.append(f"[{ts}] {text}")
            else:
                text = CustomEncryption.decrypt_message(payload, st.session_state.key)
                st.session_state.chat_log.append(f"[{ts}] {user}: {text}")

except BlockingIOError:
    pass
except Exception as e:
    st.error(f"Receive error: {e}")

# ── 2) Display chat history ─────────────────────────────────────────────────
for line in st.session_state.chat_log:
    st.markdown(f"> {line}")

# ── 3) Message input & send ─────────────────────────────────────────────────
with st.form("send", clear_on_submit=True):
    txt  = st.text_input("Message", "")
    send = st.form_submit_button("Send")

if send and txt:
    payload = CustomEncryption.encrypt_message(txt, st.session_state.key)
    length  = struct.pack('!I', len(payload))
    try:
        st.session_state.sock.sendall(length + payload)
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_log.append(f"[{ts}] {st.session_state.username}: {txt}")
    except Exception as e:
        st.error(f"Send failed: {e}")