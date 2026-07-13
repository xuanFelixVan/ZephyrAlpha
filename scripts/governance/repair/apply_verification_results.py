#!/usr/bin/env python3
"""
apply_verification_results.py — 第32轮验证结果批量应用到架构债务注册表

功能：
1. 批量替换DRIFTED路径（12条已知路径迁移）
2. 标记FIXED问题为已修复
3. 标记NOT_NEEDED问题为豁免
4. 移除失效引用（chaos_injector.py:292等）
5. 输出变更统计

用法：python scripts/governance/repair/apply_verification_results.py [--dry-run]
"""

__manifest__ = """
args: []
description: apply_verification_results.py — 第32轮验证结果批量应用到架构债务注册表
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import sys
from pathlib import Path

REGISTRY = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")

# ═══════════════════════════════════════════════════════════
# 1. 路径替换映射（DRIFTED → 新路径）
# ═══════════════════════════════════════════════════════════
PATH_REPLACEMENTS = [
    # 旧路径前缀 → 新路径前缀
    (r"src/zephyr/behavioral_audit/", r"src/zephyr/governance/drift_detection/"),
    (r"src[/\\]zephyr[/\\]behavioral_audit[/\\]", r"src/zephyr/governance/drift_detection/"),
    (r"src\\zephyr\\behavioral_audit\\", r"src/zephyr/governance/drift_detection/"),
    # ops/ → trading/feedback_loop/ (仅限特定子目录，ops/observability单独处理)
    (r"src/zephyr/ops/evolution_engine", r"src/zephyr/feedback_loop/evolution_engine"),
    (r"src/zephyr/ops/scheduler", r"src/zephyr/feedback_loop/scheduler"),
    (r"src/zephyr/ops/metrics_collector", r"src/zephyr/governance/metrics_collector"),
    (r"src/zephyr/ops/slo_manager", r"src/zephyr/governance/slo_manager"),
    (r"src/zephyr/ops/gates/", r"src/zephyr/infrastructure/system_telemetry/gates/"),
    # ops/observability → shared/ (observability_02/ 已删除,真实现归位至 shared/ 根)
    (r"src/zephyr/ops/observability/", r"src/zephyr/shared/"),
    # circuit_breaker
    (r"src/zephyr/ops/circuit_breaker", r"src/zephyr/governance/circuit_breaker"),
    # autonomy_core/llm_gateway.py 已删除
    # autonomy_core/context_injector → autonomy_core/context/context_injector
    (r"src/zephyr/autonomy_core/context_injector", r"src/zephyr/autonomy_core/context/context_injector"),
    # governance/escalation_engine → governance/escalation/escalation_engine
    (r"src/zephyr/governance/escalation_engine", r"src/zephyr/governance/escalation/escalation_engine"),
    # governance/delegation_engine → governance/delegation/delegation_engine
    (r"src/zephyr/governance/delegation_engine", r"src/zephyr/governance/delegation/delegation_engine"),
    # governance/env_watcher → governance/ops/env_watcher
    (r"src/zephyr/governance/env_watcher", r"src/zephyr/governance/ops/env_watcher"),
    # phase_a_backup → _archive
    (r"scripts/governance/phase_a_backup", r"scripts/governance/_archive/one_off/phase_a_backup"),
    # tests/ 根目录 → tests/<子目录>/
    (r"tests/test_e_contracts", r"tests/e/test_e_contracts"),
    (r"tests/test_rule_red_blue", r"tests/rule/test_rule_red_blue"),
    (r"tests/test_f21_event_driven", r"tests/f_lifecycle/test_f21_event_driven"),
    (r"tests/test_db_integration", r"tests/db/test_db_integration"),
    (r"tests/test_governance_db", r"tests/governance/shared/test_governance_db"),
    (r"tests/test_depgraph_db", r"tests/governance/depgraph/test_depgraph_db"),
    (r"tests/test_depgraph_generator_design_protection", r"tests/governance/depgraph/test_depgraph_generator_design_protection"),
    (r"tests/test_input_sanitizer_llm_security", r"tests/llm_security/test_input_sanitizer_llm_security"),
    (r"tests/test_f3_auto_integration", r"tests/infrastructure/test_f3_auto_integration"),
    (r"tests/test_f3_extreme", r"tests/infrastructure/test_f3_extreme"),
    (r"tests/test_f18_redblue", r"tests/f_lifecycle/test_f18_redblue"),
    (r"tests/test_verify_schema_health", r"tests/io/test_verify_schema_health"),
    (r"tests/test_mcp_signal_shutdown", r"tests/infrastructure/test_mcp_signal_shutdown"),
    (r"tests/test_mcp_idle_timeout", r"tests/infrastructure/test_mcp_idle_timeout"),
    (r"tests/test_mcp_health_check_recovery", r"tests/infrastructure/test_mcp_health_check_recovery"),
    (r"tests/test_mcp_boot_hooks_integration", r"tests/infrastructure/test_mcp_boot_hooks_integration"),
    (r"tests/test_task_system_red_team", r"tests/autonomy/test_task_system_red_team"),
    (r"tests/test_mcp_red_team", r"tests/infrastructure/test_mcp_red_team"),
    (r"tests/test_cross_layer_systems_red_team", r"tests/kb/test_cross_layer_systems_red_team"),
    (r"tests/test_action_dispatcher", r"tests/action/test_action_dispatcher"),
    (r"tests/test_defense_runner", r"tests/safety/test_defense_runner"),
    (r"tests/test_pipeline_skill_injection", r"tests/autonomy/test_pipeline_skill_injection"),
    (r"tests/test_adversarial_mutator", r"tests/llm_security/test_adversarial_mutator"),
    (r"tests/test_phase_g_perf", r"tests/trading/test_phase_g_perf"),
    (r"tests/test_sequence_guard_agent_rbac", r"tests/agent_rbac/test_sequence_guard_agent_rbac"),
    # Windows绝对路径风格
    (r"D:\\ZephyrAlpha\\src\\zephyr\\behavioral_audit\\", r"D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detection\\"),
    (r"d:\\ZephyrAlpha\\src\\zephyr\\behavioral_audit\\", r"d:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detection\\"),
]

# ═══════════════════════════════════════════════════════════
# 2. FIXED问题标记（按维度）
# ═══════════════════════════════════════════════════════════
# 在对应行追加 [✓ FIXED] 标记
FIXED_MARKERS = [
    # 5.16.5 - _GlobalCommitLock已用原子os.open
    (r"5\.16\.5.*_GlobalCommitLock.*TOCTOU", " [✓ FIXED: 已用原子os.open(O_CREAT|O_EXCL)消除TOCTOU]"),
    # 5.16.6 - stash逻辑已由worktree隔离替代
    (r"5\.16\.6.*stash.*commit.*pop", " [✓ FIXED: 已由worktree物理隔离替代]"),
    # 5.22.9 - 三个孤儿__init___from_*.py文件已删除
    (r"5\.22\.9.*孤儿.*__init___from", " [✓ FIXED: 三个孤儿文件已删除]"),
    # 5.27.7 - 文档"3073模块"已移除
    (r"5\.27\.7.*模块数.*不符", " [✓ FIXED: 文档中硬编码数字已移除]"),
    # 5.28.2 - 错误消息已含字段名约束
    (r"5\.28\.2.*错误消息无actionable", " [✓ FIXED: 错误消息已含字段名约束]"),
    # 5.28.7 - 拼写错误已消除
    (r"5\.28\.7.*拼写错误", " [✓ FIXED: faield/succesful拼写错误已消除]"),
    # 5.35.5 - breaking change检测已建立
    (r"5\.35\.5.*breaking.*change.*检测", " [✓ FIXED: 已建立BreakingChangeDetector等多处检测机制]"),
    # 5.39.7 - OTLP exporter已配置
    (r"5\.39\.7.*OTLP.*exporter", " [✓ FIXED: tracing.py已配置完整OTLP gRPC exporter]"),
    # 5.40.3 - retry_count自赋值已修复
    (r"5\.40\.3.*retry_count.*自赋值", " [✓ FIXED: 自赋值bug已消除，改为6处正确的+=1]"),
    # 5.43.3 - SQLite已用连接池
    (r"5\.43\.3.*SQLite.*连接池", " [✓ FIXED: 已用threading.local连接池复用]"),
    # 5.43.4 - asyncio.gather已加Semaphore
    (r"5\.43\.4.*asyncio\.gather.*Semaphore", " [✓ FIXED: 已加Semaphore限流]"),
]

# ═══════════════════════════════════════════════════════════
# 3. NOT_NEEDED问题标记
# ═══════════════════════════════════════════════════════════
NOT_NEEDED_MARKERS = [
    # 5.32.6 - _MIGRATIONS孤儿代码已缓解
    (r"5\.32\.6.*_MIGRATIONS.*孤儿", " [⊘ NOT_NEEDED: 显式注释已缓解AI混淆风险]"),
    # 5.42.2 - deprecated矛盾未发现
    (r"5\.42\.2.*deprecated.*活跃调用", " [⊘ NOT_NEEDED: 未发现矛盾实例，存在规范deprecation框架]"),
]

# ═══════════════════════════════════════════════════════════
# 4. 失效引用处理
# ═══════════════════════════════════════════════════════════
STALE_REFERENCES = [
    # autonomy_core/llm_gateway.py 已删除
    (r"autonomy_core/llm_gateway\.py", "autonomy_core/llm_gateway.py [⚠ 已删除，仅剩integration/和infrastructure/pipeline/副本]"),
    # chaos_injector.py:292引用失效
    (r"chaos_injector\.py:292", "chaos_injector.py:292 [⚠ 引用失效：该文件无asyncio代码]"),
]


def apply_path_replacements(text: str) -> tuple[str, int]:
    """批量替换路径"""
    count = 0
    for old, new in PATH_REPLACEMENTS:
        new_text = re.sub(old, new, text)
        if new_text != text:
            diff = len(text) - len(new_text)
            # 计算替换次数
            old_count = len(re.findall(old, text))
            count += old_count
            text = new_text
    return text, count


def apply_markers(text: str, markers: list, tag: str) -> tuple[str, int]:
    """在匹配行追加标记"""
    count = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for pattern, suffix in markers:
            if re.search(pattern, line) and suffix.strip() not in line:
                lines[i] = line.rstrip() + suffix
                count += 1
    return "\n".join(lines), count


def apply_stale_references(text: str) -> tuple[str, int]:
    """标记失效引用"""
    count = 0
    for old, new in STALE_REFERENCES:
        new_text = re.sub(old, new, text)
        if new_text != text:
            count += len(re.findall(old, text))
            text = new_text
    return text, count


def main():
    dry_run = "--dry-run" in sys.argv

    print(f"读取注册表: {REGISTRY}")
    original = REGISTRY.read_text(encoding="utf-8")
    text = original

    # Step 1: 路径替换
    text, path_count = apply_path_replacements(text)
    print(f"[1] 路径替换: {path_count}处")

    # Step 2: FIXED标记
    text, fixed_count = apply_markers(text, FIXED_MARKERS, "FIXED")
    print(f"[2] FIXED标记: {fixed_count}处")

    # Step 3: NOT_NEEDED标记
    text, nn_count = apply_markers(text, NOT_NEEDED_MARKERS, "NOT_NEEDED")
    print(f"[3] NOT_NEEDED标记: {nn_count}处")

    # Step 4: 失效引用
    text, stale_count = apply_stale_references(text)
    print(f"[4] 失效引用标记: {stale_count}处")

    total = path_count + fixed_count + nn_count + stale_count
    print(f"\n总变更: {total}处")

    if text == original:
        print("无变更，跳过写入")
        return

    if dry_run:
        print("\n[DRY RUN] 不写入文件。变更统计如上。")
        # 输出前10处diff
        orig_lines = original.split("\n")
        new_lines = text.split("\n")
        diffs = 0
        for i, (o, n) in enumerate(zip(orig_lines, new_lines)):
            if o != n:
                diffs += 1
                if diffs <= 20:
                    print(f"  L{i+1}: -{o[:120]}")
                    print(f"  L{i+1}: +{n[:120]}")
        print(f"  ...共{diffs}行变更")
    else:
        REGISTRY.write_text(text, encoding="utf-8")
        print(f"已写入: {REGISTRY}")


if __name__ == "__main__":
    main()
