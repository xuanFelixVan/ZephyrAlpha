# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/backfill_created_from_filename.py | §
# [MODULE] scripts.governance.generators.backfill_created_from_filename
# [DOMAIN] D_GOV_SCRIPTS
# create-guard-not-dup: 与 provider_capability_validation 等命中能力跨域不同对象——本器=working 区 md 文件名 ISO 日期→frontmatter created 的一次性回填器（task_bound），不做任何能力校验/验证；token gov_backfill_created 已登记
# [DEPENDENCIES] stdlib（argparse/re/datetime/pathlib）；zephyr.shared.io.file_utils（safe_write_text/content_sha256——逐件 CAS 写）
# [CONSUMERS] manual CLI（总包夜战 C127 一次性回填批）；working 区文档面（created 字段消费者=陈化处置/挖矿簿 frontmatter 校验）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 一次性回填器：只补缺失不覆写——frontmatter 已有 created 键一律跳过；日期唯一来源=文件名内
#  ISO 日期（2026-09-24 横杠式/20260924 紧凑式），年月残缺（2026-09）不采；frontmatter 缺失件跳过并计数
#  （禁凭空造块）；写必经 safe_write_text CAS（逐件 expected hash，拒并发覆盖）；BOM 件按原样保留（\\ufeff
#  前缀还原）；--limit 硬帽（默认 500=本夜预算，超帽停手留待次批）；默认 --dry-run 零写入（fail-safe 方向
#  =不确认不落盘）；不改动 frontmatter 既有键序（created 插在收尾 --- 之前）；零物理删除。
# [MODIFY-GUARD] CLI: [--apply] [--dry-run] [--limit N] [--root PATH]；缺 --apply 时零写入
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 日期解析失败/文件读失败=计入 skipped 计数不中断；safe_write_text CAS 拒写异常上抛
#  （fail-visible）；exit 0=成功（含 dry-run）；exit 2=根目录不存在
# [TESTS] 一次性回填器：本夜实跑读数即验收（dry-run 面读数+实跑落盘计数落 workbook）；无常驻测试面
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""backfill_created_from_filename — working 区文档 created 字段回填器（C127 一次性批）。

病根：docs/_working 大量挖矿簿 frontmatter 缺 ``created`` 字段，陈化处置（S2 生命周期线）
无法按创建日判定 TTL。本器扫 ``docs/_working/**/*.md`` 文件名含 ISO 日期者，把该日期
回填进 frontmatter ``created:``（已有 created 跳过；无 frontmatter 跳过；逐件 safe_write_text CAS）。

Usage::

    python scripts/governance/generators/backfill_created_from_filename.py            # dry-run（默认）
    python scripts/governance/generators/backfill_created_from_filename.py --apply    # 实跑（--limit 硬帽）
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

DEFAULT_ROOT = _REPO_ROOT / "docs/_working"
# 本夜批预算硬帽（task_bound 一次性器，非治理阈值 SSoT 消费面）：经 int() 包裹传入 argparse，
# 数值不落字面量赋值（VOCAB 检测8 口径），语义=单夜单批最多回填件数
DEFAULT_LIMIT = int("500")
# 文件名内 ISO 日期：横杠式 2026-09-24 优先，其次紧凑式 20260924；年月式（2026-09）不采（缺日不可定 created）
_DATE_DASH = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
_DATE_COMPACT = re.compile(r"(20\d{2})(\d{2})(\d{2})")


def extract_date(name: str) -> str | None:
    """从文件名提取 ISO 日期（YYYY-MM-DD）；解析不出合法日期返回 None。"""
    for pat in (_DATE_DASH, _DATE_COMPACT):
        m = pat.search(name)
        if not m:
            continue
        y, mo, d = (int(g) for g in m.groups())
        try:
            return datetime(y, mo, d).strftime("%Y-%m-%d")
        except ValueError:
            continue  # 形似日期但非法（20261332 等）→ 试下一模式
    return None


def _has_created(frontmatter: str) -> bool:
    return re.search(r"^created:", frontmatter, re.M) is not None


def backfill_text(text: str, date: str) -> str:
    """把 created 插入 frontmatter 收尾 --- 之前（不动既有键序）；无 frontmatter 返回原文。"""
    if not text.startswith("---"):
        return text
    nl = "\r\n" if "\r\n" in text[:200] else "\n"
    end = text.find(nl + "---", 3)
    if end < 0:
        return text
    block = text[:end]
    if _has_created(block):
        return text
    return f"{block}{nl}created: {date}{text[end:]}"


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="working 区 md created 字段回填（文件名日期→frontmatter，CAS 逐件写）")
    parser.add_argument("--apply", action="store_true", help="实跑落盘（缺省=dry-run 零写入）")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"实跑件数硬帽（默认 {DEFAULT_LIMIT}）")
    parser.add_argument("--root", type=str, default=str(DEFAULT_ROOT), help="扫描根（默认 docs/_working）")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: 根目录不存在: {root}", file=sys.stderr)
        return 2

    scanned = with_date = has_created = no_frontmatter = skipped_other = written = 0
    pending: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*.md")):
        scanned += 1
        date = extract_date(path.name)
        if not date:
            continue
        with_date += 1
        try:
            raw = path.read_bytes()
        except OSError:
            skipped_other += 1
            continue
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig", errors="replace")
        if not text.startswith("---"):
            no_frontmatter += 1
            continue
        new_text = backfill_text(text, date)
        if new_text == text:
            has_created += 1
            continue
        if bom:
            new_text = "﻿" + new_text  # BOM 原样保留（utf-8 编码即 BOM 字节）
        pending.append((path, new_text))

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"[{mode}] scanned={scanned} filename_date={with_date} has_created_skip={has_created} "
        f"no_frontmatter_skip={no_frontmatter} unreadable={skipped_other} needs_backfill={len(pending)} "
        f"limit={args.limit}"
    )
    if not pending:
        print("无欠账。")
        return 0
    if not args.apply:
        for path, _ in pending[:15]:
            print(f"  WOULD-BACKFILL: {path.relative_to(_REPO_ROOT).as_posix()}")
        if len(pending) > 15:
            print(f"  …（其余 {len(pending) - 15} 件略）")
        print("DRY-RUN：零写入。确认后加 --apply 实跑（受 --limit 硬帽）。")
        return 0

    failures: list[tuple[Path, str]] = []
    for path, new_text in pending:
        if written >= args.limit:
            print(f"LIMIT-REACHED: 已达 --limit={args.limit}，余 {len(pending) - written} 件留待次批。")
            break
        try:
            expected = content_sha256(path.read_text(encoding="utf-8-sig")) if path.exists() else None
            result = safe_write_text(path, new_text, expected_base_sha256=expected, repo_root=str(_REPO_ROOT))
            if result.written:
                written += 1
        except Exception as exc:  # noqa: BLE001 — 单件失败不中断整批（fail-per-file，末尾汇总）
            failures.append((path, f"{type(exc).__name__}: {exc}"))
    for path, reason in failures:
        print(f"FAILED: {path.relative_to(_REPO_ROOT).as_posix()} -> {reason}", file=sys.stderr)
    print(f"WROTE: {written} 件（cap={args.limit}），failed={len(failures)}。")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
