import os

def check_file_encoding(file_path):
    # List of encodings to try
    encodings = ['utf-8', 'utf-16', 'windows-1251', 'cp1251', 'latin1', 'iso-8859-1']
    
    print(f"Checking file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    print("\nTrying different encodings:")
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read(500)  # Read first 500 characters
                print(f"\n--- {encoding} ---")
                print(content)
                print(f"Read {len(content)} characters")
        except Exception as e:
            print(f"\n--- {encoding} ---")
            print(f"Error: {str(e)[:100]}...")  # Print first 100 chars of error
    
    # Try reading as binary
    try:
        with open(file_path, 'rb') as f:
            binary_data = f.read(100)  # Read first 100 bytes
            print("\n--- Binary (first 100 bytes) ---")
            print(binary_data)
    except Exception as e:
        print(f"Error reading binary: {str(e)}")

if __name__ == "__main__":
    file_name = "How Great Leaders Inspire Action  Simon Sinek  TED [qp0HIF3SfI4].ru.vtt"
    check_file_encoding(file_name)
