#!/usr/bin/env python3
"""Preflight: validate store.json data quality"""
import json, sys

s = json.loads(open("data/store.json").read())
citizens = s["citizens"]
total = len(citizens)

checks = []

# 1. Count
checks.append(("Total", total, f"{total} citizens"))

# 2. Unique platform_ids
ids = [c.get("platform_id","") for c in citizens.values()]
dupes = len(ids) - len(set(ids))
checks.append(("Unique IDs", dupes == 0, f"{dupes} dupes" if dupes else "all unique"))

# 3. Required fields
missing = []
for cid, c in citizens.items():
    for f in ["name","platform_id","skills","location","languages","tier","rating","completed_tasks","price_range","equipment"]:
        if f not in c:
            missing.append(f"{cid}.{f}")
checks.append(("Fields", not missing, f"{len(missing)} missing" if missing else "all present"))

# 4. Skills
bad = [cid for cid,c in citizens.items() if not c.get("skills") or not isinstance(c["skills"],list)]
checks.append(("Skills list", not bad, str(bad) if bad else "ok"))

# 5. Rating
bad_r = [cid for cid,c in citizens.items() if c.get("rating",0)<4.0 or c.get("rating",0)>5.0]
checks.append(("Rating", not bad_r, str(bad_r) if bad_r else "all 4.0-5.0"))

# 6. Tiers
tiers = {}
for c in citizens.values():
    t = c.get("tier","MISSING")
    tiers[t] = tiers.get(t,0)+1
checks.append(("Tiers", tiers.get("enterprise",0)>=2 and tiers.get("premier",0)>=4 and tiers.get("express",0)>=6 and tiers.get("pool",0)>=4, str(tiers)))

# 7. Location
locs = {}
for c in citizens.values():
    locs[c.get("location","?")] = locs.get(c.get("location","?"),0)+1
sh = locs.get("上海",0)
checks.append(("Shanghai%", sh/total >= 0.6, f"{sh/total*100:.0f}% Shanghai"))

# 8. Price
bad_p = [cid for cid,c in citizens.items() if len(c.get("price_range",[]))!=2]
checks.append(("Price range", not bad_p, str(bad_p) if bad_p else "ok"))

for name, ok, detail in checks:
    mark = "PASS" if ok else "FAIL"
    print(f"  {mark} {name}: {detail}")

passed = sum(1 for _,ok,_ in checks if ok)
print(f"\n{passed}/{len(checks)} checks passed")
sys.exit(0 if passed == len(checks) else 1)
