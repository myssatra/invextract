import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.ocr.extractor import extract_tables_from_file, allowed_file
from src.llm.processor import process_data_with_llm
from config.settings import SYSTEM_TEMPLATE
import shutil
from pathlib import Path

app = FastAPI(title="Receipt Processing API")

INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/process-file/", response_model=dict)
async def process_file(file: UploadFile = File(...)):
    """
    Принимает PDF или изображение, извлекает таблицы и возвращает структурированный JSON.
    """
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла. Разрешены: .pdf, .png, .jpg, .jpeg")

    input_file_path = INPUT_DIR / file.filename
    with open(input_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        temp_output_path = OUTPUT_DIR / f"temp_{file.filename}.json"
        extracted_json_path = extract_tables_from_file(str(input_file_path), str(temp_output_path))

        structured_json = process_data_with_llm(extracted_json_path, SYSTEM_TEMPLATE)

        return json.loads(structured_json)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")
    finally:
        if input_file_path.exists():
            os.remove(input_file_path)
        if temp_output_path.exists():
            os.remove(temp_output_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)