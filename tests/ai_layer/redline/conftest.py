# [A_test] module_id: zephyr.ai_layer.redline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_redline_tests
# [MODULE] tests.ai_layer.redline.conftest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline
# [MATURITY] testing
# [INVARIANTS] FakeGateway 只模拟 gate 面所需的最小 git 语义（diff --cached name-only /
#              git show :staged / git show HEAD:path）；测试零生产路径写入（gate 审计经
#              project_root 注入 tmp_path；S1 审计路径显式注入 tmp_path）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本目录
# [TTL] task_bound
"""tests/ai_layer/redline — OBJ_S 红线机检面测试夹具（FakeGateway + 目录级隔离）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


class _FakeResult:
    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode


class FakeGateway:
    """gate 面最小 git 语义模拟：staged=索引内容表，head=HEAD 基线表。"""

    def __init__(
        self,
        staged: dict[str, str],
        head: dict[str, str] | None = None,
        project_root: Path | None = None,
    ) -> None:
        self._staged = staged
        self._head = head or {}
        self.project_root = str(project_root) if project_root else "."

    def run_git(self, args: list[str]) -> _FakeResult:  # noqa: ARG002 — 签名对齐 gateway
        if args[:4] == ["git", "diff", "--cached", "--name-only"]:
            return _FakeResult("\n".join(self._staged), 0)
        if args[:2] == ["git", "show"]:
            target = args[2]
            if target.startswith(":"):
                text = self._staged.get(target[1:])
                return _FakeResult(text, 0) if text is not None else _FakeResult("", 1)
            if target.startswith("HEAD:"):
                text = self._head.get(target[5:])
                return _FakeResult(text, 0) if text is not None else _FakeResult("", 1)
        return _FakeResult("", 1)


@pytest.fixture()
def fake_gateway_factory(tmp_path: Path) -> Any:
    """FakeGateway 构造器（project_root 注入 tmp_path → gate 审计天然隔离生产路径）。"""

    def _make(staged: dict[str, str], head: dict[str, str] | None = None) -> FakeGateway:
        return FakeGateway(staged, head, project_root=tmp_path)

    return _make
