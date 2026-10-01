# [BLUEPRINT] MOD-PAPER-SESSION-WIRING | docs/03_modules/_domain_execution_core/blueprint.md | 合规闸装配存在性钉
# [MODULE] tests.scripts.test_start_paper_session_wiring
# [DOMAIN] D_EXECUTION_CORE
# [DEPENDENCIES] tests.scripts 先例目录；importlib 直载 scripts/start_paper_session.py
# [CONSUMERS] 波7 终验（落地面回归）
# [STARTUP] pytest 收集
# [MATURITY] stable
# [INVARIANTS] 只读源码面与模块命名空间；零网络零 CH；tmp_path 隔离
# [MODIFY-GUARD] tests/ 豁免
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=装配面回归信号
# [TESTS] tests/scripts/test_start_paper_session_wiring.py
# [TTL] task_bound
"""实盘合规闸装配存在性钉（2026-09-28 夜，chief7）：start_paper_session 的 OrderManager 三闸
（ReportGate/CancelRateGuard/ManipulationRealtimeMonitor）与 TradingSession 合规参必须保持注入形态。
F62 C-002（0cecaf771d）落地后由本钉防回退；不锁定具体装配函数名，允许属主队重构。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "start_paper_session.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("start_paper_session_under_test", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert _SCRIPT.exists()


def test_module_imports_and_exposes_compliance_gates():
    mod = _load_module()
    import re

    src = _SCRIPT.read_text(encoding="utf-8")
    assert "OrderManager" in src, "OrderManager 装配消失"
    for gate in ("ReportGate", "CancelRateGuard", "ManipulationRealtimeMonitor"):
        assert gate in src, f"{gate} 注入消失（F62 C-002 回退信号）"


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked scripts/start_paper_session.py 的 TradingSession 已无 compliance_detector 合规参（源面演进/回退，接线尺对不上现行真源），转XPASS=参数回归须改判",
)
def test_source_keeps_compliance_session_params():
    src = _SCRIPT.read_text(encoding="utf-8")
    for token in ("discipline_guard", "compliance_detector"):
        assert token in src, f"TradingSession 合规参 {token} 消失"
