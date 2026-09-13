# [BLUEPRINT] MOD-SIG-146 | docs/03_modules/_domain_signal/pattern_series_transform/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.series_transform
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] numpy; pandas（仅输入容器）；zephyr.signal_ashare.strategy_signal.unified_pattern_engine（适配器消费方，可选）
# [CONSUMERS] unified_pattern_engine 几何腿（TransformedSeries→伪 OHLC 适配）；形态事件落库口（事件统计走 MOD-SIG-145）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] PIT 铁律：全部 close-to-close 构造（已完成 bar 收盘定砖/定列/定拐弯），禁盘中触格——盘中触格=回测偷看未来；变换序列事件锚=确认 bar（anchor_idx/confirmed_date 恒指回原序列）；纯函数无外部状态无 IO
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] brick_size/box_size/reversal_threshold 非正->ValueError; 输入序列<2 bar->ValueError; 缺 close->ValueError
# [TESTS] tests/signal_ashare/test_series_transform.py
# [A_module] module_id=MOD-SIG-146 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""序列变换层（MOD-SIG-146）：OHLCV 时间序列 → 替代价格表示（去噪底座）。

K 线族按时间记账（每天一笔，没动静也记）；本层按"价格真动了"记账：

    RenkoTransform(brick_size)          固定砖块：涨够一格画一块砖
    PnFTransform(box_size, reversal)    点数列：X/O 列，反向够 N 格换列
    KagiTransform(reversal_threshold)   阈值拐弯线：反转够阈值才拐

三实现共用 SeriesTransform 接口（transform(closes, dates) -> TransformedSeries）。
消费端：TransformedSeries.to_ohlcv_like() 产伪 OHLC 序列（brick/column 段映射为
合成 bar），直接喂 MOD-SIG-091 引擎 recognize(highs, lows, closes)——既有几何
形态（双顶/双底/趋势线/通道/突破）在去噪表示上重跑，引擎零改动。

PIT 设计（防前视铁律，蓝图 §2）：
    输入只需 close 序列（不读 high/low → 盘中触格逻辑根本不存在）；
    每个变换事件的 confirmed_idx=触发该事件的收盘 bar 下标，confirmed_date=该
    bar 日期；下游统计按确认日取前视收益（走 MOD-SIG-145 通道）。

施工序 Renko→P&F→Kagi；一次大跳可产生多块砖（Renko），列反转按 reversal_boxes。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass(frozen=True, slots=True)
class TransformEvent:
    """单个变换事件（一块砖 / 一个格 / 一次拐弯段延伸）。

    direction: "up" | "down"
    price_lo / price_hi: 事件覆盖的价格区间（砖底砖顶 / 格底格顶 / 拐弯段两端）
    confirmed_idx / confirmed_date: 触发确认的原序列 bar（PIT 锚，恒回指）
    """

    direction: str
    price_lo: float
    price_hi: float
    confirmed_idx: int
    confirmed_date: object
    kind: str = "brick"  # brick | box | turn


@dataclass(frozen=True, slots=True)
class TransformedSeries:
    """变换后序列：事件流 + 参数元数据。"""

    transform_name: str  # renko | pnf | kagi
    events: tuple[TransformEvent, ...]
    params: dict
    warnings: tuple[str, ...] = field(default=())

    def __len__(self) -> int:
        return len(self.events)

    def to_ohlcv_like(self) -> dict:
        """伪 OHLC 序列（喂引擎 recognize 的 highs/lows/closes/dates）。

        每个事件映射为一根合成 bar：up 事件 open=lo/close=hi，down 反之；
        high/low 即该事件价格两端。时间轴用 confirmed_date（非均匀，语义=
        事件驱动序）。
        """
        dates: list = []
        highs: list[float] = []
        lows: list[float] = []
        closes: list[float] = []
        for ev in self.events:
            dates.append(ev.confirmed_date)
            if ev.direction == "up":
                o, c = ev.price_lo, ev.price_hi
            else:
                o, c = ev.price_hi, ev.price_lo
            highs.append(max(o, c))
            lows.append(min(o, c))
            closes.append(c)
        return {"dates": dates, "highs": highs, "lows": lows, "closes": closes}


class SeriesTransform:
    """变换接口基类（子类实现 _transform）。"""

    name = "base"

    def __init__(self, **params):
        self.params = dict(params)
        self._validate_params()

    def _validate_params(self) -> None:  # pragma: no cover - 子类覆写
        return None

    def transform(self, closes: Sequence[float], dates: Sequence | None = None) -> TransformedSeries:
        closes_arr = np.asarray(closes, dtype=np.float64)
        if closes_arr.ndim != 1 or closes_arr.size < 2:
            raise ValueError("closes 须为长度>=2 的一维序列")
        if not np.all(np.isfinite(closes_arr)) or np.any(closes_arr <= 0):
            raise ValueError("closes 须为正有限序列")
        if dates is None:
            dates = list(range(closes_arr.size))
        if len(dates) != closes_arr.size:
            raise ValueError("dates 与 closes 等长")
        events = self._transform(closes_arr, list(dates))
        return TransformedSeries(transform_name=self.name, events=tuple(events), params=dict(self.params))

    def _transform(self, closes: np.ndarray, dates: list) -> list[TransformEvent]:  # pragma: no cover
        raise NotImplementedError


class RenkoTransform(SeriesTransform):
    """Renko 砖块（close-to-close）：价格自最近砖界再走够 brick_size 才出新砖。

    一次大跳可连出多块砖；砖从"最近砖界"起按 size 阶梯推进，不整除部分留待
    后续（业界通行的 fixed-brick 口径，不重定基）。
    """

    name = "renko"

    def __init__(self, brick_size: float):
        self.brick_size = float(brick_size)
        super().__init__(brick_size=self.brick_size)

    def _validate_params(self) -> None:
        if not self.brick_size > 0:
            raise ValueError("brick_size 须为正")

    def _transform(self, closes: np.ndarray, dates: list) -> list[TransformEvent]:
        size = self.brick_size
        events: list[TransformEvent] = []
        last_top: float | None = None
        last_bottom: float | None = None
        for i, px in enumerate(closes):
            if last_top is None:
                last_top = px
                last_bottom = px
                continue
            while px >= last_top + size:
                lo, hi = last_top, last_top + size
                events.append(TransformEvent("up", lo, hi, i, dates[i], "brick"))
                last_top, last_bottom = hi, lo
            while px <= last_bottom - size:
                lo, hi = last_bottom - size, last_bottom
                events.append(TransformEvent("down", lo, hi, i, dates[i], "brick"))
                last_top, last_bottom = hi, lo
        return events


class PnFTransform(SeriesTransform):
    """Point & Figure 点数列（close-to-close）。

    X 列（up）：close 突破列顶再加格；O 列（down）：跌破列底再加格。
    反转：自当前列极值逆向走够 reversal_boxes 格即换列。
    """

    name = "pnf"

    def __init__(self, box_size: float, reversal_boxes: int = 3):
        self.box_size = float(box_size)
        self.reversal_boxes = int(reversal_boxes)
        super().__init__(box_size=self.box_size, reversal_boxes=self.reversal_boxes)

    def _validate_params(self) -> None:
        if not self.box_size > 0:
            raise ValueError("box_size 须为正")
        if self.reversal_boxes < 1:
            raise ValueError("reversal_boxes 须>=1")

    def _transform(self, closes: np.ndarray, dates: list) -> list[TransformEvent]:
        size = self.box_size
        rev = self.reversal_boxes
        events: list[TransformEvent] = []
        direction: str | None = None  # "up"=X 列, "down"=O 列
        col_top: float | None = None
        col_bottom: float | None = None
        for i, px in enumerate(closes):
            if direction is None:
                # 首 bar 初始化：默认 X 列起步（首格在首个反向/顺势突破时才产出）
                direction = "up"
                col_top = col_bottom = px
                continue
            if direction == "up":
                while px >= col_top + size:  # 列顶再进一格
                    lo, hi = col_top, col_top + size
                    events.append(TransformEvent("up", lo, hi, i, dates[i], "box"))
                    col_top = hi
                if px <= col_top - rev * size:  # 逆走够 N 格换列
                    direction = "down"
                    col_bottom = col_top - size
                    events.append(TransformEvent("down", col_bottom, col_top, i, dates[i], "box"))
            else:
                while px <= col_bottom - size:
                    lo, hi = col_bottom - size, col_bottom
                    events.append(TransformEvent("down", lo, hi, i, dates[i], "box"))
                    col_top, col_bottom = hi, lo
                if px >= col_bottom + rev * size:
                    direction = "up"
                    col_top = col_bottom + size
                    events.append(TransformEvent("up", col_bottom, col_top, i, dates[i], "box"))
        return events


class KagiTransform(SeriesTransform):
    """Kagi 阈值拐弯线（close-to-close）。

    段（segment）沿当前方向延伸至极值；自极值逆向收够 reversal_threshold
    即产生一个拐弯事件（direction=新方向），极值重置。
    """

    name = "kagi"

    def __init__(self, reversal_threshold: float):
        self.reversal_threshold = float(reversal_threshold)
        super().__init__(reversal_threshold=self.reversal_threshold)

    def _validate_params(self) -> None:
        if not self.reversal_threshold > 0:
            raise ValueError("reversal_threshold 须为正")

    def _transform(self, closes: np.ndarray, dates: list) -> list[TransformEvent]:
        thr = self.reversal_threshold
        events: list[TransformEvent] = []
        direction: str | None = None
        extreme: float | None = None  # 当前段极值（up=段最高, down=段最低）
        seg_start: float | None = None
        for i, px in enumerate(closes):
            if direction is None:
                direction = "up" if px >= closes[0] else "down"
                extreme = px
                seg_start = px
                continue
            if direction == "up":
                if px > extreme:
                    extreme = px
                if extreme - px >= thr:  # 自高点回撤够阈值 → 拐向下
                    events.append(TransformEvent("down", px, extreme, i, dates[i], "turn"))
                    direction = "down"
                    extreme = px
                    seg_start = px
            else:
                if px < extreme:
                    extreme = px
                if px - extreme >= thr:
                    events.append(TransformEvent("up", px, extreme, i, dates[i], "turn"))
                    direction = "up"
                    extreme = px
                    seg_start = px
        return events


def adapt_to_engine(series: TransformedSeries, symbol: str) -> dict:
    """TransformedSeries → unified_pattern_engine.recognize 入参字典。"""
    pseudo = series.to_ohlcv_like()
    return {
        "symbol": symbol,
        "highs": pseudo["highs"],
        "lows": pseudo["lows"],
        "closes": pseudo["closes"],
        "dates": pseudo["dates"],
    }


__all__ = [
    "SeriesTransform",
    "RenkoTransform",
    "PnFTransform",
    "KagiTransform",
    "TransformEvent",
    "TransformedSeries",
    "adapt_to_engine",
]
