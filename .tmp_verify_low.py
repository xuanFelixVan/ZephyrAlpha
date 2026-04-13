import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

REPO  = Path('.')
STATE = REPO / 'docs/09_AUDIT/STATE'

data    = json.loads((STATE / 'FIX_DEAD_LINKS_20260413.json').read_text(encoding='utf-8'))
details = data.get('details', [])

low    = [d for d in details if d.get('confidence') == 'low'    and d.get('action') == 'REPLACE']
hi_med = {(d['source'], d['url']) for d in details if d.get('confidence') in ('high','medium') and d.get('action') == 'REPLACE'}

# How many low-conf entries were ALSO fixed by a high/medium entry (same source+url)?
overlap = [(d['source'], d['url']) for d in low if (d['source'], d['url']) in hi_med]
only_low = [d for d in low if (d['source'], d['url']) not in hi_med]

print(f'Total low-confidence       : {len(low)}')
print(f'Also in high/medium (stale): {len(overlap)}  ({100*len(overlap)//len(low)}%)')
print(f'Only in low (truly skipped): {len(only_low)}  ({100*len(only_low)//len(low) if low else 0}%)')
print()

# Spot-check: do the "only_low" targets actually exist NOW?
print('Checking if "only_low" targets exist on disk (sampling 20):')
exists_cnt = 0
missing_cnt = 0
for d in only_low[:20]:
    tgt = d.get('resolved_target', '')  # target of NEW url
    # Actually we need to check if the OLD broken link target still exists
    # The OLD url resolved to TGT, which was broken. 
    # But after Phase 3.1a, the MEDIUM fix for the same file might have changed the link text.
    
    # Check if the OLD url still exists literally in the source file
    src_path = REPO / d['source']
    old_url  = d['url']
    if src_path.exists():
        content = src_path.read_text(encoding='utf-8', errors='ignore')
        if old_url in content:
            missing_cnt += 1
            print(f'  STILL BROKEN: {d["source"][-50:]} -> {old_url}  (target: {tgt})')
        else:
            exists_cnt += 1
            # print(f'  ALREADY FIXED: {d["source"][-50:]} -> {old_url}')
    else:
        print(f'  SOURCE GONE: {d["source"]}')

print(f'\nOf sampled 20 "only_low":')
print(f'  Old url still in file (actually broken): {missing_cnt}')
print(f'  Old url gone from file (already fixed) : {exists_cnt}')
print()

# Full count for all only_low
print('Full count for ALL only_low entries:')
still_broken = 0
already_fixed = 0
source_gone = 0
for d in only_low:
    src_path = REPO / d['source']
    old_url  = d['url']
    if not src_path.exists():
        source_gone += 1
    elif old_url in src_path.read_text(encoding='utf-8', errors='ignore'):
        still_broken += 1
    else:
        already_fixed += 1

print(f'  Still broken (url in file) : {still_broken}')
print(f'  Already fixed (url gone)   : {already_fixed}')
print(f'  Source file gone           : {source_gone}')
print(f'  Total                      : {still_broken + already_fixed + source_gone}')
