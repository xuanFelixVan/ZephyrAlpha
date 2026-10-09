# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1/§2/§3（考试循环簇红蓝自测装配）
# [MODULE] tests.governance.meta_question.conftest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] tests/governance/meta_question/test_metaq_registry.py（SQLite mock 连接与合法问题底稿——importlib 复用上游夹具本体，禁复制第二份 DDL）; zephyr.governance.meta_question.exam_loop（被测包）
# [CONSUMERS] tests/governance/meta_question/test_exam_loop_*.py（5 件，只经夹具取用，禁跨模块相对 import——本目录非包）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 零 PG 生产接触（全内存 SQLite mock + tmp_path JSONL，禁写生产路径）；
#              上游 mock_env 本体经 __wrapped__ 复用（pytest 8 装饰后为 FixtureFunctionDefinition，禁假设它仍是原函数）；
#              题卷底稿必带结构化判据四项（min_confidence/power_min/out_of_sample_share_min/可机解 threshold），
#              红蓝用例靠"删缺项"制造红灯，不靠改断言（上一班教训：判通过的尺须先证明它能红）；
#              扩展码落地态每例重置（autouse，防自省缓存跨例串味）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 上游夹具本体取不到=收集期报错（fail-closed，禁降级复制 DDL 掩盖真源漂移）
# [TESTS] self
# [TTL] task_bound
"""考试循环簇测试装配（复用上游 mock 环境，零 PG 生产路径）。"""

from __future__ import annotations

import importlib.util
import json
import pathlib
from datetime import timedelta
from types import SimpleNamespace
from typing import Any, Iterator

import pytest

from zephyr.governance.meta_question.exam_loop import event_codes
from zephyr.governance.meta_question.exam_loop.exam_lifecycle import ExamLoopStateMachine
from zephyr.governance.meta_question.exam_loop.ledger import ExamLoopLedger
from zephyr.governance.meta_question.exam_loop.writeback import ExamLoopWriteback
from zephyr.shared.utils.time_utils import now_utc

_DIR = pathlib.Path(__file__).resolve().parent

SESSION = "st-wo-b1-examloop"
IMPOSTOR = "st-impostor-b1|AI"
PLAN_VERSION = "v2-wo-b1-test"

SQL_EVIDENCE_PROBE_QUERY = "SELECT count(*) FROM meta_question"
SQL_SELECT_AUDIT_ROWS = 'SELECT q_id, actor, what, "before", "after", evidence FROM main.meta_question_audit'


def _load_upstream() -> Any:
    """按路径加载同目录 test_registry（复用 DDL/连接代理/底稿，零复制）。"""
    spec = importlib.util.spec_from_file_location("mq_registry_upstream", _DIR / "test_metaq_registry.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPSTREAM = _load_upstream()
_MOCK_ENV = getattr(UPSTREAM.mock_env, "__wrapped__", None)
if _MOCK_ENV is None:  # pragma: no cover - pytest 版本漂移即 fail-closed
    raise RuntimeError("上游 mock_env 夹具本体不可达（pytest 版本漂移），禁复制 DDL 绕过")


# ---------------------------------------------------------------------------
# 载荷构造器（结构化考卷 / 合规回填 / 合法问题）
# ---------------------------------------------------------------------------


def structured_plan(**overrides: Any) -> dict[str, Any]:
    """结构化预注册考卷（PQ-0098 六件；用例 pop 缺项即触发降级/拒收）。"""
    plan: dict[str, Any] = {
        "method": "全表扫描 jsonb 字段",
        "criterion": "rank_ic",
        "threshold": ">=0.02",
        "min_confidence": 90.0,
        "power_min": 0.8,
        "out_of_sample_share_min": 0.3333333,
        "sample_size": 500,
        "effect_size": 0.15,
        "window_rule": "trailing_250",
    }
    plan.update(overrides)
    for key, value in list(plan.items()):
        if value is None:
            plan.pop(key)
    return plan


def question(**overrides: Any) -> dict[str, Any]:
    """合法问题底稿（上游五要素 + 本簇结构化考卷）。"""
    q = dict(UPSTREAM._valid_question())
    q["exam_plan"] = structured_plan()
    q["frequency"] = "weekly"
    q.update(overrides)
    return q


def exam_payload(**overrides: Any) -> dict[str, Any]:
    """一场合规考试的回填载荷（13§1.1 执行头+结果四段+断言段齐备）。"""
    now = now_utc()
    payload: dict[str, Any] = {
        "outcome": "answered",
        "exam_ref": "wo-b1/probe/PQ-TEST",
        "examiner_ref": "整装回测",
        "run_ref": "run-0001",
        "exam_plan_version": PLAN_VERSION,
        "conclusion_value": 0.031,
        "conclusion_dir": "支持",
        "confidence_level": 95.0,
        "ci_lo": 0.02,
        "ci_hi": 0.04,
        "data_window": {
            "start": (now - timedelta(days=40)).date().isoformat(),
            "end": (now - timedelta(days=1)).date().isoformat(),
            "fetch_ts": (now - timedelta(hours=6)).isoformat(),
            "decision_ts": (now - timedelta(hours=5)).isoformat(),
        },
        "sample_out_share": 0.5,
        "sample_size": 500,
        "effect_size": 0.15,  # √(n-3)·atanh(0.15)=3.37 → 功效≈0.96（用例若要"低功效延期"红腿则传更小值）
        "pit_assertion": "各源 as-of 均早于决策时点",
        "pit_check_ref": "probe/pit_check",
        "exam_completed_at": (now - timedelta(minutes=30)).isoformat(),
        "evidence_refs": [{"table": "meta_question.meta_question", "query": SQL_EVIDENCE_PROBE_QUERY}],
    }
    payload.update(overrides)
    for key, value in list(payload.items()):
        if value is None:
            payload.pop(key)
    return payload


# ---------------------------------------------------------------------------
# 账本判读（红蓝断言用）
# ---------------------------------------------------------------------------


def audit_rows(env: dict[str, Any], q_id: str | None = None) -> list[dict[str, Any]]:
    """读 PG 轨审计行（mock 库，before/after 解 JSON）。"""
    sql = SQL_SELECT_AUDIT_ROWS
    params: tuple[Any, ...] = ()
    if q_id:
        sql += " WHERE q_id=?"
        params = (q_id,)
    cur = env["raw"].execute(sql + " ORDER BY id", params)
    rows: list[dict[str, Any]] = []
    for row in cur.fetchall():
        item = dict(zip(("q_id", "actor", "what", "before", "after", "evidence"), row, strict=True))
        for key in ("before", "after"):
            item[key] = json.loads(item[key]) if isinstance(item[key], str) and item[key] else (item[key] or {})
        rows.append(item)
    return rows


def jsonl_rows(env: dict[str, Any]) -> list[dict[str, Any]]:
    path = env["jsonl_path"]
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def event_code_hits(rows: list[dict[str, Any]], code: str) -> list[dict[str, Any]]:
    """过渡载体口径命中（what 直写 / after.event_code / evidence 前缀，三径同真）。"""
    prefix = event_codes.evidence_prefix() + code
    return [
        row
        for row in rows
        if row.get("what") == code
        or (row.get("after") or {}).get(event_codes.event_code_key()) == code
        or str(row.get("evidence") or "").startswith(prefix)
    ]


HELPERS = SimpleNamespace(
    SESSION=SESSION,
    IMPOSTOR=IMPOSTOR,
    PLAN_VERSION=PLAN_VERSION,
    structured_plan=structured_plan,
    question=question,
    exam_payload=exam_payload,
    audit_rows=audit_rows,
    jsonl_rows=jsonl_rows,
    event_code_hits=event_code_hits,
    event_codes=event_codes,
    now_utc=now_utc,
)


# ---------------------------------------------------------------------------
# 夹具
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _fresh_landing_cache() -> Iterator[None]:
    """扩展码落地态每例重置（防上一例的缓存串味）。"""
    event_codes.clear_landing_cache()
    yield
    event_codes.clear_landing_cache()


@pytest.fixture()
def mock_env(tmp_path: pathlib.Path) -> Any:
    """上游夹具再导出（供本目录新测试使用，行为与上游完全同源）。"""
    yield from _MOCK_ENV(tmp_path)


@pytest.fixture()
def env(mock_env: dict[str, Any]) -> dict[str, Any]:
    """mock_env 之上装配考试循环簇三件套（ledger/exam_lifecycle/writeback 共用同一 registry）。"""
    registry = mock_env["registry"]
    ledger = ExamLoopLedger(registry)
    sm = ExamLoopStateMachine(ledger)
    return {
        **mock_env,
        "registry": registry,
        "ledger": ledger,
        "sm": sm,
        "wb": ExamLoopWriteback(registry, ledger=ledger, state_machine=sm),
    }


@pytest.fixture()
def mq() -> SimpleNamespace:
    """判读工具组（本目录非包，禁相对 import，一律经夹具取用）。"""
    return HELPERS


@pytest.fixture()
def claimed(env: dict[str, Any], mq: SimpleNamespace) -> dict[str, Any]:
    """已推进到 in_exam 且被本会话活跃认领的问题（回写鉴权合法前提）。"""
    registry = env["registry"]
    q_id = registry.register(mq.question(), actor=mq.SESSION)
    registry.transition(q_id, "mining", actor=mq.SESSION)
    registry.transition(q_id, "in_exam", actor=mq.SESSION)
    registry.claim(q_id, mq.SESSION, lease_hours=24)
    return {"q_id": q_id, "env": env}
