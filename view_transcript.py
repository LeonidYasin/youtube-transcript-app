import sys

def print_hebrew_sample(filename='transcript.txt', num_lines=5):
    """Print the first few lines of the transcript with proper encoding."""
    try:
        # Set the console to use UTF-8 encoding
        sys.stdout.reconfigure(encoding='utf-8')
        
        with open(filename, 'r', encoding='utf-8') as f:
            print("=== Первые строки транскрипта на иврите ===\n")
            for i, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Only print non-empty lines
                    print(f"{i}. {line}")
                    if i >= num_lines:
                        break
                        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print_hebrew_sample()
