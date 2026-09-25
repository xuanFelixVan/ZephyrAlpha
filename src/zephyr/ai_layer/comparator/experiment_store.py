# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.experiment_store
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection);
#                zephyr.infrastructure.database_service (get_db_service);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (ExperimentStore/hash 工具注入);
#             zephyr.ai_layer.comparator.compare_events (list_archived 只读先验查询);
#             CLI python -m zephyr.ai_layer.comparator.experiment_store [--schema ai_compare] [--verify]
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] DDL-as-Code：ai_compare.ai_comparison_experiment DDL 真源即本文件（设计真源=L4 DESIGN §2.3，
#              挂 scripts/ai_layer/apply_ai_intake_ddl.py 同模式）；独立 schema `ai_compare` 与 L2 ai_intake
#              隔离（产线禁读界不破），schema 名白名单 ^ai_compare(_test_[a-z0-9_]*)?$ fail-closed；
#              时间戳一律 TIMESTAMPTZ（RULE-SCHEMA-TZ）；幂等 DDL（IF NOT EXISTS/DROP+CREATE TRIGGER）；
#              frozen 后 criteria_yaml/criteria_hash 不可变=DB 触发器+应用层 guard 双道（不可变锁）；
#              verdict append-only（旧裁定只增不改，变更判据=新 experiment_id）；status 流转
#              frozen→running→verdict→archived 单向（DB 触发器与应用层同表驱动）；
#              判读纯函数（transition/immutable/append 三 guard）与 SQL 渲染分离，可离线枚举单测
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.3（改表结构先改设计稿，走 OBJ_R）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] schema 名不合规→ValueError 立即拒跑（不静默改名）；frozen 判据字段 UPDATE→
#                  FrozenCriteriaError（应用层）+DB 触发器 RAISE EXCEPTION 双捕；verdict 二次改写→
#                  VerdictAppendOnlyError；非法 status 流转→ExperimentTransitionError；
#                  archived 前 verdict 缺失→拒绝归档；PG 不可达（CLI）→打印错误+退出码 2
# [TESTS] tests/ai_layer/comparator/test_experiment_store.py（三 guard 纯函数全枚举/DDL 断言/
#         FakeConn 注入 CRUD 流转/PG opt-in：真触发器拒 frozen 改判据+verdict append-only）
"""experiment_store — L4 实验卡库：`ai_compare.ai_comparison_experiment` DDL 登记器 + 卡服务。

设计真源：``docs/_working/ai_layer_vision/L4_compare/DESIGN.md`` §2.3（判据预注册双层结构的
实例层=考卷，一场一张卡）+ §2.6 独立性机检的不可变锁/append-only 落地点。schema ``ai_compare``
与 L2 ``ai_intake`` 同 PG 实例但 schema 级隔离（红蓝 R1-B9 裁定，产线禁读界不破）。

三道锁定机制的本件落点（DESIGN §2.3）::

    不可变锁  frozen 后 criteria_yaml/criteria_hash UPDATE 拒绝（触发器+应用层双道）+审计日志
    哈希锁    criteria_hash=canonical YAML 文本 sha256（执行器开考前重算比对，见 executor）
    时序锁    frozen_at/first_commit_at 时间戳字段在卡上，三时间戳机检在 executor.check_time_lock

status 流转单向::

    frozen → running → verdict → archived   （archived 前置：verdict 已定）
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from dataclasses import dataclass
from typing import Any, Final, Mapping

import yaml

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.infrastructure.database_service import get_db_service
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "ALLOWED_TRANSITIONS",
    "ExperimentDraft",
    "ComparisonExperimentRecord",
    "ExperimentStore",
    "FrozenCriteriaError",
    "ExperimentTransitionError",
    "SCHEMA_RE",
    "canonical_criteria_text",
    "check_frozen_update",
    "check_status_transition",
    "check_verdict_append",
    "criteria_hash",
    "new_experiment_id",
    "render_criteria_ref",
]

SCHEMA_RE: Final = re.compile(r"^ai_compare(_test_[a-z0-9_]+)?$")
DEFAULT_SCHEMA: Final = "ai_compare"
VERDICTS: Final = frozenset({"win", "win_starred", "draw", "loss", "rejected_too_good"})
TOO_GOOD_EXITS: Final = frozenset({"E1", "E2", "E3"})
ATTRIBUTIONS: Final = frozenset({"leakage", "hidden_risk", "luck_or_gaming"})
STATUS_FLOW: Final = ("frozen", "running", "verdict", "archived")
ALLOWED_TRANSITIONS: Final[dict[str, tuple[str, ...]]] = {
    "frozen": ("running",),
    "running": ("verdict",),
    "verdict": ("archived",),
}
FROZEN_IMMUTABLE_FIELDS: Final = ("criteria_yaml", "criteria_hash")
SLUG_RE: Final = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
DAY_RE: Final = re.compile(r"^\d{8}$")
EXPERIMENT_ID_RE: Final = re.compile(r"^EX-\d{8}-[a-z0-9][a-z0-9-]{0,63}$")


class FrozenCriteriaError(Exception):
    """frozen 后判据字段（criteria_yaml/criteria_hash）UPDATE 被拒（不可变锁）。"""


class VerdictAppendOnlyError(Exception):
    """verdict 已定后再改写被拒（旧裁定只增不改，DESIGN §2.6-7）。"""


class ExperimentTransitionError(Exception):
    """status 流转非法（只许 frozen→running→verdict→archived 单向）。"""


def check_schema_name(schema: str) -> str:
    """schema 名白名单校验（fail-closed：不合规直接 ValueError，绝不静默改名）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 ai_compare 或 ai_compare_test_<后缀>，"
            "防 DDL 打偏到他人 schema）"
        )
    return schema


def check_status_transition(current: str | None, target: str) -> tuple[bool, str]:
    """status 流转机检（纯函数）：只许 ALLOWED_TRANSITIONS 单向，其余拒绝。"""
    if target not in STATUS_FLOW:
        return False, f"unknown_status:{target}"
    if current == target:
        return True, "no_op"
    if current not in ALLOWED_TRANSITIONS or target not in ALLOWED_TRANSITIONS[current]:
        return False, f"illegal_transition:{current}->{target}"
    return True, "ok"


def check_frozen_update(field: str) -> tuple[bool, str]:
    """不可变锁机检（纯函数）：判据字段 frozen 后禁 UPDATE。"""
    if field in FROZEN_IMMUTABLE_FIELDS:
        return False, f"frozen_criteria_immutable:{field}"
    return True, "ok"


def check_verdict_append(current_verdict: str | None, new_verdict: str) -> tuple[bool, str]:
    """append-only verdict 机检（纯函数）：verdict 只许从 NULL 定一次，不许改写。"""
    if new_verdict not in VERDICTS:
        return False, f"unknown_verdict:{new_verdict}"
    if current_verdict is not None and current_verdict != "":
        return False, f"verdict_append_only:{current_verdict}"
    return True, "ok"


def new_experiment_id(day: str, slug: str) -> str:
    """生成 experiment_id=`EX-<yyyymmdd>-<slug>`（格式机检，DESIGN §2.3）。"""
    if not DAY_RE.match(day or ""):
        raise ValueError(f"day 需 yyyymmdd：{day!r}")
    if not SLUG_RE.match(slug or ""):
        raise ValueError(f"slug 需小写字母数字连字符且 ≤64 字符：{slug!r}")
    return f"EX-{day}-{slug}"


def render_criteria_ref(experiment_id: str, criteria_hash: str) -> str:
    """任务书 criteria_ref 锚点：`<experiment_id>#<hash>`（DESIGN §2.3 时序锁）。"""
    if not EXPERIMENT_ID_RE.match(experiment_id or ""):
        raise ValueError(f"experiment_id 格式不合规：{experiment_id!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", criteria_hash or ""):
        raise ValueError(f"criteria_hash 需 64 位 sha256 hex：{criteria_hash!r}")
    return f"{experiment_id}#{criteria_hash}"


def canonical_criteria_text(criteria: Mapping[str, Any]) -> str:
    """判据字典 → canonical YAML 文本（sort_keys 确定性序列化，哈希锁的输入）。"""
    return yaml.safe_dump(
        dict(criteria), sort_keys=True, allow_unicode=True, default_flow_style=False
    )


def criteria_hash(canonical_text: str) -> str:
    """canonical 文本 sha256（哈希锁 SSOT）。"""
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# DDL-as-Code（独立 schema ai_compare；幂等；TIMESTAMPTZ）
# ---------------------------------------------------------------------------

_SQL_TABLE = """
CREATE TABLE IF NOT EXISTS {s}.ai_comparison_experiment (
    experiment_id     TEXT PRIMARY KEY,
    challenger_ref    TEXT NOT NULL,
    champion_ref      TEXT NOT NULL,
    venue_ref         TEXT NOT NULL CHECK (venue_ref IN
                          ('venue_c4','venue_replay','venue_dual_run','venue_tool_bench')),
    domain_id         TEXT,
    mechanism_family  TEXT,
    candidate_simhash TEXT,
    criteria_yaml     TEXT NOT NULL,
    criteria_hash     CHAR(64) NOT NULL,
    status            TEXT NOT NULL DEFAULT 'frozen'
                          CHECK (status IN ('frozen','running','verdict','archived')),
    fairness_fields   JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    verdict           TEXT CHECK (verdict IN ('win','win_starred','draw','loss','rejected_too_good')),
    too_good_exit     TEXT CHECK (too_good_exit IN ('E1','E2','E3')),
    attribution       TEXT CHECK (attribution IN ('leakage','hidden_risk','luck_or_gaming')),
    rejection_reason  TEXT,
    evidence_ref      TEXT,
    verdict_log       JSONB NOT NULL DEFAULT '[]'::jsonb,
    evaluator_session   TEXT NOT NULL,
    contractor_session  TEXT NOT NULL,
    dispatched_at     TIMESTAMPTZ,
    first_commit_at   TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    frozen_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_SQL_TRIGGER_FN = """
CREATE OR REPLACE FUNCTION {s}.trg_ai_comparison_experiment_guard() RETURNS trigger AS $fn$
BEGIN
    IF NEW.criteria_yaml IS DISTINCT FROM OLD.criteria_yaml
       OR NEW.criteria_hash IS DISTINCT FROM OLD.criteria_hash THEN
        RAISE EXCEPTION 'frozen_criteria_immutable: %', OLD.experiment_id;
    END IF;
    IF NEW.verdict IS DISTINCT FROM OLD.verdict AND OLD.verdict IS NOT NULL THEN
        RAISE EXCEPTION 'verdict_append_only: %', OLD.experiment_id;
    END IF;
    IF NEW.status IS DISTINCT FROM OLD.status AND NOT (
           (OLD.status = 'frozen'  AND NEW.status = 'running')
        OR (OLD.status = 'running' AND NEW.status = 'verdict')
        OR (OLD.status = 'verdict' AND NEW.status = 'archived')) THEN
        RAISE EXCEPTION 'illegal_status_transition: % -> %', OLD.status, NEW.status;
    END IF;
    IF NEW.status = 'archived' AND NEW.verdict IS NULL THEN
        RAISE EXCEPTION 'archive_requires_verdict: %', NEW.experiment_id;
    END IF;
    RETURN NEW;
END;
$fn$ LANGUAGE plpgsql
"""

_SQL_TRIGGER_DROP = (
    "DROP TRIGGER IF EXISTS trg_ai_comparison_experiment_guard ON {s}.ai_comparison_experiment"
)
_SQL_TRIGGER_CREATE = """
CREATE TRIGGER trg_ai_comparison_experiment_guard
BEFORE UPDATE ON {s}.ai_comparison_experiment
FOR EACH ROW EXECUTE FUNCTION {s}.trg_ai_comparison_experiment_guard()
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS ix_ai_compare_status ON {s}.ai_comparison_experiment (status)",
    "CREATE INDEX IF NOT EXISTS ix_ai_compare_venue ON {s}.ai_comparison_experiment (venue_ref, status)",
    "CREATE INDEX IF NOT EXISTS ix_ai_compare_family ON {s}.ai_comparison_experiment (mechanism_family)",
)

_SQL_GRANTS: Final[tuple[str, ...]] = (
    "GRANT USAGE ON SCHEMA {s} TO depgraph_reader",
    "GRANT USAGE ON SCHEMA {s} TO depgraph_writer",
    "GRANT SELECT ON {s}.ai_comparison_experiment TO depgraph_reader",
    "GRANT SELECT, INSERT, UPDATE ON {s}.ai_comparison_experiment TO depgraph_writer",
)


def _ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL 语句（幂等；schema 名已由 check_schema_name 校验）。"""
    return [
        f"CREATE SCHEMA IF NOT EXISTS {schema}",
        _SQL_TABLE.format(s=schema),
        _SQL_TRIGGER_FN.format(s=schema),
        _SQL_TRIGGER_DROP.format(s=schema),
        _SQL_TRIGGER_CREATE.format(s=schema),
        *(tpl.format(s=schema) for tpl in _SQL_INDEXES),
    ]


_EXPECTED_RELATIONS: Final[tuple[str, ...]] = ("ai_comparison_experiment",)

SQL_VERIFY = (
    "SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name"
)
# information_schema.triggers 对非表主角色不可见（reader 实测空集），改查 pg_trigger（角色无关）
SQL_HAS_TRIGGER = (
    "SELECT 1 FROM pg_trigger t "
    "JOIN pg_class c ON c.oid = t.tgrelid "
    "JOIN pg_namespace n ON n.oid = c.relnamespace "
    "WHERE n.nspname = %s AND t.tgname = 'trg_ai_comparison_experiment_guard' "
    "AND t.tgisinternal = false"
)


def deploy(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> int:
    """部署/刷新 ai_compare schema（幂等，admin 通道）。返回执行语句数。

    :param schema: 目标 schema（白名单校验）
    :param conn: 可选已存在连接（测试注入用）；缺省自建 superuser 连接（apply_ai_intake_ddl
                 同模式）并负责关闭。角色分级 GRANT：角色缺席（本地精简实例）时 SAVEPOINT
                 回滚该条只告警不阻断（DDL 主体是事务性的，不能整事务回滚）。
    """
    check_schema_name(schema)
    own = conn is None
    if own:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    executed = 0
    try:
        cur = conn.cursor()
        for stmt in _ddl_statements(schema):
            cur.execute(stmt)
            executed += 1
        for grant in _SQL_GRANTS:
            cur.execute("SAVEPOINT sp_grant")
            try:
                cur.execute(grant.format(s=schema))
                executed += 1
                cur.execute("RELEASE SAVEPOINT sp_grant")
            except Exception as exc:  # noqa: BLE001——授权失败不阻断 DDL 主体，warning 留痕
                log.warning("GRANT 跳过：%s", exc)
                cur.execute("ROLLBACK TO SAVEPOINT sp_grant")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if own:
            conn.close()
    return executed


def _row_to_map(cur: Any, row: Any) -> dict[str, Any]:
    """行 → 列名映射（DatabaseService 字典游标与裸元组游标双兼容）。"""
    if isinstance(row, dict):
        return dict(row)
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def verify(schema: str = DEFAULT_SCHEMA) -> tuple[bool, list[str]]:
    """核对表与守卫触发器是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(read_only=True)
    missing: list[str] = []
    try:
        cur = conn.cursor()
        cur.execute(SQL_VERIFY, (schema,))
        found = {row[0] for row in cur.fetchall()}
        missing.extend(f"table:{t}" for t in _EXPECTED_RELATIONS if t not in found)
        cur.execute(SQL_HAS_TRIGGER, (schema,))
        if not cur.fetchall():
            missing.append("trigger:trg_ai_comparison_experiment_guard")
    finally:
        conn.close()
    return (not missing), missing


def _row_str(row: Mapping[str, Any], key: str, default: str = "") -> str:
    """ComparisonExperimentRecord.from_row 内联逻辑搬移：str(row.get(key) or default)。"""
    return str(row.get(key) or default)


def _row_optional(row: Mapping[str, Any], key: str) -> Any:
    """ComparisonExperimentRecord.from_row 内联逻辑搬移：真值保原值，假值（空串/None）归一 None。"""
    value = row.get(key)
    return value if value else None


@dataclass(frozen=True)
class ComparisonExperimentRecord:
    """实验卡只读快照（DB 行的应用层形态）。"""

    experiment_id: str
    challenger_ref: str
    champion_ref: str
    venue_ref: str
    criteria_yaml: str
    criteria_hash: str
    status: str
    evaluator_session: str
    contractor_session: str
    mechanism_family: str | None = None
    candidate_simhash: str | None = None
    verdict: str | None = None
    too_good_exit: str | None = None
    attribution: str | None = None
    rejection_reason: str | None = None
    evidence_ref: str | None = None
    frozen_at: str | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "ComparisonExperimentRecord":
        """DB 行 → 卡（缺字段给安全默认，不炸——历史行兼容）。"""
        return cls(
            experiment_id=_row_str(row, "experiment_id"),
            challenger_ref=_row_str(row, "challenger_ref"),
            champion_ref=_row_str(row, "champion_ref"),
            venue_ref=_row_str(row, "venue_ref"),
            criteria_yaml=_row_str(row, "criteria_yaml"),
            criteria_hash=_row_str(row, "criteria_hash"),
            status=_row_str(row, "status", "frozen"),
            evaluator_session=_row_str(row, "evaluator_session"),
            contractor_session=_row_str(row, "contractor_session"),
            mechanism_family=_row_optional(row, "mechanism_family"),
            candidate_simhash=_row_optional(row, "candidate_simhash"),
            verdict=_row_optional(row, "verdict"),
            too_good_exit=_row_optional(row, "too_good_exit"),
            attribution=_row_optional(row, "attribution"),
            rejection_reason=_row_optional(row, "rejection_reason"),
            evidence_ref=_row_optional(row, "evidence_ref"),
            frozen_at=_row_str(row, "frozen_at") or None,
        )


_SQL_INSERT = """
INSERT INTO {s}.ai_comparison_experiment (
    experiment_id, challenger_ref, champion_ref, venue_ref, domain_id, mechanism_family,
    candidate_simhash, criteria_yaml, criteria_hash, status, fairness_fields,
    evaluator_session, contractor_session, dispatched_at, first_commit_at
) VALUES (
    %(experiment_id)s, %(challenger_ref)s, %(champion_ref)s, %(venue_ref)s, %(domain_id)s,
    %(mechanism_family)s, %(candidate_simhash)s, %(criteria_yaml)s, %(criteria_hash)s,
    'frozen', %(fairness_fields)s::jsonb, %(evaluator_session)s, %(contractor_session)s,
    %(dispatched_at)s, %(first_commit_at)s
)
"""

_SQL_GET = (
    "SELECT * FROM {s}.ai_comparison_experiment WHERE experiment_id = %s"
)
_SQL_LIST_ARCHIVED = (
    "SELECT * FROM {s}.ai_comparison_experiment WHERE status = 'archived' ORDER BY frozen_at"
)


@dataclass(frozen=True)
class ExperimentDraft:
    """预注册落卡的上下文打包（NO-LONG-PARAM-LIST 处方，同 rule_replay.ReplayTarget 惯例）。"""

    experiment_id: str
    challenger_ref: str
    champion_ref: str
    venue_ref: str
    evaluator_session: str
    contractor_session: str
    domain_id: str | None = None
    mechanism_family: str | None = None
    candidate_simhash: str | None = None
    fairness_fields: Mapping[str, Any] | None = None
    dispatched_at: Any | None = None
    first_commit_at: Any | None = None


class ExperimentStore:
    """L4 实验卡服务：预注册落卡 + 单向流转 + append-only verdict（全经 DatabaseService）。"""

    def __init__(
        self,
        schema: str = DEFAULT_SCHEMA,
        service: Any | None = None,
        write_conn: Any | None = None,
    ) -> None:
        check_schema_name(schema)
        self.schema: Final = schema
        self._svc = service or get_db_service()
        self._write_conn_override: Final = write_conn
        self._write_conn: Any | None = None

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    def read_conn(self) -> Any:
        """只读连接：经 DatabaseService（读路径唯一真源，read_only=True）。"""
        return self._svc.get_depgraph_conn(read_only=True)

    def write_conn(self) -> Any:
        """写连接（depgraph_writer 角色，进程内复用一条；测试可注入）。"""
        if self._write_conn_override is not None:
            return self._write_conn_override
        if self._write_conn is None or self._write_conn.closed:
            # card_store 同款处置：DatabaseService 写侧当前不可达（req_ailayerB_03 留痕），
            # 直连 depgraph_schema 写角色入口；DEPGRAPH-WRITE-PATH 白名单登记由主会话统一执行。
            self._write_conn = get_depgraph_pg_connection(read_only=False, autocommit=True)
        return self._write_conn

    def close(self) -> None:
        """释放本实例持有的写连接（读连接归 DatabaseService 生命周期管）。"""
        if self._write_conn is not None and not self._write_conn.closed:
            self._write_conn.close()
        self._write_conn = None

    def freeze(self, draft: ExperimentDraft, criteria: Mapping[str, Any]) -> ComparisonExperimentRecord:
        """预注册落卡：canonical 判据+哈希一次性冻结（status=frozen，不可变锁即日生效）。"""
        missing = [
            name
            for name in ("experiment_id", "challenger_ref", "champion_ref", "venue_ref",
                         "evaluator_session", "contractor_session")
            if not str(getattr(draft, name) or "").strip()
        ]
        if missing:
            raise ValueError(f"freeze 缺必填字段:{','.join(missing)}")
        if draft.venue_ref not in {"venue_c4", "venue_replay", "venue_dual_run", "venue_tool_bench"}:
            raise ValueError(f"未知考场:{draft.venue_ref}")
        if draft.evaluator_session == draft.contractor_session:
            raise ValueError("session_mutuality_violation:contractor==evaluator（拒考，DESIGN §2.6-1）")
        canonical = canonical_criteria_text(criteria)
        params = {
            "experiment_id": draft.experiment_id,
            "challenger_ref": draft.challenger_ref,
            "champion_ref": draft.champion_ref,
            "venue_ref": draft.venue_ref,
            "domain_id": draft.domain_id,
            "mechanism_family": draft.mechanism_family,
            "candidate_simhash": draft.candidate_simhash,
            "criteria_yaml": canonical,
            "criteria_hash": criteria_hash(canonical),
            "fairness_fields": json.dumps(dict(draft.fairness_fields or {}), ensure_ascii=False),
            "evaluator_session": draft.evaluator_session,
            "contractor_session": draft.contractor_session,
            "dispatched_at": draft.dispatched_at,
            "first_commit_at": draft.first_commit_at,
        }
        self.write_conn().cursor().execute(self._sql(_SQL_INSERT), params)
        return self.get(draft.experiment_id)  # type: ignore[return-value]

    def get(self, experiment_id: str) -> ComparisonExperimentRecord | None:
        """按 id 取卡（只读）；不存在返回 None。"""
        cur = self.read_conn().cursor()
        cur.execute(self._sql(_SQL_GET), (experiment_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return ComparisonExperimentRecord.from_row(_row_to_map(cur, row))

    def transition(self, experiment_id: str, target: str) -> tuple[bool, str]:
        """status 单向流转（frozen→running→verdict→archived）；非法流转抛 ExperimentTransitionError。"""
        current = self.get(experiment_id)
        if current is None:
            raise KeyError(f"experiment_not_found:{experiment_id}")
        ok, why = check_status_transition(current.status, target)
        if not ok and why != "no_op":
            raise ExperimentTransitionError(f"{experiment_id}:{why}")
        if why == "no_op":
            return True, why
        self.write_conn().cursor().execute(
            f"UPDATE {self.schema}.ai_comparison_experiment "
            "SET status = %s, updated_at = %s WHERE experiment_id = %s",
            (target, now_utc(), experiment_id),
        )
        return True, why

    def set_verdict(
        self,
        experiment_id: str,
        verdict: str,
        *,
        evidence_ref: str | None = None,
        too_good_exit: str | None = None,
        attribution: str | None = None,
        rejection_reason: str | None = None,
    ) -> tuple[bool, str]:
        """append-only 定裁：verdict 只许从 NULL 定一次；E3 必附归因三选一（留痕）。"""
        current = self.get(experiment_id)
        if current is None:
            raise KeyError(f"experiment_not_found:{experiment_id}")
        ok, why = check_verdict_append(current.verdict, verdict)
        if not ok:
            raise VerdictAppendOnlyError(f"{experiment_id}:{why}")
        if verdict == "rejected_too_good" and attribution not in ATTRIBUTIONS:
            raise ValueError(f"rejected_too_good 必附归因三选一，得:{attribution!r}")
        if too_good_exit is not None and too_good_exit not in TOO_GOOD_EXITS:
            raise ValueError(f"too_good_exit 需 E1/E2/E3，得:{too_good_exit!r}")
        log_entry = json.dumps(
            {
                "verdict": verdict,
                "evidence_ref": evidence_ref,
                "too_good_exit": too_good_exit,
                "attribution": attribution,
                "rejection_reason": rejection_reason,
                "ruled_at": now_utc().isoformat(),
                "evaluator_session": current.evaluator_session,
            },
            ensure_ascii=False,
        )
        self.write_conn().cursor().execute(
            f"UPDATE {self.schema}.ai_comparison_experiment "
            "SET verdict = %s, evidence_ref = COALESCE(%s, evidence_ref), too_good_exit = %s, "
            "attribution = %s, rejection_reason = %s, "
            "verdict_log = verdict_log || %s::jsonb, updated_at = %s "
            "WHERE experiment_id = %s",
            (
                verdict,
                evidence_ref,
                too_good_exit,
                attribution,
                rejection_reason,
                log_entry,
                now_utc(),
                experiment_id,
            ),
        )
        return True, why

    def archive(self, experiment_id: str) -> tuple[bool, str]:
        """归档（verdict 已定才许）；归档事件 comparison_archived_due 由 compare_events 层 emit。"""
        current = self.get(experiment_id)
        if current is None:
            raise KeyError(f"experiment_not_found:{experiment_id}")
        if not current.verdict:
            raise ValueError(f"archive_requires_verdict:{experiment_id}")
        return self.transition(experiment_id, "archived")

    def list_archived(self) -> list[ComparisonExperimentRecord]:
        """只读：全部 archived 卡（comparison_prior_query 先验查询的数据面）。"""
        cur = self.read_conn().cursor()
        cur.execute(self._sql(_SQL_LIST_ARCHIVED))
        return [ComparisonExperimentRecord.from_row(_row_to_map(cur, row)) for row in cur.fetchall()]


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署或核对 ai_compare schema（apply_ai_intake_ddl 同模式）。"""
    import argparse

    parser = argparse.ArgumentParser(description="L4 实验卡库 DDL 部署器（ai_compare，幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_compare）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.verify:
            ok, missing = verify(args.schema)
            print(f"VERIFY {args.schema}: {'OK' if ok else 'MISSING ' + ','.join(missing)}")
            return 0 if ok else 3
        n = deploy(args.schema)
        ok, missing = verify(args.schema)
        print(f"DEPLOYED {args.schema} stmts={n} verify={'OK' if ok else missing}")
        return 0 if ok else 3
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001——CLI 边界统一转退出码 2（PG 不可达/权限不足等）
        print(f"DDL FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    sys.exit(main())
