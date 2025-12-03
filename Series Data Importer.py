import json
import os
import re
import sys

# --- Configuration ---
# The name of the input file to read the series data from.
INPUT_FILE = 'Lecture.md'
# The name of the output JSON file compatible with series_tracker.py.
OUTPUT_FILE = 'List.json'

# Regex to capture the series name and chapter number from a line:
# Example: "Series Name- ep: 12.5" -> Group 1: "Series Name", Group 2: "12.5"
SERIES_LINE_PATTERN = re.compile(r"^(.+?)\s*-\s*ep:\s*([\d\.]+)$")

def load_text_data(filepath):
    """Loads the content of the input text file (Lecture.md)."""
    if not os.path.exists(filepath):
        print(f"[ERROR] Input file '{filepath}' not found. Please ensure it is in the same directory.")
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read input file: {e}")
        sys.exit(1)

def save_json_data(data, filepath):
    """Saves the parsed data dictionary to the output JSON file (List.json)."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Using indent=4 makes the file readable and debuggable
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n[SUCCESS] Data successfully parsed and saved to '{filepath}'.")
    except Exception as e:
        print(f"[ERROR] Failed to save JSON data: {e}")

def parse_series_data(text_content):
    """
    Parses the text content line by line to build the JSON structure.
    """
    series_data = {}
    current_category = "Other" # Default category
    lines = text_content.strip().split('\n')
    
    print(f"[INFO] Starting data parsing from {INPUT_FILE}...")

    for line in lines:
        line = line.strip()
        if not line or '-----' in line:
            continue
            
        # 1. Check for Category Header (e.g., "Manga :")
        # Matches lines that end with a colon and might contain category names
        if line.endswith(':'):
            # Clean up the category name (e.g., 'Manga :' -> 'Manga')
            category_name = line.split(':')[0].strip()
            
            # Capitalize and validate against the CATEGORIES list in the tracker file
            if category_name in ['Manga', 'Manhwa', 'Manhua', 'Other']:
                current_category = category_name
                print(f"\n--- Found Category: {current_category} ---")
            continue
            
        # 2. Check for Series Entry
        match = SERIES_LINE_PATTERN.match(line)
        if match:
            series_name = match.group(1).strip()
            chapter_str = match.group(2).strip()
            
            # Validate and convert chapter number to float
            try:
                chapter_number = float(chapter_str)
            except ValueError:
                print(f"[WARNING] Skipping invalid chapter for '{series_name}': '{chapter_str}'")
                continue
                
            # Store data in the required format
            series_data[series_name] = {
                "chapter": chapter_number,
                "category": current_category
            }
            # print(f"  Parsed: {series_name} (Ch {chapter_number})") # Uncomment for detailed output

    return series_data

def main():
    """Main execution function for the importer script."""
    # 1. Load the raw text data
    raw_content = load_text_data(INPUT_FILE)
    
    # 2. Parse the data into a dictionary
    output_dict = parse_series_data(raw_content)
    
    # 3. Save the dictionary as JSON
    save_json_data(output_dict, OUTPUT_FILE)
    
    print(f"\n[SUMMARY] Total series successfully imported: {len(output_dict)}.")
    print("You can now run 'series_tracker.py' to use this data.")

if __name__ == "__main__":
    main()
