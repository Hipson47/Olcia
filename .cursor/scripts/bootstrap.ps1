param()
if (-not (Test-Path .venv)) { py -3.11 -m venv .venv }
. .venv/Scripts/Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt -q 2>$null || $true
pip install python-dotenv chromadb sentence-transformers -q
python - << 'PY'
from pathlib import Path; from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[2]; load_dotenv(ROOT/'.env'); print('BOOTSTRAP_OK')
PY