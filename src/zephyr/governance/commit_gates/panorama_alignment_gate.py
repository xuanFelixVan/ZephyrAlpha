# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.panorama_alignment_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d5_architecture.generators.align_panoramas (run_alignment, PanoramaEmptyError)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] warn-only——永不阻断 commit（passed=True）；仅当 staged 文件触及 depgraph/dataflow/decision 相关路径时触发检测；run_alignment 异常时 fail-loud（logger.warning，仍 return True）；三图任一为空（PanoramaEmptyError）时跳过检测（return True）
# [MODIFY-GUARD] gate_id="GATE-PANORAMA-ALIGNMENT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——run_alignment/PanoramaEmptyError/DB 异常降级为 fail-loud warn（不阻断 commit 保留 warn-only 契约）
# [TESTS] tests/governance/commit_gates/test_panorama_alignment_gate.py
# [A_module] module_id=MOD-GOV-panorama_alignment_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""panorama_alignment_gate.py — 三图模块对齐 warn-only 门禁（四图模块对齐 Step 4）

在 GitCommitGateway pre-commit 阶段调用 align_panoramas.run_alignment() 检测三图
（depgraph / dataflowgraph / decisiongraph）的模块对齐情况，命中阈值时 logger.warning
告警（**不阻断 commit**），提示 AI 修复对齐问题。

触发条件：staged 文件路径触及 depgraph/dataflow/decision 相关变更：
  - src/zephyr/governance/depgraph_schema.py / persistence/{dataflow,decision}graph_schema.py
  - scripts/governance/apply_depgraph.py / apply_dataflowgraph.py / apply_decisiongraph.py
  - scripts/governance/generate_project_depgraph.py
  - docs/01_policies_and_standards/_registry/catalogs/{dataflow_graph,decision_layers}_registry.yaml
  - scripts/governance/d5_architecture/generators/align_panoramas.py

warn-only 裁定
---------------
三图对齐涉及 4273+ 孤儿（历史遗留），阻断会阻碍所有 depgraph 相关开发。
初期仅 warn-only 告警，待孤儿数降至阈值以下后可改 block。

Usage::

    from zephyr.governance.commit_gates.panorama_alignment_gate import make_panorama_alignment_gate

    registry.register(make_panorama_alignment_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import sys

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_panorama_alignment_gate"]


# 触发门禁的文件路径前缀/子串（staged 文件命中任一则触发检测）
_TRIGGER_PATTERNS = (
    "src/zephyr/governance/depgraph_schema.py",
    "src/zephyr/governance/persistence/dataflowgraph_schema.py",
    "src/zephyr/governance/persistence/decisiongraph_schema.py",
    "scripts/governance/apply_depgraph.py",
    "scripts/governance/apply_dataflowgraph.py",
    "scripts/governance/apply_decisiongraph.py",
    "scripts/governance/generate_project_depgraph.py",
    "docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/decision_layers_registry.yaml",
    "scripts/governance/d5_architecture/generators/align_panoramas.py",
)

# 告警阈值
_ORPHAN_WARN_THRESHOLD = 100  # 孤儿数 > 100 告警
_STATE_DRIFT_WARN_THRESHOLD = 0  # 状态漂移 > 0 告警


def _should_trigger(staged_files: list[str]) -> bool:
    """判断 staged 文件是否触及三图相关变更。"""
    for f in staged_files:
        norm = f.replace("\\", "/")
        for pattern in _TRIGGER_PATTERNS:
            if pattern in norm:
                return True
    return False


def make_panorama_alignment_gate() -> GateSpec:
    """构造三图模块对齐 warn-only 门禁 GateSpec。

    Returns:
        GateSpec(gate_id="GATE-PANORAMA-ALIGNMENT", priority=830)。
        priority=830——在 GATE-MODULE-INVENTORY-SYNC 之后执行。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 文件清单
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "GATE-PANORAMA-ALIGNMENT gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_files = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "GATE-PANORAMA-ALIGNMENT gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True,
            )
            return True, ""

        # 2. 判断是否触发检测
        if not _should_trigger(staged_files):
            return True, ""  # 不涉及三图变更，跳过

        # 3. 调用 align_panoramas.run_alignment()
        #    动态导入避免模块加载时硬依赖 scripts/ 路径
        try:
            # scripts/governance/d5_architecture/generators/ 需要在 sys.path 中
            scripts_root = os.path.join(str(gateway.project_root), "scripts")
            if scripts_root not in sys.path:
                sys.path.insert(0, scripts_root)

            from governance.d5_architecture.generators.align_panoramas import (
                PanoramaEmptyError,
                run_alignment,
            )

            # 不写报告文件（门禁场景只需检测结果，不污染 docs/）
            report = run_alignment(write_report=False)
        except PanoramaEmptyError as e:
            # 三图任一为空——跳过检测（可能是初始化阶段）
            logger.info(
                "GATE-PANORAMA-ALIGNMENT skip: 三图任一为空(%s)，跳过对齐检测。",
                str(e),
            )
            return True, ""
        except Exception as e:
            # fail-loud：检测器失效，告警但不阻断
            logger.warning(
                "GATE-PANORAMA-ALIGNMENT gate fail-open: run_alignment 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True,
            )
            return True, ""

        # 4. 检查阈值并告警
        orphan_count = len(report.orphans)
        drift_count = len(report.state_drifts)
        domain_mismatch_count = len(report.domain_mismatches)
        design_only_count = len(report.design_only_in_one)

        warnings: list[str] = []
        if orphan_count > _ORPHAN_WARN_THRESHOLD:
            warnings.append(
                f"孤儿数 {orphan_count} > 阈值 {_ORPHAN_WARN_THRESHOLD}"
            )
        if drift_count > _STATE_DRIFT_WARN_THRESHOLD:
            warnings.append(
                f"状态漂移 {drift_count} > 阈值 {_STATE_DRIFT_WARN_THRESHOLD}"
            )

        if warnings:
            warn_msg = " | ".join(warnings)
            logger.warning(
                "GATE-PANORAMA-ALIGNMENT gate warn-only: %s "
                "(域不一致=%d, 设计态孤立=%d)",
                warn_msg, domain_mismatch_count, design_only_count,
            )

        # warn-only：永远 passed=True
        return True, ""

    return GateSpec(gate_id="GATE-PANORAMA-ALIGNMENT", check=_check, priority=830)
