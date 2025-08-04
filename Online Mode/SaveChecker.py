import os
import json
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# ---- CONFIG ----
AES_KEY = b"0123456789abcdef0123456789abcdef" # 32 bytes for AES-256
HMAC_SECRET = b"MySuperSecretHMACKey"            # Secret for tamper check
SAVE_FILE_PATH = os.path.join("Saves", "save.bin")

# ---- HELPERS ----
def pad(data):
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt(data_bytes):
    iv = get_random_bytes(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data_bytes))
    return iv + encrypted  # Prepend IV

def decrypt(encrypted_bytes):
    iv = encrypted_bytes[:16]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_bytes[16:])
    return unpad(decrypted)

def compute_hmac(data):
    return hmac.new(HMAC_SECRET, data, hashlib.sha256).digest()

# ---- SAVE/LOAD ----
def encode_save_file(save_data=None):
    if not save_data:
        save_data = {
            'enchanter': False,
            'monarch': False,
            'madman': False,
            'tutorial': False,
            'beat_enchanter_first_time': False
        }

    # Serialize to JSON
    json_data = json.dumps(save_data).encode('utf-8')

    # Encrypt it
    encrypted = encrypt(json_data)

    # HMAC the encrypted blob
    hmac_value = compute_hmac(encrypted)

    # Final data = encrypted + hmac
    final_data = encrypted + hmac_value

    # Save to file
    os.makedirs(os.path.dirname(SAVE_FILE_PATH), exist_ok=True)
    with open(SAVE_FILE_PATH, 'wb') as f:
        f.write(final_data)

def decode_save_file():
    try:
        with open(SAVE_FILE_PATH, 'rb') as f:
            content = f.read()

        encrypted_data = content[:-32]
        stored_hmac = content[-32:]

        # Check HMAC
        if compute_hmac(encrypted_data) != stored_hmac:
            raise ValueError("Save file has been tampered with or corrupted.")

        decrypted_json = decrypt(encrypted_data)
        save_data = json.loads(decrypted_json.decode('utf-8'))

        return save_data

    except FileNotFoundError:
        print("Save file not found.")
        return None
    except Exception as e:
        print("Failed to load save:", str(e))
        return None

# ---- DEMO ----
if __name__ == "__main__":
    loaded = decode_save_file()
    print("Loaded:", loaded)
