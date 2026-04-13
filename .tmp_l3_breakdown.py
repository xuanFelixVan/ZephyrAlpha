import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
from collections import Counter

REPO  = Path('.')
d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json').read_text(encoding='utf-8'))
invalid = d['links']['invalid_details_sample']

print(f'Remaining invalid links: {len(invalid)}')
print()

# Check fix report - how many are REMOVE_LINK candidates
fix_data = json.loads(Path('docs/09_AUDIT/STATE/FIX_DEAD_LINKS_20260413.json').read_text(encoding='utf-8'))
remove_candidates = [d2 for d2 in fix_data.get('details',[]) if d2.get('action') == 'REMOVE_LINK']
print(f'REMOVE_LINK candidates in fix report: {len(remove_candidates)}')

prefixes = Counter()
for item in invalid:
    src = item['source'].replace('\\','/')
    parts = src.split('/')
    if src.startswith('docs/'):
        prefixes['/'.join(parts[:3]) + '/'] += 1
    else:
        prefixes[parts[0] + '/'] += 1

print('\nSource breakdown (remaining invalid):')
for p, cnt in prefixes.most_common(15):
    print(f'  {cnt:4d}  {p}')

# Sample 10 from top source
top_src_prefix = prefixes.most_common(1)[0][0].rstrip('/')
top_src = [i for i in invalid if i['source'].replace('\\','/').startswith(top_src_prefix)]
print(f'\nSample from top source ({top_src_prefix}):')
for item in top_src[:5]:
    print(f'  src: {item["source"][-60:]}')
    print(f'  url: {item["url"]}')
    print(f'  res: {item["resolved"]}')
    print()

# Are any fixable?
replace_cnt = len([d2 for d2 in fix_data.get('details',[]) if d2.get('action') == 'REPLACE'])
print(f'Fixable (REPLACE) in current fix report: {replace_cnt}')
print(f'Unfixable (REMOVE_LINK) in current fix report: {len(remove_candidates)}')
