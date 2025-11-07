# To-Do List Manager (Google Sheets CLI)

This project is a Command-Line Interface (CLI) application developed in Python that acts as a To-Do List manager. It uses the **Google Sheets API** as its primary database, allowing users to perform full CRUD operations (Create, Read, Update Status, Delete) on their tasks.

## 💻 Application Logic and Data Flow

The To-Do List Manager operates through a continuous loop in the command line, providing users with a real-time interface to manipulate cloud-based data.

### 1. Initialization and Data Load

- Authorization: The application first establishes a secure connection to Google Sheets using credentials from the local creds.json file.
- Data Fetch: It opens the designated spreadsheet ('to_do_list') and loads all content from the 'tasks' worksheet.
- Data Conversion: All sheet values are immediately converted into a local Python data structure: a list of dictionaries (TASK_DATA). This list serves as the application's working memory.

### 2. Main Loop and User Interaction

The application enters an interactive loop (initial_prompt) where the user can choose from the following operations:

- View Tasks (Read): The list is displayed, sorted first by done status (pending tasks first) and then by priority (High to Low).
- Add Task (Create):

  - The user provides a description and priority (1-3).
  - A new unique id is generated (maximum existing ID + 1).
  - The new task is appended to the Google Sheet (API call).
  - The new task dictionary is immediately appended to the local TASK_DATA.

- Update Status (Update):
  - The user enters a task id.
  - The task is found in the local TASK_DATA (using get_task_by_id).
  - The task's done status is toggled (True/False) locally.
  - The corresponding cell in the Google Sheet (Column D) is updated using the tasks.find() method to locate the correct row by id.
- Delete Task (Delete):
  - The user enters a task id.
  - The task's row is found in the Google Sheet using tasks.find(id, in_column=1).
  - The entire row is deleted from the Google Sheet (API call).
  - The task is removed from the local TASK_DATA list using a list comprehension filter.
