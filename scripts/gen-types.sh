#!/bin/bash
# SSOT Pipeline — 从 api_models.py → OpenAPI → TypeScript 类型
# 用法: bash scripts/gen-types.sh
# 改 api_models.py 后跑一遍，前端类型自动同步

set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEB_DIR="$DIR/web"

echo "→ 启动 API Server 导出 OpenAPI spec..."
cd "$DIR"

# 先杀掉旧进程
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# 启动 server，等它就绪
python3 server.py &
SERVER_PID=$!
sleep 2

# 导出 openapi.json
curl -s http://localhost:8080/openapi.json > "$WEB_DIR/src/lib/openapi.json"
echo "  ✓ openapi.json ($(wc -c < "$WEB_DIR/src/lib/openapi.json") bytes)"

# 生成 TypeScript 类型
cd "$WEB_DIR"
npx openapi-typescript src/lib/openapi.json -o src/lib/api.generated.ts 2>&1 | grep -v "^$"
echo "  ✓ api.generated.ts"

# 关停临时 server
kill $SERVER_PID 2>/dev/null
echo "→ 完成。TypeScript 类型已同步。"
