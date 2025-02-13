# src/main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

from .vision import process_card_image
from .data_manager import CardDataManager
from .config import API_HOST, API_PORT, API_RELOAD, MAX_BATCH_SIZE

import asyncio
import uvicorn

app = FastAPI()
card_manager = CardDataManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan-batch", response_model=List[Dict])
async def scan_batch(files: List[UploadFile] = File(...)):
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_BATCH_SIZE} files allowed")
    
    async def process_single(file: UploadFile) -> Dict:
        contents = await file.read()
        return await process_card_image(contents)
    
    tasks = [process_single(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_results = [r for r in results if isinstance(r, dict)]
    return valid_results

@app.post("/add-batch", response_model=List[Dict])
async def add_batch(cards: List[Dict] = Body(...)):
    if len(cards) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_BATCH_SIZE} cards allowed")
    
    results = []
    for card in cards:
        result = card_manager.add_card(card)
        results.append(result)
    
    return results

def main():
    uvicorn.run("src.main:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)

if __name__ == "__main__":
    main()