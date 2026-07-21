# [A_test] module_id: MOD-GOV_restore_from_backup | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §dr-drill
# [MODULE] tests.dr.test_restore_from_backup
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_restore_from_backup.py — 备份恢复演练测试（5.33.9 治本：无恢复演练测试）

覆盖：
- backup_pg_depgraph 导出 JSON 格式可被解析恢复（表名完整性/行数一致性/行字段集合一致）
- 旧备份自动清理（保留最近 max_backups 份）
- backup_runtime_handoffs 备份 .runtime/ handoffs+reconcile_reports 可回读恢复（5.33.7 配套）

不连真实 PG：monkeypatch psycopg2.connect + depgraph_schema._build_pg_dsn，
REPO_ROOT 重定向到 tmp_path（测试隔离，不写生产路径）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_META_DIR = _REPO_ROOT / "scripts" / "governance" / "meta"
if str(_META_DIR) not in sys.path:
    sys.path.insert(0, str(_META_DIR))

import backup_runtime_state as brs  # noqa: E402


# ── Fake PG（内存模拟，不连真实 PostgreSQL） ─────────────────────────────

def _install_fake_pg(monkeypatch, tmp_path, nodes_rows, edges_rows):
    """替换 backup_pg_depgraph 的 PG 依赖：连接 + DSN + REPO_ROOT。"""
    import psycopg2

    import zephyr.governance.depgraph_schema as depgraph_schema

    class _FakeCursor:
        def __init__(self) -> None:
            self.description: list = []
            self._rows: list = []

        def execute(self, sql: str) -> None:
            if "FROM nodes" in sql:
                self.description = [("node_id",), ("path",), ("domain_id",)]
                self._rows = nodes_rows
            elif "FROM edges" in sql:
                self.description = [("edge_id",), ("from_node_id",), ("to_node_id",)]
                self._rows = edges_rows
            else:
                raise AssertionError(f"FakePG 未预期的 SQL: {sql}")

        def fetchall(self):
            return list(self._rows)

    class _FakeConn:
        def cursor(self):
            return _FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: _FakeConn())
    monkeypatch.setattr(depgraph_schema, "_build_pg_dsn", lambda: {})
    monkeypatch.setattr(brs, "REPO_ROOT", tmp_path)


# ── 5.33.9 恢复演练：backup_pg_depgraph JSON 可解析恢复 ──────────────────

def test_pg_backup_json_format_restorable(monkeypatch, tmp_path):
    """导出的备份 JSON 可被解析并逐行恢复（表名完整/行数一致/字段集合一致）。"""
    nodes_rows = [(1, "src/a.py", "D_GOV"), (2, "src/b.py", "D_GOV"), (3, "src/c.py", "D_DATA")]
    edges_rows = [(10, 1, 2), (11, 2, 3)]
    _install_fake_pg(monkeypatch, tmp_path, nodes_rows, edges_rows)

    backup_path = brs.backup_pg_depgraph(max_backups=10)
    assert backup_path is not None

    data = json.loads(Path(backup_path).read_text(encoding="utf-8"))
    # 结构完整性：顶层字段 + 两张核心表
    assert set(data) >= {"timestamp", "source", "tables"}
    assert set(data["tables"]) == {"nodes", "edges"}

    # 恢复演练：逐表重建行，行数与 count 字段一致
    restored: dict[str, list[dict]] = {}
    for tbl, payload in data["tables"].items():
        assert payload["count"] == len(payload["rows"])
        restored[tbl] = payload["rows"]

    assert [r["path"] for r in restored["nodes"]] == ["src/a.py", "src/b.py", "src/c.py"]
    assert len(restored["edges"]) == 2
    # 每行字段集合一致（可据此重建 INSERT 列清单）
    node_keysets = {tuple(sorted(r)) for r in restored["nodes"]}
    assert len(node_keysets) == 1
    edge_keysets = {tuple(sorted(r)) for r in restored["edges"]}
    assert len(edge_keysets) == 1


def test_pg_backup_prunes_old_snapshots(monkeypatch, tmp_path):
    """旧备份自动清理：仅保留最近 max_backups 份。"""
    _install_fake_pg(monkeypatch, tmp_path, [(1, "x.py", "D_GOV")], [])
    backup_dir = tmp_path / "tmp" / "pg_backups"
    backup_dir.mkdir(parents=True)
    for i in range(12):
        (backup_dir / f"depgraph_2026010{i:02d}_000000.json").write_text("{}", encoding="utf-8")

    path = brs.backup_pg_depgraph(max_backups=10)
    assert path is not None

    remaining = sorted(backup_dir.glob("depgraph_*.json"))
    assert len(remaining) == 10
    assert remaining[-1] == Path(path)  # 最新备份保留


# ── 5.33.7 配套：backup_runtime_handoffs 可回读恢复 + 保留 10 份 ─────────

def test_handoffs_backup_roundtrip_and_prune(monkeypatch, tmp_path):
    """handoffs/reconcile_reports 备份内容可回读恢复，且仅保留最近 10 份。"""
    monkeypatch.setattr(brs, "REPO_ROOT", tmp_path)
    handoffs = tmp_path / ".runtime" / "handoffs"
    reports = tmp_path / ".runtime" / "reconcile_reports"
    handoffs.mkdir(parents=True)
    reports.mkdir(parents=True)
    (handoffs / "handoff_A.json").write_text(json.dumps({"session": "A"}), encoding="utf-8")
    (reports / "r1.json").write_text("{}", encoding="utf-8")

    backup_root = tmp_path / "backups"
    for i in range(11):
        (backup_root / f"runtime_handoffs_2026010{i:02d}_000000").mkdir(parents=True)

    dest = brs.backup_runtime_handoffs(max_backups=10, backup_dir=backup_root)
    assert dest is not None
    dest_path = Path(dest)

    # 恢复演练：备份内容可读回且与源一致
    restored = json.loads((dest_path / "handoffs" / "handoff_A.json").read_text(encoding="utf-8"))
    assert restored == {"session": "A"}
    assert (dest_path / "reconcile_reports" / "r1.json").is_file()

    # manifest 清单完整
    manifest = json.loads((dest_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["backup_type"] == "runtime_handoffs"
    assert len(manifest["sources"]) == 2

    # 保留最近 10 份（11 旧 + 1 新 -> 10）
    remaining = sorted(p for p in backup_root.glob("runtime_handoffs_*") if p.is_dir())
    assert len(remaining) == 10
    assert remaining[-1] == dest_path
