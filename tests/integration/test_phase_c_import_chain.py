# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.integration.test_phase_c_import_chain
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Phase C — Import Chain Validation

验证所有 Phase C concrete class 的 import 路径在工作。
对标 Phase B 的 test_import_chain.py——Phase C 升级版。
"""
from __future__ import annotations

import importlib
from typing import NamedTuple

import pytest


class ConcreteClass(NamedTuple):
    full_name: str
    description: str
    layer: str


PHASE_C_CLASSES: list[ConcreteClass] = [
    ConcreteClass("zephyr.l00_data_source.implementations.akshare_provider", "AkshareProvider", "L00"),
    ConcreteClass("zephyr.l00_data_source.implementations.default_quality_gate", "DefaultQualityGate", "L00"),
    ConcreteClass("zephyr.l03_signal_generation.implementations.default_signal_aggregator", "DefaultSignalAggregator", "L03"),
    ConcreteClass("zephyr.l03_signal_generation.implementations.default_capital_allocator", "DefaultCapitalAllocator", "L03"),
    ConcreteClass("zephyr.l04_risk_management.implementations.default_position_limit_checker", "DefaultPositionLimitChecker", "L04"),
    ConcreteClass("zephyr.l04_risk_management.implementations.default_stop_loss_engine", "DefaultStopLossEngine", "L04"),
    ConcreteClass("zephyr.l04_risk_management.implementations.default_risk_limits_calculator", "DefaultRiskLimitsCalculator", "L04"),
    ConcreteClass("zephyr.l04_risk_management.implementations.default_risk_validator", "DefaultRiskValidator", "L04"),
    ConcreteClass("zephyr.l04_risk_management.implementations.default_risk_manager_orchestrator", "DefaultRiskManagerOrchestrator", "L04"),
    ConcreteClass("zephyr.l05_portfolio_construction.strategies.default_equity_strategy", "DefaultEquityStrategy", "L05"),
    ConcreteClass("zephyr.l06_trade_execution.adapters.simulation_broker", "SimulationBroker", "L06"),
    ConcreteClass("zephyr.l06_trade_execution.order_manager", "OrderManager", "L06"),
    ConcreteClass("zephyr.l06_trade_execution.execution_engine", "ExecutionEngine", "L06"),
    ConcreteClass("zephyr.l07_post_trade_analytics.implementations.default_tca_engine", "DefaultTCAEngine", "L07"),
    ConcreteClass("zephyr.l07_post_trade_analytics.implementations.default_attribution_engine", "DefaultAttributionEngine", "L07"),
    ConcreteClass("zephyr.l09_research_innovation.implementations.default_backtest_engine", "DefaultBacktestEngine", "L09"),
    ConcreteClass("zephyr.l10_compliance.implementations.default_security_gateway", "DefaultSecurityGateway", "L10"),
    ConcreteClass("zephyr.l11_ml_platform.implementations.default_inference_engine", "DefaultInferenceEngine", "L11"),
    ConcreteClass("zephyr.l13_experimentation.implementations.default_experiment_pipeline", "DefaultExperimentPipeline", "L13"),
]

PHASE_E_MODULES: list[ConcreteClass] = [
    ConcreteClass("zephyr.l01_infrastructure.config", "AppConfig/load_config/reload_config", "L01"),
    ConcreteClass("zephyr.l01_infrastructure.kill_switch_sim", "KillSwitchSimulator", "L01"),
    ConcreteClass("zephyr.l01_infrastructure.script_system.finding", "Finding", "L01"),
    ConcreteClass("zephyr.l02_alpha_factor.factor_base", "FactorBase/FactorRegistry/FactorMeta", "L02"),
    ConcreteClass("zephyr.l08_human_ai_interface.interface_base", "DashboardBase/NotificationManagerBase", "L08"),
    ConcreteClass("zephyr.l01_infrastructure.system_telemetry.contract_metrics", "ContractMetricsCollector", "L12"),
]


class TestPhaseCImportChain:
    """验证所有 Phase C concrete class 模块可正常导入"""

    @pytest.mark.parametrize(
        "cc",
        PHASE_C_CLASSES,
        ids=[cc.full_name for cc in PHASE_C_CLASSES],
    )
    def test_module_imports_without_error(self, cc: ConcreteClass) -> None:
        module = importlib.import_module(cc.full_name)
        assert module is not None, f"Failed to import {cc.full_name}"


class TestPhaseEImportChain:
    """验证 Phase E (L01/L02/L08/L12) 模块可正常导入"""

    @pytest.mark.parametrize(
        "cc",
        PHASE_E_MODULES,
        ids=[cc.full_name for cc in PHASE_E_MODULES],
    )
    def test_phase_e_modules_import(self, cc: ConcreteClass) -> None:
        module = importlib.import_module(cc.full_name)
        assert module is not None, f"Failed to import {cc.full_name}"
