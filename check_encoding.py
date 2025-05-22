def print_file_hex(file_path, num_bytes=200):
    try:
        with open(file_path, 'rb') as f:
            bytes_data = f.read(num_bytes)
            
        print(f"First {len(bytes_data)} bytes of {file_path} in hex:")
        print("-" * 80)
        
        # Print hex values
        hex_str = ' '.join(f'{b:02x}' for b in bytes_data)
        print(hex_str)
        
        # Print ASCII representation (with dots for non-printable chars)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in bytes_data)
        print(ascii_str)
        
    except Exception as e:
        print(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    file_path = 'transcript_text.txt'
    print_file_hex(file_path)
