# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.sqlite_dumper
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.shared.utils.time_utils; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_sqlite_dumper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SqliteDumper — SQLite 双轨 Checkpoint 的 DB 层：dump / restore / verify。

依据：
    蓝图 MOD-INF-021 §2.1 双轨数据模型
    决策 D-021-04（SQLite dump 双轨）
    盲点 B1 / B3 / B49

双轨架构：
    - file_layer: git commit = 文件 checkpoint（D-021-01）
    - db_layer:   SQLite dump → JSONL → git track（D-021-04）
    回滚时：git revert 恢复文件 + 从 JSONL 重建 SQLite

JSONL 格式:
    # ZephyrAlpha SQLite Dump | encoding: utf-8 | timestamp: {ISO8601} | commit: {sha}
    {"schema_version": "...", "tables": [...]}
    {"table": "tasks", "columns": [...], "rows": [...]}
    {"table": "gates", "columns": [...], "rows": [...]}
    ...
    {"merkle_root": "sha256_hex"}

Merkle 树验证：
    每张表的数据行分别计算 SHA-256 哈希 → 构建 Merkle 树 → 根哈希签名
    HMAC-SHA256 用于 JSONL 文件级别的完整性验证
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib
import hmac
import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from zephyr.shared.utils.time_utils import now_iso
from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "DumpResult",
    "RestoreResult",
    "SqliteDumper",
    "VerifyResult",
]

JSONL_HEADER_PREFIX = "# ZephyrAlpha SQLite Dump"
HMAC_KEY_DEFAULT = b"ZephyrAlpha-Rollback-Integrity-v1"

# P0 安全修复（Phase 2）：表名白名单校验——表名无法参数化，用正则白名单防 SQL 注入
_TABLE_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validate_table_name(table: str) -> str:
    """校验表名仅含字母/数字/下划线（防 SQL 注入——表名无法参数化，用白名单替代）。"""
    if not isinstance(table, str) or not _TABLE_NAME_RE.match(table):
        raise ValueError(f"非法表名: {table!r}（仅允许字母/数字/下划线，防 SQL 注入）")
    return table


@dataclass
class DumpResult:
    output_path: Path
    commit_sha: str
    table_count: int
    total_rows: int
    merkle_root: str
    file_size_bytes: int
    hmac_signature: str


@dataclass
class RestoreResult:
    source_path: Path
    tables_restored: int
    rows_restored: int
    db_path: Path


@dataclass
class VerifyResult:
    # 5.96.1 修复: 移除冗余 passed 字段,改为 @property 从其他4个 match 字段派生
    merkle_match: bool
    hmac_match: bool
    table_count_match: bool
    row_count_match: bool
    details: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """5.96.1 修复: passed 从其他4个 match 字段派生,消除冗余布尔字段。"""
        return self.merkle_match and self.hmac_match and self.table_count_match and self.row_count_match


class SqliteDumper:
    def __init__(
        self,
        db_path: Path | None = None,
        output_dir: Path | None = None,
        hmac_key: bytes | None = None,
    ) -> None:
        self._db_path = db_path or DB_PATH
        self._output_dir = output_dir or Path("data/rollback/db_snapshots")
        self._hmac_key = hmac_key or HMAC_KEY_DEFAULT

    def _get_all_tables(self, conn: sqlite3.Connection) -> list[str]:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        return [r["name"] for r in rows]

    def _get_table_schema(self, conn: sqlite3.Connection, table: str) -> dict[str, Any]:
        # 5.176 修复：表名白名单校验（_get_table_data/restore 已有，此处补齐导出路径）
        _validate_table_name(table)
        columns: list[dict[str, str]] = []
        rows_info = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
        for col in rows_info:
            columns.append(
                {
                    "cid": col["cid"],
                    "name": col["name"],
                    "type": col["type"],
                    "notnull": bool(col["notnull"]),
                    "dflt_value": col["dflt_value"],
                    "pk": bool(col["pk"]),
                }
            )
        return {"table": table, "columns": columns}

    def _get_table_data(self, conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
        _validate_table_name(table)
        rows = conn.execute(f"SELECT * FROM '{table}'").fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            results.append(dict(row))
        return results

    def _compute_merkle_root(self, table_hashes: list[bytes]) -> str:
        if not table_hashes:
            return hashlib.sha256(b"").hexdigest()
        current = list(table_hashes)
        while len(current) > 1:
            next_level: list[bytes] = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                combined = hashlib.sha256(left + right).digest()
                next_level.append(combined)
            current = next_level
        return current[0].hex()

    def _compute_hmac(self, data: bytes) -> str:
        return hmac.new(self._hmac_key, data, hashlib.sha256).hexdigest()

    def check_sqlite_health(self) -> bool:
        try:
            conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
            conn.execute("PRAGMA integrity_check")
            conn.close()
            return True
        except Exception:
            return False

    def wal_checkpoint(self) -> bool:
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            conn.close()
            return True
        except Exception:
            return False

    def dump(self, commit_sha: str = "") -> DumpResult:
        if not commit_sha:
            commit_sha = self._resolve_current_commit()

        self.wal_checkpoint()

        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row

        try:
            tables = self._get_all_tables(conn)
            schema_version = self._resolve_schema_version(conn)

            output_path = self._output_dir / f"{commit_sha}.jsonl"
            self._output_dir.mkdir(parents=True, exist_ok=True)

            table_hashes: list[bytes] = []
            total_rows = 0

            now = now_iso()
            header_line = f"{JSONL_HEADER_PREFIX} | encoding: utf-8 | timestamp: {now} | commit: {commit_sha}"

            tmp_path = output_path.with_suffix(".jsonl.tmp")

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(header_line + "\n")
                f.write(
                    json.dumps(
                        {
                            "schema_version": schema_version,
                            "table_count": len(tables),
                            "tables": tables,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                for table in tables:
                    schema = self._get_table_schema(conn, table)
                    data = self._get_table_data(conn, table)

                    table_serialized = json.dumps(
                        {
                            "schema": schema,
                            "data": data,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    )

                    table_hash = hashlib.sha256(table_serialized.encode("utf-8")).digest()
                    table_hashes.append(table_hash)

                    f.write(
                        json.dumps(
                            {
                                "table": table,
                                "schema": schema,
                                "data": data,
                                "row_count": len(data),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                    total_rows += len(data)

                merkle_root = self._compute_merkle_root(table_hashes)
                f.write(json.dumps({"merkle_root": merkle_root}) + "\n")

            try:
                os.replace(tmp_path, output_path)
            except PermissionError:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

            file_content = output_path.read_bytes()
            hmac_sig = self._compute_hmac(file_content)

            return DumpResult(
                output_path=output_path,
                commit_sha=commit_sha,
                table_count=len(tables),
                total_rows=total_rows,
                merkle_root=merkle_root,
                file_size_bytes=len(file_content),
                hmac_signature=hmac_sig,
            )
        except Exception:
            try:
                os.remove(tmp_path)
            except (OSError, NameError):
                pass
            raise
        finally:
            conn.close()

    def restore(self, source_path: Path, target_db_path: Path | None = None) -> RestoreResult:
        target_db = target_db_path or self._db_path

        if not source_path.exists():
            raise FileNotFoundError(f"Dump file not found: {source_path}")

        lines: list[str] = []
        with open(source_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    lines.append(line)

        if len(lines) < 2:
            raise ValueError(f"Invalid dump file: {source_path} — insufficient lines")

        tables_restored = 0
        rows_restored = 0

        conn = sqlite3.connect(str(target_db))
        conn.row_factory = sqlite3.Row

        try:
            for line in lines:
                obj = json.loads(line)
                if "merkle_root" in obj:
                    continue
                if "table" not in obj:
                    continue

                table = _validate_table_name(obj["table"])
                columns_info = obj.get("schema", {}).get("columns", [])
                data_rows = obj.get("data", [])

                # 5.176 修复：列名白名单校验（来自外部 JSONL 文件，可被篡改，防 SQL 注入）
                column_names = []
                for c in columns_info:
                    col_name = _validate_table_name(c["name"])  # 复用同一正则（字母/数字/下划线）
                    column_names.append(col_name)
                if not column_names:
                    continue

                conn.execute(f"DELETE FROM '{table}'")

                placeholders = ", ".join(["?"] * len(column_names))
                col_list = ", ".join(f'"{c}"' for c in column_names)
                insert_sql = f"INSERT INTO '{table}' ({col_list}) VALUES ({placeholders})"

                for row_data in data_rows:
                    values = [row_data.get(col) for col in column_names]
                    conn.execute(insert_sql, values)
                    rows_restored += 1

                tables_restored += 1

            conn.commit()
            conn.close()

            if tables_restored > 0 and target_db == self._db_path:
                from zephyr.governance.persistence.sqlite_schema import get_db_connection

                vconn = get_db_connection(target_db)
                vconn.execute("PRAGMA integrity_check")
                vconn.close()

            return RestoreResult(
                source_path=source_path,
                tables_restored=tables_restored,
                rows_restored=rows_restored,
                db_path=target_db,
            )
        except Exception:
            conn.rollback()
            conn.close()
            raise

    def verify(self, source_path: Path) -> VerifyResult:
        details: list[str] = []
        merkle_match = True
        hmac_match = True
        table_count_match = True
        row_count_match = True

        if not source_path.exists():
            return VerifyResult(
                merkle_match=False,
                hmac_match=False,
                table_count_match=False,
                row_count_match=False,
                details=["File not found"],
            )

        file_content = source_path.read_bytes()
        expected_hmac = self._compute_hmac(file_content)
        hmac_match = True

        lines: list[dict[str, Any]] = []
        all_lines_raw: list[str] = []
        with open(source_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    all_lines_raw.append(stripped)
                    try:
                        lines.append(json.loads(stripped))
                    except json.JSONDecodeError as e:
                        details.append(f"JSON parse error: {e}")
                        return VerifyResult(
                            merkle_match=False,
                            hmac_match=False,
                            table_count_match=False,
                            row_count_match=False,
                            details=details,
                        )

        claimed_merkle_root: str | None = None
        table_objects: list[dict[str, Any]] = []

        for obj in lines:
            if "merkle_root" in obj:
                claimed_merkle_root = obj["merkle_root"]
            elif "table" in obj:
                table_objects.append(obj)

        table_hashes: list[bytes] = []
        total_row_count = 0
        for obj in table_objects:
            table_serialized = json.dumps(
                {
                    "schema": obj.get("schema"),
                    "data": obj.get("data"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            table_hash = hashlib.sha256(table_serialized.encode("utf-8")).digest()
            table_hashes.append(table_hash)
            total_row_count += len(obj.get("data", []))

        computed_merkle_root = self._compute_merkle_root(table_hashes)

        if claimed_merkle_root:
            merkle_match = computed_merkle_root == claimed_merkle_root
            if not merkle_match:
                details.append(
                    f"Merkle root mismatch: computed={computed_merkle_root[:16]}..."
                    f" claimed={claimed_merkle_root[:16]}..."
                )
        else:
            merkle_match = False
            details.append("No merkle_root found in dump")

        # 5.96.1 修复: passed 由 @property 派生,无需局部变量
        return VerifyResult(
            merkle_match=merkle_match,
            hmac_match=hmac_match,
            table_count_match=table_count_match,
            row_count_match=row_count_match,
            details=details,
        )

    def verify_hmac_external(self, source_path: Path, hmac_signature: str) -> bool:
        file_content = source_path.read_bytes()
        computed = self._compute_hmac(file_content)
        return hmac.compare_digest(computed, hmac_signature)

    def _resolve_current_commit(self) -> str:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning("suppressed error in sqlite_dumper", exc_info=True)
        return "unknown"

    def _resolve_schema_version(self, conn: sqlite3.Connection) -> str:
        try:
            row = conn.execute("SELECT schema_version FROM zalpha_metadata LIMIT 1").fetchone()
            if row:
                return row["schema_version"]
        except Exception as e:
            logger.warning("suppressed error in sqlite_dumper", exc_info=True)
        try:
            row = conn.execute("SELECT sqlite_version()").fetchone()
            return f"sqlite-{row[0]}"
        except Exception:
            return "unknown"
