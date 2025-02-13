# src/data_manager.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from .config import CSV_PATH

logger = logging.getLogger(__name__)

class CardDataManager:
    def __init__(self):
        self.headers = ['colour', 'name', 'type', 'creature_type', 
                       'mana_cost', 'power', 'toughness', 'quantity',
                       'abilities', 'oracle_text']
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
            pd.DataFrame(columns=self.headers).to_csv(CSV_PATH, index=False)

    def validate_card_data(self, card: Dict) -> Dict:
        required_fields = {'name', 'type', 'colour', 'mana_cost'}
        missing_fields = required_fields - set(card.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        card['quantity'] = 1
        
        optional_fields = [h for h in self.headers if h not in required_fields and h != 'quantity']
        for field in optional_fields:
            card[field] = card.get(field) if card.get(field) else None

        return {key: card.get(key) for key in self.headers}

    def add_card(self, card: Dict) -> Dict:
        validated_card = self.validate_card_data(card)
        
        if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
            df = pd.read_csv(CSV_PATH)
            existing = df[df['name'] == validated_card['name']]
            
            if not existing.empty:
                df.loc[existing.index[0], 'quantity'] += 1
                df.to_csv(CSV_PATH, index=False)
                return df.loc[existing.index[0]].to_dict()
        else:
            df = pd.DataFrame(columns=self.headers)
            
        new_row = pd.DataFrame([validated_card], columns=self.headers)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)
        
        return validated_card

    def get_cards(self, filters: Optional[Dict] = None) -> List[Dict]:
        if not CSV_PATH.exists():
            return []
            
        df = pd.read_csv(CSV_PATH)
        df = df.replace([np.nan], [None])
        
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        return df.to_dict('records')