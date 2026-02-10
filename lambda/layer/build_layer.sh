#!/usr/bin/env bash
set -euo pipefail

PYVER=3.12
WORKDIR="$(pwd)/layer_build"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/python"

python${PYVER} -m venv "$WORKDIR/venv"
source "$WORKDIR/venv/bin/activate"
pip install --upgrade pip
pip install pynacl

# Install into layer folder
pip install --target "$WORKDIR/python" pynacl

cd "$WORKDIR"
zip -r ../pynacl_layer.zip python
echo "Created pynacl_layer.zip"
