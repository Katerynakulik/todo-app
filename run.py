# -*- coding: utf-8 -*-
import gspread
from google.oauth2.service_account import Credentials
import sys

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

try: 
    # Authorization using the creds.json file
    CREDS = Credentials.from_service_account_file('creds.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('to_do_list')
    
    tasks = SHEET.worksheet('tasks')
except FileNotFoundError:
    print("❌ ERROR: 'creds.json' not found. Ensure the file is in the project root.")
    sys.exit()
except Exception as e:
    print(f"❌ ERROR connecting to Google Sheets: {e}")
    sys.exit()

# --- GLOBAL DATA ---
# This will store the list of dictionaries derived from the sheet
TASK_DATA = [] 
HEADERS = [] # To store ['id', 'task', 'priority', 'done']

# --- DATA CONVERSION ---

def load_data_from_sheet():
    """Loads all data from the sheet and converts it into a list of dictionaries."""
    global TASK_DATA, HEADERS
    
    try:
        # 1. Fetch all values (list of lists)
        all_values = tasks.get_all_values()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return False
        
    if not all_values:
        return True # Empty sheet is valid
        
    # The first row is the header
    HEADERS = all_values[0]
    
    # 2. Convert data rows into list of dictionaries
    TASK_DATA = []
    
    for row in all_values[1:]:
        if len(row) != len(HEADERS):
            continue # Skip incomplete rows
            
        try:
            task_dict = {
                # Convert 'id' and 'priority' to integers
                HEADERS[0]: int(row[0]), 
                HEADERS[1]: row[1],
                HEADERS[2]: int(row[2]),
                # Convert 'done' (expected as '0' or '1') to a boolean
                HEADERS[3]: int(row[3]) == 1 
            }
            TASK_DATA.append(task_dict)
        except ValueError:
            # Skip rows where ID, Priority, or Done status is not a valid number
            print(f"Warning: Skipping row with invalid numeric data: {row}")
            continue

    print(f"✅ Data loaded successfully. Total tasks: {len(TASK_DATA)}")
    return True

def display_tasks():
    """Reads and displays all current tasks in a user-friendly format."""
    
    if not TASK_DATA:
        print("\n--- To-Do List is Empty! ---")
        return

    print("\n--- Current To-Do List ---")
    print("-" * 55)
    print(f"| {'ID':<3} | {'PRIORITY':<8} | {'STATUS':<6} | {'TASK DESCRIPTION':<25} |")
    print("-" * 55)
    
    # Sort by done status (False/Pending first) and then by priority (1 is highest)
    sorted_tasks = sorted(TASK_DATA, key=lambda x: (x['done'], x['priority']))
    
    for task in sorted_tasks:
        status = "✅ DONE" if task['done'] else "⬜ PEND"
        # Displaying 'priority' as text for better readability
        priority_text = {1: 'HIGH', 2: 'MEDIUM', 3: 'LOW'}.get(task['priority'], 'N/A')
        print(f"| {task['id']:<3} | {priority_text:<8} | {status:<6} | {task['task']:<25} |")
    print("-" * 55)

def get_new_task_details():
    """Prompts the user for a new task's description and priority."""
    
    # 1. Get Task Description
    task_description = input("Enter task description: ").strip()
    while not task_description:
        print("Task description cannot be empty.")
        task_description = input("Enter task description: ").strip()

    # 2. Get Task Priority
    while True:
        try:
            priority_input = input("Enter priority (1=HIGH, 2=MEDIUM, 3=LOW): ").strip()
            priority = int(priority_input)
            if 1 <= priority <= 3:
                break
            else:
                print("Priority must be 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number (1, 2, or 3).")
            
    return task_description, priority


def create_task():
    """
    Handles the creation of a new task, assigns a unique ID, and updates the Sheet.
    """
    global TASK_DATA
    
    task_description, priority = get_new_task_details()

    # 1. Determine the New ID
    new_id = max(t['id'] for t in TASK_DATA) + 1 if TASK_DATA else 1

    # 2. Prepare the new row for Google Sheet (must be a list of strings)
    new_task_row = [str(new_id), task_description, str(priority), '0']

    # 3. Append the new row to Google Sheet
    try:
        # Appending a row to the end of the sheet
        tasks.append_row(new_task_row)
        print(f"\n✅ SUCCESS: Task ID {new_id} ('{task_description}') created and added to Google Sheet.")
        
        # 4. Update local data (TASK_DATA) immediately without reloading the whole sheet
        new_task_dict = {
            'id': new_id, 
            'task': task_description, 
            'priority': priority, 
            'done': False # False corresponds to '0'
        }
        TASK_DATA.append(new_task_dict)
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to add task to Google Sheet. {e}")

def get_task_by_id(task_id):
    """
    Searches the local TASK_DATA list for a task with the given ID.
    """
    try:
        task_id = int(task_id)
    except ValueError:
        return None
        
    for task in TASK_DATA:
        if task['id'] == task_id:
            return task
    return None

def initial_prompt():
    """
    Asks the user whether they want to add a new task or view the list.
    """
    
    while True:
        choice = input("\nDo you want to add a new task? (y/n): ").lower().strip()
        
        if choice == 'y':
            create_task() 
            display_tasks() 
            break
            
        elif choice == 'n':
            # Display tasks, then ask about status change
            display_tasks()
            
            # Logic to ask about changing task status
            change_status = input("\nDo you want to change the status of a task (mark as done/pending)? (y/n): ").lower().strip()
            
            if change_status == 'y':
                # Redirect to status change logic (to be implemented next)
                print("\n--- Changing Task Status ---")
                # We'll call the update_status() function here later
                print("Status update function will be called here.")
                break # Exit loop after handling 'y'
            elif change_status == 'n':
                print("Returning to application exit point.")
                break # Exit and let the main flow conclude
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                continue # Re-ask about status change
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


# --- APPLICATION START ---
if __name__ == "__main__":
    print("Welcome to the To-Do List Manager!")
    
    # Attempt to load data at the start
    if load_data_from_sheet():
        initial_prompt() 
    
    print("Application finished.")
    sys.exit()