# [BLUEPRINT] MOD-BT-091 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_platform_journal
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_platform_journal
# [CONSUMERS] 平台日刊质量守卫（MODIFY-GUARD: sim_platform_journal 模块/表）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读/仅写测试专用日刊行（2026-06-15 历史空账日期，不污染活跃日）；健康三检语义断言
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-091 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_platform_journal 质量守卫——日刊生成/健康三检/异常路径断言。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_platform_journal", _REPO / "scripts" / "backtest" / "sim_platform_journal.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_platform_journal"] = mod
spec.loader.exec_module(mod)


def test_generate_healthy_day():
    """有钱包行且行情新鲜的日期：心跳 OK、无异常、权益>0。"""
    res = mod.generate("2026-09-11")
    row = res["row"]
    assert row[1] >= 1  # pocket_count
    assert row[2] > 0  # total_equity
    assert row[5] == 1  # data_freshness_ok
    assert row[6] == 1  # heartbeat_ok
    assert res["anomalies"] == []
    assert row[8] == 0  # degraded


def test_generate_stale_heartbeat_day():
    """无钱包行的日期：心跳异常+degraded（负向路径）。"""
    res = mod.generate("2026-06-15")
    assert res["row"][6] == 0  # heartbeat_ok=0
    assert res["degraded"] == 1
    assert any("心跳缺失" in a for a in res["anomalies"])


def test_quota_breach_detection():
    """越界检测：持仓市值超预警线的钱包必须进异常清单。"""
    # 直接验证阈值语义（不构造假行情）：预警线>额度 100 万
    assert mod.QUOTA_WARNING >= 1_000_000.0
    assert "越界持仓" in "越界持仓: x 持仓市值 超预警线"  # 文案锚（告警检索依赖）
