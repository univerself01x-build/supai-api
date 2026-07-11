#!/usr/bin/env python3
"""Clean old citizen data: remove non-photographers, update schema fields"""
import json, sys
sys.path.insert(0, '.')
from engine import save_store, load_store

s = load_store()

# Remove non-photographer citizens
removed = []
for cid in list(s['citizens'].keys()):
    c = s['citizens'][cid]
    if c.get('platform') in ('feishu', 'weixin') and cid not in ('citizen_007',):
        del s['citizens'][cid]
        removed.append(f"{cid}:{c['name']}")
print(f"Removed: {removed}")

# Update remaining old citizens with new schema
for cid, updates in {
    'citizen_008': {'tier':'express','location':'上海','price_range':[1500,3000],
                    'equipment':['Sony A7M3'],'rating':4.3,'completed_tasks':18},
    'citizen_009': {'tier':'premier','location':'北京','price_range':[2000,4000],
                    'equipment':['Canon R6','DJI Ronin-S'],'rating':4.6,'completed_tasks':22},
    'citizen_007': {'tier':'pool','location':'上海','price_range':[800,1200],
                    'equipment':[],'rating':4.2,'completed_tasks':3},
}.items():
    if cid in s['citizens']:
        s['citizens'][cid].update(updates)

save_store(s)

# Verify
s2 = load_store()
total = len(s2['citizens'])
missing = sum(1 for c in s2['citizens'].values() if 'tier' not in c or 'location' not in c or 'price_range' not in c)
print(f"Citizens: {total} | Missing fields: {missing}")
for cid, c in s2['citizens'].items():
    print(f"  {cid}: {c['name']} | {c.get('tier','?')} | {c.get('location','?')} | ¥{c.get('price_range',[0,0])}")
