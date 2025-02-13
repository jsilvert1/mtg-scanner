# src/scryfall.py
from typing import Dict, Optional
import httpx
import logging
from .config import SCRYFALL_API_URL

logger = logging.getLogger(__name__)

class ScryfallAPI:
    @staticmethod
    async def fuzzy_search(card_text: str) -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{SCRYFALL_API_URL}/cards/named",
                    params={"fuzzy": card_text}
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Scryfall response for {card_text}: {data}")
                return data
            except Exception as e:
                logger.error(f"Scryfall API error for {card_text}: {str(e)}")
                return None

    @staticmethod
    def extract_card_properties(card_data: Dict) -> Dict:
        return {
            "colour": "".join(card_data.get("colors", [])),
            "name": card_data.get("name"),
            "type": card_data.get("type_line"),
            "creature_type": card_data.get("type_line").split("—")[1].strip() if "—" in card_data.get("type_line", "") else "",
            "mana_cost": card_data.get("mana_cost"),
            "power": card_data.get("power"),
            "toughness": card_data.get("toughness"),
            "abilities": ", ".join(card_data.get("keywords", [])),
            "oracle_text": card_data.get("oracle_text", "")
        }