import pandas as pd
from argon2 import PasswordHasher
import secrets

def hash_value(value: str, ph: PasswordHasher) -> str:
    """
    Hash a given value using Argon2.
    
    Parameters
    ----------
    value : str
        The string to hash.
    ph : PasswordHasher
        An Argon2 PasswordHasher instance preconfigured with desired parameters.
    
    Returns
    -------
    str
        A hashed representation of 'value'.
    """
    # Convert the value to a string just to be sure it's hashable
    if not isinstance(value, str):
        value = str(value)
    return ph.hash(value)

def main(input_path, columns, output_path):

    df = pd.read_csv(input_path)

    # Create an Argon2 PasswordHasher instance with recommended parameters
    # You may adjust memory_cost, time_cost, and parallelism depending on performance/security needs.
    ph = PasswordHasher(
        time_cost=3,      # Number of iterations
        memory_cost=102400, # Memory usage in KiB
        parallelism=2      # Number of parallel threads
    )

    # Hash the sensitive columns. Ideally, only hash data that must remain pseudonymous.
    # Store the hash and do NOT store the original data.

    for column in columns:
        df[f'{column}_hashed'] = df[column].apply(lambda x: hash_value(x, ph))

    # Optionally drop the original columns to ensure data is not linkable
    df.drop(columns=columns, inplace=True)

    # The resulting dataframe now has hashed versions of sensitive fields.
    print(df)

    df.to_csv(output_path, index=False)

# Example usage:
if __name__ == "__main__":
    
    pass
