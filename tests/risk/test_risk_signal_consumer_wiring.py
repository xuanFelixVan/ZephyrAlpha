# [BLUEPRINT] MOD-RK-SIGNAL-WIRING | 风险信号"产而不消"接线欠账回归锁 (H5-P0) | §
# [TTL] permanent
# [MODULE] tests.risk.test_risk_signal_consumer_wiring
# [DOMAIN] D_RISK
# [TESTS] 无（本件为 src 生产代码消费方 AST 回归锁 + 契约头诚实性核验，非被测单元）
# [COVERAGE] 4 只风险监控器（集中度/盘中 VaR 重算/拥挤度/回撤状态机）零现役消费方的实测锁定 + 生存线正对照 + 契约头无谎报 + 未偷偷接看板 + 数据缺席出声
# [MATURITY] evolving

"""风险信号"产而不消"接线欠账回归锁 (H5-P0, 2026-09-15 实测).

背景裁定：四只风险监控器经 AST/实例化/调用位实测均为「设计性死件 / 无诚实数据出口」，
在授权文件范围内无法在不臆造输入、不新增死探针、不动越权装配代码的前提下接入既有事件通道，
故按任务 (d) 走「如实登记契约头 = 无现役消费方」而非「为接线而接线」。本锁不验证「触发→
通知出口收到」（出口不存在，验证即造假），而验证三件诚实且可回归的事实：

    1. 消费方实测为零：src 生产代码里对这四只监控器**没有任何 runtime 实例化/调用位**
       （回撤状态机唯一实例化在未接线的 session_persistence，其入口函数又零调用者）。
    2. 契约头诚实：每只监控器的 [CONSUMERS] 头已登记「无现役」且不含旧的谎报消费方 token。
    3. 未被偷偷接线：四只监控器符号不出现在通知看板 ops_alert_feed.py（防未来静默半接线）。

正对照 test_positive_control_*：生存线判定函数 evaluate_survival_line 在 ops_alert_feed 有
**真实调用位**（≥1），证明上述「零」是扫描器识别有效消费方的结果，而非扫描器本身失明漏报。
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

# 被审监控器符号 -> 其定义文件（相对仓库根，POSIX）。消费方统计排除定义文件自身。
MONITORS: dict[str, str] = {
    "ConcentrationMonitor": "src/zephyr/risk/core/concentration_monitor.py",
    "IntradayVarRecalcController": "src/zephyr/risk/core/var_intraday_recalc.py",
    "CrowdingMonitor": "src/zephyr/risk/core/crowding_monitor.py",
    "DrawdownStateMachine": "src/zephyr/risk/core/drawdown_state_machine.py",
}

BOARD_FILE = "src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py"
SESSION_PERSIST_FILE = "src/zephyr/risk/core/drawdown_session_persistence.py"
RISK_ORCH_FILE = "src/zephyr/risk/implementations/default_risk_manager_orchestrator.py"

# 各监控器契约头中被实测证伪的旧「消费方」token（不得再出现）。
FALSE_CONSUMER_TOKENS: dict[str, list[str]] = {
    MONITORS["ConcentrationMonitor"]: [
        "MOD-RK-02(Pre-Trade Checker",
        "Portfolio Risk Monitor",
        "MOD-RK-13(Crowding Monitor",
    ],
    MONITORS["IntradayVarRecalcController"]: [
        "intraday_risk_loop(盘中循环检测触发后调用",
        "RiskLayerOrchestrator(编排注入)",
    ],
    MONITORS["CrowdingMonitor"]: [
        "MOD-L04-001(DefaultRiskManagerOrchestrator",
        "组合内集中度输入",
    ],
    MONITORS["DrawdownStateMachine"]: [
        "RiskOrchestrator(§6.5 接线位)",
    ],
}


@lru_cache(maxsize=1)
def _src_trees() -> tuple[tuple[str, ast.Module], ...]:
    """解析 src/ 下全部生产 .py（排除 __pycache__），返回 (相对路径, AST) 元组，缓存一次。"""
    out: list[tuple[str, ast.Module]] = []
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            out.append((rel, ast.parse(path.read_text(encoding="utf-8"))))
        except SyntaxError:
            continue
    return tuple(out)


def _call_name(node: ast.Call) -> str | None:
    """取调用被调名：Name -> id；Attribute -> attr；其余 -> None。"""
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _call_sites(symbol: str, *, exclude_def: bool) -> dict[str, int]:
    """统计 src 生产代码中以 Call 位使用 `symbol`（实例化或函数调用）的文件 -> 次数。

    注释 / 文档字符串 / 类型注解（含 forward-ref 字符串）不计入，只认真实调用位。
    """
    def_file = MONITORS.get(symbol)
    counts: dict[str, int] = {}
    for rel, tree in _src_trees():
        if exclude_def and def_file is not None and rel == def_file:
            continue
        n = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Call) and _call_name(node) == symbol)
        if n:
            counts[rel] = n
    return counts


def _typechecking_import_files(symbol: str) -> set[str]:
    """返回在 `if TYPE_CHECKING:` 块内 import `symbol` 的文件集合（非 runtime 消费方）。"""
    hits: set[str] = set()
    for rel, tree in _src_trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            test = node.test
            guard = test.id if isinstance(test, ast.Name) else (test.attr if isinstance(test, ast.Attribute) else None)
            if guard != "TYPE_CHECKING":
                continue
            for sub in ast.walk(node):
                if isinstance(sub, ast.ImportFrom) and any(a.name == symbol for a in sub.names):
                    hits.add(rel)
    return hits


def _header_consumers_line(rel_path: str) -> str:
    """取某文件契约头的 `[CONSUMERS]` 行原文。"""
    for line in (ROOT / rel_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# [CONSUMERS]"):
            return line
    raise AssertionError(f"{rel_path} 缺少 [CONSUMERS] 契约头")


# ── 正对照：证明扫描器能识别「真实消费方」，故下面的「零」可信 ──────────────────────


def test_positive_control_survival_line_has_real_live_consumer() -> None:
    """evaluate_survival_line 在 ops_alert_feed 有真实调用位（生存线确已接线）。

    若本用例失败，说明扫描器漏报，则其余「零消费方」断言不成立。
    """
    files = _call_sites("evaluate_survival_line", exclude_def=False)
    assert files.get(BOARD_FILE, 0) >= 1, f"正对照失效：未检出 evaluate_survival_line 的现役调用位 -> {files}"


# ── 1. 消费方实测为零（设计性死件 / 无诚实出口） ─────────────────────────────────


@pytest.mark.parametrize(
    "symbol",
    ["ConcentrationMonitor", "IntradayVarRecalcController", "CrowdingMonitor"],
)
def test_monitor_has_zero_live_consumers(symbol: str) -> None:
    """集中度 / 盘中 VaR 重算 / 拥挤度：src 生产代码零 runtime 实例化、零调用位。"""
    files = _call_sites(symbol, exclude_def=True)
    assert files == {}, f"{symbol} 出现未登记的现役消费方调用位：{files}"


def test_crowding_monitor_only_typechecking_reference_and_dead_container() -> None:
    """拥挤度唯一结构性引用是 TYPE_CHECKING 专用；其容器编排器自身也从未被实例化。"""
    tc = _typechecking_import_files("CrowdingMonitor")
    assert tc == {RISK_ORCH_FILE}, f"CrowdingMonitor 的 TYPE_CHECKING 引用异常：{tc}"
    # 该编排器 check_crowding 挂在 DefaultRiskManagerOrchestrator 上，但后者全仓零实例化 -> 永不可达
    assert _call_sites("DefaultRiskManagerOrchestrator", exclude_def=True) == {}, "DefaultRiskManagerOrchestrator 已被实例化，拥挤度消费路径需重新核定"


def test_drawdown_state_machine_only_dead_chain() -> None:
    """回撤状态机唯一实例化在未接线的 session_persistence，而该模块两个入口函数零调用者。"""
    files = _call_sites("DrawdownStateMachine", exclude_def=True)
    assert set(files) == {SESSION_PERSIST_FILE}, f"DrawdownStateMachine 出现登记外的实例化位：{files}"
    assert _call_sites("premarket_initialization", exclude_def=False) == {}, "盘前入口已被调用，状态机链可能已激活，需重新核定"
    assert _call_sites("postmarket_persist", exclude_def=False) == {}, "盘后入口已被调用，状态机链可能已激活，需重新核定"


# ── 2. 契约头诚实（[CONSUMERS] 已登记「无现役」且无旧的谎报 token） ────────────────


@pytest.mark.parametrize("rel_path", list(FALSE_CONSUMER_TOKENS))
def test_consumers_header_registered_truthfully(rel_path: str) -> None:
    """四只监控器 [CONSUMERS] 头须声明「无现役」，且不得残留实测证伪的旧消费方声称。"""
    line = _header_consumers_line(rel_path)
    assert "无现役" in line, f"{rel_path} 的 [CONSUMERS] 未登记『无现役消费方』：{line}"
    for token in FALSE_CONSUMER_TOKENS[rel_path]:
        assert token not in line, f"{rel_path} 的 [CONSUMERS] 残留已证伪的旧消费方 token：{token!r}"


# ── 3. 未被偷偷接到通知看板（防未来静默半接线） ───────────────────────────────────


@pytest.mark.parametrize("symbol", list(MONITORS))
def test_monitor_not_secretly_wired_to_board(symbol: str) -> None:
    """四只监控器符号不得出现在通知看板 ops_alert_feed.py（当前无诚实出口，若出现即须重审契约）。"""
    board_src = (ROOT / BOARD_FILE).read_text(encoding="utf-8")
    assert symbol not in board_src, f"{symbol} 出现在 ops_alert_feed.py，与『无现役消费方』登记矛盾，须重审接线与契约头"


# ── 4. 数据缺席→不产出且出声（组件边界 Fail-Closed，实测） ──────────────────────


def test_concentration_fail_closed_on_absent_input() -> None:
    """集中度：空权重输入须抛错出声，绝不返回伪 ok 快照（数据缺席不产出）。"""
    from zephyr.risk.core.concentration_monitor import (
        ConcentrationMonitor,
        InvalidConcentrationInputError,
    )

    monitor = ConcentrationMonitor()
    with pytest.raises(InvalidConcentrationInputError):
        monitor.update({})
    # 抛错后不得留下任何「已归一/正常级别」的可消费快照
    assert monitor.last_level.name == "NONE"
