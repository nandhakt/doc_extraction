"""
Run the FastAPI backend server.
"""

import uvicorn
from config import FASTAPI_HOST, FASTAPI_PORT

if __name__ == "__main__":
    print(f"🚀 Starting Document Extraction API on http://{FASTAPI_HOST}:{FASTAPI_PORT}")
    print(f"📚 API Docs available at http://{FASTAPI_HOST}:{FASTAPI_PORT}/docs")
    
    uvicorn.run(
        "api.main:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=True,
        log_level="info"
    )


