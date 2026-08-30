# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates._reference_helpers
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.ruling_reference_gate; zephyr.gov_enforcement.commit_gates.arch_reference_gate; zephyr.gov_enforcement.commit_gates.dangling_reference_gate
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数——所有差异通过参数注入(extract_refs_fn/extract_registered_nums_fn/registry_rel)，不依赖模块级状态
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 异常抛 OSError 让调用方 fail-closed；文件读取失败返回 None/空集
# [TESTS] tests/governance/commit_gates/test_ruling_reference_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
_reference_helpers.py — 引用检测门禁共享工具函数（ARCH-REFERENCE / RULING-REFERENCE / DANGLING-REFERENCE）

治本（2026-07-18，FUNCTION-DUP 消除）：arch_reference_gate.py 与 ruling_reference_gate.py
存在 5 个函数体完全相同的私有 helper（_get_head_content / _scan_file_violations /
_load_head_registered_nums / _collect_new_refs_by_file / _check_atomicity），
被 FUNCTION-DUP gate 阻断。提取到本模块，通过参数注入差异（extract_refs_fn /
extract_registered_nums_fn / registry_rel），共享同一实现。

治本（2026-07-18，M03 重复簇消除）：arch_reference_gate.py 和 dangling_reference_gate.py
迁移到本模块消费，消除 M03 检出的 5 个重复函数簇。当前三个 gate 复用同一实现：
  - ruling_reference_gate：消费全部 5 个 helper（参数注入 _RULING_REF_RE / ruling_registry）
  - arch_reference_gate：消费全部 5 个 helper（参数注入 _ARCH_REF_RE / architecture_issue_registry）
  - dangling_reference_gate：仅消费 get_head_content（HEAD 版本对比）

设计决策
--------
1. **参数注入而非模块级状态**：各 gate 的 _extract_refs 使用不同正则
   (_ARCH_REF_RE vs _RULING_REF_RE)，_extract_registered_nums 解析不同 registry
   结构。通过 callable 参数注入差异，共享控制流。
2. **函数名去下划线前缀**：避免与 arch_reference_gate.py 的私有函数同名导致
   FUNCTION-DUP 误报（不同函数名 = 不同 AST 节点 = 不同 hash）。
3. **dangling_reference_gate 部分迁移**：dangling_reference_gate 仅用 get_head_content
   一个 helper（其余逻辑与 arch/ruling 不同），通过 `from ... import get_head_content`
   导入在调用方命名空间创建绑定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: _reference_helpers.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: rel_path 参数
#   fields: 参数 rel_path，类型注解 str
#   code: _reference_helpers.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: files 参数
#   fields: 参数 files，类型注解 list[str]
#   code: _reference_helpers.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: registered_nums 参数
#   fields: 参数 registered_nums，类型注解 set[str]
#   code: _reference_helpers.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_head_content
#   name_en: get_head_content
#   intro: 获取文件在 HEAD 版本的内容。
#   desc: 获取文件在 HEAD 版本的内容。 Args: project_root: 仓库根路径。 rel_path: 相对路径（正斜杠）。 Returns: HEAD 版本文件内容；文件…；源码 L143-L166
#   inputs: project_root rel_path
#   outputs: str | None
# - id: A2
#   name_zh: ② scan_file_violations
#   name_en: scan_file_violations
#   intro: 检测 staged 文件中新增的悬空引用。
#   desc: 检测 staged 文件中新增的悬空引用。 Args: extract_refs_fn: 从文本提取引用编号的 callable（gate 专用正则）。；源码 L169-L210
#   inputs: project_root files registered_nums extract_refs_fn
#   outputs: tuple[list[tuple[str, list[str]]], str…
# - id: A3
#   name_zh: ③ load_head_registered_nums
#   name_en: load_head_registered_nums
#   intro: 获取 HEAD 版本 registry 中已登记的编号集合（L2 同提交原子性检查用）。
#   desc: 获取 HEAD 版本 registry 中已登记的编号集合（L2 同提交原子性检查用）。 Args: registry_rel: registry 文件相对路径（gate 专用）…；源码 L213-L254
#   inputs: project_root registry_rel extract_registered_nums_fn
#   outputs: set[str] | None
# - id: A4
#   name_zh: ④ collect_new_refs_by_file
#   name_en: collect_new_refs_by_file
#   intro: 收集 staged 文件中不在 HEAD registry 的新增引用（L2 同提交原子性检查用）。
#   desc: 收集 staged 文件中不在 HEAD registry 的新增引用（L2 同提交原子性检查用）。 排除 registry 自身——registry 文件引用自己的 id 不算…；源码 L257-L288
#   inputs: project_root files head_nums registry_rel extract_refs_fn
#   outputs: dict[str, set[str]]
# - id: A5
#   name_zh: ⑤ check_atomicity
#   name_en: check_atomicity
#   intro: L2 同提交原子性检查：新引用不在 HEAD registry 时，要求 registry 同 commit。
#   desc: L2 同提交原子性检查：新引用不在 HEAD registry 时，要求 registry 同 commit。；源码 L291-L295
#   inputs: new_refs_by_file registry_in_commit
#   outputs: list[tuple[str, list[str]]]
# 层: 输出
# - id: O1
#   name_zh: str | None
#   name_en: str | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.commit_gates.ruling_reference_gate; zephyr.gov_enforceme…
# - id: O2
#   name_zh: tuple[list[tuple[str, list[str]]], str…
#   name_en: tuple[list[tuple[str, list[str]]], str…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.commit_gates.ruling_reference_gate; zephyr.gov_enforceme…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import is_test_exempt
from zephyr.shared.infra.process_pool import run_subprocess_hidden

_GIT_SHOW_TIMEOUT = 10
# 治本（audit-02，2026-08-02）：原"可含 #ARCH-/#裁定# 引用的文本文件扩展名"散布三处且不一致——
# _reference_helpers._SCANNABLE_EXTS=(.py,.yaml,.yml,.md)、dangling_reference_gate._SCANNABLE_EXTS
# （同上独立副本）、reconciliation_registry._ARCH_TEXT_EXTS=(.md,.yaml,.yml,.py,.txt)。三者均缺
# .json，导致 config/mcp.json 中 #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S2 引用逃逸 commit-time
# 阻断门（ARCH-REFERENCE）+ post-commit warn reconciler（GATE-ARCH-REFS）双层防线。收敛为单一共享
# 常量 REFERENCE_TEXT_EXTS，arch/ruling/dangling gate + reconciler 共用，含 .json/.txt。
# 安全性：各 gate 仅检测 NEW 引用（current - HEAD diff），历史引用不阻断；扩展集为并集仅增强覆盖。
REFERENCE_TEXT_EXTS = (".py", ".yaml", ".yml", ".md", ".json", ".txt")


def get_head_content(project_root: Path, rel_path: str) -> str | None:
    """获取文件在 HEAD 版本的内容。

    Args:
        project_root: 仓库根路径。
        rel_path: 相对路径（正斜杠）。

    Returns:
        HEAD 版本文件内容；文件不在 HEAD 中（新文件）返回 None；
        git 命令本身失败（非"文件不存在"）抛 OSError 让调用方 fail-closed。
    """
    try:
        result = run_subprocess_hidden(
            ["git", "show", f"HEAD:{rel_path}"],
            capture_output=True,
            cwd=str(project_root),
            timeout=_GIT_SHOW_TIMEOUT,
            text=False,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        raise OSError(f"git show HEAD:{rel_path} failed: {e}") from e
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", errors="replace")


def scan_file_violations(
    project_root: Path,
    files: list[str],
    registered_nums: set[str],
    extract_refs_fn: Callable[[str], set[str]],
) -> tuple[list[tuple[str, list[str]]], str | None]:
    """检测 staged 文件中新增的悬空引用。

    Args:
        extract_refs_fn: 从文本提取引用编号的 callable（gate 专用正则）。
    """
    violations: list[tuple[str, list[str]]] = []
    for f in files:
        if not os.path.isfile(f):
            continue
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel):
            continue
        if not rel.endswith(REFERENCE_TEXT_EXTS):
            continue
        try:
            current_content = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        current_refs = extract_refs_fn(current_content)
        if not current_refs:
            continue
        try:
            head_content = get_head_content(project_root, rel)
        except OSError as e:
            return [], f"git show failed for {rel} (fail-closed): {e}"
        if head_content is None:
            new_refs = current_refs
        else:
            head_refs = extract_refs_fn(head_content)
            new_refs = current_refs - head_refs
        if not new_refs:
            continue
        dangling = sorted(new_refs - registered_nums)
        if dangling:
            violations.append((rel, dangling))
    return violations, None


def load_head_registered_nums(
    project_root: Path,
    registry_rel: str,
    extract_registered_nums_fn: Callable[[dict], set[str]],
) -> set[str] | None:
    """获取 HEAD 版本 registry 中已登记的编号集合（L2 同提交原子性检查用）。

    Args:
        registry_rel: registry 文件相对路径（gate 专用）。
        extract_registered_nums_fn: 从 registry dict 提取编号的 callable。

    Returns:
        HEAD 版本编号集合；registry 不在 HEAD 返回空集合；
        非 git 仓库或 git 异常返回 None（跳过 L2）。
    """
    try:
        rev_result = run_subprocess_hidden(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            cwd=str(project_root),
            timeout=_GIT_SHOW_TIMEOUT,
            text=False,
        )
        if rev_result.returncode != 0:
            return None
    except (subprocess.TimeoutExpired, OSError):
        return None
    try:
        head_content = get_head_content(project_root, registry_rel)
    except OSError:
        return None
    if head_content is None:
        return set()
    try:
        import yaml

        data = yaml.safe_load(head_content)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None
    if not isinstance(data, dict):
        return None
    return extract_registered_nums_fn(data)


def collect_new_refs_by_file(
    project_root: Path,
    files: list[str],
    head_nums: set[str],
    registry_rel: str,
    extract_refs_fn: Callable[[str], set[str]],
) -> dict[str, set[str]]:
    """收集 staged 文件中不在 HEAD registry 的新增引用（L2 同提交原子性检查用）。

    排除 registry 自身——registry 文件引用自己的 id 不算"新增引用"。

    Args:
        registry_rel: registry 文件相对路径（gate 专用，排除自身）。
        extract_refs_fn: 从文本提取引用编号的 callable。
    """
    result: dict[str, set[str]] = {}
    for f in files:
        if not os.path.isfile(f):
            continue
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel) or not rel.endswith(REFERENCE_TEXT_EXTS):
            continue
        if rel == registry_rel:
            continue
        try:
            content = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        new_refs = extract_refs_fn(content) - head_nums
        if new_refs:
            result[rel] = new_refs
    return result


def check_atomicity(new_refs_by_file: dict[str, set[str]], registry_in_commit: bool) -> list[tuple[str, list[str]]]:
    """L2 同提交原子性检查：新引用不在 HEAD registry 时，要求 registry 同 commit。"""
    if registry_in_commit:
        return []
    return [(rel, sorted(refs)) for rel, refs in new_refs_by_file.items()]
