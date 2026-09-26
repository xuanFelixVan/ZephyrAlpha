# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §3 五要素机检（WO-001 真检口径）
# [MODULE] tests.governance.meta_question.wo_intake_reconcile.test_registry_real_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.meta_question_registry（WO-001 补丁落地后具备 load_source_line_register）; data/registers/metaq_source_line/source_line_registry.yaml（命中面）
# [CONSUMERS] WO-001② 关闸验收判据（新 register 事件 degraded_check 占比=0 的正反两腿）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 零生产路径写入：mock 库=内存 SQLite，册副本与 JSONL 全走 tmp_path（宪法 §9.6）；
#              未落地态整体 skip（禁让未落地补丁把 CI 染红，也禁伪装成通过）
# [MODIFY-GUARD] scripts/governance/meta_question/wo_intake_reconcile/patches/0001-*.patch（被测契约即该补丁）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红；registry 无真检入口=整件 skip（reason 指补丁号）
# [TESTS] 本件即测试
# [TTL] permanent
"""WO-001 registry 降级桩换真检的红蓝测试（补丁落地后生效）。

能红用例是本件主体：**线被删出册/数据源写错名/册不可用**三臂都必须真降级，
否则"命中即不降级"只是把桩拆了换成另一个无条件分支。
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Self

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓内路径真源，禁自算 parents[N]

_REGISTRY_MODULE = sys.modules["zephyr.governance.meta_question.meta_question_registry"]
# NO-BARE-SQL（§5.160.2）：测试侧断言用语句也集中在模块级，函数体不嵌 SQL。
SQL_AUDITS = "SELECT what, evidence FROM main.meta_question_audit WHERE q_id=?"
SQL_COUNT_MAIN = "SELECT COUNT(*) FROM main.meta_question"
LANDED = hasattr(_REGISTRY_MODULE, "load_source_line_register")
pytestmark = pytest.mark.skipif(not LANDED, reason="WO-001 真检补丁未落地（patches/0001 施加后自动生效）")

_REGISTER_PATH = REPO_ROOT / "data" / "registers" / "metaq_source_line" / "source_line_registry.yaml"

_DDL = (
    """CREATE TABLE main.meta_question (q_id TEXT PRIMARY KEY, title TEXT NOT NULL, layer TEXT NOT NULL,
      line_ref TEXT, graph_ref TEXT, data_sources TEXT NOT NULL DEFAULT '[]',
      exam_plan TEXT NOT NULL DEFAULT '{}', consumers TEXT NOT NULL DEFAULT '[]',
      frequency TEXT NOT NULL, pit_proof TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'draft',
      parent_id TEXT, merged_into TEXT, provenance TEXT NOT NULL DEFAULT '{}',
      net_zero_note TEXT NOT NULL DEFAULT '', chain_refs TEXT NOT NULL DEFAULT '[]',
      evidence_refs TEXT NOT NULL DEFAULT '[]', last_exam TEXT, priority_score REAL,
      priority_updated_at TEXT, claimed_by TEXT, claimed_until TEXT, version INTEGER NOT NULL DEFAULT 1,
      created_at TEXT, updated_at TEXT)""",
    """CREATE TABLE main.meta_question_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, q_id TEXT NOT NULL,
      actor TEXT NOT NULL, what TEXT NOT NULL, "before" TEXT, "after" TEXT,
      evidence TEXT NOT NULL DEFAULT '', created_at TEXT)""",
)


class _Cursor:
    def __init__(self, raw: sqlite3.Connection) -> None:
        self._cur = raw.cursor()

    def execute(self, sql: str, params: Any = ()) -> Self:
        self._cur.execute(sql.replace("%s", "?"), params)
        return self

    def fetchone(self) -> Any:
        return self._cur.fetchone()

    def fetchall(self) -> list[Any]:
        return self._cur.fetchall()

    @property
    def description(self) -> Any:
        return self._cur.description


class _Conn:
    def __init__(self, raw: sqlite3.Connection) -> None:
        self.raw = raw

    def cursor(self) -> _Cursor:
        return _Cursor(self.raw)

    def commit(self) -> None:
        self.raw.commit()

    def rollback(self) -> None:
        self.raw.rollback()

    def close(self) -> None:
        return None


@pytest.fixture()
def env(tmp_path: Path) -> dict[str, Any]:
    raw = sqlite3.connect(":memory:")
    for ddl in _DDL:
        raw.execute(ddl)
    raw.commit()
    conn = _Conn(raw)
    return {"raw": raw, "conn": conn, "tmp": tmp_path}


def _registry(env: dict[str, Any], register_path: Path | None) -> MetaQuestionRegistry:
    kwargs: dict[str, Any] = {
        "schema": "main",
        "get_conn": lambda *, read_only=True: env["conn"],
        "audit_jsonl_path": env["tmp"] / "audit.jsonl",
    }
    if "source_line_register_path" in _ctor_params():
        kwargs["source_line_register_path"] = register_path
    return MetaQuestionRegistry(**kwargs)


def _ctor_params() -> set[str]:
    spec = __import__("inspect").signature(MetaQuestionRegistry.__init__).parameters
    return set(spec)


def _question(**overrides: Any) -> dict[str, Any]:
    q: dict[str, Any] = {
        "title": "板块强弱持续性能否领先个股（真检蓝腿）？",
        "layer": "L1",
        "line_ref": "SL-A03",
        "graph_ref": None,
        "data_sources": ["DS-TQCENTER", "DS-TDX"],
        "exam_plan": {"criterion": "rank_ic", "threshold": 0.02},
        "consumers": ["L3状态变量层"],
        "frequency": "daily",
        "pit_proof": "板块成分快照按公告日取数，决策时点仅可见 T-1",
        "provenance": {"origin": "wo001-test"},
        "net_zero_note": "净零声明 NZ-TEST-WO001（替代人工散落提问，无删除对象）",
    }
    q.update(overrides)
    return q


def _audits(raw: sqlite3.Connection, q_id: str) -> list[tuple[str, str]]:
    return [(row[0], row[1]) for row in raw.execute(SQL_AUDITS, (q_id,))]


def _register_one(env: dict[str, Any], register_path: Path, **overrides: Any) -> list[tuple[str, str]]:
    reg = _registry(env, register_path)
    q_id = reg.register(_question(**overrides), actor="wo001-test|AI")
    return _audits(env["raw"], q_id)


def _slim_register(tmp_path: Path, drop_line: str | None = None, drop_token: str | None = None) -> Path:
    doc = yaml.safe_load(_REGISTER_PATH.read_text(encoding="utf-8"))
    if drop_line:
        doc["lines"] = [e for e in doc["lines"] if e["line_id"] != drop_line]
    if drop_token:
        for entry in doc["lines"]:
            entry["source_tokens"] = [t for t in entry["source_tokens"] if t != drop_token]
        doc["source_token_universe"] = [t for t in doc["source_token_universe"] if t != drop_token]
    doc["counts"]["lines"] = len(doc["lines"])
    doc["counts"]["tier_A"] = sum(1 for e in doc["lines"] if e["tier"] == "A")
    doc["counts"]["tier_B"] = sum(1 for e in doc["lines"] if e["tier"] == "B")
    doc["counts"]["tier_C"] = sum(1 for e in doc["lines"] if e["tier"] == "C")
    doc["counts"]["source_token_universe"] = len(doc["source_token_universe"])
    out = tmp_path / "register_slim.yaml"
    out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return out


def test_green_full_hit_produces_no_degraded_event(env: dict[str, Any]) -> None:
    events = _register_one(env, _REGISTER_PATH)
    assert ("register", "") in events or any(w == "register" for w, _ in events)
    assert not any(w == "degraded_check" for w, _ in events), events


def test_red_line_removed_from_register_degrades(env: dict[str, Any]) -> None:
    slim = _slim_register(env["tmp"], drop_line="SL-A03")
    events = _register_one(env, slim)
    degraded = [(w, e) for w, e in events if w == "degraded_check"]
    assert degraded, "线被删出册必须真降级（真检有牙）"
    assert "source_line_resolvability" in degraded[0][1]


def test_red_unknown_source_token_degrades(env: dict[str, Any]) -> None:
    events = _register_one(env, _REGISTER_PATH, data_sources=["DS-TQCENTER", "not_a_registered_source"])
    assert any(w == "degraded_check" for w, _ in events), events


def test_red_missing_register_file_degrades_all(env: dict[str, Any]) -> None:
    events = _register_one(env, env["tmp"] / "nope.yaml", title="册不可用时的登记（红腿）？")
    degraded = [(w, e) for w, e in events if w == "degraded_check"]
    assert degraded and degraded[0][1] == "W4_source_line_registry_pending", degraded


def test_red_off_vocab_consumer_still_degrades(env: dict[str, Any]) -> None:
    events = _register_one(
        env, _REGISTER_PATH, consumers=["未答看板"], title="四件套消费清单未建时的消费方判定（红腿）？"
    )
    assert any("consumer_registry_resolvability" in e for w, e in events if w == "degraded_check"), events


def test_legacy_ungrounded_fixture_still_degrades(env: dict[str, Any]) -> None:
    """回归护栏：在队 test_metaq_registry.py 的 _valid_question（无 line_ref+野源）必须仍带降级痕，
    否则 WO-001 补丁会把别人的蓝腿测试洗成假通过。"""
    legacy = _question(
        title="大盘情绪因子在 L3 传导是否显著",
        layer="L3",
        line_ref=None,
        data_sources=["src.quote.daily"],
        consumers=["D1_decision"],
    )
    reg = _registry(env, _REGISTER_PATH)
    q_id = reg.register(legacy, actor="wo001-test|AI")
    events = _audits(env["raw"], q_id)
    assert any(w == "degraded_check" for w, _ in events), events


def test_register_rejects_before_any_write(env: dict[str, Any]) -> None:
    with pytest.raises(Exception) as exc:
        _registry(env, _REGISTER_PATH).register(_question(data_sources=[]), actor="wo001-test|AI")
    assert "data_sources_empty" in str(exc.value)
    assert env["raw"].execute(SQL_COUNT_MAIN).fetchone()[0] == 0
