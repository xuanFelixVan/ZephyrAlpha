# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-ISSUE-RESOLVED-INTEGRITY-001
# [MODULE] zephyr.gov_enforcement.commit_gates.issue_resolved_integrity_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn-only——检测 staged architecture_issue_registry.yaml 中 status=resolved 的条目，验证其 impact 字段中提到的文件路径是否存在（#ARCH-CONSUMERS-ACCURACY-003 Phase 2 / #ARCH-ISSUE-RESOLVED-INTEGRITY-001 治本）；命中返回 passed=True + warning detail（不阻断）；只在 architecture_issue_registry.yaml 被 staged 时触发；跳过含"删除/待建/Phase 2/不本次执行"关键词的条目（合法的不存在）；fail-open（YAML 解析失败不阻断）
# [MODIFY-GUARD] gate_id="ISSUE-RESOLVED-INTEGRITY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 解析失败降级为 fail-open（passed=True）
# [TESTS] tests/governance/commit_gates/test_issue_resolved_integrity_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""issue_resolved_integrity_gate.py — ISSUE-RESOLVED-INTEGRITY warn-only 门禁

#ARCH-CONSUMERS-ACCURACY-003 Phase 2 / #ARCH-ISSUE-RESOLVED-INTEGRITY-001 治本（2026-07-22）：

病根（第一性原理）
-----------------
"Resolved but incomplete" 系统性风险——AI 倾向于在主体工作完成后立即标记
resolved，遗漏收尾登记工作。这与 CONSUMERS 字段准确性问题的病根同构——
派生数据（issue status）被当作声明数据对待，无门禁强制验证 resolved 完整性。

实证：#ARCH-CONSUMERS-ACCURACY-002 标记 resolved 但 P1-4（capability
registry 登记）实际从未完成——capability_id 和 creation_token 双缺失。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册 warn-only 门禁（priority=130）：
  1. 只在 architecture_issue_registry.yaml 被 staged 时触发
  2. 解析 YAML，找到 status=resolved 的条目
  3. 从 impact 字段提取文件路径（.py/.yaml/.json 后缀）
  4. 验证文件路径是否存在
  5. 如果不存在且不含"删除/待建/Phase 2"关键词，warn

设计权衡
--------
1. **warn-only**：历史 resolved 条目可能引用已删除的文件，一次性爆会瘫痪
   commit 流程。
2. **关键词跳过**：含"删除/待建/Phase 2/不本次执行"关键词的条目视为合法的
   不存在（文件被删除或尚未创建），跳过检测。
3. **只检测 impact 字段**：fix_phase 是自由文本格式不统一，难以可靠提取
   文件路径；impact 是 YAML 列表，文件路径在字符串开头，可可靠提取。
4. **fail-open**：YAML 解析失败时不阻断 commit。
5. **priority=130**：原 117 与 RECONCILER-FILE-OPS 撞号（#ARCH-GATE-PRIORITY-UNIQUENESS-001
   fail-closed），后到者让位——REGISTRY-CODE-ANCHOR=129 之后的下一个空位。

Usage::

    from zephyr.gov_enforcement.commit_gates.issue_resolved_integrity_gate import (
        make_issue_resolved_integrity_gate,
    )
    registry.register(make_issue_resolved_integrity_gate())
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = [
    "make_issue_resolved_integrity_gate",
    "extract_file_paths_from_impact",
    "check_impact_files_exist",
]

# 只在 architecture_issue_registry.yaml 被 staged 时触发
_REGISTRY_PATH = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"

# 文件路径正则：匹配含 / 和 .py/.yaml/.json 后缀的路径
_FILE_PATH_RE = re.compile(r"[\w/.\-]+\.(?:py|yaml|json)")

# 跳过关键词——文件不存在但含这些关键词时视为合法（删除/待建/不本次执行）
_SKIP_KEYWORDS = (
    "删除",
    "待建",
    "Phase 2",
    "不本次执行",
    "长期可选",
    "deprecated",
    "预留",
    "superseded",
)


def extract_file_paths_from_impact(impact_value: object) -> list[tuple[str, str]]:
    """从 impact 字段值提取文件路径列表。

    impact 可以是 YAML 列表或字符串。提取含 / 和 .py/.yaml/.json 后缀的路径。

    Args:
        impact_value: impact 字段值（YAML 列表或字符串）

    Returns:
        [(file_path, original_item), ...] 列表。
        file_path 是提取的文件路径，original_item 是原始字符串（用于关键词检测）。
    """
    if isinstance(impact_value, list):
        items = impact_value
    elif isinstance(impact_value, str):
        items = impact_value.split("\n")
    else:
        return []

    paths: list[tuple[str, str]] = []
    for item in items:
        if not isinstance(item, str):
            continue
        for m in _FILE_PATH_RE.finditer(item):
            paths.append((m.group(), item))
    return paths


def check_impact_files_exist(
    issue_id: str,
    impact_value: object,
    project_root: Path,
) -> list[str]:
    """检查 issue 的 impact 字段中提到的文件路径是否存在。

    跳过含"删除/待建/Phase 2"等关键词的条目（合法的不存在）。

    Args:
        issue_id: issue 编号（如 #ARCH-CONSUMERS-ACCURACY-003）
        impact_value: impact 字段值
        project_root: 项目根目录

    Returns:
        不存在文件的 warning 消息列表（空=通过）。
    """
    warnings: list[str] = []
    for path_str, original_item in extract_file_paths_from_impact(impact_value):
        # 跳过含"删除/待建/Phase 2"等关键词的条目
        if any(kw in original_item for kw in _SKIP_KEYWORDS):
            continue
        # 验证文件路径存在
        full_path = project_root / path_str
        if not full_path.exists():
            warnings.append(f"  {issue_id}: impact 文件 '{path_str}' 不存在（可能工作项未完成）")
    return warnings


def make_issue_resolved_integrity_gate() -> GateSpec:
    """构造 ISSUE-RESOLVED-INTEGRITY pre-commit warn-only 门禁（priority=130）。

    检测 staged architecture_issue_registry.yaml 中 status=resolved 的条目，
    验证其 impact 字段中提到的文件路径是否存在。不存在则 warn（passed=True 不阻断）。

    #ARCH-CONSUMERS-ACCURACY-003 Phase 2 / #ARCH-ISSUE-RESOLVED-INTEGRITY-001 治本：
    防止 "resolved but incomplete" —— AI 标记 resolved 但遗漏收尾登记工作。

    Returns:
        GateSpec(gate_id="ISSUE-RESOLVED-INTEGRITY", priority=130)。
        warn-only：检出违规返回 (True, warning_detail)，不阻断 commit。
    """

    def _check(gateway, files: list[str], **_kwargs) -> tuple[bool, str]:
        # 只在 architecture_issue_registry.yaml 被 staged 时触发
        normalized_files = [f.replace("\\", "/") for f in files]
        if _REGISTRY_PATH not in normalized_files:
            return True, ""

        content = _read_staged_file(gateway, _REGISTRY_PATH)
        if not content:
            return True, ""  # fail-open

        # 获取项目根目录
        project_root = getattr(gateway, "project_root", None)
        if project_root is None:
            return True, ""  # fail-open
        project_root = Path(project_root)

        # 解析 YAML
        try:
            import yaml

            data = yaml.safe_load(content)
        except Exception:  # noqa: BLE001 — fail-open
            return True, ""

        if not isinstance(data, dict):
            return True, ""

        entries = data.get("entries", [])
        if not isinstance(entries, list):
            return True, ""

        # 检测每个 status=resolved 的条目
        warnings: list[str] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("status") != "resolved":
                continue
            issue_id = entry.get("issue_id", "?")
            impact = entry.get("impact", [])
            warnings.extend(check_impact_files_exist(issue_id, impact, project_root))

        if warnings:
            detail = (
                "ISSUE-RESOLVED-INTEGRITY (warn-only)：检测到 status=resolved 的条目"
                "引用了不存在的文件（#ARCH-CONSUMERS-ACCURACY-003 治本）\n"
                "  病根：AI 标记 resolved 但遗漏收尾登记工作——"
                "派生数据（issue status）被当作声明数据对待。\n"
                "  修复：①检查文件路径是否正确；②若文件已删除，在 impact 中标注'删除'；"
                "③若文件待建，标注'待建'或'Phase 2'。\n"
                + "\n".join(warnings[:30])
                + (f"\n  ...(+{len(warnings) - 30} more)" if len(warnings) > 30 else "")
            )
            logger.warning("ISSUE-RESOLVED-INTEGRITY gate warn:\n%s", detail)
            return True, detail  # warn-only：passed=True 不阻断
        return True, ""

    return GateSpec(
        gate_id="ISSUE-RESOLVED-INTEGRITY",
        check=_check,
        priority=130,
    )


if __name__ == "__main__":
    """CLI 入口——手动验证 gate 是否可正确构造。"""
    g = make_issue_resolved_integrity_gate()
    print(f"gate_id={g.gate_id}, priority={g.priority}, check_callable={callable(g.check)}")
