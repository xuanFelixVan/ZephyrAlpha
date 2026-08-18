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
- backup_pg_architecture 导出 JSON 格式可被解析恢复（19表完整性/行数一致性/字段集合一致）
- 旧备份自动清理（保留最近 max_backups 份）
- backup_runtime_handoffs 备份 .runtime/ handoffs+reconcile_reports 可回读恢复（5.33.7 配套）

不连真实 PG：monkeypatch psycopg2.connect + depgraph_schema.build_pg_dsn，
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

def _install_fake_pg(monkeypatch, tmp_path, table_rows: dict[str, list] | None = None):
    """替换 backup_pg_architecture 的 PG 依赖：连接 + DSN + REPO_ROOT。

    Args:
        table_rows: {table_name: [row_tuples, ...]} 字典。
                    未提供的表返回空结果（模拟空表）。
    """
    import psycopg2

    import zephyr.governance.depgraph_schema as depgraph_schema

    _table_rows = table_rows or {}

    class _FakeCursor:
        def __init__(self) -> None:
            self.description: list = []
            self._rows: list = []

        def execute(self, sql: str) -> None:
            # 解析 "SELECT * FROM <table>" 提取 table name
            table = None
            upper = sql.upper()
            if "FROM " in upper:
                idx = upper.index("FROM ") + 5
                table = sql[idx:].strip().split()[0].strip(";").strip()
            if table is None:
                raise AssertionError(f"FakePG 无法解析 SQL: {sql}")
            self._rows = list(_table_rows.get(table, []))
            # 简单 description：根据行数生成占位列名
            ncols = len(self._rows[0]) if self._rows else 1
            self.description = [(f"col{i}",) for i in range(ncols)]

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


# ── 5.33.9 恢复演练：backup_pg_architecture JSON 可解析恢复 ──────────────

def test_pg_backup_json_format_restorable(monkeypatch, tmp_path):
    """导出的备份 JSON 可被解析并逐行恢复（19表完整/行数一致/字段集合一致）。"""
    # 为部分表提供数据，其余表默认空列表（验证空表也被备份）
    table_rows = {
        "nodes": [(1, "src/a.py", "D_GOV"), (2, "src/b.py", "D_GOV"), (3, "src/c.py", "D_DATA")],
        "edges": [(10, 1, 2), (11, 2, 3)],
        "battle_map_steps": [(1, "BM-BUY-01", "买入流程")],
        "decision_nodes": [(1, "signal", "decision/signal/alpha_v1")],
        "dataflow_datasets": [(1, "market_data.tick", "production")],
    }
    _install_fake_pg(monkeypatch, tmp_path, table_rows)

    backup_path = brs.backup_pg_architecture(max_backups=10)
    assert backup_path is not None

    data = json.loads(Path(backup_path).read_text(encoding="utf-8"))
    # 结构完整性：顶层字段
    assert set(data) >= {"timestamp", "source", "tables"}

    # 19 表完整性：所有 _ARCHITECTURE_TABLES 表都必须出现在备份中
    expected_tables = set(brs._ARCHITECTURE_TABLES)
    actual_tables = set(data["tables"])
    assert actual_tables == expected_tables, (
        f"备份表不完整：缺失={expected_tables - actual_tables}, "
        f"多余={actual_tables - expected_tables}"
    )

    # 恢复演练：逐表重建行，行数与 count 字段一致
    restored: dict[str, list[dict]] = {}
    for tbl, payload in data["tables"].items():
        assert payload["count"] == len(payload["rows"])
        restored[tbl] = payload["rows"]

    # 有数据的表验证内容
    assert [r["col0"] for r in restored["nodes"]] == [1, 2, 3]
    assert len(restored["edges"]) == 2
    assert len(restored["battle_map_steps"]) == 1
    assert len(restored["decision_nodes"]) == 1
    assert len(restored["dataflow_datasets"]) == 1
    # 空表验证（count=0, rows=[]）
    assert data["tables"]["domains"]["count"] == 0
    assert data["tables"]["domains"]["rows"] == []


def test_pg_backup_prunes_old_snapshots(monkeypatch, tmp_path):
    """旧备份自动清理：仅保留最近 max_backups 份。"""
    _install_fake_pg(monkeypatch, tmp_path, {"nodes": [(1, "x.py", "D_GOV")]})
    backup_dir = tmp_path / "tmp" / "pg_backups"
    backup_dir.mkdir(parents=True)
    for i in range(12):
        (backup_dir / f"architecture_2026010{i:02d}_000000.json").write_text("{}", encoding="utf-8")

    path = brs.backup_pg_architecture(max_backups=10)
    assert path is not None

    remaining = sorted(backup_dir.glob("architecture_*.json"))
    assert len(remaining) == 10
    assert remaining[-1] == Path(path)  # 最新备份保留


def test_pg_backup_throttle_skips_recent(monkeypatch, tmp_path):
    """Obs2 治本：throttle_seconds 窗口内跳过冗余快照，返回上次备份路径。

    模拟 apply 连续调用：首次备份成功，60s 内第二次被节流跳过。
    """
    _install_fake_pg(monkeypatch, tmp_path, {"nodes": [(1, "a.py", "D_GOV")]})
    backup_dir = tmp_path / "tmp" / "pg_backups"
    backup_dir.mkdir(parents=True)

    # 首次备份（throttle_seconds=0 不节流，模拟 apply 首次调用前的状态）
    first = brs.backup_pg_architecture(max_backups=10, throttle_seconds=0)
    assert first is not None
    first_path = Path(first)
    assert first_path.is_file()

    # 60s 内再次调用（throttle_seconds=60）——应跳过并返回上次路径
    skipped = brs.backup_pg_architecture(max_backups=10, throttle_seconds=60)
    assert skipped == first  # 返回上次备份路径，不创建新文件

    # 仅 1 份备份（节流生效，未产生第 2 份）
    remaining = sorted(backup_dir.glob("architecture_*.json"))
    assert len(remaining) == 1
    assert remaining[0] == first_path


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
