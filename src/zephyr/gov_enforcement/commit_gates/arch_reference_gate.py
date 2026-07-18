# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.arch_reference_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._reference_helpers (get_head_content, scan_file_violations, load_head_registered_nums, collect_new_refs_by_file, check_atomicity); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只检测 staged 文件中**新增的** #ARCH-NNN 引用（不阻断已有的悬空引用，防阻塞大量历史文件）；fail-closed——registry 缺失或 git 异常时阻断；跳过 tests/ 豁免区；扫描文件类型 .py/.yaml/.yml/.md；正则支持纯数字/两段式/多段式域前缀（#ARCH-008 / #ARCH-CH-007 / #ARCH-GOV-SHIM-001，2026-07-17 多段式支持治本 ARCH-GOV-SHIM-001 漏检）；issue_id 从工作区 architecture_issue_registry.yaml 提取（commit 后的新真源）；L1 编号空洞检测（ARCH_GAP_WARNING）——按域前缀分组检测编号连续性，WARNING 不阻断；L2 同提交原子性门禁（ARCH_ATOMICITY_VIOLATION）——新引用不在 HEAD registry 时要求 registry 同 commit，否则硬阻断；L2 非 git 仓库（如测试 tmp_path）跳过检测返回 None，避免误阻断
# [MODIFY-GUARD] gate_id="ARCH-REFERENCE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 读取异常/git 异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）
# [TESTS] tests/governance/commit_gates/test_arch_reference_gate.py
# [A_module] module_id=MOD-GOV-arch_reference_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""arch_reference_gate.py — #ARCH-NNN / #ARCH-DOMAIN-NNN 悬空引用自动检测门禁（ARCH-REFERENCE）

检测 staged 文件中**新增的** ``#ARCH-NNN`` / ``#ARCH-CH-NNN`` / ``#ARCH-MM-NNN`` /
``#ARCH-GOV-SHIM-NNN`` 等引用（支持纯数字、两段式域前缀和多段式域前缀）
是否在 architecture_issue_registry.yaml 中登记。命中则阻断 commit（``ARCH_REFERENCE_VIOLATION``）。

病根（第一性原理）
-----------------
architecture_issue_registry.yaml 编号铁律#6 规定："任何 #ARCH-XXX 引用必须
在本注册表有对应条目，禁止 grep-and-claim 占位"。但此前无代码强制——新 AI 可
不查 registry 就用未登记编号，违反铁律后只能靠人工审核发现。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（``--no-verify`` 绕不过）注册门禁，检测
**新增的** ``#ARCH-NNN`` 引用是否在 registry 中有对应 issue_id。只检测新增引用
（通过 git diff HEAD 对比），不阻断已有的悬空引用——否则会阻塞历史文件。
增量检测让历史悬空引用逐步清理，新引用零容忍。

设计决策
--------
1. **只检测新增引用**：通过 ``git show HEAD:<path>`` 获取 HEAD 版本，比较
   新增引用集。新文件（HEAD 不存在）的引用全部视为新增。
2. **fail-closed**：registry 不存在 / git 异常时阻断——环境异常必须阻断。
3. **issue_id 从工作区 registry 提取**：commit 后 registry 的新真源即工作区版本。
4. **priority=75**：紧跟 DANGLING-REFERENCE(70) 之后、CAPABILITY-OVERLAP(200) 之前
   ——同属"引用完整性"类检查，集中执行。
5. **正则提取**：``#ARCH-([A-Z]+(?:-[A-Z]+)*-\\d+|\\d+)`` 匹配 ``#ARCH-008`` /
   ``#ARCH-037`` / ``#ARCH-CH-007`` / ``#ARCH-MM-001`` / ``#ARCH-GOV-SHIM-001`` 等，
   捕获组为编号后缀（纯数字、两段式域前缀-数字、或多段式域前缀-数字）。
   registry 中 issue_id 形如 ``'#ARCH-008'`` / ``'#ARCH-CH-007'`` / ``'#ARCH-GOV-SHIM-001'``，
   提取后缀后比较。多段式支持治本 ARCH-GOV-SHIM-001 三段式格式漏检（2026-07-17）。
6. **不扫 commit message**：只扫 ``files`` 参数（commit 目标文件）。

Usage::

    from zephyr.gov_enforcement.commit_gates.arch_reference_gate import make_arch_reference_gate

    registry.register(make_arch_reference_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

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

__all__ = ["make_arch_reference_gate"]

# #ARCH-NNN / #ARCH-DOMAIN-NNN 引用检测正则：匹配 "#ARCH-008" / "#ARCH-CH-007" /
# "#ARCH-GOV-SHIM-001" 等（支持纯数字、两段式域前缀和多段式域前缀）
# 捕获组为编号后缀（纯数字 "008"、域前缀-数字 "CH-007"、或多段式 "GOV-SHIM-001"）
# 多段式支持治本 ARCH-GOV-SHIM-001 三段式格式漏检（2026-07-17）
_ARCH_REF_RE = re.compile(r"#ARCH-([A-Z]+(?:-[A-Z]+)*-\d+|\d+)")

# registry 相对路径（对标 dangling_reference_gate.py 用 gateway.project_root 的稳健设计）
# 治本（M03，2026-07-18）：_SCANNABLE_EXTS / _GIT_SHOW_TIMEOUT 已下沉到 _reference_helpers，
# 本模块不再需要（消除 M03 重复簇：get_head_content / scan_file_violations /
# load_head_registered_nums / collect_new_refs_by_file / check_atomicity 5 个函数
# 与 _reference_helpers 重复）。
_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"


def _extract_registered_nums(registry_data: dict) -> set[str]:
    """从 architecture_issue_registry.yaml 解析结果提取已登记的 ARCH 编号集合。

    Args:
        registry_data: yaml.safe_load 解析后的 dict。

    Returns:
        已登记的编号字符串集合（如 {"008", "019", "037"}）。
    """
    nums: set[str] = set()
    for entry in registry_data.get("entries", []) or []:
        if isinstance(entry, dict):
            iid = entry.get("issue_id", "")
            if isinstance(iid, str) and iid:
                # issue_id 形如 "#ARCH-008"，提取数字部分
                m = _ARCH_REF_RE.search(iid)
                if m:
                    nums.add(m.group(1))
    return nums


def _extract_refs(content: str) -> set[str]:
    """从文件内容提取所有 #ARCH-NNN 引用的编号。

    Args:
        content: 文件文本。

    Returns:
        被引用的编号字符串集合（如 {"008", "037"}）。
    """
    return set(_ARCH_REF_RE.findall(content))


def _load_registered_nums(project_root: Path) -> tuple[bool, str, set[str]]:
    registry_yaml = project_root / _REGISTRY_REL
    # fail-closed：registry 不存在是环境异常，必须阻断
    if not registry_yaml.is_file():
        return False, (
            f"architecture_issue_registry.yaml not found (ARCH-REFERENCE fail-closed)——"
            f"无法提取已登记编号，禁止放行以防门禁静默失效。"
            f"路径：{registry_yaml}"
        ), set()
    # 加载 registry 并提取已登记编号（工作区版本 = commit 后的新真源）
    try:
        import yaml
        registry_data = yaml.safe_load(registry_yaml.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return False, f"registry 解析失败 (fail-closed): {type(e).__name__}: {e}", set()
    if not isinstance(registry_data, dict):
        return False, "registry 顶层非 dict（结构异常，fail-closed）。", set()
    registered_nums = _extract_registered_nums(registry_data)
    if not registered_nums:
        return False, (
            "registry 无任何已登记 ARCH 编号（ARCH-REFERENCE fail-closed）——"
            "文件可能损坏或 entries 为空，请检查 architecture_issue_registry.yaml。"
        ), set()
    return True, "", registered_nums


def _format_violations_detail(violations: list[tuple[str, list[str]]]) -> str:
    detail_lines = []
    for rel, nums in violations:
        detail_lines.append(f"  - {rel}: #ARCH-{', #ARCH-'.join(nums)}")
    return (
        "新增 #ARCH-NNN 悬空引用（ARCH_REFERENCE_VIOLATION）——"
        "以下文件引用了 architecture_issue_registry.yaml 中未登记的编号：\n"
        + "\n".join(detail_lines)
        + "\n修复：在 architecture_issue_registry.yaml 中补登对应条目，"
        "或移除/修正引用。（注：本门禁只检测新增引用，历史悬空引用不阻断。）"
    )


def _detect_id_gaps(registered_nums: set[str]) -> dict[str, list[int]]:
    """L1 编号空洞检测：检测每个域前缀的编号连续性。

    Returns:
        {domain_prefix: [missing_numbers]} 字典，如 {"CH": [6, 8]}。
    """
    from collections import defaultdict
    by_domain: dict[str, list[int]] = defaultdict(list)
    for num in registered_nums:
        parts = num.split("-")
        if len(parts) == 2 and parts[0].isalpha() and parts[1].isdigit():
            by_domain[parts[0]].append(int(parts[1]))
        elif num.isdigit():
            by_domain[""].append(int(num))
    gaps: dict[str, list[int]] = {}
    for domain, nums in by_domain.items():
        if len(nums) < 2:
            continue
        unique_sorted = sorted(set(nums))
        full_range = set(range(unique_sorted[0], unique_sorted[-1] + 1))
        missing = sorted(full_range - set(unique_sorted))
        if missing:
            gaps[domain] = missing
    return gaps


def _format_atomicity_detail(violations: list[tuple[str, list[str]]]) -> str:
    lines = [f"  - {rel}: #ARCH-{', #ARCH-'.join(nums)}" for rel, nums in violations]
    return (
        "同提交原子性违规（ARCH_ATOMICITY_VIOLATION）——"
        "以下文件引用了 HEAD registry 中不存在的新编号，"
        "但 architecture_issue_registry.yaml 不在本次 commit 中：\n"
        + "\n".join(lines)
        + "\n修复：将 architecture_issue_registry.yaml 的对应条目更新"
        "加入同一 commit（git add 后一起提交）。"
    )


def _format_gap_warning(gaps: dict[str, list[int]]) -> str:
    parts = []
    for domain, missing in gaps.items():
        prefix = f"ARCH-{domain}-" if domain else "ARCH-"
        parts.append(f"{prefix}{missing}")
    return (
        "⚠️ 编号空洞检测（ARCH_GAP_WARNING，不阻断）——"
        "以下 ARCH 编号域存在编号空洞：\n  "
        + "\n  ".join(parts)
        + "\n建议：确认空洞编号是否为已删除/合并的条目，"
        "如是则无需处理；如为分配错误则补登或重新分配。"
    )


def make_arch_reference_gate() -> GateSpec:
    """构造 #ARCH-NNN 悬空引用检测门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="ARCH-REFERENCE", priority=75)。
        priority=75——紧跟 DANGLING-REFERENCE(70) 之后、CAPABILITY-OVERLAP(200) 之前
        （同属"引用完整性"类检查，集中执行）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        ok, detail, registered_nums = _load_registered_nums(project_root)
        if not ok:
            return False, detail

        # 治本（M03，2026-07-18）：scan_file_violations 等共享 helper 已下沉到
        # _reference_helpers，通过 _extract_refs 参数注入本 gate 专用正则。
        violations, error = scan_file_violations(
            project_root, files, registered_nums, _extract_refs
        )
        if error is not None:
            return False, error

        if violations:
            return False, _format_violations_detail(violations)

        # L2: 同提交原子性检查——新引用不在 HEAD registry 时，要求 registry 同 commit
        # 防止"引用了新编号但 registry 没同提交登记"导致 commit 后 HEAD registry 仍缺条目
        head_nums = load_head_registered_nums(
            project_root, _REGISTRY_REL, _extract_registered_nums
        )
        if head_nums is not None:
            new_refs_by_file = collect_new_refs_by_file(
                project_root, files, head_nums, _REGISTRY_REL, _extract_refs
            )
            if new_refs_by_file:
                registry_rel = _REGISTRY_REL.replace("\\", "/")
                registry_in_commit = any(
                    os.path.relpath(f, str(project_root)).replace("\\", "/") == registry_rel
                    for f in files
                )
                atomicity_violations = check_atomicity(new_refs_by_file, registry_in_commit)
                if atomicity_violations:
                    return False, _format_atomicity_detail(atomicity_violations)

        # L1: 编号空洞检测（WARNING，不阻断）——发现编号空洞时通过但不报错
        gaps = _detect_id_gaps(registered_nums)
        if gaps:
            return True, _format_gap_warning(gaps)
        return True, ""

    return GateSpec(gate_id="ARCH-REFERENCE", check=_check, priority=75)
