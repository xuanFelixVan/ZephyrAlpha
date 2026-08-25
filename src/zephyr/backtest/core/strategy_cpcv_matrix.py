# [BLUEPRINT] MOD-BT-028 | docs/03_modules/_domain_backtest/strategy_cpcv_matrix/blueprint.md
# [MODULE] zephyr.backtest.core.strategy_cpcv_matrix
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.cpcv
# [CONSUMERS] 运行时装配批（策略池候选注入/筛选漏斗离线验证段接线）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只编排不重造(CPCV切分复用MOD-BT-001 cpcv); 性能矩阵输入注入(本模块不跑回测); 稳健分=mean(OOS降序秩)/n_strategies∈(0,1]; 交集筛选=min_votes门槛+max_candidates封顶; 稳健池空→degraded留痕不伪造放行; 输入非法Fail-Closed
# [MODIFY-GUARD] tests/backtest/test_strategy_cpcv_matrix.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategyCPCVError(未登记错误码-申请中)
# [TESTS] tests/backtest/test_strategy_cpcv_matrix.py
# [A_module] module_id=MOD-BT-028 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: performance(策略×样本性能矩阵,注入) + strategy_ids + config
# I2: candidate_votes(策略→候选名单,注入)
# A1: build_score_matrix(复用generate_cpcv_splits→逐折各策略IS/OOS均值)
# A2: compute_robust_scores(逐折OOS降序秩(同值平均秩)→稳健分=mean秩/M)
# A3: select_candidates(稳健池≤threshold→≥min_votes交集→票数降序+稳健分升序→≤30封顶)
# O1: StrategyCPCVReport(split_scores/robust_scores/robust_pool/selected_candidates/degraded)
# [/ALGO_FLOW]
"""第五层：多策略交叉验证——策略级 CPCV 打分矩阵 + 多策略交集筛选（MOD-BT-028）。

真源：construction_backlog_dig.tsv B10-01272（A1交易决策架构 §1.1，裁定=做 P1）
+ CAND-WFO-003。（改铸注记：初铸 MOD-BT-027 与并行会话 W-P1-18 C-003
layered_validation_pipeline 撞车，2026-08-25 改铸 MOD-BT-028。）

定位（查重铁律①分工论证，异非撞名）：本模块是筛选漏斗第五层的**离线回测验证
层**（D_BACKTEST，CPCV 方法论， Lopez de Prado 组合净化交叉验证策略级打分）；
W-P1-05 的 B10-01504 是同层号的**在线信号层**（D_ASHARE_SIGNAL，60 秒级三席
YES/NO 投票+市场状态否决门）——数据平面与方法论均不同，各自 canonical。

三段式（全部确定性纯函数，性能矩阵/候选名单调用方注入）：
  ① 打分矩阵：复用 MOD-BT-001 generate_cpcv_splits 生成 CPCV 切分，逐折计算
     各策略 IS/OOS 均值（train/test 索引由切分给出，purge+embargo 语义继承）。
  ② 稳健分：逐折按 OOS 均值降序秩（秩 1=最优，同值取平均秩），策略稳健分
     = mean(oos_rank)/n_strategies ∈ (0,1]，越小越稳健（PBO 同族秩口径）。
  ③ 交集筛选：稳健分 ≤ robust_threshold 的策略入稳健池；候选=池内 ≥min_votes
     策略共同提名的标的，按（提名数降序, 最佳提名者稳健分升序, 代码升序）取
     max_candidates（默认 30，对齐 A1 漏斗 ~30 只候选）。

Fail-Closed：矩阵形状不齐/含非有限值/strategy_ids 不齐或重复/阈值越界/
candidate_votes 含未知策略 → StrategyCPCVError；稳健池为空 → 空候选 +
degraded=True 留痕（不伪造放行）。

不做什么：不跑真实回测（性能矩阵注入）、不做在线投票（归 B10-01504）、
不产出下单信号（只出候选名单与打分矩阵）。

SSoT: docs/03_modules/_domain_backtest/strategy_cpcv_matrix/blueprint.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Sequence

import numpy as np

from zephyr.backtest.core.cpcv import generate_cpcv_splits

__all__: Final = [
    "SplitScore",
    "StrategyCPCVConfig",
    "StrategyCPCVError",
    "StrategyCPCVReport",
    "build_score_matrix",
    "compute_robust_scores",
    "run_strategy_cpcv",
    "select_candidates",
]


class StrategyCPCVError(Exception):
    """策略级 CPCV 打分矩阵/交集筛选错误（输入非法）。"""

    error_code = "ZA-BT-0037"  # 2026-08-25 主代理正式登记（P1 R4W19）

    def __init__(self, *args: object, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class StrategyCPCVConfig:
    """策略级 CPCV 配置（不可变）。

    Attributes:
        n_groups: CPCV 分组数（>=2）
        k_test: 每折测试组数（1 <= k_test < n_groups）
        t1: 各样本标签末端索引（None=点标签，语义同 cpcv.generate_cpcv_splits）
        embargo: test 末端后隔离样本数（>=0）
        robust_threshold: 稳健池阈值（0,1]，稳健分 ≤ 阈值入池（默认 0.5=OOS 中位秩以上）
        min_votes: 候选入选最小提名数（>=1，默认 2=交集语义）
        max_candidates: 候选封顶（>=1，默认 30，对齐 A1 漏斗 ~30 只）
    """

    n_groups: int = 6
    k_test: int = 2
    t1: Sequence[int] | None = None
    embargo: int = 0
    robust_threshold: float = 0.5
    min_votes: int = 2
    max_candidates: int = 30

    def __post_init__(self) -> None:
        if not 0.0 < self.robust_threshold <= 1.0:
            raise StrategyCPCVError(f"robust_threshold必须在(0,1], got {self.robust_threshold}")
        if self.min_votes < 1:
            raise StrategyCPCVError(f"min_votes必须>=1, got {self.min_votes}")
        if self.max_candidates < 1:
            raise StrategyCPCVError(f"max_candidates必须>=1, got {self.max_candidates}")


@dataclass(frozen=True)
class SplitScore:
    """单折策略级打分（不可变）。"""

    split_id: int
    test_groups: tuple[int, ...]
    is_means: dict[str, float]
    oos_means: dict[str, float]


@dataclass(frozen=True)
class StrategyCPCVReport:
    """第五层多策略交叉验证报告（不可变）。

    Attributes:
        split_scores: 逐折 IS/OOS 打分矩阵
        robust_scores: 策略稳健分（mean(OOS降序秩)/M ∈ (0,1]，越小越稳健）
        robust_pool: 稳健池策略（robust_score ≤ robust_threshold，按稳健分升序）
        selected_candidates: [(candidate, votes)] 交集筛选结果（票数降序+稳健分升序+代码升序，≤max_candidates）
        degraded: 稳健池为空降级标记（空候选不伪造放行）
    """

    split_scores: tuple[SplitScore, ...] = ()
    robust_scores: dict[str, float] = field(default_factory=dict)
    robust_pool: tuple[str, ...] = ()
    selected_candidates: tuple[tuple[str, int], ...] = ()
    degraded: bool = False


def _validate_performance(
    performance: Sequence[Sequence[float]],
    strategy_ids: Sequence[str],
) -> np.ndarray:
    """性能矩阵结构校验（Fail-Closed），返回 (n_strategies, n_samples) 数组。"""
    if not strategy_ids:
        raise StrategyCPCVError("strategy_ids不能为空")
    if len(set(strategy_ids)) != len(strategy_ids):
        raise StrategyCPCVError("strategy_ids不得重复")
    rows = [list(row) for row in performance]
    if len(rows) != len(strategy_ids):
        raise StrategyCPCVError(
            f"performance行数({len(rows)})必须等于strategy_ids数({len(strategy_ids)})"
        )
    if not rows or not rows[0]:
        raise StrategyCPCVError("performance不能为空矩阵")
    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            raise StrategyCPCVError("performance必须矩形（各行样本数一致）")
    arr = np.asarray(rows, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise StrategyCPCVError("performance含NaN/Inf, 拒绝计算")
    return arr


def build_score_matrix(
    performance: Sequence[Sequence[float]],
    strategy_ids: Sequence[str],
    config: StrategyCPCVConfig | None = None,
) -> list[SplitScore]:
    """构建策略级 CPCV 打分矩阵（逐折各策略 IS/OOS 均值）。

    切分复用 MOD-BT-001 generate_cpcv_splits（purge+embargo 语义继承），
    本函数只聚合打分不重造切分。
    """
    cfg = config or StrategyCPCVConfig()
    arr = _validate_performance(performance, strategy_ids)
    n_samples = arr.shape[1]
    splits = generate_cpcv_splits(
        n_samples, cfg.n_groups, cfg.k_test, t1=cfg.t1, embargo=cfg.embargo
    )
    out: list[SplitScore] = []
    for split in splits:
        train_idx = np.asarray(split.train_indices, dtype=int)
        test_idx = np.asarray(split.test_indices, dtype=int)
        if train_idx.size == 0 or test_idx.size == 0:
            raise StrategyCPCVError(
                f"split {split.split_id} 切分后 train/test 为空（purge+embargo 过严），拒绝打分"
            )
        is_means = {
            sid: float(np.mean(arr[r, train_idx])) for r, sid in enumerate(strategy_ids)
        }
        oos_means = {
            sid: float(np.mean(arr[r, test_idx])) for r, sid in enumerate(strategy_ids)
        }
        out.append(
            SplitScore(
                split_id=split.split_id,
                test_groups=split.test_groups,
                is_means=is_means,
                oos_means=oos_means,
            )
        )
    return out


def _average_ranks_descending(values: np.ndarray) -> np.ndarray:
    """降序平均秩（最大值秩=1，同值取平均秩），纯 numpy 避免 scipy 依赖。"""
    order = np.argsort(-values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    sorted_vals = values[order]
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and sorted_vals[j] == sorted_vals[i]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0  # 秩从1开始: 位置[i, j)的平均秩
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def compute_robust_scores(split_scores: Sequence[SplitScore]) -> dict[str, float]:
    """计算策略稳健分：逐折 OOS 均值降序秩（秩1=最优，同值平均秩）→ mean(秩)/M。

    返回值 ∈ (0,1]，越小越稳健（PBO 同族秩口径：秩/(M+1) 的中位秩=0.5 对应
    本口径 mean_rank/M 的中位秩=(M+1)/(2M)≈0.5）。
    """
    if not split_scores:
        raise StrategyCPCVError("split_scores不能为空")
    strategy_ids = list(split_scores[0].oos_means.keys())
    if not strategy_ids:
        raise StrategyCPCVError("split_scores策略集不能为空")
    for sc in split_scores:
        if set(sc.oos_means.keys()) != set(strategy_ids):
            raise StrategyCPCVError("各折策略集必须一致")
    m = len(strategy_ids)
    rank_sum = {sid: 0.0 for sid in strategy_ids}
    for sc in split_scores:
        oos = np.asarray([sc.oos_means[sid] for sid in strategy_ids], dtype=float)
        ranks = _average_ranks_descending(oos)
        for idx, sid in enumerate(strategy_ids):
            rank_sum[sid] += float(ranks[idx])
    n_splits = len(split_scores)
    return {sid: rank_sum[sid] / n_splits / m for sid in strategy_ids}


def select_candidates(
    robust_scores: dict[str, float],
    candidate_votes: dict[str, Sequence[str]],
    config: StrategyCPCVConfig | None = None,
) -> StrategyCPCVReport:
    """多策略交集筛选：稳健池 ∩ ≥min_votes 提名 → 票数降序取 ≤max_candidates。

    排序键确定性：（提名数降序, 最佳提名者稳健分升序, 候选代码升序）。
    稳健池为空 → degraded=True + 空候选（不伪造放行）。
    """
    cfg = config or StrategyCPCVConfig()
    if not robust_scores:
        raise StrategyCPCVError("robust_scores不能为空")
    unknown = set(candidate_votes) - set(robust_scores)
    if unknown:
        raise StrategyCPCVError(f"candidate_votes含未知策略: {sorted(unknown)}")

    pool = sorted(
        (sid for sid, s in robust_scores.items() if s <= cfg.robust_threshold),
        key=lambda sid: (robust_scores[sid], sid),
    )
    if not pool:
        return StrategyCPCVReport(
            robust_scores=dict(robust_scores),
            robust_pool=(),
            selected_candidates=(),
            degraded=True,
        )

    vote_count: dict[str, int] = {}
    best_pool_score: dict[str, float] = {}
    for sid in pool:
        for cand in candidate_votes.get(sid, ()):
            vote_count[cand] = vote_count.get(cand, 0) + 1
            score = robust_scores[sid]
            if cand not in best_pool_score or score < best_pool_score[cand]:
                best_pool_score[cand] = score

    eligible = [c for c, n in vote_count.items() if n >= cfg.min_votes]
    eligible.sort(key=lambda c: (-vote_count[c], best_pool_score[c], c))
    selected = tuple((c, vote_count[c]) for c in eligible[: cfg.max_candidates])
    return StrategyCPCVReport(
        robust_scores=dict(robust_scores),
        robust_pool=tuple(pool),
        selected_candidates=selected,
        degraded=False,
    )


def run_strategy_cpcv(
    performance: Sequence[Sequence[float]],
    strategy_ids: Sequence[str],
    candidate_votes: dict[str, Sequence[str]],
    config: StrategyCPCVConfig | None = None,
) -> StrategyCPCVReport:
    """第五层全链路：打分矩阵 → 稳健分 → 交集筛选（三段合一便捷入口）。"""
    cfg = config or StrategyCPCVConfig()
    split_scores = build_score_matrix(performance, strategy_ids, cfg)
    robust = compute_robust_scores(split_scores)
    report = select_candidates(robust, candidate_votes, cfg)
    return StrategyCPCVReport(
        split_scores=tuple(split_scores),
        robust_scores=report.robust_scores,
        robust_pool=report.robust_pool,
        selected_candidates=report.selected_candidates,
        degraded=report.degraded,
    )
