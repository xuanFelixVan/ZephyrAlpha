# [A_test] module_id: SRC-TST-2007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-624 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_demo_e2e_pipeline_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations
from zephyr.shared.io.paths import REPO_ROOT

"""demo_e2e_pipeline.py 语法自检（不执行全链路——需网络与 akshare）。"""


from pathlib import Path


def test_demo_e2e_pipeline_compiles() -> None:
    root = REPO_ROOT
    script = root / "demo_e2e_pipeline.py"
    src = script.read_text(encoding="utf-8")
    compile(src, str(script), "exec", dont_inherit=True)
