import os
import pandas as pd
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_aes_key(key_length: int = 16) -> bytes:
    """
    Generates a random AES key of specified length (in bytes).
    Default: 16 bytes = 128-bit key.
    """
    return os.urandom(key_length)

def encrypt_value_gcm(plain_text: str, key: bytes) -> (str, str):
    """
    Encrypt a single value using AES-GCM.
    
    Returns:
      (ciphertext_base64, nonce_base64)
    
    The ciphertext and nonce are returned as Base64-encoded strings. 
    We must store both the nonce and ciphertext to decrypt later.
    """
    if plain_text is None:
        return None, None

    aesgcm = AESGCM(key)
    nonce = os.urandom(16)
    
    plain_bytes = plain_text.encode('utf-8')
    # Encrypt
    ciphertext = aesgcm.encrypt(nonce, plain_bytes, associated_data=None)
    
    return base64.b64encode(ciphertext).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')

def decrypt_value_gcm(encrypted_text: str, nonce_b64: str, key: bytes) -> str:
    """
    Decrypt a single value using AES-GCM given the ciphertext, nonce, and key.
    """
    if encrypted_text is None or nonce_b64 is None:
        return None
    
    aesgcm = AESGCM(key)
    ciphertext = base64.b64decode(encrypted_text)
    nonce = base64.b64decode(nonce_b64)
    
    decrypted_data = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return decrypted_data.decode('utf-8')

def encrypt_columns_gcm(df: pd.DataFrame, id_col: str, columns_to_encrypt: list) -> (pd.DataFrame, pd.DataFrame):
    """
    Given a DataFrame, an ID column, and a list of columns to encrypt with AES-GCM:
    - Generate a unique key for each (id, column) pair.
    - Encrypt each specified column value per ID.
    - Return:
      encrypted_df: DataFrame with encrypted columns (ciphertexts),
      keys_df: DataFrame with keys and nonces needed for decryption.
    """
    # Get unique IDs
    unique_ids = df[id_col].unique()
    
    # Prepare data structures for keys
    keys_data = {id_col: [], 'column_name': [], 'encrypt_key': [], 'nonce': []}
    
    # We'll store encrypted values in the main DF directly
    encrypted_df = df.copy()
    
    # For each column, we will need to store per-row nonce and ciphertext, but the key
    # can be reused per (id, column) pair. However, GCM mode requires a unique nonce per encryption.
    # We can approach this by assigning a unique key per (id, column), and a unique nonce per row.
    # This is not typical because one usually reuses a key for multiple values but changes nonce for each value.
    # For simplicity, let's generate a single key per (id, column) and a new nonce per row.
    # That means each encrypted value will have its own nonce stored.
    
    # Create structures to hold encrypted column data and nonces for each row.
    # We'll keep nonce for each row in a separate DataFrame or in a nested structure.
    # Instead, we can store them temporarily and then merge back.
    nonce_store = {col: [] for col in columns_to_encrypt}
    
    # Mapping from (id, column) -> key
    key_map = {}
    
    # Generate keys for each (id, column) pair
    for uid in unique_ids:
        for col in columns_to_encrypt:
            key = generate_aes_key()
            # Store it in a map
            key_map[(uid, col)] = key

    # Encrypt data
    # For each row and column, encrypt using the corresponding key and a fresh nonce
    for col in columns_to_encrypt:
        # We'll store nonces here temporarily
        row_nonces = []
        encrypted_col_data = []
        for _, row in encrypted_df.iterrows():
            uid = row[id_col]
            key = key_map[(uid, col)]
            ciphertext_b64, nonce_b64 = encrypt_value_gcm(row[col], key)
            encrypted_col_data.append(ciphertext_b64)
            row_nonces.append(nonce_b64)
        
        encrypted_df[col] = encrypted_col_data
        nonce_store[col] = row_nonces

    # Flatten the nonce data into a keys DataFrame with a row per (id, column, row)
    # But note that this will produce multiple nonces per id+column pair since each row has its own nonce.
    # Instead, let's store keys and nonces in a wide format: one entry per row, 
    # with separate nonce columns for each encrypted column.
    
    # Build keys_df with one row per original row, containing keys and nonces for all encrypted columns
    all_keys_records = []
    for i, row in encrypted_df.iterrows():
        record = {id_col: row[id_col]}
        # For each column, get the key and the nonce
        uid = row[id_col]
        for col in columns_to_encrypt:
            key = key_map[(uid, col)]
            nonce_b64 = nonce_store[col][i]
            record[f'{col}_key'] = base64.b64encode(key).decode('utf-8')
            record[f'{col}_nonce'] = nonce_b64
        all_keys_records.append(record)

    keys_df = pd.DataFrame(all_keys_records)

    return encrypted_df, keys_df

# Example main function using JSON input
def main(file_path_raw_data, id_col, columns_to_encrypt, output_path_encrypted_data, output_path_keys):
    
    # Read the JSON file into a DataFrame
    df = pd.read_json(file_path_raw_data)
    # Encrypt columns with GCM
    encrypted_df, keys_df = encrypt_columns_gcm(df, id_col=id_col, columns_to_encrypt=columns_to_encrypt)
    
    # Store the results
    encrypted_df.to_csv(output_path_encrypted_data, index=False)
    keys_df.to_csv(output_path_keys, index=False)

    print("Encryption complete. 'encrypted_data.csv' and 'encryption_keys.csv' created.")

if __name__ == "__main__":
    pass