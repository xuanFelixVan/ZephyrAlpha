#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.governance.dedup_ttl_headers
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants (REPO_ROOT)
# [CONSUMERS] RC-14 存量修复批（后续批：python scripts/governance/dedup_ttl_headers.py --apply）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只删确定性注入块（line1=BLUEPRINT+auto-injected prose 且 line2=# [TTL] permanent 且其后仍有 # [TTL] 行）；注入块是唯一 TTL 时禁删（防造无 TTL 半成品）；幂等（删后复跑零改动）；原头部真值（含 [TTL] limited）原样保留；禁启发式改写非注入形态的重复头（--scan-loose 只列清单归人工批）；换行保真（BRK-086 治本）=读写一律按字节（read_bytes + splitlines(keepends) + write_bytes），禁文本模式整篇读写把 CRLF 折叠成 LF 造出差评级假差异
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单文件读写 OSError 降级计入 failed 并以退出码 2 汇报，不中断批量；git ls-files 失败回退 --files 显式清单（tmp_path 单测可用）
# [TESTS] tests/governance/audit/test_module_id_header_injector_rc14.py::TestDedupTool
# [A_module] module_id=MOD-INF-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 AI/Owner 按需调用的一次性治理 CLI（存量重复头去重 dry-run/apply，人工按需触发，无常驻进程无 cron 无事件订阅义务），属 noqa_exempt_registry.yaml m11 条目列示的"一次性治理脚本"合法场景
# [TTL] permanent
"""dedup_ttl_headers.py — S4 头注入器历史重复 TTL 头去重工具（RC-14 存量修复，裁定#338③ 工单）

背景：reconciliation_registry._module_id_inject_header 旧版只看 content[:500] 有无
[BLUEPRINT] 便整块前置注入，且模板恒带 "# [TTL] permanent"——已有 [TTL] 头的文件
被二次注入重复头（HEAD 实测：466 个带注入标记文件中 196 个重复 TTL 头）。
注入器本体已治本（同工单），本工具负责存量：幂等删除重复注入块，保真值。

判重口径（只动确定性形态，不做启发式改写）：
  命中 = 文件前两行恰好为注入块
      # [BLUEPRINT] <id> | (auto-injected by S4 reconciler) | <tail>
      # [TTL] permanent
    且第 3 行起仍存在 "# [TTL]" 注释行（即被注入文件本有自己的 TTL 头/真值）。
  动作 = 删除前两行注入块，保留原头部（原 [TTL] 值原样保留 → 幂等）。
  文件唯一 TTL 行就是这个注入块时不动（删除会制造无 TTL 半成品，注入器语义禁止）。

用法：
  python scripts/governance/dedup_ttl_headers.py --scan --json out.json   # 生成器口径清单
  python scripts/governance/dedup_ttl_headers.py --dry-run                # 默认，只报不动
  python scripts/governance/dedup_ttl_headers.py --apply                  # 执行去重
  python scripts/governance/dedup_ttl_headers.py --apply --files list.txt # 只处理清单内文件
  python scripts/governance/dedup_ttl_headers.py --scan-loose             # >1 TTL 但非注入形态（人工批清单）

退出码：0=无待处理；1=发现待处理（dry-run/scan）；2=apply 有失败。
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import json
import re

from _shared.constants import REPO_ROOT

INJECTED_PROSE = "(auto-injected by S4 reconciler)"

# 注入块首行：# [BLUEPRINT] <id> | (auto-injected by S4 reconciler) | <tail>
_INJECTED_LINE1_RE = re.compile(
    r"^# \[BLUEPRINT\] (?P<id>\S+) \| (?P<prose>\(auto-injected by S4 reconciler\)) \| (?P<tail>.*)$"
)
_INJECTED_LINE2_RE = re.compile(r"^# \[TTL\] permanent\s*$")
_TTL_LINE_RE = re.compile(r"^\s*#\s*\[TTL\]", re.M)
# 形态 B（确定形态，非启发式）：文件自带 BLUEPRINT 头，头部注释块内出现第 2 条
# `# [TTL] permanent` 重复行（S4 旧注入器把整块模板追加到头部块尾所致）。
_BLUEPRINT_HEADER_RE = re.compile(r"^# \[BLUEPRINT\] ")
_DUP_TTL_LINE_RE = re.compile(r"^# \[TTL\] permanent\s*$")


def _iter_py_files(root: Path, only: set[str] | None = None) -> list[Path]:
    """遍历仓内跟踪口径的 .py 文件（git ls-files，排除未跟踪杂物）。

    root 非 git 仓（单测 tmp_path）且显式给了 --files 清单时，直接按清单回退。

    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    only = {p.replace("\\", "/") for p in only} if only else None
    out = run_subprocess_hidden(
        ["git", "ls-files", "*.py"],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if out.returncode != 0:
        if only is not None:
            return [root / f for f in sorted(only) if f.endswith(".py")]
        return []
    files = []
    for f in out.stdout.splitlines():
        f = f.replace("\\", "/")
        if only is not None and f not in only:
            continue
        files.append(root / f)
    return files


def _read_raw_lines(path: Path) -> list[bytes]:
    """BRK-086 治本：按字节读并切行，保留每条物理行自己的换行符。

    禁 read_text()/write_text() 整篇读写——文本模式的 universal-newlines 会把
    CRLF 折叠成 LF，使"只删 1 行"的改动被 git 报成整篇重写（+N -(N±1) 差评级假差异，
    毁 blame 且触 REGISTRY-MASS-DELETION 误判）。判定用解码后的视图，改写用字节。
    """
    return path.read_bytes().splitlines(keepends=True)


def _decoded_view(raw_lines: list[bytes]) -> list[str]:
    """仅供正则判定的文本视图：逐行解码并把行尾 CRLF 归一为 LF（不参与回写）。"""
    return [ln.decode("utf-8", errors="replace").replace("\r\n", "\n") for ln in raw_lines]


def _header_block_len(lines: list[str]) -> int:
    """头部注释块长度：自 line0 起连续以 '#' 开头的行数（遇到首个非注释行即止）。"""
    n = 0
    for ln in lines:
        if not ln.lstrip().startswith("#"):
            break
        n += 1
    return n


def _duplicate_ttl_index(lines: list[str]) -> int | None:
    """形态 B 判定：头部块内 ≥2 条 `# [TTL] permanent` 时返回应删下标（最后一条）。

    只删重复的最后一条、保留首条真值 → 幂等，且永不制造无 TTL 半成品；
    头部块之外（如 docstring 里提到的 `[TTL]`）一律不参与。
    """
    span = _header_block_len(lines)
    idx = [i for i in range(span) if _DUP_TTL_LINE_RE.match(lines[i])]
    return idx[-1] if len(idx) >= 2 else None


def _classify_injected_block(lines: list[str]) -> tuple[bool, str]:
    """形态 A：整块前置注入（line1=BLUEPRINT(auto-injected)+line2=# [TTL] permanent）。"""
    if not _INJECTED_LINE1_RE.match(lines[0]):
        return False, "line1-not-injected-block"
    if not _INJECTED_LINE2_RE.match(lines[1]):
        return False, "line2-not-injected-ttl"
    if not _TTL_LINE_RE.search("".join(lines[2:])):
        return False, "injected-block-is-only-ttl"
    return True, "duplicate-injected-block"


def dedup_file(path: Path) -> tuple[bool, str]:
    """对单文件执行去重（幂等）：删重复注入块或头部块内重复 TTL 行，保原真值与原始换行字节。

    :return: (是否改动, 说明)
    """
    hit, why = classify_file(path)
    if not hit:
        return False, why
    raw_lines = _read_raw_lines(path)
    if why == "duplicate-header-ttl-line":
        idx = _duplicate_ttl_index(_decoded_view(raw_lines))
        if idx is None:
            return False, "already-clean"
        kept = raw_lines[:idx] + raw_lines[idx + 1 :]
        action = "dropped-duplicate-ttl-line"
    else:
        kept = raw_lines[2:]
        action = "dropped-injected-block"
    path.write_bytes(b"".join(kept))
    return True, action


def classify_file(path: Path) -> tuple[bool, str]:
    """判定单文件是否为可去重形态（形态 A 优先，未命中再判形态 B）。

    :return: (是否命中, 说明)
    """
    try:
        raw_lines = _read_raw_lines(path)
    except OSError as e:
        return False, f"read-failed:{e}"
    lines = _decoded_view(raw_lines)
    if len(lines) < 3:
        return False, "too-short"
    hit, why = _classify_injected_block(lines)
    if hit:
        return True, why
    if _BLUEPRINT_HEADER_RE.match(lines[0]) and _duplicate_ttl_index(lines) is not None:
        return True, "duplicate-header-ttl-line"
    return False, why


def loose_scan(root: Path, only: set[str] | None = None) -> list[dict]:
    """>1 个 "# [TTL]" 注释行但不匹配注入块形态的文件（人工批清单，本工具不自动动）。"""
    report = []
    for path in _iter_py_files(root, only):
        try:
            text = "\n".join(_decoded_view(_read_raw_lines(path)))
        except OSError:
            continue
        n = len(_TTL_LINE_RE.findall(text))
        if n > 1:
            hit, why = classify_file(path)
            if not hit:
                report.append({"file": path.relative_to(root).as_posix(), "ttl_lines": n, "why_not_auto": why})
    return report


def _parse_args() -> argparse.Namespace:
    """_parse_args implementation."""
    parser = argparse.ArgumentParser(description="S4 重复 TTL 头去重（RC-14 存量修复）")
    parser.add_argument("--root", default=str(REPO_ROOT), help="仓库根（默认自动探测）")
    parser.add_argument("--scan", action="store_true", help="只出清单统计")
    parser.add_argument("--scan-loose", action="store_true", help="附报非注入形态的重复 TTL 文件（人工批）")
    parser.add_argument("--apply", action="store_true", help="执行去重（默认 dry-run）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只报不动（缺省即 dry-run；显式旗标对齐 docstring/工单口径，"
                             "并强制压过 --apply 防双旗标歧义）")
    parser.add_argument("--files", default=None, help="限定文件清单（文本文件，每行一个仓内相对路径）")
    parser.add_argument("--json", default=None, help="清单落盘路径")
    parser.add_argument("--limit", type=int, default=0, help="最多处理 N 个文件（0=不限）")
    return parser.parse_args()


def _load_only_files(files_arg: str | None) -> set[str] | None:
    """_load_only_files implementation."""
    if not files_arg:
        return None
    return {
        line.strip().replace("\\", "/")
        for line in Path(files_arg).read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _collect_hits(root: Path, only: set[str] | None, limit: int) -> list[dict]:
    """_collect_hits implementation."""
    hits: list[dict] = []
    for path in _iter_py_files(root, only):
        hit, _why = classify_file(path)
        if not hit:
            continue
        rel = path.relative_to(root).as_posix()
        lines = _decoded_view(_read_raw_lines(path))
        # 与 dedup_file 用同一判据选动作，避免 dry-run 清单与实际改写口径分叉
        shape_a, _why = _classify_injected_block(lines)
        matched = _INJECTED_LINE1_RE.match(lines[0]) if shape_a else None
        hits.append(
            {
                "file": rel,
                "injected_id": matched.group("id") if matched else "header-block-dup",
                "action": "drop-first-2-lines" if shape_a else "drop-duplicate-ttl-line",
            }
        )
        if limit and len(hits) >= limit:
            break
    return hits


def _apply_hits(root: Path, hits: list[dict]) -> int:
    """_apply_hits implementation."""
    failed = 0
    for h in hits:
        path = root / h["file"]
        try:
            changed, why = dedup_file(path)
            if changed:
                print(f"  [applied] {h['file']}")
            else:
                print(f"  [skipped] {h['file']}: {why}")
        except OSError as e:
            failed += 1
            print(f"  [failed] {h['file']}: {e}")
    return failed


def _print_dry_run_preview(hits: list[dict]) -> None:
    """_print_dry_run_preview implementation."""
    for h in hits[:30]:
        print(f"  [dry-run] {h['file']} (injected {h['injected_id']})")
    if len(hits) > 30:
        print(f"  ... 共 {len(hits)} 个（--json 落盘看全量）")


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = _parse_args()

    root = Path(args.root).resolve()
    only = _load_only_files(args.files)

    # --dry-run 显式声明时强制只读（压过 --apply，双旗标歧义取保守侧）
    apply_mode = bool(args.apply) and not args.dry_run

    hits = _collect_hits(root, only, args.limit)
    loose = loose_scan(root, only) if args.scan_loose else []

    summary = {
        "root": str(root),
        "duplicate_injected_block_files": len(hits),
        "loose_duplicate_files": len(loose),
        "mode": "apply" if apply_mode else "dry-run",
    }
    print(json.dumps(summary, ensure_ascii=False))

    if args.json:
        Path(args.json).write_text(
            json.dumps({"summary": summary, "targets": hits, "loose": loose}, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )

    if args.scan:
        return 1 if hits else 0

    if not hits:
        return 0

    if not apply_mode:
        _print_dry_run_preview(hits)
        return 1

    failed = _apply_hits(root, hits)
    print(f"[done] applied={len(hits) - failed} failed={failed}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
