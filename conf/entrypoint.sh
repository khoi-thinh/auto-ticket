#!/bin/bash
# parameter expansion, "use the value of PORT if it exists, otherwise use 8080"
export RUNTIME_PORT=${PORT:-8080}
/opt/venv/bin/gunicorn --worker-class uvicorn.workers.UvicornWorker main:app --bind "0.0.0.0:$RUNTIME_PORT"
