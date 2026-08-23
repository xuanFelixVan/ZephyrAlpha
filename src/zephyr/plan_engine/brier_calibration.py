# [BLUEPRINT] MOD-PLAN-010 | 待统筹登记（45号 §4 W0 + 缺口总账 GAP-F-07③）
# [MODULE] zephyr.plan_engine.brier_calibration
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.reporting.prediction_log_writer(query_predictions)
# [CONSUMERS] 作战室 W0 校准度三条（预测命中校准曲线）; W6 长期校准回看（"22% 概率格实际命中率 40%"类系统性偏差识别）; GAP-F-01 情景概率分布模型（多分类 Brier 验证口径）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 算法核心纯函数（Brier 公式/分桶/ECE 不依赖 DB，可单测）; 只读 prediction_log（经 query_predictions 公共 API，零裸 SQL）; 概率输入校验 fail-closed（越界/分布和≠1/空样本即拒）; 缺概率字段的 outcome 行计 skipped_invalid 不混入样本
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（概率/outcome/分布/参数/空样本非法 fail-closed）; query_predictions 的 sqlite3.Error 透传
# [TESTS] tests/plan_engine/test_brier_calibration.py
# [A_module] module_id=MOD-PLAN-010 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

BrierCalibration — 预案概率校准计算器 (MOD-PLAN-010)

45号作战手册 §4 W0 + 缺口总账 GAP-F-07③ 落码：W0"校准度"正式算法=布赖尔评分
（Brier Score，概率预测均方误差——"说 70% 的事是不是真的 70% 发生"，45号 §10
术语表）。三件产出：

    - brier_score：二值 Brier（单事件概率 vs 0/1 真值），衡量置信度质量
      （当前消费 ScenarioPlan.confidence_scale 经 outcome payload
      predicted_confidence 字段——GAP-F-01 概率模型落地前唯一概率代理）。
    - brier_score_multiclass：多分类 Brier（9 格概率分布 vs 实际 one-hot，
      mean Σ(p_k-o_k)²）——GAP-F-01 情景概率分布模型的验证口径预留。
    - calibration_bins + expected_calibration_error：校准分桶（reliability
      curve 数据：每桶 预测均值 vs 经验频率 vs 校准差）+ ECE（加权平均
      绝对校准差）——W6"22% 概率格实际命中率 40%"类系统性偏差的识别载体。

读库口径（prediction_log outcome 族 payload）：概率取 probability 字段优先、
predicted_confidence 兜底（MOD-PLAN-008 回写契约）；真值=hit:bool→1/0；
双字段皆缺/类型错 → skipped_invalid 计数不混入样本（防污染校准曲线）。
零样本 → ValueError（校准分不可伪造，fail-closed）。

不做什么：不出调参建议（归 MOD-RPT-029）/不做三维归因（归 MOD-PLAN-009）/
         不判定 hit（回写方职责，44号 §12.1 M4-④ 裁定二）。

依据: 45_warroom_playbook §4 W0/W6 + §10（Brier Score 术语）
SSoT: depgraph MOD-PLAN-010（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: (概率, 0/1 真值) 序列 / (概率分布, 命中格索引) 序列 / prediction_log outcome 族
# 特征: 预测概率 vs 经验频率
# 算法: Brier=mean((p-o)²) / 多分类 Brier=mean(Σ(p_k-o_k)²) / 等宽分桶可靠性曲线 / ECE
# 输出: CalibrationReport（纯 frozen dataclass，JSON 可序列化）

"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final, Iterable, Sequence

from zephyr.reporting.prediction_log_writer import query_predictions

__all__: Final = [
    "CalibrationBin",
    "CalibrationReport",
    "brier_score",
    "brier_score_multiclass",
    "calibration_bins",
    "compute_calibration",
    "expected_calibration_error",
    "load_confidence_pairs",
]

# ── 口径常量 ──

DEFAULT_WINDOW_DAYS: Final = 20  # W0 校准默认窗口（45号 §4 W0"近 20 日"口径）
DEFAULT_N_BINS: Final = 10  # 校准分桶默认桶数（reliability curve 十分桶惯例）
OUTCOME_PREDICTION_TYPE: Final = "outcome"  # outcome 族（prediction_log 单一账本）
_STATS_QUERY_LIMIT: Final = 10000  # 窗口内单模块行数上限
_PROB_SUM_TOLERANCE: Final = 1e-6  # 多分类分布和≈1 容差

# outcome payload 概率字段优先级（MOD-PLAN-008 回写契约：predicted_confidence）
_KEY_PROBABILITY: Final = "probability"
_KEY_PREDICTED_CONFIDENCE: Final = "predicted_confidence"
_KEY_HIT: Final = "hit"


# ── 数据契约 ──


@dataclass(frozen=True)
class CalibrationBin:
    """校准分桶单桶（reliability curve 一格）。"""

    bin_index: int  # 桶序号（0 起）
    lower: float  # 桶下界（含）
    upper: float  # 桶上界（不含；末桶含 1.0）
    count: int  # 桶内样本数
    mean_predicted: float | None  # 桶内预测概率均值（空桶 None）
    empirical_freq: float | None  # 桶内经验命中率（空桶 None）
    calibration_gap: float | None  # mean_predicted - empirical_freq（空桶 None；负=系统性低估）


@dataclass(frozen=True)
class CalibrationReport:
    """校准报告（读库组合入口输出，纯数据不判定，JSON 可序列化）。"""

    module: str
    window_days: int
    window_start: str
    window_end: str
    sample_size: int
    brier: float  # 二值 Brier
    ece: float  # 期望校准误差（分桶加权平均 |gap|）
    n_bins: int
    bins: tuple[CalibrationBin, ...]
    skipped_invalid: int = 0  # 缺概率字段/类型错被剔除的行数

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（W0 校准度/W6 长期校准消费契约）。"""
        return {
            "module": self.module,
            "window_days": self.window_days,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "sample_size": self.sample_size,
            "brier": self.brier,
            "ece": self.ece,
            "n_bins": self.n_bins,
            "bins": [
                {
                    "bin_index": b.bin_index,
                    "lower": b.lower,
                    "upper": b.upper,
                    "count": b.count,
                    "mean_predicted": b.mean_predicted,
                    "empirical_freq": b.empirical_freq,
                    "calibration_gap": b.calibration_gap,
                }
                for b in self.bins
            ],
            "skipped_invalid": self.skipped_invalid,
        }


# ── 校验原语（fail-closed）──


def _validate_prob(p: object, field: str = "probability") -> float:
    """概率校验：有限实数且 ∈[0,1]（fail-closed）。"""
    if isinstance(p, bool) or not isinstance(p, (int, float)):
        raise ValueError(f"{field} 非法（须 [0,1] 实数）: {p!r}")
    f = float(p)
    if not math.isfinite(f) or f < 0.0 or f > 1.0:
        raise ValueError(f"{field} 非法（须 [0,1] 实数）: {p!r}")
    return f


def _validate_outcome(o: object) -> float:
    """真值校验：0/1（bool/int/float 兼容，fail-closed）。"""
    if isinstance(o, bool):
        return 1.0 if o else 0.0
    if isinstance(o, (int, float)) and float(o) in (0.0, 1.0):
        return float(o)
    raise ValueError(f"outcome 非法（须 0/1 真值）: {o!r}")


def _validate_pairs(pairs: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    """(概率, 真值) 序列校验+归一（空序列 fail-closed）。"""
    out: list[tuple[float, float]] = []
    for item in pairs:
        p, o = item
        out.append((_validate_prob(p), _validate_outcome(o)))
    if not out:
        raise ValueError("pairs 非法（空序列不可算校准，fail-closed）")
    return out


def _validate_n_bins(n_bins: object) -> int:
    """分桶数校验：正整数（fail-closed）。"""
    if isinstance(n_bins, bool) or not isinstance(n_bins, int) or n_bins < 1:
        raise ValueError(f"n_bins 非法（须正整数）: {n_bins!r}")
    return n_bins


# ── 算法核心（纯函数，不依赖 DB）──


def brier_score(pairs: Iterable[tuple[float, float]]) -> float:
    """二值 Brier 评分（纯函数）：mean((p - o)²)，越小越准（0=完美）。

    Args:
        pairs: (预测概率, 真值 0/1) 序列（空序列 fail-closed）。

    Returns:
        Brier 评分 ∈[0,1]。

    Raises:
        ValueError: 概率越界/真值非 0|1/空序列（fail-closed）。
    """
    norm = _validate_pairs(pairs)
    return sum((p - o) ** 2 for p, o in norm) / len(norm)


def brier_score_multiclass(distributions: Iterable[tuple[Sequence[float], int]]) -> float:
    """多分类 Brier 评分（纯函数）：mean(Σ_k (p_k - o_k)²)，0=完美。

    9 格情景概率分布的验证口径（GAP-F-01 预留）：o_k=1 当 k=实际命中格索引，
    余为 0。取值 ∈[0,2]（全押错格=2）。

    Args:
        distributions: (概率分布序列, 实际命中格索引) 序列；分布须非空、各分量
            ∈[0,1]、和≈1（±1e-6），索引 ∈[0, len)（空序列/非法 fail-closed）。

    Returns:
        多分类 Brier 评分。

    Raises:
        ValueError: 分布非法/索引越界/空序列（fail-closed）。
    """
    items = list(distributions)
    if not items:
        raise ValueError("distributions 非法（空序列不可算校准，fail-closed）")
    total = 0.0
    for probs, outcome_idx in items:
        if isinstance(outcome_idx, bool) or not isinstance(outcome_idx, int):
            raise ValueError(f"outcome 索引非法（须 int）: {outcome_idx!r}")
        vals = [_validate_prob(p, "distribution 分量") for p in probs]
        if not vals:
            raise ValueError("概率分布非法（空分布，fail-closed）")
        if abs(sum(vals) - 1.0) > _PROB_SUM_TOLERANCE:
            raise ValueError(f"概率分布和≠1（±{_PROB_SUM_TOLERANCE}）: {sum(vals)!r}")
        if outcome_idx < 0 or outcome_idx >= len(vals):
            raise ValueError(f"outcome 索引越界（分布维数 {len(vals)}）: {outcome_idx!r}")
        total += sum(
            (p - (1.0 if k == outcome_idx else 0.0)) ** 2 for k, p in enumerate(vals)
        )
    return total / len(items)


def calibration_bins(
    pairs: Iterable[tuple[float, float]],
    n_bins: int = DEFAULT_N_BINS,
) -> tuple[CalibrationBin, ...]:
    """校准分桶（纯函数）：等宽桶 [i/n,(i+1)/n)，末桶含 1.0 → reliability curve 数据。

    Args:
        pairs: (预测概率, 真值 0/1) 序列（空序列 fail-closed）。
        n_bins: 桶数（正整数）。

    Returns:
        n_bins 个 CalibrationBin（空桶 count=0、均值/频率/校准差 None）。

    Raises:
        ValueError: 概率越界/真值非 0|1/空序列/n_bins 非法（fail-closed）。
    """
    norm = _validate_pairs(pairs)
    v_bins = _validate_n_bins(n_bins)
    width = 1.0 / v_bins
    sums: list[float] = [0.0] * v_bins
    hits: list[float] = [0.0] * v_bins
    counts: list[int] = [0] * v_bins
    for p, o in norm:
        idx = min(int(p / width), v_bins - 1)  # p=1.0 落末桶
        sums[idx] += p
        hits[idx] += o
        counts[idx] += 1
    out: list[CalibrationBin] = []
    for i in range(v_bins):
        if counts[i] == 0:
            out.append(
                CalibrationBin(
                    bin_index=i,
                    lower=round(i * width, 10),
                    upper=round((i + 1) * width, 10),
                    count=0,
                    mean_predicted=None,
                    empirical_freq=None,
                    calibration_gap=None,
                )
            )
            continue
        mean_p = sums[i] / counts[i]
        freq = hits[i] / counts[i]
        out.append(
            CalibrationBin(
                bin_index=i,
                lower=round(i * width, 10),
                upper=round((i + 1) * width, 10),
                count=counts[i],
                mean_predicted=mean_p,
                empirical_freq=freq,
                calibration_gap=mean_p - freq,
            )
        )
    return tuple(out)


def expected_calibration_error(
    pairs: Iterable[tuple[float, float]],
    n_bins: int = DEFAULT_N_BINS,
) -> float:
    """期望校准误差 ECE（纯函数）：Σ(桶样本占比 × |校准差|)，越小越校准。

    Args:
        pairs: (预测概率, 真值 0/1) 序列（空序列 fail-closed）。
        n_bins: 桶数（正整数）。

    Returns:
        ECE ∈[0,1]。

    Raises:
        ValueError: 同 calibration_bins（fail-closed）。
    """
    norm = _validate_pairs(pairs)
    bins = calibration_bins(norm, n_bins=n_bins)
    total = len(norm)
    return sum(
        (b.count / total) * abs(b.calibration_gap)
        for b in bins
        if b.count > 0 and b.calibration_gap is not None
    )


# ── 读库组合（prediction_log outcome 族 → 校准报告）──


def _validate_module(module: object) -> str:
    """module 校验：非空字符串（fail-closed）。"""
    if not isinstance(module, str) or not module.strip():
        raise ValueError(f"module 非法（须非空字符串）: {module!r}")
    return module.strip()


def _validate_window_days(window_days: object) -> int:
    """window_days 校验：正整数（fail-closed）。"""
    if isinstance(window_days, bool) or not isinstance(window_days, int) or window_days < 1:
        raise ValueError(f"window_days 非法（须正整数）: {window_days!r}")
    return window_days


def _extract_prob(payload: dict) -> float | None:
    """payload → 概率：probability 字段优先、predicted_confidence 兜底；非法→None。"""
    for key in (_KEY_PROBABILITY, _KEY_PREDICTED_CONFIDENCE):
        v = payload.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        f = float(v)
        if math.isfinite(f) and 0.0 <= f <= 1.0:
            return f
    return None


def load_confidence_pairs(
    module: str,
    window_days: int = DEFAULT_WINDOW_DAYS,
    db_path: str | Path | None = None,
    as_of: date | None = None,
) -> tuple[list[tuple[float, float]], int]:
    """从 prediction_log 读 outcome 族行 → (概率, 0/1) 序列（窗口过滤+契约校验）。

    口径：概率=probability 优先/predicted_confidence 兜底；真值=hit:bool→1/0；
    双字段皆缺或类型错 → skipped_invalid 计数不混入样本。

    Args:
        module: 统计对象模块标识（非空字符串，fail-closed）。
        window_days: 统计窗口天数（正整数；含 as_of 当日的自然日闭区间）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        as_of: 窗口基准日（None=date.today()；测试注入固定日期保确定性）。

    Returns:
        (pairs, skipped_invalid)。

    Raises:
        ValueError: module/window_days 非法（fail-closed）。
        sqlite3.Error: 库级异常透传。
    """
    v_module = _validate_module(module)
    v_window = _validate_window_days(window_days)
    end = as_of if as_of is not None else date.today()
    window_start = (end - timedelta(days=v_window - 1)).isoformat()
    window_end = end.isoformat()

    rows = query_predictions(
        module=v_module,
        prediction_type=OUTCOME_PREDICTION_TYPE,
        limit=_STATS_QUERY_LIMIT,
        db_path=db_path,
    )

    pairs: list[tuple[float, float]] = []
    skipped = 0
    for row in rows:
        if not (window_start <= row["trade_date"] <= window_end):
            continue
        try:
            payload = json.loads(row["payload_json"])
        except (json.JSONDecodeError, TypeError):
            skipped += 1
            continue
        if not isinstance(payload, dict):
            skipped += 1
            continue
        hit = payload.get(_KEY_HIT)
        if not isinstance(hit, bool):
            skipped += 1
            continue
        prob = _extract_prob(payload)
        if prob is None:
            skipped += 1
            continue
        pairs.append((prob, 1.0 if hit else 0.0))
    return pairs, skipped


def compute_calibration(
    module: str,
    window_days: int = DEFAULT_WINDOW_DAYS,
    n_bins: int = DEFAULT_N_BINS,
    db_path: str | Path | None = None,
    as_of: date | None = None,
) -> CalibrationReport:
    """组合主入口（MOD-PLAN-010）：读库 → Brier + 校准分桶报告。

    Args:
        module: 统计对象模块标识（如 "plan_engine.scenario_planner"）。
        window_days: 统计窗口天数（默认 20，45号 §4 W0 口径）。
        n_bins: 校准分桶数（默认 10）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        as_of: 窗口基准日（None=date.today()）。

    Returns:
        CalibrationReport（JSON 可序列化，W0 校准度消费契约）。

    Raises:
        ValueError: module/window_days/n_bins 非法或零样本（fail-closed——
            校准分不可伪造）。
        sqlite3.Error: 库级异常透传。
    """
    v_module = _validate_module(module)
    v_window = _validate_window_days(window_days)
    v_bins = _validate_n_bins(n_bins)
    end = as_of if as_of is not None else date.today()
    window_start = (end - timedelta(days=v_window - 1)).isoformat()
    pairs, skipped = load_confidence_pairs(
        v_module, window_days=v_window, db_path=db_path, as_of=end,
    )
    return CalibrationReport(
        module=v_module,
        window_days=v_window,
        window_start=window_start,
        window_end=end.isoformat(),
        sample_size=len(pairs),
        brier=brier_score(pairs),
        ece=expected_calibration_error(pairs, n_bins=v_bins),
        n_bins=v_bins,
        bins=calibration_bins(pairs, n_bins=v_bins),
        skipped_invalid=skipped,
    )
