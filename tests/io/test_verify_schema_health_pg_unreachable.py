# [A_test] module_id: MOD-GOV_verify_schema_health | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | scripts/governance/d11_compliance/verify_schema_health.py | §test
# [MODULE] tests.io.test_verify_schema_health_pg_unreachable
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH] ARCH-119
"""test_verify_schema_health_pg_unreachable.py — verify_schema_health PG 离线优雅阻断单测（tracker #116 顺手项 / #ARCH-119）

权威依据：scripts/governance/d11_compliance/verify_schema_health.py main()

报告 §1.3：连接调用原在 try 块外——PG 离线=未捕获异常崩溃式 fail-closed。
修复后：PG 离线 → [ERROR][PG-UNREACHABLE] 明确告警 + 引导文案 + exit 2
（EXIT_ERROR，仍阻断但非崩溃栈）。

测试组：
- 连接抛异常 → main() 返回 EXIT_ERROR(2) + 输出含 [PG-UNREACHABLE] 与引导文案，
  且无未捕获异常（崩溃栈不出现）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = REPO_ROOT / "scripts" / "governance"
_VSH_PATH = _GOV_DIR / "d11_compliance" / "verify_schema_health.py"

for _p in (str(_GOV_DIR), str(REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _load_vsh():
    """按文件位置加载 verify_schema_health（scripts 非包模块）。"""
    spec = importlib.util.spec_from_file_location("verify_schema_health_d11", _VSH_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPgUnreachableGracefulBlock:
    """PG 离线 → 明确告警阻断（非崩溃栈）。"""

    def test_pg_unreachable_returns_exit_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        vsh = _load_vsh()

        def _raise(*a, **k):
            raise ConnectionError("connection refused")

        monkeypatch.setattr(vsh, "get_depgraph_pg_connection", _raise)
        monkeypatch.setattr(sys, "argv", ["verify_schema_health.py"])
        rc = vsh.main()
        assert rc == vsh.EXIT_ERROR
        assert rc == 2
        out = capsys.readouterr().out
        assert "[PG-UNREACHABLE]" in out
        assert "引导" in out
        assert "Traceback" not in out
