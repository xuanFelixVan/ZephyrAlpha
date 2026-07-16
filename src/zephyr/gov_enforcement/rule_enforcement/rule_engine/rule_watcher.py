# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §rule_watcher
# [MODULE] zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_watcher
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES]
# [CONSUMERS] cold_start sequence; AI sessions; governance pipeline
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] YAML files are content SSoT; mtime-based change detection; sync direction YAML->DB
# [MODIFY-GUARD] sync_rule_registry.py; verify_rule_yaml_migration.py; rule_engine.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Returns empty list on missing dir; never raises for missing files; logs errors to stdout
# [TESTS] tests/test_rule_watcher.py
# [TTL] permanent
# noqa: m02-manual  M02豁免: 规则文件watchdog常驻服务(python -m zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_watcher),CLI触发启动,启动后自动轮询;非reconciler无需事件触发

"""
RuleWatcher — YAML 规则文件变更检测与自动同步

通过 os.stat() 跟踪 YAML 文件 mtime，检测变更后自动触发：
  1. sync_rule_registry.py --sync-yaml（同步到 depgraph）
  2. verify_rule_yaml_migration.py --check-hash（哈希验证）

用法：
    from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_watcher import RuleWatcher
    watcher = RuleWatcher()
    changes = watcher.check_changes()
    if changes:
        watcher.sync_changed(changes)
        watcher.verify_changed(changes)

CLI:
    python -m zephyr.gov_enforcement.rule_enforcement.rule_watcher          # 持续轮询
    python -m zephyr.gov_enforcement.rule_enforcement.rule_watcher --once    # 检查一次
    python -m zephyr.gov_enforcement.rule_enforcement.rule_watcher --poll-interval 10
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
import subprocess
import sys
import threading
import time
from pathlib import Path


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root from {current}")


_PROJECT_ROOT = _find_project_root()
_DEFAULT_RULES_DIR = _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules"
_GOVERNANCE_DB = _PROJECT_ROOT / "data" / "databases" / "governance.db"
_SYNC_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "sync_rule_registry.py"
_VERIFY_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "verify_rule_yaml_migration.py"


class RuleWatcher:
    """YAML 规则文件变更检测器 — mtime 轮询 + 自动同步 + 验证。"""

    def __init__(
        self,
        rules_dir: str | Path | None = None,
        db_path: str | Path | None = None,  # 保留向后兼容（PG模式下忽略，治本2026-06-27删除_DEFAULT_DB_PATH常量）
        poll_interval: float = 5.0,
    ):
        self._rules_dir = Path(rules_dir) if rules_dir else _DEFAULT_RULES_DIR
        self._poll_interval = poll_interval
        self._baseline: dict[str, float] = {}
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._init_baseline()

    def _init_baseline(self) -> None:
        """扫描规则目录，记录所有 YAML 文件的初始 mtime。"""
        if not self._rules_dir.exists():
            return
        for path in sorted(self._rules_dir.glob("*.yaml")):
            try:
                stat = os.stat(path)
                self._baseline[str(path)] = stat.st_mtime
            except OSError:
                pass

    def start(self) -> None:
        """启动后台轮询线程。"""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            name="RuleWatcher",
            daemon=True,
        )
        self._thread.start()
        print(f"[RuleWatcher] Started (interval={self._poll_interval}s, dir={self._rules_dir})")

    def stop(self) -> None:
        """停止轮询线程。"""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self._poll_interval * 2)
            self._thread = None
        print("[RuleWatcher] Stopped")

    def _poll_loop(self) -> None:
        """后台轮询循环。"""
        while not self._stop_event.is_set():
            changed = self.check_changes()
            if changed:
                print(f"[RuleWatcher] Detected {len(changed)} changed file(s)")
                sync_result = self.sync_changed(changed)
                if sync_result.get("exit_code") == 0:
                    self.verify_changed(changed)
                self._update_baseline(changed)
            self._stop_event.wait(self._poll_interval)

    def _update_baseline(self, changed_files: list[dict]) -> None:
        """变更处理后更新基线 mtime。"""
        for item in changed_files:
            path = item["path"]
            try:
                stat = os.stat(path)
                self._baseline[path] = stat.st_mtime
            except OSError:
                self._baseline.pop(path, None)

    def check_changes(self) -> list[dict]:
        """单次轮询 — 检查所有 YAML 文件 mtime，返回变更列表。

        Returns:
            list[dict]: 每项含 path, rule_id, old_mtime, new_mtime
        """
        changed: list[dict] = []
        if not self._rules_dir.exists():
            return changed

        current_files: set[str] = set()
        for path in sorted(self._rules_dir.glob("*.yaml")):
            path_str = str(path)
            current_files.add(path_str)
            try:
                stat = os.stat(path)
                current_mtime = stat.st_mtime
            except OSError:
                continue

            old_mtime = self._baseline.get(path_str)
            if old_mtime is None:
                changed.append(
                    {
                        "path": path_str,
                        "rule_id": path.stem,
                        "old_mtime": None,
                        "new_mtime": current_mtime,
                        "change_type": "added",
                    }
                )
            elif current_mtime != old_mtime:
                changed.append(
                    {
                        "path": path_str,
                        "rule_id": path.stem,
                        "old_mtime": old_mtime,
                        "new_mtime": current_mtime,
                        "change_type": "modified",
                    }
                )

        for path_str in list(self._baseline.keys()):
            if path_str not in current_files:
                changed.append(
                    {
                        "path": path_str,
                        "rule_id": Path(path_str).stem,
                        "old_mtime": self._baseline[path_str],
                        "new_mtime": None,
                        "change_type": "deleted",
                    }
                )
                del self._baseline[path_str]

        return changed

    def sync_changed(self, changed_files: list[dict]) -> dict:
        """同步变更文件到 depgraph。

        调用 sync_rule_registry.py --sync-yaml 进行同步。

        Args:
            changed_files: check_changes() 返回的变更列表

        Returns:
            dict: exit_code, stdout, stderr
        """
        active_files = [f for f in changed_files if f["change_type"] in ("added", "modified")]
        if not active_files:
            print("[RuleWatcher] No active files to sync (only deletions)")
            return {"exit_code": 0, "stdout": "", "stderr": ""}

        print(f"[RuleWatcher] Syncing {len(active_files)} file(s) to depgraph")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(_SYNC_SCRIPT),
                    "--sync-yaml",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(_PROJECT_ROOT),
            )
            output_summary = result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
            print(f"[RuleWatcher] Sync result: exit={result.returncode}")
            if output_summary.strip():
                print(output_summary.strip())

            self._log_sync_event(active_files, result.returncode, result.stdout)

            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            msg = "[RuleWatcher] Sync timed out after 60s"
            print(msg)
            self._log_sync_event(active_files, -1, msg)
            return {"exit_code": -1, "stdout": "", "stderr": msg}
        except Exception as exc:
            msg = f"[RuleWatcher] Sync failed: {exc}"
            print(msg)
            self._log_sync_event(active_files, -1, msg)
            return {"exit_code": -1, "stdout": "", "stderr": str(exc)}

    def verify_changed(self, changed_files: list[dict]) -> dict:
        """对变更文件运行引用完整性验证。

        调用 verify_rule_yaml_migration.py --check-references 进行验证。
        (D56裁定后source_files已删除，--check-hash已弃用，改用--check-references)

        Args:
            changed_files: check_changes() 返回的变更列表

        Returns:
            dict: exit_code, stdout, stderr, passed (bool)
        """
        active_files = [f for f in changed_files if f["change_type"] in ("added", "modified")]
        if not active_files:
            print("[RuleWatcher] No active files to verify")
            return {"exit_code": 0, "stdout": "", "stderr": "", "passed": True}

        print(f"[RuleWatcher] Verifying {len(active_files)} file(s)")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(_VERIFY_SCRIPT),
                    "--check-references",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(_PROJECT_ROOT),
            )
            passed = result.returncode == 0
            status = "PASS" if passed else "FAIL"
            print(f"[RuleWatcher] Verify result: {status} (exit={result.returncode})")

            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": passed,
            }
        except subprocess.TimeoutExpired:
            msg = "[RuleWatcher] Verify timed out after 60s"
            print(msg)
            return {"exit_code": -1, "stdout": "", "stderr": msg, "passed": False}
        except Exception as exc:
            msg = f"[RuleWatcher] Verify failed: {exc}"
            print(msg)
            return {"exit_code": -1, "stdout": "", "stderr": str(exc), "passed": False}

    def _log_sync_event(self, changed_files: list[dict], exit_code: int, output: str) -> None:
        """写入同步事件到 governance.db rule_enforcement_log（如果表存在）。"""
        if not _GOVERNANCE_DB.exists():
            return
        try:
            conn = get_db_connection(str(_GOVERNANCE_DB), timeout=5.0)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rule_enforcement_log'")
            if cursor.fetchone() is None:
                conn.close()
                return
            for f in changed_files:
                rule_id = f.get("rule_id", "unknown")
                conn.execute(
                    """INSERT INTO rule_enforcement_log
                       (rule_id, operation, target, result, details, enforced_at, enforced_by)
                       VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
                    (
                        rule_id,
                        "rule_watcher_sync",
                        f.get("path", ""),
                        "success" if exit_code == 0 else "failed",
                        f"exit_code={exit_code}; files_synced={len(changed_files)}",
                        "RuleWatcher",
                    ),
                )
            conn.commit()
            conn.close()
        except sqlite3.Error:
            pass


def main() -> int:
    """CLI 入口点。"""
    parser = argparse.ArgumentParser(description="RuleWatcher — YAML 规则文件变更检测与自动同步")
    parser.add_argument(
        "--once",
        action="store_true",
        help="检查一次后退出（不启动持续轮询）",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=5.0,
        help="轮询间隔秒数（默认: 5）",
    )
    parser.add_argument(
        "--rules-dir",
        type=str,
        default=None,
        help="规则 YAML 目录路径（默认: docs/01_policies_and_standards/rules/）",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="depgraph 路径（PG模式下忽略；原 SQLite data/databases/depgraph.db 已删除归档）",
    )
    args = parser.parse_args()

    watcher = RuleWatcher(
        rules_dir=args.rules_dir,
        db_path=args.db_path,
        poll_interval=args.poll_interval,
    )

    if args.once:
        changes = watcher.check_changes()
        if changes:
            print(f"[RuleWatcher] Found {len(changes)} change(s):")
            for c in changes:
                print(f"  {c['change_type']}: {c['rule_id']} ({c['path']})")
            sync_result = watcher.sync_changed(changes)
            if sync_result.get("exit_code") == 0:
                verify_result = watcher.verify_changed(changes)
                if not verify_result.get("passed", True):
                    return 1
            else:
                return 1
        else:
            print("[RuleWatcher] No changes detected")
        return 0

    try:
        watcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        return 0


if __name__ == "__main__":
    sys.exit(main())
