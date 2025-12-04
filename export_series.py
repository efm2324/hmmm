import json
import os
import sys

# Define file paths. Assumes List.json is in the same directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, 'List.json')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'Lecture_out.md')

# Define the category order to match the series tracker
CATEGORIES = ['Manga', 'Manhwa', 'Manhua', 'Other']

def load_json_data(filepath):
    """Loads series data from the List.json file."""
    if not os.path.exists(filepath):
        print(f"[ERROR] Input file '{filepath}' not found. Please ensure List.json exists.")
        sys.exit(1)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[ERROR] Could not decode JSON from '{filepath}'. File may be corrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while loading data: {e}")
        sys.exit(1)

def format_data_to_text(data):
    """
    Formats the series dictionary into a categorized, sorted markdown/text string.
    """
    if not data:
        return "Lecture:\n\n--------------------------------------------\n\n[No series tracked]"

    # 1. Start with the main header and separator, matching the original file structure
    output_lines = [
        "Lecture:",
        "",
        "",
        "",
        "--------------------------------------------",
        "",
        ""
    ]

    # 2. Group and sort data by category
    grouped_data = {cat: {} for cat in CATEGORIES}
    
    for series_name, info in data.items():
        # Use 'Other' as a fallback if the category is missing or invalid
        category = info.get("category", "Other")
        if category not in CATEGORIES:
            category = "Other"
            
        grouped_data[category][series_name] = info

    # 3. Iterate through categories in the defined order
    for category_name in CATEGORIES:
        series_in_category = grouped_data[category_name]
        
        if series_in_category:
            # Add category header
            output_lines.append(f"{category_name} :")
            output_lines.append("")
            output_lines.append("")
            output_lines.append("")
            
            # Add sorted series entries
            # Sort by series name alphabetically (case-insensitive)
            for series, info in sorted(series_in_category.items(), key=lambda item: item[0].lower()):
                chapter = info.get("chapter", 0.0)
                # Format the output line: Series Name- ep: ChapterNumber
                output_lines.append(f"{series}- ep: {chapter}")
                output_lines.append("")
                output_lines.append("")
                output_lines.append("")
                
            # Add separator after each category block (if not the last block)
            # This logic mimics the spacing seen in your Lecture.txt
            output_lines.append("--------------------------------------------")
            output_lines.append("")
            output_lines.append("")
            output_lines.append("")

    # Remove extra blank lines at the very end
    while output_lines and output_lines[-1] == "":
        output_lines.pop()

    # The last separator should be removed if it's the very end of the file
    if output_lines and output_lines[-1] == "--------------------------------------------":
         output_lines.pop()


    return "\n".join(output_lines)

def main():
    """Main function to run the export process."""
    print(f"Attempting to load data from: {INPUT_FILE}")
    series_data = load_json_data(INPUT_FILE)
    
    # Generate the text content
    text_content = format_data_to_text(series_data)
    
    # Write the content to the output file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"\nSUCCESS: Successfully exported {len(series_data)} series to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n[ERROR] An error occurred while writing to file: {e}")

if __name__ == "__main__":
    main()
