# [BLUEPRINT] MOD-FWCOMP-001 | docs/03_modules/_domain_portfolio_core/framework_composer_blueprint.md | §RSC-2
# [MODULE] tests.pf_core.test_framework_composer_shrinkage
# [DOMAIN] D_PF_CORE
# [A_module] module_id=MOD-TEST-FWCOMP-SHRINK | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #RSC-2 裁定#270
"""RSC-2「Shrinkage 进整装回测」单测（裁定#270，双轨披露制）。

覆盖:
  - 默认关（shrinkage_by_date=None/空）→ 引擎选择 DefaultBacktestEngine 原路，
    result["shrinkage"] is None、metrics 不落 shrinkage_disclosure 键（零漂移锚）
  - schedule 归一化：钳制 [0,1] 只减不增 / None·空=关 / 四类非法 fail-closed
  - run_framework_backtest 节流口径：ShrinkageBacktestEngine 生效、披露键齐、
    metrics.shrinkage_disclosure 落盘
  - shrinkage_diff_stamp：纯函数数学（方向 on−off/回撤差/零差值恒等）
  - run_framework_backtest_shrinkage_dual：关/开两跑+差值章；off 侧失败不静默
  - 引擎参数透传：ShrinkageBacktestEngine(enable_stk_limit_provider=False) 生效
    （裁定#270 同 commit 修复的构造丢参缺陷）
  - PIT as-of join：早于 schedule 首条=1.0（不查未来）

测试隔离: 一律 tmp_path 落产物（ARCH-BENCH-LEAK-001，禁写 data/ 生产路径）；
引擎行情/信号为进程内合成面板（**无行情 CH 取数**）。如实披露：引擎侧仍有一条数据腿
触 CH=P0-3 幸存者过滤器读上市注册表（∴ 合成标的选在市代码，CH 不可达时该腿 fail-open
不过滤）；P0-2 涨跌停腿经 enable_stk_limit_provider=False 关闭保证确定性。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.backtest.implementations.shrinkage_engine import ShrinkageBacktestEngine
from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.pf_core.strategy_engine.framework_composer import (
    FrameworkBacktestConfig,
    FrameworkValidationError,
    _normalize_shrinkage_schedule,
    shrinkage_diff_stamp,
)

# ── 合成数据构造（进程内，零 CH/零生产路径写入）──────────────────────────

#: 合成面板标的必须是**在市**真实 6 位码：引擎 P0-3 幸存者过滤器（PitUniverseProvider）
#: 对 A 股形态代码按上市-退市窗口做证据制判定，旧选题 600001/600002/600003 在注册表里
#: 分别于 2009/2006/2010 退市（=正证据）⇒ 2026 窗口全员剔除 → 引擎零成交 → P0-4 合理性
#: 护栏如实拦截 trades_count=0 空跑（护栏是对的，错在选题）。改用同在市代码（同域先例
#: test_framework_composer.py e2e 用 600519/000858）；CH 不可达时 provider 自身降级
#: fail-open（返回 None=不过滤），两环境皆通。
_SYMBOLS = ["600519", "000858", "600036"]
_N_DAYS = 30


def _make_market_data(n_days: int = _N_DAYS, seed: int = 11) -> pd.DataFrame:
    """合成日 K（MultiIndex symbol×date，OHLCV；轻微正漂移——满仓与节流曲线可分辨）。"""
    import numpy as np

    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", periods=n_days, freq="B")
    frames = []
    for sym in _SYMBOLS:
        close = 100.0
        rows = []
        for t in range(n_days):
            ret = 0.002 + rng.normal(0, 0.012)
            close = close * (1 + ret)
            rows.append(
                {
                    "symbol": sym,
                    "date": dates[t],
                    "open": close,
                    "high": close * 1.01,
                    "low": close * 0.99,
                    "close": close,
                    "volume": 1_000_000,
                }
            )
        frames.append(pd.DataFrame(rows))
    return pd.concat(frames, ignore_index=True).set_index(["symbol", "date"]).sort_index()


def _make_signals(data: pd.DataFrame) -> pd.DataFrame:
    """等权信号面板（date×symbol，值恒 1.0 → 引擎归一化后 1/N 满仓）。"""
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame({sym: 1.0 for sym in _SYMBOLS}, index=pd.DatetimeIndex(dates, name="date"))


def _shrunken_equity(base_curve: list[dict], shocks: dict[str, float]) -> list[dict]:
    """从基准曲线派生"被收缩"曲线（逐日乘系数）——diff_stamp 纯函数验证输入。"""
    return [
        {"timestamp": p["timestamp"], "equity": p["equity"] * shocks.get(p["timestamp"], 1.0)}
        for p in base_curve
    ]


def _throttled_equity(base_curve: list[dict], factors: dict[str, float]) -> list[dict]:
    """按引擎边界节流的**真实语义**派生开跑曲线：因子作用于当日损益（P&L），非净值水平。

    ShrinkageBacktestEngine 把归一化后的目标权重乘当日 Shrinkage、剩余质量落现金 ⇒
    当日收益被缩放、次日自新水位续算（下跌日=减损，谷底抬升）。
    与之相对，`_shrunken_equity` 乘的是**水平**：任何 <1 因子只会把当日压得更低，
    在"峰不动、谷下移"的派生曲线上永远得不出"节流使回撤变浅"的方向。
    """
    out: list[dict] = []
    prev_off: float | None = None
    prev_on: float | None = None
    for p in base_curve:
        eq = float(p["equity"])
        if prev_off is None:
            on_eq = eq
        else:
            factor = factors.get(p["timestamp"], 1.0)
            on_eq = prev_on + (eq - prev_off) * factor
        out.append({"timestamp": p["timestamp"], "equity": on_eq})
        prev_off, prev_on = eq, on_eq
    return out


# ── schedule 归一化 ───────────────────────────────────────────────────


class TestNormalizeShrinkageSchedule:
    def test_none_and_empty_are_off(self) -> None:
        assert _normalize_shrinkage_schedule(None) is None
        assert _normalize_shrinkage_schedule({}) is None

    def test_clamp_only_reduce(self) -> None:
        schedule = _normalize_shrinkage_schedule(
            {"2026-09-01": 0.5, "2026-09-02": 1.4, "2026-09-03": -0.2}
        )
        assert schedule is not None
        values = list(schedule.values())
        assert values == [0.5, 1.0, 0.0]  # >1 截 1.0；<0 截 0.0（只减不增）
        assert all(isinstance(k, datetime) for k in schedule)

    @pytest.mark.parametrize(
        "raw",
        [
            42,
            "not-a-map",
            {"2026-09-01": "x"},
            {"bad-date": 0.5},
            {"2026-09-01": float("nan")},
        ],
    )
    def test_fail_closed(self, raw: object) -> None:
        with pytest.raises(FrameworkValidationError):
            _normalize_shrinkage_schedule(raw)


# ── 引擎参数透传（裁定#270 同 commit 缺陷修复）────────────────────────


class TestShrinkageEngineKwargsForward:
    def test_enable_stk_limit_provider_forwarded(self) -> None:
        engine = ShrinkageBacktestEngine(
            config=BacktestConfig(), enable_stk_limit_provider=False
        )
        assert engine._enable_stk_limit_provider is False

    def test_default_true_unchanged(self) -> None:
        engine = ShrinkageBacktestEngine(config=BacktestConfig())
        assert engine._enable_stk_limit_provider is True


# ── diff 差值章（纯函数数学）─────────────────────────────────────────


class TestShrinkageDiffStamp:
    def _base_curve(self) -> list[dict]:
        return [
            {"timestamp": "2026-01-01", "equity": 1_000_000.0},
            {"timestamp": "2026-01-02", "equity": 1_100_000.0},
            {"timestamp": "2026-01-03", "equity": 990_000.0},
            {"timestamp": "2026-01-04", "equity": 1_050_000.0},
        ]

    def test_identical_curves_zero_diff(self) -> None:
        curve = self._base_curve()
        stamp = shrinkage_diff_stamp(curve, curve, [])
        assert stamp["days_compared"] == 4
        assert stamp["total_return_diff_pct"] == 0.0
        assert stamp["max_drawdown_diff_pct"] == 0.0
        assert all(r["diff_pct"] == 0.0 for r in stamp["nav_diff_by_day"])

    def test_direction_and_drawdown_math(self) -> None:
        base = self._base_curve()
        # 开跑：第 3/4 日被节流压低（模拟收缩放弃了后续反弹）
        on = _shrunken_equity(base, {"2026-01-03": 0.95, "2026-01-04": 0.90})
        stamp = shrinkage_diff_stamp(base, on, [("2026-01-03", 0.5), ("2026-01-04", 0.6)])
        assert stamp["throttled_days"] == 2
        assert stamp["total_return_off_pct"] == pytest.approx(5.0, abs=1e-6)
        # on 终值 = 1_050_000×0.9=945_000 → on 总收益 = (945000/1000000−1)×100 = −5.5%
        assert stamp["total_return_on_pct"] == pytest.approx(-5.5, abs=1e-6)
        assert stamp["total_return_diff_pct"] == pytest.approx(-10.5, abs=1e-6)  # on−off
        # off 回撤：峰 1_100_000（d2）谷 990_000（d3）→ 1−990000/1100000 = 10%；
        # on：峰不变 1_100_000，谷收缩为 990_000×0.95=940_500 → 1−940500/1100000 = 14.5%
        #（峰未收缩谷收缩 → 回撤加深，合成派生曲线的数学事实）
        assert stamp["max_drawdown_off_pct"] == pytest.approx(10.0, abs=1e-6)
        assert stamp["max_drawdown_on_pct"] == pytest.approx(14.5, abs=1e-6)
        assert stamp["max_drawdown_diff_pct"] == pytest.approx(4.5, abs=1e-6)

    def test_throttle_saves_drawdown_direction(self) -> None:
        # 节流在下跌日减损：on 回撤应浅于 off（diff 为负）
        base = self._base_curve()
        # 引擎口径=当日损益×因子（d3 是 −10% 下跌日，0.5 只吃一半亏损 → 谷底被抬升）
        on = _throttled_equity(base, {"2026-01-03": 0.5})
        stamp = shrinkage_diff_stamp(base, on, [("2026-01-03", 0.5)])
        # off：峰 1_100_000（d2）谷 990_000（d3）→ 10%；
        # on ：d3 = 1_100_000 − 110_000×0.5 = 1_045_000（峰不变）→ 5%
        # diff 口径 = on − off（见 shrinkage_diff_stamp docstring）→ 5 − 10 = −5
        assert stamp["max_drawdown_off_pct"] == pytest.approx(10.0, abs=1e-6)
        assert stamp["max_drawdown_on_pct"] == pytest.approx(5.0, abs=1e-6)
        assert stamp["max_drawdown_diff_pct"] == pytest.approx(-5.0, abs=1e-6)
        assert stamp["max_drawdown_diff_pct"] < 0

    def test_empty_curves_no_crash(self) -> None:
        stamp = shrinkage_diff_stamp([], [], [])
        assert stamp["days_compared"] == 0
        assert stamp["final_equity_off"] is None
        assert stamp["total_return_diff_pct"] is None


# ── run_framework_backtest 节流口径（引擎级集成，tmp_path 隔离）───────


@pytest.fixture()
def fw_env(tmp_path, monkeypatch):
    """整装回测集成环境：单成员方案 YAML + 合成行情，产物落 tmp_path。"""
    from zephyr.pf_core.strategy_engine import framework_composer as fc

    data = _make_market_data()
    signals = _make_signals(data)
    dates = data.index.get_level_values("date").unique().sort_values()

    plans_path = tmp_path / "fw_plans_test.yaml"
    plans_path.write_text(
        "plans:\n"
        "  - plan_id: fw-shrink-test\n"
        "    name_zh: 收缩测试方案\n"
        "    risk_profile: balanced\n"
        "    description: RSC-2 单测\n"
        "    weights:\n"
        "      - strategy_id: member-a\n"
        "        weight: 1.0\n"
        "        role: test\n",
        encoding="utf-8",
    )

    panels = {"member-a": signals}
    config = FrameworkBacktestConfig(
        plans_path=str(plans_path),
        storage_path=str(tmp_path / "artifacts"),
        enable_stk_limit_provider=False,
        factor_ids=(),
    )
    return {
        "fc": fc,
        "data": data,
        "panels": panels,
        "config": config,
        "dates": [d.to_pydatetime() for d in dates],
        "tmp_path": tmp_path,
    }


class TestRunFrameworkBacktestShrinkage:
    def test_default_off_zero_drift_and_no_keys(
        self, fw_env, monkeypatch
    ) -> None:
        """默认关：引擎原路（DefaultBacktestEngine）、shrinkage=None、metrics 无键。"""
        fc = fw_env["fc"]
        captured = {}

        real_engine = fc.DefaultBacktestEngine if hasattr(fc, "DefaultBacktestEngine") else None

        import zephyr.backtest.implementations.vectorized_engine as ve

        orig_init = ve.DefaultBacktestEngine.__init__

        def spy_init(self, *a, **kw):
            captured["engine_cls"] = "default"
            captured["kwargs"] = kw
            orig_init(self, *a, **kw)

        monkeypatch.setattr(ve.DefaultBacktestEngine, "__init__", spy_init)
        # compose 面板不经 CH：直接打内核（面板构建层被 monkeypatch 绕开——
        # _build_member_panels 是取数边界，单测注入合成面板）
        monkeypatch.setattr(
            fc, "_build_member_panels", lambda *a, **kw: (fw_env["data"], dict(fw_env["panels"]), [])
        )
        monkeypatch.setattr(
            fc, "_member_signal_contracts", lambda *a, **kw: {"member-a": {"route": "runner-flat"}}
        )
        monkeypatch.setattr(fc, "_select_vectorizable_members", lambda plan: ([plan.weights[0]], []))

        result, ts = fc._run_framework_backtest_core(
            "fw-shrink-test", list(_SYMBOLS), "2026-01-01", "2026-12-31", fw_env["config"]
        )
        assert result["ok"] is True
        assert result["shrinkage"] is None  # 键恒存在，未启用=None
        assert "shrinkage_disclosure" not in result["metrics"]  # 不落键（零漂移）
        assert captured["engine_cls"] == "default"
        assert captured["kwargs"].get("enable_stk_limit_provider") is False
        assert ts.get("equity_curve"), "ts.equity_curve 供双跑编排"
        assert real_engine is not None  # 引用健在（防误删 import）

    def test_throttle_on_uses_shrinkage_engine_and_discloses(
        self, fw_env, monkeypatch
    ) -> None:
        """开启：ShrinkageBacktestEngine 生效、披露齐、metrics 落 shrinkage_disclosure。"""
        fc = fw_env["fc"]
        import zephyr.backtest.implementations.shrinkage_engine as se

        captured = {}
        orig_init = se.ShrinkageBacktestEngine.__init__

        def spy_init(self, *a, **kw):
            captured["cls"] = "shrinkage"
            captured["kwargs"] = kw
            orig_init(self, *a, **kw)

        monkeypatch.setattr(se.ShrinkageBacktestEngine, "__init__", spy_init)
        monkeypatch.setattr(
            fc, "_build_member_panels", lambda *a, **kw: (fw_env["data"], dict(fw_env["panels"]), [])
        )
        monkeypatch.setattr(
            fc, "_member_signal_contracts", lambda *a, **kw: {"member-a": {"route": "runner-flat"}}
        )
        monkeypatch.setattr(fc, "_select_vectorizable_members", lambda plan: ([plan.weights[0]], []))

        schedule = {fw_env["dates"][5].strftime("%Y-%m-%d"): 0.5}
        config = fc.FrameworkBacktestConfig(
            plans_path=fw_env["config"].plans_path,
            storage_path=fw_env["config"].storage_path,
            enable_stk_limit_provider=False,
            factor_ids=(),
            shrinkage_by_date=schedule,
        )
        result, _ts = fc._run_framework_backtest_core(
            "fw-shrink-test", list(_SYMBOLS), "2026-01-01", "2026-12-31", config
        )
        assert result["ok"] is True
        assert captured["cls"] == "shrinkage"
        assert captured["kwargs"].get("enable_stk_limit_provider") is False  # 透传生效

        disc = result["shrinkage"]
        assert disc is not None and disc["caliber"] == "rsc2-engine-boundary-throttle"
        assert disc["ruling"] == "裁定#270"
        assert disc["schedule_days"] == 1
        assert disc["applied_days"] >= 1  # 有信号日引擎逐日记录
        assert disc["throttled_days"] >= 1
        assert disc["factor_min"] is not None and disc["factor_min"] <= 1.0
        assert len(disc["log"]) == disc["applied_days"]
        # metrics 落键（禁静默）
        assert result["metrics"].get("shrinkage_disclosure") == disc

    def test_bad_schedule_fail_closed_before_engine(self, fw_env, monkeypatch) -> None:
        """非法 schedule：进引擎前 fail-closed（FrameworkValidationError）。"""
        fc = fw_env["fc"]
        config = fc.FrameworkBacktestConfig(
            plans_path=fw_env["config"].plans_path,
            storage_path=fw_env["config"].storage_path,
            enable_stk_limit_provider=False,
            factor_ids=(),
            shrinkage_by_date={"not-a-date": 0.5},
        )
        with pytest.raises(FrameworkValidationError):
            fc._run_framework_backtest_core(
                "fw-shrink-test", list(_SYMBOLS), "2026-01-01", "2026-12-31", config
            )

    def test_dual_run_off_on_and_diff(self, fw_env, monkeypatch) -> None:
        """双跑编排：关/开两跑+差值章；两 run_id 独立；逐日差结构齐。"""
        fc = fw_env["fc"]
        monkeypatch.setattr(
            fc, "_build_member_panels", lambda *a, **kw: (fw_env["data"], dict(fw_env["panels"]), [])
        )
        monkeypatch.setattr(
            fc, "_member_signal_contracts", lambda *a, **kw: {"member-a": {"route": "runner-flat"}}
        )
        monkeypatch.setattr(fc, "_select_vectorizable_members", lambda plan: ([plan.weights[0]], []))

        schedule = {
            fw_env["dates"][i].strftime("%Y-%m-%d"): (0.4 if i % 3 == 0 else 1.0)
            for i in range(len(fw_env["dates"]))
        }
        out = fc.run_framework_backtest_shrinkage_dual(
            "fw-shrink-test",
            list(_SYMBOLS),
            "2026-01-01",
            "2026-12-31",
            fw_env["config"],
            shrinkage_by_date=schedule,
        )
        assert out["ok"] is True
        assert out["run_ids"]["off"] and out["run_ids"]["on"]
        assert out["run_ids"]["off"] != out["run_ids"]["on"]
        assert len(out["equity_curves"]["off"]) == len(out["equity_curves"]["on"]) > 0
        diff = out["diff"]
        assert diff["caliber"] == "rsc2-shrinkage-dual-run-diff"
        assert diff["throttled_days"] > 0
        assert diff["days_compared"] == len(out["equity_curves"]["off"])
        # 有正收益漂移 + 节流 → on 曲线应系统性低于 off（方向断言，允许首日相等）
        finals = diff["final_equity_off"], diff["final_equity_on"]
        assert finals[1] < finals[0]
        assert diff["total_return_diff_pct"] < 0
        # 逐日明细结构
        row = diff["nav_diff_by_day"][-1]
        assert set(row) == {"date", "equity_off", "equity_on", "diff_pct"}

    def test_dual_off_side_failure_not_silent(self, fw_env, monkeypatch) -> None:
        """off 侧失败 → ok=False + phase=off（不静默吞错）。"""
        fc = fw_env["fc"]

        def fail_core(*a, **kw):
            return {"ok": False, "error": "synthetic off failure"}, {}

        monkeypatch.setattr(fc, "_run_framework_backtest_core", fail_core)
        out = fc.run_framework_backtest_shrinkage_dual(
            "fw-shrink-test",
            list(_SYMBOLS),
            "2026-01-01",
            "2026-12-31",
            fw_env["config"],
            shrinkage_by_date={"2026-01-05": 0.5},
        )
        assert out["ok"] is False
        assert out["phase"] == "off"
        assert "synthetic off failure" in out["error"]

    def test_dual_requires_shrinkage_kwarg(self, fw_env) -> None:
        """无 schedule 的双跑无意义：关键字参数必填。"""
        fc = fw_env["fc"]
        with pytest.raises(TypeError):
            fc.run_framework_backtest_shrinkage_dual(
                "fw-shrink-test", list(_SYMBOLS), "2026-01-01", "2026-12-31"
            )


# ── PIT 语义（schedule as-of join 经引擎生效路径）────────────────────


class TestPitAsOfSemantics:
    def test_schedule_before_first_day_means_full_deploy(self, fw_env, monkeypatch) -> None:
        """早于 schedule 首条的日期=1.0 满部署（provider PIT 语义，不查未来）。"""
        from zephyr.backtest.regime_validation.shrinkage_provider import ScheduleShrinkageProvider

        provider = ScheduleShrinkageProvider(
            {datetime(2026, 6, 1): 0.3}
        )
        assert provider.get_shrinkage(datetime(2026, 1, 5)) == 1.0  # 早于首条
        assert provider.get_shrinkage(datetime(2026, 5, 31)) == 1.0  # as-of 前一日
        assert provider.get_shrinkage(datetime(2026, 6, 1)) == 0.3  # 当日生效
        assert provider.get_shrinkage(datetime(2026, 7, 10)) == 0.3  # ≤ 最近一条（不查未来）
