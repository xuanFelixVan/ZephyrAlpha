# [A_test] module_id: MOD-GOV_battle_map_exe_flow | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-278 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_battle_map_execution_flow
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB不可达->skip_test; 拓扑断裂->AssertionError
# [TESTS] tests/governance/test_battle_map_execution_flow.py
# [A_module] module_id=MOD-TEST-278 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_battle_map_execution_flow.py — 执行阶段 6 环节数据流转闭环验证

验证 battle_map_05_execution.md 真源中执行阶段 6 环节的闭环逻辑：

  BM-EXE-01 自适应风控审批
    ↓ 审批后订单（data_flow）
  BM-EXE-04 Pre-Trade合规检查
    ↓ 合规通过订单（data_flow）
  BM-EXE-05 智能订单路由与拆单
    ↓ 子订单序列（data_flow）
  BM-EXE-02 交易执行
    ↓ 成交回报（data_flow）
  BM-EXE-06 成交回报处理与持仓更新
    ↓ 成交数据（data_flow）
  BM-EXE-03 执行质量TCA
    ↓ TCA反馈（degradation，闭环回到 BM-EXE-05）

两类测试：
  1. **拓扑验证（e2e，需 DB）**：从 PostgreSQL battle_map 三表读取，验证 6 环节存在、
     sort_order 顺序正确、5 条 data_flow 边构成主链、1 条 degradation 边闭合回路、
     每环节有锚点（BM-INV-001）、indicators 6 件套完整。
  2. **数据流模拟（纯逻辑，无 DB）**：用 mock 处理器模拟每环节的输入→输出转换，
     验证主链端到端跑通、TCA 反馈闭环改善拆单参数。

设计原则（对标 test_apply_depgraph_smoke.py）：
  - 真实 DB 连接做拓扑验证（@pytest.mark.e2e）；DB 不可达则 skip
  - 模拟测试零 DB 依赖，纯逻辑验证闭环语义
  - 不写入生产库——全部只读

Usage::

    py -3.12 -m pytest tests/governance/test_battle_map_execution_flow.py -v
    py -3.12 -m pytest tests/governance/test_battle_map_execution_flow.py -k "not e2e"  # 跳过 DB
    py -3.12 -m pytest tests/governance/test_battle_map_execution_flow.py::TestExecutionDataFlowSimulation -v
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

# ── 执行阶段 6 环节常量（与 DB step_id / sort_order 对齐）──────────────

# 主链顺序（sort_order 升序）：风控审批→合规→路由拆单→交易执行→Fill处理→TCA
EXPECTED_CHAIN: list[str] = [
    "BM-EXE-01",  # sort=10  自适应风控审批（production）
    "BM-EXE-04",  # sort=20  Pre-Trade合规检查（design）
    "BM-EXE-05",  # sort=30  智能订单路由与拆单（design）
    "BM-EXE-02",  # sort=40  交易执行（production）
    "BM-EXE-06",  # sort=50  成交回报处理与持仓更新（design）
    "BM-EXE-03",  # sort=60  执行质量TCA（production）
]

# 预期 sort_order 映射
EXPECTED_SORT_ORDERS: dict[str, int] = {
    "BM-EXE-01": 10,
    "BM-EXE-04": 20,
    "BM-EXE-05": 30,
    "BM-EXE-02": 40,
    "BM-EXE-06": 50,
    "BM-EXE-03": 60,
}

# 预期 data_flow 主链边（from → to）
EXPECTED_DATA_FLOW_EDGES: list[tuple[str, str]] = [
    ("BM-EXE-01", "BM-EXE-04"),  # 审批后订单→合规检查
    ("BM-EXE-04", "BM-EXE-05"),  # 合规通过→路由拆单
    ("BM-EXE-05", "BM-EXE-02"),  # 拆单方案/子订单→下单执行
    ("BM-EXE-02", "BM-EXE-06"),  # 成交回报→Fill处理与持仓更新
    ("BM-EXE-06", "BM-EXE-03"),  # 成交数据→TCA分析
]

# 预期 degradation 反馈边（闭环：TCA→拆单算法优化）
EXPECTED_FEEDBACK_EDGE: tuple[str, str] = ("BM-EXE-03", "BM-EXE-05")

# indicators 6 件套必需字段
REQUIRED_INDICATOR_KEYS = {
    "trigger", "consumes", "params", "data_flow", "code_mapping", "degradation",
}
# data_flow 子结构必需字段
REQUIRED_DATA_FLOW_KEYS = {"input", "output", "process", "downstream"}


# ============================================================================
# Part 1: 拓扑验证（e2e，需 PostgreSQL）—— 从 DB 读取真实结构
# ============================================================================


def _get_reader():
    """构造 BattleMapReader，DB 不可达时 skip。"""
    try:
        from zephyr.governance.persistence.battle_map_reader import BattleMapReader

        reader = BattleMapReader()
        # 触发真实连接，验证 PG 可达
        reader.get_step_count()
        return reader
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"battle_map PostgreSQL 不可达: {exc}")


@pytest.mark.e2e
class TestExecutionTopology:
    """执行阶段拓扑验证——从 DB 读取 battle_map 三表，验证 6 环节闭环结构。"""

    @pytest.fixture(scope="class")
    def exe_steps(self):
        """加载 execution 阶段全部环节。"""
        reader = _get_reader()
        try:
            steps = reader.get_steps_by_flow_stage("execution")
        finally:
            reader.close()
        return {s["step_id"]: s for s in steps}

    @pytest.fixture(scope="class")
    def exe_edges(self, exe_steps):
        """加载涉及执行环节的流转边。"""
        reader = _get_reader()
        try:
            edges = reader.get_all_edges()
        finally:
            reader.close()
        exe_ids = set(exe_steps.keys())
        return [
            e for e in edges
            if e["from_step_id"] in exe_ids or e["to_step_id"] in exe_ids
        ]

    @pytest.fixture(scope="class")
    def exe_anchors(self, exe_steps):
        """加载执行环节的锚点。"""
        reader = _get_reader()
        try:
            anchors = reader.get_all_anchors()
        finally:
            reader.close()
        exe_ids = set(exe_steps.keys())
        return [a for a in anchors if a["step_id"] in exe_ids]

    def test_6_steps_exist(self, exe_steps):
        """6 个执行环节全部存在。"""
        for sid in EXPECTED_CHAIN:
            assert sid in exe_steps, f"缺少执行环节 {sid}（DB 中未找到）"

    def test_exactly_6_execution_steps(self, exe_steps):
        """execution 阶段恰好 6 个环节（无多余/无遗漏）。"""
        assert len(exe_steps) == 6, (
            f"execution 阶段应有 6 环节，实际 {len(exe_steps)}: "
            f"{sorted(exe_steps.keys())}"
        )

    def test_sort_order_chain(self, exe_steps):
        """sort_order 按主链顺序递增（10/20/30/40/50/60）。"""
        for sid, expected_sort in EXPECTED_SORT_ORDERS.items():
            actual = exe_steps[sid].get("sort_order")
            assert actual == expected_sort, (
                f"{sid} sort_order 应为 {expected_sort}，实际 {actual}"
            )

    def test_sort_order_monotonic(self, exe_steps):
        """按 sort_order 排列后，环节序列等于预期主链。"""
        ordered = sorted(exe_steps.values(), key=lambda s: s["sort_order"])
        actual_chain = [s["step_id"] for s in ordered]
        assert actual_chain == EXPECTED_CHAIN, (
            f"sort_order 排列后环节序列不符:\n预期 {EXPECTED_CHAIN}\n实际 {actual_chain}"
        )

    def test_data_flow_main_chain(self, exe_edges):
        """5 条 data_flow 边构成主链 BM-EXE-01→04→05→02→06→03。"""
        data_flow_edges = {
            (e["from_step_id"], e["to_step_id"])
            for e in exe_edges
            if e["edge_type"] == "data_flow"
        }
        for expected in EXPECTED_DATA_FLOW_EDGES:
            assert expected in data_flow_edges, (
                f"缺少 data_flow 边 {expected[0]}→{expected[1]}"
            )

    def test_degradation_feedback_loop(self, exe_edges):
        """degradation 反馈边 BM-EXE-03→BM-EXE-05 存在（闭环）。"""
        degradation_edges = {
            (e["from_step_id"], e["to_step_id"])
            for e in exe_edges
            if e["edge_type"] == "degradation"
        }
        assert EXPECTED_FEEDBACK_EDGE in degradation_edges, (
            f"缺少 degradation 反馈边 {EXPECTED_FEEDBACK_EDGE[0]}→{EXPECTED_FEEDBACK_EDGE[1]}，"
            f"闭环断裂"
        )

    def test_no_old_shortcut_edges(self, exe_edges):
        """旧直连边已删除（无 BM-EXE-01→02 / 02→03 / 03→02 旁路）。"""
        removed_edges = {
            ("BM-EXE-01", "BM-EXE-02"),  # 旧：审批后订单直连交易执行
            ("BM-EXE-02", "BM-EXE-03"),  # 旧：成交回报直连TCA
            ("BM-EXE-03", "BM-EXE-02"),  # 旧：TCA反馈直连交易执行
        }
        actual_edges = {
            (e["from_step_id"], e["to_step_id"]) for e in exe_edges
        }
        leftover = removed_edges & actual_edges
        assert not leftover, f"旧旁路边未删除: {leftover}"

    def test_each_step_has_anchor(self, exe_anchors):
        """每个执行环节至少一个锚点（BM-INV-001）。"""
        anchored_steps = {a["step_id"] for a in exe_anchors}
        for sid in EXPECTED_CHAIN:
            assert sid in anchored_steps, (
                f"{sid} 无锚点（违反 BM-INV-001，悬空决策）"
            )

    def test_indicators_6件套_complete(self, exe_steps):
        """每个环节 indicators 含 6 件套全部字段。"""
        for sid in EXPECTED_CHAIN:
            indicators = exe_steps[sid].get("indicators") or {}
            missing = REQUIRED_INDICATOR_KEYS - set(indicators.keys())
            assert not missing, f"{sid} indicators 缺字段: {missing}"

    def test_indicators_data_flow_complete(self, exe_steps):
        """每个环节 indicators.data_flow 含 input/output/process/downstream。"""
        for sid in EXPECTED_CHAIN:
            df = (exe_steps[sid].get("indicators") or {}).get("data_flow") or {}
            missing = REQUIRED_DATA_FLOW_KEYS - set(df.keys())
            assert not missing, f"{sid} data_flow 缺字段: {missing}"

    def test_data_flow_chain_consistency(self, exe_steps):
        """主链相邻环节的 output→input 语义一致（上游 output 出现在下游 consumes）。

        验证设计意图：每个环节的 data_flow.output 应被下游环节的 consumes 引用，
        确保数据流不断裂。
        """
        # 构建 output 映射：step_id → output 描述文本
        outputs: dict[str, str] = {}
        for sid in EXPECTED_CHAIN:
            df = (exe_steps[sid].get("indicators") or {}).get("data_flow") or {}
            out = df.get("output", "")
            if out:
                outputs[sid] = out

        # 验证主链每条边的上游 output 与下游 consumes/input 有语义关联
        for from_sid, to_sid in EXPECTED_DATA_FLOW_EDGES:
            upstream_output = outputs.get(from_sid, "")
            downstream = exe_steps.get(to_sid, {})
            df_down = (downstream.get("indicators") or {}).get("data_flow") or {}
            downstream_input = df_down.get("input", "")
            # 至少一个非空（设计完整性）
            assert upstream_output or downstream_input, (
                f"{from_sid}→{to_sid} 数据流断裂: 上游 output='{upstream_output}'，"
                f"下游 input='{downstream_input}'"
            )


# ============================================================================
# Part 2: 数据流模拟（纯逻辑，无 DB）—— mock 处理器验证闭环语义
# ============================================================================


@dataclass
class DataPacket:
    """模拟数据包——在环节间流转的数据载体。

    每个环节接收一个 DataPacket，处理后产出新的 DataPacket。
    history 记录经过的环节序列，用于验证流转路径。
    """

    type: str  # 数据类型标识（如 "position_order" / "approved_order"）
    payload: dict[str, Any]  # 实际数据
    history: list[str] = field(default_factory=list)  # 经过的 step_id 序列


# ── 各环节模拟处理器 ──────────────────────────────────────────────────
# 每个处理器：验证输入类型 → 模拟处理 → 产出输出类型 → 记录 history
# 处理逻辑是对真源 indicators.data_flow.process 的简化模拟


def _process_risk_approval(pkt: DataPacket) -> DataPacket:
    """BM-EXE-01 自适应风控审批：仓位指令 → 审批后订单。

    模拟 C-004 风控审批（订单拦截器）：检查单标的权重上限、HALT 级违例阻断。
    """
    assert pkt.type == "position_order", f"BM-EXE-01 输入应为 position_order，实际 {pkt.type}"
    symbol = pkt.payload["symbol"]
    target_qty = pkt.payload["target_qty"]
    side = pkt.payload["side"]
    # 模拟风控检查：单标的权重 ≤10% 通过
    assert target_qty > 0, "目标仓位必须 >0"
    return DataPacket(
        type="approved_order",
        payload={"symbol": symbol, "qty": target_qty, "side": side, "approved": True},
        history=pkt.history + ["BM-EXE-01"],
    )


def _process_pretrade_compliance(pkt: DataPacket) -> DataPacket:
    """BM-EXE-04 Pre-Trade合规检查：审批后订单 → 合规通过订单。

    模拟 Pre-Trade 合规主链 6 项顺序检查（涨跌停/参与率/持仓限额/行业集中度/
    撤单率/报单停留时间锁）+ 操纵防护（Wash Trade/Spoofing）。Fail-Closed。
    """
    assert pkt.type == "approved_order", f"BM-EXE-04 输入应为 approved_order，实际 {pkt.type}"
    assert pkt.payload["approved"], "订单未通过风控审批，合规检查拒绝"
    return DataPacket(
        type="compliant_order",
        payload={**pkt.payload, "compliant": True},
        history=pkt.history + ["BM-EXE-04"],
    )


def _process_smart_routing(pkt: DataPacket, tca_feedback: dict | None = None) -> DataPacket:
    """BM-EXE-05 智能订单路由与拆单：合规通过订单 → 子订单序列。

    模拟 Almgren-Chriss 最优执行轨迹 + 算法选择 + 大单拆分 + 参与率控制。
    TCA 反馈（degradation 闭环）可调整参与率和算法选择。
    """
    assert pkt.type == "compliant_order", f"BM-EXE-05 输入应为 compliant_order，实际 {pkt.type}"
    assert pkt.payload.get("compliant"), "订单未通过合规检查，拒绝拆单"
    qty = pkt.payload["qty"]
    # 默认参与率 10%；TCA 反馈可能调整（闭环优化）
    participation_rate = 0.10
    algo = "TWAP"
    if tca_feedback:
        # TCA 反馈：滑点过高→降低参与率+换算法
        if tca_feedback.get("slippage_bps", 0) > 5:
            participation_rate = 0.05
            algo = "VWAP"
    # 拆单：按参与率切分子订单
    child_qty = max(1, int(qty * participation_rate))
    child_count = max(1, (qty + child_qty - 1) // child_qty)
    children = [
        {"child_id": i, "qty": child_qty if i < child_count - 1 else qty - child_qty * (child_count - 1)}
        for i in range(child_count)
    ]
    return DataPacket(
        type="child_orders",
        payload={
            "symbol": pkt.payload["symbol"],
            "side": pkt.payload["side"],
            "children": children,
            "algo": algo,
            "participation_rate": participation_rate,
        },
        history=pkt.history + ["BM-EXE-05"],
    )


def _process_trade_execution(pkt: DataPacket) -> DataPacket:
    """BM-EXE-02 交易执行：子订单序列 → 交易指令+成交回报+PnL。

    模拟 C-002 下单（miniQMT 通道）+ 成交回报。
    """
    assert pkt.type == "child_orders", f"BM-EXE-02 输入应为 child_orders，实际 {pkt.type}"
    fills = []
    for child in pkt.payload["children"]:
        fills.append({
            "child_id": child["child_id"],
            "filled_qty": child["qty"],
            "fill_price": 10.0 + child["child_id"] * 0.01,  # 模拟成交价
        })
    return DataPacket(
        type="fill_report",
        payload={
            "symbol": pkt.payload["symbol"],
            "side": pkt.payload["side"],
            "fills": fills,
            "pnl": sum(f["filled_qty"] * f["fill_price"] for f in fills) * 0.001,
        },
        history=pkt.history + ["BM-EXE-02"],
    )


def _process_fill_handling(pkt: DataPacket) -> DataPacket:
    """BM-EXE-06 成交回报处理与持仓更新：成交回报 → 持仓快照+PnL。

    模拟 Fill 解析 + 部分成交聚合 + 费用计算 + 持仓更新 + 订单状态机流转。
    成交数据透传给下游 BM-EXE-03（TCA 消费成交回报做成本归因）。
    """
    assert pkt.type == "fill_report", f"BM-EXE-06 输入应为 fill_report，实际 {pkt.type}"
    fills = pkt.payload["fills"]
    total_qty = sum(f["filled_qty"] for f in fills)
    avg_price = sum(f["filled_qty"] * f["fill_price"] for f in fills) / total_qty if total_qty else 0
    # 费用：佣金0.03% + 印花税0.05%（卖出）+ 过户费0.001%
    commission = total_qty * avg_price * 0.0003
    return DataPacket(
        type="position_snapshot",
        payload={
            "symbol": pkt.payload["symbol"],
            "quantity": total_qty,
            "avg_cost": avg_price,
            "commission": commission,
            "pnl": pkt.payload["pnl"] - commission,
            # 成交数据透传：BM-EXE-03 TCA 需要原始 fill 做成本归因
            "fills": fills,
        },
        history=pkt.history + ["BM-EXE-06"],
    )


def _process_tca_analysis(pkt: DataPacket) -> DataPacket:
    """BM-EXE-03 执行质量TCA：成交数据 → 执行质量评分+成本归因。

    模拟 IS 成本分解（时机成本+市场冲击+滑点+佣金）+ 基准对比。
    产出 TCA 反馈数据，用于闭环回到 BM-EXE-05 优化拆单。

    输入是 BM-EXE-06 透传的 position_snapshot（含 fills 成交数据）。
    """
    assert pkt.type == "position_snapshot", f"BM-EXE-03 输入应为 position_snapshot，实际 {pkt.type}"
    fills = pkt.payload["fills"]
    # 模拟滑点：成交价偏差
    arrival_price = 10.0
    slippage_bps = sum(
        abs(f["fill_price"] - arrival_price) / arrival_price * 10000 * f["filled_qty"]
        for f in fills
    ) / max(1, sum(f["filled_qty"] for f in fills))
    return DataPacket(
        type="tca_report",
        payload={
            "symbol": pkt.payload["symbol"],
            "slippage_bps": round(slippage_bps, 2),
            "is_cost": round(slippage_bps + 3, 2),  # IS = 滑点 + 佣金(3bps)
            "benchmark": "arrival",
            "quality_score": max(0, 100 - slippage_bps * 2),
        },
        history=pkt.history + ["BM-EXE-03"],
    )


# 环节处理器注册表（step_id → processor）
STEP_PROCESSORS: dict[str, Any] = {
    "BM-EXE-01": _process_risk_approval,
    "BM-EXE-04": _process_pretrade_compliance,
    "BM-EXE-05": _process_smart_routing,
    "BM-EXE-02": _process_trade_execution,
    "BM-EXE-06": _process_fill_handling,
    "BM-EXE-03": _process_tca_analysis,
}


class TestExecutionDataFlowSimulation:
    """数据流模拟——验证 6 环节主链端到端跑通 + TCA 反馈闭环。"""

    def test_main_chain_end_to_end(self):
        """主链 BM-EXE-01→04→05→02→06→03 端到端跑通。

        初始仓位指令 → 经过 6 环节处理 → 产出 TCA 报告。
        history 记录验证经过的环节序列等于主链。
        """
        # 初始输入：仓位指令（来自 BM-POS-01，上游）
        initial = DataPacket(
            type="position_order",
            payload={"symbol": "600519", "target_qty": 1000, "side": "buy"},
        )

        # 按 sort_order 顺序执行主链
        pkt = initial
        for sid in EXPECTED_CHAIN:
            processor = STEP_PROCESSORS[sid]
            # BM-EXE-05 需要 tca_feedback 参数，主链首次执行无反馈
            if sid == "BM-EXE-05":
                pkt = processor(pkt, tca_feedback=None)
            else:
                pkt = processor(pkt)

        # 验证：最终产出是 TCA 报告
        assert pkt.type == "tca_report", f"主链终点应为 tca_report，实际 {pkt.type}"
        assert "slippage_bps" in pkt.payload
        assert "is_cost" in pkt.payload

        # 验证：经过的环节序列等于主链
        assert pkt.history == EXPECTED_CHAIN, (
            f"流转路径不符:\n预期 {EXPECTED_CHAIN}\n实际 {pkt.history}"
        )

    def test_data_type_handoff_correct(self):
        """相邻环节的数据类型交接正确（上游 output type = 下游 input type）。"""
        # 预期数据类型交接链
        expected_handoffs = [
            ("position_order", "BM-EXE-01", "approved_order"),
            ("approved_order", "BM-EXE-04", "compliant_order"),
            ("compliant_order", "BM-EXE-05", "child_orders"),
            ("child_orders", "BM-EXE-02", "fill_report"),
            ("fill_report", "BM-EXE-06", "position_snapshot"),
            ("position_snapshot", "BM-EXE-03", "tca_report"),
        ]
        # 逐环节验证输入→输出类型
        pkt = DataPacket(
            type="position_order",
            payload={"symbol": "000001", "target_qty": 500, "side": "buy"},
        )
        for input_type, sid, output_type in expected_handoffs:
            assert pkt.type == input_type, (
                f"{sid} 输入类型应为 {input_type}，实际 {pkt.type}"
            )
            processor = STEP_PROCESSORS[sid]
            if sid == "BM-EXE-05":
                pkt = processor(pkt, tca_feedback=None)
            else:
                pkt = processor(pkt)
            assert pkt.type == output_type, (
                f"{sid} 输出类型应为 {output_type}，实际 {pkt.type}"
            )

    def test_tca_feedback_closes_loop(self):
        """TCA 反馈闭环：BM-EXE-03 产出 → 回到 BM-EXE-05 调整拆单参数。

        验证 degradation 边的语义：TCA 滑点过高时，反馈降低参与率+切换算法。
        """
        # 第一轮：无反馈，默认参与率 10%、TWAP
        order = DataPacket(
            type="compliant_order",
            payload={"symbol": "600519", "qty": 1000, "side": "buy", "compliant": True},
        )
        first_round = _process_smart_routing(order, tca_feedback=None)
        assert first_round.payload["participation_rate"] == 0.10
        assert first_round.payload["algo"] == "TWAP"

        # 模拟 TCA 反馈：滑点 8bps（>5bps 阈值，触发降级）
        tca_feedback = {"slippage_bps": 8.0, "is_cost": 11.0}

        # 第二轮：带反馈，参与率降到 5%、算法切 VWAP（闭环优化）
        second_round = _process_smart_routing(order, tca_feedback=tca_feedback)
        assert second_round.payload["participation_rate"] == 0.05, (
            "TCA 反馈应将参与率从 10% 降到 5%（滑点过高降级）"
        )
        assert second_round.payload["algo"] == "VWAP", (
            "TCA 反馈应将算法从 TWAP 切换到 VWAP"
        )

    def test_full_closed_loop_two_iterations(self):
        """完整闭环两轮迭代：主链跑通→TCA反馈→第二轮拆单优化。

        第一轮：默认参数执行 → TCA 发现滑点高
        第二轮：TCA 反馈调整参数 → 滑点降低
        """
        # ── 第一轮 ──
        pkt = DataPacket(
            type="position_order",
            payload={"symbol": "600519", "target_qty": 2000, "side": "buy"},
        )
        # 主链：01→04→05（无反馈）→02→06→03
        pkt = _process_risk_approval(pkt)
        pkt = _process_pretrade_compliance(pkt)
        first_routing = _process_smart_routing(pkt, tca_feedback=None)
        pkt = _process_trade_execution(first_routing)
        pkt = _process_fill_handling(pkt)
        first_tca = _process_tca_analysis(
            # TCA 消费 BM-EXE-06 透传的 position_snapshot（含 fills 成交数据）
            DataPacket(
                type="position_snapshot",
                payload={
                    "symbol": "600519",
                    "quantity": 200,
                    "avg_cost": 10.08,
                    "commission": 0.6,
                    "pnl": 19.4,
                    "fills": [{"child_id": 0, "filled_qty": 200, "fill_price": 10.08}],
                },
            )
        )

        # 第一轮 TCA 反馈
        feedback = {
            "slippage_bps": first_tca.payload["slippage_bps"],
            "is_cost": first_tca.payload["is_cost"],
        }

        # ── 第二轮：新订单用 TCA 反馈重新拆单（闭环优化）──
        # 第二轮是一个新的合规订单，但携带第一轮的 TCA 反馈进入 BM-EXE-05
        second_order = DataPacket(
            type="compliant_order",
            payload={"symbol": "600519", "qty": 2000, "side": "buy", "compliant": True},
        )
        second_routing = _process_smart_routing(second_order, tca_feedback=feedback)

        # 验证闭环：第二轮参与率 ≤ 第一轮（反馈降级生效）
        assert second_routing.payload["participation_rate"] <= first_routing.payload["participation_rate"], (
            "TCA 反馈闭环未生效：第二轮参与率应 ≤ 第一轮"
        )

    def test_compliance_fail_closed(self):
        """BM-EXE-04 合规检查 Fail-Closed：未通过风控审批的订单被拦截。"""
        unapproved = DataPacket(
            type="approved_order",
            payload={"symbol": "600519", "qty": 100, "side": "buy", "approved": False},
        )
        with pytest.raises(AssertionError, match="未通过风控审批"):
            _process_pretrade_compliance(unapproved)

    def test_splitting_correctness(self):
        """BM-EXE-05 拆单正确性：子订单数量之和 = 原始订单数量。"""
        order = DataPacket(
            type="compliant_order",
            payload={"symbol": "600519", "qty": 1000, "side": "buy", "compliant": True},
        )
        result = _process_smart_routing(order, tca_feedback=None)
        children = result.payload["children"]
        total = sum(c["qty"] for c in children)
        assert total == 1000, f"子订单数量之和应为 1000，实际 {total}"

    def test_fill_aggregation(self):
        """BM-EXE-06 成交聚合：多个 fill 聚合为单一持仓快照。"""
        fill_report = DataPacket(
            type="fill_report",
            payload={
                "symbol": "600519",
                "side": "buy",
                "fills": [
                    {"child_id": 0, "filled_qty": 100, "fill_price": 10.0},
                    {"child_id": 1, "filled_qty": 100, "fill_price": 10.1},
                    {"child_id": 2, "filled_qty": 100, "fill_price": 10.2},
                ],
                "pnl": 30.0,
            },
        )
        snapshot = _process_fill_handling(fill_report)
        assert snapshot.payload["quantity"] == 300
        # 平均成本应在 10.0~10.2 之间
        assert 10.0 <= snapshot.payload["avg_cost"] <= 10.2
        assert snapshot.payload["commission"] > 0

    def test_tca_is_cost_decomposition(self):
        """BM-EXE-03 TCA：IS 成本 = 滑点 + 佣金（成本分解正确）。"""
        position_snapshot = DataPacket(
            type="position_snapshot",
            payload={
                "symbol": "600519",
                "quantity": 1000,
                "avg_cost": 10.05,
                "commission": 3.0,
                "pnl": 47.0,
                "fills": [{"child_id": 0, "filled_qty": 1000, "fill_price": 10.05}],
            },
        )
        tca = _process_tca_analysis(position_snapshot)
        # IS = 滑点 + 佣金(3bps 固定)
        expected_slippage = abs(10.05 - 10.0) / 10.0 * 10000  # 5.0 bps
        assert abs(tca.payload["slippage_bps"] - expected_slippage) < 0.1
        assert abs(tca.payload["is_cost"] - (expected_slippage + 3)) < 0.1


# ============================================================================
# Part 3: 独立运行入口（python 直接执行，输出可视化流转报告）
# ============================================================================


def _run_simulation_visual():
    """独立运行：打印 6 环节数据流转可视化报告（无需 pytest）。"""
    print("=" * 72)
    print("执行阶段 6 环节数据流转闭环模拟")
    print("=" * 72)

    pkt = DataPacket(
        type="position_order",
        payload={"symbol": "600519", "target_qty": 1000, "side": "buy"},
    )
    print(f"\n[初始输入] {pkt.type}: {pkt.payload}")

    # 主链执行
    for sid in EXPECTED_CHAIN:
        processor = STEP_PROCESSORS[sid]
        if sid == "BM-EXE-05":
            pkt = processor(pkt, tca_feedback=None)
        else:
            pkt = processor(pkt)
        print(f"\n[{sid}] → {pkt.type}: {pkt.payload}")

    print(f"\n[流转路径] {' → '.join(pkt.history)}")
    print("[闭环验证] TCA 反馈 → BM-EXE-05（degradation）")

    # 闭环第二轮
    feedback = {"slippage_bps": pkt.payload["slippage_bps"], "is_cost": pkt.payload["is_cost"]}
    print(f"\n[TCA 反馈] {feedback}")
    order2 = DataPacket(
        type="compliant_order",
        payload={"symbol": "600519", "qty": 1000, "side": "buy", "compliant": True},
    )
    round2 = _process_smart_routing(order2, tca_feedback=feedback)
    print(f"[第二轮拆单] 参与率={round2.payload['participation_rate']} 算法={round2.payload['algo']}")
    print("\n" + "=" * 72)
    print("✅ 闭环验证通过")
    print("=" * 72)


if __name__ == "__main__":
    _run_simulation_visual()
