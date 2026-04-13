import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json').read_text(encoding='utf-8'))
invalid = d['links']['invalid_details_sample']
print(f'Remaining: {len(invalid)}')
for item in invalid:
    print(f'  src: {item["source"]}')
    print(f'  url: {item["url"]}')
    print(f'  res: {item["resolved"]}')
    print()
