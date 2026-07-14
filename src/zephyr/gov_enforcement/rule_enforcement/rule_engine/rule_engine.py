# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §rule_engine
# [MODULE] zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_engine
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] SkillLoader; GateEngine; cold_start sequence; AI sessions
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] YAML files are content SSoT; depgraph is index only; sync direction YAML->DB
# [MODIFY-GUARD] sync_rule_registry.py; verify_rule_yaml_migration.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Returns empty list on missing rules; never raises for missing data
# [TESTS] tests/test_rule_e2e.py
# [TTL] permanent

"""
RuleLoader — 规则加载核心 API
=============================
通过 depgraph rule_bindings 索引查找 rule_id -> 读取 YAML 文件 -> 返回规则字典。

优先路径：depgraph rule_bindings -> rule_id -> YAML 文件
回退路径：直接扫描 docs/01_policies_and_standards/rules/ 目录

用法：
    from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_engine import RuleLoader
    loader = RuleLoader()
    rules = loader.load_for_operation("file_write")
    critical = loader.get_critical_rules()
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import psycopg2
import yaml
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root from {current}")


_PROJECT_ROOT = _find_project_root()
_RULES_DIR = _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules"


class _PgConnExecuteWrapper:
    """兼容 sqlite3.Connection.execute() 接口的 psycopg2 connection 包装器。

    P2迁移后：psycopg2 connection 没有 execute() 方法，此包装器使原 SQLite 代码无需修改。
    每次调用 execute() 创建一个新的 RealDictCursor（与原 sqlite3.Row 的 dict(row)/row['col'] 用法等价）。
    """

    def __init__(self, pg_conn: psycopg2.extensions.connection) -> None:
        self._pg_conn = pg_conn

    def execute(self, sql: str, params: tuple = ()) -> object:
        cur = self._pg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        return cur

    def close(self) -> None:
        self._pg_conn.close()


def _rule_id_to_filename(rule_id: str) -> str:
    upper = rule_id.upper().replace("-", "_")
    lower = rule_id.lower().replace("-", "_")
    for candidate in (lower, upper):
        path = _RULES_DIR / f"{candidate}.yaml"
        if path.exists():
            return f"{candidate}.yaml"
    return f"{lower}.yaml"

class RuleLoader:
    """规则加载器 — 从 YAML 文件加载规则，通过 depgraph (PostgreSQL) 索引查找。"""

    def __init__(
        self,
        db_path: str | Path | None = None,  # 保留向后兼容（PG模式下忽略，治本2026-06-27删除_DB_PATH常量）
        rules_dir: str | Path | None = None,
    ) -> None:
        self._rules_dir = Path(rules_dir) if rules_dir else _RULES_DIR
        self._cache: dict[str, dict[str, Any]] = {}
        self._db_available: bool | None = None

    def _get_conn(self) -> _PgConnExecuteWrapper | None:
        """获取 PG 连接，验证 rule_bindings 表存在且有数据。

        P2迁移后：原 SQLite db_path.exists() 检查改为 PG 连接 + information_schema 检查。
        任何 PG 连接/查询异常均降级为 db_available=False，回退到 YAML 扫描。
        """
        if self._db_available is False:
            return None
        try:
            conn = _PgConnExecuteWrapper(get_depgraph_pg_connection(autocommit=True))
            # 检查 rule_bindings 表存在
            cursor = conn.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'rule_bindings'
            """)
            if cursor.fetchone() is None:
                conn.close()
                self._db_available = False
                return None
            # 检查 rule_bindings 有数据
            cursor = conn.execute("SELECT COUNT(*) AS cnt FROM rule_bindings")
            if cursor.fetchone()["cnt"] == 0:
                conn.close()
                self._db_available = False
                return None
            self._db_available = True
            return conn
        except (psycopg2.Error, OSError, FileNotFoundError, ValueError):
            # PG 连接失败、配置文件缺失等情况：降级到 YAML 扫描
            self._db_available = False
            return None

    def _read_yaml(self, rule_id: str) -> dict[str, Any] | None:
        if rule_id in self._cache:
            return self._cache[rule_id]
        filename = _rule_id_to_filename(rule_id)
        path = self._rules_dir / filename
        if not path.exists():
            warnings.warn(f"RuleLoader: YAML not found for rule_id={rule_id} (tried {path})", stacklevel=2)
            return None
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as exc:
            warnings.warn(f"RuleLoader: failed to read {path}: {exc}", stacklevel=2)
            return None
        if data is None:
            return None
        self._cache[rule_id] = data
        return data

    def _load_rules_from_db(self, rule_ids: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for rid in rule_ids:
            data = self._read_yaml(rid)
            if data is not None:
                results.append(data)
        return results

    def _scan_rules_dir(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        if not self._rules_dir.exists():
            return results
        for path in sorted(self._rules_dir.glob("*.yaml")):
            rule_id = path.stem
            data = self._read_yaml(rule_id)
            if data is not None:
                results.append(data)
        return results

    def load_for_operation(self, op_name: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if conn is None:
            return self._scan_rules_dir()
        try:
            cursor = conn.execute(
                "SELECT DISTINCT rule_id FROM rule_bindings WHERE function_name = %s",
                (op_name,),
            )
            rule_ids = [row["rule_id"] for row in cursor.fetchall()]
            if not rule_ids:
                return []
            return self._load_rules_from_db(rule_ids)
        except psycopg2.Error:
            return []
        finally:
            conn.close()

    def load_for_skill(self, skill_id: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if conn is None:
            return self._scan_rules_dir()
        try:
            cursor = conn.execute(
                "SELECT DISTINCT rule_id FROM rule_bindings WHERE trigger_type = 'skill_id' AND trigger_id = %s",
                (skill_id,),
            )
            rule_ids = [row["rule_id"] for row in cursor.fetchall()]
            if not rule_ids:
                return []
            return self._load_rules_from_db(rule_ids)
        except psycopg2.Error:
            return []
        finally:
            conn.close()

    def load_for_gate(self, gate_id: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if conn is None:
            return self._scan_rules_dir()
        try:
            cursor = conn.execute(
                "SELECT DISTINCT rule_id FROM rule_bindings WHERE trigger_type = 'gate_id' AND trigger_id = %s",
                (gate_id,),
            )
            rule_ids = [row["rule_id"] for row in cursor.fetchall()]
            if not rule_ids:
                return []
            return self._load_rules_from_db(rule_ids)
        except psycopg2.Error:
            return []
        finally:
            conn.close()

    def get_critical_rules(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if conn is None:
            all_rules = self._scan_rules_dir()
            return [r for r in all_rules if r.get("metadata", {}).get("impact_level") == "H"]
        try:
            cursor = conn.execute("SELECT DISTINCT node_id FROM nodes WHERE node_type = 'rule' AND impact_level = 'H'")
            rule_ids = [row["node_id"] for row in cursor.fetchall()]
            if not rule_ids:
                all_rules = self._scan_rules_dir()
                return [r for r in all_rules if r.get("metadata", {}).get("impact_level") == "H"]
            return self._load_rules_from_db(rule_ids)
        except psycopg2.Error:
            all_rules = self._scan_rules_dir()
            return [r for r in all_rules if r.get("metadata", {}).get("impact_level") == "H"]
        finally:
            conn.close()

    def get_rule_by_id(self, rule_id: str) -> dict[str, Any] | None:
        return self._read_yaml(rule_id)

    def list_all_rules(self) -> list[dict[str, Any]]:
        all_rules = self._scan_rules_dir()
        summaries: list[dict[str, Any]] = []
        for r in all_rules:
            summaries.append(
                {
                    "rule_id": r.get("rule_id", ""),
                    "title": r.get("title", ""),
                    "layer": r.get("layer", ""),
                    "severity": r.get("severity", ""),
                    "scope": r.get("scope", ""),
                }
            )
        return summaries

    def clear_cache(self) -> None:
        self._cache.clear()
        self._db_available = None


__all__ = ["RuleLoader"]
