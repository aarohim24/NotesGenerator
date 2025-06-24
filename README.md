# AI-Powered Document to Notes Converter

## Overview

A desktop application that uses AI to transform documents (PDF/DOCX) into structured study materials. The system combines OpenAI's GPT-3.5 with a local BART model fallback to ensure reliable note generation.

## Key Features

### Core Functionality
- **Multi-Format Processing**: Supports PDF and DOCX inputs
- **AI Note Generation**: Four output styles (Bullet Points, Outline, Summary, Flashcards)
- **Model Redundancy**: Automatic fallback to local BART model if API unavailable

### Export Capabilities
- Markdown with proper heading hierarchy
- Standalone HTML documents

### Technical Highlights
- Chunked processing for large documents
- Configurable detail levels (1-5 granularity)
- Custom prompt engineering interface
- Progress tracking with time estimation

## Installation

```bash
git clone https://github.com/yourusername/ai-notes-generator.git
cd ai-notes-generator

python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file:
```ini
OPENAI_API_KEY=your_api_key_here
```

2. Optional: Adjust `config.json` for:
- Default output directory
- Model temperature settings
- Chunk size preferences

## Usage

```bash
python main.py
```

