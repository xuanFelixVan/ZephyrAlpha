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

# Strategy distribution
strats = Counter(d.get('strategy','?') for d in low)
print('\nStrategy distribution:')
for s, n in strats.most_common():
    print(f'  {n:5d}  {s}')

# Source prefix distribution
src_prefixes = Counter()
for d in low:
    parts = d['source'].replace('\\','/').split('/')
    src_prefixes['/'.join(parts[:3])] += 1
print('\nTop source prefixes:')
for p, n in src_prefixes.most_common(10):
    print(f'  {n:4d}  {p}')

# Sample 60 entries: 20 per source bucket
print('\n' + '='*80)
print('SAMPLE (up to 60 entries, diverse sources)')
print('='*80)

sampled = []
per_source = defaultdict(list)
for d in low:
    parts = d['source'].replace('\\','/').split('/')
    key = '/'.join(parts[:3])
    per_source[key].append(d)

# Take up to 5 per source group, sorted by source
for key in sorted(per_source.keys()):
    for d in per_source[key][:5]:
        sampled.append(d)
        if len(sampled) >= 60:
            break
    if len(sampled) >= 60:
        break

for i, d in enumerate(sampled, 1):
    src    = d.get('source', '').replace('\\','/')[-60:]
    old    = d.get('original_link', '').replace('\\','/')[-60:]
    new    = d.get('suggested_link', '').replace('\\','/')[-60:]
    strat  = d.get('strategy', '')[-30:]
    print(f'\n#{i:3d}  src  : ...{src}')
    print(f'      old  : {old}')
    print(f'      new  : {new}')
    print(f'      strat: {strat}')
