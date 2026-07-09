#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV-SYNC-PANORAMA | docs/_working/2026-07-09-panorama_module_sync_engine.md | §Phase3
# [MODULE] scripts.governance.d5_architecture.syncers.blueprint_frontmatter_reconciler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts.governance.sync_panorama_module
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 单向写入（depgraph→blueprint.md frontmatter）;只写4个核心字段;文档内容不动;蓝图不存在则自动创建最小蓝图(含frontmatter+空正文);blueprint_path为空时用命名约定docs/03_modules/<module_id>.md查找;blueprint_path无扩展名时补.md(DCR-005合规)
# [MODIFY-GUARD] reconcile_blueprint_frontmatter 为对外入口;frontmatter 解析用 _FRONTMATTER_RE 正则;只更新 module_id/responsibility_domain/design_maturity/build_status;_create_minimal_blueprint 为唯一蓝图创建入口;_query_module_BP 优先返回 blueprint_path 非空行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 模块不在depgraph→exit 3;蓝图不存在→exit 0(自动创建);DB异常→exit 4
# [TESTS] tests/governance/test_blueprint_frontmatter_reconciler.py
# [TTL] permanent
# [ARCH-REF] #ARCH-056
"""blueprint_frontmatter_reconciler.py — 蓝图 frontmatter 核心字段对齐（ARCH-056 Phase 3）

从 depgraph 读取模块核心字段，单向写入 blueprint.md frontmatter。
只写 4 个核心字段：module_id / responsibility_domain / design_maturity / build_status。
蓝图文档内容（sections/description/lifecycle）不动。

如蓝图文件不存在，自动创建最小蓝图（含 frontmatter 4 字段 + 空正文 TODO 标记）。
如 blueprint_path 为空（depgraph 未登记路径），使用命名约定 docs/03_modules/<module_id>.md，
文件不存在时自动创建。blueprint_path 无扩展名时自动补 .md（DCR-005 合规）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SRC_DIR = _REPO_ROOT / "src"
for _p in (str(_REPO_ROOT), str(_SRC_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

# ---------------------------------------------------------------------------
# SQL 常量（SQL 集中化，§5.160.2）
# ---------------------------------------------------------------------------
# ORDER BY (blueprint_path IS NULL) → blueprint_path 非空的行优先（正确性：有路径的行
# 更可能是模块主节点而非文件级子节点）；LIMIT 1 → depgraph 同一 blueprint_id 可有多行
_SQL_QUERY_MODULE_BP = (
    "SELECT blueprint_id, domain_id, design_maturity, build_status, blueprint_path "
    "FROM nodes WHERE blueprint_id = %s "
    "ORDER BY (blueprint_path IS NULL), blueprint_path LIMIT 1"
)

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(content: str) -> dict:
    """解析 YAML frontmatter 为 dict（简单实现，不依赖 PyYAML）。"""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def _update_frontmatter(content: str, updates: dict) -> str:
    """更新 frontmatter 中的核心字段，保留文档内容。"""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return content
    fm_text = match.group(1)
    for key, val in updates.items():
        pattern = re.compile(rf"^{re.escape(key)}:\s*.*$", re.MULTILINE)
        new_line = f"{key}: {val}"
        if pattern.search(fm_text):
            fm_text = pattern.sub(new_line, fm_text)
        else:
            fm_text = fm_text.rstrip() + "\n" + new_line
    return f"---\n{fm_text}\n---\n" + content[match.end():]


def _query_module_bp(module_id: str) -> tuple[str, str, str, str] | None:
    """从 depgraph 查询模块的蓝图路径和核心字段。

    Returns: (bp_path, domain_id, design_maturity, build_status) 或 None
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_QUERY_MODULE_BP, (module_id,))
            row = cur.fetchone()
            if not row:
                return None
            if isinstance(row, dict):
                return (
                    row.get("blueprint_path") or "",
                    row.get("domain_id") or "",
                    row.get("design_maturity") or "",
                    row.get("build_status") or "",
                )
            return (row[4] or "", row[1] or "", row[2] or "", row[3] or "")
    finally:
        conn.close()


def _create_minimal_blueprint(bp_file: Path, module_id: str,
                               domain_id: str, dm: str, bs: str) -> int:
    """创建最小 blueprint.md（含 frontmatter 4 核心字段 + 空正文 TODO 标记）。

    父目录不存在时自动创建（mkdir -p）。
    """
    bp_file.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        f"module_id: {module_id}\n"
        f"responsibility_domain: {domain_id}\n"
        f"design_maturity: {dm}\n"
        f"build_status: {bs}\n"
        "doc_type: blueprint\n"
        "ttl: permanent\n"
        "---\n\n"
        f"# {module_id} Blueprint\n\n"
        "> Auto-created by blueprint_frontmatter_reconciler (ARCH-056).\n"
        "> TODO: Fill in module description, sections, dependencies, lifecycle.\n"
    )
    bp_file.write_text(content, encoding="utf-8")
    return 0


def _write_frontmatter_updates(bp_file: Path, module_id: str,
                                domain_id: str, dm: str, bs: str) -> int:
    """读取蓝图文件，更新 frontmatter 核心字段。"""
    content = bp_file.read_text(encoding="utf-8")
    updates = {
        "module_id": module_id,
        "responsibility_domain": domain_id,
    }
    fm = _parse_frontmatter(content)
    if "design_maturity" in fm:
        updates["design_maturity"] = dm
    if "build_status" in fm:
        updates["build_status"] = bs
    new_content = _update_frontmatter(content, updates)
    if new_content != content:
        bp_file.write_text(new_content, encoding="utf-8")
    return 0


def reconcile_blueprint_frontmatter(module_id: str) -> int:
    """对齐单个模块的蓝图 frontmatter。

    Returns: 0=成功/跳过, 3=模块不在depgraph, 4=DB异常
    """
    result = _query_module_bp(module_id)
    if result is None:
        return 3
    bp_path, domain_id, dm, bs = result

    bp_file: Path | None = None
    if bp_path:
        bp_file = Path(bp_path) if Path(bp_path).is_absolute() else _REPO_ROOT / bp_path
        # DCR-005: docs/03_modules/ 下文件必须有 .md 扩展名；
        # depgraph 中 blueprint_path 可能无扩展名（历史数据），此处补 .md
        if bp_file.suffix == "":
            bp_file = bp_file.with_suffix(".md")
    else:
        # blueprint_path 为空，使用命名约定 docs/03_modules/<module_id>.md
        # 文件不存在时由下方 _create_minimal_blueprint 自动创建
        bp_file = _REPO_ROOT / "docs" / "03_modules" / f"{module_id}.md"

    if not bp_file.exists():
        return _create_minimal_blueprint(bp_file, module_id, domain_id, dm, bs)

    return _write_frontmatter_updates(bp_file, module_id, domain_id, dm, bs)
