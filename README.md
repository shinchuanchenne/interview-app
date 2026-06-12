# Interview Answer Management App

A lightweight multi-user CRUD application built with Python and Streamlit for organizing Japanese interview preparation content.


## Overview

This application supports:

- User login with locally stored credentials
- Per-user interview data storage
- Creating interview preparation entries
- Editing existing entries
- Deleting entries
- Organizing questions by category
- Reviewing answers in a card-based layout
- Practicing with random interview questions


## Features

- Login and account creation UI
- Per-user local JSON storage
- Password hashing with per-user salt
- Automatic creation of a personal data file for each user
- Default categories created for each new user
- User-defined category creation
- Category rename support
- Empty-category deletion support
- Category-based navigation
- Per-category item ordering
- Global interview mode with random question selection
- Category-specific interview mode with random question selection
- Prevention of immediate repetition in random mode
- Toggle controls for showing or hiding points and answers


## Data Model

Each interview entry contains the following fields:

- `question`: Japanese interview question
- `points`: Answer points or talking notes
- `answer`: Formal answer
- `category`: Entry category
- `order`: Position within the category
- `id`: Unique card identifier

Each user has a dedicated JSON file containing:

- `username`
- `categories`
- `items`

Default categories for a newly created user:

- `經歷`
- `前職`
- `人柄`
- `專案`
- `志望動機`


## Project Structure

```text
interview-python-app/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── PROJECT_CONTEXT.txt
├── users.json
└── user_data/
    └── <hashed-username>.json
```

Notes:

- `users.json` stores account credentials metadata
- `user_data/` stores one JSON file per user
- both are created automatically when needed
- both are excluded from Git by default


## Requirements

- Python 3
- `pip`


## Installation

Clone the repository:

```bash
git clone <repository-url>
cd interview-python-app
```

Alternatively, download the repository as a ZIP archive and extract it locally.

Install dependencies:

```bash
pip install -r requirements.txt
```

If the environment uses `pip3`, run:

```bash
pip3 install -r requirements.txt
```


## Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

If the `streamlit` command is not available in the shell, use:

```bash
python -m streamlit run app.py
```

or:

```bash
python3 -m streamlit run app.py
```

The default local address is:

```text
http://localhost:8501
```


## Authentication

The application starts with a login screen.

Available actions:

- `登入` for existing users
- `建立帳號` for new users

Credential handling:

- User passwords are not stored as plain text
- Passwords are hashed using PBKDF2-HMAC-SHA256
- Each user record includes a unique salt

Storage:

- account metadata is stored in `users.json`
- interview data is stored in `user_data/<hashed-username>.json`


## Usage

### Sidebar Navigation

- Questions are listed in the left sidebar by category
- Selecting a question opens its content in the main panel
- Items within the same category can be reordered using `↑` and `↓`
- Each category includes `抽題`, `編輯`, and `刪除` controls
- A category can be deleted only when it contains no cards

### Interview Mode

- `面試模式` in the upper-left area selects a random question from all entries of the current user
- `抽題` beside each category selects a random question only from that category
- Random selection does not immediately repeat the currently displayed question

### Question Cards

The main panel displays three cards in vertical order:

1. Question
2. Answer Points
3. Formal Answer

The following display controls are available:

- `顯示 Point`
- `顯示答案`

### Creating an Entry

- Expand `新增一筆面試準備資料`
- Select an existing category, or provide a new category name
- If a new category name is provided, it takes precedence over the selected existing category
- Enter question, points, and answer
- Select `新增資料`

### Category Management

- Each user manages categories independently
- Category names can be edited from the sidebar using `編輯`
- Categories can be removed using `刪除` only when no cards remain in that category

### Editing an Entry

- Expand `編輯這張小卡`
- Modify the desired fields
- Select `更新資料`

### Deleting an Entry

- Expand `編輯這張小卡`
- Select `刪除資料`

### Logging Out

- Use `登出` in the sidebar to end the current session


## Local Data Storage

The application uses two local storage layers:

### 1. Account Registry

File:

- `users.json`

Purpose:

- stores usernames
- stores password hash values
- stores per-user salts

### 2. Per-User Interview Data

Directory:

- `user_data/`

Each user has one dedicated JSON file containing:

- `username`
- `categories`
- `items`

Behavior:

- `users.json` is created automatically if missing
- `user_data/` is created automatically if missing
- a per-user JSON file is created automatically when a new account is created
- a per-user JSON file is also recreated if missing when the user logs in


## Testing Status

Core logic has been validated with local logic tests covering:

- user creation
- per-user JSON creation
- password hashing
- login success and failure
- default category initialization
- category creation and duplicate rejection
- category-local ordering
- reordering behavior
- save/load round trips
- random selection rules

Latest recorded result:

```text
17 tests, 0 failed
```

These checks validate the logic layer, not full browser-driven UI automation.


## Git Tracking and `.gitignore`

The repository excludes the following local files and directories:

```text
data.json
categories.json
users.json
user_data/
.venv/
__pycache__/
.DS_Store
```

As a result, local credentials and local interview data are not included in Git commits by default.

If any of these files were previously committed before `.gitignore` was updated, stop tracking them with:

```bash
git rm --cached users.json
git rm -r --cached user_data
git commit -m "Stop tracking local user data"
```


## Publishing to GitHub

If Git has not been initialized in the project directory, run:

```bash
git init
git add .
git commit -m "Initial commit"
```

After creating a repository on GitHub, connect and push the local project:

```bash
git remote add origin https://github.com/<account>/<repository>.git
git branch -M main
git push -u origin main
```


## Windows Setup

1. Install Python from [python.org](https://www.python.org/downloads/windows/).
2. Enable `Add Python to PATH` during installation.
3. Open `Command Prompt` or `PowerShell`.
4. Change to the project directory:

```bash
cd path\to\interview-python-app
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Start the application:

```bash
streamlit run app.py
```

If necessary, use:

```bash
python -m streamlit run app.py
```
