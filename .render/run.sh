#!/bin/bash

set -euo pipefail

/app/.venv/bin/siteplan manage collectstatic --no-input
/app/.venv/bin/siteplan run-gunicorn -b 0.0.0.0:8000 --serve-static
