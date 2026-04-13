import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
from collections import Counter, defaultdict

REPO  = Path('.')
STATE = REPO / 'docs/09_AUDIT/STATE'

data    = json.loads((STATE / 'FIX_DEAD_LINKS_20260413.json').read_text(encoding='utf-8'))
details = data.get('details', [])

low = [d for d in details if d.get('confidence') == 'low' and d.get('action') == 'REPLACE']
print(f'Low-confidence REPLACE entries: {len(low)}')

# Pattern analysis: categorize by link type
categories = {
    'SITEMAP_link': [],
    'INDEX_to_INDEX': [],
    'blueprint_link': [],
    'same_basename_diff_dir': [],
    'other': [],
}
for d in low:
    url = d.get('url', '')
    new = d.get('new_url', '')
    tgt = d.get('resolved_target', '')
    src = d.get('source', '')
    
    url_base = url.split('/')[-1].lower()
    tgt_base = tgt.split('/')[-1].lower() if tgt else ''
    
    if 'sitemap' in url_base or 'sitemap' in tgt_base:
        categories['SITEMAP_link'].append(d)
    elif url_base in ('index.md', 'readme.md') and tgt_base in ('index.md', 'readme.md'):
        categories['INDEX_to_INDEX'].append(d)
    elif 'blueprint' in url_base or 'blueprint' in tgt_base:
        categories['blueprint_link'].append(d)
    elif url_base == tgt_base:
        categories['same_basename_diff_dir'].append(d)
    else:
        categories['other'].append(d)

print('\nCategory distribution:')
for cat, items in categories.items():
    print(f'  {len(items):4d}  {cat}')

# Sample 5 per category
print('\n' + '='*80)
print('REPRESENTATIVE SAMPLES (5 per category)')
print('='*80)

for cat, items in categories.items():
    if not items:
        continue
    print(f'\n--- {cat.upper()} ({len(items)} total) ---')
    for d in items[:5]:
        src = d['source'].replace('\\','/')
        url = d['url']
        new = d['new_url']
        tgt = d['resolved_target']
        print(f'  SRC: {src[-65:]}')
        print(f'  OLD: {url}')
        print(f'  NEW: {new}')
        print(f'  TGT: {tgt}')
        # Quick judgement hint
        url_base = url.split('/')[-1]
        tgt_base = tgt.split('/')[-1] if tgt else ''
        ok = url_base.lower() == tgt_base.lower()
        print(f'  --> basename_match={ok}  {"[LIKELY OK]" if ok else "[CHECK NEEDED]"}')
        print()

# Summary judgement
print('='*80)
print('OVERALL ASSESSMENT:')
total = len(low)
ok_count = sum(1 for d in low if d['url'].split('/')[-1].lower() == (d['resolved_target'] or '').split('/')[-1].lower())
suspicious = total - ok_count
print(f'  Total low-confidence  : {total}')
print(f'  basename matches      : {ok_count} ({100*ok_count//total}%)')
print(f'  basename mismatch     : {suspicious} ({100*suspicious//total}%)')
print()
print('Basename-mismatch samples (up to 10):')
mismatch = [d for d in low if d['url'].split('/')[-1].lower() != (d['resolved_target'] or '').split('/')[-1].lower()]
for d in mismatch[:10]:
    print(f'  OLD: {d["url"][:60]}  -->  NEW tgt: {d["resolved_target"][:60]}')
