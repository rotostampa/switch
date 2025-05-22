#!/bin/bash

# export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp/}rotostampa-pycache"

uv run                                            \
    --directory "$(dirname "${BASH_SOURCE[0]}")"  \
    --isolated --exact --no-env-file --no-project \
    --link-mode hardlink --no-config              \
    --with-requirements requirements.txt          \
    --with-requirements requirements-dev.txt      \
    --python 3.13.3                               \
    --python-preference only-managed              \
    --module switch "$@"