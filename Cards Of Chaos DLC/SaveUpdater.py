import os
import json
import hmac
import hashlib
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
except ImportError:
    try:
        os.system("pip install -r requirements.txt") if os.name == "nt" else os.system(
            "pip3 install -r requirements.txt")
    except Exception as e:
        pass
        # print(f"Failed to install dependencies: {e}")
# ---- CONFIG ----
AES_KEY = b"0123456789abcdef0123456789abcdef"  # 32 bytes for AES-256
HMAC_SECRET = b"MySuperSecretHMACKey"            # Secret for tamper check
SAVE_FILE_PATH = os.path.join("Saves", "save.bin")

# ---- HELPERS ----


def pad(data):
    """
    Pad the data to be a multiple of 16 bytes using PKCS#7 padding.
    """
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)


def unpad(data):
    """
    Remove PKCS#7 padding from the data.
    """
    pad_len = data[-1]
    return data[:-pad_len]


def encrypt(data_bytes):
    """
    Encrypt the data using AES in CBC mode with a random IV.
    The IV is prepended to the encrypted data.
    """
    iv = get_random_bytes(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data_bytes))
    return iv + encrypted  # Prepend IV


def decrypt(encrypted_bytes):
    """
    Decrypt the data using AES in CBC mode.
    The IV is extracted from the first 16 bytes of the encrypted data.
    """
    iv = encrypted_bytes[:16]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_bytes[16:])
    return unpad(decrypted)


def compute_hmac(data):
    """
    Compute the HMAC of the data using SHA-256.
    """
    return hmac.new(HMAC_SECRET, data, hashlib.sha256).digest()

# ---- SAVE/LOAD ----


def encode_save_file(save_data=None):
    """
    Save the game state to a file, encrypting and HMACing the data.
    If no data is provided, a default state of false is used.
    """

    if not save_data:
        with open("version.txt", 'r') as f:
            version = f.read().strip()
        save_data = {
                'enchanter': False,
                'monarch': False,
                'madman': False,
                'tutorial': False,
                'beat_enchanter_first_time': False,
                'music': True,
                'hScore': 0,
                'GameVersion': version,
                'modded': (False if os.getcwd().split('\\')[-1] == 'base' else True),
            }

    save_data['modded'] = False if os.getcwd().split(
        '\\')[-1] == 'base' else True

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
    """
    Load and decrypt the save file, checking for tampering using HMAC.
    Returns the decoded save data as a dictionary, or None if loading fails.
    """

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

if __name__ == "__main__" and os.path.dirname(__file__) == os.getcwd():
    with open("version.txt", 'r') as f:
        version = f.read().strip()
    data = {
        'enchanter': False,
        'monarch': False,
        'madman': False,
        'tutorial': False,
        'beat_enchanter_first_time': False,
        'music': True,
        'hScore': 0,
        'GameVersion': version,
        'modded': (False if os.getcwd().split('\\')[-1] == 'base' else True),
    }
    encode_save_file(data)
    print("Saved:", data)
    loaded = decode_save_file()
    print("Loaded:", loaded)
elif __name__ == "__main__":
    print("This script is not meant to be run directly from the general directory.")
    print("Please run it from the base directory of the project.")
