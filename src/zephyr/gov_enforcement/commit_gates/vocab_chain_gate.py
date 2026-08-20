# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.vocab_chain_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增 .py 文件含 SSoT 文件路径硬编码（docs/01_*/.../*.yaml / docs/02_*/.../*.yaml / data/.../*.json）时阻断 commit；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A），不检测修改文件（避免基线存量违规划死工作流）；AST 解析失败 fail-open（logger.warning）；本 gate 自身文件豁免（含路径模式字符串用于检测）；扩展 VOCAB-HARDCODE 覆盖面至 SSoT 引用消费链
# [MODIFY-GUARD] gate_id="VOCAB-CHAIN"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m01-vocab-hardcode  M01豁免: 本文件是VOCAB-CHAIN检测器自身,源码含SSoT路径模式字符串用于AST匹配,非实际硬编码
"""vocab_chain_gate.py — SSoT 引用硬编码阻断门禁（VOCAB-CHAIN，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc2 enforceability）

病根（裁定#221，原 ai_first_governance_principles.md §二，文档已删 2026-07-30，git 历史可查）
------------------------------------------------
rc2_vocab_chain_blindspot: 词表→代码消费链机械盲区
VOCAB-HARDCODE gate (priority=80) 仅检测硬编码字符串（词表合法值），
未覆盖完整消费链——SSoT 文件路径硬编码（值域/字段名/SSoT 引用）是盲区。

治本方案
--------
本 gate 在 GitCommitGateway pre-commit 阶段（in-process，``--no-verify`` 绕不过）注册，
AST 分析 staged 新增 .py 文件中的字符串字面量，检测 SSoT 文件路径硬编码：

  1. ``docs/01_policies_and_standards/**/*.yaml`` —— 规则/词表/契约 SSoT
  2. ``docs/02_enterprise_architecture/**/*.yaml`` —— 架构 SSoT
  3. ``data/runtime_violation_snapshot/*.json`` —— 运行时快照 SSoT
  4. ``data/telemetry/**/*.jsonl`` —— 遥测 SSoT

这些路径应通过 capability_canonical_file_registry 反查发现，不应硬编码在源码中。

设计权衡
--------
1. **只检测新增文件**：存量违规由后续清理。本 gate 防止新增违规。
2. **in-process AST**：无 subprocess 调用，纯 ast.parse + ast.walk，自包含。
3. **fail-open on AST error**：语法错误文件不阻断，由其他 gate 负责。
4. **gate 自豁免**：本 gate 源码含路径模式字符串（用于检测），需自豁免。
5. **priority=73**：在 DOMAIN-NAME-ZH(72) 之后、RULING-REFERENCE(74) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.vocab_chain_gate import make_vocab_chain_gate

    registry.register(make_vocab_chain_gate())
"""

from __future__ import annotations

import ast
import logging
import os
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_vocab_chain_gate"]

# SSoT 路径前缀模式（这些路径应通过 capability registry 反查，不应硬编码在源码中）
# 注意：模式使用正则，需转义路径分隔符
_SSOT_PATH_PATTERNS = (
    re.compile(r"^docs/01_policies_and_standards/.*\.ya?ml$"),
    re.compile(r"^docs/02_enterprise_architecture/.*\.ya?ml$"),
    re.compile(r"^data/runtime_violation_snapshot/.*\.json$"),
    re.compile(r"^data/telemetry/.*\.jsonl$"),
)

# 豁免目录：这些目录的文件本身就处理 SSoT 路径（注册表/生成器/检查器/门禁）
_EXEMPT_PATH_FRAGMENTS = (
    "gov_enforcement/commit_gates/",
    "gov_enforcement\\commit_gates\\",
    "governance/commit_gates/",
    "governance\\commit_gates\\",
    "governance/generators/",
    "governance\\generators\\",
    "governance/d3_metadata/",
    "governance\\d3_metadata\\",
    "registry/catalogs/",
    "registry\\catalogs\\",
    "rule_bridge/",
    "rule_bridge\\",
)


def _is_exempt_path(rel_path: str) -> bool:
    """检查文件路径是否在豁免目录中（这些文件本就处理 SSoT 路径）。"""
    for frag in _EXEMPT_PATH_FRAGMENTS:
        if frag in rel_path:
            return True
    return False


def _matches_ssot_pattern(s: str) -> bool:
    """检查字符串是否匹配 SSoT 路径模式。

    只匹配看起来像文件路径的字符串（含 / 且以 .yaml/.yml/.json/.jsonl 结尾）。
    """
    # 快速过滤：必须含路径分隔符且以已知扩展名结尾
    if "/" not in s and "\\" not in s:
        return False
    lower = s.lower()
    if not (lower.endswith(".yaml") or lower.endswith(".yml") or lower.endswith(".json") or lower.endswith(".jsonl")):
        return False
    # 归一化为正斜杠
    normalized = s.replace("\\", "/")
    for pattern in _SSOT_PATH_PATTERNS:
        if pattern.match(normalized):
            return True
    return False


def _extract_string_literals(tree: ast.AST) -> list[str]:
    """从 AST 中提取所有字符串字面量（ast.Constant 且 value 为 str）。"""
    literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.append(node.value)
    return literals


def _detect_ssot_hardcoding(abs_path: str, content: str) -> list[str]:
    """检测文件中硬编码的 SSoT 路径，返回违规字符串列表。"""
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning(
            "VOCAB-CHAIN gate skip file %s: AST 解析失败(%s: %s)。",
            abs_path,
            type(e).__name__,
            e,
        )
        return []

    literals = _extract_string_literals(tree)
    violations: list[str] = []
    seen: set[str] = set()
    for lit in literals:
        if lit in seen:
            continue
        if _matches_ssot_pattern(lit):
            seen.add(lit)
            violations.append(lit)
    return violations


def _get_staged_new_py_files(gateway) -> tuple[list[str], str]:
    """获取 staged 新增 .py 文件列表 + worktree root。

    Returns:
        (py_files, wt_root) — py_files 为空时表示无文件或 fail-open。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            logger.warning(
                "VOCAB-CHAIN gate fail-open: git diff 失败(rc=%d)。",
                diff_result.returncode,
            )
            return [], ""
        staged_new = diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — broad exception catch for fail-open
        logger.warning(
            "VOCAB-CHAIN gate fail-open: git diff 异常(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return [], ""

    py_files = [f.replace("\\", "/") for f in staged_new if f.endswith(".py") and not is_test_exempt(f)]
    if not py_files:
        return [], ""

    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        wt_root = toplevel.stdout.strip() if toplevel.returncode == 0 else str(gateway.project_root)
    except Exception:  # noqa: BLE001 — broad exception catch for fail-open
        wt_root = str(gateway.project_root)

    return py_files, wt_root


def make_vocab_chain_gate() -> GateSpec:
    """构造 SSoT 引用硬编码阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="VOCAB-CHAIN", priority=73)。
        priority=73——在 DOMAIN-NAME-ZH(72) 之后、RULING-REFERENCE(74) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .py 文件
        py_files, wt_root = _get_staged_new_py_files(gateway)
        if not py_files:
            return True, ""

        # 2. AST 检测每个文件
        all_violations: list[str] = []
        for rel_path in py_files:
            # 豁免：本 gate 自身、注册表、生成器、检查器目录
            if _is_exempt_path(rel_path):
                continue

            abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError as e:
                logger.warning(
                    "VOCAB-CHAIN gate skip file %s: 读取失败(%s: %s)。",
                    abs_path,
                    type(e).__name__,
                    e,
                )
                continue

            violations = _detect_ssot_hardcoding(abs_path, content)
            for v in violations:
                all_violations.append(f'{rel_path}: "{v}"')

        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, (
                f"新增 .py 文件含 SSoT 路径硬编码（应通过 capability_canonical_file_registry "
                f"反查发现，非硬编码）: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="VOCAB-CHAIN", check=_check, priority=73)
