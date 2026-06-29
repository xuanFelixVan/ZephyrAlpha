# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md | §6.4
# [MODULE] scripts.migration.cross_domain_import_fix
# [INVARIANTS] 显式映射表(磁盘验证); 最长前缀匹配; 原子写入; 并行
# [MODIFY-GUARD] 域目录结构变更需同步
# [CONSUMERS] TC-6-4 跨域import修复
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无py文件->exit 0
# [TESTS] tests/test_cross_domain_import_fix.py
"""修复跨域 import 引用。

策略:
  1. 使用显式映射表（每条映射已通过磁盘验证）
  2. 最长前缀优先替换
  3. 额外处理 integration.zephyr 嵌套残留

用法:
    python scripts/migration/cross_domain_import_fix.py --dry-run
    python scripts/migration/cross_domain_import_fix.py
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZEPHYR_SRC = PROJECT_ROOT / "src" / "zephyr"

EXCLUDED_DIRS = {"__pycache__", ".git", "integration/mcp_server"}

CROSS_DOMAIN_MAPPINGS: dict[str, str] = {
    "zephyr.orchestration.agent_lifecycle.registry": "zephyr.orchestration.agent_lifecycle.registry",
    "zephyr.governance.audit_trail.contracts": "zephyr.governance.audit_trail.contracts",
    "zephyr.governance.audit_trail.writer": "zephyr.governance.audit_trail.writer",
    "zephyr.governance.audit_trail.bridge": "zephyr.governance.audit_trail.bridge",
    "zephyr.governance.audit_trail.log_rotation": "zephyr.governance.audit_trail.log_rotation",
    "zephyr.governance.audit_trail.retention": "zephyr.governance.audit_trail.retention",
    "zephyr.governance.audit_trail.tiered_storage": "zephyr.governance.audit_trail.tiered_storage",
    "zephyr.shared.models": "zephyr.shared.models",
    "zephyr.infrastructure.shared_services.lifecycle.task_lifecycle_manager": "zephyr.infrastructure.shared_services.lifecycle.task_lifecycle_manager",
    "zephyr.infrastructure.shared_services.queue.task_queue": "zephyr.infrastructure.shared_services.queue.task_queue",
    "zephyr.integration.zephyr.security.mcp_server.event_hook": "zephyr.governance.event_hook",
    "zephyr.security.llm_defense.llm_security.gateway": "zephyr.security.llm_defense.llm_security_01.gateway",
    "zephyr.security.llm_defense.llm_security.input_sanitizer": "zephyr.security.llm_defense.llm_security_01.input_sanitizer",
    "zephyr.security.llm_defense.llm_security.patterns.secrets": "zephyr.security.llm_defense.llm_security_01.patterns.secrets",
    "zephyr.ops.system_telemetry.compliance_rule": "zephyr.portfolio.core.compliance_rule",
    "zephyr.ops.system_telemetry.synthesized_signal": "zephyr.execution.trading.trading_contracts.market.synthesized_signal",
    "zephyr.ops.system_telemetry.capital_allocation_result": "zephyr.execution.trading.trading_contracts.execution.capital_allocation_result",
    "zephyr.ops.system_telemetry.risk_limits": "zephyr.risk.risk_limits",
    "zephyr.risk.risk_manager": "zephyr.risk.risk_manager",
    "zephyr.risk.risk_manager_base": "zephyr.risk.risk_manager_base",
    "zephyr.governance.audit_trail.text_to_finding_adapter": "zephyr.governance.audit_orchestrator.text_to_finding_adapter",
    "zephyr.governance.audit_trail.integrity": "zephyr.governance.integrity",
    "zephyr.governance.audit_trail.merkle_hourly": "zephyr.governance.merkle_hourly",
    "zephyr.governance.audit_trail.evidence_pack": "zephyr.governance.evidence_pack",
    "zephyr.signal.capital_allocator": "zephyr.signal.capital_allocator",
    "zephyr.signal.implementations.default_signal_aggregator": "zephyr.signal.implementations.default_signal_aggregator",
    "zephyr.signal.implementations.default_capital_allocator": "zephyr.signal.implementations.default_capital_allocator",
    "zephyr.ml_serve.serving_orchestrator.inference_base": "zephyr.intelligence.inference_base",
    "zephyr.infrastructure.runtime_integration.auto_fix_engine": "zephyr.security.access_control.auto_fix_engine_03",
    "zephyr.resilience.budget_enforcement": "zephyr.resilience.budget_enforcement",
    "zephyr.infrastructure.runtime_integration.pipeline": "zephyr.orchestration.pipeline_routing",
    "zephyr.infra_ops.a2a_protocol.a2a_card_registry": "zephyr.infrastructure.runtime_integration.a2a_protocol.a2a_card_registry",
    "zephyr.infra_ops.a2a_protocol.layer3_coordination.a2a_protocol_gateway": "zephyr.infrastructure.runtime_integration.a2a_protocol.layer3_coordination.a2a_protocol_gateway",
    "zephyr.infra_ops.code_dedup_engine.scanner": "zephyr.testing.code_dedup.scanner",
    "zephyr.infra_ops.system_telemetry.metrics_bridge": "zephyr.infrastructure.runtime_integration.system_telemetry.metrics_bridge",
    "zephyr.integration.local_model.embedding_router": "zephyr.integration.local_model.embedding_router",
    "zephyr.governance.audit_trail.self_monitor": "zephyr.governance.audit_trail.self_monitor",
    "zephyr.governance.audit_trail.models": "zephyr.governance.audit_orchestrator.models",
    "zephyr.governance.audit_trail.query": "zephyr.governance.audit_trail.query",
    "zephyr.infrastructure.shared_services.lifecycle.daemon_registry": "zephyr.infrastructure.shared_services.lifecycle.daemon_registry",
    "zephyr.shared.blueprint_decomposer": "zephyr.shared.blueprint_decomposer",
    "zephyr.infrastructure.shared_services.session_continuity": "zephyr.infrastructure.shared_services.session_continuity",
    "zephyr.infra_ops.system_telemetry.facade": "zephyr.infrastructure.runtime_integration.system_telemetry.facade",
    "zephyr.infra_ops.system_telemetry.auto_bootstrap": "zephyr.infrastructure.runtime_integration.system_telemetry.auto_bootstrap",
    "zephyr.integration.zephyr.integration.mcp_server.event_hook": "zephyr.governance.event_hook",
    "zephyr.integration.zephyr.autonomy_core.pipeline_base": "zephyr.research.simulation.pipeline_base",
    "zephyr.governance.behavioral_admission.admission_controller": "zephyr.orchestration.runtime_core.admission_controller",
    "zephyr.infrastructure.runtime_integration.db.task_repo": "zephyr.data.persistence.task_repo",
    "zephyr.infrastructure.runtime_integration.db.sqlite_schema": "zephyr.data.persistence.sqlite_schema",
    "zephyr.observability.feedback_loop.fitness_functions": "zephyr.observability.feedback_loop.fitness_functions",
    "zephyr.security.llm_defense.llm_security.self_protection.red_team_scanner": "zephyr.security.llm_defense.llm_security_01.self_protection.red_team_scanner",
    "zephyr.ops.system_telemetry.file_utils": "zephyr.shared.file_utils",
    "zephyr.integration.observability.session_audit": "zephyr.infrastructure.shared_services.observability_02.session_audit",
    "zephyr.ops.system_telemetry.market_data": "zephyr.execution.trading.trading_contracts.market.market_data",
    "zephyr.ops.system_telemetry.instrument": "zephyr.data.instrument",
    "zephyr.portfolio.core.money": "zephyr.execution.trading.trading_contracts.portfolio.contracts.money",
    "zephyr.portfolio.core.strategy_lifecycle_event": "zephyr.execution.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event",
    "zephyr.governance.rule_enforcement.check_type_registry": "zephyr.governance.rule_enforcement.check_types.check_type_registry",
    "zephyr.infra_ops.system_telemetry": "zephyr.infrastructure.runtime_integration.system_telemetry",
    "zephyr.infra_ops.a2a_protocol": "zephyr.infrastructure.runtime_integration.a2a_protocol",
    "zephyr.ops.system_telemetry.errors": "zephyr.shared.errors",
    "zephyr.infrastructure.runtime_integration.infra.resource_optimization_engine": "zephyr.infrastructure.shared_services.lifecycle.resource_optimization_engine",
    "zephyr.infrastructure.runtime_integration.infra.resource_optimization_models": "zephyr.infrastructure.shared_services.lifecycle.resource_optimization_models",
    "zephyr.integration.pipeline.backpressure_bridge": "zephyr.observability.feedback_loop.backpressure_bridge",
    "zephyr.ops.feedback_loop.conformal_prediction": "zephyr.observability.feedback_loop.evolution.conformal_prediction",
    "zephyr.intelligence.inference_base": "zephyr.intelligence.inference_base",
    "zephyr.ml_serve.llm_gateway": "zephyr.orchestration.pipeline_routing.llm_gateway",
    "zephyr.integration.zephyr.ml_experiment_pipeline": "zephyr.risk.cross_asset.cross_market_data_adapter.ml_experiment_pipeline",
    "zephyr.ops.feedback_loop.auto_reward": "zephyr.observability.feedback_loop.evolution.auto_reward",
    "zephyr.ops.feedback_loop.self_bottleneck_detector": "zephyr.observability.feedback_loop.diagnosers.self_bottleneck_detector",
    "zephyr.ops.system_telemetry.context": "zephyr.shared.utils.context",
    "zephyr.governance.drift_detection.drift_infrastructure": "zephyr.behavioral_audit.drift_infrastructure",
    "zephyr.infra_ops.code_dedup_engine": "zephyr.testing.code_dedup",
    "zephyr.integration.errors.capability_card": "zephyr.orchestration.runtime_core.capability_card",
    "zephyr.integration.errors.capability_registry": "zephyr.orchestration.runtime_core.capability_registry",
    "zephyr.ops.feedback_loop.cold_start_manual": "zephyr.observability.feedback_loop.docs.cold_start_manual",
    "zephyr.integration.a2a_protocol.a2a_schemas": "zephyr.infrastructure.runtime_integration.a2a_protocol.layer2_communication.a2a_schemas",
    "zephyr.integration.a2a_protocol.a2a_state": "zephyr.infrastructure.runtime_integration.a2a_protocol.layer2_communication.a2a_state",
    "zephyr.integration.a2a_protocol.agent_card": "zephyr.infrastructure.runtime_integration.a2a_protocol.layer1_discovery.agent_card",
    "zephyr.orchestration.runtime_core.drift_hotfix_bypass": "zephyr.behavioral_audit.drift_hotfix_bypass",
    "zephyr.ops.feedback_loop.dynamic_threshold": "zephyr.observability.feedback_loop.evolution.dynamic_threshold",
    "zephyr.ops.feedback_loop.self_api_throttle_defense": "zephyr.observability.feedback_loop.resilience.self_api_throttle_defense",
    "zephyr.ops.feedback_loop.graceful_degradation_planner": "zephyr.observability.feedback_loop.resilience.graceful_degradation_planner",
    "zephyr.security.llm_defense.llm_security.artifact_scanner": "zephyr.governance.artifact_scanner",
    "zephyr.orchestration.runtime_core.chaos_injector": "zephyr.behavioral_audit.chaos_injector",
    "zephyr.data.protocols": "zephyr.observability.feedback_loop.protocols",
    "zephyr.orchestration.runtime_core.self_test_verifier": "zephyr.behavioral_audit.self_test_verifier",
    "zephyr.governance.rule_enforcement.en_process_lifecycle_gateway": "zephyr.governance.rule_enforcement.invariants.en_process_lifecycle_gateway",
    "zephyr.governance.audit_trail": "zephyr.governance.audit_trail",
    "zephyr.security.access_control": "zephyr.security.access_control",
    "zephyr.integration.zephyr.benchmark_suite": "zephyr.intelligence.model_profiling.benchmark_suite",
    "zephyr.integration.zephyr.capability_passport": "zephyr.intelligence.model_profiling.capability_passport",
    "zephyr.integration.zephyr.cli": "zephyr.intelligence.model_profiling.cli",
    "zephyr.integration.zephyr.deepseek_v4_chat": "zephyr.intelligence.model_profiling.deepseek_v4_chat",
    "zephyr.integration.zephyr.event_hook": "zephyr.governance.event_hook",
    "zephyr.integration.zephyr.exam_orchestrator": "zephyr.intelligence.model_profiling.exam_orchestrator",
    "zephyr.integration.zephyr.exam_test_cases": "zephyr.intelligence.model_profiling.exam_test_cases",
    "zephyr.integration.zephyr.integration.mcp_result_push": "zephyr.governance.mcp_result_push",
    "zephyr.integration.zephyr.model_discovery": "zephyr.intelligence.model_profiling.model_discovery",
    "zephyr.integration.zephyr.infrastructure.runtime_integration.pipeline_base": "zephyr.research.simulation.pipeline_base",
    "zephyr.integration.zephyr.profiler": "zephyr.intelligence.model_profiling.profiler",
    "zephyr.integration.zephyr.provider_data": "zephyr.intelligence.model_profiling.provider_data",
    "zephyr.integration.zephyr.results_writer": "zephyr.intelligence.model_profiling.results_writer",
    "zephyr.integration.zephyr.task_model_learner": "zephyr.intelligence.model_profiling.task_model_learner",
    "zephyr.ops.system_telemetry.order": "zephyr.execution.trading.trading_contracts.execution.order",
    "zephyr.ops.system_telemetry.fill": "zephyr.execution.trading.trading_contracts.execution.fill",
    "zephyr.ops.system_telemetry.factor_signal": "zephyr.execution.trading.trading_contracts.market.factor_signal",
    "zephyr.ops.system_telemetry.position": "zephyr.execution.trading.trading_contracts.execution.position",
    "zephyr.ops.system_telemetry.execution_report": "zephyr.execution.trading.trading_contracts.execution.execution_report",
    "zephyr.ops.system_telemetry.risk_dashboard_snapshot": "zephyr.execution.trading.trading_contracts.risk.risk_dashboard_snapshot",
    "zephyr.ops.system_telemetry.risk_metrics": "zephyr.execution.trading.trading_contracts.risk.risk_metrics",
    "zephyr.signal.aggregator_base": "zephyr.signal.aggregator_base",
    "zephyr.signal.signal_synthesizer": "zephyr.signal.signal_synthesizer",
    "zephyr.governance.admission_response": "zephyr.integration.behavioral_admission.admission_response",
    "zephyr.governance.rule_enforcement.gate_engine": "zephyr.governance.rule_enforcement.gate_engine",
    "zephyr.data.knowledge_management.kb.unified_memory_api": "zephyr.research.unified_memory_api",
    "zephyr.data.knowledge_management.vector_memory.local_model_scheduler": "zephyr.integration.local_model.local_model_scheduler",
    "zephyr.ops.system_telemetry.risk_limit_violation_error": "zephyr.execution.trading.trading_contracts.risk.risk_limit_violation_error",
    "zephyr.ops.system_telemetry.model_serving_request": "zephyr.execution.trading.trading_contracts.execution.model_serving_request",
    "zephyr.data.knowledge_management.vector_memory.vector_bridge": "zephyr.orchestration.context_management.vector_bridge",
    "zephyr.data.knowledge_management.kb.kb_repo": "zephyr.research.kb_repo",
    "zephyr.governance.phase_check_registry": "zephyr.resilience.rollback.phase_check_registry",
    "zephyr.risk.risk_validator": "zephyr.risk.risk_validator",
    "zephyr.security.llm_defense.llm_security_01.protocol": "zephyr.infrastructure.runtime_integration.a2a_protocol.governance.protocol",
    "zephyr.data.knowledge_management.kb.reranker": "zephyr.research.reranker",
    "zephyr.data.knowledge_management.kb.sync_engine": "zephyr.research.sync_engine",
    "zephyr.research.kb_repo": "zephyr.research.kb_repo",
    "zephyr.alt_data.kb.graph_validator": "zephyr.alt_data.kb.graph_validator",
    "zephyr.research.unified_memory_api": "zephyr.research.unified_memory_api",
    "zephyr.data.knowledge_management.kb.ingest": "zephyr.data.storage.ingest",
    "zephyr.observability.audit_trail.integrity": "zephyr.governance.integrity",
    "zephyr.observability.audit_trail.merkle_hourly": "zephyr.governance.merkle_hourly",
    "zephyr.risk.default_position_limit_checker": "zephyr.risk.implementations.default_position_limit_checker",
    "zephyr.risk.default_stop_loss_engine": "zephyr.risk.implementations.default_stop_loss_engine",
    "zephyr.risk.default_risk_limits_calculator": "zephyr.risk.implementations.default_risk_limits_calculator",
    "zephyr.risk.default_risk_validator": "zephyr.risk.implementations.default_risk_validator",
    "zephyr.risk.default_risk_manager_orchestrator": "zephyr.risk.implementations.default_risk_manager_orchestrator",
    "zephyr.security.agent_rbac.security_decision": "zephyr.shared.contracts.security.security_decision",
    "zephyr.observability.audit_trail.bridges.contracts": "zephyr.resilience.rollback.contracts",
    "zephyr.observability.audit_trail.bridges.anomaly": "zephyr.governance.audit_orchestrator.anomaly",
    "zephyr.security.llm_defense.llm_security.security_gateway_base": "zephyr.governance.security_gateway_base",
    "zephyr.security.llm_defense.llm_security.context_scanner": "zephyr.security.llm_defense.llm_security_01.context_scanner",
    "zephyr.security.llm_defense.llm_security.aisg_sandbox": "zephyr.governance.aisg_sandbox",
    "zephyr.security.llm_defense.llm_security.default_security_gateway": "zephyr.governance.default_security_gateway",
    "zephyr.governance.rule_enforcement.phase_check_registry": "zephyr.resilience.rollback.phase_check_registry",
}


def _verify_mappings() -> list[str]:
    errors: list[str] = []
    for old_mod, new_mod in CROSS_DOMAIN_MAPPINGS.items():
        new_parts = new_mod.split(".")
        rel_path = "/".join(new_parts[1:]) + ".py"
        init_path = "/".join(new_parts[1:]) + "/__init__.py"
        if (ZEPHYR_SRC / rel_path).exists() or (ZEPHYR_SRC / init_path).exists():
            continue
        errors.append(f"{old_mod} -> {new_mod} (target not found: {rel_path})")
    return errors


def _build_prefix_mapping(module_mapping: dict[str, str]) -> list[tuple[str, str]]:
    items = sorted(module_mapping.items(), key=lambda x: len(x[0]), reverse=True)
    return items


def _replace_imports_in_content(content: str, prefix_map: list[tuple[str, str]]) -> tuple[str, int]:
    changes = 0
    for old_mod, new_mod in prefix_map:
        if old_mod not in content:
            continue
        count = content.count(old_mod)
        if count > 0:
            content = content.replace(old_mod, new_mod)
            changes += count
    return content, changes


def _process_file(filepath: Path, prefix_map: list[tuple[str, str]], dry_run: bool = False) -> dict:
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
    for exc in EXCLUDED_DIRS:
        if exc in rel:
            return {"file": rel, "status": "excluded", "changes": 0}

    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"file": rel, "status": "read_error", "changes": 0}

    new_content, changes = _replace_imports_in_content(content, prefix_map)

    if changes == 0:
        return {"file": rel, "status": "no_change", "changes": 0}

    if dry_run:
        return {"file": rel, "status": "would_update", "changes": changes}

    tmp_path = f"{filepath}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(new_content, encoding="utf-8")
        os.replace(tmp_path, filepath)
        return {"file": rel, "status": "updated", "changes": changes}
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": rel, "status": "write_error", "changes": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix cross-domain import references")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual changes")
    args = parser.parse_args()

    print("=== Cross-Domain Import Fix ===")
    if args.dry_run:
        print("(dry-run mode)")

    print("\nStep 1: Verifying mappings against disk...")
    errors = _verify_mappings()
    if errors:
        print(f"  [ERROR] {len(errors)} mappings have invalid targets:")
        for e in errors:
            print(f"    {e}")
        sys.exit(1)
    print(f"  All {len(CROSS_DOMAIN_MAPPINGS)} mappings verified OK")

    print("\nStep 2: Mappings to apply:")
    for old_mod, new_mod in sorted(CROSS_DOMAIN_MAPPINGS.items()):
        print(f"  {old_mod} -> {new_mod}")

    prefix_map = _build_prefix_mapping(CROSS_DOMAIN_MAPPINGS)

    print("\nStep 3: Scanning .py files for replacements...")
    py_files: list[Path] = []
    scan_dirs = [ZEPHYR_SRC, PROJECT_ROOT / "frontend", PROJECT_ROOT / "tests"]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob("*.py"):
            if f.is_file() and "__pycache__" not in str(f):
                rel_str = str(f.relative_to(scan_dir)).replace("\\", "/")
                skip = False
                for exc in EXCLUDED_DIRS:
                    if exc in rel_str:
                        skip = True
                        break
                if not skip:
                    py_files.append(f)

    print(f"  Scanning {len(py_files)} .py files...")

    total_updated = 0
    total_changes = 0
    total_errors = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_process_file, f, prefix_map, args.dry_run): f for f in py_files}
        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                total_updated += 1
                total_changes += result["changes"]
            elif result["status"] == "write_error":
                total_errors += 1
                print(f"  ERROR: {result['file']}")

    print("\n=== Results ===")
    print(f"  Files updated: {total_updated}")
    print(f"  Import changes: {total_changes}")
    print(f"  Errors: {total_errors}")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
