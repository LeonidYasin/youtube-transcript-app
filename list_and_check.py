import os
import glob

def list_files():
    print("Files in directory:")
    for file in os.listdir('.'):
        if 'qp0HIF3SfI4' in file or '.vtt' in file:
            print(f"- {file}")
    
    # Try to find the VTT file
    vtt_files = glob.glob('*.vtt')
    if vtt_files:
        print("\nFound VTT files:")
        for vtt in vtt_files:
            print(f"- {vtt}")
            
            # Try to read the file
            try:
                with open(vtt, 'rb') as f:
                    content = f.read(500)  # Read first 500 bytes
                    print("\nFirst 100 bytes as hex:")
                    print(' '.join(f'{b:02x}' for b in content[:100]))
                    
                    print("\nTrying different encodings:")
                    for encoding in ['utf-8', 'utf-16', 'windows-1251', 'cp1251', 'latin1']:
                        try:
                            decoded = content.decode(encoding)
                            print(f"\n--- {encoding} ---")
                            print(decoded[:200] + '...')
                        except Exception as e:
                            print(f"\n--- {encoding} ---")
                            print(f"Error: {str(e)[:100]}...")
                            
            except Exception as e:
                print(f"Error reading file: {str(e)}")
    else:
        print("No VTT files found")

if __name__ == "__main__":
    list_files()
