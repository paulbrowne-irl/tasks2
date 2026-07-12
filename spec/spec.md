# Task Management System - Specification

## Overview

A responsive Python web application that stores and organises tasks in Google Sheets. It provides a Flask web interface for viewing and refreshing task information and maintaining the task spreadsheet.

**Purpose:** Provide a central spreadsheet-backed task list that supports adding tasks, assigning categories, tracking changes, identifying completed work, and organising tasks by colour or priority.

---

## What Users Can Do

1.  **View Tasks:** Open the task-management web interface backed by the main Google Spreadsheet.
2.  **Add Tasks:** Add a task with a task name and category.
3.  **Organise Tasks:** Sort task information by colour and maintain category information.
4.  **Track Completion:** Identify completed tasks using the `z done` marker.
5.  **Track Changes:** Record the date of the latest task change in the `T Date` field.
6.  **Triage Task Sheets:** Review and organise task sheets through the task-sheet triage action.

---

## User Interface

### Layout Mockup


**Task Management**
```
┌─────────────────────────────────────────┐
│  Tasks, Content and Links               │
│                                         │
│  [ Refresh Tasks ]                      │
│                                         │
│  [ Add Task ] [ Sort by Colour ]        │
│                                         │
│  Task list and categories               │
└─────────────────────────────────────────┘
```

**Initial Menu** 
1. Refresh task information
2. Add a task
3. Sort tasks by colour
4. Triage task sheets


---

## Features

### Feature 1: Task Management

**Input:**
- **Category:** The category assigned to the task.
- **Task name:** The task description or name.

**Behavior:**
- A new task is appended to the task spreadsheet.
- The task is stored with its category and task name.
- The task spreadsheet is opened using its configured Google Spreadsheet ID.

**Output:**
- The updated task information is displayed in the web interface.

---

### Feature 2: Task Organisation

**Behavior:**
- Tasks can be sorted by colour.
- Category information is maintained using the spreadsheet's task columns.
- Completed work is identified using the `z done` sheet marker.
- The latest change date is maintained in the `T Date` field.

---

### Feature 3: Task-Sheet Triage

**Behavior:**
- The application supports a task-sheet triage action for reviewing and organising task sheets.
- The task-sheet action operates on the configured task spreadsheet.

**Output:**
- Updated task-sheet state.
- Success or error status message in the web interface.

### Feature 4: Email Processing

**Behavior:**
- The application can process configured email messages on a scheduled basis.
- Processed messages can be routed to the intended recipient and archived.

---

## Technical Architecture

### Business Components

i.  **Data Model**:
    - `Task`: Holds a category and task name.
    - `Task Sheet`: Holds the task rows and supporting task-management columns.
    - `Task Metadata`: Includes the latest-change date, completion marker, colour, and hash information where applicable.

### Core Components

1.  **User Interface**:
    - Interface: responsive browser-based web application.
    - Use Flask-rendered HTML with CSS and browser JavaScript for the frontend.
    - The frontend communicates with Flask routes over HTTP.

2.  **Task Spreadsheet Service**:
    - Language: Python.
    - Logic: Read and update Google Sheets, append tasks, and maintain task metadata.

3.  **Web Framework and Hosting**:
    - Use Flask to provide the web application and HTTP API.
    - Host the Flask application on Google Firebase.
    - Authenticate users through their Google account using Firebase Authentication.
    - The deployment must support the responsive task web interface, Google Spreadsheet access, task creation, sorting, and task-sheet triage.

6.  **Testing**:
    - Use Serenity for testing and create tests
    - Extract 3 scenarios 
    - write a script
    - 

7. **README.md**:
    - Provide a clear readme.md summarizing what the application does
    - Provide a clear readme.md file documenting how to open and use the task-management web application.
    - Provide a clear readme.md file documenting how to run the tests
    - Describe the application structure and technical archicture.
    

---

## Success Criteria

**Test 1: Refresh Tasks**
- Open the task-management web application.
- Refresh the task information.
- Verify success message.
- Verify the task information is read from the configured `Tasks` sheet.

**Test 2: Add Task**
- Enter a category and task name.
- Submit the task.
- **Result:** The task is appended to the task spreadsheet.

**Test 3: Sort Tasks**
- Request sorting by colour.
- **Result:** Tasks are organised in colour order.

**Test 4: Task-Sheet Triage**
- Run the task-sheet triage action.
- **Result:** Task sheets are reviewed and organised.

---

## API & Data

**Output Data:**
- Tasks stored in the configured Google Spreadsheet.
- The main spreadsheet contains a `Tasks` sheet.
- The spreadsheet also supports a `z done` completion marker and a `T Date` latest-change field.
- Task rows include category, task name, latest-change metadata, and supporting hash information where applicable.

**Task Data Format:**
- The implementation must use the configured spreadsheet columns and preserve the task data needed for adding, sorting, completion tracking, and task-sheet triage.

---

## Technical Requirements

**Language:** Python.
**Web Framework:** Flask.
**Build System:** Python package management using `requirements.txt`.
**Dependencies:**
- Flask and a production WSGI server.
- Google Sheets API client for reading and writing spreadsheet data.
- Firebase Authentication integration for Google-account sign-in.

**Environment:** Responsive web browser application hosted on Google Firebase.
**Responsive Design:** The web interface must adapt for mobile and desktop browsers.
**Accessibility:** The interface must provide basic accessibility, including labelled inputs, readable contrast, and keyboard-usable controls.
**Logging:** Python-compatible application logging.
**Authentication:** Firebase Authentication using Google account sign-in.
**Data Storage:** All persistent task data must be stored in Google Sheets. No separate application database may be used.
**External Integration:** Google Sheets API for all task and task-metadata storage operations.

## Read Only files in this project
Do not modify these files or folders
- any files in the `spec/` directory
- `sources.md` file
- `presentation.md` file
- `todo.md` file
- `versions.md` file

Provide a responsive browser-based web UI for viewing and managing tasks. The web UI should display task information and provide task-management actions in the browser.

The web UI should use Flask-rendered HTML templates with CSS and browser JavaScript.

The web UI must be responsive and usable on mobile and desktop browsers.

The web UI must provide basic accessibility through labelled inputs, readable contrast, and keyboard-usable controls.

The application should require users to authenticate with Firebase Authentication using their Google account before accessing task data. All stored task data must remain in Google Sheets.

The GUI should have the following features:
* A task list or task information display
* Controls to add a task with a category and task name
* A control to refresh task information
* A control to sort tasks by colour
* A control to run task-sheet triage
* Status or output information for completed actions

Update all necessary source code to implement the responsive Flask web UI, including the Python project configuration, HTML templates, JavaScript, Readme.md, Firebase deployment configuration, and tests where applicable.

Task operations must preserve the configured spreadsheet structure, including the `Tasks` sheet, category data, `z done` marker, `T Date` field, and supporting task metadata.
