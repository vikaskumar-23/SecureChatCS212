# SecureChat

A simple encrypted chat application built with Python sockets and Streamlit. It features a custom byte-wise shift cipher for secure messaging between clients connected to a central server.

---

## Features

* **Server** (`server.py`): Manages client connections and broadcasts framed messages to all participants.
* **Client** (`streamlit_app.py`): Streamlit-based UI for sending and receiving messages in real-time.
* **Custom Encryption**: Byte-wise shift cipher where each plaintext byte is shifted by `(key % 256)` on encryption and unshifted on decryption:

  * **Encrypt**: `(plaintext_byte + key) % 256`
  * **Decrypt**: `(ciphertext_byte - key + 256) % 256`
* **Auto-Refresh**: Chat interface refreshes every 2 seconds to fetch new messages.

---

## Prerequisites

* Python 3.7 or newer
* **pip** package manager

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/<your-username>/SecureChat.git
   cd SecureChat
   ```

2. **Install dependencies**:

   ```bash
   pip install streamlit streamlit-autorefresh
   ```

---

## Configuration

* **Server**:

  * Listens on `0.0.0.0:12345` by default.
  * Adjust `HOST` and `PORT` in `server.py` if needed.

* **Client (Streamlit)**:

  * Connects to `localhost:12345` by default.
  * Adjust `SERVER_HOST` and `SERVER_PORT` in `streamlit_app.py` to point to your server.

---

## Usage

1. **Start the server**:

   ```bash
   python server.py
   ```

   You should see:

   ```
   [*] Server listening on 0.0.0.0:12345
   ```

2. **Run the client**:

   ```bash
   streamlit run streamlit_app.py
   ```

3. **Connect**:

   * In the Streamlit UI, enter a **username** and an **integer key** (same on all clients to decrypt properly).
   * Click **Connect**.

4. **Chat**:

   * Type a message and hit **Send**.
   * Messages are encrypted on send and decrypted on receipt.

---

## Encryption Details

This project uses a simple, symmetric, byte-wise shift cipher:

1. **Key derivation**:

   ```python
   shift = key % 256
   ```
2. **Encryption**:

   ```python
   encrypted_bytes = bytes((b + shift) % 256 for b in plaintext_bytes)
   ```
3. **Decryption**:

   ```python
   decrypted_bytes = bytes((b - shift + 256) % 256 for b in ciphertext_bytes)
   ```

> **Note:**
>
> * All bytes are processed, so non-ASCII characters and binary data can be sent (UTF-8 encoding is used).
> * Decryption with the wrong key produces garbled text.

---

## File Overview

* `server.py`: TCP server implementation.
* `streamlit_app.py`: Streamlit client UI and encryption logic.

---
