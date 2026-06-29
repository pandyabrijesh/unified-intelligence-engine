#!/usr/bin/env bash
if [[ -z "${SENTIMENT_MODEL_NAME:-}" || "${SENTIMENT_MODEL_NAME}" == "xlm-roberta-base" ]]; then
  export SENTIMENT_MODEL_NAME=cardiffnlp/twitter-xlm-roberta-base-sentiment
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port 9000 --log-level info
