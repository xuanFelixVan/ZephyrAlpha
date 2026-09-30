# [A_test] module_id: MOD-GOV_pst_modified_scope | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.test_pst_modified_scope
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/test_pst_modified_scope.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_pst_modified_scope.py — MANUAL-ONLY-PERMANENT 修改面作用域收窄单测（裁定#458 ③）

权威依据：裁定#458（ruling_registry.yaml，2026-09-30）——修改文件面
"新增行触发+全文件无订阅"判定收窄为新增行所在顶层函数/类作用域。

测试两例：
- 例 1（放行）：存量脚本带事件订阅（worker 作用域内 bus.subscribe），
  在订阅作用域之外普通改一行 → 放行；在带订阅作用域内新增 manual 模式行 →
  亦放行（作用域级订阅判定钉住）。
- 例 2（仍拦）：无任何事件订阅的 permanent 脚本，新增行自身为
  ArgumentParser 实调用且所在作用域（函数）无订阅 → 仍拦；
  对照组：同文件新增普通行（无 manual 模式）→ 放行（不误伤）。

测试隔离：MagicMock 模拟 gateway.run_git 的 --unified=0 diff；行号由内容
程序化推导避免 off-by-one；不写生产路径（tmp_path / 内存内容直传）。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.manual_only_permanent_gate import (  # noqa: E402
    _check_manual_only_permanent_modified,
)


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_diff_gateway(diff_stdout: str):
    """构造仅服务 _check_manual_only_permanent_modified 的 mock gateway（--unified=0 通道）。"""
    gw = MagicMock()

    def _run_git(cmd):
        if "--unified=0" in cmd:
            return _MockResult(0, diff_stdout)
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


def _line_no(content: str, needle: str) -> int:
    """返回 needle 所在行号（1-based；唯一命中）。"""
    hits = [i for i, line in enumerate(content.splitlines(), start=1) if needle in line]
    assert len(hits) == 1, f"needle {needle!r} 必须唯一命中，实际 {hits}"
    return hits[0]


# ── 例 1：存量脚本带订阅，订阅作用域外改一行 → 放行 ──────────────────────────

_CONTENT_WITH_SUB = '''# [TTL] permanent
"""existing compliant permanent script with event subscription."""
import argparse


def worker(bus):
    bus.subscribe("tick", on_tick)
    return True


def on_tick(evt):
    return evt


def settings():
    threshold = 50
    return threshold
'''


class TestModifiedScopeNarrowing:
    def test_existing_script_with_subscription_edit_outside_subscription_scope_released(self):
        """存量脚本带订阅（worker 作用域），订阅作用域外普通改一行 → 放行。

        同文件第二断言：在带订阅作用域内新增 ArgumentParser 行 → 亦放行
        （作用域级判定：worker 内 AST 实证订阅在场，manual 触发不判死）。
        """
        # 断言 ①：订阅作用域之外的普通一行改动（threshold 50 → 100）→ 放行
        modified = _CONTENT_WITH_SUB.replace("    threshold = 50", "    threshold = 100")
        ln = _line_no(modified, "threshold = 100")
        diff = "@@ -%d +%d @@\n" % (ln, ln) + "-    threshold = 50\n" + "+    threshold = 100\n"
        gw = _make_diff_gateway(diff)
        assert (
            _check_manual_only_permanent_modified(gw, "scripts/existing_with_sub.py", "existing_with_sub.py", modified)
            is False
        ), "订阅作用域外普通改行必须放行（裁定#458 收窄语义）"

        # 断言 ②：在带订阅作用域（worker）内新增 manual 模式行 → 放行（作用域内有订阅）
        sub_ln = _line_no(_CONTENT_WITH_SUB, 'bus.subscribe("tick", on_tick)')
        modified_in_scope = _CONTENT_WITH_SUB.replace(
            '    bus.subscribe("tick", on_tick)\n',
            '    bus.subscribe("tick", on_tick)\n    parser = argparse.ArgumentParser()\n',
        )
        insert_ln = sub_ln + 1  # 新文件中插入行位于 subscribe 行之后
        diff_in_scope = f"@@ -{sub_ln},0 +{insert_ln},1 @@\n" + "+    parser = argparse.ArgumentParser()\n"
        gw2 = _make_diff_gateway(diff_in_scope)
        assert (
            _check_manual_only_permanent_modified(
                gw2, "scripts/existing_with_sub.py", "existing_with_sub.py", modified_in_scope
            )
            is False
        ), "带订阅作用域内新增 manual 行必须放行（作用域级订阅判定）"

    def test_added_manual_line_in_scope_without_subscription_blocked(self):
        """无任何事件订阅的 permanent 脚本：新增行自身 ArgumentParser 实调用且
        所在作用域（run 函数）无订阅 → 仍拦；对照组普通新增行 → 放行。"""
        content = '''# [TTL] permanent
"""cli tool without event subscription."""
import argparse


def main():
    return run()


def run():
    args = parse_args()
    return args
'''
        run_ln = _line_no(content, "def run():")
        # 断言 ①：新增 ArgumentParser 实调用行于无订阅作用域 → 仍拦
        modified = content.replace("def run():\n", 'def run():\n    parser = argparse.ArgumentParser(prog="demo")\n')
        added_ln = run_ln + 1
        diff = f"@@ -{run_ln},0 +{added_ln},1 @@\n" + '+    parser = argparse.ArgumentParser(prog="demo")\n'
        gw = _make_diff_gateway(diff)
        assert _check_manual_only_permanent_modified(gw, "scripts/cli_no_sub.py", "cli_no_sub.py", modified) is True, (
            "新增行自身 manual 模式且所在作用域无订阅必须仍拦（裁定#458）"
        )

        # 断言 ②（对照组）：同作用域新增普通行（无 manual 模式文本）→ 放行
        diff_ctrl = f"@@ -{run_ln},0 +{added_ln},1 @@\n" + '+    _log.info("run entered")\n'
        gw2 = _make_diff_gateway(diff_ctrl)
        assert _check_manual_only_permanent_modified(gw2, "scripts/cli_no_sub.py", "cli_no_sub.py", content) is False, (
            "无 manual 模式的普通新增行不得误伤"
        )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
