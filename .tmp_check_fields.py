import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

data    = json.loads(Path('docs/09_AUDIT/STATE/FIX_DEAD_LINKS_20260413.json').read_text(encoding='utf-8'))
details = data.get('details', [])
low     = [d for d in details if d.get('confidence') == 'low' and d.get('action') == 'REPLACE']

print(f'Total low-confidence: {len(low)}')
print()
print('Keys of first record:')
print(list(low[0].keys()))
print()
print('First record:')
for k, v in low[0].items():
    print(f'  {k}: {repr(str(v)[:100])}')
