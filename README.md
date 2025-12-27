# Unified Intelligence Engine – 21 Features

This project is a **runnable demo** that implements all 21 high-level features we listed,
in a single reusable engine you can use as:
- a Python package (`from app.engine import UnifiedEngine`), and
- an HTTP API (`POST /v1/analyze`).

## Install

```bash
pip install -r requirements.txt
```

## Configure sentiment backbone (optional)

By default the engine will try to load `xlm-roberta-base`, which is NOT a sentiment model.
You should point it to your **fine-tuned sentiment model** (local path or HF Hub):

```bash
export SENTIMENT_MODEL_NAME=your-username/your-xlmroberta-sentiment-5class
```

or edit `SentimentAnalyzer` in `app/features/sentiment.py`.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open Swagger UI: http://127.0.0.1:8000/docs

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/v1/analyze"       -H "Content-Type: application/json"       -d '{
    "text": "Major road accident on SG Highway, traffic is stuck and people are angry.",
    "language": "auto",
    "source": "social",
    "domain": "incident",
    "metadata": {"id": "tweet_123"}
  }'
```

This will return a JSON with:
- sentiment (HF xlm-roberta-based)
- emotion
- toxicity
- intent
- topic
- incident
- simple NER + locations
- summary
- aspect sentiment
- similarity (placeholder)
- embeddings (hash-based demo)
- spam
- quality
- explainability
- confidence
- action recommendation
- metadata + model_info
