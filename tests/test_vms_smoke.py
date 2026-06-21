# [A_test] module_id: SRC-TST-1797 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-443 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_vms_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
import sys, tempfile, warnings
sys.path.insert(0,'src')
from pathlib import Path
from zephyr.governance.vector_memory.in_process_vector_memory import InProcessVectorMemory

vms = InProcessVectorMemory(persist_dir=Path(tempfile.mkdtemp()) / 'vms_test')
print('[1] init OK')
vms.start()
print('[2] start OK')
infos = vms.init_all_collections()
print(f'[3] init_all_collections OK ({len(infos)} collections)')

for info in infos:
    print(f'    {info.name}: dim={info.dimension}, exists={info.exists}')

vid = vms.write('decisions', 'fix database connection leak', {'source': 'smoke_test', 'provenance': {'origin': 'smoke_test', 'source': 'manual'}})
print(f'[4] write OK, vector_id={vid}')

results = vms.search('decisions', 'database connection', k=3)
print(f'[5] search OK, {len(results)} results')
for r in results:
    print(f'    id={r["id"]} score={r["score"]:.4f}')

recalled = vms.recall('decisions', k=3)
print(f'[6] recall OK, {len(recalled)} records')

hc = vms.health_check()
print(f'[7] health={hc["status"]}')

vms.clear_all()
print('[8] clear_all OK')
vms.shutdown()
print('[9] shutdown OK')
print('=== ALL SMOKE TESTS PASSED ===')