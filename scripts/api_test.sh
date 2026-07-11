#!/bin/bash
# 速派 API 冒烟测试
# 先启动: python3 server.py 8081 &
BASE="http://localhost:8081/api"
PASS=0
FAIL=0

check() {
    local name="$1" method="$2" url="$3" data="$4" expected="$5"
    if [ -n "$data" ]; then
        resp=$(curl -s -X "$method" "$url" -H "Content-Type: application/json" -d "$data" 2>/dev/null)
    else
        resp=$(curl -s -X "$method" "$url" 2>/dev/null)
    fi
    if echo "$resp" | python3 -c "$expected" 2>/dev/null; then
        echo "  PASS $name"
        PASS=$((PASS+1))
    else
        echo "  FAIL $name — $resp" | head -c 120
        echo
        FAIL=$((FAIL+1))
    fi
}

echo "=== API 冒烟测试 ==="

# 1. Status
check "GET /api/status" GET "$BASE/status" "" "import sys,json; d=json.load(sys.stdin); assert d['status']=='ok'"

# 2. Project list
check "GET /api/projects" GET "$BASE/projects" "" "import sys,json; d=json.load(sys.stdin); assert 'human' in d; assert isinstance(d['human'],list)"

# 3. Project detail
check "GET /api/projects/task_003" GET "$BASE/projects/task_003" "" "import sys,json; d=json.load(sys.stdin); h=d['human']; assert h['title']=='发布会拍摄'"

# 4. Project 404
check "GET /api/projects/nonexist" GET "$BASE/projects/nonexist" "" "import sys,json; d=json.load(sys.stdin); assert 'error' in d"

# 5. Match
check "POST /api/match (enterprise)" POST "$BASE/match" '{"scene":"AI产品发布会","budget":8000}' "import sys,json; d=json.load(sys.stdin); h=d['human']; assert h['tier']=='enterprise'; assert len(h['recommendedTeam'])>0"

# 6. Match (pool)
check "POST /api/match (pool)" POST "$BASE/match" '{"scene":"生日派对跟拍","budget":800}' "import sys,json; d=json.load(sys.stdin); h=d['human']; assert h['tier'] in ('pool','express')"

# 7. Match (missing budget)
check "POST /api/match (no budget)" POST "$BASE/match" '{"scene":"产品拍摄"}' "import sys,json; d=json.load(sys.stdin); h=d['human']; assert len(h.get('recommendedTeam',[]))>=0"

echo ""
echo "Result: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ] && echo "ALL PASS" || echo "FAILURES DETECTED"
exit $FAIL
