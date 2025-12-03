import json
import os
import sys

# Determine the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the name of the file where data will be stored (absolute path)
DATA_FILE = os.path.join(SCRIPT_DIR, 'List.json')

# Define the allowed categories for tracking series
CATEGORIES = ['Manga', 'Manhwa', 'Manhua', 'Other']

def load_series_data(filepath=DATA_FILE):
    """
    Loads series tracking data from a JSON file.
    If the file does not exist, returns an empty dictionary.
    """
    if not os.path.exists(filepath):
        # Only print the "not found" message once on startup
        if os.path.basename(sys.argv[0]) in sys.argv[0]:
            print(f"[{filepath}] not found. Starting a new tracker.")
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        print(f"[ERROR] Error reading JSON from [{filepath}]. The file might be corrupted. Returning empty data.")
        return {}
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while loading data: {e}")
        return {}

def save_series_data(data, filepath=DATA_FILE):
    """
    Saves the series tracking data (a dictionary) to a JSON file.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Use indent=4 for human-readable formatting
            json.dump(data, f, indent=4, ensure_ascii=False)
        # We suppress the "Data successfully saved" message in update_series_chapter 
        # to avoid spamming the console on every small update, but keep it here.
        # print(f"\n[INFO] Data successfully saved to [{filepath}].")
    except Exception as e:
        print(f"[ERROR] An error occurred while saving data: {e}")

def update_series_chapter(series_name, chapter_number, category, series_data, auto_save=True):
    """
    Adds a new series or updates the chapter number and category of an existing one.
    This function modifies the series_data dictionary directly.
    """
    # --- Category Validation ---
    if category not in CATEGORIES:
        print(f"[ERROR] Invalid category '{category}'. Must be one of: {', '.join(CATEGORIES)}. Update cancelled.")
        return False

    # --- Chapter Validation (Float) ---
    try:
        chapter_number = float(chapter_number)
        if chapter_number < 0:
            print("[ERROR] Chapter number cannot be negative. Update cancelled.")
            return False
    except ValueError:
        print("[ERROR] Invalid chapter number provided. It must be a number (e.g., 10 or 10.5). Update cancelled.")
        return False

    # 2. Prepare update variables and check if the series exists
    is_new = series_name not in series_data
    old_data = series_data.get(series_name, {"chapter": 0.0, "category": category})
    
    # Ensure old chapter is treated as float for comparison
    old_chapter = float(old_data.get("chapter", 0.0))
    old_category = old_data.get("category", category)
    
    # 3. Update the data using the new nested structure
    series_data[series_name] = {
        "chapter": chapter_number,
        "category": category
    }

    # 4. Save immediately to ensure data persistence
    if auto_save:
        save_series_data(series_data)
        
    # 5. Provide feedback
    if is_new:
        print(f"\nSUCCESS: Added new series '{series_name}' ({category}) at Chapter {chapter_number}.")
    else:
        # Check if the category was also updated
        category_change = ""
        if category != old_category:
            category_change = f" and category changed from '{old_category}' to '{category}'"
            
        if chapter_number > old_chapter:
            print(f"\nSUCCESS: Updated series '{series_name}'. Progressed from Chapter {old_chapter} to Chapter {chapter_number}{category_change}.")
        elif chapter_number == old_chapter and category != old_category:
             print(f"\nSUCCESS: Updated series '{series_name}'. Chapter {chapter_number} remains the same, but category changed to '{category}'.")
        elif chapter_number == old_chapter:
            print(f"\nNOTE: Series '{series_name}' chapter remains at Chapter {chapter_number}. No change made.")
        else: # chapter_number < old_chapter (e.g., correcting an error)
            print(f"\nSUCCESS: Corrected chapter for '{series_name}' from Chapter {old_chapter} to Chapter {chapter_number}{category_change}.")
            
    return True

def view_all_series(data):
    """
    Prints all tracked series and their current chapters, including the category.
    The list is sorted alphabetically by series name.
    """
    if not data:
        print("\nSeries Tracker is currently empty.")
        return

    print("\n--- Current Series Tracker Status (Sorted A-Z) ---")
    # Sort series alphabetically by name
    for series, info in sorted(data.items()):
        # Retrieve chapter and ensure it displays nicely
        chapter = info.get("chapter", 0)
        category = info.get("category", "Uncategorized")
        
        # Use ljust for clean alignment
        print(f"[{category.ljust(6)}] {series.ljust(30)} | Chapter {chapter}")
    print("--------------------------------------------------\n")


def handle_add_series(data):
    """
    Handles the full flow for adding a new series.
    Displays the list automatically on success.
    """
    print("\n--- Add New Series ---")
    
    # 1. Input Category (first selection)
    print(f"Available Categories: {', '.join(CATEGORIES)}")
    category = input("Enter Category: ").strip()

    # 2. Input Series Name
    series_name = input("Enter Series Name: ").strip()
    if not series_name:
        print("[NOTE] Series name cannot be empty.")
        return False

    # 3. Input Chapter (Float accepted)
    chapter_number = input("Enter Current Chapter (e.g. 12 or 12.5): ").strip()
    
    # Use the core function
    if update_series_chapter(series_name, chapter_number, category, data):
        # Automatically display the updated list
        view_all_series(data)
        return True
    return False


def handle_update_chapter(data):
    """
    Handles the flow for updating chapter progress for an existing series.
    Displays the list automatically on success.
    """
    print("\n--- Quick Chapter Update ---")
    series_name = input("Enter Series Name to Update: ").strip()
    
    if series_name not in data:
        print(f"[ERROR] Series '{series_name}' not found in tracker.")
        print("Please use option 1 ('Add/Update Series') to track it first, or check your spelling.")
        return False
        
    # Get existing category to pass to the update function
    existing_category = data[series_name]["category"]
    
    # Input Chapter
    chapter_number = input(f"Enter New Chapter Number (Current: {data[series_name]['chapter']}): ").strip()

    # Use the core function (the category remains the existing one)
    if update_series_chapter(series_name, chapter_number, existing_category, data):
        # Automatically display the updated list
        view_all_series(data)
        return True
    return False

# --- NEW FUNCTION FOR FINDING AND OPTIONALLY UPDATING A SERIES ---
def handle_find_series(data):
    """
    Allows the user to find a series, view its status, and choose to update it.
    Supports partial matching and requires explicit selection.
    """
    print("\n--- Find Series and Check Status ---")
    search_term = input("Enter Series Name (or part of the name): ").strip()

    if not search_term:
        print("[NOTE] Search term cannot be empty.")
        return

    # Normalize the search term to lowercase for case-insensitive matching
    search_term_lower = search_term.lower()
    
    # Find all series that contain the search term
    matching_series = []
    for series_name in sorted(data.keys()):
        if search_term_lower in series_name.lower():
            matching_series.append(series_name)
    
    if not matching_series:
        print(f"\n[INFO] No series found matching '{search_term}'.")
        return

    # --- Multiple Matches Found: List options and prompt for selection ---
    print(f"\nFound {len(matching_series)} matching series:")
    for i, name in enumerate(matching_series):
        print(f"  {i+1}: {name}")
    
    # Loop to ensure a valid choice is made
    while True:
        selection_input = input("\nEnter the NUMBER of the series to view, or press ENTER to return to the main menu: ").strip()
        
        if not selection_input:
            print("\nReturning to main menu.")
            return

        try:
            selection_index = int(selection_input) - 1
            if 0 <= selection_index < len(matching_series):
                series_name = matching_series[selection_index]
                break # Valid selection made, exit the loop
            else:
                print(f"[ERROR] Invalid number. Please enter a number between 1 and {len(matching_series)}.")
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number or press ENTER.")


    # --- Exact Series Selected: Display status and prompt for update ---
    series_info = data[series_name]
    current_chapter = series_info.get("chapter", 0.0)
    current_category = series_info.get("category", "Uncategorized")
    
    print("\n--- Series Status ---")
    print(f"Selected: {series_name}")
    print(f"Category: {current_category}")
    print(f"Current Chapter: {current_chapter}")
    print("---------------------")

    # Ask if the user wants to update
    update_choice = input("Do you want to update the chapter? (y/N): ").strip().lower()

    if update_choice == 'y':
        new_chapter_str = input("Enter New Chapter Number: ").strip()
        
        # Use the core update function with the current category
        if update_series_chapter(series_name, new_chapter_str, current_category, data):
            print(f"\nSeries '{series_name}' chapter updated successfully.")
    
    print("\nReturning to main menu.")
        
def main_menu():
    """Presents the main menu and handles user choices."""
    series_data = load_series_data()
    
    while True:
        print("\n===============================")
        print(" Series Tracker Command Menu ")
        print("===============================")
        print("1. Add/Update Series (requires Category)")
        print("2. Quick Chapter Update (existing Series)")
        print("3. View All Tracked Series")
        print("4. Find & Check Status of a Series")
        print("5. Exit and Save") # Option changed from 4 to 5
        print("===============================")
        
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            handle_add_series(series_data)
        elif choice == '2':
            handle_update_chapter(series_data)
        elif choice == '3':
            view_all_series(series_data)
        elif choice == '4':
            handle_find_series(series_data)
        elif choice == '5': # Option changed from 4 to 5
            print("\nExiting tracker. Saving final data...")
            # We call save here one last time in case the update function was modified 
            # to not save automatically, ensuring exit persistence.
            save_series_data(series_data)
            sys.exit(0)
        else:
            print("\n[WARNING] Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main_menu()
