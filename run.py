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
        all_values = TASKS_SHEET.get_all_values()
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