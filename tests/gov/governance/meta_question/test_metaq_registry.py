# [A_test] module_id: MOD-TEST-meta_question_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §7 写入 API 契约
# [MODULE] tests.governance.meta_question.test_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question (MetaQuestionRegistry, export_snapshot); scripts/governance/apply_meta_question_ddl.py (importlib 零 DB 用例)
# [CONSUMERS] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红；禁写生产路径：JSONL/快照输出全走 tmp_path fixture，mock 库=内存 SQLite
# [TESTS] self
# [TTL] task_bound
"""meta_question_registry 写入 API 测试（SQLite mock 连接注入，零 PG 依赖）。

覆盖：register 正/反（每条校验规则至少 1 反例）/ transition 合法边+非法边 /
乐观锁冲突 / claim 互斥与租约过期 / record_exam_result 状态联动 / 审计 JSONL 内容 /
snapshot 机生导出 / DDL 部署器 schema 白名单与语句渲染（零 DB）。
PG 生产库零接触（本套件不含任何真实连接）。
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path
from typing import Any, Self

import pytest
import yaml

from zephyr.governance.meta_question import (
    AUDIT_WHAT_VOCAB,
    LEGAL_TRANSITIONS,
    MetaQuestionRegistry,
    QuestionValidationError,
    VersionConflictError,
    export_snapshot,
)
from zephyr.governance.meta_question.snapshot import export_snapshot_from_json
from zephyr.shared.io.paths import REPO_ROOT

# SQL 字面量集中化（§5.160.2 NO-BARE-SQL）：同文 SQL 逐处独立常量——收口对拍尺按
# 多重集计数，共用常量会使字面量条数缩减判 RED，故不合并，仅搬移位置不改一字。
SQL_SELECT_STATUS_VERSION_TITLE_BY_QID = "SELECT status, version, title FROM main.meta_question WHERE q_id=%s"
SQL_SELECT_STATUS_VERSION_BY_QID = "SELECT status, version FROM main.meta_question WHERE q_id=%s"
SQL_SELECT_STATUS_VERSION_AFTER_CONFLICT = "SELECT status, version FROM main.meta_question WHERE q_id=%s"
SQL_SELECT_STATUS_LAST_EXAM_BY_QID = "SELECT status, last_exam FROM main.meta_question WHERE q_id=%s"
SQL_SELECT_STATUS_BY_QID = "SELECT status FROM main.meta_question WHERE q_id=%s"
SQL_SELECT_CLAIM_FIELDS_BY_QID = "SELECT claimed_by, claimed_until FROM main.meta_question WHERE q_id=%s"
SQL_SELECT_PROVENANCE_PQ0001 = "SELECT provenance FROM main.meta_question WHERE q_id='PQ-0001'"
SQL_SELECT_QID_STATUS_ORDERED = "SELECT q_id, status FROM main.meta_question ORDER BY q_id"
SQL_SELECT_QID_STATUS_EXAM_LINKED = "SELECT q_id, status FROM main.meta_question ORDER BY q_id"
SQL_SELECT_EXAM_RESULT_FIELDS_BY_QID = (
    "SELECT outcome, recorded_by, conclusion FROM main.meta_question_exam_result WHERE q_id=%s"
)
SQL_SELECT_AUDIT_ACTOR_WHAT_BY_QID = "SELECT actor, what FROM main.meta_question_audit WHERE q_id=%s ORDER BY id"
SQL_SELECT_AUDIT_UPDATE_WHAT_BY_QID = (
    "SELECT what FROM main.meta_question_audit WHERE q_id=%s AND what='update' ORDER BY id"
)
SQL_SELECT_LAST_AUDIT_WHAT_BLIND_PROMOTE = (
    "SELECT what FROM main.meta_question_audit WHERE q_id=%s ORDER BY id DESC LIMIT 1"
)
SQL_SELECT_LAST_AUDIT_WHAT_EXAM_WRITEBACK = (
    "SELECT what FROM main.meta_question_audit WHERE q_id=%s ORDER BY id DESC LIMIT 1"
)
SQL_SET_STATUS_BLINDED_BY_QID = "UPDATE main.meta_question SET status='blinded' WHERE q_id=%s"
SQL_SET_CLAIMED_UNTIL_EPOCH_BY_QID = (
    "UPDATE main.meta_question SET claimed_until='2000-01-01 00:00:00+00:00' WHERE q_id=%s"
)
SQL_COUNT_META_QUESTION = "SELECT COUNT(*) FROM main.meta_question"
SQL_COUNT_META_QUESTION_AUDIT = "SELECT COUNT(*) FROM main.meta_question_audit"
SQL_COUNT_EXAM_RESULT = "SELECT COUNT(*) FROM main.meta_question_exam_result"

# ---------------------------------------------------------------------------
# SQLite mock 连接（%s→? 翻译；close=no-op 保活 :memory: 库）
# ---------------------------------------------------------------------------

SQLITE_DDL: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS main.meta_question (
        q_id TEXT PRIMARY KEY CHECK (q_id GLOB 'PQ-[0-9][0-9][0-9][0-9]'),
        title TEXT NOT NULL,
        layer TEXT NOT NULL CHECK (layer IN ('L0','L1','L2','L3','L4','L5','L6')),
        line_ref TEXT,
        graph_ref TEXT,
        data_sources TEXT NOT NULL DEFAULT '[]',
        exam_plan TEXT NOT NULL DEFAULT '{}',
        consumers TEXT NOT NULL DEFAULT '[]',
        frequency TEXT NOT NULL,
        pit_proof TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
            'draft','registered','mining','in_exam','answered','reexam',
            'suspended','merged','retired','blinded')),
        parent_id TEXT,
        merged_into TEXT,
        provenance TEXT NOT NULL DEFAULT '{}',
        net_zero_note TEXT NOT NULL DEFAULT '',
        chain_refs TEXT NOT NULL DEFAULT '[]',
        evidence_refs TEXT NOT NULL DEFAULT '[]',
        last_exam TIMESTAMPTZ,
        priority_score NUMERIC,
        priority_updated_at TIMESTAMPTZ,
        claimed_by TEXT,
        claimed_until TIMESTAMPTZ,
        version INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS main.meta_question_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        q_id TEXT NOT NULL,
        actor TEXT NOT NULL,
        what TEXT NOT NULL,
        "before" TEXT,
        "after" TEXT,
        evidence TEXT NOT NULL DEFAULT '',
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS main.meta_question_exam_result (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        q_id TEXT NOT NULL REFERENCES meta_question(q_id),
        exam_ref TEXT,
        conclusion TEXT,
        confidence TEXT,
        data_window TEXT,
        pit_assertion TEXT,
        outcome TEXT NOT NULL CHECK (outcome IN ('answered','reexam','suspended')),
        recorded_by TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
)


class _SQLiteCursorProxy:
    """%s→? 占位符翻译（psycopg2 口径 SQL 与 sqlite3 方言之间的最小垫片）。"""

    def __init__(self, raw: sqlite3.Cursor) -> None:
        self._raw = raw

    def execute(self, sql: str, params: Any = ()) -> Self:
        if params is not None and not isinstance(params, (tuple, list)):
            params = (params,)
        self._raw.execute(sql.replace("%s", "?"), tuple(params))
        return self

    def fetchone(self) -> Any:
        return self._raw.fetchone()

    def fetchall(self) -> list[Any]:
        return self._raw.fetchall()

    @property
    def rowcount(self) -> int:
        return self._raw.rowcount

    @property
    def description(self) -> Any:
        return self._raw.description


class _SQLiteConnProxy:
    """registry 写入 API 的 mock 连接：close 语义=no-op（:memory: 库随 fixture 保活）。"""

    def __init__(self, raw: sqlite3.Connection) -> None:
        self._raw = raw

    def cursor(self) -> _SQLiteCursorProxy:
        return _SQLiteCursorProxy(self._raw.cursor())

    def commit(self) -> None:
        self._raw.commit()

    def rollback(self) -> None:
        self._raw.rollback()

    def close(self) -> None:  # noqa: D401 ——注入连接不真关，由 fixture 生命周期管理
        pass


@pytest.fixture()
def mock_env(tmp_path: Path) -> dict[str, Any]:
    """内存 SQLite 库 + 注入式 registry + JSONL 审计路径（全在 tmp_path，零生产路径）。"""
    raw = sqlite3.connect(":memory:")
    for ddl in SQLITE_DDL:
        raw.execute(ddl)
    raw.commit()
    proxy = _SQLiteConnProxy(raw)
    jsonl_path = tmp_path / "meta_question_audit.jsonl"
    registry = MetaQuestionRegistry(
        schema="main",
        get_conn=lambda *, read_only=True: proxy,
        audit_jsonl_path=jsonl_path,
    )
    env = {
        "registry": registry,
        "raw": raw,
        "proxy": proxy,
        "jsonl_path": jsonl_path,
    }
    yield env
    raw.close()


def _reg(env: dict[str, Any]) -> MetaQuestionRegistry:
    return env["registry"]


def _raw_exec(env: dict[str, Any], sql: str, params: Any = ()) -> sqlite3.Cursor:
    """测试侧直连执行（绕过 registry，用于装配/篡改场景）。"""
    cur = env["raw"].execute(sql.replace("%s", "?"), tuple(params or ()))
    env["raw"].commit()
    return cur


def _valid_question(**overrides: Any) -> dict[str, Any]:
    """五要素齐备的合法候选问题（登记族底稿）。"""
    q: dict[str, Any] = {
        "title": "大盘情绪因子在 L3 传导是否显著",
        "layer": "L3",
        "line_ref": None,
        "graph_ref": None,
        "data_sources": ["src.quote.daily"],
        "exam_plan": {"criterion": "rank_ic", "threshold": 0.02},
        "consumers": ["D1_decision"],
        "frequency": "daily",
        "pit_proof": "全部数据源以 as-of 公告日对齐，决策时点仅可见 T-1 数据",
        "provenance": {"origin": "W6-mining-batch-1"},
        "net_zero_note": "替代对话散落提问现状（净零声明 NZ-TEST-001）",
    }
    q.update(overrides)
    return q


def _to_registered(env: dict[str, Any], actor: str = "sess-A|AI", **overrides: Any) -> str:
    q_id = _reg(env).register(_valid_question(**overrides), actor=actor)
    return q_id


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# register（10§7.1 校验顺序 / 10§7.2 错误码）
# ---------------------------------------------------------------------------


class TestRegister:
    def test_register_assigns_serial_qid_and_audits(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id_1 = reg.register(_valid_question(), actor="sess-A|AI")
        q_id_2 = reg.register(_valid_question(title="另一问：源线 U1 的重复率如何"), actor="sess-A|AI")
        assert q_id_1 == "PQ-0001"
        assert q_id_2 == "PQ-0002"  # 连号 max+1，墓碑不复用
        cur = _raw_exec(mock_env, SQL_SELECT_STATUS_VERSION_TITLE_BY_QID, (q_id_1,))
        row = cur.fetchone()
        assert row == ("registered", 1, _valid_question()["title"])
        cur = _raw_exec(mock_env, SQL_SELECT_AUDIT_ACTOR_WHAT_BY_QID, (q_id_1,))
        rows = cur.fetchall()
        assert rows[0] == ("sess-A|AI", "register")
        assert any(r[1] == "degraded_check" for r in rows)  # 10§3 降级痕必留

    def test_register_missing_required_field(self, mock_env) -> None:
        for missing in ("title", "provenance", "pit_proof", "data_sources"):
            q = _valid_question()
            q.pop(missing)
            with pytest.raises(QuestionValidationError) as ei:
                _reg(mock_env).register(q, actor="sess-A|AI")
            assert ei.value.subcode == f"field_missing:{missing}"

    def test_register_net_zero_note_missing(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(net_zero_note=""), actor="sess-A|AI")
        assert ei.value.subcode == "net_zero_note_missing"
        with pytest.raises(QuestionValidationError) as ei:
            q = _valid_question()
            q.pop("net_zero_note")
            _reg(mock_env).register(q, actor="sess-A|AI")
        assert ei.value.subcode == "net_zero_note_missing"

    def test_register_layer_invalid(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(layer="L9"), actor="sess-A|AI")
        assert ei.value.subcode == "layer_invalid"

    def test_register_data_sources_empty_or_bad_shape(self, mock_env) -> None:
        for bad in ([], "not-a-list", ["", "  "]):
            with pytest.raises(QuestionValidationError) as ei:
                _reg(mock_env).register(_valid_question(data_sources=bad), actor="sess-A|AI")
            assert ei.value.subcode == "data_sources_empty"

    def test_register_exam_plan_no_threshold(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(exam_plan={"criterion": "rank_ic"}), actor="sess-A|AI")
        assert ei.value.subcode == "exam_plan_no_threshold"
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(exam_plan="not-a-dict"), actor="sess-A|AI")
        assert ei.value.subcode == "exam_plan_no_threshold"

    def test_register_threshold_zero_is_legal(self, mock_env) -> None:
        """阈值=0 是合法数值（禁 truthy 误判）。"""
        q_id = _reg(mock_env).register(
            _valid_question(exam_plan={"criterion": "win_rate_diff", "threshold": 0}),
            actor="sess-A|AI",
        )
        assert q_id == "PQ-0001"

    def test_register_consumers_empty(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(consumers=[]), actor="sess-A|AI")
        assert ei.value.subcode == "consumer_unresolvable"

    def test_register_frequency_not_in_enum(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(frequency="hourly"), actor="sess-A|AI")
        assert ei.value.subcode == "frequency_not_in_enum"

    def test_register_event_driven_requires_event_source(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(frequency="event_driven"), actor="sess-A|AI")
        assert ei.value.subcode == "event_source_ref_missing"
        q_id = _reg(mock_env).register(
            _valid_question(
                frequency="event_driven",
                exam_plan={
                    "criterion": "hit",
                    "threshold": 1,
                    "event_source_ref": "evt.board_action",
                },
            ),
            actor="sess-A|AI",
        )
        assert q_id == "PQ-0001"

    def test_register_pit_proof_missing(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).register(_valid_question(pit_proof="  "), actor="sess-A|AI")
        assert ei.value.subcode == "pit_proof_missing"

    def test_register_duplicate_high_similarity(self, mock_env) -> None:
        reg = _reg(mock_env)
        first = reg.register(_valid_question(), actor="sess-A|AI")
        # 归一化等价（大小写/标点/空白差异）+ 同 layer + 同 line_ref → 高相似拒
        with pytest.raises(QuestionValidationError) as ei:
            reg.register(_valid_question(title="大盘情绪因子在L3传导是否显著。"), actor="sess-B|AI")
        assert ei.value.subcode == "dup_high_similarity"
        assert ei.value.details["duplicate_of"] == first
        # 不同 layer → 非重复（查重限同层比对）
        other = reg.register(_valid_question(layer="L4"), actor="sess-B|AI")
        assert other == "PQ-0002"

    def test_register_validation_failure_is_side_effect_free(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError):
            _reg(mock_env).register(_valid_question(layer="L9"), actor="sess-A|AI")
        assert _raw_exec(mock_env, SQL_COUNT_META_QUESTION).fetchone()[0] == 0
        assert _raw_exec(mock_env, SQL_COUNT_META_QUESTION_AUDIT).fetchone()[0] == 0

    def test_register_stamps_provenance(self, mock_env) -> None:
        _reg(mock_env).register(_valid_question(), actor="sess-A|AI")
        cur = _raw_exec(mock_env, SQL_SELECT_PROVENANCE_PQ0001)
        prov = json.loads(cur.fetchone()[0])
        assert prov["registered_by"] == "sess-A|AI"
        assert "registered_at" in prov  # OSF 注册时戳对标（10§2.1）


# ---------------------------------------------------------------------------
# transition（13§1.5 合法边 / 20§3.2 乐观锁）
# ---------------------------------------------------------------------------


class TestTransition:
    def test_transition_happy_path_and_audit(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = _to_registered(mock_env)
        out = reg.transition(q_id, "mining", actor="sess-A|AI", evidence="开工令 E-1")
        assert out == {"q_id": q_id, "from_status": "registered", "to_status": "mining"}
        reg.transition(q_id, "in_exam", actor="sess-A|AI")
        cur = _raw_exec(mock_env, SQL_SELECT_STATUS_VERSION_BY_QID, (q_id,))
        assert cur.fetchone() == ("in_exam", 3)  # registered=1，两次流转各 +1
        cur = _raw_exec(mock_env, SQL_SELECT_AUDIT_UPDATE_WHAT_BY_QID, (q_id,))
        assert len(cur.fetchall()) == 2

    def test_transition_rejects_illegal_edge(self, mock_env) -> None:
        q_id = _to_registered(mock_env)
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).transition(q_id, "answered", actor="sess-A|AI")
        assert ei.value.subcode == "illegal_transition"
        assert ei.value.details == {"from_status": "registered", "to_status": "answered"}

    def test_transition_covers_required_edges(self, mock_env) -> None:
        """任务钉扎边：挂起→registered 唤醒、in_exam/answered→挂起、任意→merged/retired。"""
        reg = _reg(mock_env)
        # in_exam→suspended
        q1 = _to_registered(mock_env, title="挂起边验证问一")
        reg.transition(q1, "mining", actor="sess-A|AI")
        reg.transition(q1, "in_exam", actor="sess-A|AI")
        reg.transition(q1, "suspended", actor="sess-A|AI", evidence="数据不可得")
        # suspended→registered 唤醒边
        reg.transition(q1, "registered", actor="sess-A|AI", evidence="唤醒阈达成")
        # answered→suspended
        q2 = _to_registered(mock_env, title="挂起边验证问二")
        reg.transition(q2, "mining", actor="sess-A|AI")
        reg.transition(q2, "in_exam", actor="sess-A|AI")
        _reg(mock_env).record_exam_result(q2, {"outcome": "answered", "exam_ref": "exam-1"}, actor="sess-A|AI")
        reg.transition(q2, "suspended", actor="sess-A|AI", evidence="复考连续失败 2 次")
        # 任意→merged / 任意→retired 通配边
        reg.transition(q2, "merged", actor="sess-A|AI", evidence="并入 PQ-0001")
        q3 = _to_registered(mock_env, title="退役边验证问三")
        reg.transition(q3, "retired", actor="Owner", evidence="零触发零消费退役批")
        cur = _raw_exec(mock_env, SQL_SELECT_QID_STATUS_ORDERED)
        assert dict(cur.fetchall()) == {q1: "registered", q2: "merged", q3: "retired"}

    def test_terminal_states_have_no_outgoing_edges(self, mock_env) -> None:
        q_id = _to_registered(mock_env)
        _reg(mock_env).transition(q_id, "merged", actor="sess-A|AI")
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).transition(q_id, "registered", actor="sess-A|AI")
        assert ei.value.subcode == "illegal_transition"
        assert not LEGAL_TRANSITIONS["merged"] and not LEGAL_TRANSITIONS["retired"]

    def test_transition_version_conflict(self, mock_env, monkeypatch) -> None:
        """乐观锁：读到旧版本后行被他写推进 → WHERE version=:expected 零行命中=冲突。"""
        reg = _reg(mock_env)
        q_id = _to_registered(mock_env)
        reg.transition(q_id, "mining", actor="sess-A|AI")  # version → 2
        real_load = reg._load_row

        def stale_loader(cur: Any, qid: str) -> dict[str, Any]:
            row = real_load(cur, qid)
            row["version"] = int(row["version"]) - 1  # 模拟读到推进前的旧快照
            return row

        monkeypatch.setattr(reg, "_load_row", stale_loader)
        with pytest.raises(VersionConflictError) as ei:
            reg.transition(q_id, "in_exam", actor="sess-A|AI")
        assert ei.value.q_id == q_id and ei.value.expected_version == 1
        # 冲突后主表不被部分改写（fail-closed 回滚）
        cur = _raw_exec(mock_env, SQL_SELECT_STATUS_VERSION_AFTER_CONFLICT, (q_id,))
        assert cur.fetchone() == ("mining", 2)

    def test_transition_to_unknown_status(self, mock_env) -> None:
        q_id = _to_registered(mock_env)
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).transition(q_id, "on_fire", actor="sess-A|AI")
        assert ei.value.subcode == "status_invalid"

    def test_transition_qid_not_found(self, mock_env) -> None:
        with pytest.raises(QuestionValidationError) as ei:
            _reg(mock_env).transition("PQ-9999", "mining", actor="sess-A|AI")
        assert ei.value.subcode == "qid_not_found"

    def test_transition_requires_active_claim(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = _to_registered(mock_env)
        reg.claim(q_id, "sess-A|AI")
        with pytest.raises(QuestionValidationError) as ei:
            reg.transition(q_id, "mining", actor="sess-B|AI")
        assert ei.value.subcode == "claim_mismatch"
        reg.transition(q_id, "mining", actor="sess-A|AI")  # 认领人本人可流转
        reg.transition(q_id, "in_exam", actor="Max")  # Max 可越过（10§7.4①）

    def test_blinded_promote_edge(self, mock_env) -> None:
        """盲册晋级边：blinded→registered（blind_promote，10§6.3 晋级=状态迁移留痕）。"""
        q_id = _to_registered(mock_env, title="盲册养问")
        _raw_exec(mock_env, SQL_SET_STATUS_BLINDED_BY_QID, (q_id,))
        _reg(mock_env).transition(q_id, "registered", actor="Max", evidence="缺口补齐晋级")
        cur = _raw_exec(mock_env, SQL_SELECT_LAST_AUDIT_WHAT_BLIND_PROMOTE, (q_id,))
        assert cur.fetchone()[0] == "blind_promote"


# ---------------------------------------------------------------------------
# claim / release_claim（12§2.1 认领协议）
# ---------------------------------------------------------------------------


class TestClaim:
    def test_claim_mutex_then_release(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = _to_registered(mock_env)
        receipt = reg.claim(q_id, "sess-A|AI", lease_hours=24)
        assert receipt["claimed_by"] == "sess-A|AI"
        with pytest.raises(QuestionValidationError) as ei:
            reg.claim(q_id, "sess-B|AI")
        assert ei.value.subcode == "claim_conflict"
        reg.release_claim(q_id, "sess-A|AI")
        receipt_b = reg.claim(q_id, "sess-B|AI")
        assert receipt_b["claimed_by"] == "sess-B|AI"

    def test_claim_expired_lease_lazily_reclaimed(self, mock_env) -> None:
        """租约过期=惰性回收（12§2.1）：他人可径直认领，无需先释放。"""
        reg = _reg(mock_env)
        q_id = _to_registered(mock_env)
        reg.claim(q_id, "sess-A|AI", lease_hours=1)
        _raw_exec(mock_env, SQL_SET_CLAIMED_UNTIL_EPOCH_BY_QID, (q_id,))
        receipt = reg.claim(q_id, "sess-B|AI")
        assert receipt["claimed_by"] == "sess-B|AI"

    def test_release_claim_auth(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = _to_registered(mock_env)
        with pytest.raises(QuestionValidationError) as ei:
            reg.release_claim(q_id, "sess-B|AI")
        assert ei.value.subcode == "claim_not_held"
        reg.claim(q_id, "sess-A|AI")
        with pytest.raises(QuestionValidationError) as ei:
            reg.release_claim(q_id, "sess-B|AI")
        assert ei.value.subcode == "release_not_claimant"
        reg.release_claim(q_id, "Max")  # Max 可越过
        cur = _raw_exec(mock_env, SQL_SELECT_CLAIM_FIELDS_BY_QID, (q_id,))
        assert cur.fetchone() == (None, None)


# ---------------------------------------------------------------------------
# record_exam_result（13§1 回写契约；R3 独立表）
# ---------------------------------------------------------------------------


class TestRecordExamResult:
    def _drive_to_in_exam(self, env: dict[str, Any], title: str) -> str:
        reg = _reg(env)
        q_id = reg.register(_valid_question(title=title), actor="sess-A|AI")
        reg.transition(q_id, "mining", actor="sess-A|AI")
        reg.transition(q_id, "in_exam", actor="sess-A|AI")
        return q_id

    def test_exam_answered_links_status_and_rows(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = self._drive_to_in_exam(mock_env, "开考问一")
        out = reg.record_exam_result(
            q_id,
            {
                "exam_ref": "exam_run_2026_09_22_01",
                "conclusion": {"value": 0.031, "dir": "支持"},
                "confidence": {"level": 95, "ci_lo": 0.01, "ci_hi": 0.05},
                "data_window": {"start": "2025-01-01", "end": "2026-09-19"},
                "pit_assertion": "各源 as-of 均先于决策时点",
                "outcome": "answered",
            },
            actor="sess-A|AI",
        )
        assert out["status"] == "answered"
        cur = _raw_exec(mock_env, SQL_SELECT_STATUS_LAST_EXAM_BY_QID, (q_id,))
        status, last_exam = cur.fetchone()
        assert status == "answered" and last_exam
        cur = _raw_exec(mock_env, SQL_SELECT_EXAM_RESULT_FIELDS_BY_QID, (q_id,))
        outcome, recorded_by, conclusion = cur.fetchone()
        assert (outcome, recorded_by) == ("answered", "sess-A|AI")
        assert json.loads(conclusion)["value"] == 0.031
        cur = _raw_exec(mock_env, SQL_SELECT_LAST_AUDIT_WHAT_EXAM_WRITEBACK, (q_id,))
        assert cur.fetchone()[0] == "exam_writeback"

    def test_exam_outcome_reexam_and_suspend(self, mock_env) -> None:
        reg = _reg(mock_env)
        q1 = self._drive_to_in_exam(mock_env, "复考联动问")
        reg.record_exam_result(q1, {"outcome": "reexam", "exam_ref": "exam_r1"}, actor="sess-A|AI")
        q2 = self._drive_to_in_exam(mock_env, "挂起联动问")
        reg.record_exam_result(q2, {"outcome": "suspended", "exam_ref": "exam_s1"}, actor="sess-A|AI")
        cur = _raw_exec(mock_env, SQL_SELECT_QID_STATUS_EXAM_LINKED)
        assert dict(cur.fetchall()) == {q1: "reexam", q2: "suspended"}
        # reexam→answered（13§2.2 三取二胜出侧转 answered）
        reg.record_exam_result(q1, {"outcome": "answered", "exam_ref": "exam_r2"}, actor="sess-A|AI")
        cur = _raw_exec(mock_env, SQL_SELECT_STATUS_BY_QID, (q1,))
        assert cur.fetchone()[0] == "answered"

    def test_exam_invalid_outcome_and_state(self, mock_env) -> None:
        reg = _reg(mock_env)
        with pytest.raises(QuestionValidationError) as ei:
            reg.record_exam_result("PQ-0001", {"outcome": "exploded"}, actor="sess-A|AI")
        assert ei.value.subcode == "status_invalid"
        q_id = _to_registered(mock_env)
        with pytest.raises(QuestionValidationError) as ei:
            reg.record_exam_result(q_id, {"outcome": "answered"}, actor="sess-A|AI")
        assert ei.value.subcode == "status_invalid"  # registered 态不可直接出 answered
        assert _raw_exec(mock_env, SQL_COUNT_EXAM_RESULT).fetchone()[0] == 0

    def test_exam_writeback_requires_claim(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = self._drive_to_in_exam(mock_env, "回写鉴权问")
        reg.claim(q_id, "sess-A|AI")
        with pytest.raises(QuestionValidationError) as ei:
            reg.record_exam_result(q_id, {"outcome": "answered"}, actor="sess-B|AI")
        assert ei.value.subcode == "claim_mismatch"  # 13§1 回写鉴权句（R-08）


# ---------------------------------------------------------------------------
# 审计 JSONL 双轨（20§2.2）
# ---------------------------------------------------------------------------


class TestAuditJsonl:
    def test_jsonl_content_and_vocab(self, mock_env) -> None:
        reg = _reg(mock_env)
        q_id = reg.register(_valid_question(), actor="sess-A|AI")
        reg.transition(q_id, "mining", actor="sess-A|AI", evidence="开工令 E-1")
        events = _read_jsonl(mock_env["jsonl_path"])
        whats = [e["what"] for e in events]
        assert whats[0] == "register"
        assert "update" in whats and "degraded_check" in whats
        for event in events:
            assert set(event) == {"who", "when", "what", "object", "diff", "evidence"}
            assert event["what"] in AUDIT_WHAT_VOCAB  # SSOT 词表（20§2.1）
            assert event["object"] == q_id
            assert event["who"] == "sess-A|AI"
        register_event = events[0]
        assert register_event["diff"] == [{"field": "status", "old": None, "new": "registered"}]
        transition_event = next(e for e in events if e["what"] == "update")
        assert transition_event["diff"] == [{"field": "status", "old": "registered", "new": "mining"}]
        assert transition_event["evidence"] == "开工令 E-1"

    def test_jsonl_untouched_by_failed_operation(self, mock_env) -> None:
        """失败操作零审计痕（追加账不记未发生之事；20§2 落地即账=先账后实同事务）。"""
        reg = _reg(mock_env)
        q_id = reg.register(_valid_question(), actor="sess-A|AI")
        before = _read_jsonl(mock_env["jsonl_path"])
        assert before  # register+degraded_check 已落
        with pytest.raises(QuestionValidationError):
            reg.transition(q_id, "in_exam", actor="sess-A|AI")  # registered→in_exam 非法边
        assert _read_jsonl(mock_env["jsonl_path"]) == before  # 失败零追加


# ---------------------------------------------------------------------------
# snapshot 机生导出（10§1.3 / 20§3.3）
# ---------------------------------------------------------------------------


class TestSnapshot:
    def test_export_snapshot_sorted_and_headered(self, mock_env, tmp_path: Path) -> None:
        reg = _reg(mock_env)
        reg.register(_valid_question(title="B 问"), actor="sess-A|AI")
        reg.register(_valid_question(title="A 问"), actor="sess-A|AI")
        out = tmp_path / "registry_latest.yaml"
        summary = export_snapshot(reg.get_conn, out, schema="main")
        assert summary["row_count"] == 2
        payload = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert payload["row_count"] == 2
        assert [q["q_id"] for q in payload["questions"]] == ["PQ-0001", "PQ-0002"]  # q_id 序
        assert "generated_at" in payload and payload["source"].startswith("zephyr.governance.meta_question.snapshot")
        assert "禁手工维护" in payload["declaration"]
        first = payload["questions"][0]
        assert first["data_sources"] == ["src.quote.daily"]  # jsonb 文本已结构化
        assert isinstance(first["version"], int)

    def test_export_snapshot_from_json_fallback(self, tmp_path: Path) -> None:
        rows = [
            {"q_id": "PQ-0002", "title": "B", "layer": "L1", "status": "registered", "version": 1},
            {"q_id": "PQ-0001", "title": "A", "layer": "L0", "status": "registered", "version": 1},
        ]
        src = tmp_path / "rows.json"
        src.write_text(json.dumps(rows), encoding="utf-8")
        out = tmp_path / "snap.json.yaml"
        summary = export_snapshot_from_json(src, out, schema="meta_question")
        assert summary["row_count"] == 2
        payload = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert [q["q_id"] for q in payload["questions"]] == ["PQ-0001", "PQ-0002"]
        with pytest.raises(ValueError):
            bad = tmp_path / "bad.json"
            bad.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
            export_snapshot_from_json(bad, tmp_path / "x.yaml")


# ---------------------------------------------------------------------------
# DDL 部署器（零 DB：schema 白名单 + 语句渲染；PG 生产库零接触）
# ---------------------------------------------------------------------------


def _load_ddl_module() -> Any:
    path = REPO_ROOT / "scripts" / "governance" / "apply_meta_question_ddl.py"
    spec = importlib.util.spec_from_file_location("apply_meta_question_ddl_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestDdlDeployer:
    def test_schema_whitelist_fail_closed(self) -> None:
        mod = _load_ddl_module()
        assert mod.check_schema_name("meta_question") == "meta_question"
        assert mod.check_schema_name("meta_question_test_w2_it") == "meta_question_test_w2_it"
        for bad in ("ai_intake", "meta_question_extra", "Meta_Question", "meta_question; DROP", ""):
            with pytest.raises(ValueError):
                mod.check_schema_name(bad)

    def test_drop_refuses_non_test_schema_before_connect(self) -> None:
        mod = _load_ddl_module()
        with pytest.raises(ValueError, match="拒删非测试 schema"):
            mod.drop_test_schema("meta_question")  # 前缀校验先于任何连接建立

    def test_ddl_statement_rendering(self) -> None:
        mod = _load_ddl_module()
        schema = "meta_question_test_render"
        stmts = mod._ddl_statements(schema)
        # 1 schema + 3 tables + 5 indexes
        assert len(stmts) == 9
        assert stmts[0] == f"CREATE SCHEMA IF NOT EXISTS {schema}"
        main_sql = stmts[1]
        assert "CREATE TABLE IF NOT EXISTS" in main_sql and f"{schema}.meta_question " in main_sql
        assert "^PQ-[0-9]{4}$" in main_sql  # q_id 格式 CHECK
        assert "'blinded'" in main_sql  # R2 枚举
        assert "claimed_until" in main_sql and "priority_score" in main_sql  # R1 运营字段
        audit_sql = stmts[2]
        for what in mod.AUDIT_WHAT_VOCAB:
            assert f"'{what}'" in audit_sql  # 20§2.1 SSOT 词表全量 CHECK
        exam_sql = stmts[3]
        assert "REFERENCES" in exam_sql and "'suspended'" in exam_sql
        joined = "\n".join(stmts)
        for index_name in mod.EXPECTED_INDEXES:
            assert index_name in joined
        for stmt in stmts:
            assert "DROP" not in stmt.upper()  # 部署路径零 DROP（幂等 IF NOT EXISTS）

    def test_grant_statements_role_split(self) -> None:
        mod = _load_ddl_module()
        grants = mod._grant_statements("meta_question")
        reader = [g for g in grants if "depgraph_reader" in g]
        writer = [g for g in grants if "depgraph_writer" in g]
        assert all("INSERT" not in g for g in reader)  # 读角色只读
        assert any("INSERT, UPDATE, DELETE" in g for g in writer)
        assert any("meta_question_audit_id_seq" in g for g in writer)  # bigserial 序列授权
