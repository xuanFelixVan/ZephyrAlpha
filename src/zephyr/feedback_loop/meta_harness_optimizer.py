# [BLUEPRINT] MOD-FBL-004 | docs/03_modules/_domain_feedback_loop/meta_harness_optimizer/blueprint.md
# [MODULE] zephyr.feedback_loop.meta_harness_optimizer
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] 无（协议核心纯内存；evaluator/clock 全注入）
# [CONSUMERS] 运行时装配批（学习系统超参 A/B 实验台统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 学习超参词表闭合(mutation_rate|match_threshold|review_policy); 策略参数不可入配置(仅 LearningConfig 实例硬约束); 显著性判定 |Δ|>=margin(恰等归显著); 显著胜者分数高者/平局保留原配置; 递归深度 depth>max_depth Fail-Closed; experiment_id 确定性递增(exp-NNNN); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_feedback_loop/meta_harness_optimizer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MetaHarnessError(占位 ZA-FBL-UNREGISTERED-META-HARNESS)——evaluator未注入/非法学习超参/越界取值/策略参数混入/超递归深度上限/evaluator返回非法时抛
# [TESTS] tests/feedback_loop/test_meta_harness_optimizer.py
# [A_module] module_id=MOD-FBL-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
MetaHarnessOptimizer — Meta-Harness 元优化器（MOD-FBL-004）。

B12-03617（AUD-DRAFT-001-DIGEST P2 波 P2-W14，CAND-FBL-006，B12）：学习系统
**自身超参**（变异率 mutation_rate / 匹配阈值 match_threshold / 审核策略
review_policy，词表白名单）的 **A/B 实验台**（两组配置 → 注入 evaluator 打分 →
显著性判定）+ **优胜配置保留**（显著胜者晋升为当前配置，平局保留原配置）+
**递归优化护栏**（仅调学习参数、**不动策略参数**硬约束 + 递归深度上限）。

纯内存确定性：evaluator/时钟全注入，无网络/无子进程；同输入必同输出。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: initial_config 参数
#   fields: 参数 initial_config（无注解）
#   code: meta_harness_optimizer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: evaluator 参数
#   fields: 参数 evaluator（无注解）
#   code: meta_harness_optimizer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: meta_harness_optimizer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: significance_margin 参数
#   fields: 参数 significance_margin（无注解）
#   code: meta_harness_optimizer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MetaHarnessOptimizer
#   name_en: MetaHarnessOptimizer
#   intro: Meta-Harness 元优化器（A/B 实验台 + 优胜保留 + 递归护栏）。
#   desc: Meta-Harness 元优化器（A/B 实验台 + 优胜保留 + 递归护栏）。；公共方法（定义序）: run_ab_experiment, current_config, max_depth, history；源码…
#   inputs: initial_config evaluator clock significance_margin max_depth
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: MetaHarnessOptimizer
#   downstream: 运行时装配批（学习系统超参 A/B 实验台统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ABExperimentResult",
    "ArmWinner",
    "LearningConfig",
    "MetaHarnessError",
    "MetaHarnessOptimizer",
    "ReviewPolicy",
]


class MetaHarnessError(Exception):
    """元优化器输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FBL-UNREGISTERED-META-HARNESS。
    """


class ReviewPolicy(str, Enum):
    """审核策略（词表白名单闭合）。"""

    STRICT = "strict"  # 严格审核
    STANDARD = "standard"  # 标准审核
    LENIENT = "lenient"  # 宽松审核


class ArmWinner(str, Enum):
    """A/B 实验胜方。"""

    A = "A"
    B = "B"
    TIE = "tie"


@dataclass(frozen=True)
class LearningConfig:
    """学习超参配置（词表白名单闭合，frozen）。

    硬约束：仅学习系统自身超参三字段，**策略参数不可入配置**——任何携带
    策略参数的载体都无法通过 LearningConfig Schema 校验。
    """

    mutation_rate: float
    match_threshold: float
    review_policy: ReviewPolicy

    def __post_init__(self) -> None:
        mr = self.mutation_rate
        if (
            isinstance(mr, bool)
            or not isinstance(mr, (int, float))
            or not math.isfinite(float(mr))
            or not (0.0 < float(mr) <= 1.0)
        ):
            raise MetaHarnessError(f"非法 mutation_rate: {mr!r}（须 0<rate<=1 有限实数）")
        mt = self.match_threshold
        if (
            isinstance(mt, bool)
            or not isinstance(mt, (int, float))
            or not math.isfinite(float(mt))
            or not (0.0 <= float(mt) <= 1.0)
        ):
            raise MetaHarnessError(f"非法 match_threshold: {mt!r}（须 0<=threshold<=1 有限实数）")
        if not isinstance(self.review_policy, ReviewPolicy):
            raise MetaHarnessError(
                f"非法 review_policy: {self.review_policy!r}（词表白名单: {[p.value for p in ReviewPolicy]}）"
            )


@dataclass(frozen=True)
class ABExperimentResult:
    """A/B 实验结果（frozen）。"""

    experiment_id: str
    arm_a: LearningConfig
    arm_b: LearningConfig
    score_a: float
    score_b: float
    winner: ArmWinner
    significant: bool
    depth: int
    completed_at: datetime.datetime


def _require_finite_score(value: object, field: str) -> float:
    """evaluator 返回值校验：非 bool 的 int/float 且有限，否则 Fail-Closed。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MetaHarnessError(f"{field} 非数值: {value!r}")
    out = float(value)
    if not math.isfinite(out):
        raise MetaHarnessError(f"{field} 非有限数值: {value!r}")
    return out


class MetaHarnessOptimizer:
    """Meta-Harness 元优化器（A/B 实验台 + 优胜保留 + 递归护栏）。"""

    def __init__(
        self,
        *,
        initial_config: LearningConfig,
        evaluator: Callable[[LearningConfig], float] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        significance_margin: float = 0.01,
        max_depth: int = 1,
    ) -> None:
        if not isinstance(initial_config, LearningConfig):
            raise MetaHarnessError(
                f"initial_config 非 LearningConfig: {initial_config!r}（策略参数禁入：仅学习超参白名单 Schema）"
            )
        if evaluator is None:
            raise MetaHarnessError("evaluator 未注入（A/B 实验强制注入评估器，Fail-Closed）")
        if (
            isinstance(significance_margin, bool)
            or not isinstance(significance_margin, (int, float))
            or not math.isfinite(float(significance_margin))
            or float(significance_margin) < 0.0
        ):
            raise MetaHarnessError(f"非法 significance_margin: {significance_margin!r}（须 >=0 有限实数）")
        if isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 0:
            raise MetaHarnessError(f"非法 max_depth: {max_depth!r}（须 >=0 整数）")
        self._current = initial_config
        self._evaluator = evaluator
        self._clock = clock or datetime.datetime.now
        self._margin = float(significance_margin)
        self._max_depth = max_depth
        self._seq = 0
        self._history: list[ABExperimentResult] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _evaluate(self, config: LearningConfig, field: str) -> float:
        """经注入 evaluator 打分（异常/非法返回 Fail-Closed；MetaHarnessError 透传）。"""
        try:
            raw = self._evaluator(config)
        except MetaHarnessError:
            raise
        except Exception as exc:  # noqa: BLE001 — evaluator 异常按 Fail-Closed 转译
            _log.exception("evaluator 评估异常")
            raise MetaHarnessError(f"evaluator 评估异常: {exc!r}") from exc
        return _require_finite_score(raw, field)

    @staticmethod
    def _require_learning_config(config: object, field: str) -> LearningConfig:
        """策略参数不动硬约束：仅 LearningConfig 实例可入实验。"""
        if not isinstance(config, LearningConfig):
            raise MetaHarnessError(f"{field} 非 LearningConfig: {config!r}（仅学习超参白名单；策略参数禁入，硬约束）")
        return config

    # ── A/B 实验台 ────────────────────────────────────────────────────────

    def run_ab_experiment(
        self,
        arm_a: LearningConfig,
        arm_b: LearningConfig,
        *,
        depth: int = 0,
    ) -> ABExperimentResult:
        """A/B 实验：两组配置 → evaluator 打分 → 显著性判定 → 优胜保留。

        显著性：|score_a - score_b| >= significance_margin（恰等归显著）；
        胜者为分数高者，不显著/同分为 TIE。TIE 保留原配置不变。
        递归护栏：depth > max_depth 直接 Fail-Closed。
        """
        cfg_a = self._require_learning_config(arm_a, "arm_a")
        cfg_b = self._require_learning_config(arm_b, "arm_b")
        if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
            raise MetaHarnessError(f"非法 depth: {depth!r}（须 >=0 整数）")
        if depth > self._max_depth:
            raise MetaHarnessError(f"递归深度超限: depth={depth} > max_depth={self._max_depth}（护栏）")
        score_a = self._evaluate(cfg_a, "score_a")
        score_b = self._evaluate(cfg_b, "score_b")
        diff = score_a - score_b
        significant = abs(diff) >= self._margin
        if significant and diff > 0.0:
            winner = ArmWinner.A
        elif significant and diff < 0.0:
            winner = ArmWinner.B
        else:
            winner = ArmWinner.TIE
        if winner is ArmWinner.A:
            self._current = cfg_a
        elif winner is ArmWinner.B:
            self._current = cfg_b
        # TIE：保留原配置（优胜保留语义——无显著优胜不动当前配置）
        self._seq += 1
        result = ABExperimentResult(
            experiment_id=f"exp-{self._seq:04d}",
            arm_a=cfg_a,
            arm_b=cfg_b,
            score_a=score_a,
            score_b=score_b,
            winner=winner,
            significant=significant,
            depth=depth,
            completed_at=self._clock(),
        )
        self._history.append(result)
        _log.info(
            "A/B 实验: %s depth=%d A=%.4f B=%.4f winner=%s significant=%s",
            result.experiment_id,
            depth,
            score_a,
            score_b,
            winner.value,
            significant,
        )
        return result

    # ── 查询 ─────────────────────────────────────────────────────────────

    @property
    def current_config(self) -> LearningConfig:
        """当前优胜保留配置。"""
        return self._current

    @property
    def max_depth(self) -> int:
        """递归深度上限。"""
        return self._max_depth

    def history(self) -> tuple[ABExperimentResult, ...]:
        """实验流水（按 experiment_id 递增顺序，确定性）。"""
        return tuple(self._history)
