# [A_test] module_id: SRC-TST-1797 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-443 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_vms_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import sys
import tempfile

sys.path.insert(0, "src")
from pathlib import Path

from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

def test_vms_smoke():
    """VMS 端到端冒烟测试——所有逻辑在函数内，模块级零副作用。"""
    vms = InProcessVectorMemory(persist_dir=Path(tempfile.mkdtemp()) / "vms_test")
    print("[1] init OK")
    vms.start()
    print("[2] start OK")
    infos = vms.init_all_collections()
    print(f"[3] init_all_collections OK ({len(infos)} collections)")

    for info in infos:
        print(f"    {info.name}: dim={info.dimension}, exists={info.exists}")

    vid = vms.write(
        "decisions",
        "fix database connection leak",
        {"source": "smoke_test", "provenance": {"origin": "smoke_test", "source": "manual"}},
    )
    print(f"[4] write OK, vector_id={vid}")

    results = vms.search("decisions", "database connection", k=3)
    print(f"[5] search OK, {len(results)} results")
    for r in results:
        # 降级检索路径返回的字典可能无 'score' 键，用 get 防御
        print(f"    id={r['id']} score={r.get('score', 0.0):.4f}")

    recalled = vms.recall("decisions", k=3)
    print(f"[6] recall OK, {len(recalled)} records")

    hc = vms.health_check()
    print(f"[7] health={hc['status']}")

    vms.clear_all()
    print("[8] clear_all OK")
    vms.shutdown()
    print("[9] shutdown OK")
    print("=== ALL SMOKE TESTS PASSED ===")
