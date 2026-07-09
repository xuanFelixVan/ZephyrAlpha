# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/sync_blueprint_code_index.py | §
# [MODULE] scripts.governance.d5_architecture.syncers.sync_blueprint_code_index
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.syncers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""


对标：AGENTS.md §6.1 蓝图-代码同步强制约定
      validate_blueprint_code_sync.py（验证端）的修复端——验证查问题，同步修问题

功能：
  1. 扫描所有蓝图，为缺少「已实现代码完整路径索引」章节的蓝图自动补齐
  2. 更新蓝图 frontmatter version（patch +1）
  3. 检测蓝图 §19 中声称的幽灵路径并标记

用法：
  python scripts/governance/d5_architecture/sync_blueprint_code_index.py          # 实际写入
  python scripts/governance/d5_architecture/sync_blueprint_code_index.py --check  # 只检查漂移（CI 模式）
"""

from __future__ import annotations

import os

__manifest__ = """
args: []
description: SYNC-BLUEPRINT-CODE — 蓝图§19已实现代码路径索引自动同步（AGENTS.md §6.1 — 为缺少路径索引的蓝图自动补齐+version
  patch+1，--check模式仅检测漂移）
dimensions:
- D5
- D8
priority: P1
timeout_seconds: 60
warn_only: false
"""

import re
import sys
from argparse import ArgumentParser
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

BLUEPRINT_GLOBS = [
    "docs/03_modules/*/blueprint.md",
    "docs/03_modules/*/*/blueprint.md",
]

SECTION_PATTERN = re.compile(
    r"^##\s+\d+\.\s+已实现代码完整路径索引",
    re.MULTILINE,
)

PATH_IN_TABLE_PATTERN = re.compile(r"`([^`]+\.(?:py|yaml|yml|json|toml))`")
PATH_MUST_HAVE_DIR = re.compile(r"[/\\]")

BLUEPRINT_MODULE_MAP: dict[str, dict] = {
    "_master-blueprint": {
        "module_id": "MOD-MASTER_BLUEPRINT",
        "source_dirs": [],
        "extra_source_files": [],
        "test_patterns": [],
        "config_files": [],
        "governance_scripts": [],
        "note": "总蓝图不产生代码，仅定义集成契约",
    },
    "capacity-assurance": {
        "module_id": "MOD-INF-001",
        "source_dirs": [],
        "extra_source_files": [],
        "test_patterns": [],
        "config_files": [],
        "governance_scripts": [
            "scripts/governance/d5_architecture/validate_ssot.py",
            "scripts/governance/d3_metadata/validate_blueprint_provenance.py",
        ],
        "note": "容量保障——蓝图含代码骨架但尚无实际运行代码模块",
    },
    "code-dedup-engine": {
        "module_id": "MOD-INF-017",
        "source_dirs": [],
        "extra_source_files": [],
        "test_patterns": [],
        "config_files": [],
        "governance_scripts": [],
        "note": "代码去重引擎——蓝图已创建但尚无代码实现",
    },
    "context-engine": {
        "module_id": "MOD-CONTEXT_ENGINE",
        "source_dirs": ["src/zephyr/context-engine"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/test_context_injector.py",
            "tests/test_doc_compressor.py",
            "tests/test_prompt_registry.py",
            "tests/test_intent_parser.py",
            "tests/test_intent_keyword_mapper.py",
            "tests/test_pattern_library.py",
            "tests/test_system_snapshot.py",
        ],
        "config_files": [
            "config/context_rules.yaml",
            "config/compression_policy.yaml",
        ],
        "governance_scripts": [],
        "note": "上下文引擎——9文件骨架+assembler+injector已实现",
    },
    "database": {
        "module_id": "MOD-DATABASE",
        "source_dirs": ["src/zephyr/db"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/test_task_repo.py",
            "tests/test_sqlite_schema.py",
            "tests/test_atomic_transaction_manager.py",
            "tests/test_olap_engine.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "数据库——task_repo+sqlite_schema+ATM已实现，olap_engine待施工",
    },
    "feedback-loop": {
        "module_id": "MOD-FEEDBACK_LOOP",
        "source_dirs": ["src/zephyr/feedback-loop"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/feedback/test_metrics_collector.py",
            "tests/test_fitness_functions.py",
            "tests/test_feedback_collector.py",
            "tests/test_auto_evolution.py",
            "tests/test_evolution_engine.py",
            "tests/test_eval_harness.py",
            "tests/integration/test_evolution_e2e.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "反馈闭环——6文件骨架+metrics_collector+fitness_functions已实现",
    },
    "gate-engine": {
        "module_id": "MOD-GATE_ENGINE",
        "source_dirs": ["src/zephyr/governance/rule_enforcement"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/test_gate_engine.py",
            "tests/test_task_completion_gate.py",
            "tests/safety/test_circuit_breaker.py",
            "tests/test_contract_template_manager.py",
            "tests/integration/test_gate_e2e.py",
        ],
        "config_files": [],
        "governance_scripts": [
            "scripts/governance/d6_security/validate_gate_discipline.py",
        ],
        "note": "门禁引擎——gate_engine.py+5个KMS YAML门禁已实现",
    },
    "knowledge-base": {
        "module_id": "MOD-KB-001",
        "source_dirs": ["src/zephyr/kb"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/test_ingest.py",
            "tests/test_triage.py",
            "tests/test_analyze.py",
            "tests/test_activate.py",
            "tests/test_extract.py",
            "tests/test_batch_ingest.py",
            "tests/test_kb_repo.py",
            "tests/test_graph_validator.py",
            "tests/test_unified_memory_api.py",
            "tests/test_embedding_migrate.py",
            "tests/test_knowledge_activation_rate.py",
        ],
        "config_files": [
            "config/embedding_model_registry.yaml",
        ],
        "governance_scripts": [],
        "note": "知识库——API骨架已实现，G1-G5门禁待beta",
    },
    "llm-security": {
        "module_id": "MOD-LLM_SECURITY",
        "source_dirs": ["src/zephyr/llm-security"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/test_input_sanitizer.py",
            "tests/test_process_sandbox.py",
            "tests/test_ai_behavior_audit_logger.py",
            "tests/test_hallucination_interception.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "LLM安全网关——3文件骨架+input_sanitizer已实现",
    },
    "mcp-servers": {
        "module_id": "MOD-INF-013",
        "source_dirs": ["src/zephyr/mcp"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/infrastructure/test_mcp_servers.py",
            "tests/integration/test_mcp_e2e.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "MCP服务器——task_manager decompose_blueprint已实现",
    },
    "pipeline": {
        "module_id": "MOD-INF-009",
        "source_dirs": ["src/zephyr/pipeline"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/pipeline/test_pipeline_orchestrator.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "任务管线——pipeline_orchestrator+models骨架完成",
    },
    "runtime-integration": {
        "module_id": "MOD-INF-002",
        "source_dirs": ["src/zephyr/orchestrator"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/orchestrator/test_agent_orchestrator.py",
            "tests/test_agent_health_monitor.py",
            "tests/test_hallucination_detector.py",
            "tests/test_rollback_manager.py",
            "tests/test_state_synchronizer.py",
            "tests/test_trigger_router.py",
            "tests/test_file_task_mapper.py",
            "tests/test_wave_generator.py",
            "tests/orchestrator/test_deferred_queue.py",
            "tests/integration/test_agent_e2e.py",
        ],
        "config_files": [
            "config/trigger_router.yaml",
            "config/capabilities.yaml",
            "config/session_state_machine.yaml",
        ],
        "governance_scripts": [],
        "note": "运行时集成——orchestrator 9文件已实现",
    },
    "script-system": {
        "module_id": "MOD-INF-005",
        "source_dirs": ["src/zephyr/infrastructure_runtime_integration/script_system"],
        "extra_source_files": [],
        "test_patterns": [],
        "config_files": [],
        "governance_scripts": [],
        "note": "脚本系统——第三条生产线，scaffold MVP已交付",
    },
    "shared-core": {
        "module_id": "MOD-INF-016",
        "source_dirs": ["src/zephyr/shared", "src/zephyr/core"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/test_schemas.py",
            "tests/test_ssot_guard.py",
            "tests/test_capability.py",
            "tests/test_money.py",
            "tests/test_instrument.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "共享+核心——全部12文件已实现",
    },
    "system-telemetry": {
        "module_id": "MOD-INF-015",
        "source_dirs": ["src/zephyr/observability/telemetry"],
        "extra_source_files": [],
        "test_patterns": [],
        "config_files": [],
        "governance_scripts": [],
        "note": "系统遥测——5子模块目录结构已建，代码全skeleton",
    },
    "task-card-kms": {
        "module_id": "MOD-INF-003",
        "source_dirs": [],
        "extra_source_files": [
            "src/zephyr/db/sqlite_schema.py",
            "src/zephyr/mcp/task_manager_server.py",
            "src/zephyr/core/blueprint_decomposer.py",
            "src/zephyr/pipeline/pipeline_orchestrator.py",
            "src/zephyr/governance/rule_enforcement/task_completion_gate.py",
            "src/zephyr/governance/rule_enforcement/g4_activate.yaml",
        ],
        "test_patterns": [
            "tests/test_sqlite_schema.py",
            "tests/infrastructure/test_mcp_servers.py",
            "tests/pipeline/test_pipeline_orchestrator.py",
            "tests/test_task_completion_gate.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "任务卡+KMS——experimental构建完成，已升级为MOD-INF-039",
    },
    "task-system": {
        "module_id": "MOD-TASK_SYSTEM",
        "source_dirs": ["src/zephyr/core", "src/zephyr/pipeline"],
        "extra_source_files": [
            "src/zephyr/db/task_repo.py",
            "src/zephyr/db/sqlite_schema.py",
            "src/zephyr/mcp/task_manager_server.py",
            "src/zephyr/governance/rule_enforcement/task_completion_gate.py",
        ],
        "test_patterns": [
            "tests/test_task_repo.py",
            "tests/test_sqlite_schema.py",
            "tests/infrastructure/test_mcp_servers.py",
            "tests/pipeline/test_pipeline_orchestrator.py",
            "tests/test_task_completion_gate.py",
            "tests/adversarial/test_task_system_red_team.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "任务系统——v0.3.0融合最优，experimental待重写",
    },
    "vector-memory": {
        "module_id": "MOD-INF-011",
        "source_dirs": ["src/zephyr/vector-memory"],
        "extra_source_files": [],
        "test_patterns": [],
        "config_files": [],
        "governance_scripts": [],
        "note": "向量记忆——仅目录+__init__.py docstring",
    },
    "vibe-coding-pipelines": {
        "module_id": "MOD-INF-004",
        "source_dirs": ["src/zephyr/pipeline"],
        "extra_source_files": [],
        "test_patterns": [
            "tests/pipeline/test_pipeline_orchestrator.py",
        ],
        "config_files": [],
        "governance_scripts": [],
        "note": "Vibe Coding双管线——scaffold构建完成，已升级为MOD-INF-039",
    },
}


def _scan_dir_for_files(rel_dir: str) -> list[str]:
    """_scan_dir_for_files implementation."""
    abs_dir = REPO_ROOT / rel_dir
    if not abs_dir.exists():
        return []
    results = []
    for f in sorted(abs_dir.rglob("*")):
        if f.is_file() and f.suffix in (".py", ".yaml", ".yml", ".json", ".toml"):
            rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel.endswith("__init__.py"):
                continue
            results.append(rel)
    return results


def _check_file_exists(rel_path: str) -> bool:
    """_check_file_exists implementation."""
    return (REPO_ROOT / rel_path).exists()


def _is_skeleton_file(rel_path: str) -> bool:
    """_is_skeleton_file implementation."""
    abs_path = REPO_ROOT / rel_path
    if not abs_path.exists():
        return False
    try:
        content = abs_path.read_text(encoding="utf-8")
        non_blank = [l for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]
        return len(non_blank) < 10
    except Exception:
        return True


def _determine_impl_status(rel_path: str) -> str:
    """_determine_impl_status implementation."""
    if not _check_file_exists(rel_path):
        return "❌ 未实现"
    if _is_skeleton_file(rel_path):
        return "⚠️ 骨架"
    return "✅ 已实现"


def _get_existing_files(module_name: str) -> dict[str, list[str]]:
    """_get_existing_files implementation."""
    mapping = BLUEPRINT_MODULE_MAP.get(module_name, {})
    all_files: dict[str, list[str]] = {
        "source": [],
        "test": [],
        "config": [],
        "governance": [],
    }

    for d in mapping.get("source_dirs", []):
        for f in _scan_dir_for_files(d):
            if f not in all_files["source"]:
                all_files["source"].append(f)

    for f in mapping.get("extra_source_files", []):
        f_norm = f.replace("\\", "/")
        if f_norm not in all_files["source"]:
            all_files["source"].append(f_norm)

    for f in mapping.get("test_patterns", []):
        f_norm = f.replace("\\", "/")
        all_files["test"].append(f_norm)

    for f in mapping.get("config_files", []):
        f_norm = f.replace("\\", "/")
        all_files["config"].append(f_norm)

    gov_dir = REPO_ROOT / "scripts" / "governance"
    if module_name == "script-system" and gov_dir.exists():
        for f in sorted(gov_dir.rglob("*.py")):
            if f.parent.name == "_shared":
                continue
            rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
            all_files["governance"].append(rel)
    else:
        for f in mapping.get("governance_scripts", []):
            f_norm = f.replace("\\", "/")
            all_files["governance"].append(f_norm)

    return all_files


def _find_max_section_number(content: str) -> int:
    """_find_max_section_number implementation."""
    pattern = re.compile(r"^##\s+(\d+)\.\s+", re.MULTILINE)
    nums = [int(m.group(1)) for m in pattern.finditer(content)]
    return max(nums) if nums else 0


def _bump_version(version_str: str) -> str:
    """_bump_version implementation."""
    parts = version_str.split(".")
    if len(parts) == 3:
        patch = int(parts[2]) + 1
        return f"{parts[0]}.{parts[1]}.{patch}"
    return version_str


def _generate_path_index_section(section_num: int, module_name: str) -> str:
    """_generate_path_index_section implementation."""
    mapping = BLUEPRINT_MODULE_MAP.get(module_name, {})
    note = mapping.get("note", "")
    files = _get_existing_files(module_name)

    has_any_code = any(_check_file_exists(f) for category in files.values() for f in category)

    lines = []
    lines.append(f"## {section_num}. 已实现代码完整路径索引")
    lines.append("")
    lines.append("> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。")
    lines.append("> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。")
    lines.append(f"> {note}")
    lines.append("")

    if not has_any_code:
        lines.append(f"### {section_num}.1 源码文件")
        lines.append("")
        lines.append("| 文件路径 | 实现状态 | 说明 |")
        lines.append("|---------|:---:|------|")
        lines.append("| — | — | 本模块尚无已实现代码 |")
        lines.append("")
    else:
        sub_num = 1
        if files["source"]:
            lines.append(f"### {section_num}.{sub_num} 源码文件")
            lines.append("")
            lines.append("| 文件路径 | 实现状态 | 说明 |")
            lines.append("|---------|:---:|------|")
            for f in files["source"]:
                status = _determine_impl_status(f)
                lines.append(f"| `{f}` | {status} | |")
            lines.append("")
            sub_num += 1

        if files["test"]:
            lines.append(f"### {section_num}.{sub_num} 测试文件")
            lines.append("")
            lines.append("| 文件路径 | 实现状态 | 说明 |")
            lines.append("|---------|:---:|------|")
            for f in files["test"]:
                status = _determine_impl_status(f)
                lines.append(f"| `{f}` | {status} | |")
            lines.append("")
            sub_num += 1

        if files["config"]:
            lines.append(f"### {section_num}.{sub_num} 配置文件")
            lines.append("")
            lines.append("| 文件路径 | 实现状态 | 说明 |")
            lines.append("|---------|:---:|------|")
            for f in files["config"]:
                status = _determine_impl_status(f)
                lines.append(f"| `{f}` | {status} | |")
            lines.append("")
            sub_num += 1

        if files["governance"]:
            lines.append(f"### {section_num}.{sub_num} 治理脚本")
            lines.append("")
            lines.append("| 文件路径 | 实现状态 | 说明 |")
            lines.append("|---------|:---:|------|")
            for f in files["governance"]:
                status = _determine_impl_status(f)
                lines.append(f"| `{f}` | {status} | |")
            lines.append("")
            sub_num += 1

    lines.append(f"### {section_num}.5 路径索引使用指南")
    lines.append("")
    lines.append("**新 AI session 读取顺序**：")
    lines.append(f"1. 读本蓝图 §{section_num}（本节）→ 知道「哪些已实现、在哪里」")
    lines.append("2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」")
    lines.append("3. 读施工 Phase 规划 → 知道「下一步该做什么」")
    lines.append("")
    lines.append("**路径约定**：")
    lines.append("- 所有路径相对于 `D:\\ZephyrAlpha\\\\`")
    lines.append("- 源码在 `src/zephyr/` 下")
    lines.append("- 测试在 `tests/` 下")
    lines.append("- 配置在 `config/` 下")
    lines.append("- 治理脚本在 `scripts/governance/` 下")
    lines.append("")

    return "\n".join(lines)


def _process_blueprint(bp_path: Path, check_only: bool = False) -> tuple[bool, list[str]]:
    """_process_blueprint implementation."""
    content = bp_path.read_text(encoding="utf-8")
    rel_bp = bp_path.relative_to(REPO_ROOT)
    actions: list[str] = []

    if SECTION_PATTERN.search(content):
        actions.append(f"✅ {rel_bp}: 已有路径索引章节，无需更新")
        return False, actions

    module_name = bp_path.parent.name
    if module_name not in BLUEPRINT_MODULE_MAP:
        actions.append(f"⚠️ {rel_bp}: 模块名 '{module_name}' 不在映射表中，跳过")
        return False, actions

    if check_only:
        actions.append(f"🔴 {rel_bp}: 缺少路径索引章节（需同步）")
        return True, actions

    max_section = _find_max_section_number(content)
    next_section = max_section + 1

    section_content = _generate_path_index_section(next_section, module_name)

    changelog_pattern = re.compile(r"^##\s+变更记录", re.MULTILINE)
    governance_pattern = re.compile(r"^##\s+治理信息", re.MULTILINE)

    insert_match = changelog_pattern.search(content) or governance_pattern.search(content)
    if insert_match:
        insert_pos = insert_match.start()
        content = content[:insert_pos] + section_content + "\n---\n\n" + content[insert_pos:]
    else:
        content = content.rstrip() + "\n\n---\n\n" + section_content

    version_pattern = re.compile(r'^version:\s*["\']?([\d.]+)["\']?', re.MULTILINE)
    version_match = version_pattern.search(content)
    if version_match:
        old_version = version_match.group(1)
        new_version = _bump_version(old_version)
        content = content.replace(f'version: "{old_version}"', f'version: "{new_version}"', 1)
        content = content.replace(f"version: {old_version}", f"version: {new_version}", 1)
        actions.append(f"📝 version: {old_version} → {new_version}")

    atomic_write_safe(bp_path, content)
    actions.append(f"✅ {rel_bp}: 已添加 §{next_section} 已实现代码完整路径索引")
    return True, actions


def sync(check_only: bool = False) -> int:
    """同步索引."""
    blueprints: list[Path] = []
    """sync."""
    for glob_pattern in BLUEPRINT_GLOBS:
        blueprints.extend(REPO_ROOT.glob(glob_pattern))
    blueprints = sorted(set(blueprints))

    print(f"[SYNC-BLUEPRINT-CODE] 扫描 {len(blueprints)} 份蓝图...")

    updated = 0
    needs_sync = 0

    for bp in blueprints:
        changed, actions = _process_blueprint(bp, check_only)
        for action in actions:
            print(f"  {action}")
        if changed:
            if check_only:
                needs_sync += 1
            else:
                updated += 1

    if check_only:
        if needs_sync > 0:
            print(f"\n[SYNC-BLUEPRINT-CODE] 🔴 发现 {needs_sync} 份蓝图需要同步")
            print("       请运行 sync_blueprint_code_index.py 修复")
            return EXIT_FINDINGS
        print("[SYNC-BLUEPRINT-CODE] ✅ 所有蓝图路径索引已同步，无漂移")
        return EXIT_PASS
    print(f"\n[SYNC-BLUEPRINT-CODE] ✅ 完成！更新了 {updated}/{len(blueprints)} 份蓝图")
    return EXIT_PASS
    """sync."""


def main() -> None:
    """入口函数."""
    parser = ArgumentParser(description="蓝图 §19 已实现代码路径索引自动同步（AGENTS.md §6.1）")
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查漂移（CI 模式: exit 1 = 有蓝图缺少路径索引）",
    )
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    code = sync(check_only=args.check)
    sys.exit(code)


if __name__ == "__main__":
    main()
