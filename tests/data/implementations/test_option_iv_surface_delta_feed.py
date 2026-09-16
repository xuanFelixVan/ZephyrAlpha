# [A_test] module_id: MOD-DATA-OPTIONIV-DELTA | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §test
# [MODULE] tests.data.implementations.test_option_iv_surface_delta_feed
# [TESTS] src/zephyr/data/implementations/miniqmt_provider.py; src/zephyr/regime/features/regime_data_loader.py; src/zephyr/regime/features/synthetic_vix.py
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# [ARCH-REF] #SVX-1-P0
"""SVX-1-P0 期权 IV 进料口 delta 恒零治本回归锚（feed → loader → synthetic VIX 全链）。

挖矿文档 docs/_working/full-auto-chain/S11_assembled_backtest/nodes/wyckoff_vix_mining.md §4
把 SVX-1 记为「IV 路径零测试」（P2）。2026-09-16 生产取证（ClickHouse 实读）把它抬升为 P0，
并定位到**进料口**而非插值算法：

  c1_market.option_iv_surface 现存 9653 行（510050.SH 4844 + 510300.SH 4809，
  2026-01-29~2026-09-16），其中 `delta=0 AND vega=0` 的行数 **9653（100%）**。
  DDL 里 delta/gamma/theta/vega 是 `Decimal(18,6) DEFAULT 0`，而唯一写入方
  miniqmt_provider._fetch_option_iv_surface 的 columns 清单根本不声明这四列 →
  BufferedWriter 列过滤（buffered_writer._init_columns 按 result.columns 与表列取交集）
  把它们永久留在 DEFAULT 0。消费端 synthetic_vix 的 ATM 筛子是
  `|abs(delta)-0.5| < 0.15`，|0-0.5|=0.5 → **全部行被排除 → 期权 IV 主路径结构性零产出**。

  第二个独立零：`_load_option_iv` 用 `underlying IN ('510050','510300')` 过滤，
  而进料口写入的 underlying 带交易所后缀（'510050.SH'）→ 同一谓词在真库上
  返回 **0 行**（带后缀查询返回 9653 行）。即便补上 delta，消费端依然一行读不到。

  第三个同源病灶：`_solve_iv` 不收敛时返回 None，`_compute_iv_rows` 照样 append
  该行 → TSV 写 `\\N` 进非 Nullable Decimal 列 → DEFAULT 0 兜底 → 真库
  iv=0 的 1028 行（9653-8625）。「解不出」与「零波动」在库里不可区分（违禁静默零值）。

本文件锁的是「零不可能再回来」：
  ① columns 清单 MUST 声明 delta/gamma/theta/vega（否则一切皆空谈）；
  ② delta MUST 来自仓内唯一 BS 真源 `calc_bs_greeks`（禁第二套公式，RULE-SSOT/clone-guard）；
  ③ IV 反解失败 → 整行不落库 + 非静默 WARNING（禁 None→DEFAULT 0 的伪装）；
  ④ 进料口产出的曲面喂进 compute_synthetic_vix 必须**出数**（端到端零产出即红灯）；
  ⑤ 加载谓词必须同时命中带/不带交易所后缀的 underlying，且不得把 iv<=0 当数据；
  ⑥ 消费端 fail-closed：缺 delta/坏 iv 仍返回空 Series（契约不变）但 MUST 出声。

全链 CH/网络/xtquant 注入（monkeypatch），禁触网禁写库禁写 data/。
"""

from __future__ import annotations

import datetime
import logging

import numpy as np
import pandas as pd
import pytest

from zephyr.data.implementations.miniqmt_provider import (
    MiniQmtIngestProvider,
    _bs_price,
    _OptionCtx,
    _solve_iv,
)
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload
from zephyr.regime.features.synthetic_vix import compute_synthetic_vix

# ---------------------------------------------------------------------------
# 现实期权链夹具（A 股 ETF 期权口径：50ETF 现价 2.85、ATM 行权价 2.85、
# 近月 DTE=18 / 次月 DTE=46、真值 IV 0.20）
# ---------------------------------------------------------------------------

_TRADE_DAY = datetime.date(2026, 9, 16)
_R = 0.03
_SIGMA_TRUE = 0.20

# 治本后进料口列序（iv 仍在 index 6、data_source 仍在末列——既有血缘断言的位置契约）
_IV_COLS = [
    "trade_date",
    "symbol",
    "underlying",
    "strike",
    "expiry",
    "option_type",
    "iv",
    "exchange",
    "delta",
    "gamma",
    "theta",
    "vega",
    "data_source",
]


def _day_str(offset: int = 0) -> str:
    return (_TRADE_DAY + datetime.timedelta(days=offset)).strftime("%Y%m%d")


def _expiry_str(dte: int) -> str:
    """到期日（YYYYMMDD，xtdata EndDelivDate 口径）。"""
    return _day_str(dte)


def _premium(strike: float, dte: int, opt_type: str, sigma: float = _SIGMA_TRUE) -> float:
    """用仓内 BS 定价函数生成合理权利金，使 _solve_iv 能反解回 sigma。

    非 self-consistent：断言不比「生成价」，而是比「落库 delta == 由落库 iv 反推的
    真源输出」（见 TestDeltaFromSingleBsSource），因此定价函数与反解函数同错也不会放过。
    """
    price = _bs_price(2.85, strike, max(dte / 365.0, 0.001), _R, sigma, opt_type)
    assert price is not None and price > 0
    return round(price, 4)


def _ctx(
    *,
    underlying: str = "510050.SH",
    strike: float = 2.85,
    dte: int = 18,
    opt_type: str = "call",
    opt_close: float | None = None,
    spot: float = 2.85,
) -> _OptionCtx:
    """单日单合约的真实形态上下文（价格=BS 反解可得的合理权利金）。"""
    price = _premium(strike, dte, opt_type) if opt_close is None else opt_close
    return _OptionCtx(
        pd.DataFrame({"close": [price]}, index=pd.Index([_day_str()], dtype=object)),
        pd.DataFrame({"close": [spot]}, index=pd.Index([_day_str()], dtype=object)),
        "10010971.SHO",
        underlying,
        strike,
        _expiry_str(dte),
        opt_type,
        _TRADE_DAY + datetime.timedelta(days=dte),
        _R,
        "SHO",
        "miniqmt",
    )


def _row_dict(row: tuple) -> dict:
    return dict(zip(_IV_COLS, row, strict=True))


def _as_loader_frame(rows: list[tuple]) -> pd.DataFrame:
    """按 regime_data_loader._load_option_iv 的产出形态（列名/MultiIndex）装配曲面。"""
    df = pd.DataFrame(rows, columns=_IV_COLS)[
        ["trade_date", "underlying", "strike", "expiry", "iv", "option_type", "delta", "vega"]
    ]
    for c in ["strike", "iv", "delta", "vega"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["expiry"] = pd.to_datetime(df["expiry"])
    return df.set_index(["trade_date", "underlying"]).sort_index()


# ---------------------------------------------------------------------------
# ① 进料口列清单：不声明 = BufferedWriter 列过滤 = 永不落库
# ---------------------------------------------------------------------------


class TestFeedDeclaresGreeksColumns:
    """① columns 清单缺 delta/vega 是本缺陷的结构性根因（不是插值算法）。"""

    @staticmethod
    def _captured(monkeypatch) -> tuple[list[str], int]:
        p = MiniQmtIngestProvider()
        stub_row = (
            "2026-09-16",
            "10010971.SHO",
            "510050.SH",
            2.85,
            "2026-10-04",
            "call",
            0.2,
            "SHO",
            0.53,
            0.9,
            -0.001,
            0.06,
            "miniqmt",
        )
        monkeypatch.setattr(p, "_compute_iv_for_option", lambda *a, **k: [stub_row])
        payload = FetchPayload(
            table="c1_market.option_iv_surface",
            symbols=["10010971.SHO"],
            start=_TRADE_DAY,
            end=_TRADE_DAY,
        )
        results = list(p._fetch_option_iv_surface(payload, SourcePolicy()))
        assert results, "进料口未产出任何批次"
        return list(results[0].columns), len(results[0].rows[0])

    def test_columns_include_delta_and_vega(self, monkeypatch) -> None:
        cols, _ = self._captured(monkeypatch)
        missing = {"delta", "gamma", "theta", "vega"} - set(cols)
        assert not missing, f"columns 未声明 {missing} → 落库恒为 DDL DEFAULT 0（SVX-1-P0 根因）"

    def test_row_width_matches_columns(self, monkeypatch) -> None:
        """列名与行元组同序等宽——否则 TSV 字段错位（Code 27/串列）。"""
        cols, width = self._captured(monkeypatch)
        assert width == len(cols)

    def test_iv_and_data_source_positions_stable(self, monkeypatch) -> None:
        """iv 仍在 index 6、data_source 仍是末列（既有血缘断言的位置契约）。"""
        cols, _ = self._captured(monkeypatch)
        assert cols[6] == "iv"
        assert cols[-1] == "data_source"


# ---------------------------------------------------------------------------
# ② delta 必须是「同一套 BS 真源」的产物，且量级/符号合理
# ---------------------------------------------------------------------------


class TestDeltaFromSingleBsSource:
    """② delta 由仓内唯一 BS Greeks 真源 calc_bs_greeks 在**反解出的 IV** 上算得。"""

    def test_feed_delegates_to_greeks_ssot_with_solved_iv(self, monkeypatch) -> None:
        """录参替身：进料口 MUST 委托 calc_bs_greeks（禁第二套 BS 公式），且
        sigma 入参 = 本行反解出的 iv（不是历史波动率、不是初值 0.3）。"""
        seen: dict = {}

        def _spy(S, K, T, r, sigma, opt_type):
            seen.update(S=S, K=K, T=T, r=r, sigma=sigma, opt_type=opt_type)
            return {"delta": 0.5321, "gamma": 0.9876, "theta": -0.0011, "vega": 0.0543}

        monkeypatch.setattr(MiniQmtIngestProvider, "calc_bs_greeks", staticmethod(_spy))
        rows = MiniQmtIngestProvider._compute_iv_rows(_ctx())
        assert len(rows) == 1
        rec = _row_dict(rows[0])
        assert rec["delta"] == 0.5321
        assert seen, "未调用 BS Greeks 真源（可能内联了第二套公式）"
        assert seen["sigma"] == pytest.approx(rec["iv"], rel=0, abs=1e-12)
        assert seen["K"] == 2.85 and seen["opt_type"] == "call" and seen["T"] > 0

    def test_call_atm_delta_in_plausible_band(self) -> None:
        """真源不替身：ATM call（S=K=2.85, IV≈0.20, DTE=18）delta ∈ (0.45,0.60)。"""
        delta = _row_dict(MiniQmtIngestProvider._compute_iv_rows(_ctx())[0])["delta"]
        assert delta is not None
        assert 0.45 < delta < 0.60, f"ATM call delta={delta}（0 或 >0.6 皆异常）"
        assert abs(abs(delta) - 0.5) < 0.15, "ATM call 必须通过消费端 ATM 筛子"

    def test_put_atm_delta_is_negative(self) -> None:
        delta = _row_dict(MiniQmtIngestProvider._compute_iv_rows(_ctx(opt_type="put"))[0])["delta"]
        assert -0.60 < delta < -0.40
        assert abs(abs(delta) - 0.5) < 0.15  # 消费端取 abs → put 同归 ATM 池

    def test_delta_equals_greeks_ssot_output(self) -> None:
        """落库 delta 与真源在同一 (S,K,T,r,iv,type) 上的输出逐位相等（无二次加工）。"""
        rec = _row_dict(MiniQmtIngestProvider._compute_iv_rows(_ctx(dte=46))[0])
        expected = MiniQmtIngestProvider.calc_bs_greeks(
            2.85, 2.85, max(46 / 365.0, 0.001), _R, rec["iv"], "call"
        )
        assert rec["delta"] == pytest.approx(expected["delta"], abs=1e-9)
        assert rec["vega"] == pytest.approx(expected["vega"], abs=1e-9)
        assert rec["gamma"] == pytest.approx(expected["gamma"], abs=1e-9)

    def test_otm_delta_is_small_but_not_zero(self) -> None:
        """虚值（K=3.05, DTE=18）delta 小但 MUST 非 0——0 是「缺失」的伪装色。"""
        delta = _row_dict(MiniQmtIngestProvider._compute_iv_rows(_ctx(strike=3.05))[0])["delta"]
        assert 0 < delta < 0.45


# ---------------------------------------------------------------------------
# ③ IV 反解失败 → 整行不落（禁 None→DEFAULT 0 的静默伪装）
# ---------------------------------------------------------------------------


class TestUnsolvedIvNeverBecomesSilentZero:
    """③ 解不出 IV 的行不落库：非 Nullable Decimal + `\\N` → DEFAULT 0 = 假 0。"""

    def test_absurd_price_drops_row(self, caplog) -> None:
        ctx = _ctx(opt_close=5.0, spot=3.05)  # 权利金远高于标的 → Newton 不收敛
        assert _solve_iv(3.05, 2.85, max(18 / 365.0, 0.001), _R, 5.0, "call") is None
        with caplog.at_level(logging.WARNING):
            rows = MiniQmtIngestProvider._compute_iv_rows(ctx)
        assert rows == [], "IV 反解失败仍落行 → iv/delta 被 DEFAULT 0 伪装成真实值"
        assert any(r.levelno >= logging.WARNING for r in caplog.records), "降级必须非静默"

    def test_partial_dates_keep_only_solved(self) -> None:
        """多日链：坏价日剔除、好价日保留（不得整批连坐，也不得填 0）。"""
        ctx = _ctx()
        ctx.opt_df = pd.DataFrame(
            {"close": [_premium(2.85, 18, "call"), 5.0]},
            index=pd.Index([_day_str(), _day_str(1)], dtype=object),
        )
        ctx.ul_df = pd.DataFrame(
            {"close": [2.85, 3.05]}, index=pd.Index([_day_str(), _day_str(1)], dtype=object)
        )
        rows = MiniQmtIngestProvider._compute_iv_rows(ctx)
        assert [r[0] for r in rows] == [_TRADE_DAY.isoformat()]
        assert all(r[6] and r[6] > 0 for r in rows)


# ---------------------------------------------------------------------------
# ④ 端到端：进料口产出 → 消费端必须出数（当前恒空 = 本 P0 的定义）
# ---------------------------------------------------------------------------


class TestFeedReachesSyntheticVix:
    """④ 把进料口真实产出的行装配成消费端口径 → compute_synthetic_vix MUST 出数。"""

    @staticmethod
    def _chain_rows(underlying: str, base_sigma: float) -> list[tuple]:
        rows: list[tuple] = []
        for dte, sigma in ((18, base_sigma), (46, base_sigma + 0.02)):
            for opt_type in ("call", "put"):
                ctx = _ctx(underlying=underlying, dte=dte, opt_type=opt_type)
                price = _bs_price(2.85, 2.85, max(dte / 365.0, 0.001), _R, sigma, opt_type)
                ctx.opt_df = pd.DataFrame(
                    {"close": [round(price, 4)]}, index=pd.Index([_day_str()], dtype=object)
                )
                got = MiniQmtIngestProvider._compute_iv_rows(ctx)
                assert len(got) == 1
                rows.append(got[0])
        return rows

    def test_surface_from_feed_produces_nonempty_vix(self) -> None:
        rows = self._chain_rows("510050.SH", 0.20) + self._chain_rows("510300.SH", 0.22)
        surface = _as_loader_frame(rows)
        assert len(surface) > 0
        assert (surface["delta"] != 0).all(), "进料口仍产出 delta=0（SVX-1-P0 未治）"
        vix = compute_synthetic_vix(surface)
        assert not vix.empty, "期权 IV 主路径零产出（ATM 筛子全排除）"
        assert vix.between(10.0, 40.0).all(), f"VIX 档位异常：{list(vix)}"

    def test_vix_matches_hand_interpolation_of_feed_ivs(self) -> None:
        """端到端数值锚：进料口 IV → ATM 池均值 → 30 天线性插值 → ×100，手算可比。"""
        rows = self._chain_rows("510050.SH", 0.20)
        ivs = sorted(_row_dict(r)["iv"] for r in rows)
        near, far = ivs[0], ivs[-1]
        expected = (near + (far - near) * (30 - 18) / (46 - 18)) * 100
        vix = compute_synthetic_vix(_as_loader_frame(rows))
        assert vix.iloc[0] == pytest.approx(expected, rel=1e-3)


# ---------------------------------------------------------------------------
# ⑤ 加载谓词：真库 underlying 带交易所后缀，裸代码谓词恒 0 行
# ---------------------------------------------------------------------------


class TestLoaderPredicateMatchesProductionShape:
    """⑤ 取证：`underlying IN ('510050','510300')` → 0 行；带 .SH 后缀 → 9653 行。"""

    @staticmethod
    def _loader(monkeypatch, tsv: str) -> tuple[object, list[str]]:
        from zephyr.regime.features import regime_data_loader as rdl

        sqls: list[str] = []
        monkeypatch.setattr(rdl.ch_reader, "query", lambda sql: sqls.append(sql) or tsv)
        return rdl.RegimeDataLoader(
            data_load_start="2023-01-01", backtest_end="2026-09-16"
        ), sqls

    @staticmethod
    def _prod_tsv(n: int = 2) -> str:
        """生产形态 TSV：underlying 带 .SH 后缀、iv/delta 为小数。"""
        return "\n".join(
            "\t".join(
                [
                    f"2026-09-{15 + i}",
                    "510050.SH",
                    "2.85",
                    "2026-10-04",
                    "0.201234",
                    "call",
                    "0.532100",
                    "0.005432",
                ]
            )
            for i in range(n)
        )

    def test_predicate_is_suffix_agnostic(self, monkeypatch) -> None:
        loader, sqls = self._loader(monkeypatch, self._prod_tsv())
        df = loader._load_option_iv()
        assert sqls, "未发起查询"
        assert "underlying IN ('510050', '510300')" not in sqls[-1], (
            "谓词用裸代码而库内是 '510050.SH' → 恒 0 行（IV 主路径第二道结构性零）"
        )
        assert df is not None and len(df) == 2
        assert df["delta"].notna().all()

    def test_nonpositive_iv_not_loaded(self, monkeypatch) -> None:
        """iv=0 的库内行（反解失败被 DEFAULT 0 伪装）不得进入曲面。"""
        loader, sqls = self._loader(monkeypatch, "")
        assert loader._load_option_iv() is None
        assert "iv > 0" in sqls[-1]

    def test_empty_result_is_non_silent(self, monkeypatch, caplog) -> None:
        loader, _ = self._loader(monkeypatch, "")
        with caplog.at_level(logging.WARNING):
            assert loader._load_option_iv() is None
        msgs = " | ".join(r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING)
        assert "option_iv_surface" in msgs


# ---------------------------------------------------------------------------
# ⑥ 消费端 fail-closed：把「缺失」与「真 0」分开，且不可静默
# ---------------------------------------------------------------------------


class TestConsumerTreatsMissingDeltaAsFailClosed:
    """⑥ 曲面有行但 ATM 池为空 → 仍返回空 Series（契约不变）但 MUST 出声。"""

    @staticmethod
    def _surface(deltas: list, ivs: list) -> pd.DataFrame:
        n = len(deltas)
        df = pd.DataFrame(
            {
                "trade_date": pd.to_datetime(["2026-09-16"] * n),
                "underlying": ["510050.SH"] * n,
                "expiry": ["2026-10-04"] * n,
                "iv": ivs,
                "delta": deltas,
                "option_type": ["call"] * n,
                "strike": [2.85] * n,
                "vega": [0.05] * n,
            }
        )
        return df.set_index(["trade_date", "underlying"]).sort_index()

    def test_all_zero_delta_warns(self, caplog) -> None:
        """库里历史 delta=0 行（或上游忘落）→ 空产出 + WARNING 点名 delta（禁静默降级）。"""
        with caplog.at_level(logging.WARNING):
            out = compute_synthetic_vix(self._surface([0.0, 0.0], [0.20, 0.22]))
        assert out.empty  # 契约：数据缺失返回空 Series（调用方回退 vol_pct）
        msgs = " | ".join(r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING)
        assert "delta" in msgs, f"零产出必须点名可疑字段而非只说「算得空序列」：{msgs}"

    def test_nan_delta_excluded_without_killing_valid_rows(self) -> None:
        """delta 为 NULL（显式不可用）→ 该行不入池，但同面有效行照常出数。"""
        out = compute_synthetic_vix(self._surface([np.nan, 0.52], [0.20, 0.22]))
        assert len(out) == 1
        assert out.iloc[0] == pytest.approx(22.0, rel=1e-9)

    def test_nonpositive_iv_excluded_with_warning(self, caplog) -> None:
        """iv<=0 不是「零波动」而是「坏行」——混入 ATM 池会把 VIX 拉半（禁静默）。"""
        with caplog.at_level(logging.WARNING):
            out = compute_synthetic_vix(self._surface([0.52, 0.51], [0.20, 0.0]))
        assert out.iloc[0] == pytest.approx(20.0, rel=1e-9), "iv=0 行污染了 ATM 均值"
        msgs = " | ".join(r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING)
        assert "iv" in msgs

    def test_healthy_surface_is_silent(self, caplog) -> None:
        """正常曲面不得 spam WARNING（降级告警只在真降级时响）。"""
        with caplog.at_level(logging.WARNING):
            out = compute_synthetic_vix(self._surface([0.52, 0.49], [0.20, 0.22]))
        assert not out.empty
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
