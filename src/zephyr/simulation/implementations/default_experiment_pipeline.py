# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain-simulation/experiment-core/blueprint.md
# [MODULE] zephyr.simulation.implementations.default_experiment_pipeline
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.__init__
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
# [A_module] module_id=MOD-L13-001-default_experiment_pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""实验 — Default Experiment Pipeline

实验管线具体实现。实现 ExperimentPipelineBase (OCP 实验-EXP)。

CTR 契约：
  消费者 — CTR-P1-014 (BacktestResult) ← D_RESEARCH
  生产者 — ExperimentResult → D_RESEARCH, D_ML_TRAIN

SSoT: cross_layer_contracts.yaml → CTR-P1-014
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from zephyr.simulation.pipeline_base import (
    ExperimentConfig,
    ExperimentMetric,
    ExperimentPipelineBase,
)

_logger = logging.getLogger(__name__)

__pipeline_id__ = "default-experiment-pipeline"


class DefaultExperimentPipeline(ExperimentPipelineBase):
    """默认实验管线——A/B 对照 + 统计验证"""

    __pipeline_id__ = __pipeline_id__

    def __init__(self):
        self._results_cache: dict[str, list[ExperimentMetric]] = {}

    def run(
        self,
        config: ExperimentConfig,
        idempotency_key: str,
    ) -> list[ExperimentMetric]:
        _logger.info(
            "Experiment started: experiment_id=%s hypothesis=%s",
            config.experiment_id,
            config.hypothesis,
        )

        metrics: list[ExperimentMetric] = []
        for metric_name in config.metrics:
            control_val = float(config.control_params.get(metric_name, 0))
            treatment_val = float(config.treatment_params.get(metric_name, 0))

            effect_size = self.compute_effect_size(
                control_val,
                treatment_val,
                pooled_std=abs(control_val - treatment_val) / 2 or 0.01,
            )

            p_value = self._estimate_p_value(effect_size)

            metric = ExperimentMetric(
                experiment_id=config.experiment_id,
                metric_name=metric_name,
                control_value=control_val,
                treatment_value=treatment_val,
                effect_size=effect_size,
                p_value=p_value,
                is_significant=p_value < 0.05,
                timestamp=datetime.now(UTC),
            )
            metrics.append(metric)

        self._results_cache[config.experiment_id] = metrics
        _logger.info(
            "Experiment completed: experiment_id=%s metrics=%d",
            config.experiment_id,
            len(metrics),
        )
        return metrics

    def get_results(self, experiment_id: str) -> list[ExperimentMetric] | None:
        return self._results_cache.get(experiment_id)

    def _estimate_p_value(self, effect_size: float) -> float:
        """简化 p-value 估计——基于 Cohen's d"""
        abs_d = abs(effect_size)
        if abs_d < 0.2:
            return 0.5
        if abs_d < 0.5:
            return 0.1
        if abs_d < 0.8:
            return 0.01
        return 0.001


__all__ = ["DefaultExperimentPipeline"]
