import os
import re

def convert_vtt_to_txt(vtt_file, output_file=None):
    """
    Convert a VTT subtitle file to a clean text file.
    
    Args:
        vtt_file (str): Path to the input VTT file
        output_file (str, optional): Path to the output text file. 
                                   If not provided, will use the same name as input with .txt extension.
    """
    # Set default output filename if not provided
    if not output_file:
        base_name = os.path.splitext(vtt_file)[0]
        output_file = f"{base_name}.txt"
    
    try:
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove VTT header and metadata
        content = re.sub(r'^.*?\n\n', '', content, flags=re.DOTALL)
        
        # Remove timestamps and other VTT formatting
        lines = []
        for line in content.split('\n'):
            # Skip empty lines and timestamp lines
            if not line.strip() or '-->' in line:
                continue
            # Remove any remaining VTT formatting
            line = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
            line = line.strip()
            if line:
                lines.append(line)
        
        # Join lines into paragraphs where appropriate
        text = '\n'.join(lines)
        
        # Save to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Successfully converted {vtt_file} to {output_file}")
        return text
        
    except Exception as e:
        print(f"Error processing {vtt_file}: {str(e)}")
        return None

def process_subtitles():
    """Process all VTT files in the subtitles directory"""
    subtitles_dir = os.path.join(os.path.dirname(__file__), 'subtitles')
    output_dir = os.path.join(os.path.dirname(__file__), 'text_transcripts')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all VTT files
    vtt_files = [f for f in os.listdir(subtitles_dir) if f.endswith('.vtt')]
    
    if not vtt_files:
        print("No VTT files found in the subtitles directory.")
        return
    
    print(f"Found {len(vtt_files)} VTT file(s) to process:")
    
    for vtt_file in vtt_files:
        input_path = os.path.join(subtitles_dir, vtt_file)
        output_file = os.path.join(output_dir, os.path.splitext(vtt_file)[0] + '.txt')
        
        print(f"\nProcessing: {vtt_file}")
        convert_vtt_to_txt(input_path, output_file)

if __name__ == "__main__":
    process_subtitles()
