#!/usr/bin/env bash
#

set -eo pipefail

case "${1}" in
  backend)
    echo "Starting Backend..."
    fastapi dev server/main.py --port 8080 --host 0.0.0.0
    ;;
  frontend)
    echo "Starting Frontend..."
    streamlit run streamlit/Main.py --server.port=8501 --server.address=0.0.0.0
    ;;
  *)
    echo "Unknown Operation!!!"
    ;;
esac
