"""
Thin re-export so Render's (and other PaaS) default start command —
`uvicorn main:app` run from the repo root — finds the app without needing a
custom Root Directory or Start Command setting. The real app lives in
src/main.py; everything (data path, .env path) is relative to that file's
own location, so loading it this way changes nothing about its behavior.
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("profilewatch_app", Path(__file__).resolve().parent / "src" / "main.py")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app
