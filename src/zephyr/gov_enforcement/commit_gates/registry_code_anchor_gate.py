# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 业务注册表代码锚点门禁; staged注册表或代码删除/改名时触发; fail-open(脚本异常); fail-closed(违规阻断)
# [MODIFY-GUARD] gate_id="REGISTRY-CODE-ANCHOR"; #ARCH-BREG-002 门禁A
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess异常降级为 fail-open(passed=True); 违规阻断(passed=False)
# [TESTS] tests/governance/commit_gates/test_registry_code_anchor_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
registry_code_anchor_gate.py — 业务注册表代码锚点门禁（REGISTRY-CODE-ANCHOR）

#ARCH-BREG-002 门禁A（分域真源：实现域 owner=代码，库侧锚点必须真实）。

双触发：
  1. staged 文件含 15 个业务注册表 YAML → subprocess 调用
     check_registry_code_anchor.py --files <staged>（锚点存在性全项校验）。
  2. staged 含 src/ 下 .py 的删除/改名（git diff --cached --name-status D/R）
     → 反向查找：被删/改名路径是否仍被注册表条目 code_path/code_symbol 引用，
     引用存在则硬阻断（防代码侧改动制造库侧锚点漂移——13 条存量漂移实证同族）。

设计决策
--------
1. **fail-open**：subprocess 异常/超时/脚本不存在时放行（环境问题不阻断工作流）。
2. **fail-closed on violations**：checker exit 1 硬阻断；反查命中引用硬阻断。
3. **priority=129**：NO-SECRET-HARDCODE(128) 之后、CAPABILITY-OVERLAP(200) 之前——
   原定 106，实测被 UNDEFINED-NAME 占用（GateRegistrationError 撞号让位惯例）。
4. **deprecated/retired 条目豁免**：反查时跳过（tombstone 锚点为历史记录）。

Usage::

    from zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate import (
        make_registry_code_anchor_gate,
    )
    registry.register(make_registry_code_anchor_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: registry_code_anchor_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_registry_code_anchor_gate
#   name_en: make_registry_code_anchor_gate
#   intro: 构造业务注册表代码锚点门禁（fail-open on env error, fail-closed on violat…
#   desc: 构造业务注册表代码锚点门禁（fail-open on env error, fail-closed on violations）。 Returns: GateSpec(gate_…；源码 L196-L271
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
    run_checker_script,
)

logger = logging.getLogger(__name__)

__all__ = ["make_registry_code_anchor_gate"]

# checker 脚本路径（相对 project_root）
_CHECKER_REL = "scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py"

# 15 个含 code 锚点的业务注册表文件名（与 checker REGISTRY_LISTS 一致）
_REGISTRY_NAMES = frozenset(
    {
        "factor_registry.yaml",
        "strategy_registry.yaml",
        "technical_indicator_registry.yaml",
        "universe_registry.yaml",
        "benchmark_registry.yaml",
        "cost_model_registry.yaml",
        "execution_algo_registry.yaml",
        "risk_limit_registry.yaml",
        "data_asset_registry.yaml",
        "chart_pattern_registry.yaml",
        "field_dictionary.yaml",
        "experiment_registry.yaml",
        "model_registry.yaml",
        "regime_cycle_registry.yaml",
        "portfolio_model_registry.yaml",
    }
)

_CATALOGS_REL = "docs/01_policies_and_standards/_registry/catalogs"

# subprocess 超时（秒）
_TIMEOUT = 60

# 反查正则：code_path/code_symbol 行中提取路径 token
_ANCHOR_LINE_RE = re.compile(r"^\s*code_(?:path|symbol):\s*[\"\']?([^\"\'#\s]+)")
_ENTRY_ID_RE = re.compile(r"^\s*- \w+_id:\s*[\"']?([^\"'\s]+)")
_STATUS_DEAD_RE = re.compile(r"^\s+status:\s*[\"']?(deprecated|retired)")


def _staged_registry_files(files: list[str], project_root: Path) -> list[str]:
    """staged 中属于 15 个业务注册表的文件（相对路径）。"""
    hits = []
    for f in files:
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel):
            continue
        if rel.startswith(_CATALOGS_REL + "/") and os.path.basename(rel) in _REGISTRY_NAMES:
            hits.append(rel)
    return hits


def _deleted_or_renamed_py(gateway) -> list[str]:
    """staged 中被删除/改名的 src/ 下 .py 路径（相对路径，正斜杠）。"""
    result = gateway.run_git(["git", "diff", "--cached", "--name-status", "--diff-filter=DR"])
    if result.returncode != 0:
        return []
    paths = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        if status.startswith("D") and len(parts) >= 2:
            old = parts[1]
        elif status.startswith("R") and len(parts) >= 3:
            old = parts[1]  # 改名取旧路径
        else:
            continue
        old = old.replace("\\", "/")
        if old.startswith("src/") and old.endswith(".py"):
            paths.append(old)
    return paths


def _find_anchor_references(project_root: Path, deleted: list[str]) -> list[str]:
    """反查：deleted 路径是否仍被注册表条目引用（deprecated/retired 条目豁免）。"""
    if not deleted:
        return []
    hits = []
    catalogs = project_root / _CATALOGS_REL
    for name in sorted(_REGISTRY_NAMES):
        reg = catalogs / name
        if not reg.is_file():
            continue
        try:
            lines = reg.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        # 简化扫描：逐行匹配锚点字段，跟踪最近条目 id（dash 行）与 status
        current_id = "?"
        deprecated = False
        for ln in lines:
            m_eid = _ENTRY_ID_RE.match(ln)
            if m_eid:
                current_id = m_eid.group(1)
                deprecated = False
                continue
            if _STATUS_DEAD_RE.match(ln):
                deprecated = True
                continue
            m = _ANCHOR_LINE_RE.match(ln)
            if m and not deprecated:
                anchor = m.group(1).split("::", 1)[0].rstrip("/")
                for d in deleted:
                    d_norm = d.rstrip("/")
                    # 命中：锚点等于被删路径，或被删目录的前缀（覆盖目录锚点与 :: 符号锚点）
                    if anchor == d_norm or anchor.startswith(d_norm + "/") or d_norm.startswith(anchor + "/"):
                        hits.append(f"{name} 条目 {current_id}: {m.group(1)}")
    return hits


def make_registry_code_anchor_gate() -> GateSpec:
    """构造业务注册表代码锚点门禁（fail-open on env error, fail-closed on violations）。

    Returns:
        GateSpec(gate_id="REGISTRY-CODE-ANCHOR", priority=106)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        staged_regs = _staged_registry_files(files, project_root)
        deleted_py = _deleted_or_renamed_py(gateway)

        if not staged_regs and not deleted_py:
            return True, ""

        # 分支 1：代码删除/改名 → 反查库引用
        if deleted_py:
            refs = _find_anchor_references(project_root, deleted_py)
            if refs:
                detail = "\n".join(f"  - {r}" for r in refs[:20])
                return False, (
                    "业务注册表代码锚点门禁检测到违规（REGISTRY_CODE_ANCHOR_VIOLATION）——"
                    f"触发原因: src/ 代码删除/改名 {len(deleted_py)} 个，仍被注册表条目引用\n"
                    f"{detail}\n"
                    "修复：先同步更新库条目 code_path/code_symbol 或将条目标记 deprecated（#ARCH-BREG-002）"
                )

        # 分支 2：注册表变更 → checker 锚点校验
        if staged_regs:
            checker_path = project_root / _CHECKER_REL
            if not checker_path.is_file():
                logger.warning(
                    "REGISTRY-CODE-ANCHOR gate fail-open: checker 不存在(%s)，检测器失效。",
                    checker_path,
                )
                return True, ""
            try:
                result = run_checker_script(
                    checker_path,
                    ["--ci", "--files", *staged_regs],
                    cwd=str(project_root),
                    timeout=_TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                logger.warning(
                    "REGISTRY-CODE-ANCHOR gate fail-open: checker 超时(%ds)，检测器失效。",
                    _TIMEOUT,
                )
                return True, ""
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning(
                    "REGISTRY-CODE-ANCHOR gate fail-open: subprocess 异常(%s: %s)，检测器失效。",
                    type(e).__name__,
                    e,
                    exc_info=True,
                )
                return True, ""

            if result.returncode == 0:
                return True, ""
            if result.returncode == 2:
                logger.warning(
                    "REGISTRY-CODE-ANCHOR gate fail-open: checker 异常(exit 2): %s",
                    (result.stderr or result.stdout)[:200],
                )
                return True, ""
            detail = result.stdout.strip() if result.stdout else "锚点校验违规（见 checker 输出）"
            return False, (
                "业务注册表代码锚点门禁检测到违规（REGISTRY_CODE_ANCHOR_VIOLATION）——"
                f"触发原因: 注册表变更 {len(staged_regs)} 个\n{detail}"
            )

        return True, ""

    return GateSpec(gate_id="REGISTRY-CODE-ANCHOR", check=_check, priority=129)
