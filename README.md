# Unified Text Intelligence Engine (Multi-Feature NLP Service)

This project is a **unified text intelligence engine** that you can reuse across all your apps
(Product reviews, YouTube transcripts, e-newspapers, Social media, etc.).

It wraps multiple features into **one standardized API**:

- Sentiment (3 or 5 class, HuggingFace)
- Emotion
- Toxicity / Hate
- Intent
- Topic
- Incident detection
- NER-lite
- Location resolution
- Summary
- Aspect sentiment
- Similarity
- Embeddings
- Spam detection
- Text quality scoring
- Explainability
- Confidence scoring
- Action recommendation
- Standard metadata + model info

---

## 1. Running Locally

### 1.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.2 Set HuggingFace Sentiment Model

Example multilingual sentiment model:

```bash
export SENTIMENT_MODEL_NAME=cardiffnlp/twitter-xlm-roberta-base-sentiment
```

Or use your fine‑tuned local model:

```bash
export SENTIMENT_MODEL_NAME=/path/to/gu_en_sentiment_model
```

### 1.3 Run FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

### 1.4 Test API

```bash
curl http://localhost:9000/healthz
```

---

## 2. Running with Podman / Docker

### 2.1 Build Container

```bash
podman build -t unified-intel-engine:latest .
```

### 2.2 Run on Alternative Host Port (recommended)

```bash
podman run --rm     -e SENTIMENT_MODEL_NAME=cardiffnlp/twitter-xlm-roberta-base-sentiment     -p 9100:9000     unified-intel-engine:latest
```

Now access:

- http://localhost:9100/docs
- http://localhost:9100/healthz

### 2.3 Run with Local Model Mounted

```bash
podman run --rm     -e SENTIMENT_MODEL_NAME=/models/gu_en_sentiment     -v /Users/brijesh/models:/models:z     -p 9100:9000     unified-intel-engine:latest
```

---

## 3. Use as a Python Package

### 3.1 Install Package in Editable Mode

```bash
pip install -e .
```

### 3.2 Example Usage

```python
from app import UnifiedEngine
from app.schemas import AnalyzeRequest

engine = UnifiedEngine()

req = AnalyzeRequest(
    text="આ સેવા બહુ ઉત્તમ હતી અને મને ખુબ આનંદ આવ્યો.",
    language="auto",
    source="product",
    domain="product"
)

resp = engine.analyze(req)
print(resp.sentiment, resp.action)
```

---

## 4. API Endpoints

### **POST /v1/analyze**

Analyze text with full 21-feature pipeline.

### **GET /healthz**

Healthcheck endpoint.

---

## 5. Example Request

```bash
curl -X POST "http://localhost:9100/v1/analyze"   -H "Content-Type: application/json"   -d '{
    "text": "Major accident on SG Highway, people are angry.",
    "language": "auto",
    "source": "social",
    "domain": "incident",
    "metadata": {"id": "tweet_123"}
  }'
```

---

## 6. Dockerfile (Already Included)

The Dockerfile in this project builds a production-ready API server using Python 3.11 slim.

---

## 7. Summary

This engine can function as:

- A **local Python library**
- A **standalone API microservice**
- A **container deployed on Podman/Docker/Kubernetes**

All apps you develop can use this same unified intelligence core.

---
