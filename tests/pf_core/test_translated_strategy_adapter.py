# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.pf_core.test_translated_strategy_adapter
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.translated_strategy_adapter; zephyr.pf_core.strategy_engine.framework_composer
# [CONSUMERS] pytest（SOP Step 5 循环验收）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 测试禁写生产路径（假翻译件/假注册表全走 tmp_path）；不触 ClickHouse；
#   面板=build() 原样（忠实重放断言）；composer 路由仅 STR- 前缀
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] pytest tests/pf_core/test_translated_strategy_adapter.py
# [A_module] module_id=MOD-BT-196-tests | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""STR-* 翻译件面板适配器单测（MOD-BT-196）。

覆盖面:
    - 路由判据（STR- 前缀 vs kebab）
    - 注册表解析（命中/缺条目/非 translated 件拒绝）
    - build() 契约（忠实重放/缓存单次调用/契约不符拒绝）
    - composer _build_member_panels 的 STR- 路由（假翻译件端到端，不触 CH）
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from zephyr.pf_core.strategy_engine.translated_strategy_adapter import (
    TranslatedAdapterError,
    build_translated_weight_panel,
    build_translated_weights,
    clear_caches,
    is_translated_member,
    prefetch_translated_panels,
    resolve_code_path,
)

_S = "2024-01-01"
_E = "2024-01-10"

_FAKE_MODULE = '''
import pandas as pd

CALLS = {"n": 0}


def build(start, end):
    CALLS["n"] += 1
    idx = pd.date_range(start, periods=5, freq="B")
    w = pd.DataFrame(0.0, index=idx, columns=["600000", "000852"])
    w.iloc[2:, 0] = 0.5
    w.iloc[3:, 1] = 0.25
    closes = pd.DataFrame({"600000": [10.0, 11.0, 12.0, 13.0, 14.0],
                           "000852": [5000.0, 5100.0, 5200.0, 5300.0, 5400.0]}, index=idx)
    return w, closes
'''


@pytest.fixture(autouse=True)
def _clean_caches():
    clear_caches()
    yield
    clear_caches()


@pytest.fixture()
def fake_registry(tmp_path: Path) -> Path:
    """tmp 翻译件 + tmp 注册表（STR-TEST-001→假 c4 件）。"""
    tdir = tmp_path / "translated"
    tdir.mkdir()
    (tdir / "c4_faketest.py").write_text(_FAKE_MODULE, encoding="utf-8")
    reg = tmp_path / "strategy_registry.yaml"
    reg.write_text(
        yaml.safe_dump(
            {
                "strategies": [
                    {"strategy_id": "STR-TEST-001", "code_path": str(tdir / "c4_faketest.py")},
                    {"strategy_id": "STR-BAD-001", "code_path": "src/zephyr/pf_core/default_equity_strategy.py"},
                    {"strategy_id": "STR-NOPATH-001"},
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return reg


class TestRouting:
    def test_prefix_predicate(self):
        assert is_translated_member("STR-VREV-025") is True
        assert is_translated_member("topn-momentum") is False
        assert is_translated_member("str-lower") is False  # 大小写敏感，防误路由

    def test_resolve_code_path(self, fake_registry: Path):
        cp = resolve_code_path("STR-TEST-001", fake_registry)
        assert cp.endswith("c4_faketest.py")

    @pytest.mark.parametrize("sid", ["STR-BAD-001", "STR-NOPATH-001", "STR-GHOST-999"])
    def test_resolve_rejects(self, fake_registry: Path, sid: str):
        with pytest.raises(TranslatedAdapterError):
            resolve_code_path(sid, fake_registry)


class TestBuildContract:
    def test_faithful_replay(self, fake_registry: Path):
        data, panel = build_translated_weight_panel("STR-TEST-001", ["600000"], _S, _E, fake_registry)
        assert isinstance(panel, pd.DataFrame) and not panel.empty
        assert list(panel.columns) == ["600000", "000852"]
        assert float(panel.iloc[2, 0]) == 0.5  # build() 原样（禁再加工）
        assert float(panel.iloc[0, 0]) == 0.0
        assert not data.empty and set(data.columns) == {"close"}
        assert {str(ix[0]) for ix in data.index} == {"600000", "000852"}

    def test_build_called_once_per_window(self, fake_registry: Path):
        # 同 (sid,start,end) 二次构建走缓存——适配器缓存的模块实例 CALLS 计数=1
        from zephyr.pf_core.strategy_engine.translated_strategy_adapter import _MODULE_CACHE

        build_translated_weights("STR-TEST-001", _S, _E, fake_registry)
        build_translated_weights("STR-TEST-001", _S, _E, fake_registry)
        assert len(_MODULE_CACHE) == 1
        cached_mod = next(iter(_MODULE_CACHE.values()))
        assert cached_mod.CALLS["n"] == 1  # 适配器侧两次请求，翻译件 build 只执行一次

    def test_prefetch_skips_failures(self, fake_registry: Path):
        panels = prefetch_translated_panels(
            ["STR-TEST-001", "STR-GHOST-999", "topn-momentum"], _S, _E, fake_registry
        )
        assert set(panels) == {"STR-TEST-001"}


class TestComposerRoute:
    def test_member_panel_routes_to_adapter(self, fake_registry: Path, monkeypatch):
        """composer _build_member_panels 对 STR- 成员走适配器（不触 StrategyRunner/CH）。"""
        from zephyr.pf_core.strategy_engine.framework_composer import (
            FrameworkBacktestConfig,
            FrameworkPlan,
            PlanWeight,
            _build_member_panels,
        )

        plan = FrameworkPlan(
            plan_id="fw-test", name="t", risk_profile="balanced", description="",
            weights=(PlanWeight("STR-TEST-001", 0.5, ""), PlanWeight("default-equity", 0.5, "")),
        )
        # kebab 成员打桩为空面板（证明 STR 路由独立于 kebab 成败）
        class _FakeRunner:
            def build_weight_panel(self, *a, **k):
                return pd.DataFrame(), pd.DataFrame()

        import zephyr.pf_core.strategy_engine.framework_composer as fc

        monkeypatch.setattr(
            "zephyr.pf_core.strategy_engine.strategy_runner.StrategyRunner", _FakeRunner
        )
        # 路由测试注入 tmp 注册表（composer 路径无 registry 参数，适配器读模块级真源路径）
        monkeypatch.setattr(
            "zephyr.pf_core.strategy_engine.translated_strategy_adapter.STRATEGY_REGISTRY_PATH",
            fake_registry,
        )
        data, panels, skipped = _build_member_panels(plan, ["600000"], _S, _E, FrameworkBacktestConfig())
        assert "STR-TEST-001" in panels  # 适配器面板进入合成
        assert ("default-equity", "panel/data empty") in [tuple(s) for s in skipped]
        assert set(data.columns) == {"close"}  # 首个非空成员=STR 适配器（closes 兜底 data 生效）
