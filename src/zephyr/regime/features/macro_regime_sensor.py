# [BLUEPRINT] MOD-REGIME-MAC | docs/_working/night_sweep/b_audit/nb1_b5_cn_macro_family.md 复活接入处方 R2-R3
# [MODULE] zephyr.regime.features.macro_regime_sensor
# [DOMAIN] D_REGIME
# [DEPENDENCIES] pandas; numpy; zephyr.data.ch_reader; zephyr.data.table_registry;
#                zephyr.data.macro_vintage (PIT_LATEST_SQL/TABLE_VINTAGE); zephyr.shared.utils.time_utils.now_utc
# [CONSUMERS] TDM-E-L1-S0 宏观环境传感器（config/trading_decision_map.yaml module_ref，本车道改指）;
#             L01_regime 月级谨慎度修正因子（macro_weather_score/caution_factor）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] ①序列码唯一经 config/macro_indicator_series_map.yaml 翻译层（禁散落硬编码，NB1-B5 R1）；
#              ②PIT 铁律：as_of 非空必走 vintage 通道（pub_ts<=as_of，回补终值天然缺席），
#                现值表读数仅限 as_of=None 的盘前 live 判定面；
#              ③缺员降权：缺数据序列只缩减该组贡献权重并留痕，绝不以 0 值/前值填充冒充；
#              ④打分纯函数可测：滚动分位→组内均值→加权合成，零随机零时钟依赖；
#              ⑤本模块只读，禁写任何表（消费面职责单一）。
# [MODIFY-GUARD] blueprint=docs/_working/night_sweep/b_audit/nb1_b5_cn_macro_family.md（R2-R3 处方）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 映射表缺失/空→ValueError fail-closed；CH 查询失败→ClickHouseQueryError 透传
#                  （严格读通道，禁吞成空表；调用方自行降级）；未知 direction/transform→ValueError。
# [TESTS] tests/regime/features/test_macro_regime_sensor.py（mock 数据路径，零 CH 依赖）
# [A_module] module_id=MOD-REGIME-MAC | layer=module | stability=new | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] TDM-E-L1-S0 宏观环境传感器；NB1-B5 复活接入处方 R1-R5
"""macro_regime_sensor — 宏观环境传感器（TDM-E-L1-S0 真消费模块，NB1-B5 复活件）。

背景（NB1-B5 三审结论）：MAC 宏观指标族 16 条全 candidate、TDM 挂 8 条 macro_refs，
但 src 侧零代码消费——声明面与代码消费面断裂。本模块按 Owner 批复
"CN-MAC 整族不退役，按 R1-R5 处方复活接入"补上消费线：

    R1 config/macro_indicator_series_map.yaml  指标 ID ↔ 序列码唯一翻译层
    R2 read_macro_indicators()                 PIT 读视图（indicator_id, obs_date, pub_ts, value）
    R3 MacroRegimeSensor                       四组信号→宏观天气分 0-100→月级谨慎度修正因子
    R4 FRED 美系                                既有 macro_fred 腿已全覆盖（本模块只读复用）
    R5 册务                                     entry_count 15→16+转正（注册表侧随本件落地）

方法（NB1 复活处方三步法）：滚动分位（默认 36 个月窗）→ 方向修正 → 组内均值（缺员降权）
→ 组间加权合成（A 货币 0.30 / B 流动性信用 0.30 / C 海外 0.20 / D 增长物价 0.20）
→ 天气分 0-100；月线定 regime（月末采样 caution_factor 供 L01），周线同 read 视图
周五采样做确认信号（不另建管线）。

 caution=2021 年后信用周期对大盘领先性钝化（NB1 三审引证）——本模块输出仅为
 L01 谨慎度修正因子，不直接驱动仓位。

用法::

    from zephyr.regime.features.macro_regime_sensor import MacroRegimeSensor
    reading = MacroRegimeSensor().score()                    # live（现值表）
    hist = MacroRegimeSensor().monthly_series(as_of="2026-09-30 00:00:00")  # PIT 月度因子序列


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 序列映射表
#   fields: config/macro_indicator_series_map.yaml（指标 ID ↔ CH 序列码唯一翻译层，R1）
#   code: load_series_map(path) L117
# - id: I2
#   name: PIT 宏观读视图
#   fields: indicator_ids, as_of（indicator_id, obs_date, pub_ts, value 四列）
#   code: read_macro_indicators() L213（R2，missing 条目跳过）
# 层: 算法
# - id: A1
#   name_zh: ① 序列准备
#   name_en: prepare_series
#   intro: 逐指标取序列、月度重采样对齐；36 个月滚动窗（ROLLING_WINDOW_MONTHS，min_periods=12）。
#   desc: MacroRegimeSensor._prepare_series。
# - id: A2
#   name_zh: ② 滚动分位
#   name_en: member_percentiles
#   intro: 逐成员滚动分位 ∈ [0,1]（_rolling_percentile L280）。
#   desc: 缺员降权（组内均值只计在岗成员）。
# - id: A3
#   name_zh: ③ 方向修正
#   name_en: direction_adjust
#   intro: positive/inverse/neutral 三向修正（_direction_adjust L304）——inverse 指标取 1-pct。
#   desc: _TRANSFORMS level/yoy/diff 先行（transform_series L257）。
# - id: A4
#   name_zh: ④ 组内均值+组间加权合成
#   name_en: group_weighted_score
#   intro: A 货币 0.30/B 流动性信用 0.30/C 海外 0.20/D 增长物价 0.20 加权→天气分 0-100。
#   desc: _load_groups_weights L321；score() L431（R3）。
# - id: A5
#   name_zh: ⑤ 谨慎度映射
#   name_en: weather_to_caution
#   intro: 天气分→月级 caution_factor（weather_to_caution L313），月末采样供 L01；周线周五采样做确认。
#   desc: monthly_series L518 / weekly_series L524；仅谨慎度修正因子，不直接驱动仓位。
# 层: 输出
# - id: O1
#   name: 宏观天气读数
#   fields: score() dict（weather 0-100/caution_factor/各组明细）；monthly/weekly DataFrame
#   code: score/monthly_series/weekly_series
# [/ALGO_FLOW]
#
# 边:
# I1 --> I2
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
# A4 --> O1
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Final

import numpy as np
import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.shared.utils.time_utils import now_utc

#: 映射表真源路径（R1 翻译层；模块安装根相对）
SERIES_MAP_RELPATH: Final = Path("config/macro_indicator_series_map.yaml")

#: PIT 语义：as_of 回测取数走 vintage 通道（pub_ts<=as_of），现值读数仅限盘前 live 判定面。
# NO-BARE-SQL：SQL 集中于此（§5.160.2）。普通赋值（非 : Final）——NO-BARE-SQL 豁免仅识别
# ast.Assign 的 _?SQL_ 常量（macro_vintage 同款约定）；表名为运行期入参故只集中静态片段。
_SQL_LIVE_PREFIX = "SELECT indicator_name, report_date, indicator_value FROM "
_SQL_LIVE_SUFFIX = " FINAL WHERE indicator_name IN ("

#: 合法枚举（映射表字段校验；未知值 fail-closed）
_TRANSFORMS: Final = {"level", "yoy", "diff"}
_DIRECTIONS: Final = {"positive", "inverse", "neutral"}

#: 四组信号（代码侧缺省兜底；运行时组声明真源=映射表 groups/weights 段，
#: 本常量仅在映射表未声明时生效——改组以映射表为准）
GROUPS: Final[dict[str, tuple[str, ...]]] = {
    "A_monetary": ("MAC-CN-007", "MAC-CN-008", "MAC-CN-009", "MAC-US-001"),
    "B_liquidity_credit": ("MAC-CN-005", "MAC-CN-006"),
    "C_overseas": ("MAC-CN-011", "MAC-US-002", "MAC-US-004"),
    "D_growth_policy": ("MAC-CN-001", "MAC-CN-002", "MAC-CN-003", "MAC-CN-004"),
}

#: 组间权重（映射表 weights 同构镜像）
GROUP_WEIGHTS: Final[dict[str, float]] = {
    "A_monetary": 0.30,
    "B_liquidity_credit": 0.30,
    "C_overseas": 0.20,
    "D_growth_policy": 0.20,
}

#: 滚动分位窗（月，NB1 三步法；2021 后信用钝化→窗内自适应而非全史固定）
ROLLING_WINDOW_MONTHS: Final = 36
#: 滚动分位最小样本（不足则 expanding 兜底，再不足→该序列缺员）
_MIN_PERIODS: Final = 12

#: 月级谨慎度修正因子映射（天气分→L01 因子；确定性阶梯，禁平滑拟合）
CAUTION_TIERS: Final[tuple[tuple[float, float, str], ...]] = (
    (70.0, 1.00, "supportive"),  # 宏观支撑 → 全额风险预算
    (40.0, 0.90, "neutral"),  # 中性 → 略谨慎
    (float("-inf"), 0.75, "cautious"),  # 压制 → 谨慎
)


# ---------------------------------------------------------------- R1 翻译层


def _install_root() -> Path:
    """模块安装根解析（本文件位置 src/zephyr/regime/features 上溯 4 级；worktree 施工区内=施工区根）。"""
    return Path(__file__).resolve().parents[4]


def load_series_map(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """加载 MAC-* → 序列码映射表（R1 翻译层唯一入口）。

    Returns:
        {indicator_id: mapping entry}（含 primary 与 aux_series 展平标记）。
        status=missing 的条目原样返回（消费侧按缺员处理，不删除）。

    Raises:
        ValueError: 文件缺失/空/无 mappings 段/字段非法（fail-closed）。
    """
    import yaml

    p = Path(path) if path else _install_root() / SERIES_MAP_RELPATH
    if not p.exists():
        msg = f"宏观序列映射表缺失: {p}"
        raise ValueError(msg)
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    mappings = doc.get("mappings")
    if not mappings:
        msg = f"映射表无 mappings 段: {p}"
        raise ValueError(msg)
    out: dict[str, dict[str, Any]] = {}
    for m in mappings:
        iid = m.get("indicator_id")
        if not iid:
            msg = f"映射条目缺 indicator_id: {m!r}"
            raise ValueError(msg)
        tr = m.get("transform", "level")
        dr = m.get("direction", "neutral")
        if tr not in _TRANSFORMS:
            msg = f"{iid} 未知 transform={tr!r}"
            raise ValueError(msg)
        if dr not in _DIRECTIONS:
            msg = f"{iid} 未知 direction={dr!r}"
            raise ValueError(msg)
        out[str(iid)] = m
    return out


# ---------------------------------------------------------------- R2 PIT 读视图


def _series_codes(indicator_ids: list[str], smap: dict[str, dict[str, Any]]) -> dict[str, str]:
    """展开指标 ID → 需要拉取的序列码集合（含 aux；missing 条目跳过并留痕）。"""
    codes: dict[str, str] = {}
    for iid in indicator_ids:
        entry = smap.get(iid)
        if entry is None:
            continue
        if entry.get("status") == "missing" or not entry.get("series_code"):
            continue
        codes[str(entry["series_code"])] = iid
        for aux in entry.get("aux_series") or []:
            code = aux.get("series_code")
            if aux.get("status") != "missing" and code:
                codes[str(code)] = iid
    return codes


def _fetch_series_codes(codes: list[str], *, as_of: str | None) -> pd.DataFrame:
    """按序列码清单拉数：as_of=None 走现值表；as_of 给定走 vintage PIT 通道。

    Returns:
        DataFrame[code, obs_date, value]（obs_date=date，value=float）。
    """
    if not codes:
        return pd.DataFrame(columns=["code", "obs_date", "value"])
    quoted = ", ".join("'" + c.replace("'", "''") + "'" for c in codes)
    if as_of is None:
        # NO-BARE-SQL：SQL 集中于模块级 _SQL_ 常量（§5.160.2，macro_vintage 同款前缀/后缀
        # 拼装式）；表名运行期入参（TableRegistry 真源），故只集中静态片段。
        table = get_registry().table("market_macro_data")
        sql = _SQL_LIVE_PREFIX + table + _SQL_LIVE_SUFFIX + quoted + ")"
        rows = ch_reader.query_rows(sql)
    else:
        # PIT 铁律：只取 pub_ts <= as_of 的已发布观测（vintage 表，回补终值天然缺席）。
        # PIT_LATEST_SQL=macro_vintage 模块级常量（既有豁免登记），本处只做参数化填充。
        from zephyr.data.macro_vintage import PIT_LATEST_SQL

        sql = PIT_LATEST_SQL.format(as_of=as_of, names_clause=f" AND indicator_name IN ({quoted})")
        rows = ch_reader.query_rows(sql)
    if not rows:
        return pd.DataFrame(columns=["code", "obs_date", "value"])
    if as_of is None:
        df = pd.DataFrame(rows, columns=["code", "obs_date", "value"])
    else:
        # PIT 模板列序: indicator_name, report_date, indicator_value, pub_ts, vintage, pub_ts_basis
        df = pd.DataFrame(rows, columns=["code", "obs_date", "value", "pub_ts", "vintage", "basis"])
        df["pub_ts"] = pd.to_datetime(df["pub_ts"], utc=True, errors="coerce")
    df["obs_date"] = pd.to_datetime(df["obs_date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna(subset=["obs_date", "value"])[
        ["code", "obs_date", "value", *(["pub_ts"] if as_of is not None else [])]
    ]


def read_macro_indicators(
    indicator_ids: list[str] | tuple[str, ...] | None = None,
    *,
    as_of: str | None = None,
    map_path: str | Path | None = None,
) -> pd.DataFrame:
    """R2 读视图：MAC 指标 → (indicator_id, series_role, code, obs_date, value[, pub_ts])。

    Args:
        indicator_ids: 指标 ID 清单；None=映射表全部 wired 条目。
        as_of: PIT 时点（ISO 字符串）；None=现值表 live 读数（盘前判定面）。
        map_path: 映射表路径覆盖（测试注入 tmp_path 用）。

    Returns:
        DataFrame，列=[indicator_id, series_role, code, obs_date, value]，
        PIT 模式追加 pub_ts 列。缺数据指标自然缺席（调用方按缺员降权）。
    """
    smap = load_series_map(map_path)
    if indicator_ids is None:
        indicator_ids = [iid for iid, e in smap.items() if e.get("status") != "missing"]
    indicator_ids = list(indicator_ids)
    codes_map = _series_codes(indicator_ids, smap)
    raw = _fetch_series_codes(sorted(codes_map), as_of=as_of)
    if raw.empty:
        return pd.DataFrame(columns=["indicator_id", "series_role", "code", "obs_date", "value"])
    # aux 序列标 aux 角色
    aux_codes: set[str] = set()
    for iid in indicator_ids:
        for aux in smap.get(iid, {}).get("aux_series") or []:
            if aux.get("series_code"):
                aux_codes.add(str(aux["series_code"]))
    raw = raw.copy()
    raw["indicator_id"] = raw["code"].map(codes_map)
    raw = raw.dropna(subset=["indicator_id"])  # 拉数层返回的多余序列不进读视图
    raw["series_role"] = np.where(raw["code"].isin(aux_codes), "aux", "primary")
    cols = ["indicator_id", "series_role", "code", "obs_date", "value"]
    if as_of is not None:
        cols.append("pub_ts")
    return raw[cols].sort_values(["indicator_id", "code", "obs_date"]).reset_index(drop=True)


# ---------------------------------------------------------------- 变换与打分


def transform_series(df: pd.DataFrame, *, transform: str) -> pd.DataFrame:
    """按映射 transform 变换单序列（输入须已按 obs_date 升序的单 code 帧）。

    level=原值；yoy=滚动12期和的同比（流量类，如社融增量亿元）；
    diff=一阶差分（水平类利率的方向语义）。
    """
    out = df.copy()
    if transform == "level" or out.empty:
        return out
    if transform == "diff":
        out["value"] = out["value"].diff()
        return out.dropna(subset=["value"])
    if transform == "yoy":
        s = out.set_index("obs_date")["value"].astype(float)
        roll_sum = s.rolling("365D").sum()  # 滚动12个月和（流量）
        prev = roll_sum.shift(freq="365D")  # 一年前同窗和
        yoy = (roll_sum / prev - 1.0) * 100.0
        out = out.assign(value=yoy.reindex(out["obs_date"]).values)
        return out.dropna(subset=["value"])
    msg = f"未知 transform={transform!r}"
    raise ValueError(msg)


def _rolling_percentile(
    values: pd.Series, window: int = ROLLING_WINDOW_MONTHS, min_periods: int = _MIN_PERIODS
) -> pd.Series:
    """滚动分位（NB1 三步法第一步）：当前值在窗内的历史分位 0-1。

    月频语义按"观测序"近似月窗（window 个观测）；样本 < min_periods 时 expanding
    兜底；仍不足 → NaN（缺员，不硬凑）。
    """
    if values.empty:
        return values.copy()

    def _pct(arr: np.ndarray) -> float:
        cur = arr[-1]
        base = arr[:-1]
        if len(base) < min_periods - 1:
            return float("nan")
        return float((base <= cur).mean())

    roll = values.rolling(window=window, min_periods=min_periods).apply(_pct, raw=True)
    # expanding 兜底：早期样本不足 rolling 的位置用 expanding（≥min_periods 才有效）
    exp = values.expanding(min_periods=min_periods).apply(_pct, raw=True)
    return roll.fillna(exp)


def _direction_adjust(pct: float, direction: str) -> float:
    """方向修正：positive 原值；inverse 取 1-p；neutral 不参与（返回 NaN）。"""
    if direction == "positive":
        return pct
    if direction == "inverse":
        return 1.0 - pct
    return float("nan")


def weather_to_caution(score: float) -> tuple[float, str]:
    """天气分 → (caution_factor, tier)（确定性阶梯 CAUTION_TIERS）。"""
    for threshold, factor, tier in CAUTION_TIERS:
        if score >= threshold:
            return factor, tier
    return CAUTION_TIERS[-1][1], CAUTION_TIERS[-1][2]


def _load_groups_weights(
    map_path: str | Path | None,
) -> tuple[dict[str, tuple[str, ...]], dict[str, float]]:
    """从映射表读 groups/weights 声明面；未声明段回退代码缺省（GROUPS/GROUP_WEIGHTS）。"""
    import yaml

    p = Path(map_path) if map_path else _install_root() / SERIES_MAP_RELPATH
    if not p.exists():
        return dict(GROUPS), dict(GROUP_WEIGHTS)
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    groups_raw = doc.get("groups") or {}
    weights_raw = doc.get("weights") or {}
    groups = {str(g): tuple(ids) for g, ids in groups_raw.items()} if groups_raw else dict(GROUPS)
    weights = {str(k): float(v) for k, v in weights_raw.items()} if weights_raw else dict(GROUP_WEIGHTS)
    return groups, weights


class MacroRegimeSensor:
    """宏观环境传感器：四组信号 → 宏观天气分 0-100 → 月级谨慎度修正因子。

    输入=R2 读视图（映射表驱动）；输出=score()/monthly_series()/weekly_series()。
    缺员降权：某组内可用序列（有分位值者）均值×组权重×(可用数/声明数)；
    天气分=各有效组加权（权重按有效组重归一）。
    """

    def __init__(
        self,
        map_path: str | Path | None = None,
        *,
        window: int = ROLLING_WINDOW_MONTHS,
        groups: dict[str, tuple[str, ...]] | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.map_path = map_path
        self.window = window
        default_groups, default_weights = _load_groups_weights(map_path)
        self.groups = dict(groups or default_groups)
        self.weights = dict(weights or default_weights)

    # -- 内部：指标 → 变换后序列帧 {iid: DataFrame[obs_date, value, role]} --
    def _prepare_series(self, reads: pd.DataFrame) -> dict[str, pd.DataFrame]:
        smap = load_series_map(self.map_path)
        prepared: dict[str, pd.DataFrame] = {}
        for iid, grp in reads.groupby("indicator_id"):
            entry = smap.get(str(iid))
            if entry is None or entry.get("status") == "missing":
                continue
            tr = entry.get("transform", "level")
            frames = []
            for role, sub in grp.groupby("series_role"):
                sub = sub.sort_values("obs_date")
                sub = transform_series(sub[["obs_date", "value"]], transform=tr)
                if sub.empty:
                    continue
                sub = sub.assign(series_role=role)
                frames.append(sub)
            if frames:
                prepared[str(iid)] = pd.concat(frames, ignore_index=True)
        return prepared

    def _member_percentiles(self, prepared: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """逐序列滚动分位+方向修正（aux 剪刀差在此派生）。"""
        smap = load_series_map(self.map_path)
        scored: dict[str, pd.DataFrame] = {}
        for iid, frame in prepared.items():
            entry = smap[iid]
            parts: list[pd.DataFrame] = []
            primaries = frame[frame["series_role"] == "primary"]
            primary_direction = str(entry.get("direction", "neutral"))
            if not primaries.empty:
                pct = _rolling_percentile(primaries["value"].reset_index(drop=True), window=self.window)
                adj = pct.map(lambda p, d=primary_direction: _direction_adjust(p, d))
                parts.append(
                    pd.DataFrame(
                        {
                            "obs_date": primaries["obs_date"].reset_index(drop=True),
                            "signal": adj,
                        }
                    )
                )
            for aux in entry.get("aux_series") or []:
                aux_frame = frame[frame["series_role"] == "aux"]
                if aux_frame.empty:
                    continue
                if aux.get("derive") == "derive_scissors":
                    # 剪刀差=aux − primary（如 M1同比 − M2同比），再滚动分位
                    if primaries.empty:
                        continue
                    merged = pd.merge(
                        aux_frame[["obs_date", "value"]].rename(columns={"value": "aux_v"}),
                        primaries[["obs_date", "value"]].rename(columns={"value": "pri_v"}),
                        on="obs_date",
                    )
                    if merged.empty:
                        continue
                    sc = merged.assign(value=merged["aux_v"] - merged["pri_v"])[["obs_date", "value"]]
                    pct = _rolling_percentile(sc["value"].reset_index(drop=True), window=self.window)
                    aux_dir = str(aux.get("direction", "positive"))
                    parts.append(
                        pd.DataFrame(
                            {
                                "obs_date": sc["obs_date"].reset_index(drop=True),
                                "signal": pct.map(lambda p, d=aux_dir: _direction_adjust(p, d)),
                            }
                        )
                    )
            if parts:
                scored[iid] = pd.concat(parts, ignore_index=True).dropna(subset=["signal"])
        return scored

    def score(self, *, as_of: str | None = None) -> dict[str, Any]:
        """宏观天气打分。

        Args:
            as_of: PIT 时点；None=live（现值表）。

        Returns:
            dict(weather_score, caution_factor, tier, groups={组: {score, members, missing}},
                 missing_indicators, as_of, generated_at)
        """
        smap = load_series_map(self.map_path)
        wanted = [iid for g in self.groups.values() for iid in g]
        reads = read_macro_indicators(wanted, as_of=as_of, map_path=self.map_path)
        prepared = self._prepare_series(reads)
        scored = self._member_percentiles(prepared)

        declared_total = sum(len(g) for g in self.groups.values())
        missing: list[str] = []
        group_out: dict[str, dict[str, Any]] = {}
        weighted_num = 0.0
        weighted_den = 0.0
        for gname, members in self.groups.items():
            signals: list[pd.DataFrame] = []
            member_missing: list[str] = []
            context_members: list[str] = []
            scoring_members = [iid for iid in members if smap.get(iid, {}).get("direction", "neutral") != "neutral"]
            for iid in members:
                if iid not in scoring_members:
                    context_members.append(iid)  # neutral=背景变量，不参与方向打分（映射表语义）
                    continue
                frame = scored.get(iid)
                if frame is None or frame.empty:
                    if smap.get(iid, {}).get("status") != "missing":
                        missing.append(iid)
                    member_missing.append(iid)
                    continue
                signals.append(frame)
            if signals:
                # 组分=成员各自最新可得信号的均值（发布节奏不齐时对齐各员最新点，
                # PIT 语义由 read 层保证；禁用未来观测）
                latest = [float(f["signal"].iloc[-1]) for f in signals]
                group_score = float(np.mean(latest))
            else:
                group_score = float("nan")
            coverage = (len(scoring_members) - len(member_missing)) / len(scoring_members) if scoring_members else 0.0
            group_out[gname] = {
                "score": group_score,
                "coverage": coverage,
                "members": list(members),
                "scoring_members": scoring_members,
                "context_members": context_members,
                "missing": member_missing,
            }
            if not np.isnan(group_score):
                w = self.weights.get(gname, 0.0) * coverage  # 缺员降权
                weighted_num += group_score * w
                weighted_den += w

        weather = weighted_num / weighted_den * 100.0 if weighted_den > 0 else float("nan")
        caution, tier = (float("nan"), "no_data") if np.isnan(weather) else weather_to_caution(weather)
        return {
            "weather_score": round(float(weather), 1) if not np.isnan(weather) else None,
            "caution_factor": caution,
            "tier": tier,
            "groups": group_out,
            "missing_indicators": sorted(set(missing)),
            "declared_indicators": declared_total,
            "as_of": as_of,
            "generated_at": now_utc().isoformat(),
        }

    # -- 聚合查询面：月线定 regime / 周线做确认 --
    @staticmethod
    def _sample(reads: pd.DataFrame, freq: str) -> pd.DataFrame:
        """观测采样：freq='ME' 取每月最后观测，'W-FRI' 取每周五（含向前回看最近观测）。"""
        if reads.empty:
            return reads
        out = reads.copy()
        out = out.set_index("obs_date").sort_index()
        if freq == "ME":
            return out.groupby([out.index.to_period("M"), "indicator_id", "series_role", "code"]).tail(1).reset_index()
        if freq == "W-FRI":
            period = out.index.to_period("W-FRI")
            return out.groupby([period, "indicator_id", "series_role", "code"]).tail(1).reset_index()
        msg = f"未知采样频率 freq={freq!r}（支持 'ME'/'W-FRI'）"
        raise ValueError(msg)

    def monthly_series(self, *, as_of: str | None = None) -> pd.DataFrame:
        """月度采样因子序列（L01 月级谨慎度修正的入参面；月末最后观测）。"""
        wanted = [iid for g in self.groups.values() for iid in g]
        reads = read_macro_indicators(wanted, as_of=as_of, map_path=self.map_path)
        return self._sample(reads, "ME")

    def weekly_series(self, *, as_of: str | None = None) -> pd.DataFrame:
        """周度采样确认信号（同一 read 视图，不另建管线；周五年内最近观测）。"""
        wanted = [iid for g in self.groups.values() for iid in g]
        reads = read_macro_indicators(wanted, as_of=as_of, map_path=self.map_path)
        return self._sample(reads, "W-FRI")

    def monthly_weather_history(self, *, as_of: str | None = None) -> pd.DataFrame:
        """逐月天气分历史（回测 as_of 语义用；每月末截面重打分的轻量近似=按月对齐信号均值）。"""
        wanted = [iid for g in self.groups.values() for iid in g]
        reads = read_macro_indicators(wanted, as_of=as_of, map_path=self.map_path)
        prepared = self._prepare_series(reads)
        scored = self._member_percentiles(prepared)
        if not scored:
            return pd.DataFrame(columns=["month", "weather_score", "caution_factor", "tier"])
        frames = []
        for gname, members in self.groups.items():
            for iid in members:
                frame = scored.get(iid)
                if frame is not None and not frame.empty:
                    f = frame.assign(group=gname, iid=iid)
                    frames.append(f)
        if not frames:
            return pd.DataFrame(columns=["month", "weather_score", "caution_factor", "tier"])
        allsig = pd.concat(frames, ignore_index=True)
        allsig["month"] = allsig["obs_date"].dt.to_period("M")
        monthly = allsig.groupby(["month", "iid"])["signal"].mean().unstack("iid")
        weather = []
        for month, row in monthly.iterrows():
            num = den = 0.0
            for gname, members in self.groups.items():
                vals = [row[iid] for iid in members if iid in row.index and not pd.isna(row[iid])]
                if vals:
                    w = self.weights.get(gname, 0.0) * len(vals) / len(members)
                    num += float(np.mean(vals)) * w
                    den += w
            weather.append((month, num / den * 100.0 if den > 0 else np.nan))
        out = pd.DataFrame(weather, columns=["month", "weather_score"]).dropna()
        if out.empty:
            return pd.DataFrame(columns=["month", "weather_score", "caution_factor", "tier"])
        out["caution_factor"] = out["weather_score"].map(lambda s: weather_to_caution(s)[0])
        out["tier"] = out["weather_score"].map(lambda s: weather_to_caution(s)[1])
        return out.reset_index(drop=True)
