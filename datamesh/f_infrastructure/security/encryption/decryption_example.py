import argparse
import base64
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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

def decrypt_columns_gcm(encrypted_df: pd.DataFrame, keys_df: pd.DataFrame, id_col: str, columns_to_decrypt: list) -> pd.DataFrame:
    """
    Given an encrypted DataFrame, a keys DataFrame, and the list of columns to decrypt:
    - Merge the encrypted data with the keys data on the ID column.
    - Use the keys and nonces to decrypt the specified columns.
    - Return a new DataFrame with decrypted plaintext.
    """
    # Merge encrypted data and keys on the ID column
    merged_df = pd.merge(encrypted_df, keys_df, on=id_col)

    # Decrypt the specified columns
    for col in columns_to_decrypt:
        key_col = f'{col}_key'
        nonce_col = f'{col}_nonce'

        decrypted_values = []
        for i, row in merged_df.iterrows():
            # Retrieve key and nonce
            key = base64.b64decode(row[key_col])
            nonce_b64 = row[nonce_col]
            ciphertext_b64 = row[col]

            # Decrypt the value
            plain_text = decrypt_value_gcm(ciphertext_b64, nonce_b64, key)
            decrypted_values.append(plain_text)

        # Replace the encrypted column with the decrypted plaintext
        merged_df[col] = decrypted_values

    # Remove the key/nonce columns
    for col in columns_to_decrypt:
        del merged_df[f'{col}_key']
        del merged_df[f'{col}_nonce']

    return merged_df

def main(path_encrypted_data, path_keys_data, id_col, columns ,output_path):

    #id_col: pk 
    #columns: encrypted columns

    # Load the data
    encrypted_df = pd.read_csv(path_encrypted_data)
    keys_df = pd.read_csv(path_keys_data)

    # Decrypt the columns
    decrypted_df = decrypt_columns_gcm(
        encrypted_df=encrypted_df,
        keys_df=keys_df,
        id_col=id_col,
        columns_to_decrypt=columns
    )

    # Save the decrypted data
    decrypted_df.to_csv(output_path, index=False)
    print(f"Decryption complete. Decrypted data written to '{output_path}'.")

if __name__ == '__main__':
    pass