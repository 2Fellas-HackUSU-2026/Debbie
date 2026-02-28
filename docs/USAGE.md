# Word Document Gap Finder & Templater

This tool allows you to upload a Word document (`.docx`), identify areas that need to be filled in (either manually or with AI suggestions), and convert them into a Jinja2-templated document for automated data injection later.

## Quick Start

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Configuration
Create a `.env` file in the `config/` directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_sk_...
```

### 3. Installation
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 4. Running the Tool
Start the FastAPI server:
```bash
python3 api/main.py
```
Open your browser and navigate to **`http://localhost:8000`**.

## Features

### 📄 Document Parsing
The tool parses your Word document into its structural components (paragraphs and tables) and renders them as an interactive web page.

### 🧠 AI-Powered Suggestions
Once a document is uploaded, the tool automatically uses OpenAI to scan for potential "blanks" (underscores, empty cells, placeholder text like `[DATE]`). These will appear with a yellow **Suggested** badge in the UI.

### 🖱️ Graphical Selection
- **Paragraphs**: Click any paragraph to select it.
- **Table Cells**: Click any cell in a table to select it individually.
- **Table Columns**: Click the **down arrow (↓)** at the top of any table column to select the entire column. This is ideal for "Job Steps" or "Hazard" columns.

### 🏷️ Variable Mapping
After selecting a region, enter a variable name (e.g., `project_manager`).
- For **Columns**, the tool automatically appends an index (e.g., `step_description_0`, `step_description_1`) to each row.

### 🛠️ Templating Output
When you click **Finalize Document**, the tool:
1. Replaces all selected text in the `.docx` with Jinja2 placeholders (e.g., `{{ project_manager }}`).
2. Generates a `mapping.json` file in the `api/uploads` directory that records which variable corresponds to which document part.
3. Automatically triggers a download of the new templated `.docx` file.

## Project Structure
- `api/main.py`: FastAPI backend and document processing logic.
- `web/index.html`: Interactive frontend.
- `api/uploads/`: Temporary storage for uploaded and processed documents.
- `config/`: Configuration files and `.env`.
- `requirements.txt`: Python dependencies.
