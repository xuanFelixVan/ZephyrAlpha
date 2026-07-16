# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.dangling_reference_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 只检测 staged 文件中**新增的** AGENTS.md §X.Y 引用（不阻断已有的悬空引用，防阻塞大量历史文件）；fail-closed——AGENTS.md 缺失或 git 异常时阻断；跳过 tests/ 豁免区；不检测 blueprint.md §X.Y 或"蓝图 MOD-XXX §X.Y"（蓝图内部引用非 AGENTS.md）；扫描文件类型 .py/.yaml/.yml/.md；章节号从工作区 AGENTS.md 提取（commit 后的新真源）
# [MODIFY-GUARD] gate_id="DANGLING-REFERENCE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AGENTS.md 读取异常/git 异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）
# [TESTS] tests/governance/commit_gates/test_dangling_reference_gate.py
# [A_module] module_id=MOD-GOV-dangling_reference_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""dangling_reference_gate.py — AGENTS.md §X.Y 悬空引用自动检测门禁（DANGLING-REFERENCE）

检测 staged 文件中**新增的** ``AGENTS.md §X.Y`` 引用是否指向 AGENTS.md 中
实际存在的章节号。命中则阻断 commit（``DANGLING_REFERENCE_VIOLATION``）。

病根（第一性原理）
-----------------
AGENTS.md 章节重构（如 §6 从"六大纪律+子章节 §6.1~§6.16"重构为"关键路径"无子章节）
后，项目中所有 ``§6.9`` / ``§6.10`` / ``§6.14`` 引用变为悬空引用。现有
``audit_broken_links.py`` 明确跳过 ``#anchor`` / ``§X.Y`` 锚点引用
（``URL_PREFIXES`` 含 ``"#"``），AGENTS.md L286 声明的 ``broken_link_detector``
canonical 扩展点也不覆盖 §X.Y——全项目无任何机制检测 AGENTS.md 章节号引用有效性。

结果：章节重构产生的悬空引用只能靠人工审核发现，且自动生成文件（manifest/tree）
的 __manifest__ 块若含悬空引用，reconciler 重生后会持续回归。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（``--no-verify`` 绕不过）注册门禁，检测
**新增的** ``AGENTS.md §X.Y`` 引用是否悬空。只检测新增引用（通过 git diff HEAD
对比），不阻断已有的悬空引用——否则会阻塞 30+ 处历史 §6.14 引用的 commit，
门禁一上线就卡死工作流。增量检测让历史悬空引用逐步清理，新引用零容忍。

设计决策
--------
1. **只检测新增引用**：通过 ``git show HEAD:<path>`` 获取 HEAD 版本，比较
   新增引用集。新文件（HEAD 不存在）的引用全部视为新增。避免一上线就阻塞
   大量历史文件。
2. **fail-closed**：AGENTS.md 不存在 / git 异常时阻断——环境异常必须阻断，
   否则门禁静默失效（对标 directory_contract_gate.py fail-closed 设计）。
3. **章节号从工作区 AGENTS.md 提取**：commit 后 AGENTS.md 的新真源即工作区
   版本，用工作区版本提取 valid_sections 是正确的。
4. **priority=70**：在 CREATE-GUARD(60) 之后、CAPABILITY-OVERLAP(200) 之前
   执行——悬空引用是文档质量问题，优先级低于目录契约/搭便车/创建守卫等
   根因级检查，但应在能力重叠检查前完成。
5. **不检测 blueprint.md §X.Y**：蓝图内部引用是合法的（blueprint.md 有自己
   的章节体系），只有 ``AGENTS.md §X.Y`` 才检测。
6. **正则提取章节号**：``^#{2,4}\\s+(\\d+(?:\\.\\d+)*)`` 匹配 ``## 4.``、
   ``### 4.1``、``#### 4.2.1`` 等格式，捕获组为 ``4`` / ``4.1`` / ``4.2.1``。
7. **引用正则**：``AGENTS\\.md\\s*§(\\d+(?:\\.\\d+)*)`` 匹配
   ``AGENTS.md §6.9`` / ``AGENTS.md§6.9`` 等变体。

Usage::

    from zephyr.gov_enforcement.commit_gates.dangling_reference_gate import make_dangling_reference_gate

    registry.register(make_dangling_reference_gate())
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

__all__ = ["make_dangling_reference_gate"]

# AGENTS.md 章节号提取正则：匹配 ## N. / ### N.M / #### N.M.K
# 捕获组为章节号字符串（如 "4" / "4.1" / "4.2.1"）
_SECTION_HEADING_RE = re.compile(r"^#{2,4}\s+(\d+(?:\.\d+)*)", re.MULTILINE)

# AGENTS.md §X.Y 引用检测正则：匹配 "AGENTS.md §6.9" / "AGENTS.md§6.9" 等变体
# 捕获组为被引用的章节号字符串
_AGENTS_REF_RE = re.compile(r"AGENTS\.md\s*§(\d+(?:\.\d+)*)")

# 扫描的文件扩展名（可能含 AGENTS.md §X.Y 引用的文件类型）
_SCANNABLE_EXTS = (".py", ".yaml", ".yml", ".md")

# git show 超时（秒）——防止大文件/慢盘卡死 commit
_GIT_SHOW_TIMEOUT = 10


def _extract_valid_sections(agents_md_content: str) -> set[str]:
    """从 AGENTS.md 内容提取有效章节号集合。

    Args:
        agents_md_content: AGENTS.md 文件文本。

    Returns:
        有效章节号字符串集合（如 {"4", "4.1", "4.2.1", "6", ...}）。
    """
    return set(_SECTION_HEADING_RE.findall(agents_md_content))


def _extract_refs(content: str) -> set[str]:
    """从文件内容提取所有 AGENTS.md §X.Y 引用的章节号。

    Args:
        content: 文件文本。

    Returns:
        被引用的章节号字符串集合。
    """
    return set(_AGENTS_REF_RE.findall(content))


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
        # git 命令本身不可达 -> 抛异常让调用方 fail-closed
        raise OSError(f"git show HEAD:{rel_path} failed: {e}") from e
    if result.returncode != 0:
        # 文件不在 HEAD 中（新文件）-> 返回 None 表示无历史版本
        return None
    return result.stdout.decode("utf-8", errors="replace")


def _load_valid_sections(project_root: Path) -> tuple[set[str] | None, tuple[bool, str] | None]:
    """加载 AGENTS.md 有效章节号集合；失败时返回 (None, error_response)。"""
    agents_md = project_root / "AGENTS.md"
    # fail-closed：AGENTS.md 不存在是环境异常，必须阻断
    if not agents_md.is_file():
        return None, (False, (
            "AGENTS.md not found at project root (DANGLING-REFERENCE fail-closed)——"
            "无法提取有效章节号，禁止放行以防门禁静默失效。"
        ))
    # 提取有效章节号（工作区版本 = commit 后的新真源）
    try:
        agents_content = agents_md.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return None, (False, f"AGENTS.md read failed (fail-closed): {e}")
    valid_sections = _extract_valid_sections(agents_content)
    if not valid_sections:
        # AGENTS.md 存在但无任何章节号——可能是文件损坏，fail-closed
        return None, (False, (
            "AGENTS.md 无任何有效章节号（DANGLING-REFERENCE fail-closed）——"
            "文件可能损坏，请检查 AGENTS.md 章节结构。"
        ))
    return valid_sections, None


def make_dangling_reference_gate() -> GateSpec:
    """构造 AGENTS.md §X.Y 悬空引用检测门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="DANGLING-REFERENCE", priority=70)。
        priority=70——在 CREATE-GUARD(60) 之后、CAPABILITY-OVERLAP(200) 之前执行
        （悬空引用是文档质量问题，优先级低于根因级检查）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root
        valid_sections, err = _load_valid_sections(project_root)
        if err is not None:
            return err

        # 检测 staged 文件中新增的悬空引用
        violations: list[tuple[str, list[str]]] = []  # (rel_path, [dangling_sections])
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
                continue  # 读取失败跳过（其他 gate 会处理）

            current_refs = _extract_refs(current_content)
            if not current_refs:
                continue  # 无 AGENTS.md §X.Y 引用

            # 获取 HEAD 版本，计算新增引用
            try:
                head_content = _get_head_content(project_root, rel)
            except OSError as e:
                # git 命令失败 -> fail-closed 阻断
                return False, f"git show failed for {rel} (fail-closed): {e}"

            if head_content is None:
                # 新文件：所有引用都是新增
                new_refs = current_refs
            else:
                head_refs = _extract_refs(head_content)
                new_refs = current_refs - head_refs

            if not new_refs:
                continue  # 无新增引用

            # 检查新增引用是否悬空
            dangling = sorted(new_refs - valid_sections)
            if dangling:
                violations.append((rel, dangling))

        if violations:
            detail_lines = []
            for rel, secs in violations:
                detail_lines.append(f"  - {rel}: §{', §'.join(secs)}")
            return False, (
                "新增 AGENTS.md 悬空引用（DANGLING_REFERENCE_VIOLATION）——"
                "以下文件引用了 AGENTS.md 中不存在的章节号：\n"
                + "\n".join(detail_lines)
                + "\n修复：检查 AGENTS.md 实际章节号，或移除/修正引用。"
                "（注：本门禁只检测新增引用，历史悬空引用不阻断。）"
            )
        return True, ""

    return GateSpec(gate_id="DANGLING-REFERENCE", check=_check, priority=70)
