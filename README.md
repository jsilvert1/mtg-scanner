# README.md
# MTG Card Scanner

Magic: The Gathering card scanner using computer vision for collection management.

## Features
- Webcam card scanning
- OCR text detection via Google Cloud Vision
- Card lookup via Scryfall API
- Local CSV collection storage
- GUI for managing scanned cards

## Requirements
- Python 3.8+
- Google Cloud Vision API credentials
- Webcam

## Installation
```bash
git clone https://github.com/yourusername/mtg-scanner.git
cd mtg-scanner
pip install -e .
```

## Configuration
1. Copy `.env.example` to `.env`
2. Set up Google Cloud Vision:
   - Create project in Google Cloud Console
   - Enable Vision API
   - Create service account key
   - Save as `google_credentials.json`
   - Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env`

## Usage
Start API server:
```bash
mtg-server
```

Launch scanner GUI:
```bash
mtg-scanner
```

## Development
Install dev dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

## License
GPL v3
