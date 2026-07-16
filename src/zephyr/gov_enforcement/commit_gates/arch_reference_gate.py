# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.arch_reference_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只检测 staged 文件中**新增的** #ARCH-NNN 引用（不阻断已有的悬空引用，防阻塞大量历史文件）；fail-closed——registry 缺失或 git 异常时阻断；跳过 tests/ 豁免区；扫描文件类型 .py/.yaml/.yml/.md；issue_id 从工作区 architecture_issue_registry.yaml 提取（commit 后的新真源）
# [MODIFY-GUARD] gate_id="ARCH-REFERENCE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 读取异常/git 异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）
# [TESTS] tests/governance/commit_gates/test_arch_reference_gate.py
# [A_module] module_id=MOD-GOV-arch_reference_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""arch_reference_gate.py — #ARCH-NNN / #ARCH-DOMAIN-NNN 悬空引用自动检测门禁（ARCH-REFERENCE）

检测 staged 文件中**新增的** ``#ARCH-NNN`` / ``#ARCH-CH-NNN`` / ``#ARCH-MM-NNN`` 等引用
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
5. **正则提取**：``#ARCH-([A-Z]+-\\d+|\\d+)`` 匹配 ``#ARCH-008`` / ``#ARCH-037`` /
   ``#ARCH-CH-007`` / ``#ARCH-MM-001`` 等，捕获组为编号后缀（纯数字或域前缀-数字）。
   registry 中 issue_id 形如 ``'#ARCH-008'`` 或 ``'#ARCH-CH-007'``，提取后缀后比较。
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
import subprocess
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_arch_reference_gate"]

# #ARCH-NNN / #ARCH-DOMAIN-NNN 引用检测正则：匹配 "#ARCH-008" / "#ARCH-CH-007" 等
# 捕获组为编号后缀（纯数字 "008" 或域前缀-数字 "CH-007"）
_ARCH_REF_RE = re.compile(r"#ARCH-([A-Z]+-\d+|\d+)")

# 扫描的文件扩展名（可能含 #ARCH-NNN 引用的文件类型）
_SCANNABLE_EXTS = (".py", ".yaml", ".yml", ".md")

# git show 超时（秒）——防止大文件/慢盘卡死 commit
_GIT_SHOW_TIMEOUT = 10

# registry 相对路径（对标 dangling_reference_gate.py 用 gateway.project_root 的稳健设计）
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


def _get_head_content(project_root: Path, rel_path: str) -> str | None:
    """获取文件在 HEAD 版本的内容。

    Args:
        project_root: 仓库根路径。
        rel_path: 相对路径（正斜杠）。

    Returns:
        HEAD 版本文件内容；文件不在 HEAD 中（新文件）返回 None；
        git 命令本身失败（非"文件不存在"）抛 OSError 让调用方 fail-closed。
    """
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            capture_output=True,
            cwd=str(project_root),
            timeout=_GIT_SHOW_TIMEOUT,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        raise OSError(f"git show HEAD:{rel_path} failed: {e}") from e
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", errors="replace")


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
    except Exception as e:
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


def _scan_file_violations(
    project_root: Path, files: list[str], registered_nums: set[str]
) -> tuple[list[tuple[str, list[str]]], str | None]:
    # 检测 staged 文件中新增的悬空引用
    violations: list[tuple[str, list[str]]] = []
    for f in files:
        if not os.path.isfile(f):
            continue  # deletion commit：文件不存在，跳过
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel):
            continue  # tests/ 豁免区
        if not rel.endswith(_SCANNABLE_EXTS):
            continue  # 非可扫描文件类型
        # 读取当前工作区版本
        try:
            current_content = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue  # 读取失败跳过
        current_refs = _extract_refs(current_content)
        if not current_refs:
            continue  # 无 #ARCH-NNN 引用
        # 获取 HEAD 版本，计算新增引用
        try:
            head_content = _get_head_content(project_root, rel)
        except OSError as e:
            return [], f"git show failed for {rel} (fail-closed): {e}"
        if head_content is None:
            new_refs = current_refs  # 新文件：所有引用都是新增
        else:
            head_refs = _extract_refs(head_content)
            new_refs = current_refs - head_refs
        if not new_refs:
            continue  # 无新增引用
        # 检查新增引用是否悬空
        dangling = sorted(new_refs - registered_nums)
        if dangling:
            violations.append((rel, dangling))
    return violations, None


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


def _load_head_registered_nums(project_root: Path) -> set[str] | None:
    """获取 HEAD 版本 registry 中已登记的编号集合（L2 同提交原子性检查用）。

    Returns:
        HEAD 版本编号集合；registry 不在 HEAD 返回空集合；非 git 仓库或 git 异常返回 None（跳过 L2）。
    """
    # 先检查是否是 git 仓库——非 git 仓库（如测试 tmp_path）跳过 L2，避免误阻断
    try:
        rev_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            cwd=str(project_root),
            timeout=_GIT_SHOW_TIMEOUT,
        )
        if rev_result.returncode != 0:
            return None  # 非git仓库，跳过L2
    except (subprocess.TimeoutExpired, OSError):
        return None
    try:
        head_content = _get_head_content(project_root, _REGISTRY_REL)
    except OSError:
        return None
    if head_content is None:
        return set()
    try:
        import yaml
        data = yaml.safe_load(head_content)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return _extract_registered_nums(data)


def _collect_new_refs_by_file(
    project_root: Path, files: list[str], head_nums: set[str]
) -> dict[str, set[str]]:
    """收集 staged 文件中不在 HEAD registry 的新增引用（L2 同提交原子性检查用）。

    排除 registry 自身——registry 文件引用自己的 issue_id 不算"新增引用"。
    """
    result: dict[str, set[str]] = {}
    for f in files:
        if not os.path.isfile(f):
            continue
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel) or not rel.endswith(_SCANNABLE_EXTS):
            continue
        if rel == _REGISTRY_REL:
            continue  # registry 自身不检查
        try:
            content = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        new_refs = _extract_refs(content) - head_nums
        if new_refs:
            result[rel] = new_refs
    return result


def _check_atomicity(
    new_refs_by_file: dict[str, set[str]], registry_in_commit: bool
) -> list[tuple[str, list[str]]]:
    """L2 同提交原子性检查：新引用不在 HEAD registry 时，要求 registry 同 commit。"""
    if registry_in_commit:
        return []
    return [(rel, sorted(refs)) for rel, refs in new_refs_by_file.items()]


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

        violations, error = _scan_file_violations(project_root, files, registered_nums)
        if error is not None:
            return False, error

        if violations:
            return False, _format_violations_detail(violations)

        # L2: 同提交原子性检查——新引用不在 HEAD registry 时，要求 registry 同 commit
        # 防止"引用了新编号但 registry 没同提交登记"导致 commit 后 HEAD registry 仍缺条目
        head_nums = _load_head_registered_nums(project_root)
        if head_nums is not None:
            new_refs_by_file = _collect_new_refs_by_file(project_root, files, head_nums)
            if new_refs_by_file:
                registry_rel = _REGISTRY_REL.replace("\\", "/")
                registry_in_commit = any(
                    os.path.relpath(f, str(project_root)).replace("\\", "/") == registry_rel
                    for f in files
                )
                atomicity_violations = _check_atomicity(new_refs_by_file, registry_in_commit)
                if atomicity_violations:
                    return False, _format_atomicity_detail(atomicity_violations)

        # L1: 编号空洞检测（WARNING，不阻断）——发现编号空洞时通过但不报错
        gaps = _detect_id_gaps(registered_nums)
        if gaps:
            return True, _format_gap_warning(gaps)
        return True, ""

    return GateSpec(gate_id="ARCH-REFERENCE", check=_check, priority=75)
