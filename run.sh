#!/bin/bash

# export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp/}rotostampa-pycache"

cd $(dirname "${BASH_SOURCE[0]}")

uv pip install .
.venv/bin/python -m switch "$@"