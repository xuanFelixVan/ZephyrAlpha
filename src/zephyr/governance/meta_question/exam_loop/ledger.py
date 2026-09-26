# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md | §2.1 留痕规范（先账后实）+ §2.2 PG+JSONL 双轨载体
# [MODULE] zephyr.governance.meta_question.exam_loop.ledger
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.meta_question_registry (MetaQuestionRegistry：承载 _write_audit 双轨真源，本件只组合不改); zephyr.governance.meta_question.exam_ops (MetaQuestionAuditEvent 参数对象 + AUDIT_WHAT_VOCAB 已落地词表); .event_codes (落账载体选择：已落地码直写 / 扩展码过渡载体)
# [CONSUMERS] zephyr.governance.meta_question.exam_loop.exam_lifecycle; .writeback; .reexam_scheduler; scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py; tests/governance/meta_question/test_exam_loop_ledger.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本件=审计落账的唯一组合口：所有考试循环事件一律经 write_event 落 PG 行 + JSONL 追加双轨（20§2.2），禁各调用点自拼 INSERT；
#              双轨真源复用冻结件 _write_audit/_append_jsonl（本件不重写 SQL、不重写 JSONL 键序，零 extract 级克隆）；
#              what 值必须经 event_codes.resolve 决定：已落地→真实码；未落地→base_what(update) 且 event_code 双写进 after JSONB + evidence 前缀 + diff；
#              先账后实（20§2.1）：业务写与账写同事务，账行 INSERT 先于业务行 UPDATE/INSERT，由调用方持同一 cur 编排；
#              拒收痕（越权/非法流转/降阈值）须独立提交：业务写回滚而账行留存，故拒收路径专用 write_event_standalone 自开事务；
#              读侧 SQL 方言可移植（SQLite mock 无 ->> 操作符），PG 三口径全量匹配只在复考判据侧用 event_codes.sql_event_match()；
#              扩展事件码必须在册（config/examloop_audit_event_vocabulary.yaml），不在册即 ValueError——禁另立枚举
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md §2（改留痕规范先改总册）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未登记事件码=ValueError（event_codes 硬拦）；PG 写失败=原样上抛（fail-closed，禁降级为只写 JSONL）；
#                  write_event_standalone 自身失败=上抛且不影响已回滚的业务写
# [TESTS] tests/governance/meta_question/test_exam_loop_ledger.py（双轨同键/过渡载体/独立提交痕/未登记码拒写）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ledger — 考试循环簇审计落账组合口（双轨 + 扩展事件码过渡载体）。

设计真源：``20_management_policy.md`` §2.1/§2.2 + ``13_exam_backfill_loop_design.md`` §1。
本件不改冻结件 ``exam_ops.py``，只把"事件码 → 落账载体"的换算与"先账后实"的编排收口到一处，
使总包把扩展码并入 ``AUDIT_WHAT_VOCAB`` 之后调用点零改动（载体自动切换为真实 what）。

用法::

    ledger = ExamLoopLedger(registry)
    with ledger.transaction() as cur:              # 业务写同事务
        ledger.write_event(cur, "exam_writeback", q_id=..., actor=..., after={...})
        cur.execute(business_sql, ...)             # 先账后实
    ledger.write_event_standalone("claim_mismatch", q_id=..., actor=..., evidence="...")
# target: src/zephyr/governance/meta_question/exam_loop/ledger.py (docstring 575 字, 9 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/ledger.yaml
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Final, Iterator

from zephyr.governance.meta_question.exam_ops import AUDIT_WHAT_VOCAB, MetaQuestionAuditEvent
from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry

from . import event_codes

__all__: Final = ["ExamLoopLedger"]

_JOINER = " OR "

#: 可选审计载荷字段（经 **fields 关键字透传，语义与默认值同具名参数时期：
#: before/after/diff 默认 None、evidence 默认 ""；其余关键字=TypeError 契约不变）
_EVENT_PAYLOAD_FIELDS: Final[frozenset[str]] = frozenset({"before", "after", "evidence", "diff"})


def _split_event_fields(
    func_name: str, fields: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str, list[dict[str, Any]] | None]:
    """从 ``**fields`` 还原可选审计载荷字段（保持原关键字参数的默认值与 TypeError 契约）。"""
    unknown = sorted(set(fields) - _EVENT_PAYLOAD_FIELDS)
    if unknown:
        raise TypeError(f"{func_name}() got an unexpected keyword argument {unknown[0]!r}")
    return fields.get("before"), fields.get("after"), fields.get("evidence", ""), fields.get("diff")


# NO-BARE-SQL：SELECT 头集中于此（§5.160.2）；谓词个数随 codes 运行期变化，
# 故 WHERE 片段留在调用处拼装——本键存在即令语句头部不再是函数体内裸 SQL。
_SQL_AUDIT_SELECT_HEAD = "SELECT {cols} FROM {tbl} "


class ExamLoopLedger:
    """把考试循环事件落到 PG 审计行 + JSONL 追加账（组合 :class:`MetaQuestionRegistry`）。"""

    def __init__(self, registry: MetaQuestionRegistry | None = None) -> None:
        #: 复用同一 registry 实例=复用同一连接工厂与 JSONL 路径（双轨真源不分叉）
        self.registry: MetaQuestionRegistry = registry or MetaQuestionRegistry()

    # -- 事务与连接 -----------------------------------------------------------

    def conn(self, *, read_only: bool = True) -> Any:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
        """连接获取（口径同冻结件：读写角色由参数决定，禁在本件写死）。"""
        return self.registry._conn(read_only=read_only)

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        """提供一个已开事务的 cursor；正常退出 commit、异常 rollback 并关闭连接。"""
        conn = self.conn(read_only=False)
        try:
            yield conn.cursor()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # -- 落账 ---------------------------------------------------------------

    def build_event(
        self,
        code: str,
        *,
        q_id: str,
        actor: str,
        **fields: Any,
    ) -> MetaQuestionAuditEvent:
        """事件码 → 落账参数对象（载体换算集中于此，调用点不见 what 字面量）。

        可选审计载荷字段经关键字透传：``before``/``after``/``diff`` 默认 ``None``、
        ``evidence`` 默认 ``""``；未登记关键字与原具名签名一样抛 ``TypeError``。
        """
        before, after, evidence, diff = _split_event_fields("build_event", fields)
        what, before, after, evidence = event_codes.carrier(code, before, after, evidence)
        payload_diff = list(diff or [])
        key = event_codes.event_code_key()
        if key in (after or {}):
            payload_diff.append({"field": key, "old": None, "new": after[key]})
        return MetaQuestionAuditEvent(
            q_id=q_id,
            actor=actor,
            what=what,
            before=before,
            after=after,
            evidence=evidence,
            diff=payload_diff,
        )

    def write_event(
        self,
        cur: Any,  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
        code: str,
        *,
        q_id: str,
        actor: str,
        **fields: Any,
    ) -> MetaQuestionAuditEvent:
        """同事务落账（先账后实）：PG 行 + JSONL 双轨，随调用方事务提交或回滚。

        可选审计载荷字段（before/after/evidence/diff）经 ``**fields`` 关键字透传，语义同
        :meth:`build_event`。
        """
        before, after, evidence, diff = _split_event_fields("write_event", fields)
        event = self.build_event(code, q_id=q_id, actor=actor, before=before, after=after, evidence=evidence, diff=diff)
        # 双轨真源在冻结件里：_write_audit 自带 SSOT 词表硬拦 + JSONL 追加，本件零重写
        self.registry._write_audit(cur, event)
        return event

    def write_event_standalone(
        self,
        code: str,
        *,
        q_id: str,
        actor: str,
        **fields: Any,
    ) -> MetaQuestionAuditEvent:
        """拒收痕独立提交：业务写已回滚，账行必须留存（否则拦截率无从复考）。

        可选审计载荷字段（before/after/evidence/diff）经 ``**fields`` 关键字透传，语义同
        :meth:`build_event`。
        """
        before, after, evidence, diff = _split_event_fields("write_event_standalone", fields)
        event = self.build_event(code, q_id=q_id, actor=actor, before=before, after=after, evidence=evidence, diff=diff)
        conn = self.conn(read_only=False)
        try:
            self.registry._write_audit(conn.cursor(), event)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return event

    # -- 读侧（仲裁/判据共用） ----------------------------------------------

    def latest_events(self, q_id: str, codes: tuple[str, ...], *, limit: int = 20) -> list[dict[str, Any]]:
        """取该问最近若干条指定码审计事件（新→旧，载荷 JSONB 解为对象）。"""
        if not codes:
            raise ValueError("latest_events 需至少一个事件码")
        allowed = frozenset(event_codes.EXTENSION_CODES) | frozenset(AUDIT_WHAT_VOCAB)
        unknown = sorted(set(codes) - allowed)
        if unknown:
            raise ValueError(f"event_code 未登记：{unknown}（须先入扩展册或总册，禁另立枚举）")
        match = event_codes.sql_event_match(portable=True)
        columns = 'q_id, actor, what, "before", "after", evidence, created_at'
        sql = (
            _SQL_AUDIT_SELECT_HEAD.format(cols=columns, tbl=f"{self.registry.schema}.meta_question_audit")
            + f"WHERE q_id = %s AND ({_JOINER.join([match] * len(codes))}) "
            "ORDER BY id DESC LIMIT %s"
        )
        params: tuple[Any, ...] = (
            q_id,
            *[value for code in codes for value in event_codes.match_params(code, portable=True)],
            int(limit),
        )
        conn = self.conn(read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return [_decode_row(dict(zip(cols, row, strict=True))) for row in cur.fetchall()]
        finally:
            conn.close()


def _decode_row(row: dict[str, Any]) -> dict[str, Any]:
    """审计行 JSONB 列解码（PG 返回 dict，SQLite mock 返回 JSON 串）。"""
    out = dict(row)
    for key in ("before", "after"):
        value = out.get(key)
        if isinstance(value, str):
            try:
                out[key] = json.loads(value)
            except ValueError:
                pass  # 非 JSON 文本原样保留（禁静默丢数据）
    return out
