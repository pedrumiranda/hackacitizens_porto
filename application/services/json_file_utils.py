import json
import os


def save_to_file(data, file_path):
    """
    Save JSON data to a specific file path.

    Parameters:
        data (dict or list): The data to be saved (must be JSON serializable).
        file_path (str): The path where the JSON file will be saved.

    Returns:
        None
    """
    try:
        # Ensure the directory exists
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)  # Create directories if they do not exist
        
        # Save data to the file
        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4,ensure_ascii=False)
        
        print(f"Saved {len(data)} entries to {file_path}")
    
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

# Function to handle JSON files with possible extra data or multiple objects
def load_json_files(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            # Attempt to load as a single JSON object
            return json.load(file)
        except json.JSONDecodeError:
            # If it fails, try reading line by line for multi-JSON-object files
            file.seek(0)  # Reset file pointer
            return [json.loads(line) for line in file if line.strip()]  # Parse 