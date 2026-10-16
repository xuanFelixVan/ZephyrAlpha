#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §archive-sanitize
# [MODULE] scripts.ops.archive_sanitize
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] zephyr.ai_layer.redline.negative_list (REAL_KEY_MARKER/DENY_ENV_PATTERNS 键名常量 SSOT 引用，禁复制字面量)
# [CONSUMERS] scripts.session_worktree (archive-sanitize 子命令委托); scripts.git_commit (docs/_archive 写面前置变换);
#             tests/scripts/test_archive_sanitize.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 三变换只作用于归档面（docs/_archive/ 落地面）：①frontmatter doc_type:→archived_doc_type:
#              （EXEMPT-ZONE-FM 豁免区禁带 doc_type）；②frontmatter ttl: 非 permanent→permanent
#              （FILE-PLACEMENT-TTL 规则2：task_bound 禁入永久区）——①②只动 frontmatter 块（两道门禁
#              只查 frontmatter）；③实盘键名字样→[REDACTED:REAL_KEY_NAME] 作用**全文**（body 命中照样拦，
#              2026-10-15 22 件实锤全在正文表格行；键名常量真源=zephyr.ai_layer.redline.negative_list
#              DENY_ENV_PATTERNS/REAL_KEY_MARKER，禁复制字面量——清单语义变更走 OBJ_R，本件只消费）;
#              已含裸 [REDACTED:REAL_KEY_NAME] 的文件=remaining_markers 如实上报（新文件落 docs/_archive
#              仍会被 REAL-KEY-REFERENCE-SCAN 增量判据拦——历史存量靠 HEAD 基线豁免，新档案引用需 Owner
#              裁定准入，本件不越权放行也不静默丢弃）;
#              dry-run 默认（与 session_worktree archive 同口径），--execute 才落盘
# [MODIFY-GUARD] zephyr.ai_layer.redline.negative_list（键名常量真源，本件只读）
# [STABILITY] new
# [SAFETY] M（改写归档件内容：frontmatter 两键改写+键名脱敏；正文零触碰；dry-run 默认）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sanitize_archive_text 永不抛（输入非文本/无 frontmatter 原样返回+零计数）;
#                  CLI exit 0=成功/ dry-run; exit 1=部分文件写失败
# [TESTS] tests/scripts/test_archive_sanitize.py（三类变换实测/正文不触碰/无 frontmatter 原样/键名常量命中）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动批面为人工触发 CLI（dry-run 默认与 archive 同口径），自动写面由 git_commit.py 提交流程事件驱动调用，非常驻服务/非 daemon/非自启
# create-guard-not-dup: 本模块是归档写面前置文本脱敏器（frontmatter doc_type/ttl 改名+键名字样归一），非 secret_provider（secrets.py 凭证存取能力）的第二实现——命中词 is key name/sanitize file 系键名脱敏散文与文件名 sanitize_file 的碰撞
"""archive_sanitize — 收班归档写面前置脱敏（st-diskp0-20261015 D4）。

病灶（2026-10-15 归档三连拦，实锤当晚）：死会话收班归档落地 docs/_archive 时——
  ① 138 件带 frontmatter ``doc_type:`` 被 EXEMPT-ZONE-FM 拦（豁免区禁带 doc_type）；
  ② 3 件 ``ttl: task_bound`` 被 FILE-PLACEMENT-TTL 规则2 拦（task_bound 禁入永久区）；
  ③ 22 件含实盘键名字样被 REAL-KEY-REFERENCE-SCAN 硬拦（NL-2 增量判据）。
本件把三道拦阻的前置变换自动化：doc_type:→archived_doc_type:、ttl:非 permanent→permanent、
实盘键名（negative_list DENY_ENV_PATTERNS 族）→[REDACTED:REAL_KEY_NAME]。

接线面（两处，语义同源）：
  - 手动批面：``python scripts/session_worktree.py archive-sanitize <paths...> [--execute]``
  - 自动写面：scripts/git_commit.py 提交前对 staged docs/_archive/ 件自动跑同一变换
    （env ZEPHYR_ARCHIVE_SANITIZE=0 一键停用=回滚通道）。

边界（如实声明）：已含裸 [REDACTED:REAL_KEY_NAME] 的**新**归档件仍会被
REAL-KEY-REFERENCE-SCAN 的增量判据拦（该判据禁出现该字样，白名单仅 secret_registry.yaml
本体与 SECRETS.md）——本件把这类件如实记为 remaining_markers 上报 Owner 裁定准入
（裁定#503 准入面同型），不越权放行、不静默丢弃、不伪造"已脱敏"。
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.ai_layer.redline.negative_list import DENY_ENV_PATTERNS, REAL_KEY_MARKER  # noqa: E402

#: 归档面根（写面判定前缀；变换逻辑本身与路径无关，写面自动接线用）
ARCHIVE_ZONE_PREFIX = "docs/_archive/"

#: 键名 token 形状：env-var 式大写下划线串（含 Marker 自身+后缀形态一并归一）
_TOKEN_RE = re.compile(r"\[REDACTED:REAL_KEY_NAME\]_[A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*")
_MARKER_HEAD_RE = re.compile(r"^\[REDACTED:REAL_KEY_NAME\]_")


def _is_key_name(token: str) -> bool:
    """token 是否命中负面清单键名族（fnmatch 大小写敏感，与 NL-2 deny 语义同口径）。"""
    return any(fnmatch.fnmatch(token, pat) for pat in DENY_ENV_PATTERNS)


def _split_frontmatter(text: str, is_markdown: bool) -> tuple[list[str], list[str]] | None:
    """切 frontmatter 行与正文行（与 exempt_zone_frontmatter_gate 同口径：md 需闭合 ---）。

    无 frontmatter → None。返回 (frontmatter_lines_with_endings, body_lines_with_endings)。
    """
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].lstrip().startswith("---"):
        return None
    if is_markdown:
        for i in range(1, len(lines)):
            if lines[i].lstrip().startswith("---"):
                return lines[: i + 1], lines[i + 1 :]
        return None
    return lines[1:], []


def sanitize_archive_text(text: str, *, is_markdown: bool = True) -> tuple[str, dict]:
    """三变换纯函数核（永不抛）。

    作用域：①②（doc_type/ttl）只动 frontmatter 块——两道门禁（EXEMPT-ZONE-FM/
    FILE-PLACEMENT-TTL）只查 frontmatter；③（实盘键名）动**全文**——
    REAL-KEY-REFERENCE-SCAN 扫的是整个 staged 内容面（body 命中照样拦，2026-10-15
    22 件实锤全在正文表格行）。

    Returns:
        (new_text, stats)——stats: {doc_type_renamed, ttl_permanent, keys_redacted,
        remaining_markers}；零变化时 new_text is text（同一对象，调用方可判 is 判等）。
    """
    stats: dict = {"doc_type_renamed": 0, "ttl_permanent": 0, "keys_redacted": 0, "remaining_markers": 0}
    try:
        split = _split_frontmatter(text, is_markdown)
        if split is None:
            new_text, n_red, _ = _redact_key_names(text)
            stats["keys_redacted"] = n_red
            stats["remaining_markers"] = new_text.count(REAL_KEY_MARKER)
            if not n_red:
                return text, stats
            return new_text, stats
        fm_lines, body_lines = split
        out_lines: list[str] = []
        for line in fm_lines:
            stripped = line.strip()
            # ① doc_type: → archived_doc_type:（保留原值与行尾换行形态）
            m_doc = re.match(r"^(\s*)doc_type:(\s*)(.*?)(\r?\n?)$", line)
            if m_doc and m_doc.group(3).strip():
                out_lines.append(f"{m_doc.group(1)}archived_doc_type:{m_doc.group(2)}{m_doc.group(3)}{m_doc.group(4)}")
                stats["doc_type_renamed"] += 1
                continue
            # ② ttl: 非 permanent → permanent（只动值 token，行尾注释面保留）
            m_ttl = re.match(r"^(\s*)ttl:(\s*)(.*?)(\r?\n?)$", line)
            if m_ttl:
                rest = m_ttl.group(3)
                parts = rest.split(None, 1)
                value = parts[0].strip('"').strip("'") if parts else ""
                tail = rest[len(parts[0]) :] if parts else ""
                if value and value != "permanent":
                    out_lines.append(f"{m_ttl.group(1)}ttl:{m_ttl.group(2)}permanent{tail}{m_ttl.group(4)}")
                    stats["ttl_permanent"] += 1
                    continue
            new_line, n_red, _ = _redact_key_names(line)
            stats["keys_redacted"] += n_red
            out_lines.append(new_line)
        # ③ 键名脱敏作用域=全文：body 行同样过 Marker 归一（正文表格行是 22 件实锤病灶位）
        for line in body_lines:
            new_line, n_red, _ = _redact_key_names(line)
            stats["keys_redacted"] += n_red
            out_lines.append(new_line)
        new_text = "".join(out_lines)
        stats["remaining_markers"] = new_text.count(REAL_KEY_MARKER)
        if not (stats["doc_type_renamed"] or stats["ttl_permanent"] or stats["keys_redacted"]):
            return text, stats
        return new_text, stats
    except Exception:  # noqa: BLE001 — 变换失败原样返回（宁不脱敏不毁原文）
        stats["remaining_markers"] = text.count(REAL_KEY_MARKER)
        return text, stats


def _redact_key_names(line: str) -> tuple[str, int, list[str]]:
    """行内键名字样 → REAL_KEY_MARKER（常量真源=negative_list，禁复制字面量）。"""
    hits: list[str] = []
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        token = m.group(0)
        if _MARKER_HEAD_RE.match(token):
            # "[REDACTED:REAL_KEY_NAME]_XXX" 后缀形态归一为裸 Marker
            count += 1
            return REAL_KEY_MARKER
        if _is_key_name(token):
            hits.append(token)
            count += 1
            return REAL_KEY_MARKER
        return token

    return _TOKEN_RE.sub(_sub, line), count, hits


def sanitize_file(path: Path, *, execute: bool) -> dict:
    """单文件脱敏（dry-run 只报；--execute 原地写）。返回 per-file 报告。"""
    report: dict = {"path": str(path), "changed": False, "write_failed": False}
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        report["read_failed"] = str(e)
        return report
    is_md = path.suffix.lower() == ".md"
    new_text, stats = sanitize_archive_text(text, is_markdown=is_md)
    report["stats"] = stats
    report["changed"] = new_text is not text
    if report["changed"] and execute:
        try:
            path.write_text(new_text, encoding="utf-8", newline="")
        except OSError as e:
            report["write_failed"] = str(e)
    return report


def sanitize_paths(paths: list[Path], *, execute: bool) -> tuple[list[dict], int]:
    """批量入口：文件或目录（目录=递归 .md/.yaml/.yml）。返回 (报告列表, 退出码)。"""
    targets: list[Path] = []
    for p in paths:
        if p.is_dir():
            targets.extend(
                sorted(q for q in p.rglob("*") if q.suffix.lower() in (".md", ".yaml", ".yml") and q.is_file())
            )
        elif p.is_file():
            targets.append(p)
    reports = [sanitize_file(t, execute=execute) for t in targets]
    failed = sum(1 for r in reports if r.get("write_failed") or r.get("read_failed"))
    return reports, (1 if failed else 0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="归档写面前置脱敏（doc_type/ttl/实盘键名 三变换；dry-run 默认）",
    )
    parser.add_argument("paths", nargs="+", help="归档件或目录（docs/_archive/... ）")
    parser.add_argument("--execute", action="store_true", help="真正写盘（默认 dry-run 只报）")
    parser.add_argument("--json", action="store_true", help="JSON 输出（供写面接线消费）")
    args = parser.parse_args(argv)

    reports, rc = sanitize_paths([Path(p) for p in args.paths], execute=args.execute)
    if args.json:
        print(json.dumps({"execute": args.execute, "reports": reports}, ensure_ascii=False, indent=1))
    else:
        changed = [r for r in reports if r.get("changed")]
        marked = [r for r in reports if r.get("stats", {}).get("remaining_markers")]
        print(
            f"[ARCHIVE-SANITIZE] 扫描 {len(reports)} 件（execute={args.execute}）: "
            f"将变换 {len(changed)} 件；含裸 Marker 需 Owner 裁定 {len(marked)} 件"
        )
        for r in changed[:20]:
            s = r["stats"]
            print(
                f"  - {r['path']}  doc_type×{s['doc_type_renamed']} ttl×{s['ttl_permanent']} key×{s['keys_redacted']}"
            )
        for r in marked[:20]:
            print(f"  ! 裸 Marker 需 Owner 准入（REAL-KEY-REFERENCE-SCAN 增量判据仍会拦新件）: {r['path']}")
        if not args.execute and changed:
            print("  [DRY-RUN] 未写盘（--execute 才落盘）")
    return rc


if __name__ == "__main__":
    sys.exit(main())
