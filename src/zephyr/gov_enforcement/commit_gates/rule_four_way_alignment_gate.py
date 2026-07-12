# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.rule_four_way_alignment_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则四方对齐门禁; staged规则文件或catalog变更时触发; fail-open(脚本异常); fail-closed(违规阻断)
# [MODIFY-GUARD] gate_id="RULE-FOUR-WAY-ALIGN"; ARCH-020 补建
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess异常降级为 fail-open(passed=True); 违规阻断(passed=False)
# [TESTS] tests/governance/commit_gates/test_rule_four_way_alignment_gate.py
# [A_module] module_id=MOD-GOV-rule_four_way_alignment_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rule_four_way_alignment_gate.py — 规则四方对齐门禁（RULE-FOUR-WAY-ALIGN）

检测 staged 文件中规则文件或 rule_catalog_registry.yaml 变更时，触发四方对齐检查
（YAML ↔ Catalog ↔ Disk ↔ Code）。命中则阻断 commit。

病根（ARCH-020）
----------------
check_rule_four_way_alignment.py 文件不存在，四方对齐门禁完全缺失。原裁定指
line 80/94/130 过滤条件 ``data.get("layer") != "L0"`` 恒为假（layer 是架构层名
如 "compliance"，非 tier 如 "L0"）。治本：补建脚本 + 注册 GitCommitGateway
in-process gate（无法用 --no-verify 绕过）。

设计决策
--------
1. **触发条件**：staged 文件包含 ``docs/01_policies_and_standards/`` 下的规则
   文件（.yaml/.yml/.md）或 ``rule_catalog_registry.yaml`` 时触发。
2. **fail-open**：subprocess 异常/超时/脚本不存在时放行（环境问题不阻断工作流）。
3. **fail-closed on violations**：checker exit 1（检测到违规）时硬阻断。
4. **priority=76**：紧跟 ARCH-REFERENCE(75) 之后，同属"引用完整性"类检查。
5. **subprocess 调用**：复用 check_rule_four_way_alignment.py 作为真源，避免
   逻辑重复。

Usage::

    from zephyr.governance.commit_gates.rule_four_way_alignment_gate import (
        make_rule_four_way_alignment_gate,
    )

    registry.register(make_rule_four_way_alignment_gate())
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_rule_four_way_alignment_gate"]

# checker 脚本路径（相对 project_root）
_CHECKER_REL = "scripts/governance/d5_architecture/checkers/check_rule_four_way_alignment.py"

# 触发文件路径前缀（staged 文件匹配任一前缀时触发）
_TRIGGER_PREFIXES = (
    "docs/01_policies_and_standards/",
)

# 触发文件名（精确匹配）
_TRIGGER_FILES = {
    "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
}

# 可扫描的规则文件扩展名
_RULE_EXTS = (".yaml", ".yml", ".md")

# subprocess 超时（秒）
_TIMEOUT = 30


def _should_trigger(files: list[str], project_root: Path) -> tuple[bool, str]:
    """判断是否应触发门禁。

    Returns:
        (should_trigger, reason) —— should_trigger=True 时 reason 含触发文件信息。
    """
    for f in files:
        if not os.path.isfile(f):
            continue  # deletion commit
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel):
            continue
        if rel in _TRIGGER_FILES:
            return True, f"catalog 变更: {rel}"
        if rel.startswith(_TRIGGER_PREFIXES) and rel.endswith(_RULE_EXTS):
            return True, f"规则文件变更: {rel}"
    return False, ""


def make_rule_four_way_alignment_gate() -> GateSpec:
    """构造规则四方对齐门禁 GateSpec（fail-open on env error, fail-closed on violations）。

    Returns:
        GateSpec(gate_id="RULE-FOUR-WAY-ALIGN", priority=76)。
        priority=76——紧跟 ARCH-REFERENCE(75) 之后，同属"引用完整性"类检查。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        # 1. 判断是否触发
        should_run, reason = _should_trigger(files, project_root)
        if not should_run:
            return True, ""  # 无规则文件变更，跳过

        # 2. 定位 checker 脚本
        checker_path = project_root / _CHECKER_REL
        if not checker_path.is_file():
            logger.warning(
                "RULE-FOUR-WAY-ALIGN gate fail-open: checker 不存在(%s)，检测器失效。",
                checker_path,
            )
            return True, ""

        # 3. 获取 worktree root
        try:
            toplevel_result = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
            if toplevel_result.returncode == 0:
                wt_root = toplevel_result.stdout.strip()
            else:
                wt_root = str(project_root)
        except Exception:
            wt_root = str(project_root)

        # 4. subprocess 调用 checker
        try:
            result = subprocess.run(
                [sys.executable, str(checker_path), "--ci"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=wt_root,
                timeout=_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "RULE-FOUR-WAY-ALIGN gate fail-open: checker 超时(%ds)，检测器失效。",
                _TIMEOUT,
            )
            return True, ""
        except Exception as e:
            logger.warning(
                "RULE-FOUR-WAY-ALIGN gate fail-open: subprocess 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 5. 解析结果
        # exit 0 = 无违规；exit 1 = 有违规（EXIT_FINDINGS）；exit 2 = 脚本异常（EXIT_ERROR）
        if result.returncode == 0:
            return True, ""  # 无违规
        if result.returncode == 2:
            logger.warning(
                "RULE-FOUR-WAY-ALIGN gate fail-open: checker 异常(exit 2): %s",
                (result.stderr or result.stdout)[:200],
            )
            return True, ""  # 脚本异常，fail-open

        # exit 1 = 检出违规，硬阻断
        detail = result.stdout.strip() if result.stdout else "规则四方对齐违规（见 checker 输出）"
        return False, (
            f"规则四方对齐门禁检测到违规（RULE_FOUR_WAY_ALIGN_VIOLATION）——"
            f"触发原因: {reason}\n{detail}"
        )

    return GateSpec(gate_id="RULE-FOUR-WAY-ALIGN", check=_check, priority=76)
