#!/bin/bash
# SSOT 自动化：FastAPI → OpenAPI JSON → TypeScript 类型
# 改 api_models.py 后跑: bash scripts/gen_openapi.sh
set -e

echo "→ 导出 OpenAPI JSON..."
curl -s http://localhost:8080/openapi.json > docs/openapi.json
echo "  docs/openapi.json ($(wc -c < docs/openapi.json) bytes)"

echo "→ 生成 TypeScript 类型..."
cd web && npx openapi-typescript ../docs/openapi.json -o src/api.generated.ts 2>/dev/null
echo "  web/src/api.generated.ts done"

echo "✅ SSOT 同步完成"
