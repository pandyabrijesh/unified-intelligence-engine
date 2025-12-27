from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AnalyzeRequest, AnalyzeResponse
from .engine import UnifiedEngine

app = FastAPI(
    title="Unified Intelligence Engine (21 features)",
    version="0.1.0",
    description=(
        "Reusable engine for multilingual sentiment + incident + topic + toxicity + "
        "extraction and action recommendation across all your apps."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = UnifiedEngine()


@app.post("/v1/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    return engine.analyze(req)


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok"}
