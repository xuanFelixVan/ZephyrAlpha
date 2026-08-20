# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_quality
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ARCH-031: migrated from governance/governance/data_quality.py to root (canonical per [MODULE] annotation)
from enum import Enum
from typing import Callable, Final

import numpy as np
import pandas as pd
from pydantic import BaseModel


class DQDimension(str, Enum):
    # B4 SLA 四维度：COMPLETENESS / CONSISTENCY / FRESHNESS / ANOMALY
    # 扩展维度：ACCURACY / TIMELINESS / UNIQUENESS / VALIDITY
    COMPLETENESS = "Completeness"
    ACCURACY = "Accuracy"
    ANOMALY = "Anomaly"  # B4: 异常检测（时序突变/离群）
    CONSISTENCY = "Consistency"
    FRESHNESS = "Freshness"  # B4: 新鲜度（数据年龄，区别于 TIMELINESS 处理延迟）
    TIMELINESS = "Timeliness"
    UNIQUENESS = "Uniqueness"
    VALIDITY = "Validity"


class DQSpec(BaseModel):
    dimension: DQDimension
    label: str
    metric: str
    threshold: float = 0.95
    check_func: str = ""
    # 方向标记：True 表示 value 越小越健康（如 age_seconds、outlier_rate），
    # 此时 threshold 为"上限"。score_dq 据此决定 value/threshold 的方向，
    # 避免"年龄越大分越高"类荒谬结果。默认 False（value 越大越健康，threshold 为下限）。
    lower_is_better: bool = False


DQ_SPECS: Final[dict[DQDimension, DQSpec]] = {
    DQDimension.COMPLETENESS: DQSpec(
        dimension=DQDimension.COMPLETENESS,
        label="完整性",
        metric="missing_pct",
        threshold=0.99,
        check_func="check_completeness",
    ),
    DQDimension.ACCURACY: DQSpec(
        dimension=DQDimension.ACCURACY,
        label="准确性",
        metric="deviation_sigma",
        threshold=0.95,
        check_func="check_accuracy",
    ),
    DQDimension.ANOMALY: DQSpec(
        dimension=DQDimension.ANOMALY,
        label="异常检测",
        metric="zscore_outlier_rate",  # 离群率，越小越好
        threshold=0.01,  # 离群率上限 1%（lower_is_better=True 下 threshold 为上限）
        check_func="check_anomaly",
        lower_is_better=True,
    ),
    DQDimension.CONSISTENCY: DQSpec(
        dimension=DQDimension.CONSISTENCY,
        label="一致性",
        metric="recon_diff",
        threshold=0.99,
        check_func="check_consistency",
    ),
    DQDimension.FRESHNESS: DQSpec(
        dimension=DQDimension.FRESHNESS,
        label="新鲜度",
        metric="age_seconds",  # 数据年龄 now-last_updated，越小越好
        threshold=60.0,  # 数据年龄上限 60s（lower_is_better=True 下 threshold 为上限）
        check_func="check_freshness",
        lower_is_better=True,
    ),
    DQDimension.TIMELINESS: DQSpec(
        dimension=DQDimension.TIMELINESS,
        label="时效性",
        metric="latency_ms",
        threshold=0.95,
        check_func="check_timeliness",
    ),
    DQDimension.UNIQUENESS: DQSpec(
        dimension=DQDimension.UNIQUENESS,
        label="唯一性",
        metric="duplicate_rate",
        threshold=0.99,
        check_func="check_uniqueness",
    ),
    DQDimension.VALIDITY: DQSpec(
        dimension=DQDimension.VALIDITY,
        label="有效性",
        metric="schema_violation_rate",
        threshold=0.99,
        check_func="check_validity",
    ),
}


def get_dq_spec(dim: DQDimension) -> DQSpec | None:
    return DQ_SPECS.get(dim)


def score_dq(dim: DQDimension, value: float) -> float:
    spec = DQ_SPECS.get(dim)
    if spec is None:
        return 0.0
    # lower_is_better=True：value 越小越健康，得分 = 1 - min(1, value/threshold)
    # lower_is_better=False：value 越大越健康，得分 = min(1, value/threshold)
    if spec.lower_is_better:
        return max(0.0, 1.0 - min(1.0, value / spec.threshold))
    return min(1.0, value / spec.threshold)


DQ_DIM_COUNT: Final[int] = 8  # B4 四维度 + 扩展四维度


# ---------------------------------------------------------------------------
# 八维 check_func 实现（15_data_feature_layer_spec §6 待裁定项落地）
#
# 口径约定（返回值语义与 DQ_SPECS.metric/lower_is_better 对齐）：
#   - 比例类指标返回"健康占比"∈[0,1]（越大越健康，threshold 为下限）；
#     空表 vacuous 处理：completeness→0.0（空表=零完整，防"空表满分"假象），
#     uniqueness/validity/consistency/timeliness→1.0（无违例可判）。
#   - lower_is_better 维度返回原始量（anomaly→离群率、freshness→年龄秒数），
#     threshold 为上限，由 score_dq 统一换算分数。
#   - accuracy/consistency 的 reference 为参考源（主备源对账），无参考源时
#     accuracy 无法定义（ValueError），consistency 降级为 OHLC 内部结构校验。
# ---------------------------------------------------------------------------


def check_completeness(df: pd.DataFrame, columns: list[str] | None = None) -> float:
    """完整性 = 非缺失单元占比 ∈[0,1]（metric=missing_pct 的补数，越大越健康）。

    空表返回 0.0（无数据=零完整）。columns 缺省查全列。
    """
    if df is None or len(df) == 0:
        return 0.0
    sub = df[columns] if columns else df
    if sub.shape[1] == 0:
        return 0.0
    return float(1.0 - sub.isna().mean().mean())


def check_accuracy(
    df: pd.DataFrame,
    reference: pd.DataFrame | None,
    tolerance: float = 0.01,
) -> float:
    """准确性 = 与参考源相对偏差 ≤ tolerance 的数值单元占比 ∈[0,1]（越大越健康）。

    metric=deviation_sigma 的 MVP 口径：偏差达标率。无参考源无法定义准确性 → ValueError。
    空 df（参考源非空）→ 0.0（应到数据缺失=零准确）。
    """
    if reference is None:
        raise ValueError("check_accuracy 需要 reference（参考源），无参考源准确性无定义")
    if df is None or len(df) == 0:
        return 0.0
    cols = [c for c in df.columns if c in reference.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not cols:
        return 0.0
    a, b = df[cols].align(reference[cols], join="inner", axis=0)
    if len(a) == 0:
        return 0.0
    a_v, b_v = a.to_numpy(dtype=float), b.to_numpy(dtype=float)
    valid = ~(np.isnan(a_v) | np.isnan(b_v))
    if not valid.any():
        return 0.0
    rel_dev = np.abs(a_v - b_v) / (np.abs(b_v) + 1e-12)
    ok = (rel_dev <= tolerance) & valid
    return float(ok.sum() / valid.sum())


def check_anomaly(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    z_threshold: float = 4.0,
) -> float:
    """异常检测 = |zscore|>z_threshold 的单元占比 ∈[0,1]（离群率，越小越健康）。

    z 按列计算（ddof=0）；常数列（std=0）无离群；NaN 不计入分子分母。
    默认 4σ（金融时序肥尾，3σ 误报多）。空表/无数值列 → 0.0。
    """
    if df is None or len(df) == 0:
        return 0.0
    sub = df[columns] if columns else df
    num = sub.select_dtypes(include=[np.number])
    if num.shape[1] == 0:
        return 0.0
    total = 0
    outliers = 0
    for c in num.columns:
        s = num[c].dropna()
        if len(s) == 0:
            continue
        std = float(s.std(ddof=0))
        total += len(s)
        if std <= 0.0:
            continue  # 常数列无离群
        z = (s - float(s.mean())) / std
        outliers += int((z.abs() > z_threshold).sum())
    if total == 0:
        return 0.0
    return outliers / total


def check_consistency(
    df: pd.DataFrame,
    reference: pd.DataFrame | None = None,
    tolerance: float = 0.0,
) -> float:
    """一致性 ∈[0,1]（越大越健康，metric=recon_diff 的补数）。

    两模式：
      - 给 reference：跨源对账一致率（相对偏差 ≤ tolerance 的单元占比，默认精确一致）；
      - 缺省：OHLC 内部结构一致率（high≥max(open,close) ∧ low≤min(open,close) 的行占比，
        与 quality_gate 四条门禁同口径）；无 OHLC 列 → ValueError。
    空表 → 1.0（vacuous）。
    """
    if df is None or len(df) == 0:
        return 1.0
    if reference is not None:
        cols = [c for c in df.columns if c in reference.columns and pd.api.types.is_numeric_dtype(df[c])]
        if not cols:
            return 1.0
        a, b = df[cols].align(reference[cols], join="inner", axis=0)
        if len(a) == 0:
            return 1.0
        a_v, b_v = a.to_numpy(dtype=float), b.to_numpy(dtype=float)
        valid = ~(np.isnan(a_v) | np.isnan(b_v))
        if not valid.any():
            return 1.0
        rel_dev = np.abs(a_v - b_v) / (np.abs(b_v) + 1e-12)
        ok = (rel_dev <= tolerance) & valid
        return float(ok.sum() / valid.sum())
    ohlc = [c for c in ("open", "high", "low", "close") if c in df.columns]
    if len(ohlc) < 4:
        raise ValueError("check_consistency 无 reference 时需 OHLC 四列做内部结构校验")
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    row_ok = (h >= l) & (h >= o) & (h >= c) & (l <= o) & (l <= c)
    # 任一价为 NaN 的行无法判定结构 → 计为不一致（保守）
    return float(row_ok.fillna(False).mean())


def check_freshness(last_updated, now=None) -> float:
    """新鲜度 = 数据年龄秒数（now − max(last_updated)，越小越健康，metric=age_seconds）。

    last_updated 接受标量 Timestamp/datetime/str 或序列（取最大值=最新一批）。
    naive 时间按 UTC 处理（与 tz-aware 混比不抛错）。None/NaT → ValueError。
    """
    if last_updated is None:
        raise ValueError("last_updated 不能为 None")
    ts = pd.to_datetime(last_updated)
    if isinstance(ts, pd.Series | pd.DatetimeIndex):
        ts = ts.max()
    ts = pd.Timestamp(ts)
    if ts is pd.NaT or pd.isna(ts):
        raise ValueError("last_updated 解析为 NaT")
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    now_ts = pd.Timestamp.now(tz="UTC") if now is None else pd.Timestamp(now)
    if now_ts.tzinfo is None:
        now_ts = now_ts.tz_localize("UTC")
    return float((now_ts - ts).total_seconds())


def check_timeliness(
    event_time: pd.Series,
    processed_time: pd.Series,
    sla_ms: float = 1000.0,
) -> float:
    """时效性 = SLA 内处理完成占比 ∈[0,1]（越大越健康）。

    metric=latency_ms 的方向约定（lower_is_better=False）要求"越大越健康"，
    故返回达标率而非原始延迟（原始延迟语义与新鲜度 age_seconds 重复）。
    latency = processed_time − event_time（毫秒）；空输入 → 1.0（vacuous）。
    """
    ev, pr = pd.to_datetime(event_time), pd.to_datetime(processed_time)
    if len(ev) == 0:
        return 1.0
    latency_ms = (pr - ev).dt.total_seconds() * 1000.0
    return float((latency_ms <= sla_ms).mean())


def check_uniqueness(df: pd.DataFrame, subset: list[str] | None = None) -> float:
    """唯一性 = 1 − 重复行占比 ∈[0,1]（越大越健康，metric=duplicate_rate 的补数）。

    duplicated(keep="first") 口径：首次出现不算重复。subset 缺省全列。空表 → 1.0。
    """
    if df is None or len(df) == 0:
        return 1.0
    return float(1.0 - df.duplicated(subset=subset, keep="first").mean())


def check_validity(df: pd.DataFrame, rules: dict[str, tuple]) -> float:
    """有效性 = 1 − 范围违例行占比 ∈[0,1]（越大越健康，metric=schema_violation_rate 的补数）。

    rules: {列名: (下界, 上界)} 闭区间；任一端 None 表示该端不查。
    单元为 NaN 计为违例（保守：缺失即不合规）。rules 为空 → ValueError。空表 → 1.0。
    """
    if not rules:
        raise ValueError("check_validity 需要非空 rules（{列: (下界, 上界)}）")
    if df is None or len(df) == 0:
        return 1.0
    violation = pd.Series(False, index=df.index)
    for col, (lo, hi) in rules.items():
        if col not in df.columns:
            violation = violation | True  # 规则列缺失 = 整列违例
            continue
        s = df[col]
        bad = s.isna()
        if lo is not None:
            bad = bad | (s < lo)
        if hi is not None:
            bad = bad | (s > hi)
        violation = violation | bad.fillna(True)
    return float(1.0 - violation.mean())


DQ_CHECK_FUNCS: Final[dict[str, Callable[..., float]]] = {
    "check_completeness": check_completeness,
    "check_accuracy": check_accuracy,
    "check_anomaly": check_anomaly,
    "check_consistency": check_consistency,
    "check_freshness": check_freshness,
    "check_timeliness": check_timeliness,
    "check_uniqueness": check_uniqueness,
    "check_validity": check_validity,
}


def run_dq_check(dim: DQDimension, data, **kwargs) -> float:
    """按 DQ_SPECS[dim].check_func 名路由到已绑定实现，返回指标原始值。

    分数换算（方向感知）由 score_dq(dim, value) 完成。
    """
    spec = DQ_SPECS.get(dim)
    if spec is None:
        raise KeyError(f"未知 DQ 维度: {dim!r}")
    func = DQ_CHECK_FUNCS.get(spec.check_func)
    if func is None:
        raise KeyError(f"check_func '{spec.check_func}' 未绑定实现")
    return func(data, **kwargs)
