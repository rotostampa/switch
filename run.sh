#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="$SCRIPT_DIR"

uv run                                            \
    --directory "$SCRIPT_DIR"                      \
    --exact --no-env-file                         \
    --no-config                                   \
    --python-preference only-managed              \
    --module switch "$@"
