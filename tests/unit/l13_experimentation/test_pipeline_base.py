"""
单元测试：src/zephyr/l13_experimentation/pipeline_base.py
=============================================================

覆盖矩阵：
  ExperimentPipelineBase (ABC):
    - 抽象类不可实例化 × 1
    - compute_effect_size × 3
    - 注册表登记 × 1
  ScoutAgentBase (ABC):
    - 抽象类不可实例化 × 1
  ExperimentConfig:
    - frozen × 1
    - 默认 status × 1
  ExperimentMetric:
    - 默认 timestamp × 1
"""

from datetime import datetime

import pytest
from zephyr.l13_experimentation.pipeline_base import (
    ExperimentConfig,
    ExperimentMetric,
    ExperimentPipelineBase,
    ScoutAgentBase,
)


class TestExperimentPipelineBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ExperimentPipelineBase()

    def test_compute_effect_size_normal(self):
        assert ExperimentPipelineBase.compute_effect_size(0.1, 0.2, 0.05) == pytest.approx(2.0)

    def test_compute_effect_size_zero_std(self):
        assert ExperimentPipelineBase.compute_effect_size(0.1, 0.2, 0.0) == 0.0

    def test_compute_effect_size_negative(self):
        result = ExperimentPipelineBase.compute_effect_size(0.3, 0.1, 0.1)
        assert result == pytest.approx(-2.0)

    def test_registry_exists(self):
        assert hasattr(ExperimentPipelineBase, "_registry")
        assert isinstance(ExperimentPipelineBase._registry, dict)


class TestScoutAgentBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ScoutAgentBase()


class TestExperimentConfig:
    def test_frozen(self):
        cfg = ExperimentConfig(
            experiment_id="e1",
            hypothesis="h1",
            control_params={},
            treatment_params={},
            metrics=["sharpe"],
            start_date="2025-01-01",
            end_date="2025-12-31",
        )
        with pytest.raises(AttributeError):
            cfg.experiment_id = "e2"

    def test_default_status(self):
        cfg = ExperimentConfig(
            experiment_id="e1",
            hypothesis="h1",
            control_params={},
            treatment_params={},
            metrics=["sharpe"],
            start_date="2025-01-01",
            end_date="2025-12-31",
        )
        assert cfg.status == "registered"


class TestExperimentMetric:
    def test_default_timestamp(self):
        m = ExperimentMetric(
            experiment_id="e1",
            metric_name="sharpe",
            control_value=1.0,
            treatment_value=1.5,
            effect_size=0.5,
            p_value=0.03,
            is_significant=True,
        )
        assert isinstance(m.timestamp, datetime)
