# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.derivation_annotation_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._diff_helpers (_parse_diff_with_line_numbers, _read_staged_file)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增 .py/.yaml 文件含 # [DERIVES_FROM] <path> 声明但 <path> 源文件不存在时阻断 commit；tests/ 豁免；git diff 不可达 fail-open；文件读取失败 fail-open；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="DERIVATION-ANNOTATION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff/文件读取异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""derivation_annotation_gate.py — 派生关系声明真实性校验门禁（DERIVATION-ANNOTATION）

补强 SSOT-REDEFINITION（priority=65，符号级重定义检测）的盲区——
SSOT-REDEFINITION 只管"符号重定义"，本 gate 管"派生声明真实性"：
文件声明 # [DERIVES_FROM] <path> 但 <path> 源文件不存在 → 硬阻断。

病根（第一性原理）
-----------------
12 维度审计 §2.3"派生关系标注"痛点：派生文件（registry/cache/index/sync 产物）
应标注派生来源，但手工审发现：
  - 派生文件无 DERIVES_FROM 声明（来源不明）
  - DERIVES_FROM 声明的源文件已删除/重命名（悬空派生）

SSOT-REDEFINITION 只检测符号重定义，不检测派生声明真实性。需要独立 gate。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged 新增 .py/.yaml 文件
  2. 过滤 tests/ 豁免
  3. 扫描文件头部（前 30 行）的 # [DERIVES_FROM] <path> 声明
  4. 校验 <path> 源文件存在（相对 project_root）
  5. 源文件不存在 → 硬阻断

设计权衡
--------
1. **聚焦声明真实性**：只校验"有声明但源文件不存在"，不强制"派生类型必须有声明"。
   强制声明需查 capability_canonical_file_registry.yaml 的 is_derived 字段，
   复杂度高且误报风险大。本 gate 聚焦可形式化的"悬空派生"检测。
2. **只检测新增文件**：存量派生文件由人工排查，gate 只防新增。
3. **path 解析**：# [DERIVES_FROM] 后的路径视为相对 project_root，支持正斜杠。
4. **priority=114**：在 DEPGRAPH-PRE-REGISTRATION(113) 之后。
5. **fail-open on read error**：文件读取失败不阻断（避免误伤）。

Usage::

    from zephyr.gov_enforcement.commit_gates.derivation_annotation_gate import (
        make_derivation_annotation_gate,
    )

    registry.register(make_derivation_annotation_gate())
"""

from __future__ import annotations

import logging
import os
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_derivation_annotation_gate"]

# DERIVES_FROM 提取正则——匹配 # [DERIVES_FROM] <path>
# path 允许：字母/数字/下划线/连字符/正斜杠/点
_DERIVES_FROM_RE = re.compile(r"^#\s*\[DERIVES_FROM\]\s*([A-Za-z0-9_./\-]+)", re.MULTILINE)

# 触发检测的文件扩展名（代码 + 配置）
_TRIGGER_EXTENSIONS: tuple[str, ...] = (".py", ".yaml", ".yml")


def _collect_staged_new_files(gateway) -> list[str] | None:
    """获取 staged 新增 .py/.yaml 文件列表（tests/ 豁免）。

    Returns:
        相对路径列表；git diff 失败/异常返回 None（fail-open）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            logger.warning(
                "DERIVATION-ANNOTATION gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        result: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line.strip():
                continue
            fp = line.strip().replace("\\", "/")
            if not fp.endswith(_TRIGGER_EXTENSIONS):
                continue
            if is_test_exempt(fp):
                continue
            result.append(fp)
        return result
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "DERIVATION-ANNOTATION gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _extract_derives_from(abs_path: str) -> str | None:
    """从文件头部提取 # [DERIVES_FROM] <path> 声明。

    Args:
        abs_path: 文件绝对路径。

    Returns:
        派生源路径（相对 project_root）或 None（无声明/读取失败）。
    """
    try:
        with open(abs_path, encoding="utf-8") as f:
            head = "".join(next(f, "") for _ in range(30))
    except (OSError, UnicodeDecodeError):
        return None
    m = _DERIVES_FROM_RE.search(head)
    return m.group(1).strip() if m else None


def _scan_violations(gateway, new_files: list[str]) -> list[str]:
    """扫描悬空派生声明违规。

    返回违规消息列表。
    """
    project_root = gateway.project_root
    violations: list[str] = []

    for rel in new_files:
        abs_path = os.path.join(str(project_root), rel)
        derives_from = _extract_derives_from(abs_path)
        if derives_from is None:
            continue  # 无声明，不检测

        # 校验源文件存在（相对 project_root）
        source_abs = os.path.join(str(project_root), derives_from)
        if not os.path.isfile(source_abs):
            violations.append(f"  {rel}: # [DERIVES_FROM] {derives_from} 源文件不存在（悬空派生声明）")

    return violations


def make_derivation_annotation_gate() -> GateSpec:
    """构造派生关系声明真实性校验 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="DERIVATION-ANNOTATION", priority=114)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        new_files = _collect_staged_new_files(gateway)
        if not new_files:
            return True, ""

        violations = _scan_violations(gateway, new_files)

        if violations:
            detail = (
                "DERIVATION-ANNOTATION：检测到悬空派生声明，\n"
                "  派生文件声明的源文件不存在（SSoT 派生关系真实性）。\n"
                + "\n".join(violations)
                + "\n-> 修复源文件路径，或删除 # [DERIVES_FROM] 声明（若非派生文件）"
            )
            logger.error("DERIVATION-ANNOTATION gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="DERIVATION-ANNOTATION", check=_check, priority=114)
