# [BLUEPRINT] MOD-SIG-075 | 待统筹登记（缺口总账 GAP-F-41 行）
# [MODULE] zephyr.signal_ashare.cross_asset_ratio_monitor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy（纯函数核；多源价格由上游装载注入，本模块零外网/零 DB——禁真连外网）
# [CONSUMERS] （候选：宏观分析页比价卡，GAP-F-41 消费位；同族 cross_market_conduction_sensor MOD-SIG-038）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 四比价封闭 {gold_silver 金银比, gold_oil 金油比, copper_gold 铜金比, gold_copper 金铜比}；比率=分子/分母逐日日期交集对齐；z-score=最新值对滚动窗口（默认 250 日）标准化；分档封闭 {极高,偏高,中性,偏低,极低}（|z|≥2 极 / 1~2 偏 / <1 中性）；宏观含义标注=静态规则表（文档化初版，非交易信号）；输入校验 fail-closed（缺资产/非正价/交集不足/窗口非法）；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-41 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（资产缺失/价格非法/日期非法/交集不足/窗口非法，fail-closed）
# [TESTS] tests/signal_ashare/test_cross_asset_ratio_monitor.py
# [A_module] module_id=MOD-SIG-075 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""跨资产比价衍生计算（MOD-SIG-075，GAP-F-41）。

缺口总账 GAP-F-41（宏观分析页）：金银比/金油比/铜金比/金铜比四个跨资产
比价的衍生计算管线——读多源价格（注入位，禁真连外网）→ 日期交集对齐 →
比率序列 → 滚动窗口 z-score → 宏观含义标注。

宏观含义规则表（文档化初版，金融常识口径，待宏观组标定）：
    金银比↑极端：避险情绪浓厚（白银工业属性拖累，经济下行担忧）；
    金油比↑极端：原油需求担忧/通缩压力（金强油弱）；
    铜金比↑极端：全球增长预期改善（铜强金弱，风险偏好升）；
    金铜比↑极端：避险占优（金强铜弱，增长预期走弱）——金铜比为铜金比倒数镜像。

不做什么：不采集价格（prices 由上游注入）/不做交易信号/不预测汇率利率。

依据: 缺口总账 GAP-F-41
SSoT: depgraph node 10505570（MOD-SIG-075，待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: prices {asset: [(date, close)]} 注入 + CrossAssetRatioConfig
# 特征: 四比价日频序列（日期交集对齐）
# 算法: 比率 → 滚动窗口 z-score → 五档分档 → 规则表宏观标注
# 输出: CrossAssetRatioResult（四比价快照：latest/zscore/band/annotation）
"""

from __future__ import annotations

import datetime as _dt
import logging
import re as _re
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Mapping, Sequence

import numpy as np

logger = logging.getLogger(__name__)

__all__: Final = [
    "RATIO_DEFS",
    "CrossAssetRatioConfig",
    "CrossAssetRatioResult",
    "RatioSnapshot",
    "compute_cross_asset_ratios",
]

_DATE_RE: Final = _re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass(frozen=True, slots=True)
class RatioDef:
    """比价定义（分子/分母资产 + 宏观含义规则表文案）。"""

    key: str
    name_zh: str
    numerator: str
    denominator: str
    high_meaning: str  # z 极端高（≥+2）宏观含义
    low_meaning: str  # z 极端低（≤-2）宏观含义


#: 四比价封闭集合（定义序=展示序）
RATIO_DEFS: Final[dict[str, RatioDef]] = {
    "gold_silver": RatioDef(
        key="gold_silver",
        name_zh="金银比",
        numerator="gold",
        denominator="silver",
        high_meaning="避险情绪浓厚：白银工业属性拖累相对黄金走弱（经济下行担忧）",
        low_meaning="白银相对强势：工业需求/风险偏好回暖",
    ),
    "gold_oil": RatioDef(
        key="gold_oil",
        name_zh="金油比",
        numerator="gold",
        denominator="oil",
        high_meaning="金强油弱：原油需求担忧/通缩压力升温",
        low_meaning="油价相对强势：通胀/地缘溢价占优",
    ),
    "copper_gold": RatioDef(
        key="copper_gold",
        name_zh="铜金比",
        numerator="copper",
        denominator="gold",
        high_meaning="铜强金弱：全球增长预期改善，风险偏好上升",
        low_meaning="金强铜弱：避险占优，增长预期走弱",
    ),
    "gold_copper": RatioDef(
        key="gold_copper",
        name_zh="金铜比",
        numerator="gold",
        denominator="copper",
        high_meaning="避险占优：金强铜弱（增长预期走弱，铜金比倒数镜像）",
        low_meaning="铜强金弱：增长预期改善（铜金比倒数镜像）",
    ),
}

#: 必需资产全集（四比价并集）
_REQUIRED_ASSETS: Final = frozenset(a for d in RATIO_DEFS.values() for a in (d.numerator, d.denominator))

_BANDS: Final = ((2.0, "极高"), (1.0, "偏高"))  # |z| 阈值（对称，负侧 极低/偏低）


@dataclass(frozen=True, slots=True)
class CrossAssetRatioConfig:
    """比价计算配置。"""

    zscore_window: int = 250  # z-score 滚动窗口（约一年交易日）
    min_points: int = 30  # 日期交集最小根数

    def __post_init__(self) -> None:
        if int(self.zscore_window) < 10:
            raise ValueError(f"zscore_window 非法（须 ≥10）: {self.zscore_window!r}")
        if int(self.min_points) < 10:
            raise ValueError(f"min_points 非法（须 ≥10）: {self.min_points!r}")


@dataclass(frozen=True, slots=True)
class RatioSnapshot:
    """单比价快照（最新值+z+分档+宏观标注）。"""

    key: str
    name_zh: str
    latest: float
    zscore: float
    band: str  # 极高/偏高/中性/偏低/极低
    annotation: str
    as_of: str  # 最新共同日期
    n_points: int  # 交集对齐根数


@dataclass(frozen=True, slots=True)
class CrossAssetRatioResult:
    """四比价总产出（JSON 可序列化）。"""

    ratios: tuple[RatioSnapshot, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _band_of(z: float) -> str:
    az = abs(z)
    if az >= 2.0:
        return "极高" if z > 0 else "极低"
    if az >= 1.0:
        return "偏高" if z > 0 else "偏低"
    return "中性"


def _annotation(defn: RatioDef, z: float, band: str) -> str:
    if band == "极高":
        return defn.high_meaning
    if band == "极低":
        return defn.low_meaning
    if band in ("偏高", "偏低"):
        side = defn.high_meaning if z > 0 else defn.low_meaning
        return f"轻度偏离：{side}"
    return "中性区间：比价处于历史常态范围"


def _to_series(asset: str, rows: Sequence[tuple[str, float]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for date_s, price in rows:
        if not isinstance(date_s, str) or not _DATE_RE.fullmatch(date_s):
            raise ValueError(f"{asset} 日期非法（须 YYYY-MM-DD）: {date_s!r}")
        try:
            _dt.date.fromisoformat(date_s)
        except ValueError as exc:
            raise ValueError(f"{asset} 非真实日期: {date_s!r}") from exc
        p = float(price)
        if not np.isfinite(p) or p <= 0:
            raise ValueError(f"{asset} 价格非法（须为正且有限）: {price!r}")
        out[date_s] = p
    return out


def compute_cross_asset_ratios(
    prices: Mapping[str, Sequence[tuple[str, float]]],
    *,
    config: CrossAssetRatioConfig | None = None,
) -> CrossAssetRatioResult:
    """跨资产比价计算主入口（四比价→z-score→宏观标注）。

    Args:
        prices: {asset: [(date, close)]} 多源价格注入（上游装载，禁真连外网）。
            必需资产：gold/silver/oil/copper。
        config: 计算配置（None=默认窗口 250/最小交集 30）。

    Returns:
        CrossAssetRatioResult（按 RATIO_DEFS 定义序四快照）。

    Raises:
        ValueError: 资产缺失/价格非法/交集不足/参数非法（fail-closed）。
    """
    cfg = config or CrossAssetRatioConfig()
    missing = sorted(_REQUIRED_ASSETS - set(str(k) for k in prices.keys()))
    if missing:
        raise ValueError(f"必需资产缺失: {missing}")
    series = {asset: _to_series(asset, prices[asset]) for asset in _REQUIRED_ASSETS}

    snapshots: list[RatioSnapshot] = []
    for defn in RATIO_DEFS.values():
        num = series[defn.numerator]
        den = series[defn.denominator]
        common = sorted(set(num) & set(den))
        if len(common) < cfg.min_points:
            raise ValueError(
                f"{defn.name_zh} 日期交集不足（须 ≥{cfg.min_points}）: {defn.numerator}×{defn.denominator} 仅 {len(common)}"
            )
        ratio = np.array([num[d] / den[d] for d in common], dtype=float)
        window = ratio[-cfg.zscore_window :]
        std = float(np.std(window, ddof=1)) if len(window) > 1 else 0.0
        latest = float(ratio[-1])
        if std == 0.0:
            z = 0.0
            note = "窗口零波动（比率恒定），z 置 0 降级"
        else:
            z = float((latest - float(np.mean(window))) / std)
            note = ""
        band = _band_of(z)
        snapshots.append(
            RatioSnapshot(
                key=defn.key,
                name_zh=defn.name_zh,
                latest=round(latest, 6),
                zscore=round(z, 4),
                band=band,
                annotation=_annotation(defn, z, band) if not note else f"{note}；{_annotation(defn, z, band)}",
                as_of=common[-1],
                n_points=len(common),
            )
        )

    return CrossAssetRatioResult(ratios=tuple(snapshots))
