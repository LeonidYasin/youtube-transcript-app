def read_file_with_encoding(file_path, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    file_path = 'transcript_text.txt'
    print(f"Reading {file_path} with UTF-8 encoding:")
    print("-" * 80)
    print(read_file_with_encoding(file_path, 'utf-8')[:1000])
