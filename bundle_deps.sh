#!/bin/bash
# Installs addon dependencies into addon/external/ for Anki addon packaging.
# Anki bundles its own Python, so dependencies not included in Anki must be vendored here.
# requests is excluded — Anki already bundles it.
set -e
uv pip install --target=addon/external genanki
uv pip install --target=addon/external google
uv pip install --target=addon/external google-genai
uv pip install --target=addon/external sqlalchemy
uv pip install --target=addon/external elevenlabs
echo "Done. Commit addon/external/ to include in addon distribution."
