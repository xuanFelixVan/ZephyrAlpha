# [BLUEPRINT] MOD-BT-197 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_generate_framework_plan_from_tdm
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.generate_framework_plan_from_tdm
# [CONSUMERS] pytest（SOP Step 5 循环验收）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 测试禁写生产路径（TDM/plans 全走 tmp_path 注入）；不触 ClickHouse
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] pytest tests/backtest/test_generate_framework_plan_from_tdm.py
# [A_module] module_id=MOD-BT-197-tests | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fw-tdm-current 方案表生成器单测（MOD-BT-197）。

覆盖面:
    - 生成/写入/写后自校验（composer loader 全文件重解析）
    - 幂等（同 TDM 状态重跑零 diff 零写；TDM 变更后再生成有 diff）
    - 预设保护（块外字节零改动）
    - fail-closed（sleeves Σ≠1 / 重复 ref 拒绝）
    - --check 只报告不写
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "backtest"))

from generate_framework_plan_from_tdm import (  # noqa: E402
    PLAN_ID,
    generate,
    load_sleeves,
    normalize_weights,
    render_plan_block,
)

_BASE_PLANS = """schema_version: "1.1.0"
ttl: permanent
doc_type: config
title: 整装方案配置真源（测试基线）
status: active
version: "1.1.0"
owner: ZephyrAlpha-Owner

plans:
  - plan_id: fw-defensive
    name_zh: 防御型整装方案
    risk_profile: defensive
    description: 测试预设（生成器不得改动本块）
    weights:
      - strategy_id: default-equity
        weight: 1.0
"""

_TDM = """portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 0.7, activation_state: null}
  - {strategy_ref: STR-TEST-001, weight: 0.3, activation_state: [capitulation, accumulation]}
"""


@pytest.fixture()
def env(tmp_path: Path) -> dict[str, Path]:
    tdm = tmp_path / "trading_decision_map.yaml"
    tdm.write_text(_TDM, encoding="utf-8")
    plans = tmp_path / "framework_plans.yaml"
    plans.write_text(_BASE_PLANS, encoding="utf-8")
    return {"tdm": tdm, "plans": plans}


class TestGenerate:
    def test_generate_write_and_verify(self, env):
        out = generate(plans_path=env["plans"], tdm_path=env["tdm"])
        assert out["changed"] and out["written"]
        assert out["verify"]["ok"] and not out["verify"]["errors"]
        assert out["members"] == 2 and out["sum_weight"] == 1.0
        text = env["plans"].read_text(encoding="utf-8")
        assert f"plan_id: {PLAN_ID}" in text
        assert "STR-TEST-001" in text
        assert "capitulation" in text  # 激活态落 provenance/role（静态模式）

    def test_idempotent_rerun_zero_diff(self, env):
        generate(plans_path=env["plans"], tdm_path=env["tdm"])
        before = env["plans"].read_text(encoding="utf-8")
        out = generate(plans_path=env["plans"], tdm_path=env["tdm"])
        assert not out["changed"] and not out["written"]
        assert "no_change" in out["action"]
        assert env["plans"].read_text(encoding="utf-8") == before

    def test_regenerate_after_tdm_change(self, env):
        generate(plans_path=env["plans"], tdm_path=env["tdm"])
        env["tdm"].write_text(
            _TDM.replace("weight: 0.7", "weight: 0.6").replace("weight: 0.3", "weight: 0.4"),
            encoding="utf-8",
        )
        out = generate(plans_path=env["plans"], tdm_path=env["tdm"])
        assert out["changed"] and out["verify"]["ok"]
        text = env["plans"].read_text(encoding="utf-8")
        assert "weight: 0.600000" in text

    def test_preset_block_byte_untouched(self, env):
        generate(plans_path=env["plans"], tdm_path=env["tdm"])
        text = env["plans"].read_text(encoding="utf-8")
        assert _BASE_PLANS in text  # 块外（预设+头部）字节级不动

    def test_check_mode_no_write(self, env):
        out = generate(plans_path=env["plans"], tdm_path=env["tdm"], check=True)
        assert out["changed"] and not out["written"]
        assert PLAN_ID not in env["plans"].read_text(encoding="utf-8")


class TestFailClosed:
    def test_sum_violation_rejected(self, tmp_path: Path):
        tdm = tmp_path / "tdm.yaml"
        tdm.write_text(
            "portfolio_plan:\n  sleeves:\n"
            "  - {strategy_ref: default-equity, weight: 0.7}\n"
            "  - {strategy_ref: STR-TEST-001, weight: 0.2}\n",
            encoding="utf-8",
        )
        with pytest.raises(RuntimeError, match="Σ≠1|合计≠1"):
            load_sleeves(tdm)

    def test_duplicate_ref_rejected(self, tmp_path: Path):
        tdm = tmp_path / "tdm.yaml"
        tdm.write_text(
            "portfolio_plan:\n  sleeves:\n"
            "  - {strategy_ref: default-equity, weight: 0.5}\n"
            "  - {strategy_ref: default-equity, weight: 0.5}\n",
            encoding="utf-8",
        )
        with pytest.raises(RuntimeError, match="重复"):
            load_sleeves(tdm)

    def test_missing_tdm_rejected(self, tmp_path: Path):
        with pytest.raises(RuntimeError, match="缺失"):
            load_sleeves(tmp_path / "nope.yaml")


class TestNormalize:
    def test_residual_adjust_exact_unit_sum(self):
        sleeves = [
            {"strategy_ref": "a", "weight": 1 / 3},
            {"strategy_ref": "b", "weight": 1 / 3},
            {"strategy_ref": "c", "weight": 1 / 3},
        ]
        items = normalize_weights(sleeves)
        assert sum(w for _, w, _ in items) == 1_000_000  # 整数化余量归大权重，Σ 恰=1e6

    def test_render_deterministic(self):
        sleeves = [{"strategy_ref": "a", "weight": 0.6, "activation_state": None},
                   {"strategy_ref": "STR-X", "weight": 0.4, "activation_state": ["r"]}]
        b1 = render_plan_block(sleeves, "deadbeef1234")
        b2 = render_plan_block(sleeves, "deadbeef1234")
        assert b1 == b2  # 纯确定性渲染（无时间戳/无随机）


class TestComposerParse:
    def test_generated_plan_loads_via_composer(self, env):
        from zephyr.pf_core.strategy_engine.framework_composer import get_framework_plan

        generate(plans_path=env["plans"], tdm_path=env["tdm"])
        plan = get_framework_plan(PLAN_ID, env["plans"])
        assert plan.strategy_ids == ("default-equity", "STR-TEST-001")
        assert abs(plan.total_weight - 1.0) <= 1e-6
