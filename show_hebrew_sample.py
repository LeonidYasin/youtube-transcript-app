def show_sample(filename='transcript.txt', num_lines=5):
    """Display the first few lines of the transcript."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()][:num_lines]
            
        print("=== Первые строки транскрипта на иврите ===")
        for i, line in enumerate(lines, 1):
            print(f"{i}. {line}")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    show_sample()
