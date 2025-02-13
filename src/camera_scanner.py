# src/camera_scanner.py
from dotenv import load_dotenv
load_dotenv()

from tkinter import *
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import requests
import logging
from typing import List, Dict
import tempfile
import os

from .config import CAMERA_RESOLUTION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraCardScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Camera Scanner")
        self.root.geometry("1200x800")
        self.scan_results: List[Dict] = []
        self.camera = None
        self._init_ui()

    def _init_ui(self):
        camera_section = ttk.Frame(self.root)
        camera_section.pack(fill=X, padx=5, pady=5)
        
        camera_controls = ttk.Frame(camera_section)
        camera_controls.pack(fill=X)
        
        ttk.Button(camera_controls, text="Start Camera", command=self.start_camera).pack(side=LEFT, padx=5)
        self.status_label = ttk.Label(camera_controls, text="")
        self.status_label.pack(side=LEFT, padx=5)
        
        self.camera_label = ttk.Label(camera_section)
        self.camera_label.pack(pady=5)

        results_frame = ttk.Frame(self.root)
        results_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        columns = ("name", "colour", "type", "creature_type", "mana_cost", 
                  "power", "toughness", "abilities", "oracle_text", "quantity", "include")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        
        column_titles = {
            "name": "Card Name", "colour": "Color", "type": "Type",
            "creature_type": "Creature Type", "mana_cost": "Mana Cost",
            "power": "Power", "toughness": "Toughness", "abilities": "Abilities",
            "oracle_text": "Card Text", "quantity": "Qty", "include": "Include"
        }
        
        column_widths = {
            "name": 150, "colour": 80, "type": 120, "creature_type": 120,
            "mana_cost": 100, "power": 60, "toughness": 60, "abilities": 150,
            "oracle_text": 200, "quantity": 60, "include": 60
        }
        
        for col in columns:
            self.tree.heading(col, text=column_titles[col])
            self.tree.column(col, width=column_widths[col])
        
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(column=0, row=0, sticky=NSEW)
        vsb.grid(column=1, row=0, sticky=NS)
        hsb.grid(column=0, row=1, sticky=EW)
        
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=X, padx=5, pady=5)
        
        ttk.Button(bottom_frame, text="Capture", command=self.capture_image).pack(side=LEFT, padx=5)
        self.confirm_button = ttk.Button(bottom_frame, text="Confirm & Add to CSV", 
                                       command=self.process_selected, state=DISABLED)
        self.confirm_button.pack(side=RIGHT, padx=5)
        
        self.tree.bind('<Button-1>', self._handle_click)

    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.update_camera()
        
    def update_camera(self):
        if self.camera is not None:
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, CAMERA_RESOLUTION)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.camera_label.configure(image=photo)
                self.camera_label.image = photo
            self.root.after(10, self.update_camera)
            
    def capture_image(self):
        if self.camera is None:
            return
            
        ret, frame = self.camera.read()
        if ret:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                cv2.imwrite(tmp.name, frame)
                self._process_images([tmp.name])
                os.unlink(tmp.name)

    def _process_images(self, files: List[str]):
        try:
            files_data = [('files', (f'image{i}.jpg', open(file_path, 'rb'), 'image/jpeg'))
                         for i, file_path in enumerate(files)]
            
            response = requests.post('http://localhost:8000/scan-batch', files=files_data)
            response.raise_for_status()
            results = response.json()
            
            self.scan_results.extend(results)
            
            for card in results:
                self.tree.insert("", END,
                    values=(
                        card['name'],
                        card.get('colour', 'N/A'),
                        card.get('type', 'N/A'),
                        card.get('creature_type', 'N/A'),
                        card.get('mana_cost', 'N/A'),
                        card.get('power', 'N/A'),
                        card.get('toughness', 'N/A'),
                        card.get('abilities', 'N/A'),
                        card.get('oracle_text', 'N/A'),
                        card.get('quantity', 1),
                        "✓"
                    ))
                
        except Exception as e:
            logger.exception("Error processing images")
            self.tree.insert("", END,
                values=("Error", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", str(e), "N/A", "✗"))
        
        self.confirm_button.config(state=NORMAL)

    def _handle_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        column = self.tree.identify_column(event.x)
        if column != "#11":  # Include column
            return
            
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        current_values = self.tree.item(item_id)['values']
        new_mark = "✗" if current_values[10] == "✓" else "✓"
        self.tree.set(item_id, "include", new_mark)
        
    def process_selected(self):
        selected_cards = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id)['values']
            if values[10] == "✓":
                card_index = int(self.tree.index(item_id))
                if card_index < len(self.scan_results):
                    selected_cards.append(self.scan_results[card_index])
        
        if not selected_cards:
            self.status_label.config(text="No cards selected")
            return
            
        try:
            response = requests.post('http://localhost:8000/add-batch', json=selected_cards)
            response.raise_for_status()
            
            self.status_label.config(text=f"Added {len(selected_cards)} cards to collection")
            self.confirm_button.config(state=DISABLED)
            self.tree.delete(*self.tree.get_children())
            self.scan_results = []
            
        except Exception as e:
            logger.exception("Error saving cards")
            self.status_label.config(text=f"Error saving cards: {str(e)}")

    def __del__(self):
        if self.camera is not None:
            self.camera.release()

def main():
    root = Tk()
    app = CameraCardScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()