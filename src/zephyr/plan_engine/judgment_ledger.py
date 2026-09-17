# [BLUEPRINT] MOD-PLAN-026 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §二/§五
# [MODULE] zephyr.plan_engine.judgment_ledger
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.data.ch_writer; schemas.categories.judgment.(intraday_market_state|next_day_forecast|daily_plan)
# [CONSUMERS] 作战室三任务（盘中 L1 跟踪件/盘后概率件/场景引擎 MOD-PLAN-018）; 全仓"接电即接台账"新模块（标准 §五推广政策）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定/结算分离（本件只写判定列组，结算列组无写通道——铁律 §一.2）; judgment_id=ULID（时序可排序，修订=新 id 追加禁 UPDATE）; payload 校验 fail-closed（坏 JSON/概率越界/分布和≠1 即拒）; PIT 锚 input_cutoff_ts≤asof_ts; INSERT 列清单以 schemas 真源为准（本件不复制 DDL，漂移由单测机械对齐）; 写入只走 ch_writer（禁裸 SQL 散落）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（table_key/confidence/payload/PIT/触发式非可测量 非法 fail-closed）; 写入失败不抛（EmitResult.committed=False + disposition 留痕，调用方自查——发射器嵌入采集链不得反噬主流程）
# [TESTS] tests/plan_engine/test_judgment_ledger.py
# [A_module] module_id=MOD-PLAN-026 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""judgment_ledger — 判定台账发射器库件（判定台账标准 v0.1 §二 通用骨架，全仓推广件）。

"每一个产出判定的模块，都必须把判定写进数据库表"（2026-09-16 Owner 洞察制度化）。
本件=推广政策 §五"接电即接台账"的标准接插件：任何模块一行调用即可发射判定——

    from zephyr.plan_engine.judgment_ledger import emit_judgment

    emit_judgment("next_day_forecast", JudgmentDraft(
        "MOD-xxx", "v1", "index:000300.SH",
        {"p_up": 0.35, "p_flat": 0.25, "p_down": 0.40}, 0.62))

四件事封装：
1. judgment_id 生成——ULID（48bit 毫秒时序 + 80bit 随机，Crockford Base32 26 字符，
   仓内无 ULID 依赖，标准库自实现；时序可排序=台账天然按判定时刻扫读；进程内单调，
   并发发射不撞号）。
2. 通用列契约——INSERT 列清单 fail-closed 导入 schemas/categories/judgment/ 真源
   （结算列组不在清单内=判定器结构性无写通道；仓根路径自 __file__ 引导，与
   apply_market_tables_ddl 同法）。
3. payload 校验——按表 fail-closed：状态概率/三元分布/path_prior 和≈1 且分量∈[0,1]；
   daily_plan.trigger 须含比较符或数字（"trigger 必须是可测量表达式"机械初检，
   "如果走弱"不合格——深检归场景引擎）。
4. 发射 helper——payload→TSV（ch_writer.tsv_escape）→write_tsv_outcome（HTTP 主路径
   +本地落盘兜底）；committed=False 时 disposition 留痕不抛（采集链反噬防护）。

不做什么：不写结算列（无通道）；不做结算（judgment_settler 职责）；不做聚合报告
（judgment_settler.aggregate_report）。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §一/§二/§五
SSoT: depgraph node 14509129（MOD-PLAN-026，蓝图待作战室附录合并后补录）
Version: 0.1.0
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final

from zephyr.data import ch_writer
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "EmitResult",
    "JUDGMENT_TABLE_KEYS",
    "JUDGMENT_TABLES",
    "JudgmentDraft",
    "emit_judgment",
    "format_utc3",
    "new_judgment_id",
    "validate_payload",
]

# ── schemas 真源导入（仓根路径引导：src/zephyr/plan_engine/本文件 → parents[3]=仓根）──
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# fail-closed 导入（无内联 fallback——JOB-077 治本：防静默使用漂移副本）
from schemas.categories.judgment.judgment_daily_plan import INSERT_COLUMNS as _COLS_DAILY_PLAN
from schemas.categories.judgment.judgment_daily_plan import TABLE_NAME as _TBL_DAILY_PLAN
from schemas.categories.judgment.judgment_intraday_market_state import (
    INSERT_COLUMNS as _COLS_INTRADAY,
)
from schemas.categories.judgment.judgment_intraday_market_state import TABLE_NAME as _TBL_INTRADAY
from schemas.categories.judgment.judgment_next_day_forecast import (
    INSERT_COLUMNS as _COLS_NEXT_DAY,
)
from schemas.categories.judgment.judgment_next_day_forecast import TABLE_NAME as _TBL_NEXT_DAY

# ── 口径常量 ──

_DB: Final = "c1_market"
_PROB_SUM_TOLERANCE: Final = 1e-6  # 概率分布和≈1 容差（与 brier_calibration 同口径）
# 可测量触发式机械初检：须含比较符/等号/感叹号或数字（"如果走弱"不合格——标准 §三铁律）
_MEASURABLE_TRIGGER_RE: Final = re.compile(r"[><=!]|\d")


# ── 表规格注册表（新表接入=此处一行 + schemas 真源 + 单测对齐）──


@dataclass(frozen=True)
class _TableSpec:
    """单表发射契约（INSERT 列清单来自 schemas 真源，结算列组结构性缺席）。"""

    table: str  # 全限定表名
    insert_columns: str  # "(judgment_id, ...)" 列子句（真源导入）
    default_horizon: str  # 未显式给 horizon 时的默认值


_TABLE_SPECS: Final[dict[str, _TableSpec]] = {
    "intraday_market_state": _TableSpec(
        table=f"{_DB}.{_TBL_INTRADAY}",
        insert_columns=_COLS_INTRADAY,
        default_horizon="intraday_rest",
    ),
    "next_day_forecast": _TableSpec(
        table=f"{_DB}.{_TBL_NEXT_DAY}",
        insert_columns=_COLS_NEXT_DAY,
        default_horizon="next_day",
    ),
    "daily_plan": _TableSpec(
        table=f"{_DB}.{_TBL_DAILY_PLAN}",
        insert_columns=_COLS_DAILY_PLAN,
        default_horizon="intraday_session",
    ),
}

JUDGMENT_TABLE_KEYS: Final[tuple[str, ...]] = tuple(_TABLE_SPECS)

# 全限定表名映射（结算器/聚合等消费方共用——表名注册单一真源，禁另拼第二份）
JUDGMENT_TABLES: Final[dict[str, str]] = {k: s.table for k, s in _TABLE_SPECS.items()}

# 盘中五态（标准 §三表 1 state_label/state_probs 值域）
_INTRADAY_STATES: Final[tuple[str, ...]] = ("低迷", "防御", "震荡", "进攻", "亢奋")


# ── ULID（判定标准 §二：judgment_id String -- ULID）──

_ULID_B32: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford Base32（去 I L O U）
_ULID_LOCK = threading.Lock()
_ULID_LAST_MS: Final = [0]
_ULID_LAST_RAND: Final = [b"\x00" * 10]


def new_judgment_id() -> str:
    """生成 ULID（26 字符，时序可排序，进程内严格单调）。

    48bit 毫秒时序 + 80bit 随机（os.urandom）；同毫秒并发发射时随机段+1
    保证单调不重（标准 ULID monotonic 单进程语义）。零外部依赖。
    """
    ms = int(now_utc().timestamp() * 1000)  # 时钟真源=time_utils SSoT（SCHEMA-TZ 门合规）
    rand = bytearray(os.urandom(10))
    with _ULID_LOCK:
        if ms <= _ULID_LAST_MS[0]:
            ms = _ULID_LAST_MS[0]
            prev = bytearray(_ULID_LAST_RAND[0])
            for i in range(9, -1, -1):  # 随机段 +1（大端进位）
                prev[i] = (prev[i] + 1) & 0xFF
                if prev[i]:
                    break
            else:  # 80bit 溢出（同毫秒 2^80 次，物理不可达——防御性兜底）
                ms += 1
                prev = bytearray(os.urandom(10))
            rand = prev
        _ULID_LAST_MS[0] = ms
        _ULID_LAST_RAND[0] = bytes(rand)
    # 48bit 时序 → 10 字符 + 80bit 随机 → 16 字符（整型位提取，MSB first——
    # 随机段任一字节变化必反映到编码，自增单调性可观测）
    ts: list[str] = ["0"] * 10
    v = ms & 0xFFFFFFFFFFFF
    for i in range(9, -1, -1):
        ts[i] = _ULID_B32[v & 0x1F]
        v >>= 5
    body: list[str] = ["0"] * 16
    v = int.from_bytes(rand, "big")
    for i in range(15, -1, -1):
        body[i] = _ULID_B32[v & 0x1F]
        v >>= 5
    return "".join(ts) + "".join(body)


def format_utc3(dt: datetime) -> str:
    """datetime → 'YYYY-MM-DD HH:MM:SS.mmm'（DateTime64(3,'UTC') TSV 字面量）。"""
    if dt.tzinfo is None:
        raise ValueError("datetime 缺时区（RULE-SCHEMA-TZ：显式 UTC）")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


# ── payload 校验（fail-closed）──


def _num(v: object, field: str) -> float:
    """有限实数校验（bool 不算数——Python bool 是 int 子类，须显式排除）。"""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{field} 非法（须实数）: {v!r}")
    f = float(v)
    if f != f or f in (float("inf"), float("-inf")):
        raise ValueError(f"{field} 非法（须有限实数）: {v!r}")
    return f


def _prob(v: object, field: str) -> float:
    f = _num(v, field)
    if f < 0.0 or f > 1.0:
        raise ValueError(f"{field} 非法（须 [0,1]）: {v!r}")
    return f


def _validate_state_probs(probs: object) -> None:
    """盘中五态分布：键⊆五态、分量∈[0,1]、和≈1。"""
    if not isinstance(probs, dict) or not probs:
        raise ValueError(f"state_probs 非法（须非空 dict）: {probs!r}")
    total = 0.0
    for k, v in probs.items():
        if k not in _INTRADAY_STATES:
            raise ValueError(f"state_probs 键非法（值域 {_INTRADAY_STATES}）: {k!r}")
        total += _prob(v, f"state_probs[{k!r}]")
    if abs(total - 1.0) > _PROB_SUM_TOLERANCE:
        raise ValueError(f"state_probs 和≠1（±{_PROB_SUM_TOLERANCE}）: {total!r}")


def _validate_payload_intraday(p: dict) -> None:
    label = p.get("state_label")
    if label not in _INTRADAY_STATES:
        raise ValueError(f"state_label 非法（值域 {_INTRADAY_STATES}）: {label!r}")
    _validate_state_probs(p.get("state_probs"))
    rest = p.get("rest_of_day")
    if rest is not None:
        if not isinstance(rest, dict):
            raise ValueError(f"rest_of_day 非法（须 dict）: {rest!r}")
        if "tail_dir_prob_down" in rest:
            _prob(rest["tail_dir_prob_down"], "rest_of_day.tail_dir_prob_down")
        amp = rest.get("amp_range_pct")
        if amp is not None:
            if not isinstance(amp, (list, tuple)) or len(amp) != 2:
                raise ValueError(f"amp_range_pct 非法（须 [低,高] 二元）: {amp!r}")
            lo, hi = _num(amp[0], "amp_range_pct[0]"), _num(amp[1], "amp_range_pct[1]")
            if lo > hi:
                raise ValueError(f"amp_range_pct 低>高: {amp!r}")


def _validate_payload_next_day(p: dict) -> None:
    total = 0.0
    for k in ("p_up", "p_flat", "p_down"):
        total += _prob(p.get(k), k)
    if abs(total - 1.0) > _PROB_SUM_TOLERANCE:
        raise ValueError(f"p_up+p_flat+p_down 和≠1（±{_PROB_SUM_TOLERANCE}）: {total!r}")
    q = p.get("quantiles")
    if q is not None:
        if not isinstance(q, dict):
            raise ValueError(f"quantiles 非法（须 dict）: {q!r}")
        for k, v in q.items():
            _num(v, f"quantiles[{k!r}]")
    for k in ("expected_vol_pct", "expected_range_pct"):
        if k in p and _num(p[k], k) < 0:
            raise ValueError(f"{k} 非法（须 ≥0）: {p[k]!r}")


def _validate_payload_daily_plan(p: dict) -> None:
    scenarios = p.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError(f"scenarios 非法（须非空 list）: {scenarios!r}")
    prior_sum = 0.0
    ids: set[str] = set()
    for i, sc in enumerate(scenarios):
        if not isinstance(sc, dict):
            raise ValueError(f"scenarios[{i}] 非法（须 dict）: {sc!r}")
        sid = sc.get("scenario_id")
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError(f"scenarios[{i}].scenario_id 非法（须非空 str）: {sid!r}")
        if sid in ids:
            raise ValueError(f"scenarios[{i}].scenario_id 重复: {sid!r}")
        ids.add(sid)
        trig = sc.get("trigger")
        if not isinstance(trig, str) or not _MEASURABLE_TRIGGER_RE.search(trig):
            raise ValueError(
                f"scenarios[{i}].trigger 非可测量表达式（须含比较符/数字，'如果走弱'不合格）: {trig!r}"
            )
        prior_sum += _prob(sc.get("path_prior"), f"scenarios[{i}].path_prior")
    if abs(prior_sum - 1.0) > _PROB_SUM_TOLERANCE:
        raise ValueError(f"path_prior 和≠1（±{_PROB_SUM_TOLERANCE}，结算按分布算 Brier）: {prior_sum!r}")
    scope = p.get("inputs_scope")
    if scope is not None and (not isinstance(scope, list) or not all(isinstance(s, str) for s in scope)):
        raise ValueError(f"inputs_scope 非法（须 str list）: {scope!r}")


_VALIDATORS: Final[dict[str, Any]] = {
    "intraday_market_state": _validate_payload_intraday,
    "next_day_forecast": _validate_payload_next_day,
    "daily_plan": _validate_payload_daily_plan,
}


def validate_payload(table_key: str, payload: dict | str) -> str:
    """payload 校验 + JSON 序列化（fail-closed，非法即 ValueError）。

    Args:
        table_key: JUDGMENT_TABLE_KEYS 之一。
        payload: dict（结构校验后规范化序列化）或 JSON str（解析后校验再规范化）。

    Returns:
        规范化 JSON 串（ensure_ascii=False / 紧凑分隔符——CJK 直存可读）。

    Raises:
        ValueError: table_key 未知 / payload 非 dict / 坏 JSON / 结构越界。
    """
    spec = _TABLE_SPECS.get(table_key)
    if spec is None:
        raise ValueError(f"table_key 非法（值域 {JUDGMENT_TABLE_KEYS}）: {table_key!r}")
    if isinstance(payload, str):
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ValueError(f"payload 坏 JSON: {e}") from e
    elif isinstance(payload, dict):
        obj = payload
    else:
        raise ValueError(f"payload 非法（须 dict 或 JSON str）: {type(payload).__name__}")
    _VALIDATORS[table_key](obj)
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ── 发射器（各模块一行调用）──


@dataclass(frozen=True)
class EmitResult:
    """一次发射的结果（committed=False 时调用方自查 disposition，发射器不抛）。"""

    judgment_id: str
    table: str
    committed: bool
    disposition: str  # ch_committed / local_durable / not_durable（ch_writer 口径）


@dataclass(frozen=True)
class JudgmentDraft:
    """判定内容打包（NO-LONG-PARAM-LIST 合规：判定六要素+血缘一组走）。

    一行调用形如::

        emit_judgment("next_day_forecast", JudgmentDraft(
            "MOD-xxx", "v1", "index:000300.SH", {"p_up": 0.4, ...}, 0.62))
    """

    module_id: str  # 产出判定模块（MOD-xxx，非空）
    model_version: str  # 判定算法版本（非空）
    subject: str  # 判定对象（如 index:000300.SH，非空）
    payload: dict | str  # 判定内容（dict/JSON str，按表 fail-closed 校验）
    confidence: float  # 置信度 ∈[0,1]
    horizon: str | None = None  # 预测时段（None=按表默认）
    inputs_ref: str = ""  # 输入快照指纹/引用清单
    run_id: str = ""  # 血缘 run 标识


def _validate_emit_identity(table_key: str, draft: JudgmentDraft) -> _TableSpec:
    """发射参数 fail-closed 校验（返回表规格——复杂度收口在子函数）。"""
    spec = _TABLE_SPECS.get(table_key)
    if spec is None:
        raise ValueError(f"table_key 非法（值域 {JUDGMENT_TABLE_KEYS}）: {table_key!r}")
    if not isinstance(draft.module_id, str) or not draft.module_id.strip():
        raise ValueError(f"module_id 非法（须非空 str）: {draft.module_id!r}")
    if not isinstance(draft.model_version, str) or not draft.model_version.strip():
        raise ValueError(f"model_version 非法（须非空 str）: {draft.model_version!r}")
    if not isinstance(draft.subject, str) or not draft.subject.strip():
        raise ValueError(f"subject 非法（须非空 str）: {draft.subject!r}")
    _prob(draft.confidence, "confidence")
    return spec


def _resolve_pit_anchors(
    asof_ts: datetime | None,
    input_cutoff_ts: datetime | None,
) -> tuple[datetime, datetime]:
    """PIT 锚解析：默认值补齐 + 时区校验 + 截断≤判定（违规 fail-closed）。"""
    a_ts = asof_ts or datetime.now(timezone.utc)
    i_ts = input_cutoff_ts or a_ts
    for name, dt in (("asof_ts", a_ts), ("input_cutoff_ts", i_ts)):
        if not isinstance(dt, datetime) or dt.tzinfo is None:
            raise ValueError(f"{name} 非法（须带时区 datetime，RULE-SCHEMA-TZ）: {dt!r}")
    if i_ts > a_ts:
        raise ValueError(f"PIT 违规：input_cutoff_ts({format_utc3(i_ts)}) > asof_ts({format_utc3(a_ts)})")
    return a_ts, i_ts


def emit_judgment(
    table_key: str,
    draft: JudgmentDraft,
    *,
    asof_ts: datetime | None = None,
    input_cutoff_ts: datetime | None = None,
    synthetic: bool = False,
    judgment_id: str | None = None,
) -> EmitResult:
    """发射一条判定（标准 §二通用骨架全默认值，一行调用即可接台账）。

    判定/结算分离铁律：本函数只写判定列组——INSERT 列清单来自 schemas 真源，
    结算列组（outcome_*/eval_*/evaluated_*）结构性不在清单内。

    Args:
        table_key: JUDGMENT_TABLE_KEYS 之一（"intraday_market_state"/"next_day_forecast"/"daily_plan"）。
        draft: 判定内容打包 JudgmentDraft（module_id/model_version/subject/payload/
            confidence/horizon/inputs_ref/run_id）。
        asof_ts: 判定时刻（None=now UTC；PIT 锚）。
        input_cutoff_ts: 数据截断时刻（None=asof_ts；须 ≤asof_ts）。
        synthetic: 合成/测试行标记（冒烟后按 synthetic=1 清理）。
        judgment_id: 显式指定 id（None=自动 ULID；测试注入用）。

    Returns:
        EmitResult（committed=False=未入 CH，disposition 留痕）。

    Raises:
        ValueError: 参数/payload 非法（fail-closed——校验失败绝不写半行）。
    """
    spec = _validate_emit_identity(table_key, draft)
    payload_json = validate_payload(table_key, draft.payload)
    a_ts, i_ts = _resolve_pit_anchors(asof_ts, input_cutoff_ts)
    jid = judgment_id or new_judgment_id()
    row = "\t".join(
        ch_writer.tsv_escape(v)
        for v in (
            jid,
            draft.module_id,
            draft.model_version,
            format_utc3(a_ts),
            format_utc3(i_ts),
            draft.horizon or spec.default_horizon,
            draft.subject,
            payload_json,
            float(draft.confidence),
            draft.inputs_ref,
            draft.run_id,
            1 if synthetic else 0,
        )
    )
    outcome = ch_writer.write_tsv_outcome(spec.table, spec.insert_columns, (row + "\n").encode("utf-8"))
    return EmitResult(
        judgment_id=jid,
        table=spec.table,
        committed=outcome.disposition == ch_writer.WriteDisposition.CH_COMMITTED,
        disposition=str(outcome.disposition.value),
    )
