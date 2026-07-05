# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain-simulation/experiment-core/blueprint.md
# [MODULE] zephyr.simulation.pipeline_base
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.contracts.experiment_result
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L13-001-pipeline_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
实验 — Experimentation Pipeline Layer

实验管线层。负责实验设计、参数搜索、A/B 测试和结果分析。

核心职责：
  - 实验注册与管理（experiment_id / hypothesis / parameters）
  - Scout Agent 自动化实验（外部资讯 + repo diff → 对照实验 → 结论沉淀到 KMS）
  - 参数网格搜索与贝叶斯优化
  - 实验结果统计验证（p-value / effect size / power analysis）
  - 胜出策略自动提升至 D_PORTFOLIO_CORE / D_RESEARCH

扩展点：
  - ExperimentPipelineBase : OCP 实验-EXP — 实验配置 → 实验指标
  - ScoutAgentBase         : OCP 实验-SCT — 自动化实验编排（CTR-P1-014 生产者）

依赖方向：D_RESEARCH → 实验 → D_PORTFOLIO_CORE / D_SIGNAL（实验结果提升至生产管线）
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from zephyr.shared.contracts.experiment_result import ExperimentResult


def _utcnow() -> datetime:
    """当前 UTC 时间（替代已废弃的 datetime.utcnow）"""
    return datetime.now(UTC)


@dataclass(frozen=True)
class ExperimentConfig:
    """实验配置"""

    experiment_id: str
    hypothesis: str
    control_params: dict[str, Any]
    treatment_params: dict[str, Any]
    metrics: list[str]
    start_date: str
    end_date: str
    status: str = "registered"


@dataclass(frozen=True)
class ExperimentMetric:
    """单指标实验结果统计（内部中间产物）"""

    experiment_id: str
    metric_name: str
    control_value: float
    treatment_value: float
    effect_size: float
    p_value: float
    is_significant: bool
    timestamp: datetime = field(default_factory=_utcnow)


class ExperimentPipelineBase(abc.ABC):
    """
    实验管线基类（OCP 扩展点 实验-EXP）

    实现者要求：
      - run(): 接收实验配置，返回统计指标结果列表
      - 支持 A/B 分组与 p-value / effect_size 计算
      - 最终实验结论通过 ScoutAgent 汇总为 ExperimentResult
    """

    @abc.abstractmethod
    def run(self, config: ExperimentConfig, idempotency_key: str) -> list[ExperimentMetric]:
        """执行实验，返回各指标的统计结果"""
        ...

    @staticmethod
    def compute_effect_size(control: float, treatment: float, pooled_std: float) -> float:
        """Cohen's d 效应量计算"""
        if abs(pooled_std) < 1e-9:  # 5.167.6 修复: 浮点==0比较改 < epsilon (行号漂移 95→98)
            return 0.0
        return (treatment - control) / pooled_std


class ScoutAgentBase(abc.ABC):
    """
    Scout Agent 自动化实验编排器（OCP 扩展点 实验-SCT）

    契约对齐：CTR-P1-014（ExperimentResult 出站）→ D_RESEARCH, D_ML_TRAIN

    实现者要求：
      - scout(): 自动抓取外部资讯 + 内部 repo diff，设计并执行对照实验
      - 每个实验周期结束后产出 ExperimentResult
      - conclusion 状态：supported | rejected | inconclusive
      - confidence < 0.7 的结论不应发布（D_RESEARCH/D_ML_TRAIN 消费端应忽略）
      - 已确认结论 archived_to_kms = True，写入 KMS 知识管道
    """

    @abc.abstractmethod
    def scout(self, context: dict[str, Any], idempotency_key: str) -> ExperimentResult:
        """自动化实验编排：扫码外部信息 → 设计实验 → 执行 → 产出结论"""
        ...

    @abc.abstractmethod
    def archive_to_kms(self, result: ExperimentResult) -> bool:
        """将确认的实验结论归档到 KMS 知识管道"""
        ...


__all__ = [
    "ExperimentConfig",
    "ExperimentMetric",
    "ExperimentPipelineBase",
    "ScoutAgentBase",
]
