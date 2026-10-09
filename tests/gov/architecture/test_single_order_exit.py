# [A_test] module_id: MOD-GOV_test_single_order_exit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.architecture.test_single_order_exit
# [TESTS] 90 号 Phase2 项（#17 行为边界 choke point 架构验证）
# [TTL] task_bound
"""90 号 Phase2 项（#17 行为边界）：单一订单出口架构验证。

裁定真源：90_methodology_open_questions.md §17（v2.0.0）——
  采纳 choke point 方案：唯一 OrderGateway 持有 xttrader 句柄，策略层不 import
  交易接口——物理不可绕过；"不存在任何绕过网关到达交易所的路径"。

验证方式（架构检查项，40 号执行层范围内）：静态扫描 src/zephyr 全部 .py，
断言 xttrader（下单通道 SDK）的 import 仅出现于券商适配器白名单。
注：xtdata（行情通道）属数据域，不在本验证范围。
"""

from __future__ import annotations

import re

from zephyr.shared.io.paths import REPO_ROOT

#: xttrader import 白名单（choke point 适配器；新增持句柄者须 Owner 裁定）
_ALLOWED_XTTRADER_IMPORTERS = frozenset(
    {
        "src/zephyr/ex_core/adapters/miniqmt_broker.py",
    }
)

_IMPORT_RE = re.compile(r"^\s*(?:import\s+\S*xttrader|from\s+\S*xttrader\S*\s+import)")


def _iter_xttrader_imports() -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    src_root = REPO_ROOT / "src" / "zephyr"
    for fp in src_root.rglob("*.py"):
        rel = fp.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(fp.read_text(encoding="utf-8").splitlines(), 1):
            if _IMPORT_RE.match(line):
                hits.append((rel, lineno, line.strip()))
    return hits


class TestSingleOrderExit:
    def test_xttrader_import_only_in_gateway_adapter(self):
        """choke point 不变量：xttrader 仅券商适配器可 import。"""
        hits = _iter_xttrader_imports()
        offenders = [h for h in hits if h[0] not in _ALLOWED_XTTRADER_IMPORTERS]
        assert not offenders, "xttrader import 越出 choke point 白名单: %s" % offenders

    def test_choke_point_adapter_exists(self):
        """白名单适配器必须真实持有 xttrader 句柄（防白名单空转）。"""
        hits = _iter_xttrader_imports()
        assert any(h[0] in _ALLOWED_XTTRADER_IMPORTERS for h in hits)
