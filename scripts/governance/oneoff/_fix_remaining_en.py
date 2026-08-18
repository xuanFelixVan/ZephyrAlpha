# [BLUEPRINT] MOD-GOV_FIX_REM_EN | scripts/governance/oneoff/_fix_remaining_en.py | §
# [MODULE] scripts.governance.oneoff._fix_remaining_en
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pathlib; re
# [CONSUMERS] 一次性修复脚本，修复后归档
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只修改name_zh行;保留原YAML格式;精确映射module_path→中文
# [TTL] task_bound
# noqa: m11-perm-manual-legitimate  一次性修复脚本，task_bound 已执行完毕待退役清理
"""补全剩余 65 条英文条目的中文翻译——直接映射 module_path → 中文名。"""

__manifest__ = """
args: []
description: 补全剩余 65 条英文条目的中文翻译——直接映射 module_path → 中文名。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
from pathlib import Path

_YAML = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "module_translation_registry.yaml"
)

# module_path → 中文名（人工翻译，覆盖词典长尾缺失词）
_TRANSLATIONS: dict[str, str] = {
    "test_trigger_A.py": "测试触发器A",
    "test_trigger_B.py": "测试触发器B",
    "src/zephyr/security/adversarial_validation/cli.py": "对抗验证CLI",
    "src/zephyr/shared/contracts/backpressure/resume.py": "恢复",
    "src/zephyr/ex_core/microstructure_modeler.py": "微观结构建模器",
    "src/zephyr/shared/protocols/a2a/a2a_schemas.py": "A2A模式定义",
    "src/zephyr/trading/trading_contracts/portfolio/contracts/money.py": "货币契约",
    "src/zephyr/gov_drift/_analysis.py": "分析",
    "src/zephyr/gov_drift/_scanners.py": "扫描器",
    "src/zephyr/gov_drift/__main__.py": "主入口",
    "src/zephyr/infrastructure/auto_fix_engine/__main__.py": "主入口",
    "src/zephyr/infrastructure/capacity_assurance/kill_switch.py": "熔断开关",
    "src/zephyr/infrastructure/runtime/startup_shutdown.py": "启动关闭",
    "src/zephyr/infrastructure/script_system/finding.py": "发现",
    "src/zephyr/integration/ports.py": "端口",
    "src/zephyr/integration/vector_memory/design_principles.py": "设计原则",
    "src/zephyr/integration/vector_memory/hybrid_retriever.py": "混合检索器",
    "src/zephyr/integration/vector_memory/migrate_chroma_to_faiss.py": "Chroma到FAISS迁移",
    "src/zephyr/integration/vector_memory/vms_errors.py": "VMS错误",
    "src/zephyr/integration/vector_memory/vms_schemas.py": "VMS模式定义",
    "src/zephyr/intelligence/model_evaluation/reranker.py": "重排器",
    "src/zephyr/intelligence/model_profiling/cli.py": "模型分析CLI",
    "src/zephyr/intelligence/model_profiling/pipeline_routing/cli.py": "管道路由CLI",
    "src/zephyr/security/access_control/orphan_judge/swid_tag.py": "SWID标签",
    "src/zephyr/security/access_control/orphan_judge/__main__.py": "主入口",
    "src/zephyr/security/adversarial_validation/blast_radius.py": "影响半径",
    "src/zephyr/security/adversarial_validation/mcp_endpoints.py": "MCP端点",
    "src/zephyr/security/adversarial_validation/__main__.py": "主入口",
    "src/zephyr/security/llm_defense/llm_security/input_sanitizer.py": "输入净化器",
    "src/zephyr/security/llm_defense/llm_security/dashboard/app.py": "仪表盘应用",
    "src/zephyr/security/llm_defense/llm_security/layers/l6_observability.py": "L6可观测性",
    "src/zephyr/security/llm_defense/llm_security/patterns/secrets.py": "密钥模式",
    "src/zephyr/shared/alerts/alert_escalation.py": "告警升级",
    "src/zephyr/shared/api/dos_launcher.py": "DoS启动器",
    "src/zephyr/shared/contracts/protocols.py": "协议",
    "src/zephyr/shared/contracts/orchestration_protocol.py": "编排协议",
    "src/zephyr/shared/contracts/backpressure/throttle.py": "限流",
    "src/zephyr/shared/contracts/backpressure/pause.py": "暂停",
    "src/zephyr/shared/contracts/external/ext_001.py": "外部契约001",
    "src/zephyr/shared/contracts/execution/fill.py": "成交",
    "src/zephyr/shared/contracts/external/ext_002.py": "外部契约002",
    "src/zephyr/shared/contracts/external/ext_003.py": "外部契约003",
    "src/zephyr/shared/contracts/identity/permission.py": "权限",
    "src/zephyr/shared/contracts/external/ext_004.py": "外部契约004",
    "src/zephyr/shared/contracts/market/instrument.py": "标的契约",
    "src/zephyr/shared/contracts/portfolio/money.py": "货币契约",
    "src/zephyr/shared/evaluation/evals.py": "评估",
    "src/zephyr/shared/infra/observer.py": "观察者",
    "src/zephyr/shared/io/content_fingerprint.py": "内容指纹",
    "src/zephyr/shared/lifecycle/health.py": "健康检查",
    "src/zephyr/shared/maintenance/handbook.py": "维护手册",
    "src/zephyr/shared/maintenance/slo_review_assistant.py": "SLO审查助手",
    "src/zephyr/shared/maintenance/owner_trust_gauge.py": "Owner信任度评估",
    "src/zephyr/shared/observability/reasoning_spans.py": "推理链路",
    "src/zephyr/shared/protocols/a2a/a2a_coordination.py": "A2A协调",
    "src/zephyr/shared/protocols/a2a/a2a_protocol.py": "A2A协议",
    "src/zephyr/shared/resilience/fault_isolator.py": "故障隔离器",
    "src/zephyr/shared/schema/schemas.py": "模式定义",
    "src/zephyr/shared/security/secrets.py": "密钥",
    "src/zephyr/shared/utils/cli_summary.py": "CLI摘要",
    "src/zephyr/trading/ports.py": "端口",
    "src/zephyr/trading/staging_area.py": "暂存区",
    "src/zephyr/trading/work_dag.py": "工作DAG",
    "src/zephyr/trading/trading_contracts/market/instrument.py": "标的契约",
    "tests/data/test_source_health_check.py": "数据源健康检查测试",
}


def main():
    """Entry point: parse args, run logic, return exit code."""
    with open(_YAML, encoding="utf-8") as f:
        lines = f.readlines()

    current_mp: str | None = None
    new_lines: list[str] = []
    replaced = 0

    for line in lines:
        mp_m = re.match(r"^- module_path:\s*(.+?)\s*$", line)
        if mp_m:
            current_mp = mp_m.group(1).strip()
        elif re.match(r"^  module_path:\s*(.+?)\s*$", line):
            current_mp = re.match(r"^  module_path:\s*(.+?)\s*$", line).group(1).strip()

        zh_m = re.match(r"^(  name_zh:)\s*(.*)$", line)
        if zh_m and current_mp and current_mp in _TRANSLATIONS:
            new_val = _TRANSLATIONS[current_mp]
            special = any(
                c in new_val for c in [":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">", "'", '"', "%", "@"]
            )
            if special:
                new_lines.append(f'{zh_m.group(1)} "{new_val}"\n')
            else:
                new_lines.append(f"{zh_m.group(1)} {new_val}\n")
            replaced += 1
            continue
        new_lines.append(line)

    with open(_YAML, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Replaced {replaced} entries in YAML")


if __name__ == "__main__":
    main()
