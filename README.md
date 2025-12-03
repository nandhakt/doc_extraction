# 📄 DocExtract AI

An intelligent agentic document extraction solution built with **Streamlit**, **FastAPI**, and **LangGraph**. Extract structured data from PDF documents using AI, with human-in-the-loop feedback for refinement.

![Architecture](https://img.shields.io/badge/Architecture-Agentic-blueviolet)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **🤖 Agentic Extraction**: LangGraph-powered workflow for intelligent document understanding
- **📋 Schema-Driven**: Define extraction fields via JSON schema
- **👁️ Side-by-Side View**: PDF viewer alongside extracted data
- **💬 Human-in-the-Loop**: Provide feedback to refine extractions
- **🔄 Iterative Refinement**: Re-run extraction with corrections
- **📊 Confidence Scores**: See extraction confidence for each field
- **🎨 Modern UI**: Beautiful, responsive Streamlit interface

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌──────────────────┐      ┌──────────────────────────┐     │
│  │   PDF Viewer     │      │   Extraction Results     │     │
│  │   - Page nav     │      │   - Field values         │     │
│  │   - Zoom         │      │   - Confidence bars      │     │
│  └──────────────────┘      │   - Feedback input       │     │
│                            └──────────────────────────┘     │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │  Upload    │  │  Extract   │  │     Feedback         │   │
│  │  /upload   │  │  /extract  │  │     /feedback        │   │
│  └────────────┘  └────────────┘  └──────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Agent                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐   │
│  │ Extract  │───▶│ Validate │───▶│ Apply Feedback       │   │
│  │   Node   │    │   Node   │    │      Node            │   │
│  └──────────┘    └──────────┘    └──────────────────────┘   │
│        │                                    │               │
│        └────────────◀───────────────────────┘               │
│                    (Re-extraction loop)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd doc_extraction
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

### Running the Application

**Option 1: Using the startup script**
```bash
chmod +x start.sh
./start.sh
```

**Option 2: Manual startup**

Terminal 1 - Start the API:
```bash
python run_api.py
```

Terminal 2 - Start the frontend:
```bash
streamlit run streamlit_app.py
```

### Access the Application

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Define Your Schema

In the sidebar, define a JSON schema for the fields you want to extract:

```json
{
  "type": "object",
  "properties": {
    "invoice_number": {
      "type": "string",
      "description": "Invoice or document number"
    },
    "date": {
      "type": "string",
      "description": "Document date"
    },
    "total_amount": {
      "type": "number",
      "description": "Total amount"
    }
  },
  "required": ["invoice_number", "date"]
}
```

### 2. Upload a PDF

Drag and drop or click to upload your PDF document.

### 3. Extract Fields

Click "🚀 Extract Fields" to run the AI extraction.

### 4. Review Results

- View extracted values alongside their confidence scores
- Fields with low confidence are highlighted
- Navigate PDF pages to verify extraction

### 5. Provide Feedback (Optional)

If results need correction:
1. Enter feedback in the text area (e.g., "The date should be in MM/DD/YYYY format")
2. Click "🔄 Re-extract with Feedback"
3. The agent will re-process considering your feedback

### 6. Export Results

Click "📥 Export Results" to download the extracted data as JSON.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | Model to use | `gpt-4o` |
| `FASTAPI_HOST` | API host | `localhost` |
| `FASTAPI_PORT` | API port | `8000` |

### Customizing the Schema

The JSON schema supports:
- **String fields**: Text values
- **Number fields**: Numeric values
- **Array fields**: Lists of items
- **Nested objects**: Complex structures
- **Required fields**: Mark fields that must be extracted

## 📁 Project Structure

```
doc_extraction/
├── agent/
│   ├── __init__.py
│   └── extraction_agent.py    # LangGraph extraction workflow
├── api/
│   ├── __init__.py
│   ├── main.py               # FastAPI endpoints
│   └── models.py             # Pydantic schemas
├── utils/
│   ├── __init__.py
│   └── pdf_processor.py      # PDF text/image extraction
├── uploads/                   # Uploaded PDFs (auto-created)
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── run_api.py               # API startup script
├── start.sh                 # Combined startup script
├── streamlit_app.py         # Streamlit frontend
└── README.md
```

## 🛠️ API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF file |
| `POST` | `/extract/{session_id}` | Extract fields from PDF |
| `POST` | `/feedback` | Submit feedback and re-extract |
| `GET` | `/pdf/{session_id}/page/{page_num}` | Get PDF page as image |
| `GET` | `/pdf/{session_id}/info` | Get PDF metadata |
| `GET` | `/session/{session_id}` | Get session status |
| `DELETE` | `/session/{session_id}` | Delete session |

### Example API Usage

```python
import httpx
import json

# Upload PDF
with open("document.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
    session_id = response.json()["session_id"]

# Extract fields
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "date": {"type": "string"}
    }
}

response = httpx.post(
    f"http://localhost:8000/extract/{session_id}",
    data={"json_schema": json.dumps(schema)}
)
print(response.json())
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.


