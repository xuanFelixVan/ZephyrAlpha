# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_test_memo90_registry_entries | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_memo90_registry_entries
# [TESTS] docs/01_policies_and_standards/_registry/catalogs/{benchmark,cost_model,risk_limit,universe}_registry.yaml
# [TTL] task_bound
"""90 号 Phase1/2 注册表条目施工校验（AI-NIGHT-001 专项批）。

覆盖条目：
  - P1① CST-T0-001 做T成本条目（cost_model_registry）
  - P1② 中证1000/中证2000/万得全A（benchmark_registry）
  - P2#15 universe_registry 两维字段（eligibility/data_tier）
  - P2#17 RLM-POSITION-022 单票≤5% NAV 硬编码限额归并登记（risk_limit_registry）
"""

from __future__ import annotations

import yaml

from zephyr.shared.io.paths import REPO_ROOT

_CATALOGS = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"


def _load(name: str) -> dict:
    with open(_CATALOGS / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class TestMemo90P1CostModel:
    def test_cst_t0_001_registered(self):
        entries = {e["cost_model_id"]: e for e in _load("cost_model_registry.yaml")["cost_models"]}
        entry = entries["CST-T0-001"]
        comp = entry["components"]
        # 最低佣金 5 元显式建模（90 号 §5 裁定③）
        assert comp["commission"]["min"] == 5.0
        # 印花税卖出单边万5
        assert comp["stamp_duty"]["rate"] == 0.0005
        assert comp["stamp_duty"]["side"] == "sell_only"
        # 滑点×2 双边 + 分档
        assert comp["slippage"]["params"]["round_trip_multiplier"] == 2
        assert comp["slippage"]["params"]["tier_high_liquidity_bps"] == 10
        assert comp["slippage"]["params"]["tier_daban_event_bps"] == 20
        # 开仓硬前置：预期价差≥0.3%
        assert comp["open_precondition"]["min_expected_edge_rate"] == 0.003
        # testing 态（production 启用挂起待 Owner）
        assert entry["status"] == "candidate"


class TestMemo90P1Benchmarks:
    """90 号 §13 裁定：sleeve 级多基准——打板/事件→中证2000；多因子→中证1000 或万得全A。"""

    def test_three_sleeve_benchmarks_registered(self):
        entries = {e["benchmark_id"]: e for e in _load("benchmark_registry.yaml")["benchmarks"]}
        expected = {
            "BMK-INDEX-005": "000852",  # 中证1000
            "BMK-INDEX-006": "932000",  # 中证2000
            "BMK-INDEX-007": "881001",  # 万得全A
        }
        for bmk_id, code in expected.items():
            assert bmk_id in entries, f"{bmk_id} 未登记"
            assert any(code in str(a) for a in entries[bmk_id]["aliases"]), f"{bmk_id} aliases 缺代码 {code}"
            assert entries[bmk_id]["benchmark_type"] == "index"
            assert entries[bmk_id]["status"] == "candidate"


class TestMemo90P2UniverseTwoDim:
    """90 号 §15 裁定：两维精简（交易准入×数据覆盖），P0-P3 deprecated。"""

    def test_all_universes_have_two_dim_fields(self):
        entries = _load("universe_registry.yaml")["universes"]
        assert len(entries) >= 6
        for e in entries:
            assert e.get("eligibility") in ("eligible", "restricted", "prohibited"), (
                f"{e['universe_id']} eligibility 缺失/非法: {e.get('eligibility')}"
            )
            assert e.get("data_tier") in ("realtime", "eod"), (
                f"{e['universe_id']} data_tier 缺失/非法: {e.get('data_tier')}"
            )

    def test_known_assignments(self):
        entries = {e["universe_id"]: e for e in _load("universe_registry.yaml")["universes"]}
        # 打板池/全A可交易池：eligible + realtime
        assert entries["UNI-DYNAMIC-001"]["eligibility"] == "eligible"
        assert entries["UNI-DYNAMIC-001"]["data_tier"] == "realtime"
        assert entries["UNI-RULE-001"]["eligibility"] == "eligible"
        # 事件驱动池 candidate：restricted；regime 验证篮子非生产：restricted
        assert entries["UNI-RULE-002"]["eligibility"] == "restricted"
        assert entries["UNI-BASKET-001"]["eligibility"] == "restricted"


class TestMemo90P2RiskLimitConsolidation:
    """90 号 §17 裁定：散落硬编码限额归并 risk_limit_registry 声明式登记。"""

    def test_single_instrument_cap_registered(self):
        entries = {e["risk_limit_id"]: e for e in _load("risk_limit_registry.yaml")["risk_limits"]}
        entry = entries["RLM-POSITION-027"]
        assert entry["limit_type"] == "position"
        assert entry["threshold_value"] == 5.0
        assert entry["threshold_unit"] == "%"
        assert entry["breach_action"] == "block"
        # 代码真源锚点：PositionLimitConfig.single_instrument_cap
        assert "position_limit_enforcer" in entry["code_symbol"]
