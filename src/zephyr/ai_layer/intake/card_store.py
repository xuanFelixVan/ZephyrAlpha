# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] zephyr.ai_layer.intake.card_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.database_service (get_db_service)
# [CONSUMERS] zephyr.ai_layer.intake.gate (IntakeGate.admit); zephyr.ai_layer.intake.intake_events (handler 落点); zephyr.ai_layer.intake.kpi
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 全部读写经 DatabaseService（禁裸 duckdb/psycopg2 连接）；schema 名白名单校验后拼接（fail-closed）；
#              状态机只许 L0→L1→L2→E2→intake→e2_pending 顺序前进，任意非 intake 态可跳 rejected，
#              rejected 是终态（禁复活，复活=新卡重新进货）；elite 保优数=每格 3 条，rank>3 置 benched（墓碑制不删）；
#              simhash 以 BIT(64) 存取（写入 format(v,'064b')，读出 int(x,2)）；
#              生熟分离：本模块只服务 ai_intake.* 生食库，禁被产线代码 import
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.2/§2.4/§2.5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法流转/未知卡/schema 名不合规→RuntimeError|ValueError fail-closed（绝不静默放行）；
#                  DB 不可达→异常上抛（不吞不降级）；insert 撞 UNIQUE(content_sha256/card_id)→IntegrityError 上抛由 gate 转拒因
# [TESTS] tests/ai_layer/intake/（★ 在册缺口：本模块测试 test_card_store.py 未建，处方见 lanes/aibase_relay.md §6）
# [TTL] permanent
"""card_store — L2 原材料卡库服务（CRUD + 状态机 + MAP-Elites 行为格保优回写）。

设计真源：``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md`` §2.2（T2 卡主表）
§2.4（行为格 48 格 = 6 域 × 8 机制族，每格保优 3 条）§2.5（状态机合法性）。

分层裁定：状态机判据 ``check_stage_transition()`` 是**纯函数**（零 DB 依赖，可全枚举单测）；
DB 侧只负责读写与 rank 重算，判据不在 SQL 里。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.infrastructure.database_service import get_db_service

log = logging.getLogger(__name__)

__all__: Final = [
    "CardDraft",
    "CardStore",
    "IntakeCard",
    "STAGE_ORDER",
    "check_stage_transition",
    "hamming",
    "parse_simhash",
    "render_simhash",
]

SCHEMA_RE: Final = re.compile(r"^ai_intake(_test_[a-z0-9_]+)?$")
STAGE_ORDER: Final[tuple[str, ...]] = ("L0", "L1", "L2", "E2", "intake", "e2_pending")
STAGE_REJECTED: Final = "rejected"
STAGE_ALL: Final[tuple[str, ...]] = STAGE_ORDER + (STAGE_REJECTED,)
ELITE_KEEP_PER_CELL: Final = 3
SIMHASH_BITS: Final = 64

SQL_INSERT_CARD = """
INSERT INTO {s}.ai_intake_card (
    card_id, domain_id, title, novelty, mechanism,
    source_name, source_url, source_publisher, source_year, source_kind, license,
    content_sha256, simhash, mechanism_family, funnel_stage, stage_changed_at,
    labor_killed, four_gates, injection_probe, risk_flags, dedup_compared_vs,
    duplicate_of, raw_ref, spec_ref, handoff_ref, evidence_ref
) VALUES (
    %(card_id)s, %(domain_id)s, %(title)s, %(novelty)s, %(mechanism)s,
    %(source_name)s, %(source_url)s, %(source_publisher)s, %(source_year)s, %(source_kind)s, %(license)s,
    %(content_sha256)s, %(simhash)s::bit(64), %(mechanism_family)s, %(funnel_stage)s, now(),
    %(labor_killed)s, %(four_gates)s::jsonb, %(injection_probe)s,
    %(risk_flags)s::jsonb, %(dedup_compared_vs)s::jsonb,
    %(duplicate_of)s, %(raw_ref)s, %(spec_ref)s, %(handoff_ref)s, %(evidence_ref)s
)
"""

SQL_SELECT_CARD = """
SELECT card_id, domain_id, title, novelty, mechanism, source_name, source_url,
       source_publisher, source_year, source_kind, license, content_sha256, simhash,
       mechanism_family, elite_cell, elite_score, elite_rank, elite_status, funnel_stage,
       rejection_reason, labor_killed, four_gates, injection_probe, risk_flags,
       dedup_compared_vs, duplicate_of, raw_ref, spec_ref, handoff_ref, evidence_ref,
       created_at, updated_at
FROM {s}.ai_intake_card WHERE card_id = %s
"""

SQL_UPDATE_STAGE = """
UPDATE {s}.ai_intake_card
SET funnel_stage = %(stage)s, stage_changed_at = now(), updated_at = now(),
    rejection_reason = COALESCE(%(reason)s, rejection_reason),
    spec_ref = COALESCE(%(spec_ref)s, spec_ref),
    handoff_ref = COALESCE(%(handoff_ref)s, handoff_ref),
    evidence_ref = COALESCE(%(evidence_ref)s, evidence_ref)
WHERE card_id = %(card_id)s
"""

SQL_UPDATE_SCORE = """
UPDATE {s}.ai_intake_card
SET elite_score = %(score)s, updated_at = now(),
    evidence_ref = COALESCE(%(evidence_ref)s, evidence_ref)
WHERE card_id = %(card_id)s
"""

SQL_LIST_CELL = """
SELECT card_id, elite_score FROM {s}.ai_intake_card
WHERE elite_cell = %s AND elite_status = 'active' AND elite_score IS NOT NULL
ORDER BY elite_score DESC, created_at
"""

SQL_SET_RANK = """
UPDATE {s}.ai_intake_card
SET elite_rank = %(rank)s,
    elite_status = CASE WHEN %(rank)s > %(keep)s THEN 'benched' ELSE 'active' END,
    updated_at = now()
WHERE card_id = %(card_id)s
"""

SQL_COUNT_SOURCE_TODAY = """
SELECT count(*) FROM {s}.ai_intake_card
WHERE source_name = %s AND created_at >= date_trunc('day', now())
"""

SQL_LIST_BY_STAGE = """
SELECT card_id, domain_id, funnel_stage, elite_cell, source_name, updated_at
FROM {s}.ai_intake_card WHERE funnel_stage = %s ORDER BY created_at LIMIT %s
"""

SQL_CARD_EXISTS = "SELECT funnel_stage FROM {s}.ai_intake_card WHERE card_id = %s"


def render_simhash(value: int) -> str:
    """int → BIT(64) 字面量（PG bit 类型不接受整数字面量直插）。"""
    if not 0 <= value < (1 << SIMHASH_BITS):
        raise ValueError(f"simhash 越界（需 {SIMHASH_BITS} 位无符号）：{value}")
    return format(value, f"0{SIMHASH_BITS}b")


def parse_simhash(raw: Any) -> int:
    """BIT(64) 读出值 → int（psycopg2 返回 '0101…' 字符串）。"""
    if raw is None:
        raise ValueError("simhash 为 NULL（T2 定义 NOT NULL）")
    if isinstance(raw, int):
        return raw
    text = str(raw).strip()
    if not text or set(text) - {"0", "1"}:
        raise ValueError(f"simhash 位串非法：{text[:80]!r}")
    return int(text, 2)


def hamming(left: int, right: int) -> int:
    """两指纹汉明距离（近似查重判据 k≤3 的度量）。"""
    return bin(left ^ right).count("1")


def check_stage_transition(current: str, target: str) -> tuple[bool, str]:
    """状态机合法性纯判据（DESIGN §2.5 末行）。

    合法：①沿 STAGE_ORDER 前进一步；②任意非 intake 态跳 rejected；③同态幂等（no-op）。
    非法：跳跃前进、后退、rejected 复活、intake 之后跳 rejected（已被产线吸收）。
    """
    if current not in STAGE_ALL or target not in STAGE_ALL:
        return False, f"unknown_stage:{current}->{target}"
    if current == target:
        return True, "noop_same_stage"
    if target == STAGE_REJECTED:
        if current == "intake":
            return False, "intake_absorbed_cannot_reject"
        if current == STAGE_REJECTED:
            return False, "rejected_is_terminal_no_revive"
        return True, "reject_allowed"
    if current == STAGE_REJECTED:
        return False, "rejected_is_terminal_no_revive"
    if current not in STAGE_ORDER:
        return False, f"non_forward_from:{current}"
    idx_now, idx_next = STAGE_ORDER.index(current), STAGE_ORDER.index(target)
    if idx_next != idx_now + 1:
        return False, f"illegal_jump:{current}->{target}"
    return True, "forward_one_step"


@dataclass(frozen=True)
class CardDraft:
    """入库草稿（gate 过闸后交给 CardStore.insert 的唯一入参形态，防长参数列表）。"""

    card_id: str
    domain_id: str
    source_url: str
    content_sha256: str
    simhash: int
    mechanism_family: str
    labor_killed: str
    four_gates: dict[str, Any]
    injection_probe: str
    funnel_stage: str = "L0"
    title: str | None = None
    novelty: str | None = None
    mechanism: str | None = None
    source_name: str | None = None
    source_publisher: str | None = None
    source_year: int | None = None
    source_kind: str | None = None
    license: str | None = None
    risk_flags: list[str] = field(default_factory=list)
    dedup_compared_vs: list[str] = field(default_factory=list)
    duplicate_of: str | None = None
    raw_ref: str | None = None
    spec_ref: str | None = None
    handoff_ref: str | None = None
    evidence_ref: str | None = None


@dataclass(frozen=True)
class IntakeCard:
    """卡主表读出形态（T2 全列，只读快照）。"""

    card_id: str
    domain_id: str
    funnel_stage: str
    elite_cell: str
    mechanism_family: str
    simhash: int
    content_sha256: str
    elite_score: float | None = None
    elite_rank: int | None = None
    elite_status: str = "active"
    title: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    rejection_reason: str | None = None
    labor_killed: str | None = None
    four_gates: dict[str, Any] = field(default_factory=dict)
    dedup_compared_vs: list[str] = field(default_factory=list)
    duplicate_of: str | None = None
    spec_ref: str | None = None
    handoff_ref: str | None = None
    evidence_ref: str | None = None
    created_at: Any = None
    updated_at: Any = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "IntakeCard":
        """DB 行 → 只读快照（bit 串转 int，JSONB 转原生容器）。"""
        return cls(
            card_id=row["card_id"],
            domain_id=row["domain_id"],
            funnel_stage=row["funnel_stage"],
            elite_cell=row.get("elite_cell") or f"{row['domain_id']}|{row.get('mechanism_family')}",
            mechanism_family=row.get("mechanism_family") or "unclassified",
            simhash=parse_simhash(row.get("simhash")),
            content_sha256=str(row.get("content_sha256") or "").strip(),
            elite_score=row.get("elite_score"),
            elite_rank=row.get("elite_rank"),
            elite_status=row.get("elite_status") or "active",
            title=row.get("title"),
            source_name=row.get("source_name"),
            source_url=row.get("source_url"),
            rejection_reason=row.get("rejection_reason"),
            labor_killed=row.get("labor_killed"),
            four_gates=row.get("four_gates") or {},
            dedup_compared_vs=row.get("dedup_compared_vs") or [],
            duplicate_of=row.get("duplicate_of"),
            spec_ref=row.get("spec_ref"),
            handoff_ref=row.get("handoff_ref"),
            evidence_ref=row.get("evidence_ref"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )


class CardStore:
    """L2 卡库服务：CRUD + 状态机流转 + 行为格保优回写（全部经 DatabaseService）。"""

    def __init__(self, schema: str = "ai_intake", service: Any | None = None) -> None:
        if not SCHEMA_RE.match(schema or ""):
            raise ValueError(f"schema 名不合规：{schema!r}（只许 ai_intake / ai_intake_test_*）")
        self.schema: Final = schema
        self._svc = service or get_db_service()
        self._write_conn: Any | None = None

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    def _conn(self, *, reader: bool = False) -> Any:
        """取连接（内部统一入口）：reader=True 走只读，否则走写角色。"""
        return self.read_conn() if reader else self.write_conn()

    def read_conn(self) -> Any:
        """只读连接：经 DatabaseService（读路径唯一真源，read_only=True）。"""
        return self._svc.get_depgraph_conn(read_only=True)

    def write_conn(self) -> Any:
        """写连接（depgraph_writer 角色，进程内复用一条）。

        裁定申请 req_ailayerB_03 现场留痕：``DatabaseService.get_depgraph_conn(read_only=False)``
        实测仍返回 **depgraph_reader**（database_service.py:154 调
        ``get_depgraph_pg_connection(autocommit=True)`` 未透传 read_only，底层默认 True），
        因此无法承载 INSERT/UPDATE（L2 DESIGN §2.1"全部读写经 DatabaseService"在写侧当前不可达）。
        本模块按 ig_* 图谱写入器同款处置：直连 depgraph_schema 的写角色入口，
        并已登记 DEPGRAPH-WRITE-PATH 白名单（治本三步 a 步）；DatabaseService 侧修好后回切读同一入口。
        """
        if self._write_conn is None or self._write_conn.closed:
            self._write_conn = get_depgraph_pg_connection(read_only=False, autocommit=True)
        return self._write_conn

    def close(self) -> None:
        """释放本实例持有的写连接（读连接归 DatabaseService 生命周期管）。"""
        if self._write_conn is not None and not self._write_conn.closed:
            self._write_conn.close()
        self._write_conn = None

    def insert(self, draft: CardDraft) -> str:
        """写入新卡（UNIQUE 冲突由调用方按拒因处置，本层不吞异常）。"""
        import json

        params = {
            "card_id": draft.card_id,
            "domain_id": draft.domain_id,
            "title": draft.title,
            "novelty": draft.novelty,
            "mechanism": draft.mechanism,
            "source_name": draft.source_name,
            "source_url": draft.source_url,
            "source_publisher": draft.source_publisher,
            "source_year": draft.source_year,
            "source_kind": draft.source_kind,
            "license": draft.license,
            "content_sha256": draft.content_sha256,
            "simhash": render_simhash(draft.simhash),
            "mechanism_family": draft.mechanism_family,
            "funnel_stage": draft.funnel_stage,
            "labor_killed": draft.labor_killed,
            "four_gates": json.dumps(draft.four_gates, ensure_ascii=False),
            "injection_probe": draft.injection_probe,
            "risk_flags": json.dumps(list(draft.risk_flags), ensure_ascii=False),
            "dedup_compared_vs": json.dumps(list(draft.dedup_compared_vs), ensure_ascii=False),
            "duplicate_of": draft.duplicate_of,
            "raw_ref": draft.raw_ref,
            "spec_ref": draft.spec_ref,
            "handoff_ref": draft.handoff_ref,
            "evidence_ref": draft.evidence_ref,
        }
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(self._sql(SQL_INSERT_CARD), params)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return draft.card_id

    def get(self, card_id: str) -> IntakeCard | None:
        """按主键读卡（不存在返回 None）。"""
        conn = self._conn(reader=True)
        cur = conn.cursor()
        cur.execute(self._sql(SQL_SELECT_CARD), (card_id,))
        row = cur.fetchone()
        return IntakeCard.from_row(dict(row)) if row else None

    def stage_of(self, card_id: str) -> str | None:
        """轻量读当前状态（状态机流转前置检查用）。"""
        conn = self._conn(reader=True)
        cur = conn.cursor()
        cur.execute(self._sql(SQL_CARD_EXISTS), (card_id,))
        row = cur.fetchone()
        return (row[0] if isinstance(row, (list, tuple)) else row["funnel_stage"]) if row else None

    def transition(self, card_id: str, target: str, **refs: Any) -> str:
        """状态机流转（判据=check_stage_transition，非法即 RuntimeError fail-closed）。

        :param refs: 可选 rejection_reason / spec_ref / handoff_ref / evidence_ref 同批回写
        """
        current = self.stage_of(card_id)
        if current is None:
            raise RuntimeError(f"card_not_found:{card_id}")
        ok, why = check_stage_transition(current, target)
        if not ok:
            raise RuntimeError(f"illegal_transition:{card_id}:{why}")
        if why == "noop_same_stage":
            return why
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                self._sql(SQL_UPDATE_STAGE),
                {
                    "stage": target,
                    "card_id": card_id,
                    "reason": refs.get("rejection_reason"),
                    "spec_ref": refs.get("spec_ref"),
                    "handoff_ref": refs.get("handoff_ref"),
                    "evidence_ref": refs.get("evidence_ref"),
                },
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return why

    def record_score(self, card_id: str, score: float, evidence_ref: str | None = None) -> dict[str, Any]:
        """L4 出分回写 + 同格重排名（保优 3 条，rank>3 置 benched；墓碑制不删）。"""
        card = self.get(card_id)
        if card is None:
            raise RuntimeError(f"card_not_found:{card_id}")
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                self._sql(SQL_UPDATE_SCORE),
                {"score": float(score), "evidence_ref": evidence_ref, "card_id": card_id},
            )
            cur.execute(self._sql(SQL_LIST_CELL), (card.elite_cell,))
            rows = cur.fetchall()
            ranked = self._rank_pairs(rows)
            for cid, rank in ranked:
                cur.execute(
                    self._sql(SQL_SET_RANK),
                    {"rank": rank, "keep": ELITE_KEEP_PER_CELL, "card_id": cid},
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return {"card_id": card_id, "cell": card.elite_cell, "ranked": ranked}

    @staticmethod
    def _rank_pairs(rows: list[Any]) -> list[tuple[str, int]]:
        """把 (card_id, score) 行序列压成 (card_id, rank) 名次表（rank 从 1 起）。"""
        out: list[tuple[str, int]] = []
        for i, row in enumerate(rows, start=1):
            cid = row["card_id"] if isinstance(row, dict) else row[0]
            out.append((cid, i))
        return out

    def count_today_by_source(self, source_name: str) -> int:
        """当日该源已入库卡数（配额闸读数，DESIGN §2.5 配额闸）。"""
        conn = self._conn(reader=True)
        cur = conn.cursor()
        cur.execute(self._sql(SQL_COUNT_SOURCE_TODAY), (source_name,))
        row = cur.fetchone()
        return int(row[0] if isinstance(row, (list, tuple)) else row["count"])

    def list_by_stage(self, stage: str, limit: int = 200) -> list[dict[str, Any]]:
        """按状态列卡（事件层派洗/派考消费用）。"""
        if stage not in STAGE_ALL:
            raise ValueError(f"unknown_stage:{stage}")
        conn = self._conn(reader=True)
        cur = conn.cursor()
        cur.execute(self._sql(SQL_LIST_BY_STAGE), (stage, int(limit)))
        return [dict(r) for r in cur.fetchall()]
