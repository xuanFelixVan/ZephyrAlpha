# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.doc_ref_broken_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .md 文件中 markdown 链接的相对路径指向不存在文件时阻断 commit；只检测新增文件（diff-filter=A）；in-process 正则 + os.path.exists 检测；URL/锚点链接豁免；文件读取失败 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="DOC-REF-BROKEN"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——IO/正则异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_doc_ref_broken_gate.py
# [A_module] module_id=MOD-GOV-doc_ref_broken_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""doc_ref_broken_gate.py — 文档相对路径断裂引用阻断门禁（DOC-REF-BROKEN）

检测 staged 新增 .md 文件中 markdown 链接的相对路径是否指向不存在文件——
断链让文档导航失效，违反"文档可发现性"原则。

病根（第一性原理）
-----------------
新 AI 写文档时常引用不存在的相对路径：
  1. ``[详情](./architecture.md)`` 但文件名拼错（architectur.md）
  2. ``[模块](../src/foo.py)`` 但路径算错层级
  3. ``[设计](docs/design.md)`` 但文件未创建
断链让读者点击后 404，文档信任度下降。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 正则提取 markdown 链接 ``[text](target)``
  2. URL/mailto/锚点链接豁免（``http://`` / ``https://`` / ``mailto:`` / ``#`` / ``ftp://``）
  3. 去掉锚点部分（``target#section`` -> ``target``）
  4. 相对 .md 文件目录解析，``os.path.exists`` 检查
  5. 不存在 -> 断链 -> 违规

设计权衡
--------
1. **只检测新增 .md 文件**：存量断链由后续清理。本 gate 防止新增断链。
2. **in-process 正则**：无 subprocess，纯 re.findall + os.path.exists，自包含。
3. **fail-open on IO error**：文件读取失败不阻断。
4. **URL 豁免**：网络 URL 不在本地检查（可能暂时不可达但 URL 有效）。
5. **priority=88**：在 ORPHAN-MODULE(86) 之后、FUNCTION-DUP(90) 之前。

Usage::

    from zephyr.governance.commit_gates.doc_ref_broken_gate import make_doc_ref_broken_gate

    registry.register(make_doc_ref_broken_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import re

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_doc_ref_broken_gate"]

# markdown 链接正则：[text](target)，捕获 target
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# URL/锚点豁免前缀（这些链接不在本地检查）
_URL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "#")


def _is_url_or_anchor(target: str) -> bool:
    """判断链接目标是否是 URL/锚点（豁免本地检查）。"""
    return target.lower().startswith(_URL_PREFIXES)


def _find_broken_refs(content: str, md_dir: str) -> list[str]:
    """查找 .md 文件中所有断裂的相对路径引用。

    Args:
        content: .md 文件内容。
        md_dir: .md 文件所在目录（绝对路径）。

    Returns:
        断裂引用的目标路径列表（原始 target 字符串）。
    """
    broken: list[str] = []
    for match in _MD_LINK_RE.finditer(content):
        target = match.group(2).strip()
        if not target:
            continue
        if _is_url_or_anchor(target):
            continue  # URL/锚点豁免
        # 去掉锚点部分
        target_no_anchor = target.split("#", 1)[0]
        if not target_no_anchor:
            continue  # 纯锚点 "#section"
        # 相对 .md 目录解析
        resolved = os.path.normpath(os.path.join(md_dir, target_no_anchor))
        if not os.path.exists(resolved):
            broken.append(target)
    return broken


def make_doc_ref_broken_gate() -> GateSpec:
    """构造文档相对路径断裂引用阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="DOC-REF-BROKEN", priority=88)。
        priority=88——在 ORPHAN-MODULE(86) 之后、FUNCTION-DUP(90) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .md 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "DOC-REF-BROKEN gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "DOC-REF-BROKEN gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 2. 过滤 .md 文件（.md 文件无需 tests/ 豁免，但保留 is_test_exempt 检查防御性）
        new_md_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".md") and not is_test_exempt(f)
        ]
        if not new_md_files:
            return True, ""

        # 3. 获取 worktree root
        try:
            toplevel_result = gateway._run_git(
                ["git", "rev-parse", "--show-toplevel"]
            )
            if toplevel_result.returncode == 0:
                wt_root = toplevel_result.stdout.strip()
            else:
                wt_root = str(gateway.project_root)
        except Exception:
            wt_root = str(gateway.project_root)

        # 4. 解析为绝对路径
        abs_files = []
        for rel in new_md_files:
            if os.path.isabs(rel):
                abs_files.append(rel)
            else:
                abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
        abs_files = [f for f in abs_files if os.path.isfile(f)]
        if not abs_files:
            return True, ""

        # 5. 检测每个 .md 文件的断裂引用
        all_violations: list[str] = []
        for abs_path in abs_files:
            try:
                content = open(abs_path, "r", encoding="utf-8", errors="replace").read()
            except OSError as e:
                logger.warning(
                    "DOC-REF-BROKEN gate skip file %s: 读取失败(%s: %s)。",
                    abs_path, type(e).__name__, e,
                )
                continue

            md_dir = os.path.dirname(abs_path)
            broken = _find_broken_refs(content, md_dir)
            if broken:
                rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
                # 去重并取前 5 个
                seen: set[str] = set()
                unique_broken: list[str] = []
                for b in broken:
                    if b not in seen:
                        seen.add(b)
                        unique_broken.append(b)
                refs_str = "; ".join(unique_broken[:5])
                all_violations.append(f"文档引用断裂 {rel_name}: {refs_str}")

        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, detail
        return True, ""

    return GateSpec(gate_id="DOC-REF-BROKEN", check=_check, priority=88)
