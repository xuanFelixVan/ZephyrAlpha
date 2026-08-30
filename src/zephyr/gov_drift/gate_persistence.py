# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.gate_persistence
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] src/zephyr/gov_drift/_infrastructure.py ; tests/gate/test_gate_persistence.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 门禁结果不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Gate Persistence — gate_persistence.py


门禁结果持久化：scan_result.json + governance.db(SQLite) + manifest.json + 防篡改 SHA256。

注意（#62 裁定 2026-08-21）：本文件 data/drift_audit/drift_events.db 不再含 drift_events
表（空壳 schema B 已废止）；drift_events 唯一真源=DB_PATH governance.db（drift_engine 写）。
对标 blueprint.md §2.17门禁持久化 / D-023-31。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: gate_persistence.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① GatePersistence
#   name_en: GatePersistence
#   intro: class GatePersistence 源码 L69-L305
#   desc: 公共方法（定义序）: project_root, audit_dir, db_path, persist_scan_result, persist_gate_decision, verify_integrity, up…
#   inputs: project_root
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: GatePersistence
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/gate/test_gate_persistence.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import UTC, datetime

from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.serialization import dumps


class GatePersistence:
    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._audit_dir = os.path.join(project_root, "data", "drift_audit")

        self._db_path = os.path.join(self._audit_dir, "drift_events.db")

        os.makedirs(self._audit_dir, exist_ok=True)

        self._init_db()

    # ── Stage 4 公共化（2026-07-28）：只读 properties ──
    # 消除 tests/gate/test_gate_persistence.py 中 18 处私有成员访问。
    # 存储仍为 self._project_root/_audit_dir/_db_path（primary），公共 property 为访问器。

    @property
    def project_root(self) -> str:
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    @property
    def audit_dir(self) -> str:
        """只读：audit_dir（Stage 4 公共化）。"""
        return self._audit_dir

    @audit_dir.setter
    def audit_dir(self, value):
        """写入：audit_dir（Stage 4 公共化）。"""
        self._audit_dir = value

    @property
    def db_path(self) -> str:
        """只读：db_path（Stage 4 公共化）。"""
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        """写入：db_path（Stage 4 公共化）。"""
        self._db_path = value

    def _init_db(self) -> None:
        conn = get_db_connection(self._db_path)

        try:
            # #62 裁定（2026-08-21 裁定书）：本文件不再创建 drift_events 表——
            # drift_events 唯一真源=governance.db 22 列 schema（drift_engine 唯一写方），
            # 此处 12 列 schema B 空壳已删除（全表 0 行实证零损失），消除第三 schema 来源。
            conn.execute("""


                CREATE TABLE IF NOT EXISTS scan_results (


                    scan_id TEXT PRIMARY KEY,


                    detectors_run INTEGER,


                    total_drift_events INTEGER,


                    storm_mode_triggered INTEGER,


                    committed_at TEXT,


                    sha256 TEXT


                )


            """)

            conn.execute("""


                CREATE TABLE IF NOT EXISTS gate_decisions (


                    id INTEGER PRIMARY KEY AUTOINCREMENT,


                    module_id TEXT,


                    gate TEXT,


                    decision TEXT,


                    detail TEXT,


                    decided_at TEXT


                )


            """)

            conn.commit()
        finally:
            # 5.49.2 修复：异常路径确保连接归还
            conn.close()

    def persist_scan_result(self, scan_id: uuid.UUID, body: dict[str, object]) -> str:
        body["persisted_at"] = datetime.now(UTC).isoformat()

        sha = hashlib.sha256(dumps(body, sort_keys=True).encode("utf-8")).hexdigest()

        body["sha256"] = sha

        filepath = os.path.join(self._audit_dir, f"{scan_id}_result.json")

        tmp_path = f"{filepath}.{os.getpid()}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(body, fh, indent=2, ensure_ascii=False)

            os.replace(tmp_path, filepath)

        except PermissionError:
            try:
                os.remove(tmp_path)

            except OSError:
                pass

        conn = get_db_connection(self._db_path)

        try:
            conn.execute(
                "INSERT OR REPLACE INTO scan_results(scan_id, detectors_run, total_drift_events, storm_mode_triggered, committed_at, sha256) VALUES(?,?,?,?,?,?)",
                (
                    str(scan_id),
                    body.get("detectors_run", 0),
                    body.get("total_drift_events", 0),
                    int(body.get("storm_mode_triggered", False)),
                    body.get("persisted_at", ""),
                    sha,
                ),
            )

            conn.commit()
        finally:
            # 5.49.2 修复：异常路径确保连接归还
            conn.close()

        return sha

    def persist_gate_decision(self, module_id: str, gate: str, decision: str, detail: str = "") -> None:
        conn = get_db_connection(self._db_path)

        try:
            conn.execute(
                "INSERT INTO gate_decisions(module_id, gate, decision, detail, decided_at) VALUES(?,?,?,?,?)",
                (module_id, gate, decision, detail, datetime.now(UTC).isoformat()),
            )

            conn.commit()
        finally:
            # 5.49.2 修复：异常路径确保连接归还
            conn.close()

    def verify_integrity(self, scan_id: uuid.UUID) -> bool:
        filepath = os.path.join(self._audit_dir, f"{scan_id}_result.json")

        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, encoding="utf-8") as fh:
                data = json.load(fh)

            sha_key = data.pop("sha256", None)

            if sha_key is None:
                return False

            computed = hashlib.sha256(dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

            return computed == sha_key.get("sha256", "")

        except (json.JSONDecodeError, OSError):
            return False

    def update_manifest(self, scan_id: uuid.UUID, status: str) -> None:
        manifest_path = os.path.join(self._audit_dir, "manifest.json")

        manifest: dict[str, object]

        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, encoding="utf-8") as fh:
                    manifest = json.load(fh)

            except (json.JSONDecodeError, UnicodeDecodeError):
                manifest = {"entries": []}

        else:
            manifest = {"entries": []}

        entries: list[dict[str, str]] = manifest.get("entries", []) or []

        entries.append({"scan_id": str(scan_id), "status": status, "timestamp": datetime.now(UTC).isoformat()})

        manifest["entries"] = entries[-100:]

        tmp_path = f"{manifest_path}.{os.getpid()}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2, ensure_ascii=False)

            os.replace(tmp_path, manifest_path)

        except PermissionError:
            try:
                os.remove(tmp_path)

            except OSError:
                pass
