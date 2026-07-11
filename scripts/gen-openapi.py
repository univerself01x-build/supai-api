#!/usr/bin/env python3
"""导出 OpenAPI spec → web/src/lib/openapi.json"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from server import app

spec = app.openapi()
out = Path(__file__).parent.parent / "web" / "src" / "lib" / "openapi.json"
out.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
print(f"openapi.json → {out} ({len(spec['paths'])} endpoints)")
