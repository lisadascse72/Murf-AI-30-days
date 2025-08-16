from dotenv import load_dotenv
load_dotenv()  # Must be first

from fastapi import FastAPI, WebSocket, WebSocketDisconnect # Added WebSocket and WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import logging

from routes import chat_routes

# --- Configure logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Ensure Gemini API key is available for backend ---
# If GEMINI_API_KEY not set, copy from VITE_GEMINI_API_KEY
if not os.getenv("GEMINI_API_KEY") and os.getenv("VITE_GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("VITE_GEMINI_API_KEY")

# Log keys presence (no actual values for safety)
logging.info(f"MURF_API_KEY loaded: {bool(os.getenv('MURF_API_KEY'))}")
logging.info(f"ASSEMBLYAI_API_KEY loaded: {bool(os.getenv('ASSEMBLYAI_API_KEY'))}")
logging.info(f"GEMINI_API_KEY loaded: {bool(os.getenv('GEMINI_API_KEY'))}")

# --- Create uploads dir ---
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- Init FastAPI ---
app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routes ---
app.include_router(chat_routes.router)

# --- WebSocket Echo Endpoint ---
# This new endpoint will establish a WebSocket connection
# and simply echo back any text message it receives.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # Accept the WebSocket connection
    logging.info("WebSocket connection established.")
    try:
        while True:
            # Receive a text message from the client
            data = await websocket.receive_text()
            logging.info(f"Received WebSocket message: {data}")
            # Echo the received message back to the client
            await websocket.send_text(f"Message text was: {data}")
            logging.info(f"Echoed WebSocket message: {data}")
    except WebSocketDisconnect:
        # Handle disconnection gracefully
        logging.info("WebSocket disconnected.")
    except Exception as e:
        # Catch any other potential errors
        logging.error(f"WebSocket error: {e}")

# --- Serve uploads ---
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
