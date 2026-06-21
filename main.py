from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import pandas as pd
import os
import shutil
import uuid

from database import init_db, save_session, get_sessions, save_history, get_history
from analysis import load_dataframe, get_full_stats, clean_dataframe, get_correlation_matrix, get_outliers, run_statistical_tests
from charts import bar_chart, line_chart, scatter_chart, histogram, pie_chart, correlation_heatmap
from reports import generate_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://localhost:3001", "http://localhost:3003", "http://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store dataframes in memory per session
dataframes = {}

class StatTestRequest(BaseModel):
    session_id: str
    col1: str
    col2: str

from typing import Optional

class ChartRequest(BaseModel):
    session_id: str
    chart_type: str
    x_col: Optional[str] = None
    y_col: Optional[str] = None
    title: str = ""
    
class HistoryRequest(BaseModel):
    session_id: str
    question: str
    answer: str

class ReportRequest(BaseModel):
    session_id: str
    file_name: str
    stats: dict
    insights: str
    history: list

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        session_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df = load_dataframe(file_path, file.filename)
        dataframes[session_id] = df

        stats = get_full_stats(df)
        db_session_id = save_session(file.filename, stats["rowCount"], stats["columnCount"])

        return {
            "session_id": session_id,
            "db_session_id": db_session_id,
            "file_name": file.filename,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/clean")
async def clean_file(body: dict):
    session_id = body.get("session_id")
    if session_id not in dataframes:
        raise HTTPException(status_code=404, detail="Session not found")

    df = dataframes[session_id]
    cleaned_df, report = clean_dataframe(df)
    dataframes[session_id] = cleaned_df
    stats = get_full_stats(cleaned_df)

    return {"report": report, "stats": stats}

@app.post("/chart")
async def generate_chart(body: ChartRequest):
    print(f"Chart request received: {body}")
    if body.session_id not in dataframes:
        print(f"Session {body.session_id} not found. Available: {list(dataframes.keys())}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    df = dataframes[body.session_id]

    try:
        if body.chart_type == "bar":
            img = bar_chart(df, body.x_col, body.y_col, body.title)
        elif body.chart_type == "line":
            img = line_chart(df, body.x_col, body.y_col, body.title)
        elif body.chart_type == "scatter":
            img = scatter_chart(df, body.x_col, body.y_col, body.title)
        elif body.chart_type == "histogram":
            img = histogram(df, body.x_col, body.title)
        elif body.chart_type == "pie":
            img = pie_chart(df, body.x_col, body.title)
        elif body.chart_type == "heatmap":
            img = correlation_heatmap(df)
        else:
            raise HTTPException(status_code=400, detail="Unknown chart type")

        return {"image": img}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stats/correlation")
async def get_correlation(body: dict):
    session_id = body.get("session_id")
    if session_id not in dataframes:
        raise HTTPException(status_code=404, detail="Session not found")

    df = dataframes[session_id]
    return {"correlation": get_correlation_matrix(df)}

@app.post("/stats/outliers")
async def get_outliers_route(body: dict):
    session_id = body.get("session_id")
    if session_id not in dataframes:
        raise HTTPException(status_code=404, detail="Session not found")

    df = dataframes[session_id]
    return {"outliers": get_outliers(df)}

@app.post("/stats/test")
async def statistical_test(body: StatTestRequest):
    if body.session_id not in dataframes:
        raise HTTPException(status_code=404, detail="Session not found")

    df = dataframes[body.session_id]
    result = run_statistical_tests(df, body.col1, body.col2)
    return result

@app.post("/history/save")
async def save_history_route(body: HistoryRequest):
    save_history(body.session_id, body.question, body.answer)
    return {"success": True}

@app.get("/history/{session_id}")
async def get_history_route(session_id: int):
    return {"history": get_history(session_id)}

@app.get("/sessions")
async def get_sessions_route():
    return {"sessions": get_sessions()}

@app.post("/report")
async def generate_report_route(body: ReportRequest):
    if body.session_id not in dataframes:
        raise HTTPException(status_code=404, detail="Session not found")

    df = dataframes[body.session_id]
    pdf_bytes = generate_report(
        body.file_name,
        body.stats,
        body.insights,
        body.history,
        df
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={body.file_name}-report.pdf"}
    )

@app.get("/")
def root():
    return {"status": "AI Data Analysis Backend running"}