# [TTL] permanent
# [MODULE] tests.legacy_zephyr.factor.technical_indicators.test_squeeze_wad_reference_parity
# [DOMAIN] D_FACTOR
"""SQUEEZE 与 WAD 两件"实现有错"判据的参考实现对拍（2026-10-10 终清总队，裁定#489① 复活条件面）。

大白话：调查册判这两件实现偏离了它们自己声明的权威口径——
SQUEEZE 的 KC 通道用了普通振幅而非真实波幅、中轨用 EMA 而非 SMA、动量基座缺 Donchian 分量；
WAD 把 Tulip 的 `min(昨收,今低)` 误读成"昨低"。本件不重复论证偏离（取证在调查册），
只把修回后的实现按**外部原文逐行独立重写一遍**再对拍，于是：
① 修对了——两条曲线在含跳空的合成行情上逐点相等；
② 修之前是错的——同一参考尺下旧实现必翻红（本件带旧口径负例，不是只测新码）。

判据来源（本件自证的外部口径，非本仓自话自说）：
  SQUEEZE：LazyBear《Squeeze Momentum Indicator》Pine 原文
    ma=sma(source,lengthKC)；range=useTrueRange?tr:(high-low)（默认 true）；
    x=source-avg(avg(highest(high,L),lowest(low,L)),sma(close,L))；val=linreg(x,L,0)
  WAD：Tulip Indicators ti_wad：c>yc ⇒ sum+=c-MIN(yc,low[i])；c<yc ⇒ sum+=c-MAX(yc,high[i])
零网络零生产写，纯合成 bar。
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators.momentum import SQUEEZE
from zephyr.factor.technical_indicators.volume import WAD

N = 20


def _synthetic(n_bars: int = 90, gap_at: tuple[int, ...] = (12, 41, 68)) -> pd.DataFrame:
    """含跳空缺口的合成 OHLC：跳空日 TR 严格大于 H−L，是 SQUEEZE/WAD 两把尺的判别力来源。

    确定性生成（不依赖随机种子），同一条行情既可喂新实现也可喂旧口径负例。
    """
    closes: list[float] = [100.0]
    for i in range(1, n_bars):
        drift = 0.6 if (i % 7) < 3 else -0.5
        if i in gap_at:
            drift -= 6.0  # 跳空：当日价格整体离开前收，制造 |C_p| 项主导的 TR
        closes.append(round(closes[-1] + drift, 6))
    highs, lows = [], []
    for i, c in enumerate(closes):
        widen = 1.4 if i in gap_at else 0.5
        highs.append(round(c + widen, 6))
        lows.append(round(c - widen, 6))
    idx = pd.date_range("2024-01-01", periods=n_bars, freq="D")
    return pd.DataFrame({"high": highs, "low": lows, "close": closes, "volume": [1e6] * n_bars}, index=idx)


def _ref_true_range(high, low, close):
    tr = [high[0] - low[0]]
    for i in range(1, len(close)):
        tr.append(max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])))
    return tr


def _ref_squeeze(df: pd.DataFrame) -> tuple[list[float], list[float]]:
    """按 LazyBear 原文逐式重写（与本仓实现无关的第三条推导路径）。"""
    h = [float(x) for x in df["high"]]
    l = [float(x) for x in df["low"]]  # noqa: E741
    c = [float(x) for x in df["close"]]
    m = len(c)
    tr = _ref_true_range(h, l, c)
    on = [0.0] * m
    mom = [float("nan")] * m

    def sma(vals, i):
        seg = vals[i - N + 1 : i + 1]
        return sum(seg) / N

    def base_at(j):
        # base 序列本身要 N 根才有值 ⇒ 动量窗需要 2N-2 根预热（两侧同一事实，见 warmup 用例）
        assert j >= N - 1
        hh = max(h[j - N + 1 : j + 1])
        ll = min(l[j - N + 1 : j + 1])
        return c[j] - 0.5 * (0.5 * (hh + ll) + sma(c, j))

    for i in range(N - 1, m):
        basis = sma(c, i)
        var = sum((x - basis) ** 2 for x in c[i - N + 1 : i + 1]) / N
        dev = 2.0 * math.sqrt(var)
        rng = sma(tr, i)
        kc_upper, kc_lower = basis + 1.5 * rng, basis - 1.5 * rng
        on[i] = 1.0 if (basis - dev > kc_lower) and (basis + dev < kc_upper) else 0.0
        if i < 2 * N - 2:
            continue  # base 序列在此之前的头几根是 NaN，linreg 无定义（与实现同口径）
        ys = [base_at(j) for j in range(i - N + 1, i + 1)]
        xs = list(range(N))
        xm = sum(xs) / N
        ym = sum(ys) / N
        num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys, strict=False))
        den = sum((x - xm) ** 2 for x in xs)
        mom[i] = ym + (num / den) * ((N - 1) - xm)
    return on, mom


def _ref_wad(df: pd.DataFrame) -> list[float]:
    """按 Tulip ti_wad 逐式重写：TRL=min(昨收,今低)、TRH=max(昨收,今高)。"""
    h = [float(x) for x in df["high"]]
    l = [float(x) for x in df["low"]]  # noqa: E741
    c = [float(x) for x in df["close"]]
    out = [0.0]
    acc = 0.0
    for i in range(1, len(c)):
        yc = c[i - 1]
        if c[i] > yc:
            acc += c[i] - min(yc, l[i])
        elif c[i] < yc:
            acc += c[i] - max(yc, h[i])
        out.append(acc)
    return out


class TestSqueezeMatchesLazyBearReference:
    def setup_method(self) -> None:
        self.df = _synthetic()
        out = SQUEEZE().compute(self.df)
        self.on = [float(x) for x in out["squeeze_on"]]
        self.mom = [float(x) for x in out["squeeze_mom"]]
        self.ref_on, self.ref_mom = _ref_squeeze(self.df)

    def _on_channel(self, rng: pd.Series, kc_mult: float) -> pd.Series:
        """KC 中轨修回 SMA 后与 BB 中轨同源 ⇒ squeeze_on 恰化为 dev < kc_mult × rng。

        这条恒等式让"通道用 TR 还是用 H−L"变成可以用 kc_mult 定点放大的可观测差异，
        而不是只能靠造数据碰运气（造不出差异的负例＝假绿，见下面的显式断言）。
        """
        close = self.df["close"]
        basis = close.rolling(N).mean()
        dev = 2.0 * close.rolling(N).std(ddof=0)
        return (dev < kc_mult * rng).fillna(False).astype(float)

    def test_kc_channel_uses_true_range_not_plain_range(self):
        tr = _ref_true_range(
            [float(x) for x in self.df["high"]],
            [float(x) for x in self.df["low"]],
            [float(x) for x in self.df["close"]],
        )
        rng_tr = pd.Series(tr, index=self.df.index).rolling(N).mean()
        rng_rl = (self.df["high"] - self.df["low"]).rolling(N).mean()
        # 判别力前置闸：必须存在一个 kc_mult，使 TR 通道与 H−L 通道给出不同的 squeeze_on。
        # 找不到就判本件失败——不许用"两边都一样所以都通过"冒充测过。
        discriminating = None
        for kc_mult in [1.0 + 0.05 * k for k in range(60)]:
            a = self._on_channel(rng_tr, kc_mult)
            b = self._on_channel(rng_rl, kc_mult)
            if not a.equals(b):
                discriminating = kc_mult
                break
        assert discriminating is not None, "合成行情下 TR 与 H−L 两通道从不分叉，本件无判别力"
        got = [float(x) for x in SQUEEZE().compute(self.df, kc_mult=discriminating)["squeeze_on"]]
        want_tr = [float(x) for x in self._on_channel(rng_tr, discriminating)]
        want_rl = [float(x) for x in self._on_channel(rng_rl, discriminating)]
        assert got == want_tr, f"kc_mult={discriminating} 处 squeeze_on 偏离 TR 参考"
        assert got != want_rl, "新实现在判别点上与旧 H−L 口径仍相同 ⇒ 那条修复没落地"

    def test_squeeze_on_default_params_matches_reference(self):
        diffs = [(i, a, b) for i, (a, b) in enumerate(zip(self.on, self.ref_on, strict=False)) if a != b]
        assert diffs == [], f"默认参数下 squeeze_on 偏离 LazyBear 参考：{diffs[:5]}"

    def test_squeeze_mom_matches_reference_linreg(self):
        pairs = [
            (i, a, b)
            for i, (a, b) in enumerate(zip(self.mom, self.ref_mom, strict=False))
            if not (math.isnan(a) and math.isnan(b)) and abs(a - b) > 1e-9
        ]
        assert pairs == [], f"squeeze_mom 偏离参考 linreg：{pairs[:5]}"

    def test_mom_reference_is_not_vacuously_equal(self):
        """负例：动量基座缺 Donchian 分量（旧写法 linreg(close)−kc_mid）必须对不上参考。"""
        close = self.df["close"]
        basis = close.rolling(N).mean()
        y = close.to_numpy(dtype=float)
        m = len(y)
        mom_old = np.full(m, np.nan)
        x = np.arange(N, dtype=float)
        x_mean = x.mean()
        x_ss = ((x - x_mean) ** 2).sum()
        for i in range(N - 1, m):
            seg = y[i - N + 1 : i + 1]
            if np.isnan(seg).any():
                continue
            b = ((x - x_mean) * (seg - seg.mean())).sum() / x_ss
            mom_old[i] = seg.mean() + b * (x[-1] - x_mean) - basis.iloc[i]
        both = [
            (a, c)
            for a, c in zip(self.mom[2 * N - 2 :], mom_old[2 * N - 2 :], strict=False)
            if not (math.isnan(a) or math.isnan(c))
        ]
        assert both, "参考与旧口径都没产出可比值，本件是空的"
        assert any(abs(a - c) > 1e-6 for a, c in both), (
            "旧动量写法与参考逐点相同 ⇒ 这条测不出 Donchian 分量缺失，判据是假的"
        )

    def test_warmup_nan_only_before_double_window(self):
        """动量基座本身要 N 根，再取 N 根做 linreg ⇒ 头 2N-2 根无定义（不是 N-1）。"""
        assert all(math.isnan(v) for v in self.mom[: 2 * N - 2])
        assert not any(math.isnan(v) for v in self.mom[2 * N - 2 :])

    def test_old_misread_formula_is_distinguishable(self):
        """负例：旧口径（H−L 通道 + EMA 中轨 + linreg(close)−kc_mid）不得等于新结果。

        若这条红了，说明"修复"没改变任何读数＝只是把注释改了改。
        """
        close = self.df["close"]
        basis = close.rolling(N).mean()
        dev = 2.0 * close.rolling(N).std(ddof=0)
        tr_old = self.df["high"] - self.df["low"]
        kc_mid_old = close.ewm(span=N, adjust=False).mean()
        rng_old = tr_old.rolling(N).mean()
        on_old = (
            ((basis - dev) > (kc_mid_old - 1.5 * rng_old)) & ((basis + dev) < (kc_mid_old + 1.5 * rng_old))
        ).astype(float)
        assert not np.array_equal(on_old.to_numpy(), np.array(self.on)), (
            "新旧 squeeze_on 完全一致 ⇒ 合成数据没有判别力，本件应换数据而不是宣布通过"
        )

    def test_meta_declares_input_columns_unchanged_no_schema_change(self):
        """修复只用 high/low/close 的滚动量，不引入新输入列 ⇒ 不碰 DDL、不碰回填依赖。"""
        assert SQUEEZE().meta.input_columns == ["high", "low", "close"]
        assert SQUEEZE().meta.output_columns == ["squeeze_on", "squeeze_mom"]


class TestWadMatchesTulipReference:
    def setup_method(self) -> None:
        self.df = _synthetic()
        self.got = [float(x) for x in WAD().compute(self.df)["wad"]]
        self.ref = _ref_wad(self.df)

    def test_wad_matches_trh_trl_reference(self):
        bad = [(i, a, b) for i, (a, b) in enumerate(zip(self.got, self.ref, strict=False)) if abs(a - b) > 1e-9]
        assert bad == [], f"wad 偏离 Tulip ti_wad 参考：{bad[:5]}"

    def test_old_misread_formula_diverges_and_never_converges(self):
        """负例：旧误读口径（C−昨低 / C−昨高）与真口径的偏差随 cumsum 路径累积，不收敛。"""
        c = self.df["close"]
        diff = c.diff()
        tad_old = np.where(
            diff > 0,
            c - self.df["low"].shift(1),
            np.where(diff < 0, c - self.df["high"].shift(1), 0.0),
        )
        old = pd.Series(tad_old, index=self.df.index).cumsum().to_numpy(dtype=float)
        abs_dev = np.abs(old[1:] - np.array(self.ref[1:]))
        assert abs_dev.max() > 0.1, "两口径差异不足 0.1 ⇒ 本件对这把尺没有判别力（该换数据不是该收工）"
        assert abs_dev[-1] > abs_dev[0], "偏差不随路径累积 ⇒ 不是'分叉永不收敛'那种错，结论要重看"

    def test_flat_close_contributes_zero(self):
        """C==昨收 ⇒ TAD=0（两版实现都应如此，这条钉住不回归）。"""
        df = _synthetic(n_bars=60)
        flat = df.copy()
        flat["close"] = 100.0
        flat["high"] = 101.0
        flat["low"] = 99.0
        out = WAD().compute(flat)["wad"]
        assert (np.asarray(out, dtype=float) == 0.0).all()


def test_both_fixes_return_finite_series_on_normal_data():
    df = _synthetic(n_bars=80)
    for cls, col in ((SQUEEZE, "squeeze_mom"), (WAD, "wad")):
        vals = np.asarray(cls().compute(df)[col], dtype=float)
        tail = vals[~np.isnan(vals)]
        assert len(tail) > 0
        assert np.isfinite(tail).all(), f"{cls.__name__}.{col} 出现 ±Inf（写链 isfinite 闸会拦）"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
