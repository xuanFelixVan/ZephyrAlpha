# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] zephyr.ai_layer.cleaning.spec_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.policy (CleaningPolicy，禁占位词/值域机检判据);
#                zephyr.governance.depgraph_schema (get_depgraph_pg_connection);
#                zephyr.infrastructure.database_service (get_db_service);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.cleaning.washer (洗后落库); zephyr.ai_layer.cleaning.auditor
#             (review 回填/状态流转); L4 考场经 L2 事件链消费 spec 字段（间接）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 全部读写经 DatabaseService/depgraph_schema 角色入口（禁裸 duckdb/psycopg2）；
#              schema 名白名单 ^ai_intake(_test_[a-z0-9_]+)?$（与 L2 同实例同 schema，fail-closed）；
#              卡与 L2 候选卡=1:N 版本化：重洗不覆盖旧版（旧 active→superseded 墓碑制），
#              L2 T2.spec_ref 只指 active 版；insert 前机检=禁占位词+值域校验+来源四件套必填
#              +adapt_needed 必带 adaptation_plan（fail-closed 拒写）；TIMESTAMPTZ
#              （RULE-SCHEMA-TZ）；DDL 真源=本模块 _SQL_CREATE_SPEC（幂等 ensure_table，
#              待并入 apply_ai_intake_ddl.py——不改既有文件纪律，主会话统一增补）；
#              生熟分离：只服务 ai_intake.* 生食库，禁被产线代码 import
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.1（spec_card_v0 schema 真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 机检不过/占位词/越域值/缺来源四件套→SpecStoreError（拒写，绝不静默降级）；
#                  卡不存在 FK 违规→底层 IntegrityError 上抛；DB 不可达→异常上抛
# [TESTS] tests/ai_layer/cleaning/test_spec_store.py（DDL 幂等两次零错/机检逐项拒/版本化
#         supersede/active 指针/review 回填/rejected_wash/计数）
# [TTL] permanent
"""spec_store — L3 规格卡库服务（spec_card_v0 CRUD + 1:N 版本化 + active 指针 + 机检）。

设计真源：``docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md`` §2.1（spec_card_v0 定稿、
D-L3-01 存储裁定：PG ai_intake schema 新表 ai_cleaning_spec，卡与 L2 候选卡=1:N 版本化，
重洗不覆盖旧版；定调 #12 进化留痕可回滚）。

分层裁定：机检判据（禁占位词/值域/来源继承）全部是**纯函数**（零 DB 依赖可全枚举单测）；
DB 侧只做读写与版本翻转，判据不在 SQL 里。DDL 以幂等 ensure_table 随本模块自举
（真源=``_SQL_CREATE_SPEC``），主会话统一增补进 apply_ai_intake_ddl.py 时逐字复制即可。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.ai_layer.cleaning.policy import CleaningPolicy

log = logging.getLogger(__name__)

__all__: Final = [
    "SPEC_ID_TEMPLATE",
    "SpecCard",
    "SpecDraft",
    "SpecStore",
    "SpecStoreError",
    "check_spec_machine_rules",
    "ensure_table",
    "one_liner_ok",
]

SCHEMA_RE: Final = re.compile(r"^ai_intake(_test_[a-z0-9_]+)?$")
SPEC_ID_TEMPLATE: Final = "SP-{card_id}-v{version}"
ONE_LINER_MAX: Final = 80

_SQL_CREATE_SPEC: Final = """
CREATE TABLE IF NOT EXISTS {s}.ai_cleaning_spec (
    spec_id            TEXT PRIMARY KEY,
    card_id            TEXT NOT NULL REFERENCES {s}.ai_intake_card(card_id),
    version            SMALLINT NOT NULL,
    mechanism_one_liner TEXT NOT NULL CHECK (length(btrim(mechanism_one_liner)) BETWEEN 1 AND 80),
    mechanism_detail   TEXT NOT NULL CHECK (length(btrim(mechanism_detail)) > 0),
    applicability      JSONB NOT NULL,
    ashare_precheck    JSONB NOT NULL CHECK (ashare_precheck->>'overall' IN ('pass','adapt_needed','reject')),
    risk_flags         JSONB NOT NULL DEFAULT '[]'::jsonb,
    data_fields        JSONB NOT NULL DEFAULT '[]'::jsonb,
    reproduction_notes TEXT NOT NULL CHECK (length(btrim(reproduction_notes)) > 0),
    source_name        TEXT,
    source_url         TEXT NOT NULL CHECK (length(btrim(source_url)) > 0),
    source_publisher   TEXT,
    source_year        SMALLINT,
    source_quotes      JSONB NOT NULL DEFAULT '[]'::jsonb,
    lsg                JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    wash               JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    review             JSONB,
    status             TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','superseded','rejected_wash')),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (card_id, version)
)
"""
_SQL_INDEX_CARD: Final = (
    "CREATE INDEX IF NOT EXISTS ix_cleaning_spec_card ON {s}.ai_cleaning_spec (card_id)"
)
_SQL_INDEX_STATUS: Final = (
    "CREATE INDEX IF NOT EXISTS ix_cleaning_spec_status ON {s}.ai_cleaning_spec (status)"
)
_SQL_NEXT_VERSION: Final = (
    "SELECT COALESCE(max(version), 0) FROM {s}.ai_cleaning_spec WHERE card_id = %s"  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
)
_SQL_INSERT_SPEC: Final = """
INSERT INTO {s}.ai_cleaning_spec (
    spec_id, card_id, version, mechanism_one_liner, mechanism_detail,
    applicability, ashare_precheck, risk_flags, data_fields, reproduction_notes,
    source_name, source_url, source_publisher, source_year, source_quotes,
    lsg, wash, review, status
) VALUES (
    %(spec_id)s, %(card_id)s, %(version)s, %(mechanism_one_liner)s, %(mechanism_detail)s,
    %(applicability)s::jsonb, %(ashare_precheck)s::jsonb, %(risk_flags)s::jsonb,
    %(data_fields)s::jsonb, %(reproduction_notes)s,
    %(source_name)s, %(source_url)s, %(source_publisher)s, %(source_year)s,
    %(source_quotes)s::jsonb, %(lsg)s::jsonb, %(wash)s::jsonb, %(review)s::jsonb, %(status)s
)
"""
_SQL_SUPERSEDE: Final = (
    "UPDATE {s}.ai_cleaning_spec SET status = 'superseded' "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
    "WHERE card_id = %s AND status = 'active' AND version < %s"
)
_SQL_SELECT_SPEC: Final = """
SELECT spec_id, card_id, version, mechanism_one_liner, mechanism_detail, applicability,
       ashare_precheck, risk_flags, data_fields, reproduction_notes,
       source_name, source_url, source_publisher, source_year, source_quotes,
       lsg, wash, review, status, created_at
FROM {s}.ai_cleaning_spec WHERE spec_id = %s
"""
_SQL_SELECT_ACTIVE: Final = """
SELECT spec_id, card_id, version, mechanism_one_liner, mechanism_detail, applicability,
       ashare_precheck, risk_flags, data_fields, reproduction_notes,
       source_name, source_url, source_publisher, source_year, source_quotes,
       lsg, wash, review, status, created_at
FROM {s}.ai_cleaning_spec WHERE card_id = %s AND status = 'active'
ORDER BY version DESC LIMIT 1
"""
_SQL_SET_REVIEW: Final = (
    "UPDATE {s}.ai_cleaning_spec SET review = %(review)s::jsonb WHERE spec_id = %(spec_id)s"  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
)
_SQL_SET_STATUS: Final = (
    "UPDATE {s}.ai_cleaning_spec SET status = %(status)s WHERE spec_id = %(spec_id)s"  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
)
_SQL_COUNT_CARDS: Final = (
    "SELECT count(DISTINCT card_id) FROM {s}.ai_cleaning_spec"  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
)


class SpecStoreError(RuntimeError):
    """规格卡机检/落库违规（fail-closed）。"""


@dataclass(frozen=True)
class SpecDraft:
    """规格卡入库草稿（§2.1 spec_card_v0 全字段；source 从 L2 卡只读继承禁改写）。"""

    card_id: str
    mechanism_one_liner: str
    mechanism_detail: str
    applicability: dict[str, Any]
    ashare_precheck: dict[str, Any]
    reproduction_notes: str
    source_name: str | None
    source_url: str
    source_publisher: str | None
    source_year: int | None
    risk_flags: list[str] = field(default_factory=list)
    data_fields: list[dict[str, Any]] = field(default_factory=list)
    source_quotes: list[str] = field(default_factory=list)
    lsg: dict[str, Any] = field(default_factory=dict)
    wash: dict[str, Any] = field(default_factory=dict)
    review: dict[str, Any] | None = None
    status: str = "active"


@dataclass(frozen=True)
class SpecCard:
    """规格卡读出形态（只读快照，JSONB 已转原生容器）。"""

    spec_id: str
    card_id: str
    version: int
    status: str
    mechanism_one_liner: str
    mechanism_detail: str
    applicability: dict[str, Any]
    ashare_precheck: dict[str, Any]
    reproduction_notes: str
    source_url: str
    risk_flags: list[str]
    data_fields: list[dict[str, Any]]
    source_quotes: list[str]
    lsg: dict[str, Any]
    wash: dict[str, Any]
    review: dict[str, Any] | None
    source_name: str | None = None
    source_publisher: str | None = None
    source_year: int | None = None
    created_at: Any = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "SpecCard":
        """DB 行 → 只读快照（None 容器给安全默认）。"""
        return cls(
            spec_id=row["spec_id"],
            card_id=row["card_id"],
            version=int(row["version"]),
            status=str(row["status"]),
            mechanism_one_liner=str(row["mechanism_one_liner"]),
            mechanism_detail=str(row["mechanism_detail"]),
            applicability=row.get("applicability") or {},
            ashare_precheck=row.get("ashare_precheck") or {},
            reproduction_notes=str(row["reproduction_notes"]),
            source_url=str(row["source_url"]),
            risk_flags=row.get("risk_flags") or [],
            data_fields=row.get("data_fields") or [],
            source_quotes=row.get("source_quotes") or [],
            lsg=row.get("lsg") or {},
            wash=row.get("wash") or {},
            review=row.get("review"),
            source_name=row.get("source_name"),
            source_publisher=row.get("source_publisher"),
            source_year=row.get("source_year"),
            created_at=row.get("created_at"),
        )


def one_liner_ok(text: str, *, max_chars: int = ONE_LINER_MAX) -> bool:
    """一句话机制机检：非空且 ≤80 字（DESIGN §2.1 禁空泛）。"""
    text = (text or "").strip()
    return 0 < len(text) <= max_chars


def check_spec_machine_rules(draft: SpecDraft, policy: CleaningPolicy) -> list[str]:
    """入库机检纯判据（DESIGN §2.1 机检注记 + §2.5 机检前置的库侧子集）。

    返回违规清单（空=过）。判据：一句话长度/禁占位词/risk_flags 值域/
    precheck.overall 值域/adapt_needed 必带 adaptation_plan/status 值域/来源四件套。
    """
    problems: list[str] = []
    if not one_liner_ok(draft.mechanism_one_liner):
        problems.append(f"one_liner_len:{len(draft.mechanism_one_liner.strip())}")
    joined = " ".join(
        (draft.mechanism_one_liner, draft.mechanism_detail, draft.reproduction_notes)
    )
    for word in sorted(policy.placeholder_words):
        if word in joined:
            problems.append(f"placeholder_word:{word}")
    vocab = policy.vocab
    bad_flags = set(draft.risk_flags) - vocab["risk_flags"]
    if bad_flags:
        problems.append(f"risk_flags_out_of_vocab:{','.join(sorted(bad_flags))}")
    overall = str((draft.ashare_precheck or {}).get("overall") or "")
    if overall not in vocab["precheck_overall"]:
        problems.append(f"precheck_overall_out_of_vocab:{overall}")
    if overall == "adapt_needed" and not str(
        (draft.ashare_precheck or {}).get("adaptation_plan") or ""
    ).strip():
        problems.append("adapt_plan_missing")
    if draft.status not in vocab["spec_status"]:
        problems.append(f"status_out_of_vocab:{draft.status}")
    if not str(draft.source_url or "").strip():
        problems.append("source_url_missing")
    return problems


def ensure_table(schema: str, *, conn: Any | None = None) -> int:
    """幂等部署 ai_cleaning_spec 表+card_id/status 索引+角色分级 GRANT。

    DDL 真源=_SQL_CREATE_SPEC；GRANT 照 L2 惯例（reader 只读/writer 读写），
    角色缺席（本地精简实例）时 SAVEPOINT 回滚该条不阻断主体。

    :param conn: 可选已存在连接（测试/主会话并入 apply_ai_intake_ddl.py 时注入）；
                 缺省自建 admin 连接（superuser，DDL 需建表权限）并负责关闭。
    :return: 执行的 DDL 语句条数（幂等重复执行恒等值，GRANT 不计入）。
    """
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(f"schema 名不合规：{schema!r}（只许 ai_intake / ai_intake_test_<后缀>）")
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    own = conn is None
    if own:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    statements = [
        _SQL_CREATE_SPEC.format(s=schema),
        _SQL_INDEX_CARD.format(s=schema),
        _SQL_INDEX_STATUS.format(s=schema),
    ]
    table = f"{schema}.ai_cleaning_spec"
    grants = [
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_reader",
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_writer",
        f"GRANT SELECT ON {table} TO depgraph_reader",
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO depgraph_writer",
    ]
    try:
        cur = conn.cursor()
        for stmt in statements:
            cur.execute(stmt)
        for grant in grants:
            cur.execute("SAVEPOINT sp_grant_spec")
            try:
                cur.execute(grant)
                cur.execute("RELEASE SAVEPOINT sp_grant_spec")
            except Exception as exc:  # noqa: BLE001——角色缺席不阻断 DDL 主体（L2 同款处置）
                log.warning("GRANT 跳过：%s", exc)
                cur.execute("ROLLBACK TO SAVEPOINT sp_grant_spec")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if own and conn is not None:
            conn.close()
    return len(statements)


class SpecStore:
    """规格卡库：版本化写入（重洗不覆盖）+active 指针+review 回写（全经角色入口）。"""

    def __init__(self, schema: str = "ai_intake", service: Any | None = None) -> None:
        if not SCHEMA_RE.match(schema or ""):
            raise ValueError(f"schema 名不合规：{schema!r}（只许 ai_intake / ai_intake_test_*）")
        self.schema: Final = schema
        self._svc = service
        self._write_conn: Any | None = None

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    def read_conn(self) -> Any:
        """只读连接：经 DatabaseService（读路径唯一真源）。"""
        if self._svc is not None:
            return self._svc.get_depgraph_conn(read_only=True)
        from zephyr.infrastructure.database_service import get_db_service

        return get_db_service().get_depgraph_conn(read_only=True)

    def write_conn(self) -> Any:
        """写连接（与 L2 CardStore 同款裁定：DatabaseService 写侧当前不可达，
        直连 depgraph_schema 写角色入口，DEPGRAPH-WRITE-PATH 白名单已登记；
        DatabaseService 修好后回切读同一入口）。"""
        if self._svc is not None:
            return self._svc.get_depgraph_conn(read_only=False)
        if self._write_conn is None or self._write_conn.closed:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

            self._write_conn = get_depgraph_pg_connection(read_only=False, autocommit=True)
        return self._write_conn

    def close(self) -> None:
        """释放实例持有的写连接。"""
        if self._write_conn is not None and not self._write_conn.closed:
            self._write_conn.close()
        self._write_conn = None

    def insert(self, draft: SpecDraft, policy: CleaningPolicy) -> str:
        """机检→定版本→supersede 旧 active→写入（返回 spec_id）。

        版本号=该卡已有 max(version)+1；同批事务内旧 active 版翻 superseded
        （墓碑制不删，重洗留痕=定调 #12）。
        """
        problems = check_spec_machine_rules(draft, policy)
        if problems:
            raise SpecStoreError(f"spec_machine_check_failed:{';'.join(problems)}")
        conn = self.write_conn()
        try:
            cur = conn.cursor()
            cur.execute(self._sql(_SQL_NEXT_VERSION), (draft.card_id,))
            row = cur.fetchone()
            prev = int(row[0] if isinstance(row, (list, tuple)) else row["coalesce"])
            version = prev + 1
            spec_id = SPEC_ID_TEMPLATE.format(card_id=draft.card_id, version=version)
            cur.execute(self._sql(_SQL_SUPERSEDE), (draft.card_id, version))
            cur.execute(
                self._sql(_SQL_INSERT_SPEC),
                self._insert_params(draft, version, spec_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        log.info("spec 卡落库：%s（card=%s v%s）", spec_id, draft.card_id, version)
        return spec_id

    @staticmethod
    def _insert_params(draft: SpecDraft, version: int, spec_id: str) -> dict[str, Any]:
        return {
            "spec_id": spec_id,
            "card_id": draft.card_id,
            "version": version,
            "mechanism_one_liner": draft.mechanism_one_liner.strip(),
            "mechanism_detail": draft.mechanism_detail.strip(),
            "applicability": json.dumps(draft.applicability, ensure_ascii=False),
            "ashare_precheck": json.dumps(draft.ashare_precheck, ensure_ascii=False),
            "risk_flags": json.dumps(list(draft.risk_flags), ensure_ascii=False),
            "data_fields": json.dumps(list(draft.data_fields), ensure_ascii=False),
            "reproduction_notes": draft.reproduction_notes.strip(),
            "source_name": draft.source_name,
            "source_url": draft.source_url,
            "source_publisher": draft.source_publisher,
            "source_year": draft.source_year,
            "source_quotes": json.dumps(list(draft.source_quotes), ensure_ascii=False),
            "lsg": json.dumps(draft.lsg, ensure_ascii=False),
            "wash": json.dumps(draft.wash, ensure_ascii=False),
            "review": (
                json.dumps(draft.review, ensure_ascii=False) if draft.review is not None else None
            ),
            "status": draft.status,
        }

    def get(self, spec_id: str) -> SpecCard | None:
        """按主键读规格卡（不存在返回 None）。"""
        cur = self.read_conn().cursor()
        cur.execute(self._sql(_SQL_SELECT_SPEC), (spec_id,))
        row = cur.fetchone()
        return SpecCard.from_row(dict(row)) if row else None

    def get_active(self, card_id: str) -> SpecCard | None:
        """读某候选卡当前 active 版（无 active 返回 None——L2 spec_ref 回填前置查询）。"""
        cur = self.read_conn().cursor()
        cur.execute(self._sql(_SQL_SELECT_ACTIVE), (card_id,))
        row = cur.fetchone()
        return SpecCard.from_row(dict(row)) if row else None

    def set_review(self, spec_id: str, review: dict[str, Any]) -> None:
        """抽验回填（§2.5 review 字段；auditor 专用）。"""
        conn = self.write_conn()
        try:
            conn.cursor().execute(
                self._sql(_SQL_SET_REVIEW),
                {"review": json.dumps(review, ensure_ascii=False), "spec_id": spec_id},
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def mark_status(self, spec_id: str, status: str, policy: CleaningPolicy) -> None:
        """状态翻转（active→superseded/rejected_wash；值域 fail-closed）。"""
        if status not in policy.vocab_of("spec_status"):
            raise SpecStoreError(f"status_out_of_vocab:{status}")
        conn = self.write_conn()
        try:
            conn.cursor().execute(self._sql(_SQL_SET_STATUS), {"status": status, "spec_id": spec_id})
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def count_cards(self) -> int:
        """已洗候选卡去重计数（auditor 冷启动阈值读数）。"""
        cur = self.read_conn().cursor()
        cur.execute(self._sql(_SQL_COUNT_CARDS))
        row = cur.fetchone()
        return int(row[0] if isinstance(row, (list, tuple)) else row["count"])
