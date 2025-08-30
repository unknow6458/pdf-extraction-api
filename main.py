from fastapi import FastAPI, File, UploadFile
import fitz  # pymupdf
import hashlib
import os

app = FastAPI(title="PDF Extract API", version="1.0")

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def hash_file(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

@app.post("/v1/extract")
async def extract_pdf(file: UploadFile = File(...)):
    content = await file.read()
    file_hash = hash_file(content)

    cache_path = os.path.join(CACHE_DIR, f"{file_hash}.txt")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return {"cache": "hit", "text": f.read()}

    # Extract text
    doc = fitz.open(stream=content, filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])

    with open(cache_path, "w") as f:
        f.write(text)

    return {"cache": "miss", "text": text}
