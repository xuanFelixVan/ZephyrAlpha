import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

REPO = Path('.')
triage = json.loads(Path('docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_20260413.json').read_text(encoding='utf-8'))

tier_a = [p for p in triage['records'] if p['triage_tier'] == 'TIER_A_AUTO']
print(f'TIER_A pairs: {len(tier_a)}')
print()

for i, p in enumerate(tier_a, 1):
    pa = Path(p['path_a'])
    pb = Path(p['path_b'])
    can = p['suggested_canonical']
    score = p['score']
    priority = p.get('second_pass_priority', '')
    ea = (REPO / pa).exists()
    eb = (REPO / pb).exists()
    
    a_is_arch = ('06_ARCHIVE' in str(pa) or 'overlap-' in pa.name or 'legacy' in pa.name)
    b_is_arch = ('06_ARCHIVE' in str(pb) or 'overlap-' in pb.name or 'legacy' in pb.name)
    
    if a_is_arch and not b_is_arch:
        action = f'DELETE A, KEEP B'
    elif b_is_arch and not a_is_arch:
        action = f'DELETE B, KEEP A'
    elif a_is_arch and b_is_arch:
        action = f'DELETE A (both archived, keep canonical)'
    else:
        action = f'STUB non-canonical'
    
    print(f'#{i:2d} score={score:.3f}  priority={priority}  action={action}')
    print(f'     A: exists={ea}  {str(pa)[:80]}')
    print(f'     B: exists={eb}  {str(pb)[:80]}')
    print()
