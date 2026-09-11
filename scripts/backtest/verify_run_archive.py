# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.verify_run_archive
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.backtest.run_archive
# [CONSUMERS] SOP-D §6 巡检（可入 batch）; 批次决策点自查
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 四类违规巡检（SOP-D §6）：台账有 run_id 无目录/目录无 meta.json/文件名非 ASCII/单文件>50MB 无压缩；只读报告不自动修复；DECAY-* 为巡检追加行非 run（豁免类1，摘要单列）；CH 不可达时类1降级跳过（fail-open），磁盘类2-4 照查
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 磁盘根不可读->退出码2; 发现违规->退出码1; 干净->退出码0; --json 输出机器可读清单
# [TESTS] python scripts/backtest/verify_run_archive.py --root tmp/_verify_smoke_runs (smoke)
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  CLI 运维巡检工具（AGENTS.md 代码归类表 A 类一次性运维/诊断脚本），非常驻服务，巡检按需/入 batch 事件触发
"""run 档案图书馆巡检器（SOP-D §6：让图书馆员是代码，不是自觉）。

规范真源：docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md §6。
裁定来源：docs/_working/2026-09-11-backtest-evidence-log-discussion.md §八 R1（巡检随 R1 配套）。

四类违规（只报告，不修复）：
    1 MISSING_ARCHIVE  台账（node_verdict/strategy_screen）有 run_id 但 runs/ 无目录——结论翻不到过程
    2 ORPHAN_DIR       目录无 meta.json——无主档案
    3 NAMING_VIOLATION 文件名含非 ASCII/空格，或目录名不符合 run_id 编号，或 meta.run_id 与目录名不一致
    4 OVERSIZED_FILE   单文件 >50MB 且非压缩后缀（.gz/.gzip/.zip/.xz/.parquet 视作可接受形态）

用法::
    python scripts/backtest/verify_run_archive.py            # 真实档案区巡检
    python scripts/backtest/verify_run_archive.py --json     # 机器可读
    python scripts/backtest/verify_run_archive.py --root X   # 指定档案根（测试/演练）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.backtest.run_archive import _RUN_ID_RE, _RUNS_ROOT  # noqa: E402

_OVERSIZE_BYTES = 50 * 1024 * 1024
_ARCHIVE_SUFFIXES = {".gz", ".gzip", ".zip", ".xz", ".parquet"}
_ASCII_NAME_RE = re.compile(r"^[\x21-\x7e]+$")
_LEDGER_RUN_RE = re.compile(r"^(VAL|SCR)-")
_DECAY_PREFIX = "DECAY-"

# 台账 run_id 候选源（类1）；DECAY-* 是衰减巡检追加行的事件 id，非 run（豁免，摘要单列）
_LEDGER_TABLES = ("c1_backtest.node_verdict", "c1_backtest.strategy_screen")


def _ledger_run_ids() -> tuple[set[str], set[str], str | None]:
    """(run ids, decay ids, error)。CH 不可达返回 error（类1降级跳过，fail-open）。"""
    try:
        from zephyr.data import ch_reader
    except Exception as exc:  # noqa: BLE001 — 导入失败同不可达处理
        return set(), set(), f"ch_reader import failed: {exc}"
    runs: set[str] = set()
    decays: set[str] = set()
    for table in _LEDGER_TABLES:
        try:
            tsv = ch_reader.query(f"SELECT DISTINCT run_id FROM {table}")
        except Exception as exc:  # noqa: BLE001 — 类1降级跳过（SOP-D 巡检不阻断交易链路）
            return set(), set(), f"{table} query failed: {exc}"
        for line in tsv.strip().splitlines():
            rid = line.strip()
            if not rid:
                continue
            if rid.startswith(_DECAY_PREFIX):
                decays.add(rid)
            elif _LEDGER_RUN_RE.match(rid):
                runs.add(rid)
    return runs, decays, None


def _scan_run_dir(d: Path, findings: list[dict[str, str]]) -> str | None:
    """扫单个 run 目录（类2/类3/类4），合法命名时返回目录名（供类1比对）。"""
    if not _RUN_ID_RE.match(d.name):
        findings.append({
            "class": "NAMING_VIOLATION", "path": str(d),
            "detail": f"目录名不符合 run_id 编号规范: {d.name!r}",
        })
        return None
    _scan_meta(d, findings)
    _scan_dir_files(d, findings)
    return d.name


def _scan_meta(d: Path, findings: list[dict[str, str]]) -> None:
    """类2：目录无 meta.json / meta 损坏；三处一致（meta.run_id==目录名）。"""
    meta = d / "meta.json"
    if not meta.exists():
        findings.append({
            "class": "ORPHAN_DIR", "path": str(d),
            "detail": "目录无 meta.json（无主档案，SOP-D §5.1）",
        })
        return
    try:
        m = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append({
            "class": "ORPHAN_DIR", "path": str(meta),
            "detail": f"meta.json 不可读/损坏: {exc}",
        })
        return
    if m.get("run_id") != d.name:
        findings.append({
            "class": "NAMING_VIOLATION", "path": str(meta),
            "detail": f"meta.run_id={m.get('run_id')!r} 与目录名 {d.name!r} 不一致（三处一致铁律）",
        })


def _scan_dir_files(d: Path, findings: list[dict[str, str]]) -> None:
    """类3（非 ASCII 文件名）+类4（超大无压缩）逐文件扫描。"""
    for f in d.rglob("*"):
        if not f.is_file():
            continue
        if not _ASCII_NAME_RE.match(f.name):
            findings.append({
                "class": "NAMING_VIOLATION", "path": str(f),
                "detail": f"文件名非 ASCII/含空格: {f.name!r}（中文进文件内容，SOP-D §3）",
            })
        if f.stat().st_size > _OVERSIZE_BYTES and f.suffix.lower() not in _ARCHIVE_SUFFIXES:
            findings.append({
                "class": "OVERSIZED_FILE", "path": str(f),
                "detail": f"{f.stat().st_size / 1024 / 1024:.1f}MB > 50MB 无压缩"
                          f"（摘要+指针或 gzip，SOP-D §7）",
            })


def verify(root: Path | None = None) -> dict:
    """四类巡检 → 报告 dict（findings 每条含 class/path/detail）。"""
    runs_root = Path(root) if root else _RUNS_ROOT
    findings: list[dict[str, str]] = []
    decay_exempt: list[str] = []
    ledger_error: str | None = None

    ledger_runs, decay_ids, ledger_error = _ledger_run_ids()
    decay_exempt = sorted(decay_ids)

    disk_run_ids: set[str] = set()
    if runs_root.exists():
        for d in sorted(runs_root.iterdir()):
            if not d.is_dir():
                continue
            rid = _scan_run_dir(d, findings)
            if rid:
                disk_run_ids.add(rid)
    if ledger_error is None:
        for rid in sorted(ledger_runs - disk_run_ids):
            findings.append({
                "class": "MISSING_ARCHIVE", "path": rid,
                "detail": f"台账有 run_id={rid} 但 runs/ 无目录（结论翻不到过程，SOP-D §4 底线）",
            })

    by_class: dict[str, int] = {}
    for f in findings:
        by_class[f["class"]] = by_class.get(f["class"], 0) + 1
    return {
        "runs_root": str(runs_root),
        "ledger_run_count": len(ledger_runs),
        "disk_run_count": len(disk_run_ids),
        "decay_exempt_count": len(decay_exempt),
        "ledger_error": ledger_error,
        "violation_count": len(findings),
        "by_class": by_class,
        "findings": findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="run 档案图书馆四类违规巡检（SOP-D §6，只报告不修复）")
    ap.add_argument("--root", help="档案根目录（默认 data/backtest_artifacts/runs）")
    ap.add_argument("--json", action="store_true", help="输出 JSON（batch 消费）")
    args = ap.parse_args()
    report = verify(Path(args.root) if args.root else None)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"runs_root={report['runs_root']}")
        print(f"台账 run={report['ledger_run_count']} 磁盘 run={report['disk_run_count']}"
              f" DECAY豁免={report['decay_exempt_count']}")
        if report["ledger_error"]:
            print(f"[WARN] 台账侧类1降级跳过（CH 不可达）：{report['ledger_error']}")
        for f in report["findings"]:
            print(f"[{f['class']}] {f['path']}: {f['detail']}")
        n = report["violation_count"]
        print(f"结论：{'干净' if not n else f'{n} 项违规'}")
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
