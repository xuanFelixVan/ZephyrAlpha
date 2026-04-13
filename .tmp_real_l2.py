import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.json').read_text(encoding='utf-8'))

print('Top-level keys:', list(d.keys()))
print()

links_stats = d.get('links', {}).get('stats', {})
print('links.stats:')
for k, v in links_stats.items():
    print(f'  {k}: {v}')

print()
print(f'ACTUAL broken links (links.stats.invalid): {links_stats.get("invalid", "N/A")}')
print(f'ACTUAL total md links (links.stats.total_md_links): {links_stats.get("total_md_links", "N/A")}')

# Also check if there are invalid details
invalid_sample = d.get('links', {}).get('invalid_details_sample', [])
truncated = d.get('links', {}).get('invalid_truncated', False)
print(f'invalid_details_sample count: {len(invalid_sample)}')
print(f'invalid_truncated: {truncated}')

if invalid_sample:
    print('\nFirst 5 invalid links:')
    for item in invalid_sample[:5]:
        print(f'  src: {item.get("source")}')
        print(f'  url: {item.get("url")}')
        print(f'  resolved: {item.get("resolved")}')
        print()
