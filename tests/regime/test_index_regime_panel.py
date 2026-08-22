# [BLUEPRINT] MOD-REGIME-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""test_index_regime_panel.py — IndexRegimePanel（MOD-REGIME-008，IDX-01）单元测试

覆盖（92 号 §7.9 验收 + §11.3 裁定一"1 引擎×4 代理"纪律）：
  - 四代理配置生成：默认 config = 000300/000001/399006/000688 钉死清单，
    4 套配置共享同一 HMM 框架（同一 RegimeDetector 类 + 同一 hmm_params），
    非 4 套独立模型；
  - 概率分布契约：每卡 probabilities 键集 = REGIME_STATES（7 态）且 Σ=1、值∈[0,1]，
    单指数缺数据时该卡退化为无信息先验（Σ=1 仍保持）不炸面板；
  - 强弱排序：合成趋势（000300 强涨 / 399006 下跌）下 ranking 首尾正确、
    rank 位次与 ranking 一致；
  - 背离警示：M1-② distortion 注入（dataclass/dict 双形态）→ 市场级警示；
    自算简版（指数涨但跌家数>涨家数）→ 逐指数 weight_cover_simple；
  - 降级：单指数缺数据该卡 degraded、其余正常、面板不 degraded；
    全指数缺数据 → 面板级 degraded、strength_ranking 空；
  - 输出契约：frozen dataclass、to_json 往返可序列化、无点位/方向预测字段
    （90 号 §7 铁律）。

数据：合成 K 线 TSV 经 ch_client 注入（不连 ClickHouse）；HMM 真拟合
（hmmlearn 可用时）或引擎内建降级（不可用时均匀先验）——两路径均满足契约断言。

依据: architecture_review_2026_08_module_upgrade_audit §11.3/§11.5 IDX-01 /
92_phase2_business_construction_order §7.9
"""

from __future__ import annotations

import json
from dataclasses import fields
from itertools import pairwise
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.core.regime_detector import REGIME_STATES
from zephyr.regime.index_regime_panel import (
    INDEX_PROXIES,
    DivergenceAlert,
    IndexProxyConfig,
    IndexRegimeCard,
    IndexRegimePanel,
    IndexRegimePanelConfig,
    IndexRegimePanelError,
    compute_index_regime_panel,
)

# ── 合成数据工厂 ─────────────────────────────────────────────────────────────

_N_DAYS = 420  # 覆盖 F1 warmup（250 分位 + 20 HV）+ F2 rolling 200 + 训练窗
_DATES = pd.bdate_range(end="2026-08-19", periods=_N_DAYS)

# 各指数（drift, vol, seed）：000300 强涨 / 000001 微涨 / 399006 下跌 / 000688 高波平盘
_SYMBOL_SPECS: dict[str, tuple[float, float, int]] = {
    "000300": (0.0020, 0.010, 30001),
    "000001": (0.0008, 0.008, 10001),
    "399006": (-0.0020, 0.012, 39906),
    "000688": (0.0003, 0.025, 68801),
    "000905": (0.0005, 0.011, 90501),  # F3 共享
    "399106": (0.0004, 0.009, 99106),  # F4 广度源
}


def _gen_kline_rows(
    symbol: str,
    drift: float,
    vol: float,
    seed: int,
    adv_dec: tuple[int, int] | None = None,
    tail_drift: float | None = None,
    tail_n: int = 20,
) -> list[list[str]]:
    """生成单指数日 K 行（TSV 9 列；合成数据确定性种子）。

    tail_drift 非 None 时：最后 tail_n 日用确定性倾斜（drift±微噪声），
    保证强弱排序测试的窗口信号确定（不受随机游走噪声翻盘）。
    """
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, _N_DAYS)
    if tail_drift is not None:
        rets[-tail_n:] = tail_drift + rng.normal(0.0, 0.0003, tail_n)
    close = 1000.0 * np.exp(np.cumsum(rets))
    rows: list[list[str]] = []
    for i, dt in enumerate(_DATES):
        c = float(close[i])
        o = float(close[i - 1]) if i > 0 else c * 0.999
        h = max(o, c) * 1.002
        lo = min(o, c) * 0.998
        v = float(rng.uniform(1e8, 3e8))
        adv, dec = adv_dec if adv_dec is not None else (1500, 1200)
        rows.append(
            [
                dt.strftime("%Y-%m-%d"),
                symbol,
                f"{o:.2f}",
                f"{h:.2f}",
                f"{lo:.2f}",
                f"{c:.2f}",
                f"{v:.0f}",
                str(adv),
                str(dec),
            ]
        )
    return rows


# 尾窗确定性倾斜（强弱排序场景钉死首尾：000300 最强 / 399006 最弱）
_TAIL_DRIFTS: dict[str, float] = {"000300": 0.005, "399006": -0.004}


def _make_tsv(
    drop_symbols: tuple[str, ...] = (),
    last_day_adv_dec: tuple[int, int] | None = None,
    last_day_up: tuple[str, ...] = (),
    tail_drifts: dict[str, float] | None = _TAIL_DRIFTS,
) -> str:
    """合成全面板 TSV（6 符号；可缺符号/控末日广度/强制末日上涨/尾窗倾斜）。"""
    lines: list[str] = []
    for sym, (drift, vol, seed) in _SYMBOL_SPECS.items():
        if sym in drop_symbols:
            continue
        tail = (tail_drifts or {}).get(sym)
        rows = _gen_kline_rows(sym, drift, vol, seed, tail_drift=tail)
        if sym in last_day_up:  # 强制末日收涨（背离场景）
            prev = float(rows[-2][5])
            rows[-1][4] = f"{prev * 1.004:.2f}"  # low
            rows[-1][5] = f"{prev * 1.005:.2f}"  # close +0.5%
            rows[-1][3] = f"{prev * 1.006:.2f}"  # high
        for r in rows:
            if last_day_adv_dec is not None and sym == "399106" and r[0] == _DATES[-1].strftime("%Y-%m-%d"):
                r[7], r[8] = str(last_day_adv_dec[0]), str(last_day_adv_dec[1])
            lines.append("\t".join(r))
    return "\n".join(lines) + "\n"


def _client_from_tsv(tsv: str):
    """fake ch_client：callable(sql) → 静态 TSV（不连 ClickHouse）。"""
    return lambda _sql: tsv


def _test_config(**overrides) -> IndexRegimePanelConfig:
    """测试配置：缩短训练窗/样本阈（合成数据 420 日），其余同默认。"""
    base = {
        "train_years": 1,
        "min_train_samples": 60,
        "detect_window": 30,
        "data_load_start": _DATES[0].strftime("%Y-%m-%d"),
        "rank_window": 20,
    }
    base.update(overrides)
    return IndexRegimePanelConfig(**base)


# ── module 级面板 fixture（每场景只算一次，多测试共享）─────────────────────────


@pytest.fixture(scope="module")
def normal_panel() -> IndexRegimePanel:
    return compute_index_regime_panel(
        trade_date=_DATES[-1].strftime("%Y-%m-%d"),
        ch_client=_client_from_tsv(_make_tsv()),
        config=_test_config(),
    )


@pytest.fixture(scope="module")
def missing_one_panel() -> IndexRegimePanel:
    return compute_index_regime_panel(
        trade_date=_DATES[-1].strftime("%Y-%m-%d"),
        ch_client=_client_from_tsv(_make_tsv(drop_symbols=("399006",))),
        config=_test_config(),
    )


@pytest.fixture(scope="module")
def empty_panel() -> IndexRegimePanel:
    return compute_index_regime_panel(
        trade_date=_DATES[-1].strftime("%Y-%m-%d"),
        ch_client=_client_from_tsv(""),
        config=_test_config(),
    )


@pytest.fixture(scope="module")
def divergence_panel() -> IndexRegimePanel:
    # 末日：000300 收涨，但 399106 广度 adv=800 < dec=2200 → 权重掩护简版
    return compute_index_regime_panel(
        trade_date=_DATES[-1].strftime("%Y-%m-%d"),
        ch_client=_client_from_tsv(_make_tsv(last_day_adv_dec=(800, 2200), last_day_up=("000300",))),
        config=_test_config(),
    )


# ── 1. 四代理配置生成 ────────────────────────────────────────────────────────


class TestProxyConfig:
    def test_index_proxies_pinned(self):
        """IDX-01 钉死四代理：000300/000001/399006/000688（插入序=面板卡序）。"""
        assert list(INDEX_PROXIES.keys()) == ["000300", "000001", "399006", "000688"]
        assert INDEX_PROXIES["000300"] == "沪深300"
        assert INDEX_PROXIES["000001"] == "上证指数"
        assert INDEX_PROXIES["399006"] == "创业板指"
        assert INDEX_PROXIES["000688"] == "科创50"

    def test_default_config_four_proxies(self):
        """默认 config = 4 套配置；同一 hmm_params（一份超参共享=1 引擎非 4 模型）。"""
        cfg = IndexRegimePanelConfig()
        assert len(cfg.proxies) == 4
        assert [p.code for p in cfg.proxies] == ["000300", "000001", "399006", "000688"]
        assert all(isinstance(p, IndexProxyConfig) for p in cfg.proxies)
        assert all(p.enabled for p in cfg.proxies)
        assert cfg.hmm_params is None  # None=RegimeDetector 默认 4 态，4 代理共享

    def test_config_fail_fast(self):
        """配置非法 fail-fast（区别于数据问题的 degraded 路径）。"""
        with pytest.raises(IndexRegimePanelError):
            compute_index_regime_panel(config=IndexRegimePanelConfig(proxies=()))
        with pytest.raises(IndexRegimePanelError):
            compute_index_regime_panel(
                config=_test_config(
                    proxies=tuple(
                        IndexProxyConfig(code=c, name=n, enabled=False) for c, n in INDEX_PROXIES.items()
                    )
                )
            )
        with pytest.raises(IndexRegimePanelError):
            compute_index_regime_panel(config=_test_config(train_years=0))

    def test_bad_ch_client_fail_fast(self):
        """ch_client 形态非法 → IndexRegimePanelError（非 callable 且无 .query）。"""
        with pytest.raises(IndexRegimePanelError):
            compute_index_regime_panel(ch_client=object(), config=_test_config())


# ── 2. 概率分布契约（Σ=1，7 态键集）──────────────────────────────────────────


class TestProbabilityContract:
    def test_cards_complete(self, normal_panel: IndexRegimePanel):
        """4 卡齐全、顺序=配置序、非 degraded、trade_date=as-of。"""
        assert [c.code for c in normal_panel.cards] == ["000300", "000001", "399006", "000688"]
        assert all(not c.degraded for c in normal_panel.cards)
        assert all(c.degrade_reason is None for c in normal_panel.cards)
        assert all(c.trade_date == _DATES[-1].strftime("%Y-%m-%d") for c in normal_panel.cards)
        assert normal_panel.degraded is False
        assert normal_panel.trade_date == _DATES[-1].strftime("%Y-%m-%d")

    def test_probability_distribution_contract(self, normal_panel: IndexRegimePanel):
        """每卡 probabilities：键集=REGIME_STATES（7 态）、Σ=1、值∈[0,1]。"""
        for card in normal_panel.cards:
            assert set(card.probabilities.keys()) == set(REGIME_STATES)
            total = sum(card.probabilities.values())
            assert abs(total - 1.0) < 1e-6, f"{card.code} Σ={total}"
            assert all(0.0 <= p <= 1.0 for p in card.probabilities.values())
            assert card.dominant_regime in REGIME_STATES
            assert abs(card.confidence - max(card.probabilities.values())) < 1e-12


# ── 3. 强弱排序正确性 ────────────────────────────────────────────────────────


class TestStrengthRanking:
    def test_ranking_order(self, normal_panel: IndexRegimePanel):
        """合成趋势：000300（强涨低波）居首，399006（下跌）居末。"""
        ranking = normal_panel.strength_ranking
        assert set(ranking) == {"000300", "000001", "399006", "000688"}
        assert ranking[0] == "000300"
        assert ranking[-1] == "399006"

    def test_rank_field_consistent(self, normal_panel: IndexRegimePanel):
        """卡内 rank 位次 = ranking 位置 + 1；score 单调递减。"""
        pos = {code: i + 1 for i, code in enumerate(normal_panel.strength_ranking)}
        for card in normal_panel.cards:
            assert card.rank == pos[card.code]
        scores = [
            c.strength_score
            for c in sorted(normal_panel.cards, key=lambda c: c.rank)  # type: ignore[arg-type]
        ]
        assert all(a >= b for a, b in pairwise(scores))

    def test_strength_inputs_present(self, normal_panel: IndexRegimePanel):
        """强弱分输入（近期收益/年化波动）非空且波动非负。"""
        for card in normal_panel.cards:
            assert card.recent_return is not None
            assert card.volatility is not None and card.volatility >= 0.0
            assert card.strength_score is not None


# ── 4. 背离警示（注入 + 自算简版）─────────────────────────────────────────────


class TestDivergenceAlerts:
    def test_m1_distortion_injection_dataclass(self):
        """M1-② 注入（对象形态）：weight_cover=True → 市场级警示。"""
        m1 = SimpleNamespace(
            distortion_flag=True,
            guard_illusion=False,
            weight_cover=True,
            spread_current=0.012,
            spread_zscore=1.5,
            guard_ratio=None,
        )
        panel = compute_index_regime_panel(
            trade_date=_DATES[-1].strftime("%Y-%m-%d"),
            ch_client=_client_from_tsv(_make_tsv()),
            config=_test_config(enable_simple_divergence=False),
            m1_distortion=m1,
        )
        kinds = [a.kind for a in panel.divergence_alerts]
        assert "m1_distortion_weight_cover" in kinds
        alert = next(a for a in panel.divergence_alerts if a.kind == "m1_distortion_weight_cover")
        assert alert.index_code is None  # 市场级
        assert "权重掩护" in alert.detail
        assert alert.severity == "warn"
        assert isinstance(alert, DivergenceAlert)

    def test_m1_distortion_injection_dict(self):
        """M1-② 注入（dict 形态）：guard_illusion=True → 护盘假象警示。"""
        m1 = {"distortion_flag": True, "guard_illusion": True, "weight_cover": False, "guard_ratio": 0.72}
        panel = compute_index_regime_panel(
            trade_date=_DATES[-1].strftime("%Y-%m-%d"),
            ch_client=_client_from_tsv(_make_tsv()),
            config=_test_config(enable_simple_divergence=False),
            m1_distortion=m1,
        )
        kinds = [a.kind for a in panel.divergence_alerts]
        assert "m1_distortion_guard" in kinds

    def test_m1_distortion_flag_false_no_alert(self):
        """distortion_flag=False → 无 M1-② 警示。"""
        m1 = SimpleNamespace(distortion_flag=False, guard_illusion=False, weight_cover=False)
        panel = compute_index_regime_panel(
            trade_date=_DATES[-1].strftime("%Y-%m-%d"),
            ch_client=_client_from_tsv(_make_tsv()),
            config=_test_config(enable_simple_divergence=False),
            m1_distortion=m1,
        )
        assert panel.divergence_alerts == ()

    def test_simple_divergence_self_compute(self, divergence_panel: IndexRegimePanel):
        """自算简版：000300 末日涨 + 跌家数>涨家数 → weight_cover_simple。"""
        simple = [a for a in divergence_panel.divergence_alerts if a.kind == "weight_cover_simple"]
        assert simple, "应触发自算简版权重掩护"
        target = next(a for a in simple if a.index_code == "000300")
        assert "000300" in target.detail
        assert "权重掩护" in target.detail
        assert target.trade_date == _DATES[-1].strftime("%Y-%m-%d")

    def test_no_divergence_on_normal_breadth(self, normal_panel: IndexRegimePanel):
        """常态广度（adv>dec）→ 无自算简版警示。"""
        assert [a for a in normal_panel.divergence_alerts if a.kind == "weight_cover_simple"] == []


# ── 5. 降级：单指数缺数据 / 全缺 ─────────────────────────────────────────────


class TestDegradation:
    def test_single_index_missing_degraded(self, missing_one_panel: IndexRegimePanel):
        """399006 缺数据：该卡 degraded+reason+无信息先验（Σ=1）；其余正常；面板不 degraded。"""
        panel = missing_one_panel
        by_code = {c.code: c for c in panel.cards}
        assert set(by_code) == {"000300", "000001", "399006", "000688"}

        degraded_card = by_code["399006"]
        assert degraded_card.degraded is True
        assert degraded_card.degrade_reason is not None and "399006" in degraded_card.degrade_reason
        assert degraded_card.rank is None
        assert degraded_card.strength_score is None
        # 无信息先验仍守契约：Σ=1、7 态键集
        assert set(degraded_card.probabilities.keys()) == set(REGIME_STATES)
        assert abs(sum(degraded_card.probabilities.values()) - 1.0) < 1e-6

        for code in ("000300", "000001", "000688"):
            assert by_code[code].degraded is False
        assert panel.degraded is False
        assert "399006" not in panel.strength_ranking
        assert len(panel.strength_ranking) == 3

    def test_all_missing_panel_degraded(self, empty_panel: IndexRegimePanel):
        """全指数缺数据：4 卡全 degraded、面板级 degraded、ranking 空、仍可序列化。"""
        panel = empty_panel
        assert panel.degraded is True
        assert len(panel.cards) == 4
        assert all(c.degraded for c in panel.cards)
        assert panel.strength_ranking == ()
        assert all(c.rank is None for c in panel.cards)
        for card in panel.cards:
            assert abs(sum(card.probabilities.values()) - 1.0) < 1e-6
        json.loads(panel.to_json())  # degraded 面板也可序列化

    def test_query_exception_degrades(self):
        """ch_client 抛异常 → 全卡 degraded，不炸面板。"""

        def _boom(_sql: str) -> str:
            raise ConnectionError("CH unreachable")

        panel = compute_index_regime_panel(
            trade_date=_DATES[-1].strftime("%Y-%m-%d"),
            ch_client=_boom,
            config=_test_config(),
        )
        assert panel.degraded is True
        assert all(c.degraded for c in panel.cards)


# ── 6. 输出契约：JSON 序列化 + 不预测铁律 ─────────────────────────────────────


class TestOutputContract:
    def test_json_roundtrip(self, normal_panel: IndexRegimePanel):
        """to_json → json.loads 往返；frozen dataclass 树全 JSON 安全。"""
        payload = json.loads(normal_panel.to_json())
        assert payload["trade_date"] == _DATES[-1].strftime("%Y-%m-%d")
        assert len(payload["cards"]) == 4
        assert payload["strength_ranking"] == list(normal_panel.strength_ranking)
        card0 = payload["cards"][0]
        assert abs(sum(card0["probabilities"].values()) - 1.0) < 1e-6
        assert isinstance(card0["name"], str)  # 中文名 ensure_ascii=False 保留
        # to_dict 等价
        assert normal_panel.to_dict()["schema_version"] == "1.0"

    def test_no_point_prediction_invariant(self):
        """90 号 §7 铁律：输出契约无任何点位/方向预测字段（反射断言）。"""
        banned_tokens = ("target", "forecast", "predict", "direction", "point", "price_target")
        for cls in (IndexRegimePanel, IndexRegimeCard, DivergenceAlert):
            for f in fields(cls):
                name = f.name.lower()
                assert not any(tok in name for tok in banned_tokens), (
                    f"{cls.__name__}.{f.name} 疑似点预测字段，违反 90 号 §7 铁律"
                )

    def test_disabled_proxy_no_card(self):
        """代理 enabled=False → 不出卡（配置级剔除，非 degraded）。"""
        proxies = tuple(
            IndexProxyConfig(code=c, name=n, enabled=(c != "000688")) for c, n in INDEX_PROXIES.items()
        )
        panel = compute_index_regime_panel(
            trade_date=_DATES[-1].strftime("%Y-%m-%d"),
            ch_client=_client_from_tsv(_make_tsv()),
            config=_test_config(proxies=proxies),
        )
        assert [c.code for c in panel.cards] == ["000300", "000001", "399006"]
