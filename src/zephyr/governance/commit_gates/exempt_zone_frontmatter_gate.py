# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.exempt_zone_frontmatter_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed——豁免区文件带 frontmatter doc_type 阻断；历史违规（HEAD 已存在）跳过
# [MODIFY-GUARD] gate_id="EXEMPT-ZONE-FM"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；_EXEMPT_ZONE_PREFIXES/_FRONTMATTER_EXTS/_extract_doc_type
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] (True, msg)=通过；False=阻断（新引入豁免区 frontmatter 文件）；git ls-tree 失败不豁免继续检查
# [TESTS] tests/governance/commit_gates/test_exempt_zone_frontmatter_gate.py
# [A_module] module_id=MOD-GOV-exempt_zone_frontmatter_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""exempt_zone_frontmatter_gate.py — 豁免区 frontmatter 门禁（Phase 3 reconciler->gate 收敛）

从 make_exempt_zone_frontmatter_reconciler（post-commit warn）升级为 pre-commit 阻断 gate。
豁免区（docs/_working/ / docs/_archive/ / .runtime/ / .trae/ / templates/）文件若带
frontmatter + 非空 doc_type，说明本应放正式目录却被塞进豁免区——commit 前即阻断。

历史违规豁免（progressive_convergence）：用 git ls-tree HEAD 判断文件是否已存在。
- 存在 -> 历史违规，跳过（允许正常维护）
- 不存在 -> 新引入违规，阻断

治本动机：原 reconciler 是 post-commit 非阻断 warn，仅记录报告。本 gate 在 commit()
内嵌等效校验，阻断新引入的豁免区 frontmatter 文件。
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_exempt_zone_frontmatter_gate"]

_EXEMPT_ZONE_PREFIXES = (
    "docs/_working/",
    "docs/_archive/",
    ".runtime/",
    ".trae/",
    "docs/01_policies_and_standards/templates/",
)
_FRONTMATTER_EXTS = (".md", ".yaml", ".yml")


def _extract_doc_type(content: str, is_markdown: bool) -> str:
    """从 frontmatter 提取 doc_type 值；无 frontmatter/doc_type 返回空串。

    与 reconciliation_registry._extract_doc_type 同源逻辑（Phase 3 gate 迁移复制）。
    """
    lines = content.splitlines()
    if not lines or not lines[0].lstrip().startswith("---"):
        return ""
    if is_markdown:
        block: list[str] = []
        closed = False
        for line in lines[1:]:
            if line.lstrip().startswith("---"):
                closed = True
                break
            block.append(line)
        if not closed:
            return ""
    else:
        block = lines[1:]
    for line in block:
        stripped = line.strip()
        if stripped.startswith("doc_type:"):
            return stripped[len("doc_type:"):].strip().strip('"').strip("'")
    return ""


def make_exempt_zone_frontmatter_gate() -> GateSpec:
    """构造豁免区 frontmatter 门禁 GateSpec（fail-closed 阻断型，含历史违规豁免）。

    Returns:
        GateSpec(gate_id="EXEMPT-ZONE-FM", priority=87)。
        priority=87——在 ID-UNIQUENESS(86) 之后。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root
        violations: list[str] = []
        historical: list[str] = []

        for f in files:
            if not os.path.isfile(f):
                continue
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            matched_zone = ""
            for zone in _EXEMPT_ZONE_PREFIXES:
                if rel.startswith(zone):
                    matched_zone = zone
                    break
            if not matched_zone:
                continue
            if not rel.endswith(_FRONTMATTER_EXTS):
                continue

            # 历史违规豁免：git ls-tree HEAD 判断文件是否已存在
            try:
                result = subprocess.run(
                    ["git", "ls-tree", "HEAD", rel],
                    capture_output=True,
                    cwd=str(project_root),
                    timeout=10,
                )
                if result.stdout.strip():
                    historical.append(rel)
                    continue
            except (subprocess.TimeoutExpired, OSError):
                pass  # git 失败时不豁免，继续检查

            try:
                content = Path(f).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            doc_type = _extract_doc_type(content, rel.endswith(".md"))
            if doc_type:
                violations.append(f"{rel} (doc_type={doc_type}, zone={matched_zone})")

        if violations:
            return False, (
                f"EXEMPT-ZONE-FM: {len(violations)} exempt-zone file(s) with frontmatter doc_type "
                f"(should be in formal directory): {'; '.join(violations)}"
            )
        return True, (
            f"no exempt-zone frontmatter violations"
            + (f" (historical skipped: {', '.join(historical)})" if historical else "")
        )

    return GateSpec(gate_id="EXEMPT-ZONE-FM", check=_check, priority=87)
