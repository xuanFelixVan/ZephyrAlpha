# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] scripts.governance.generators.check_library_tri_consistency
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.generate_library_index（_HALLS/_classify/_SQL_ALL/_DISPLAY_CAP 馆谓词唯一真源）；zephyr.governance.depgraph_schema；zephyr.shared.utils.time_utils
# [CONSUMERS] docs/_working/ultimate_library/TRI_CONSISTENCY.md；S1 FMS-HYGIENE 门（设计消费方）；reconciliation_registry 挂接（待 st-p1b 落地后经其通道追加）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 三层断言=账(总账 PG)↔视图(INDEX+七馆页)↔盘面(磁盘存在性)；全程纯只读断言不修不写账（报告文件除外）；馆谓词/展示上限 import 生成器常量禁复制；regen-clean 支柱=子进程再生成后 git diff --exit-code
# [MODIFY-GUARD] gate_id 不适用（独立 CLI；registry 挂接避让 st-p1b，落地后追加）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=三层一致; exit 1=有漂移断言; exit 2=总账不可达（对标 coverage）；解析/IO 异常降级为断言条目不抛
# [TESTS] tests/library/test_tri_consistency.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_library_tri_consistency.py — 总账↔生成视图↔盘面三层一致性检查器（纯只读）。

分工边界（S5 挖矿簿 §4.4）：library_regen_reconciler=刷新管线（写）、
check_library_coverage=盘↔账两向差集（写报告）、本件=账↔视图↔盘三层断言（纯只读，
不修不写不改账）。三层断言面：

  1. 账↔视图：INDEX 在编总数/各馆在编数 vs 总账按馆谓词 count（deceased/archived 除外）；
     七馆页 rows[:_DISPLAY_CAP] 逐行 (asset_id,kind,status,home) 与总账复核（序敏感）；
     "本页列出"声明数 vs 表格实际行数（断言 S4 计数失真 bug，修后归零）。
  2. regen-clean（支柱 3）：子进程跑 generate_library_index.py 后
     ``git diff --exit-code docs/library/``——非零即手改/漂移。
  3. 视图↔盘面：七馆页 home 列（仅文件系统型 kind）确定性 stride 抽样 N=50
     ``Path.exists()``（读盘不动账；ch:/pg:/mcp: 等 home 非仓库路径不在抽样域）。

Usage::

    python scripts/governance/generators/check_library_tri_consistency.py
    python scripts/governance/generators/check_library_tri_consistency.py --skip-regen
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Final

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[3]
for _p in (str(_PROJECT_ROOT / "src"), str(_PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

__all__ = ["run_tri_check", "parse_index", "parse_page", "check_ledger_vs_view", "check_view_vs_disk"]

# 馆谓词/SQL/展示上限唯一真源=生成器模块常量（禁复制谓词，S5 挖矿簿 §4.4 第 4 条）
from scripts.governance.generators.generate_library_index import (  # noqa: E402
    _DISPLAY_CAP,
    _HALLS,
    _SQL_ALL,
    _classify,
)

_LIBRARY_DIR: Final[Path] = Path("docs/library")
_REPORT: Final[Path] = Path("docs/_working/ultimate_library/TRI_CONSISTENCY.md")
_DISK_SAMPLE_N: Final[int] = 50
# 盘面抽样仅限文件系统型 kind（home=仓库相对路径）；table/mcp_tool/task/backup/infra 的
# home 是 ch:/pg:/mcp:/任务名/绝对路径，Path.exists() 必假阳性——口径对标
# check_library_coverage._SQL_IDS 的盘比较 kinds
_FS_KINDS: Final[frozenset[str]] = frozenset({"file", "module", "doc", "registry"})
_EXIT_PASS: Final[int] = 0
_EXIT_FINDINGS: Final[int] = 1
_EXIT_DB_DOWN: Final[int] = 2

_RE_INDEX_TOTAL: Final[re.Pattern[str]] = re.compile(r"在编资产总数：(\d+)")
_RE_INDEX_HALL_ROW: Final[re.Pattern[str]] = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*\[([a-z]+)\.md\]\([a-z]+\.md\)\s*\|\s*(\d+)\s*\|$",
    re.MULTILINE,
)
_RE_PAGE_COUNTS: Final[re.Pattern[str]] = re.compile(r"条目数（本页列出）：(\d+)｜馆内总数：(\d+)")


def parse_index(text: str) -> dict[str, Any]:
    """解析 INDEX.md：在编总数 + 各馆在编数表。

    Args:
        text: INDEX.md 全文。

    Returns:
        {"total": int|None, "halls": {hall_slug: count}}（解析失败项缺失，由断言面报）。
    """
    halls: dict[str, int] = {}
    for m in _RE_INDEX_HALL_ROW.finditer(text):
        halls[m.group(2)] = int(m.group(3))
    total_m = _RE_INDEX_TOTAL.search(text)
    return {"total": int(total_m.group(1)) if total_m else None, "halls": halls}


def parse_page(text: str) -> dict[str, Any]:
    """解析单馆页：声明数（本页列出/馆内总数）+ 表格数据行 (asset_id,kind,status,home)。

    表格行=以 ``|`` 开头且非表头/分隔线的行；列数不足按原样保留空串。
    """
    counts_m = _RE_PAGE_COUNTS.search(text)
    rows: list[tuple[str, str, str, str]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0] == "asset_id":  # 表头行
            continue
        if set("".join(cells)) <= {"-", ":", ""}:  # 分隔行 |---|---|
            continue
        pad = cells + [""] * (4 - len(cells))
        rows.append((pad[0], pad[1], pad[2], pad[3]))
    return {
        "listed": int(counts_m.group(1)) if counts_m else None,
        "total": int(counts_m.group(2)) if counts_m else None,
        "rows": rows,
    }


def _aggregate_hall_rows(db_rows: list[dict[str, Any]]) -> tuple[dict[str, int], dict[str, list[dict[str, Any]]]]:
    """总账行按馆谓词聚合：返回 (各馆在编数, 各馆行清单)。"""
    hall_counts: dict[str, int] = {name: 0 for name, _t, _p in _HALLS}
    hall_rows: dict[str, list[dict[str, Any]]] = {name: [] for name, _t, _p in _HALLS}
    for row in db_rows:
        hall = _classify(row["kind"], row["home"])
        hall_counts[hall] += 1
        hall_rows[hall].append(row)
    return hall_counts, hall_rows


def _check_index_total(index: dict[str, Any], ledger_total: int, findings: list[str]) -> None:
    """INDEX 在编总数声明断言（缺声明/与账不符）。"""
    if index["total"] is None:
        findings.append("[账↔视图] INDEX.md 缺'在编资产总数'声明行")
    elif index["total"] != ledger_total:
        findings.append(f"[账↔视图] INDEX 在编总数 {index['total']} != 总账 {ledger_total}")


def _check_index_hall_counts(index: dict[str, Any], hall_counts: dict[str, int], findings: list[str]) -> None:
    """INDEX 各馆在编数行断言（缺行/与账不符）。"""
    for name, title, _p in _HALLS:
        declared = index["halls"].get(name)
        if declared is None:
            findings.append(f"[账↔视图] INDEX 缺 {title}({name}) 在编数行")
        elif declared != hall_counts[name]:
            findings.append(f"[账↔视图] INDEX {title} 在编数 {declared} != 总账 {hall_counts[name]}")


def _row_drift_detail(
    page_rows: list[tuple[str, str, str, str]], expected: list[tuple[str, str, str, str]], drift: int | None
) -> str:
    """逐行复核差异 detail（差异可定位=首异行对照；否则=行数口径）。"""
    if drift is not None and drift < len(page_rows) and drift < len(expected):
        return f"首个差异行号 {drift}: 页 {page_rows[drift]} vs 账 {expected[drift]}"
    return f"页 {len(page_rows)} 行 vs 账前 {len(expected)} 行"


def _check_hall_page(
    name: str, page_path: Path, hall_rows: dict[str, list[dict[str, Any]]], total: int, findings: list[str]
) -> None:
    """单馆页断言：馆内总数/本页列出声明 + 展示口径 + 逐行复核（序敏感）。"""
    try:
        page = parse_page(page_path.read_text(encoding="utf-8"))
    except OSError as e:
        findings.append(f"[账↔视图] 馆页 {name}.md 不可读: {e}")
        return
    if page["total"] is None:
        findings.append(f"[账↔视图] {name}.md 缺'馆内总数'声明")
    elif page["total"] != total:
        findings.append(f"[账↔视图] {name}.md 馆内总数 {page['total']} != 总账 {total}")
    # 计数失真断言：声明"本页列出"必须等于表格实际行数（S4 bug 修复后恒真）
    if page["listed"] is None:
        findings.append(f"[账↔视图] {name}.md 缺'条目数（本页列出）'声明")
    elif page["listed"] != len(page["rows"]):
        findings.append(
            f"[账↔视图] {name}.md '本页列出'声明 {page['listed']} != 表格实际 {len(page['rows'])} 行（计数失真）"
        )
    # 展示口径断言：本页列出 == min(馆内总数, _DISPLAY_CAP)
    if page["listed"] is not None and page["listed"] != min(total, _DISPLAY_CAP):
        findings.append(f"[账↔视图] {name}.md '本页列出' {page['listed']} != min(馆内总数 {total}, cap {_DISPLAY_CAP})")
    # 逐行复核（序敏感）：页表格 == 总账该馆前 N 行
    expected = [(r["asset_id"], r["kind"], r["status"], r["home"]) for r in hall_rows[name][: len(page["rows"])]]
    if page["rows"] != expected:
        drift = next(
            (i for i, (got, want) in enumerate(zip(page["rows"], expected, strict=False)) if got != want),
            None,
        )
        detail = _row_drift_detail(page["rows"], expected, drift)
        findings.append(f"[账↔视图] {name}.md 表格与总账逐行复核不一致（{detail}）")


def check_ledger_vs_view(db_rows: list[dict[str, Any]], library_dir: Path) -> list[str]:
    """账↔视图断言：INDEX 计数、七馆页声明数与逐行复核（纯函数，零 IO 于账）。

    Args:
        db_rows: 总账 active 行（_SQL_ALL 同序：ORDER BY kind, home）。
        library_dir: 生成视图目录（INDEX.md + 七馆页）。

    Returns:
        断言失败条目列表（空=一致）。
    """
    findings: list[str] = []
    hall_counts, hall_rows = _aggregate_hall_rows(db_rows)

    index_path = library_dir / "INDEX.md"
    try:
        index_text = index_path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"[账↔视图] INDEX.md 不可读: {e}"]
    index = parse_index(index_text)
    _check_index_total(index, len(db_rows), findings)
    _check_index_hall_counts(index, hall_counts, findings)

    for name, _title, _p in _HALLS:
        _check_hall_page(name, library_dir / f"{name}.md", hall_rows, hall_counts[name], findings)
    return findings


def check_view_vs_disk(library_dir: Path, repo_root: Path, sample: int = _DISK_SAMPLE_N) -> list[str]:
    """视图↔盘面断言：七馆页 home 列确定性 stride 抽样 Path.exists()（读盘不动账）。

    仅抽文件系统型 kind（_FS_KINDS）；ch:/pg:/mcp: 等 home 非仓库路径不在抽样域。
    """
    findings: list[str] = []
    homes: list[str] = []
    for name, _t, _p in _HALLS:
        page_path = library_dir / f"{name}.md"
        try:
            homes.extend(
                row[3] for row in parse_page(page_path.read_text(encoding="utf-8"))["rows"] if row[1] in _FS_KINDS
            )
        except OSError:
            continue
    if not homes:
        return ["[视图↔盘] 七馆页均不可读，抽样中止"]
    step = max(1, len(homes) // sample)
    picked = homes[::step][:sample]
    for home in picked:
        if not (repo_root / home).exists():
            findings.append(f"[视图↔盘] 盘面缺文件: {home}")
    return findings


def check_regen_clean(repo_root: Path) -> list[str]:
    """regen-clean 支柱：子进程再生成后 ``git diff --exit-code docs/library/``。

    生成器自身=合法写路径（Librarian）；本断言只读 diff，不改不修。
    """
    generator = _THIS_FILE.parent / "generate_library_index.py"
    proc = subprocess.run(  # noqa: S603 — 固定脚本路径非用户输入
        [sys.executable, str(generator)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-400:]
        return [f"[regen] 生成器失败 rc={proc.returncode}: {tail.strip()}"]
    diff = subprocess.run(  # noqa: S603 — 固定 git 只读 diff
        ["git", "diff", "--exit-code", "--", str(_LIBRARY_DIR)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if diff.returncode != 0:
        return ["[regen] 再生成后 docs/library/ 存在漂移（手改或账面时移），git diff 非零"]
    return []


def run_tri_check(repo_root: str | Path = ".", skip_regen: bool = False) -> tuple[int, list[str], dict[str, Any]]:
    """三层一致性总入口（纯只读断言+机生报告）。

    Args:
        repo_root: 仓库根。
        skip_regen: True=跳过 regen-clean 支柱（降级态：DB 不可达/在途写入窗口）。

    Returns:
        (exit_code, findings, stats)。exit 0=一致；1=有断言失败；2=总账不可达。
    """
    root = Path(repo_root).resolve()
    library_dir = root / _LIBRARY_DIR
    findings: list[str] = []
    stats: dict[str, Any] = {"ledger_rows": None, "disk_sample": _DISK_SAMPLE_N, "regen": not skip_regen}
    try:
        conn = get_depgraph_pg_connection()
    except Exception as e:  # noqa: BLE001 — DB 不可达=独立退出码（对标 coverage ERROR_CONTRACT）
        findings.append(f"[账] 总账不可达: {e}")
        _write_report(root / _REPORT, findings, stats)
        return _EXIT_DB_DOWN, findings, stats
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_ALL)
            cols = [d[0] for d in cur.description]
            db_rows = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
    except Exception as e:  # noqa: BLE001 — 查询失败同不可达口径
        findings.append(f"[账] 总账查询失败: {e}")
        _write_report(root / _REPORT, findings, stats)
        return _EXIT_DB_DOWN, findings, stats
    finally:
        conn.close()

    stats["ledger_rows"] = len(db_rows)
    findings += check_ledger_vs_view(db_rows, library_dir)
    findings += check_view_vs_disk(library_dir, root)
    if not skip_regen:
        findings += check_regen_clean(root)
    code = _EXIT_PASS if not findings else _EXIT_FINDINGS
    _write_report(root / _REPORT, findings, stats)
    return code, findings, stats


def _write_report(out: Path, findings: list[str], stats: dict[str, Any]) -> None:
    """机生报告落盘（索书号 frontmatter；对标 COVERAGE.md 先例；报告非账非视图）。

    路径随 repo_root（测试写 tmp_path，生产=仓库根），遵守测试隔离铁律。
    """
    stamp = now_utc().isoformat()
    lines = [
        "---",
        'asset_id: "DOC:docs/_working/ultimate_library/TRI_CONSISTENCY.md"',
        'ttl: "task_bound"',
        'doc_type: "audit_report"',
        "---",
        "",
        "# 图书馆三层一致性报告（账↔视图↔盘；纯只读断言）",
        "",
        f"- 构建时戳（UTC）：{stamp}",
        f"- 总账 active 行数：{stats.get('ledger_rows')}",
        f"- regen-clean 支柱：{'执行' if stats.get('regen') else '跳过（--skip-regen）'}",
        f"- **断言失败：{len(findings)} 条**",
        "",
    ]
    lines += [f"- {f}" for f in findings] if findings else ["- 三层一致：零断言失败"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：跑三层断言，打印摘要。"""
    import argparse

    parser = argparse.ArgumentParser(description="图书馆三层一致性检查器（账↔视图↔盘，纯只读）")
    parser.add_argument("--skip-regen", action="store_true", help="跳过 regen-clean 支柱（降级态）")
    parser.add_argument("--root", default=".", help="仓库根（默认 cwd）")
    args = parser.parse_args(argv)
    code, findings, stats = run_tri_check(args.root, skip_regen=args.skip_regen)
    label = {0: "PASS", 1: "FINDINGS", 2: "DB-UNREACHABLE"}.get(code, "FAIL")
    print(f"tri-consistency: {label} ledger_rows={stats.get('ledger_rows')} findings={len(findings)}")
    for f in findings[:50]:
        print(f"  - {f}")
    print(f"report={Path(args.root).resolve() / _REPORT}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
