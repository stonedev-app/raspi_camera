#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF="$SCRIPT_DIR/sync.conf"

if [ ! -f "$CONF" ]; then
  echo "Error: sync.conf が見つかりません。sync.conf.example をコピーして編集してください。"
  exit 1
fi

source "$CONF"

EXCLUDE_OPTS=(
  --exclude '.git'
  --exclude '.gitignore'
  --exclude '.DS_Store'
  --exclude 'sync.conf'
  --exclude '__pycache__'
  --exclude '*.pyc'
  --exclude '.venv'
)

case "$1" in
  upload)
    rsync -avz --delete "${EXCLUDE_OPTS[@]}" "$SCRIPT_DIR/" "$RASPI_USER@$RASPI_HOST:$REMOTE_DIR/"
    ;;
  download)
    rsync -avz "$RASPI_USER@$RASPI_HOST:$REMOTE_DIR/" "$SCRIPT_DIR/"
    ;;
  *)
    echo "使い方: $0 {upload|download}"
    exit 1
    ;;
esac
