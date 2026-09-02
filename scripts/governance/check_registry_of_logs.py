# [BLUEPRINT] MOD-INF-005 | scripts/governance/check_registry_of_logs.py | §
# [MODULE] scripts.governance.check_registry_of_logs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants; scripts.governance._shared.yaml_utils; scripts.governance._shared.encoding
# [CONSUMERS] 人工/CI 告警（warn-only MVP，GATE-REGISTRY-SYNC 同族口径）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读扫描不写仓; 退出码恒 EXIT_PASS（登记缺失/漂移只告警）
# [MODIFY-GUARD] registry_of_logs.yaml scan_scope 口径与脚本常量同步
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] 自验（--self-check 打印对账汇总）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_registry_of_logs — 日志总账索引对账（92 号清单 §7.12，M4-①）。

扫描 src/+scripts/ 四类日志/事件落盘写入模式（registry_of_logs.yaml scan_scope
口径）：
  ① open 追加模式写入（含 Path.open 追加）
  ② logging FileHandler/RotatingFileHandler/TimedRotatingFileHandler
  ③ write_text 且同行含 log/audit/.jsonl/.ndjson 词元
  ④ 治理库日志表 INSERT（drift_events/reconciliation_differences/prediction_log）
对账每个写入点文件是否已登记在某条目的 writers 清单（覆盖度=已登记/命中），
反向校验登记表 writers 文件存在性与条目 schema 完整性。

warn-only MVP（GATE-REGISTRY-SYNC 同族）：全部发现仅打印 [WARN]，退出码恒
EXIT_PASS；登记表缺失=[SKIP] EXIT_PASS；脚本自身异常=EXIT_ERROR。
"""

from __future__ import annotations

__manifest__ = {
    "args": [],
    "description": "日志总账索引对账（registry_of_logs.yaml vs 全仓写入点扫描，warn-only）",
    "dimensions": ["D3", "D11"],
    "priority": "P2",
    "timeout_seconds": 120,
    "warn_only": True,
}

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT
from _shared.yaml_utils import load_yaml

REGISTRY_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry_of_logs.yaml"

# ── 扫描口径常量（SSoT 镜像=registry_of_logs.yaml scan_scope，改动需双向同步）──
SCAN_ROOTS: tuple[str, ...] = ("src", "scripts")
EXCLUDE_DIRS: frozenset[str] = frozenset({"__pycache__", "_archive"})
SCAN_EXTENSIONS: frozenset[str] = frozenset({".py"})

RE_APPEND_OPEN = re.compile(r"""open\([^)]*["']a["']|\.open\(\s*["']a["']""")
RE_FILE_HANDLER = re.compile(r"(?:RotatingFileHandler|TimedRotatingFileHandler|FileHandler)\(")
RE_WRITE_TEXT_LOG = re.compile(r"\.write_text\(.*(log|audit|\.jsonl|\.ndjson)", re.IGNORECASE)
RE_DB_INSERT = re.compile(r"INSERT\s+INTO\s+(drift_events|reconciliation_differences|prediction_log)", re.IGNORECASE)

REQUIRED_ENTRY_FIELDS: tuple[str, ...] = (
    "log_id",
    "name_zh",
    "kind",
    "path",
    "writers",
    "consumers",
    "schema_summary",
    "retention",
    "status",
)

COVERAGE_TARGET: float = 0.95


def _iter_py_files(root: Path) -> list[Path]:
    """遍历 root 下 .py 文件（剔除 EXCLUDE_DIRS）。"""
    out: list[Path] = []
    for dirpath, dirnames, filenames in root.walk():
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if Path(fn).suffix in SCAN_EXTENSIONS:
                out.append(dirpath / fn)
    return out


def scan_write_points() -> dict[str, list[str]]:
    """扫描写入点，返回 {仓相对路径: [命中模式描述...]}（文件级去重）。"""
    hits: dict[str, list[str]] = {}
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for fp in _iter_py_files(root):
            rel = fp.relative_to(REPO_ROOT).as_posix()
            try:
                lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, 1):
                kinds: list[str] = []
                if RE_APPEND_OPEN.search(line):
                    kinds.append("append_open")
                if RE_FILE_HANDLER.search(line):
                    kinds.append("file_handler")
                if RE_WRITE_TEXT_LOG.search(line):
                    kinds.append("write_text_log")
                for m in RE_DB_INSERT.finditer(line):
                    kinds.append(f"db_insert:{m.group(1)}")
                for kind in kinds:
                    hits.setdefault(rel, []).append(f"{kind}@L{lineno}")
    return hits


def reconcile(registry: dict, hits: dict[str, list[str]]) -> dict:
    """对账：写入点 vs 登记表 writers；返回汇总 dict。"""
    logs = registry.get("logs", []) or []
    registered_writers: set[str] = set()
    schema_problems: list[str] = []
    seen_ids: set[str] = set()
    for entry in logs:
        lid = entry.get("log_id", "?") if isinstance(entry, dict) else "?"
        if not isinstance(entry, dict):
            schema_problems.append(f"条目非 dict: {entry!r}")
            continue
        for field in REQUIRED_ENTRY_FIELDS:
            if field not in entry:
                schema_problems.append(f"{lid} 缺字段 {field}")
        if lid in seen_ids:
            schema_problems.append(f"{lid} log_id 重复")
        seen_ids.add(lid)
        for w in entry.get("writers", []) or []:
            registered_writers.add(str(w))

    unregistered = {rel: ks for rel, ks in hits.items() if rel not in registered_writers}
    stale_writers = sorted(w for w in registered_writers if not (REPO_ROOT / w).is_file())

    total = len(hits)
    covered = total - len(unregistered)
    coverage = covered / total if total else 1.0

    declared = (registry.get("entry_counts") or {}).get("logs")
    count_drift = declared is not None and declared != len(logs)

    return {
        "entries": len(logs),
        "declared_entries": declared,
        "count_drift": count_drift,
        "schema_problems": schema_problems,
        "total_hits": total,
        "covered_hits": covered,
        "coverage": coverage,
        "unregistered": unregistered,
        "stale_writers": stale_writers,
    }


def main() -> int:
    """入口：扫描→对账→打印告警，恒 EXIT_PASS（warn-only）。"""
    if not REGISTRY_PATH.exists():
        print(f"[SKIP] registry_of_logs.yaml 不存在: {REGISTRY_PATH}", file=sys.stderr)
        return EXIT_PASS
    try:
        registry = load_yaml(REGISTRY_PATH)
        hits = scan_write_points()
    except Exception as exc:  # noqa: BLE001 — 脚本自身异常走 EXIT_ERROR
        print(f"[ERROR] 扫描/加载失败: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    report = reconcile(registry, hits)

    print(f"[INFO] 登记表条目: {report['entries']}（声明 {report['declared_entries']}）", file=sys.stderr)
    print(
        f"[INFO] 写入点命中文件: {report['total_hits']}，已登记: {report['covered_hits']}，"
        f"覆盖度: {report['coverage']:.1%}（目标 ≥{COVERAGE_TARGET:.0%}）",
        file=sys.stderr,
    )

    if report["count_drift"]:
        print(
            f"[WARN] entry_counts.logs={report['declared_entries']} 与实测 {report['entries']} 漂移",
            file=sys.stderr,
        )
    for p in report["schema_problems"]:
        print(f"[WARN] schema: {p}", file=sys.stderr)
    for rel, kinds in sorted(report["unregistered"].items()):
        print(f"[WARN] 未登记写入点: {rel}（{kinds[0]} 等 {len(kinds)} 处）", file=sys.stderr)
    for w in report["stale_writers"]:
        print(f"[WARN] 登记表写入方文件不存在（漂移）: {w}", file=sys.stderr)

    if report["coverage"] < COVERAGE_TARGET:
        print(f"[WARN] 覆盖度 {report['coverage']:.1%} 低于目标 {COVERAGE_TARGET:.0%}", file=sys.stderr)
    if (
        not report["unregistered"]
        and not report["stale_writers"]
        and not report["schema_problems"]
        and not report["count_drift"]
    ):
        print("[OK] 日志总账对账零告警", file=sys.stderr)
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
