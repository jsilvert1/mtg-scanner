# src/vision.py
from google.cloud import vision
import logging
from fastapi import HTTPException

from .scryfall import ScryfallAPI

logger = logging.getLogger(__name__)

async def process_card_image(image_bytes: bytes) -> dict:
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    
    try:
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            logger.error("No text detected in image")
            raise HTTPException(status_code=400, detail="No text detected in image")
            
        full_text = texts[0].description
        card_name = full_text.split('\n')[0]
        logger.debug(f"Detected card name: {card_name}")
        
        card_data = await ScryfallAPI.fuzzy_search(card_name)
        if not card_data:
            logger.error(f"Card not found in Scryfall: {card_name}")
            raise HTTPException(status_code=404, detail="Card not found in Scryfall database")
        
        properties = ScryfallAPI.extract_card_properties(card_data)
        logger.debug(f"Extracted properties: {properties}")
        return properties
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))