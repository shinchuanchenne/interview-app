# Interview Answer Management App

A lightweight CRUD application built with Python and Streamlit for organizing Japanese interview preparation content.


## Overview

This application supports:

- Creating interview preparation entries
- Editing existing entries
- Deleting entries
- Organizing questions by category
- Reviewing answers in a card-based layout
- Practicing with random interview questions


## Features

- Local JSON-based storage
- Automatic `data.json` creation when the file does not exist
- Automatic `categories.json` creation when the file does not exist
- Default categories created on first run
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

Each entry contains the following fields:

- `question`: Japanese interview question
- `points`: Answer points or talking notes
- `answer`: Formal answer
- `category`: Entry category

Default categories created on first run:

- `經歷`
- `前職`
- `人柄`
- `專案`
- `志望動機`

Additional categories can be created from the application UI.


## Project Structure

```text
interview-python-app/
├── app.py
├── requirements.txt
├── .gitignore
├── categories.json
└── data.json
```


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


## Usage

### Sidebar Navigation

- Questions are listed in the left sidebar by category
- Selecting a question opens its content in the main panel
- Items within the same category can be reordered using `↑` and `↓`
- Each category includes `抽題`, `編輯`, and `刪除` controls
- A category can be deleted only when it contains no cards

### Interview Mode

- `Interview Mode` in the upper-left area selects a random question from all entries
- `抽題` beside each category selects a random question only from that category
- Random selection does not immediately repeat the currently displayed question

### Question Cards

The main panel displays three cards in vertical order:

1. Question
2. Answer Points
3. Formal Answer

The following display controls are available:

- `Show Point`
- `Show Answer`

### Creating an Entry

- Expand `新增一筆面試準備資料`
- Select an existing category, or provide a new category name
- If a new category name is provided, it takes precedence over the selected existing category
- Enter question, points, and answer
- Select `新增資料`

### Category Management

- Default categories are created automatically when `categories.json` is first generated
- Category names can be edited from the sidebar using `編輯`
- Categories can be removed using `刪除` only when no cards remain in that category

### Editing an Entry

- Expand `編輯這張小卡`
- Modify the desired fields
- Select `更新資料`

### Deleting an Entry

- Expand `編輯這張小卡`
- Select `刪除資料`


## Local Data Storage

Application data is stored locally in `data.json` and `categories.json`.

Behavior:

- The application checks for `data.json` each time it loads data
- The application checks for `categories.json` each time it loads categories
- If the file does not exist, an empty `data.json` file is created automatically
- If the category file does not exist, a `categories.json` file is created automatically with the default categories
- No manual creation step is required before first launch


## Git Tracking and `.gitignore`

The repository excludes the following local files and directories:

```text
data.json
categories.json
.venv/
__pycache__/
.DS_Store
```

As a result, local interview data and local category configuration are not included in Git commits by default.

If `data.json` or `categories.json` was previously committed before `.gitignore` was added, stop tracking it with:

```bash
git rm --cached data.json
git rm --cached categories.json
git commit -m "Stop tracking local data files"
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
