# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# noqa: m07-orphan  M07豁免: 被 git_commit_gateway.py 的 `from ... import make_ruling_reference_gate` 引用，非真孤儿（worktree 基于 HEAD 时 import 在未提交 diff 中）
# [MODULE] zephyr.gov_enforcement.commit_gates.ruling_reference_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._reference_helpers
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只检测 staged 文件中**新增的** 裁定#NNN 引用（不阻断已有的悬空引用，防阻塞大量历史文件）；fail-closed——registry 缺失或 git 异常时阻断；跳过 tests/ 豁免区；扫描文件类型 .py/.yaml/.yml/.md；正则支持纯数字/带字母后缀（裁定#6 / 裁定#19-A / 裁定#203-B 等）；ruling_id 从工作区 ruling_registry.yaml 提取（commit 后的新真源）；L1 编号空洞检测（RULING_GAP_WARNING）——WARNING 不阻断；L2 同提交原子性门禁（RULING_ATOMICITY_VIOLATION）——新引用不在 HEAD registry 时要求 registry 同 commit，否则 hard block；L2 非 git 仓库（如测试 tmp_path）跳过检测返回 None；**阶段2 hard block 已启用**（裁定#20-G，2026-07-18，_MANUAL_STAGE=False）——新增未登记 裁定#NNN 引用直接阻断
# [MODIFY-GUARD] gate_id="RULING-REFERENCE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；_MANUAL_STAGE=False（阶段2 hard block，裁定#20-G）；priority=74（紧跟 DANGLING-REFERENCE(70) + NOQA-VALIDATION(71) 之后，ARCH-REFERENCE(75) 之前——同属"引用完整性"类检查，集中执行）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 读取异常/git 异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）；阶段2 hard block 下违规直接阻断（裁定#20-G）
# [TESTS] tests/governance/commit_gates/test_ruling_reference_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-062
"""
ruling_reference_gate.py — 裁定#NNN 悬空引用自动检测门禁（RULING-REFERENCE）

检测 staged 文件中**新增的** ``裁定#NNN`` / ``裁定#NNN-X`` 引用（支持纯数字和带字母后缀）
是否在 ruling_registry.yaml 中登记。命中则阻断 commit（``RULING_REFERENCE_VIOLATION``）。

病根（第一性原理，裁定#20-A/B）
--------------------------------
项目 100% AI 开发，每个 session 都是上下文归零的新 AI。新 AI 看到代码中"裁定#19-B"
引用时需要反查裁定内容——但全项目 493 处"裁定#NNN"引用散布在 src/docs/scripts/tests/
AGENTS.md，46+ 不同编号，**无中央登记表**（与 #ARCH-XXX 有 architecture_issue_registry.yaml
作为真源不同）。AI 无法反查裁定编号对应的完整内容，看到裁定#19 不知道是什么。

治本方案（裁定#20-A/B，对标 ARCH-REFERENCE gate）
------------------------------------------------
1. 裁定#20-A：建立 ruling_registry.yaml 作为裁定编号唯一真源（对标 architecture_issue_registry.yaml）
2. 裁定#20-B：本门禁 RULING-REFERENCE（priority=74，紧跟 ARCH-REFERENCE(75) + RULE-FOUR-WAY-ALIGNMENT(76)）
   - L1 编号存在性：新增"裁定#NNN"引用未在 registry 登记则违规
   - L1 编号空洞检测：WARNING 不阻断
   - L2 同提交原子性：新引用不在 HEAD registry 时要求 registry 同 commit
3. 阶段1 manual stage（已完成）：所有违规返回 passed=True + WARNING detail 不阻断（建立基线）
4. 阶段2 hard block（裁定#20-G 已启用，2026-07-18）：移除 _MANUAL_STAGE 标记后硬阻断

治本（2026-07-18，FUNCTION-DUP 消除）
-------------------------------------
5 个与 arch_reference_gate.py 重复的 helper 函数提取到 _reference_helpers.py，
通过参数注入 _extract_refs / _extract_registered_nums / _REGISTRY_REL 差异。
本模块保留 gate 专用逻辑（正则、registry 路径、manual stage、消息格式化）。

Usage::

    from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import make_ruling_reference_gate

    registry.register(make_ruling_reference_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ruling_reference_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_ruling_reference_gate
#   name_en: make_ruling_reference_gate
#   intro: 构造 悬空引用检测门禁 GateSpec。
#   desc: 构造 悬空引用检测门禁 GateSpec。 阶段1（_MANUAL_STAGE=True， 2026-07-18）：所有违规返回 passed=True + WARNING 不阻…；源码 L275-L333
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

from zephyr.gov_enforcement.commit_gates._reference_helpers import (
    check_atomicity,
    collect_new_refs_by_file,
    get_head_content,
    load_head_registered_nums,
    scan_file_violations,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_ruling_reference_gate"]

# 裁定#NNN / 裁定#NNN-X 引用检测正则：匹配 "裁定#6" / "裁定#19" / "裁定#19-A" /
# "裁定#203-B" 等（支持纯数字和带字母后缀）
# 捕获组为编号后缀（纯数字 "6"、带后缀 "19-A"、"203-B"）
_RULING_REF_RE = re.compile(r"裁定#(\d+(?:-[A-Z]+)?)")

# registry 相对路径（对标 architecture_issue_registry.yaml 的设计）
_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"

# 阶段1 manual stage 标记（裁定#20-B）：
# True = 所有违规返回 passed=True + WARNING detail 不阻断（建立基线）
# False = hard block（阶段2 启用，裁定#20-G）
# 阶段2 启用条件（裁定#20-G，2026-07-18 已满足）：
#   - ruling_registry.yaml 全量登记 51 个裁定（48 历史裁定 + #20/#20-D/#218）
#   - 全项目"裁定#NNN"引用 baseline 100% 在 registry 登记（0 个悬空引用）
#   - 治本清理 8 个虚构编号（#166/#167/#168/#169/#181/#182/#185/#187/#188，裁定#20-E）
#   - 重命名 1 个非合规编号（#2026-0701 → #218，裁定#20-F）
_MANUAL_STAGE = False


def _extract_registered_nums(registry_data: dict) -> set[str]:
    """从 ruling_registry.yaml 解析结果提取已登记的裁定编号集合。

    Args:
        registry_data: yaml.safe_load 解析后的 dict。

    Returns:
        已登记的编号字符串集合（如 {"6", "19", "19-A", "19-B", "203-B"}）。
    """
    nums: set[str] = set()
    # 真源字段是 "entries"（对标 architecture_issue_registry.yaml），
    # 测试兼容 "rulings" 别名（早期测试残留）
    entries = registry_data.get("entries")
    if entries is None:
        entries = registry_data.get("rulings", []) or []
    for entry in entries:
        if isinstance(entry, dict):
            rid = entry.get("ruling_id", "")
            if isinstance(rid, str) and rid:
                # ruling_id 形如 "裁定#19-B"，提取编号部分
                m = _RULING_REF_RE.search(rid)
                if m:
                    nums.add(m.group(1))
    return nums


def _extract_refs(content: str) -> set[str]:
    """从文件内容提取所有 裁定#NNN 引用的编号。

    Args:
        content: 文件文本。

    Returns:
        被引用的编号字符串集合（如 {"6", "19", "19-A"}）。
    """
    return set(_RULING_REF_RE.findall(content))


def _load_registered_nums(project_root) -> tuple[bool, str, set[str]]:
    """加载 ruling_registry.yaml 并提取已登记编号。

    Returns:
        (ok, detail, nums)：ok=False 时 detail 含失败原因（fail-closed）。
    """
    from pathlib import Path

    registry_yaml = Path(project_root) / _REGISTRY_REL
    # fail-closed：registry 不存在是环境异常，必须阻断
    # _MANUAL_STAGE=True 时降级为 WARNING（放行）——阶段2 hard block 已启用，此分支不再触发（裁定#20-G）
    if not registry_yaml.is_file():
        if _MANUAL_STAGE:
            return (
                True,
                (
                    f"⚠️ RULING-REFERENCE manual stage：ruling_registry.yaml 未找到，"
                    f"本会话不阻断（阶段1 建立基线，阶段2 已切 False）。路径：{registry_yaml}"
                ),
                set(),
            )
        return (
            False,
            (
                f"ruling_registry.yaml not found (RULING-REFERENCE fail-closed)——"
                f"无法提取已登记编号，禁止放行以防门禁静默失效。"
                f"路径：{registry_yaml}"
            ),
            set(),
        )
    try:
        import yaml

        registry_data = yaml.safe_load(registry_yaml.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        if _MANUAL_STAGE:
            return (
                True,
                f"⚠️ RULING-REFERENCE manual stage：registry 解析失败 {type(e).__name__}: {e}，本会话不阻断。",
                set(),
            )
        return False, f"registry 解析失败 (fail-closed): {type(e).__name__}: {e}", set()
    if not isinstance(registry_data, dict):
        if _MANUAL_STAGE:
            return True, "⚠️ RULING-REFERENCE manual stage：registry 顶层非 dict，本会话不阻断。", set()
        return False, "registry 顶层非 dict（结构异常，fail-closed）。", set()
    registered_nums = _extract_registered_nums(registry_data)
    if not registered_nums:
        if _MANUAL_STAGE:
            return True, "⚠️ RULING-REFERENCE manual stage：registry 无任何已登记裁定编号，本会话不阻断。", set()
        return (
            False,
            (
                "registry 无任何已登记裁定编号（RULING-REFERENCE fail-closed）——"
                "文件可能损坏或 rulings 为空，请检查 ruling_registry.yaml。"
            ),
            set(),
        )
    return True, "", registered_nums


def _format_violations_detail(violations: list[tuple[str, list[str]]]) -> str:
    detail_lines = []
    for rel, nums in violations:
        detail_lines.append(f"  - {rel}: 裁定#{', 裁定#'.join(nums)}")
    return (
        "新增 裁定#NNN 悬空引用（RULING_REFERENCE_VIOLATION）——"
        "以下文件引用了 ruling_registry.yaml 中未登记的编号：\n"
        + "\n".join(detail_lines)
        + "\n修复：在 ruling_registry.yaml 中补登对应条目，"
        "或移除/修正引用。（注：本门禁只检测新增引用，历史悬空引用不阻断。）"
    )


def _detect_id_gaps(registered_nums: set[str]) -> list[int]:
    """L1 编号空洞检测：检测纯数字编号的连续性。

    Returns:
        缺失的编号列表（如 [7, 12]）。
    """
    pure_nums: list[int] = []
    for num in registered_nums:
        # 只检测纯数字编号（不含字母后缀），如 "6", "19", "217"
        if num.isdigit():
            pure_nums.append(int(num))
    if len(pure_nums) < 2:
        return []
    unique_sorted = sorted(set(pure_nums))
    full_range = set(range(unique_sorted[0], unique_sorted[-1] + 1))
    missing = sorted(full_range - set(unique_sorted))
    return missing


def _format_atomicity_detail(violations: list[tuple[str, list[str]]]) -> str:
    lines = [f"  - {rel}: 裁定#{', 裁定#'.join(nums)}" for rel, nums in violations]
    return (
        "同提交原子性违规（RULING_ATOMICITY_VIOLATION）——"
        "以下文件引用了 HEAD registry 中不存在的新编号，"
        "但 ruling_registry.yaml 不在本次 commit 中：\n"
        + "\n".join(lines)
        + "\n修复：将 ruling_registry.yaml 的对应条目更新"
        "加入同一 commit（git add 后一起提交）。"
    )


def _format_gap_warning(missing: list[int]) -> str:
    return (
        f"⚠️ 编号空洞检测（RULING_GAP_WARNING，不阻断）——"
        f"裁定#NNN 纯数字编号存在空洞：{missing}。"
        f"建议：确认空洞编号是否为已删除/合并的条目，"
        f"如是则无需处理；如为分配错误则补登或重新分配。"
    )


def make_ruling_reference_gate() -> GateSpec:
    """构造 裁定#NNN 悬空引用检测门禁 GateSpec。

    阶段1（_MANUAL_STAGE=True，裁定#20-B 2026-07-18）：所有违规返回 passed=True + WARNING 不阻断。
    阶段2（_MANUAL_STAGE=False）：hard block 违规。

    Returns:
        GateSpec(gate_id="RULING-REFERENCE", priority=74)。
        priority=74——紧跟 DANGLING-REFERENCE(70) + NOQA-VALIDATION(71) 之后，
        ARCH-REFERENCE(75) 之前（同属"引用完整性"类检查，集中执行）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        from pathlib import Path

        project_root = Path(gateway.project_root)

        ok, detail, registered_nums = _load_registered_nums(project_root)
        if not ok:
            return False, detail
        # manual stage 下 registry 加载失败时返回 WARNING 放行
        if not registered_nums and _MANUAL_STAGE:
            return True, detail

        violations, error = scan_file_violations(project_root, files, registered_nums, _extract_refs)
        if error is not None:
            if _MANUAL_STAGE:
                return True, f"⚠️ RULING-REFERENCE manual stage：扫描异常 {error}，本会话不阻断。"
            return False, error

        if violations:
            violation_detail = _format_violations_detail(violations)
            if _MANUAL_STAGE:
                return True, f"⚠️ RULING-REFERENCE manual stage（阶段1 不阻断，建立基线）——\n{violation_detail}"
            return False, violation_detail

        # L2: 同提交原子性检查
        head_nums = load_head_registered_nums(project_root, _REGISTRY_REL, _extract_registered_nums)
        if head_nums is not None:
            new_refs_by_file = collect_new_refs_by_file(project_root, files, head_nums, _REGISTRY_REL, _extract_refs)
            if new_refs_by_file:
                registry_rel = _REGISTRY_REL.replace("\\", "/")
                registry_in_commit = any(
                    os.path.relpath(f, str(project_root)).replace("\\", "/") == registry_rel for f in files
                )
                atomicity_violations = check_atomicity(new_refs_by_file, registry_in_commit)
                if atomicity_violations:
                    atomicity_detail = _format_atomicity_detail(atomicity_violations)
                    if _MANUAL_STAGE:
                        return True, f"⚠️ RULING-REFERENCE manual stage（阶段1 不阻断）——\n{atomicity_detail}"
                    return False, atomicity_detail

        # L1: 编号空洞检测（WARNING，不阻断）
        gaps = _detect_id_gaps(registered_nums)
        if gaps:
            return True, _format_gap_warning(gaps)
        return True, ""

    return GateSpec(gate_id="RULING-REFERENCE", check=_check, priority=74)
