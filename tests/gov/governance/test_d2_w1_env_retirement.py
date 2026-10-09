# [A_test] module_id: SRC-TST-D2W1 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-D2W1 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_d2_w1_env_retirement
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_d2_w1_env_retirement.py — D2 步2 静态红绿：landing 全局 env 置位退役

- R-D2-W1-1（修前红/修后绿）：landing 源不再存在全局 os.environ GW 置位/还原。
- R-D2-W1-2：landing 两个 gateway.commit 调用点显式 internal_call=True。
- R-D2-W1-3：gateway commit 签名收 internal_call 形参（默认 False，声明位）。
- R-D2-W1-4（§4 步5）：_trusted_git_env 显式剔除 GW 旗（显式决定非继承）。
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_LAND = _PROJECT_ROOT / "scripts" / "governance" / "commit_queue_landing.py"


def test_w1_1_landing_global_env_write_retired():
    src = _LAND.read_text(encoding="utf-8")
    assert 'os.environ[_GATEWAY_ENV] = "1"' not in src, "landing 不得再全局置位 GW 旗"
    assert "prev_env = os.environ.get(_GATEWAY_ENV)" not in src, "W1 prev 快照随置位一并退役"


def test_w1_2_landing_calls_internal_call():
    src = _LAND.read_text(encoding="utf-8")
    assert src.count("internal_call=True,") >= 2, "两个 gateway.commit 调用点须显式 internal_call=True"


def test_w1_3_gateway_signature_accepts_internal_call():
    _PROJECT_ROOT_S = str(_PROJECT_ROOT)
    for p in list(sys.path):
        pass
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        sig = inspect.signature(GitCommitGateway.commit)
        assert "internal_call" in sig.parameters, "commit 须收 internal_call 形参"
        assert sig.parameters["internal_call"].default is False
    finally:
        sys.path.remove(str(_PROJECT_ROOT / "src"))


def test_w1_4_trusted_git_env_explicit_c2():
    src = _LAND.read_text(encoding="utf-8")
    assert 'env.pop("ZEPHYR_COMMIT_GATEWAY", None)' in src, "_trusted_git_env 须显式剔除 GW 旗（步5 显式决定）"
