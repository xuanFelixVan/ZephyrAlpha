# [BLUEPRINT] MOD-INF-060 | 待统筹登记（10号文 §4 Phase 2.3）| §test
# [A_test] module_id: MOD-INF-060 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""GgufModelManager 单元测试（MOD-INF-060，10号文 §4 Phase 2.3）。

覆盖：真实预算表加载与结构校验 / fail-closed（表缺失、未知时段、未登记模型）/
单模型超时段配额与硬上限阻断 / 合计超配额阻断 / 已载清单含未登记模型阻断 /
period_from_time 时段映射（含子窗口优先级与跨日窗口）/ sync_with_discovery 对账 /
to_pool_budgets 折算 + local_llm_pool 消费真源表后超预算拒载（10号文缺口 2.3 验收口径）。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.intelligence.gguf_model_manager import (
    DEFAULT_BUDGET_TABLE_PATH,
    GgufBudgetTableError,
    GgufModelManager,
    load_budget_table,
    period_from_time,
)
from zephyr.intelligence.local_llm_pool import LocalLlmPool, LocalLlmPoolConfig, LocalModelSpec

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL_TABLE = _REPO_ROOT / DEFAULT_BUDGET_TABLE_PATH


def _table_dict() -> dict:
    return {
        "hard_cap_gb": 21.6,
        "period_quotas": {
            "premarket": {"window": ["08:30", "09:00"], "inference_quota_gb": 10.0},
            "intraday": {"window": ["09:15", "15:00"], "inference_quota_gb": 10.0},
            "midday": {"window": ["11:30", "13:00"], "inference_quota_gb": 4.0},
            "postmarket": {"window": ["15:00", "15:30"], "inference_quota_gb": 4.0},
            "night": {"window": ["15:30", "08:30"], "inference_quota_gb": 4.0},
        },
        "models": [
            {"name": "qwen3:8b", "role": "primary", "quant": "Q4_K_M", "vram_gb": 5.4},
            {"name": "qwen3-coder:30b", "role": "backup", "quant": "Q4_K_M", "vram_gb": 19.0},
        ],
    }


def _write_table(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "budget.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


class TestLoadTable:
    def test_real_config_loads(self) -> None:
        mgr = load_budget_table(_REAL_TABLE)
        assert mgr.hard_cap_gb == 21.6
        assert set(mgr.periods) == {"premarket", "intraday", "midday", "postmarket", "night"}
        assert "qwen3:8b" in mgr.registered_models

    def test_missing_file_fail_closed(self, tmp_path: Path) -> None:
        with pytest.raises(GgufBudgetTableError):
            load_budget_table(tmp_path / "nope.yaml")

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda d: d.update({"hard_cap_gb": -1}),
            lambda d: d.update({"hard_cap_gb": "x"}),
            lambda d: d.pop("period_quotas"),
            lambda d: d["period_quotas"]["intraday"].update({"inference_quota_gb": 0}),
            lambda d: d["period_quotas"]["intraday"].update({"inference_quota_gb": 99.0}),
            lambda d: d.pop("models"),
            lambda d: d["models"].append({"name": "qwen3:8b", "vram_gb": 1.0}),
            lambda d: d["models"].append({"name": "bad"}),
            lambda d: d["models"].append({"name": "neg", "vram_gb": -0.5}),
        ],
    )
    def test_invalid_table_fail_closed(self, tmp_path: Path, mutate) -> None:
        data = _table_dict()
        mutate(data)
        with pytest.raises(GgufBudgetTableError):
            load_budget_table(_write_table(tmp_path, data))


class TestCheckLoad:
    @pytest.fixture()
    def mgr(self, tmp_path: Path) -> GgufModelManager:
        return load_budget_table(_write_table(tmp_path, _table_dict()))

    def test_primary_model_allowed_intraday(self, mgr: GgufModelManager) -> None:
        d = mgr.check_load("qwen3:8b", period="intraday")
        assert d.allowed is True

    def test_unregistered_model_blocked(self, mgr: GgufModelManager) -> None:
        d = mgr.check_load("llama3:70b", period="night")
        assert d.allowed is False
        assert "未登记" in d.reasons[0]

    def test_unknown_period_blocked(self, mgr: GgufModelManager) -> None:
        d = mgr.check_load("qwen3:8b", period=" lunchtime ")
        assert d.allowed is False
        assert "未知时段" in d.reasons[0]

    def test_over_period_quota_blocked_all_periods(self, mgr: GgufModelManager) -> None:
        for period in ("premarket", "intraday", "midday", "postmarket", "night"):
            d = mgr.check_load("qwen3-coder:30b", period=period)
            assert d.allowed is False, period
            assert any("超时段配额" in r for r in d.reasons)

    def test_sum_over_quota_blocked(self, mgr: GgufModelManager) -> None:
        # night 配额 4GB：已载 5.4GB 的 qwen3:8b 后再载任何模型均超
        d = mgr.check_load("qwen3:8b", period="night", loaded_models=["qwen3:8b"])
        assert d.allowed is False
        assert any("合计超时段配额" in r for r in d.reasons)

    def test_sum_within_quota_allowed(self, mgr: GgufModelManager) -> None:
        d = mgr.check_load("qwen3:8b", period="intraday", loaded_models=[])
        assert d.allowed is True

    def test_loaded_unknown_model_blocked(self, mgr: GgufModelManager) -> None:
        d = mgr.check_load("qwen3:8b", period="intraday", loaded_models=["ghost:1b"])
        assert d.allowed is False
        assert any("未登记" in r for r in d.reasons)

    def test_over_hard_cap_blocked(self, tmp_path: Path) -> None:
        data = _table_dict()
        data["models"].append({"name": "giant:180b", "vram_gb": 30.0})
        data["period_quotas"]["night"]["inference_quota_gb"] = 21.6  # 时段放行以专测硬上限
        mgr = load_budget_table(_write_table(tmp_path, data))
        d = mgr.check_load("giant:180b", period="night")
        assert d.allowed is False
        assert any("硬上限" in r for r in d.reasons)


class TestPeriodFromTime:
    @pytest.mark.parametrize(
        ("h", "m", "expected"),
        [
            (8, 30, "premarket"),
            (8, 59, "premarket"),
            (9, 15, "intraday"),
            (10, 0, "intraday"),
            (11, 30, "midday"),
            (12, 30, "midday"),  # 子窗口优先于 intraday
            (13, 0, "intraday"),
            (14, 59, "intraday"),
            (15, 0, "postmarket"),
            (15, 29, "postmarket"),
            (15, 30, "night"),
            (23, 59, "night"),
            (0, 0, "night"),
            (8, 29, "night"),
        ],
    )
    def test_windows(self, h: int, m: int, expected: str) -> None:
        assert period_from_time(h, m) == expected

    def test_gap_between_premarket_and_intraday(self) -> None:
        assert period_from_time(9, 5) == "intraday"


class TestSyncWithDiscovery:
    def test_drift_report(self, tmp_path: Path) -> None:
        mgr = load_budget_table(_write_table(tmp_path, _table_dict()))
        discovered = [
            type("DM", (), {"name": "qwen3:8b"})(),
            type("DM", (), {"name": "pulled-not-registered:1b"})(),
        ]
        report = mgr.sync_with_discovery(discovered)
        assert report.pulled_but_unregistered == ("pulled-not-registered:1b",)
        assert report.registered_but_not_pulled == ("qwen3-coder:30b",)
        assert report.registered == ("qwen3:8b",)

    def test_real_config_matches_live_inventory(self) -> None:
        """真实预算表登记清单与 2026-08-30 Ollama /api/tags 实证清单一致（9 个）。"""
        mgr = load_budget_table(_REAL_TABLE)
        assert len(mgr.registered_models) == 9


class TestPoolBudgetsConsumption:
    def test_to_pool_budgets_values(self, tmp_path: Path) -> None:
        mgr = load_budget_table(_write_table(tmp_path, _table_dict()))
        budgets = mgr.to_pool_budgets()
        assert budgets.intraday_gb == 10.0
        assert budgets.postmarket_gb == 4.0

    def test_pool_blocks_over_budget_load(self, tmp_path: Path) -> None:
        """10号文缺口 2.3 验收：local_llm_pool 消费真源表，超预算加载被阻断。"""
        mgr = load_budget_table(_write_table(tmp_path, _table_dict()))
        pool = LocalLlmPool(config=LocalLlmPoolConfig(budgets=mgr.to_pool_budgets()))
        pool.register_model(LocalModelSpec(name="qwen3:8b", quant="Q4_K_M", vram_gb=5.4, role="primary"))
        pool.register_model(LocalModelSpec(name="qwen3-coder:30b", quant="Q4_K_M", vram_gb=19.0, role="backup"))
        ok = pool.request_load("qwen3:8b", period="intraday")
        assert ok.loaded is True
        blocked = pool.request_load("qwen3-coder:30b", period="intraday")
        assert blocked.loaded is False
        assert blocked.degrade_to_api is True
