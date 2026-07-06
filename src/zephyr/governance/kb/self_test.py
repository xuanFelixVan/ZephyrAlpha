# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.self_test
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_self_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
KB 13项一键体检 + --self-test入口
==================================
蓝图: MOD-KB-001 §9.18.2
任务: KB-INF-0031

13项检查覆盖:
  1. SQLite完整性 (PRAGMA integrity_check)
  2. ChromaDB连通性
  3. KE计数 (MVKB >= 10)
  4. Category覆盖 (>= 5 categories)
  5. Load-bearing KE 状态
  6. Ghost scan (SQLite vs ChromaDB 一致性)
  7. WAL文件健康检查
  8. HNSW碎片化评估
  9. Freeze状态检查
  10. Tombstone表完整性
  11. 静默期检测 (最近是否有KE写入)
  12. 文件系统权限检查
  13. Embedding模型可用性

用法:
    python -m zephyr.governance.kb.self_test        # 全量13项
    python -m zephyr.governance.kb.self_test --json # JSON输出
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

import yaml
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)


class CheckStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    index: int
    name: str
    status: CheckStatus
    detail: str = ""
    suggestion: str = ""


@dataclass
class SelfTestReport:
    timestamp: str
    passed: int
    warned: int
    failed: int
    skipped: int
    checks: list[CheckResult] = field(default_factory=list)
    overall: CheckStatus = CheckStatus.PASS
    summary: str = ""


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


def _check_sqlite_integrity(root: Path) -> CheckResult:
    try:
        db_path = root / "data" / "databases" / "governance.db"
        if not db_path.exists():
            return CheckResult(
                1,
                "SQLite Integrity",
                CheckStatus.WARN,
                f"Database not found: {db_path}",
                "KB尚未初始化，运行 bootstrap 或等待首次KE创建后自动创建",
            )
        import sqlite3
        from zephyr.governance.persistence.sqlite_schema import get_db_connection

        conn = get_db_connection(str(db_path))
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        if result == "ok":
            return CheckResult(1, "SQLite Integrity", CheckStatus.PASS, "integrity_check: ok")
        return CheckResult(
            1,
            "SQLite Integrity",
            CheckStatus.FAIL,
            f"integrity_check: {result}",
            "数据库损坏。运行 VMS 后端的健康检查 尝试自动恢复",
        )
    except Exception as e:
        return CheckResult(
            1, "SQLite Integrity", CheckStatus.FAIL, "internal error", "检查 data/databases/governance.db 是否存在且可读写"
        )


def _check_chromadb_health(root: Path) -> CheckResult:
    return CheckResult(
        2,
        "ChromaDB Health",
        CheckStatus.WARN,
        "ChromaDB legacy layer removed, using VMS",
    )


def _check_ke_count(root: Path) -> CheckResult:
    try:
        know_dir = root / "docs" / "08_knowledge" / "01_raw_intake"
        if not know_dir.exists():
            return CheckResult(
                3, "KE Count (MVKB)", CheckStatus.WARN, "docs/08_knowledge/ 目录不存在", "运行 bootstrap 自动创建"
            )
        ke_files = list(know_dir.glob("ke-*.md"))
        count = len(ke_files)
        if count >= 10:
            return CheckResult(3, "KE Count (MVKB)", CheckStatus.PASS, f"{count} KEs (>= 10)")
        else:
            return CheckResult(
                3,
                "KE Count (MVKB)",
                CheckStatus.WARN,
                f"{count} KEs (< 10 MVKB threshold)",
                "运行 bootstrap 扫描全项目文档自动填充KE库",
            )
    except Exception as e:
        return CheckResult(3, "KE Count (MVKB)", CheckStatus.FAIL, "internal error")


def _check_category_coverage(root: Path) -> CheckResult:
    try:
        know_dir = root / "docs" / "08_knowledge" / "01_raw_intake"
        if not know_dir.exists():
            return CheckResult(4, "Category Coverage", CheckStatus.SKIP, "KE目录不存在")
        categories: set[str] = set()
        for ke_file in know_dir.glob("ke-*.md"):
            try:
                text = ke_file.read_text(encoding="utf-8", errors="replace")
                if text.startswith("---"):
                    chunk = text[3:]
                    end = chunk.find("---")
                    if end > 0:
                        fm = yaml.safe_load(chunk[:end])
                        cat = fm.get("category", "unknown") if isinstance(fm, dict) else "unknown"
                        categories.add(cat)
            except Exception:
                pass
        count = len(categories)
        if count >= 5:
            return CheckResult(4, "Category Coverage", CheckStatus.PASS, f"{count} categories: {sorted(categories)}")
        else:
            return CheckResult(
                4,
                "Category Coverage",
                CheckStatus.WARN,
                f"{count} categories (< 5 MVKB threshold): {sorted(categories)}",
                "运行 bootstrap 丰富KE来源",
            )
    except Exception as e:
        return CheckResult(4, "Category Coverage", CheckStatus.FAIL, "internal error")


def _check_load_bearing_kes(root: Path) -> CheckResult:
    try:
        know_dir = root / "docs" / "08_knowledge" / "01_raw_intake"
        if not know_dir.exists():
            return CheckResult(5, "Load-Bearing KEs", CheckStatus.SKIP, "KE目录不存在")
        load_bearing: list[str] = []
        expired_lb: list[str] = []
        now = datetime.now(UTC)
        for ke_file in know_dir.glob("ke-*.md"):
            try:
                text = ke_file.read_text(encoding="utf-8", errors="replace")
                if text.startswith("---"):
                    chunk = text[3:]
                    end = chunk.find("---")
                    if end > 0:
                        fm = yaml.safe_load(chunk[:end])
                        if isinstance(fm, dict) and fm.get("is_load_bearing"):
                            ke_id = fm.get("module_id", ke_file.stem)
                            load_bearing.append(ke_id)
                            ttl_str = fm.get("ttl")
                            if ttl_str:
                                try:
                                    ttl = datetime.fromisoformat(ttl_str.replace("Z", "+00:00"))
                                    if (ttl - now).days < 14:
                                        expired_lb.append(ke_id)
                                except Exception:
                                    pass
            except Exception:
                pass
        if not load_bearing:
            return CheckResult(
                5, "Load-Bearing KEs", CheckStatus.PASS, "No load-bearing KEs defined (OK for bootstrap phase)"
            )
        warnings = []
        if expired_lb:
            warnings.append(f"KEs expiring < 14d: {expired_lb}")
        if warnings:
            return CheckResult(
                5,
                "Load-Bearing KEs",
                CheckStatus.WARN,
                f"{len(load_bearing)} load-bearing: " + "; ".join(warnings),
                "检查即将过期的承重KE并决定是否续期或创建替代",
            )
        return CheckResult(5, "Load-Bearing KEs", CheckStatus.PASS, f"{len(load_bearing)} load-bearing KEs healthy")
    except Exception as e:
        return CheckResult(5, "Load-Bearing KEs", CheckStatus.FAIL, "internal error")


def _check_ghost_scan(root: Path) -> CheckResult:
    return CheckResult(
        6,
        "Ghost Scan",
        CheckStatus.WARN,
        "ChromaDB legacy layer removed, using VMS",
    )


def _check_wal_health(root: Path) -> CheckResult:
    try:
        db_dir = root / "data"
        wal_files = list(db_dir.glob("*.db-wal")) + list(db_dir.glob("*.db.shm"))
        if not wal_files:
            return CheckResult(7, "WAL Health", CheckStatus.PASS, "No dangling WAL files")
        oversized: list[str] = []
        for wf in wal_files:
            size_kb = wf.stat().st_size / 1024
            if size_kb > 4096:
                oversized.append(f"{wf.name}: {size_kb:.0f}KB")
        if oversized:
            return CheckResult(
                7,
                "WAL Health",
                CheckStatus.WARN,
                f"Oversized WAL files: {oversized}",
                "SQLite WAL过大可能意味着checkpoint未正常执行。关闭SQLite连接后自动合并",
            )
        return CheckResult(7, "WAL Health", CheckStatus.PASS, f"{len(wal_files)} WAL file(s) within normal size range")
    except Exception as e:
        return CheckResult(7, "WAL Health", CheckStatus.FAIL, "internal error")


def _check_hnsw_fragmentation(root: Path) -> CheckResult:
    return CheckResult(
        8,
        "HNSW Fragmentation",
        CheckStatus.WARN,
        "ChromaDB legacy layer removed, using VMS",
    )


def _check_freeze_state(root: Path) -> CheckResult:
    try:
        lock_path = root / "data" / "snapshots" / "kb_lock.json"
        if not lock_path.exists():
            return CheckResult(9, "Freeze State", CheckStatus.PASS, "Not frozen — normal mode")
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        mode = data.get("mode", "unknown")
        return CheckResult(
            9,
            "Freeze State",
            CheckStatus.WARN,
            f"KB is in {mode} mode since {data.get('since', 'unknown')}. Reason: {data.get('reason', 'unspecified')}",
            "若冻结已解决问题，运行 python -m zephyr.governance.kb.freeze --unfreeze 恢复",
        )
    except Exception as e:
        return CheckResult(9, "Freeze State", CheckStatus.FAIL, "internal error")


def _check_tombstone_integrity(root: Path) -> CheckResult:
    try:
        db_path = root / "data" / "databases" / "governance.db"
        if not db_path.exists():
            return CheckResult(10, "Tombstone Integrity", CheckStatus.SKIP, "Database not found")
        import sqlite3
        from zephyr.governance.persistence.sqlite_schema import get_db_connection

        conn = get_db_connection(str(db_path))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ke_tombstones'")
        exists = cursor.fetchone()
        conn.close()
        if not exists:
            return CheckResult(
                10,
                "Tombstone Integrity",
                CheckStatus.WARN,
                "ke_tombstones table does not exist",
                "运行 kb.ke_tombstone 初始化自动创建墓碑表",
            )
        return CheckResult(10, "Tombstone Integrity", CheckStatus.PASS, "Table exists")
    except Exception as e:
        return CheckResult(10, "Tombstone Integrity", CheckStatus.FAIL, "internal error")


def _check_silent_period(root: Path) -> CheckResult:
    try:
        know_dir = root / "docs" / "08_knowledge" / "01_raw_intake"
        if not know_dir.exists():
            return CheckResult(11, "Silent Period", CheckStatus.SKIP, "KE directory not found")
        ke_files = list(know_dir.glob("ke-*.md"))
        if not ke_files:
            return CheckResult(11, "Silent Period", CheckStatus.SKIP, "No KEs")
        recent_cutoff = now_utc().timestamp() - (7 * 24 * 3600)
        recent = [f for f in ke_files if f.stat().st_mtime > recent_cutoff]
        if not recent:
            return CheckResult(
                11,
                "Silent Period",
                CheckStatus.WARN,
                f"No KEs created/modified in last 7 days (total: {len(ke_files)})",
                "管道可能已停止工作。检查 G1-G5 门禁是否正常运行",
            )
        return CheckResult(11, "Silent Period", CheckStatus.PASS, f"{len(recent)} KEs modified in last 7 days")
    except Exception as e:
        return CheckResult(11, "Silent Period", CheckStatus.FAIL, "internal error")


def _check_filesystem_permissions(root: Path) -> CheckResult:
    try:
        test_paths = [
            root / "data",
            root / "docs" / "08_knowledge",
            root / "src" / "zephyr" / "kb",
        ]
        failures: list[str] = []
        for p in test_paths:
            if not p.exists():
                try:
                    p.mkdir(parents=True, exist_ok=True)
                except Exception:
                    failures.append(f"Cannot create: {p}")
                    continue
            try:
                test_file = p / ".kb_self_test_write"
                test_file.write_text("test", encoding="utf-8")
                test_file.unlink()
            except Exception:
                failures.append(f"Cannot write: {p}")
        if failures:
            return CheckResult(
                12,
                "Filesystem Permissions",
                CheckStatus.FAIL,
                "; ".join(failures),
                "检查文件系统权限和杀毒软件是否锁定相关目录",
            )
        return CheckResult(12, "Filesystem Permissions", CheckStatus.PASS, "All critical paths writable")
    except Exception as e:
        return CheckResult(12, "Filesystem Permissions", CheckStatus.FAIL, "internal error")


def _check_embedding_model(root: Path) -> CheckResult:
    try:
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
            emb = model.encode("测试")
            return CheckResult(13, "Embedding Model", CheckStatus.PASS, f"bge-small-zh-v1.5 OK (dim={emb.shape[0]})")
        except ImportError:
            return CheckResult(
                13,
                "Embedding Model",
                CheckStatus.WARN,
                "sentence-transformers not installed",
                "pip install sentence-transformers",
            )
        except Exception:
            try:
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                emb = model.encode("test")
                return CheckResult(
                    13,
                    "Embedding Model",
                    CheckStatus.WARN,
                    f"bge-small-zh-v1.5 unavailable, fell back to all-MiniLM-L6-v2 (dim={emb.shape[0]})",
                )
            except Exception as e2:
                return CheckResult(
                    13,
                    "Embedding Model",
                    CheckStatus.WARN,
                    f"No embedding model available: {e2}",
                    "向量检索将使用Mock模式（无向量索引），运行 pip install sentence-transformers",
                )
    except Exception as e:
        return CheckResult(13, "Embedding Model", CheckStatus.FAIL, "internal error")


class SelfTest:
    CHECK_FUNCTIONS = [
        _check_sqlite_integrity,
        _check_chromadb_health,
        _check_ke_count,
        _check_category_coverage,
        _check_load_bearing_kes,
        _check_ghost_scan,
        _check_wal_health,
        _check_hnsw_fragmentation,
        _check_freeze_state,
        _check_tombstone_integrity,
        _check_silent_period,
        _check_filesystem_permissions,
        _check_embedding_model,
    ]

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    def run(self) -> SelfTestReport:
        checks: list[CheckResult] = []
        for fn in self.CHECK_FUNCTIONS:
            try:
                result = fn(self._root)
                checks.append(result)
            except Exception as e:
                checks.append(CheckResult(-1, fn.__name__, CheckStatus.FAIL, "internal error"))

        passed = sum(1 for c in checks if c.status == CheckStatus.PASS)
        warned = sum(1 for c in checks if c.status == CheckStatus.WARN)
        failed = sum(1 for c in checks if c.status == CheckStatus.FAIL)
        skipped = sum(1 for c in checks if c.status == CheckStatus.SKIP)

        if failed > 0:
            overall = CheckStatus.FAIL
        elif warned > 0:
            overall = CheckStatus.WARN
        else:
            overall = CheckStatus.PASS

        summary = (
            f"Self-Test Complete: {passed} PASS / {warned} WARN / {failed} FAIL"
            f"{f' / {skipped} SKIP' if skipped else ''}"
        )

        return SelfTestReport(
            timestamp=datetime.now(UTC).isoformat(),
            passed=passed,
            warned=warned,
            failed=failed,
            skipped=skipped,
            checks=checks,
            overall=overall,
            summary=summary,
        )

    def print_report(self, report: SelfTestReport, json_output: bool = False) -> None:
        if json_output:
            data = {
                "timestamp": report.timestamp,
                "overall": report.overall.value,
                "passed": report.passed,
                "warned": report.warned,
                "failed": report.failed,
                "skipped": report.skipped,
                "checks": [
                    {
                        "index": c.index,
                        "name": c.name,
                        "status": c.status.value,
                        "detail": c.detail,
                        "suggestion": c.suggestion,
                    }
                    for c in report.checks
                ],
                "summary": report.summary,
            }
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return

        status_icons = {
            CheckStatus.PASS: "\u2705",
            CheckStatus.WARN: "\u26a0\ufe0f",
            CheckStatus.FAIL: "\u274c",
            CheckStatus.SKIP: "\u23ed\ufe0f",
        }
        print()
        print("=" * 60)
        print("  KB System Self-Test Report")
        print("=" * 60)
        print(f"  Timestamp: {report.timestamp}")
        print(f"  Overall:   {report.overall.value}")
        print("-" * 60)
        for c in report.checks:
            icon = status_icons.get(c.status, "?")
            print(f"  [{icon}] {c.index:2d}. {c.name}")
            if c.detail:
                print(f"         {c.detail}")
            if c.suggestion and c.status in (CheckStatus.WARN, CheckStatus.FAIL):
                print(f"         \u2192 {c.suggestion}")
        print("-" * 60)
        print(f"  {report.summary}")
        print("=" * 60)
        print()

    def cli(self) -> int:
        import argparse

        parser = argparse.ArgumentParser(description="KB System Self-Test")
        parser.add_argument("--json", action="store_true", help="JSON output")
        parser.add_argument("--project-root", type=Path, help="Project root path")
        args = parser.parse_args()
        if args.project_root:
            self._root = args.project_root
        report = self.run()
        self.print_report(report, json_output=args.json)
        if report.overall is CheckStatus.FAIL:
            return 1
        return 0


def main() -> None:
    sys.exit(SelfTest().cli())


if __name__ == "__main__":
    main()
