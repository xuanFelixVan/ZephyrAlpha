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
# [A_module] module_id=MOD-GOV-019 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 触发源查询参数
#   fields: op_name 操作名 / skill_id / gate_id / rule_id 字符串
#   code: load_for_operation(op_name) L156
# - id: I2
#   name: depgraph PG rule_bindings 索引表
#   fields: rule_id / function_name / trigger_type / trigger_id；nodes 表 impact_level
#   code: rule_bindings（PostgreSQL，L96-110 探测）
# - id: I3
#   name: 规则 YAML 文件
#   fields: rule_id / title / layer / severity / scope / metadata.impact_level
#   code: docs/01_policies_and_standards/rules/*.yaml L56
# 层: 算法
# - id: A1
#   name_zh: ① PG 可用性探测
#   name_en: RuleLoader._get_conn
#   intro: 连 PG 查 rule_bindings 表在不在、有没有数据，任何异常都降级走 YAML 扫描
#   desc: information_schema.tables 查表存在 → COUNT(*)>0 查有数据；PgError/OSError 等一律 _db_available=False 回退；结果缓存避免重复探测
#   inputs: I2
#   outputs: PG 连接或 None
# - id: A2
#   name_zh: ② 按触发源查 rule_id
#   name_en: load_for_operation / load_for_skill / load_for_gate
#   intro: 用 SQL 从索引表捞出某操作/技能/门挂的所有 rule_id
#   desc: SELECT DISTINCT rule_id FROM rule_bindings WHERE function_name=%s 或 trigger_type+trigger_id 匹配；无结果返回空列表
#   inputs: I1 A1
#   outputs: rule_id 列表
# - id: A3
#   name_zh: ③ YAML 读取与缓存
#   name_en: _read_yaml / _rule_id_to_filename
#   intro: rule_id 映射成文件名读 YAML 并缓存，读不到只告警不抛异常
#   desc: rule_id 转 lower/upper 两种候选文件名；yaml.safe_load 解析；dict _cache 按 rule_id 缓存；缺文件 warnings.warn 返回 None
#   inputs: I3
#   outputs: 规则字典
#   invariant: YAML 是内容 SSoT，depgraph 只是索引
# - id: A4
#   name_zh: ④ 目录扫描回退
#   name_en: _scan_rules_dir
#   intro: PG 不可用时直接全量扫 rules 目录下所有 YAML
#   desc: sorted(glob("*.yaml")) 逐文件 _read_yaml，汇成规则列表
#   inputs: I3 A3
#   outputs: 全量规则列表
# - id: A5
#   name_zh: ⑤ 高危规则筛选
#   name_en: get_critical_rules
#   intro: 挑出 impact_level=H 的高危规则，PG 查不到就扫 YAML 元数据过滤
#   desc: 优先 nodes 表 WHERE node_type='rule' AND impact_level='H'；失败或空结果回退 _scan_rules_dir 后按 metadata.impact_level=='H' 过滤
#   inputs: A1 A4
#   outputs: 高危规则列表
# 层: 输出
# - id: O1
#   name_zh: 规则字典列表
#   name_en: list[dict] rules
#   intro: 按操作/技能/门/高危维度返回规则内容，缺数据返回空列表绝不抛异常
#   invariant: 缺规则返回空列表；同步方向 YAML→DB
#   downstream: SkillLoader；GateEngine；cold_start sequence；AI sessions（# [CONSUMERS] 头）
# - id: O2
#   name_zh: 规则摘要列表
#   name_en: list_all_rules summaries
#   intro: 只含 rule_id/title/layer/severity/scope 五字段的轻量清单
#   downstream: 治理审计与展示（内部使用）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# A1 --> A2
# I3 --> A3
# I3 --> A4
# A3 --> A4
# A1 --> A5
# A4 --> A5
# A2 --> A3
# A3 --> O1
# A5 --> O1
# A4 --> O2
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.depgraph_schema import PgConnectionProvider, get_depgraph_pg_connection

# R3 治本（2026-07-28）：_PgConnExecuteWrapper + PgError 规范副本下沉到 pg_wrapper，
# 消除业务模块顶层 import psycopg2（DIP——业务逻辑仅依赖 persistence 抽象，不再硬耦合驱动）
from zephyr.governance.persistence.pg_wrapper import PgError, _PgConnExecuteWrapper


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root from {current}")


_PROJECT_ROOT = _find_project_root()
_RULES_DIR = _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules"


def _rule_id_to_filename(rule_id: str) -> str:
    upper = rule_id.upper().replace("-", "_")
    lower = rule_id.lower().replace("-", "_")
    for candidate in (lower, upper):
        path = _RULES_DIR / f"{candidate}.yaml"
        if path.exists():
            return f"{candidate}.yaml"
    # slug 前缀回退（#ARCH-087）：规则文件带语义后缀（trae_001_file_operation_security.yaml），
    # DB rule_id/按 ID 解析在 slug 迁移后精确名映射整体失效——glob 前缀匹配恢复解析
    matches = sorted(_RULES_DIR.glob(f"{lower}_*.yaml"))
    if matches:
        return matches[0].name
    return f"{lower}.yaml"


class RuleLoader:
    """规则加载器 — 从 YAML 文件加载规则，通过 depgraph (PostgreSQL) 索引查找。"""

    def __init__(
        self,
        db_path: str | Path | None = None,  # 保留向后兼容（PG模式下忽略，治本2026-06-27删除_DB_PATH常量）
        rules_dir: str | Path | None = None,
        pg_conn_provider: PgConnectionProvider
        | None = None,  # #ARCH-098 DIP 注入缝（默认=get_depgraph_pg_connection，测试可注入 mock）
    ) -> None:
        self._rules_dir = Path(rules_dir) if rules_dir else _RULES_DIR
        self._cache: dict[str, dict[str, Any]] = {}
        self._db_available: bool | None = None
        # DIP：默认使用 get_depgraph_pg_connection（生产），测试可注入 mock provider
        self._pg_conn_provider: PgConnectionProvider = (
            pg_conn_provider if pg_conn_provider is not None else get_depgraph_pg_connection
        )

    def _get_conn(self) -> _PgConnExecuteWrapper | None:
        """获取 PG 连接，验证 rule_bindings 表存在且有数据。

        P2迁移后：原 SQLite db_path.exists() 检查改为 PG 连接 + information_schema 检查。
        任何 PG 连接/查询异常均降级为 db_available=False，回退到 YAML 扫描。
        """
        if self._db_available is False:
            return None
        try:
            conn = _PgConnExecuteWrapper(self._pg_conn_provider(autocommit=True))
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
        except (PgError, OSError, FileNotFoundError, ValueError):
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
        except PgError:
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
        except PgError:
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
        except PgError:
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
        except PgError:
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
