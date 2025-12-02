import os
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# MongoDB configuration - use environment variable or default
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/")
DB_NAME = os.getenv("DB_NAME", "emogo")

app = FastAPI(title="EmoGo Backend API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for data validation
class VlogEntry(BaseModel):
    user_id: str
    video_url: Optional[str] = None
    video_data: Optional[str] = None  # base64 encoded video
    description: Optional[str] = None
    timestamp: Optional[datetime] = None


class SentimentEntry(BaseModel):
    user_id: str
    sentiment: str  # e.g., "happy", "sad", "angry", etc.
    score: Optional[float] = None
    timestamp: Optional[datetime] = None


class GPSEntry(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None


# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


# Database connection events
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    app.mongodb = app.mongodb_client[DB_NAME]
    print(f"Connected to MongoDB: {DB_NAME}")


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to EmoGo Backend API", "docs": "/docs", "data_export": "/export"}


# ==================== VLOG ENDPOINTS ====================
@app.post("/vlogs")
async def create_vlog(vlog: VlogEntry):
    vlog_dict = vlog.model_dump()
    if vlog_dict.get("timestamp") is None:
        vlog_dict["timestamp"] = datetime.utcnow()
    result = await app.mongodb["vlogs"].insert_one(vlog_dict)
    return {"id": str(result.inserted_id), "message": "Vlog created successfully"}


@app.get("/vlogs")
async def get_vlogs(user_id: Optional[str] = None, limit: int = 100):
    query = {}
    if user_id:
        query["user_id"] = user_id
    vlogs = await app.mongodb["vlogs"].find(query).to_list(limit)
    return [serialize_doc(v) for v in vlogs]


# ==================== SENTIMENT ENDPOINTS ====================
@app.post("/sentiments")
async def create_sentiment(sentiment: SentimentEntry):
    sentiment_dict = sentiment.model_dump()
    if sentiment_dict.get("timestamp") is None:
        sentiment_dict["timestamp"] = datetime.utcnow()
    result = await app.mongodb["sentiments"].insert_one(sentiment_dict)
    return {"id": str(result.inserted_id), "message": "Sentiment created successfully"}


@app.get("/sentiments")
async def get_sentiments(user_id: Optional[str] = None, limit: int = 100):
    query = {}
    if user_id:
        query["user_id"] = user_id
    sentiments = await app.mongodb["sentiments"].find(query).to_list(limit)
    return [serialize_doc(s) for s in sentiments]


# ==================== GPS ENDPOINTS ====================
@app.post("/gps")
async def create_gps(gps: GPSEntry):
    gps_dict = gps.model_dump()
    if gps_dict.get("timestamp") is None:
        gps_dict["timestamp"] = datetime.utcnow()
    result = await app.mongodb["gps"].insert_one(gps_dict)
    return {"id": str(result.inserted_id), "message": "GPS data created successfully"}


@app.get("/gps")
async def get_gps(user_id: Optional[str] = None, limit: int = 100):
    query = {}
    if user_id:
        query["user_id"] = user_id
    gps_data = await app.mongodb["gps"].find(query).to_list(limit)
    return [serialize_doc(g) for g in gps_data]


# ==================== DATA EXPORT PAGE ====================
@app.get("/export", response_class=HTMLResponse)
async def export_page():
    """
    Data export/download page for TAs to view and download all EmoGo data
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmoGo Data Export</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            .data-section {
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                margin: 5px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                cursor: pointer;
                border: none;
                font-size: 14px;
            }
            .btn:hover { background-color: #0056b3; }
            .btn-success { background-color: #28a745; }
            .btn-success:hover { background-color: #1e7e34; }
            pre {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                max-height: 400px;
                overflow-y: auto;
            }
            .loading { color: #666; font-style: italic; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>EmoGo Data Export</h1>
        <p>This page allows you to view and download all data collected by the EmoGo frontend.</p>

        <div class="data-section">
            <h2>1. Vlogs (Video Data)</h2>
            <p style="color: #666; font-size: 14px;">Contains video_url (local path on device) and description for each recorded vlog.</p>
            <button class="btn" onclick="loadData('vlogs')">Load Vlogs</button>
            <a class="btn btn-success" href="/vlogs" target="_blank">Download JSON</a>
            <div id="vlogs-data"><p class="loading">Click "Load Vlogs" to view data</p></div>
        </div>

        <div class="data-section">
            <h2>2. Sentiments</h2>
            <button class="btn" onclick="loadData('sentiments')">Load Sentiments</button>
            <a class="btn btn-success" href="/sentiments" target="_blank">Download JSON</a>
            <div id="sentiments-data"><p class="loading">Click "Load Sentiments" to view data</p></div>
        </div>

        <div class="data-section">
            <h2>3. GPS Coordinates</h2>
            <button class="btn" onclick="loadData('gps')">Load GPS</button>
            <a class="btn btn-success" href="/gps" target="_blank">Download JSON</a>
            <div id="gps-data"><p class="loading">Click "Load GPS" to view data</p></div>
        </div>

        <div class="data-section">
            <h2>API Documentation</h2>
            <p>For full API documentation, visit: <a href="/docs" target="_blank">/docs</a></p>
        </div>

        <script>
            async function loadData(type) {
                const container = document.getElementById(type + '-data');
                container.innerHTML = '<p class="loading">Loading...</p>';

                try {
                    const response = await fetch('/' + type);
                    const data = await response.json();

                    if (data.length === 0) {
                        container.innerHTML = '<p>No data available</p>';
                        return;
                    }

                    // Create table
                    let html = '<table><tr>';
                    const keys = Object.keys(data[0]);
                    keys.forEach(key => html += '<th>' + key + '</th>');
                    html += '</tr>';

                    data.forEach(item => {
                        html += '<tr>';
                        keys.forEach(key => {
                            let value = item[key];
                            if (typeof value === 'object') value = JSON.stringify(value);
                            // Show full video_url for vlogs
                            if (key === 'video_url' && value) {
                                html += '<td style="word-break: break-all; max-width: 300px;">' + value + '</td>';
                            } else if (value && value.length > 100) {
                                html += '<td>' + value.substring(0, 100) + '...</td>';
                            } else {
                                html += '<td>' + (value || '') + '</td>';
                            }
                        });
                        html += '</tr>';
                    });
                    html += '</table>';

                    container.innerHTML = html;
                } catch (error) {
                    container.innerHTML = '<p style="color: red;">Error loading data: ' + error.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ==================== DOWNLOAD ENDPOINTS (JSON format) ====================
@app.get("/export/vlogs")
async def export_vlogs():
    vlogs = await app.mongodb["vlogs"].find().to_list(1000)
    return JSONResponse(content=[serialize_doc(v) for v in vlogs])


@app.get("/export/sentiments")
async def export_sentiments():
    sentiments = await app.mongodb["sentiments"].find().to_list(1000)
    return JSONResponse(content=[serialize_doc(s) for s in sentiments])


@app.get("/export/gps")
async def export_gps():
    gps_data = await app.mongodb["gps"].find().to_list(1000)
    return JSONResponse(content=[serialize_doc(g) for g in gps_data])
