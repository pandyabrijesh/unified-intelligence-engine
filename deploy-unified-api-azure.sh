#!/usr/bin/env bash
set -euo pipefail

VM_USER="${VM_USER:-azureuser}"
VM_HOST="${VM_HOST:-20.106.187.193}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/OmniMonitorPOC.pem}"
REMOTE_DIR="${REMOTE_DIR:-/opt/unified-intelligence-engine/api}"
APP_PORT="${APP_PORT:-9000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LOCAL_ENV_FILE="${LOCAL_ENV_FILE:-.env}"
UPLOAD_ENV="${UPLOAD_ENV:-1}"

REMOTE_TARGET="$VM_USER@$VM_HOST"
SSH_OPTS=(-i "$SSH_KEY" -o StrictHostKeyChecking=accept-new)
RSYNC_SSH="ssh -i $SSH_KEY -o StrictHostKeyChecking=accept-new"

echo "Deploying Unified Intelligence Engine API to Azure VM..."
echo "Remote: $REMOTE_TARGET:$REMOTE_DIR"
echo "Port:   $APP_PORT"

if [ ! -d "app" ] || [ ! -f "requirements.txt" ]; then
  echo "ERROR: Run this script from the folder containing app/ and requirements.txt"
  exit 1
fi

if [ ! -f "$SSH_KEY" ]; then
  echo "ERROR: SSH key not found: $SSH_KEY"
  exit 1
fi

if [ "$UPLOAD_ENV" = "1" ] && [ ! -f "$LOCAL_ENV_FILE" ]; then
  echo "ERROR: $LOCAL_ENV_FILE not found. Set UPLOAD_ENV=0 to deploy without copying .env."
  exit 1
fi

chmod 600 "$SSH_KEY"

echo "Creating remote folder..."
ssh "${SSH_OPTS[@]}" "$REMOTE_TARGET" "REMOTE_DIR='$REMOTE_DIR' VM_USER='$VM_USER' bash -s" <<'REMOTE_EOF'
set -euo pipefail

if mkdir -p "$REMOTE_DIR" 2>/dev/null; then
  :
elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  sudo -n mkdir -p "$REMOTE_DIR"
  sudo -n chown -R "$VM_USER:$VM_USER" "$REMOTE_DIR"
else
  echo "ERROR: Cannot create $REMOTE_DIR and sudo is not available."
  echo "Use a writable folder, for example: REMOTE_DIR=\$HOME/unified-intelligence-engine/api"
  exit 1
fi

if [ ! -w "$REMOTE_DIR" ]; then
  if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
    sudo -n chown -R "$VM_USER:$VM_USER" "$REMOTE_DIR"
  fi
fi

if [ ! -w "$REMOTE_DIR" ]; then
  echo "ERROR: $REMOTE_DIR is not writable by $VM_USER"
  exit 1
fi
REMOTE_EOF

echo "Uploading API files..."
rsync -az --delete \
  -e "$RSYNC_SSH" \
  --exclude ".git/" \
  --exclude ".DS_Store" \
  --exclude ".env" \
  --exclude ".venv/" \
  --exclude "__pycache__/" \
  --exclude ".pytest_cache/" \
  --exclude ".mypy_cache/" \
  --exclude "*.pyc" \
  --exclude "*.zip" \
  --exclude "app.log" \
  --exclude "app.pid" \
  ./ "$REMOTE_TARGET:$REMOTE_DIR/"

if [ "$UPLOAD_ENV" = "1" ]; then
  echo "Uploading .env securely..."
  scp "${SSH_OPTS[@]}" "$LOCAL_ENV_FILE" "$REMOTE_TARGET:$REMOTE_DIR/.env"
  ssh "${SSH_OPTS[@]}" "$REMOTE_TARGET" "chmod 600 '$REMOTE_DIR/.env'"
fi

echo "Installing dependencies and restarting API..."
ssh "${SSH_OPTS[@]}" "$REMOTE_TARGET" "REMOTE_DIR='$REMOTE_DIR' APP_PORT='$APP_PORT' PYTHON_BIN='$PYTHON_BIN' bash -s" <<'REMOTE_EOF'
set -euo pipefail

cd "$REMOTE_DIR"

echo "Ensuring Python virtual environment..."
if [ ! -d ".venv" ]; then
  if ! "$PYTHON_BIN" -m venv .venv; then
    if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null && command -v apt-get >/dev/null 2>&1; then
      echo "Installing python3-venv and build tools..."
      sudo -n apt-get update
      sudo -n apt-get install -y python3-venv python3-pip build-essential
      "$PYTHON_BIN" -m venv .venv
    else
      echo "ERROR: Could not create virtual environment. Install python3-venv on the VM."
      exit 1
    fi
  fi
fi

. .venv/bin/activate

echo "Installing Python packages..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Stopping old API process..."
if [ -f app.pid ]; then
  old_pid="$(cat app.pid || true)"
  if [ -n "$old_pid" ]; then
    kill "$old_pid" 2>/dev/null || true
  fi
  rm -f app.pid
fi

pkill -f "$REMOTE_DIR/.venv/bin/uvicorn app.main:app" || true
sleep 2

echo "Starting API..."
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$APP_PORT" > app.log 2>&1 &
echo "$!" > app.pid

health_check() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsS "http://127.0.0.1:$APP_PORT/healthz" >/dev/null
  else
    python - "$APP_PORT" <<'PY'
import sys
import urllib.request

port = sys.argv[1]
urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=5).read()
PY
  fi
}

echo "Waiting for API health check..."
healthy=0
for attempt in {1..60}; do
  if health_check; then
    healthy=1
    break
  fi
  sleep 2
done

if [ "$healthy" != "1" ]; then
  echo "ERROR: API did not become healthy on port $APP_PORT"
  echo "Recent logs:"
  tail -120 app.log || true
  exit 1
fi

echo "API is healthy."
echo "Running ports:"
ss -tulpn 2>/dev/null | grep -E ":$APP_PORT\b" || true

echo "Recent logs:"
tail -60 app.log || true
REMOTE_EOF

echo ""
echo "Deployment completed."
echo "API health: http://$VM_HOST:$APP_PORT/healthz"
echo "API docs:   http://$VM_HOST:$APP_PORT/docs"
echo ""
echo "If the public URLs do not open, allow TCP port $APP_PORT in the VM NSG/firewall."
