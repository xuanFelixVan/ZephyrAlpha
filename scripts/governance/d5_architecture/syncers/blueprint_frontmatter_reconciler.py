#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV-SYNC-PANORAMA | docs/_working/2026-07-09-panorama_module_sync_engine.md | §Phase3
# [MODULE] scripts.governance.d5_architecture.syncers.blueprint_frontmatter_reconciler
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts.governance.sync_panorama_module
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 单向写入（depgraph→blueprint.md frontmatter）;只写4个核心字段;文档内容不动;蓝图不存在则标记缺失跳过(不创建文件);blueprint_path为空时用命名约定docs/03_modules/<module_id>.md查找;blueprint_path无扩展名时补.md(DCR-005合规)
# [MODIFY-GUARD] reconcile_blueprint_frontmatter 为对外入口;frontmatter 解析用 _FRONTMATTER_RE 正则;只更新 module_id/responsibility_domain/design_maturity/build_status;蓝图不存在时仅标记缺失不创建文件;_query_module_BP 优先返回 blueprint_path 非空行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 模块不在depgraph→exit 3;蓝图不存在→exit 0(标记缺失跳过);DB异常→exit 4
# [TESTS] tests/governance/test_blueprint_frontmatter_reconciler.py
# [TTL] permanent
# [ARCH-REF] #ARCH-056
"""blueprint_frontmatter_reconciler.py — 蓝图 frontmatter 核心字段对齐（ARCH-056 Phase 3）

从 depgraph 读取模块核心字段，单向写入 blueprint.md frontmatter。
只写 4 个核心字段：module_id / responsibility_domain / design_maturity / build_status。
蓝图文档内容（sections/description/lifecycle）不动。

如蓝图文件不存在，标记缺失并跳过（不创建文件）——避免自动生成大量空蓝图。
如 blueprint_path 为空（depgraph 未登记路径），使用命名约定 docs/03_modules/<module_id>.md
查找已存在的蓝图。blueprint_path 无扩展名时自动补 .md（DCR-005 合规）。
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

try:
    from d5_architecture.panorama_common import weighted_domain_vote, min_maturity as _min_mat
except ImportError:
    import sys as _sys
    _pc_path = str(Path(__file__).resolve().parents[1])  # d5_architecture/
    if _pc_path not in _sys.path:
        _sys.path.insert(0, _pc_path)
    from panorama_common import weighted_domain_vote, min_maturity as _min_mat

# ---------------------------------------------------------------------------
# SQL 常量（SQL 集中化，§5.160.2）
# ---------------------------------------------------------------------------
# ORDER BY (path IS NULL), path → path 非空的行优先（正确性：有路径的行
# 更可能是模块主节点而非文件级子节点）。
# 注意：不使用 LIMIT 1 — 同一 blueprint_id 可有多行（跨域模块），_query_module_bp 在
# Python 中用加权投票聚合，与 align_panoramas._fetch_depgraph_nodes 聚合策略一致。
_SQL_QUERY_MODULE_BP = (
    "SELECT blueprint_id, domain_id, design_maturity, build_status, "
    "blueprint_path, path "
    "FROM nodes WHERE blueprint_id = %s "
    "ORDER BY (path IS NULL), path"
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
        # Fix 2026-07-14: \s* matches newlines, causing cross-line swallowing when
        # the key has an empty value (e.g., "responsibility_domain:\n  - {...}").
        # Use [ \t]* to match only same-line whitespace (spaces/tabs) after colon.
        pattern = re.compile(rf"^{re.escape(key)}:[ \t]*.*$", re.MULTILINE)
        new_line = f"{key}: {val}"
        if pattern.search(fm_text):
            fm_text = pattern.sub(new_line, fm_text)
        else:
            fm_text = fm_text.rstrip() + "\n" + new_line
    return f"---\n{fm_text}\n---\n" + content[match.end():]


def _query_module_bp(module_id: str) -> tuple[str, str, str, str] | None:
    """从 depgraph 查询模块的蓝图路径和核心字段（加权投票聚合）。

    depgraph.nodes 中同一 blueprint_id 可有多行（跨域模块的正常现象，如 MOD-INF-002
    有 79 行分布在 8 个域）。聚合策略与 align_panoramas._fetch_depgraph_nodes 一致：
    - domain_id: 加权投票（panorama_common.weighted_domain_vote，测试文件降权）
    - design_maturity: 取最 design 的状态（panorama_common.min_maturity）
    - build_status: 取第一个非空
    - blueprint_path: 取第一个非空（ORDER BY 保证非空优先）

    Returns: (bp_path, domain_id, design_maturity, build_status) 或 None
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_QUERY_MODULE_BP, (module_id,))
            rows = cur.fetchall()
        if not rows:
            return None
        domains: list[str] = []
        maturities: list[str] = []
        build_status = ""
        bp_path = ""
        for row in rows:
            if isinstance(row, dict):
                dom = row.get("domain_id")
                dm = row.get("design_maturity")
                bs = row.get("build_status")
                path = row.get("blueprint_path")
            else:
                dom = row[1] if len(row) > 1 else None
                dm = row[2] if len(row) > 2 else None
                bs = row[3] if len(row) > 3 else None
                path = row[4] if len(row) > 4 else None
            if dom:
                domains.append(dom)
            if dm:
                maturities.append(dm)
            if not build_status and bs:
                build_status = bs
            if not bp_path and path:
                bp_path = path
        # domain_id: 加权投票（测试文件降权，共享工具 panorama_common）
        domain_id = weighted_domain_vote(rows)
        # design_maturity: 取最 design（min rank，共享工具 panorama_common）
        design_maturity = _min_mat(maturities) if maturities else ""
        return (bp_path or "", domain_id or "", design_maturity or "", build_status or "")
    finally:
        conn.close()


def _write_frontmatter_updates(bp_file: Path, module_id: str,
                                domain_id: str, dm: str, bs: str) -> int:
    """读取蓝图文件，更新 frontmatter 核心字段。

    v2.0.0：design_maturity/build_status 总是写入（depgraph 为真源），
    不再只在已存在时更新——消除 align_panoramas 状态漂移。
    """
    content = bp_file.read_text(encoding="utf-8")
    updates = {
        "module_id": module_id,
        "responsibility_domain": domain_id,
        "design_maturity": dm,
        "build_status": bs,
    }
    new_content = _update_frontmatter(content, updates)
    if new_content != content:
        bp_file.write_text(new_content, encoding="utf-8")
    return 0


# 蓝图扫描根目录（fallback：bp_path 找不到文件时扫描匹配 module_id）
_BP_SCAN_ROOT = _REPO_ROOT / "docs" / "03_modules"
_BP_SCAN_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_BP_SCAN_SKIP_NAMES = {"index.md"}


def _find_blueprint_by_scan(module_id: str) -> list[Path]:
    """扫描 docs/03_modules/ 下所有文件，通过 frontmatter.module_id 匹配。

    Fallback：depgraph 中 blueprint_path 为空或指向错误路径时使用。
    与 align_panoramas._fetch_blueprint_nodes 扫描策略一致。
    返回所有匹配的文件（一个 module_id 可能有多个 .md 文件声明它）。
    """
    results: list[Path] = []
    if not _BP_SCAN_ROOT.exists():
        return results
    for fpath in _BP_SCAN_ROOT.rglob("*"):
        if not fpath.is_file() or fpath.name in _BP_SCAN_SKIP_NAMES:
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        match = _BP_SCAN_FRONTMATTER_RE.match(content)
        if not match:
            continue
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                if key.strip() == "module_id":
                    v = val.strip().strip('"').strip("'")
                    if v == module_id:
                        results.append(fpath)
                    break  # 找到 module_id 行，无论是否匹配都跳过此文件
    return results


def reconcile_blueprint_frontmatter(module_id: str) -> int:
    """对齐单个模块的蓝图 frontmatter。

    Returns: 0=成功/跳过, 3=模块不在depgraph, 4=DB异常
    """
    try:
        result = _query_module_bp(module_id)
    except Exception as exc:
        print(f"[ERROR] DB query failed for {module_id}: {exc}", file=sys.stderr)
        return 4
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
        # blueprint_path 为空，使用命名约定 docs/03_modules/<module_id>.md 查找已存在蓝图
        bp_file = _REPO_ROOT / "docs" / "03_modules" / f"{module_id}.md"

    if not bp_file.exists():
        # Fallback: depgraph 中 blueprint_path 为空或指向错误路径，
        # 扫描 docs/03_modules/ 通过 frontmatter.module_id 匹配
        scanned = _find_blueprint_by_scan(module_id)
        if scanned:
            # 更新所有匹配的文件（一个 module_id 可能有多个 .md 文件）
            for f in scanned:
                _write_frontmatter_updates(f, module_id, domain_id, dm, bs)
            return 0
        else:
            print(f"[WARN] blueprint not found, skip (marked missing): {bp_file}", file=sys.stderr)
            return 0

    return _write_frontmatter_updates(bp_file, module_id, domain_id, dm, bs)
