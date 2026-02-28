import os
import uuid
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from docx import Document
import openai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))

app = FastAPI()

# Enable CORS for frontend interaction
# In production, replace ["*"] with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

UPLOAD_DIR = "api/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Selection(BaseModel):
    id: str # e.g., "p_0", "t_0_r_1_c_2", or "t_0_col_2"
    variable_name: str
    description: Optional[str] = None

class ProcessRequest(BaseModel):
    doc_id: str
    selections: List[Selection]

def parse_docx(filepath: str) -> Dict[str, Any]:
    doc = Document(filepath)
    paragraphs = []
    for i, p in enumerate(doc.paragraphs):
        paragraphs.append({
            "id": f"p_{i}",
            "text": p.text,
            "style": p.style.name
        })

    tables = []
    for i, t in enumerate(doc.tables):
        rows = []
        for r_idx, row in enumerate(t.rows):
            cells = []
            for c_idx, cell in enumerate(row.cells):
                cells.append({
                    "id": f"t_{i}_r_{r_idx}_c_{c_idx}",
                    "text": cell.text
                })
            rows.append(cells)
        tables.append({
            "id": f"t_{i}",
            "rows": rows,
            "num_columns": len(t.columns)
        })

    return {"paragraphs": paragraphs, "tables": tables}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    doc_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, f"{doc_id}.docx")

    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    structure = parse_docx(filepath)

    # Save structure for later
    with open(os.path.join(UPLOAD_DIR, f"{doc_id}.json"), "w") as f:
        json.dump(structure, f)

    return {"doc_id": doc_id, "structure": structure}

@app.get("/suggest/{doc_id}")
async def suggest_regions(doc_id: str):
    struct_path = os.path.join(UPLOAD_DIR, f"{doc_id}.json")
    if not os.path.exists(struct_path):
        raise HTTPException(status_code=404, detail="Document not found")

    with open(struct_path, "r") as f:
        structure = json.load(f)

    # Prepare prompt for OpenAI
    prompt_content = "Identify potential fillable fields in this Word document structure. "
    prompt_content += "Look for empty cells, underscores, or placeholder text. "
    prompt_content += "Return a JSON object with a key 'suggestions' which is a list of objects with 'id' (the identifier from the structure) and 'suggested_name'.\n\n"
    prompt_content += json.dumps(structure)[:8000]

    api_key = os.getenv("OPEN_AI_KEY") or os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a document analysis assistant. Return only valid JSON."},
                {"role": "user", "content": prompt_content}
            ],
            response_format={ "type": "json_object" }
        )
        suggestions = json.loads(response.choices[0].message.content)
        return suggestions
    except Exception as e:
        return {"suggestions": [], "error": str(e)}

@app.post("/process")
async def process_document(request: ProcessRequest):
    doc_path = os.path.join(UPLOAD_DIR, f"{request.doc_id}.docx")
    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail="Document not found")

    doc = Document(doc_path)
    mapping = {}

    # Apply selections
    for selection in request.selections:
        mapping[selection.variable_name] = {
            "id": selection.id,
            "description": selection.description
        }

        if selection.id.startswith("p_"):
            p_idx = int(selection.id.split("_")[1])
            if p_idx < len(doc.paragraphs):
                doc.paragraphs[p_idx].text = f"{{{{ {selection.variable_name} }}}}"
        elif selection.id.startswith("t_"):
            parts = selection.id.split("_")
            t_idx = int(parts[1])
            if t_idx < len(doc.tables):
                table = doc.tables[t_idx]
                if "col" in selection.id:
                    # Column selection e.g. t_0_col_2
                    col_idx = int(parts[3])
                    # Skip header row (index 0) usually, but for now we'll do all rows
                    # The user might want to fill everything.
                    for r_idx, row in enumerate(table.rows):
                        if col_idx < len(row.cells):
                            row.cells[col_idx].text = f"{{{{ {selection.variable_name}_{r_idx} }}}}"
                else:
                    # Individual cell selection
                    r_idx, c_idx = int(parts[3]), int(parts[5])
                    if r_idx < len(table.rows) and c_idx < len(table.rows[r_idx].cells):
                        table.rows[r_idx].cells[c_idx].text = f"{{{{ {selection.variable_name} }}}}"

    output_path = os.path.join(UPLOAD_DIR, f"{request.doc_id}_templated.docx")
    doc.save(output_path)

    mapping_path = os.path.join(UPLOAD_DIR, f"{request.doc_id}_mapping.json")
    with open(mapping_path, "w") as f:
        json.dump(mapping, f)

    return {"message": "Document processed", "download_url": f"/download/{request.doc_id}", "mapping": mapping}

@app.get("/download/{doc_id}")
async def download_document(doc_id: str):
    output_path = os.path.join(UPLOAD_DIR, f"{doc_id}_templated.docx")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="templated_document.docx")

@app.get("/")
async def read_index():
    return FileResponse("web/index.html")

if os.path.exists("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
