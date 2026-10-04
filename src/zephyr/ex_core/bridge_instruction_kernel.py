# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.bridge_instruction_kernel
# create-guard-not-dup: ex_core 桥指令内核（TRD-A10 指令桥接面），非 strategy_retirement_evaluator 第二实现——命中词=共用 cycle report 措辞
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib: dataclasses, pathlib, typing
# [CONSUMERS] zephyr.ex_core.adapters.qmt_file_bridge_broker（脑侧幽灵单/重复合同判定）; 沙箱哑执行器 ZEPHYR_EXEC（写侧周期，patch spec 见 TRD-A10 案卷）; tests/ex_core/test_bridge_instruction_kernel_trd_a10.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] #DONE 只能由"柜台挂单可见性"驱动（客户端自标 SENT 不是终态证据）; 指令文件回写=按 order_id 逐行改写的读-合并-替换，禁整文件旧快照回写（陈旧快照回写会抹掉并发写手的 #DONE 造成重复申报）; 单条指令每周期至多下发一次（重试走显式计数且有上限，超限转 #FAIL）; 幽灵单判定要求柜台导出新鲜（导出停摆期间禁判，fail-soft 不误杀活单）
# [MODIFY-GUARD] TRD-A10 桥客户端两缺陷案卷 docs/_working/decision_map_campaign_20260924/links/L07_exec/trd_a10_bridge_client_defects.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 不抛异常——返回 CycleReport/判定结果，拒单与告警语义由调用方决定
# [TESTS] tests/ex_core/test_bridge_instruction_kernel_trd_a10.py
# [A_module] module_id=MOD-L06-001-BIK | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT 文件桥指令协议内核（TRD-A10 两缺陷的共用真源）。

大白话：本项目下单不直连券商，而是往一个 CSV 里写"指令行"，QMT 沙箱里的
哑执行器读这些行去真下单，读完在行首盖章（#SENDING→#DONE/#FAIL）。本模块把
"盖章规则"从两边（沙箱写侧 / 大脑读侧）抽成一份，谁都不许自己另写一套。

为什么存在（TRD-A10，2026-09-25 LANE-BUILD 施工）：
  缺陷①隔夜单静默丢弃——执行器在盘外调 passorder 不报错，于是它给自己盖了
    #DONE 并 ack(SENT)，但柜台从未收录该委托；大脑只看得到"已发送"，订单永远
    停在 SUBMITTED = 自以为成交的裸奔。正解=**#DONE 只由柜台可见性驱动**，
    拿不到柜台凭证的单必须走 #FAIL 显式拒单。
  缺陷②submit→cancel 竞态重提交——执行器后台线程与主线程各自持有一份文件快照，
    主线程处理完把**旧快照整文件回写**，抹掉线程刚写的 #DONE，那一行退回裸行，
    下一周期被再次下发（09-22 实测同 remark 36 张合同）。正解=**读-合并-替换**
    （只按 order_id 改写目标行，写前重读）+ 单周期单次下发 + 重试上限。

真源边界：本模块只做协议决策，不碰 socket/柜台 API/线程——沙箱侧可整段搬运，
脑侧由 QmtFileBridgeBroker 委托，两处共用同一张状态转移表（禁第二真源）。

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/bridge_instruction_kernel.yaml
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

MARK_SENDING: Final = "#SENDING"
MARK_DONE: Final = "#DONE"
MARK_FAIL: Final = "#FAIL"
_ALL_MARKS: Final = (MARK_SENDING, MARK_DONE, MARK_FAIL)
_HEADER_PREFIX: Final = "order_id"

#: 行标号单调序：只许升不许降（并发写手互不抹终态的判据）
_MARK_RANK: Final[dict[str, int]] = {"": 0, MARK_SENDING: 1, MARK_DONE: 2, MARK_FAIL: 2}

#: 指令行动作列取值（与 QmtFileBridgeBroker.FileBridgeInstruction 同口径）
ACTION_ORDER: Final = "order"
ACTION_CANCEL: Final = "cancel"


@dataclass(frozen=True)
class BridgeProtocolConfig:
    """协议时限（毫秒）——沙箱与大脑共用同一套，调参只改这里。"""

    sending_timeout_ms: int = 90_000
    """#SENDING 挂账超时（超时=回滚重试或转 #FAIL），默认 90s≈30 tick×3s。"""

    max_retry: int = 3
    """同一指令允许的重下发上限，超限转 #FAIL（缺陷①的落点：拒单化）。"""

    phantom_grace_ms: int = 180_000
    """客户端声称已发（ack SENT / #DONE）但柜台零收录的判定期。"""

    counter_export_stale_ms: int = 60_000
    """柜台官方导出超龄阈值：超过即"看不见柜台"，此期间禁判幽灵单。"""

    cancel_confirm_wait_ms: int = 20_000
    """未获柜台凭证前，撤单指令最早下发等待窗（竞态触发面收窄）。"""


DEFAULT_PROTOCOL: Final = BridgeProtocolConfig()


@dataclass(frozen=True)
class BridgeInstructionRow:
    """一条指令行的解析视图。

    命名注记：与 ghost_order_sentinel.InstructionRow 同源（后者=已葬内核只读副本），
    本件为复活内核的正名（CLASS-UNIQUENESS ARCH-034 消撞号），语义一致非第二实现。
    """

    order_id: str
    action: str
    body: str
    mark: str = ""
    raw: str = ""
    target: str = ""
    """撤单行的目标 remark（action=cancel 时=柜台配对键），下单行为空。"""

    @property
    def is_claimed(self) -> bool:
        """已被执行器盖章（#SENDING/#DONE/#FAIL）=非裸行。"""
        return bool(self.mark)

    @property
    def is_terminal_mark(self) -> bool:
        return self.mark in (MARK_DONE, MARK_FAIL)


def parse_instruction(raw: str) -> BridgeInstructionRow | None:
    """解析一行指令文本（表头/空行/不可解析返回 None）。"""
    line = raw.strip()
    if not line or line.startswith(_HEADER_PREFIX):
        return None
    mark = ""
    for candidate in _ALL_MARKS:
        if line.startswith(candidate):
            mark = candidate
            line = line[len(candidate) :].strip()
            break
    fields = [f.strip() for f in line.split(",")]
    if len(fields) < 2 or not fields[0]:
        return None
    return BridgeInstructionRow(
        order_id=fields[0],
        action=fields[1],
        body=line,
        mark=mark,
        raw=raw,
        target=fields[2] if fields[1] == ACTION_CANCEL and len(fields) > 2 else "",
    )


def is_counter_confirmed(row: BridgeInstructionRow, counter_remarks: Iterable[str]) -> bool:
    """下单行的终态证据：本 remark 出现在"柜台已受理委托"集合里（唯一口径）。

    撤单行不走此判据——撤单指令永远不会成为柜台挂单 remark（v16 用同一把尺量两种
    行，于是撤单行必然卡到超时重发=09-23 实测"撤单重发"根因）。撤单行的终态证据是
    ``send`` 端口返回真值（柜台 cancel 调用成功并回 CANCEL_SENT ack），故在
    :func:`run_executor_cycle` 的下发分支里就地落 #DONE。
    """
    return row.order_id in set(counter_remarks)


def parse_instructions(lines: Iterable[str]) -> list[BridgeInstructionRow]:
    return [row for row in (parse_instruction(l) for l in lines) if row is not None]


@dataclass
class ExecutorState:
    """执行器跨周期记忆（重入/重启安全：判定不依赖内存，只依赖文件行态）。"""

    claimed_since_ms: dict[str, int] = field(default_factory=dict)
    retry_count: dict[str, int] = field(default_factory=dict)
    sent_oids: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class CycleReport:
    """一个执行周期的产出（测试断言与沙箱诊断打印共用）。"""

    submitted: tuple[str, ...] = ()
    done: tuple[str, ...] = ()
    failed: tuple[str, ...] = ()
    acks: tuple[str, ...] = ()
    skipped: tuple[str, ...] = ()

    def count(self, name: str) -> int:
        return len(getattr(self, name))


@dataclass(frozen=True)
class _Transition:
    order_id: str
    mark: str
    body: str


@dataclass(frozen=True)
class _ExecutorCycleOpts:
    """run_executor_cycle 的参数对象（NO-LONG-PARAM-LIST：8 参>7 收敛为冻结 dataclass 载体，
    对外关键字契约零变化——见 ``run_executor_cycle`` **kwargs 外壳）。"""

    read: Callable[[], list[str]]
    """读整个指令文件的行列表（沙箱里=open().read().splitlines()）。"""
    commit: Callable[[list[str]], None]
    """回写整个指令文件。"""
    counter_remarks: Iterable[str]
    """柜台当前挂单的投资备注集合（**终态唯一证据源**）。"""
    now_ms: int
    """注入时钟（毫秒），禁本地墙钟直取（m46：一律注入时钟或 now_utc）。"""
    state: ExecutorState
    """跨周期记忆（认领时刻/重试计数）。"""
    send: Callable[[BridgeInstructionRow], bool]
    """下发一笔指令，True=调用未抛异常（**不等于柜台受理**）。"""
    cfg: BridgeProtocolConfig = DEFAULT_PROTOCOL
    ack: Callable[[str], None] | None = None


@dataclass
class _CycleAccum:
    """单周期累计器（transitions/acks/四态 id 列表 + ack 出口），替代原闭包可变捕获。"""

    ack_sink: Callable[[str], None] | None = None

    transitions: list[_Transition] = field(default_factory=list)
    acks: list[str] = field(default_factory=list)
    submitted: list[str] = field(default_factory=list)
    done: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def emit(self, text: str) -> None:
        """回执行写出（ack_{env}.csv 追加）；无 ack 端口时只进周期报告。"""
        self.acks.append(text)
        if self.ack_sink is not None:
            self.ack_sink(text)

    def record(self, order_id: str, mark: str, body: str) -> None:
        """登记一条行改写（合并回写段消费）。"""
        self.transitions.append(_Transition(order_id, mark, body))


def _clear_claim(state: ExecutorState, order_id: str) -> None:
    """终态落定后清空该单的认领/重试/已发记忆（终态行下周期直接跳过）。"""
    state.claimed_since_ms.pop(order_id, None)
    state.retry_count.pop(order_id, None)
    state.sent_oids.discard(order_id)


def _disk_rank(read: Callable[[], list[str]], order_id: str) -> int:
    """写前重读盘上该行当前标号阶（并发写手已落终态=本周期不再下发）。"""
    rank = 0
    for candidate in parse_instructions(read()):
        if candidate.order_id == order_id:
            rank = _MARK_RANK.get(candidate.mark, 0)
            break
    return rank


def _advance_sending_row(
    row: BridgeInstructionRow, opts: _ExecutorCycleOpts, remarks: set[str], acc: _CycleAccum
) -> None:
    """#SENDING 行推进：柜台可见→#DONE；认领计时；超时预算内等待；超限重发/转 #FAIL。"""
    state = opts.state
    if is_counter_confirmed(row, remarks):
        # 终态推进唯一条件：柜台看得见这张委托（缺陷①治点）
        acc.record(row.order_id, MARK_DONE, row.body)
        acc.done.append(row.order_id)
        _clear_claim(state, row.order_id)
        return
    first_seen = state.claimed_since_ms.get(row.order_id)
    if first_seen is None:
        state.claimed_since_ms[row.order_id] = opts.now_ms
        return
    if opts.now_ms - first_seen < opts.cfg.sending_timeout_ms:
        return
    retries = state.retry_count.get(row.order_id, 0) + 1
    state.retry_count[row.order_id] = retries
    if retries >= opts.cfg.max_retry:
        acc.record(row.order_id, MARK_FAIL, row.body)
        acc.emit(f"{row.order_id},FAIL,counter_no_record_after_{retries}_attempts")
        acc.failed.append(row.order_id)
        _clear_claim(state, row.order_id)
    else:
        state.claimed_since_ms[row.order_id] = opts.now_ms
        acc.emit(f"{row.order_id},RETRY,attempt={retries}")
        if _disk_rank(opts.read, row.order_id) < _MARK_RANK[MARK_DONE] and opts.send(row):
            acc.submitted.append(row.order_id)


def _dispatch_bare_row(row: BridgeInstructionRow, opts: _ExecutorCycleOpts, acc: _CycleAccum) -> None:
    """裸行处理：抢占认领（已下发过的 oid 绝不因快照陈旧被再下发=缺陷②治点）→下发→
    撤单就地落 #DONE（撤单终态证据=柜台 cancel 调用成功）。"""
    state = opts.state
    if row.order_id in state.sent_oids:
        acc.skipped.append(row.order_id)
        return
    if _disk_rank(opts.read, row.order_id) >= _MARK_RANK[MARK_DONE]:
        # 盘上已被并发写手推到终态=本周期不重复下发
        state.sent_oids.add(row.order_id)
        acc.skipped.append(row.order_id)
        return
    state.sent_oids.add(row.order_id)
    acc.record(row.order_id, MARK_SENDING, row.body)
    state.claimed_since_ms[row.order_id] = opts.now_ms
    if opts.send(row):
        acc.submitted.append(row.order_id)
        if row.action == ACTION_CANCEL:
            # 撤单行的终态证据=柜台 cancel 调用成功（回 CANCEL_SENT），
            # 不等挂单集可见性——目标单撤成后 remark 本就会离开活跃挂单。
            acc.record(row.order_id, MARK_DONE, row.body)
            acc.done.append(row.order_id)
            _clear_claim(state, row.order_id)
            acc.emit(f"{row.order_id},CANCEL_SENT,{row.target}")
        else:
            acc.emit(f"{row.order_id},SENT,{row.body}")
    # send 返回 False（下发调用被拒/撤单目标未到）=仍挂 #SENDING，由超时预算
    # 统一裁决：未到上限下轮重试，到上限转 #FAIL——绝不静默回到裸行。


def _run_executor_cycle(opts: _ExecutorCycleOpts) -> CycleReport:
    """周期骨架：读→逐行三态分派→（有改写才）读-合并-替换回写→报告。"""
    lines = opts.read()
    remarks = set(opts.counter_remarks)
    acc = _CycleAccum(ack_sink=opts.ack)
    for row in parse_instructions(lines):
        if row.mark in (MARK_DONE, MARK_FAIL):
            continue
        if row.mark == MARK_SENDING:
            _advance_sending_row(row, opts, remarks, acc)
            continue
        _dispatch_bare_row(row, opts, acc)

    if acc.transitions:
        opts.commit(_merge_transitions(opts.read(), acc.transitions))
    return CycleReport(
        submitted=tuple(acc.submitted),
        done=tuple(acc.done),
        failed=tuple(acc.failed),
        acks=tuple(acc.acks),
        skipped=tuple(acc.skipped),
    )


def run_executor_cycle(**kwargs: Any) -> CycleReport:
    """执行器一个轮询周期：读指令文件→下发/盖章→回写（沙箱与压测共用）。

    NO-LONG-PARAM-LIST 治理（cx/params 修面 2026-09-30）：原 8 个 keyword-only 参数
    收敛为 **kwargs 外壳 + 冻结参数对象 :class:`_ExecutorCycleOpts`——调用方关键字名
    与默认值零变化，仅签名形态收敛。

    Keyword Args:
        read: 读整个指令文件的行列表（沙箱里=open().read().splitlines()）。
        commit: 回写整个指令文件。
        counter_remarks: 柜台当前挂单的投资备注集合（**终态唯一证据源**）。
        now_ms: 注入时钟（毫秒），禁本地墙钟直取（m46：一律注入时钟或 now_utc）。
        state: 跨周期记忆（认领时刻/重试计数）。
        send: 下发一笔指令，True=调用未抛异常（**不等于柜台受理**）。
        cfg: 协议时限（缺省=DEFAULT_PROTOCOL）。
        ack: 回执行写出（ack_{env}.csv 追加；缺省=None=只进报告）。
    """
    opts = _ExecutorCycleOpts(
        read=kwargs["read"],
        commit=kwargs["commit"],
        counter_remarks=kwargs["counter_remarks"],
        now_ms=kwargs["now_ms"],
        state=kwargs["state"],
        send=kwargs["send"],
        cfg=kwargs.get("cfg", DEFAULT_PROTOCOL),
        ack=kwargs.get("ack"),
    )
    return _run_executor_cycle(opts)


def _merge_transitions(latest: Sequence[str], transitions: Sequence[_Transition]) -> list[str]:
    """读-合并-替换：只改写目标 order_id 所在行，其余行保留盘上现状。

    缺陷②治点（两条不变量）：
      1. **禁整文件旧快照回写**——合并基准是写前重读的盘上内容，不是周期入口快照；
         入口快照整文件回写会抹掉并发写手刚落的 #DONE，那行退回裸行被再次下发
         （09-22 实测同 remark 36 张合同）。
      2. **终态单调不回退**——行标号只升不降（裸行 < #SENDING < #DONE/#FAIL）；
         本周期记录的 #SENDING 认领若撞上并发写手已落的 #DONE，保留 #DONE。
    """
    by_oid = {t.order_id: t for t in transitions}
    out: list[str] = []
    for raw in latest:
        row = parse_instruction(raw)
        if row is None or row.order_id not in by_oid:
            out.append(raw)
            continue
        t = by_oid.pop(row.order_id)
        if _MARK_RANK.get(t.mark, 0) < _MARK_RANK.get(row.mark, 0):
            out.append(raw)  # 盘上已是更高阶终态，不降级改写
            continue
        out.append(f"{t.mark} {t.body}" if t.mark else t.body)
    # 盘上已消失的目标行（被别的写手改走/归档）=不复活，符合"终态不可回退"
    return out


def claim_lines(lines: Sequence[str], order_id: str) -> list[BridgeInstructionRow]:
    """同一 order_id 的全部指令行（重复合同/重复下发取证用）。"""
    return [row for row in parse_instructions(lines) if row.order_id == order_id]


def unconfirmed_claims(
    claims: Mapping[str, int],
    *,
    counter_remarks: Iterable[str],
    terminal_oids: Iterable[str],
    now_ms: int,
    mirror_fresh: bool,
    cfg: BridgeProtocolConfig = DEFAULT_PROTOCOL,
) -> tuple[str, ...]:
    """脑侧幽灵单判定：客户端声称已发、柜台零收录、且已过判定期。

    Args:
        claims: remark(=指令 order_id 列) -> 首次声称时刻(ms)。
        counter_remarks: 柜台挂单备注集合（命中=正常在途，非幽灵）。
        terminal_oids: 本地已终态（FILLED/CANCELLED/REJECTED）的 remark。
        mirror_fresh: 柜台官方导出是否在时限内（停摆时禁判，防误杀活单）。
    Returns:
        应转 REJECTED 的 remark 元组（超期且无柜台凭证）。
    """
    if not mirror_fresh:
        return ()
    visible = set(counter_remarks) | set(terminal_oids)
    return tuple(
        oid for oid, first_ms in claims.items() if oid not in visible and now_ms - first_ms >= cfg.phantom_grace_ms
    )


def duplicate_remark_violations(remark_counts: Mapping[str, int], *, max_allowed: int = 1) -> dict[str, int]:
    """同 remark 合同数>上限=重复申报（缺陷②的柜台侧显形），供告警消费。"""
    return {remark: n for remark, n in remark_counts.items() if n > max_allowed}


def should_hold_cancel(
    *,
    counter_confirmed: bool,
    age_ms: int,
    cfg: BridgeProtocolConfig = DEFAULT_PROTOCOL,
) -> bool:
    """未获柜台凭证时的撤单暂缓判据（把 submit→cancel<5s 竞态触发面关在窗外）。

    只延不拒：超过 cancel_confirm_wait_ms 仍无凭证即放行撤单——撤单是风控动作，
    宁可多发一次无害撤单，也不许把活单留在柜台上撤不掉。
    """
    return not counter_confirmed and age_ms < cfg.cancel_confirm_wait_ms


ALARM_DUPLICATE_REMARKS: Final = "duplicate_remark_contracts"
ALARM_PHANTOM_REJECTED: Final = "phantom_rejected_present"


def protocol_alarms(
    *,
    duplicate_remarks: Mapping[str, int],
    phantom_rejected_total: int,
) -> tuple[str, ...]:
    """TRD-A10 两缺陷的"必须有人看见"信号表（零容忍面，供健康/告警侧消费）。

    为什么只列这两类既成事实：判定期内的"客户端声称已发"是正常在途态
    （每笔单下单后都会短暂出现），把它算告警等于天天误报——告警疲劳后真出事反而
    没人看，等于把静默丢弃换个地方继续静默。所以：
      - ``ALARM_DUPLICATE_REMARKS``：同 remark 多张合同（09-22 实测 36 张）＝重复申报已发生；
      - ``ALARM_PHANTOM_REJECTED``：兜底机制**确实拒掉过**一张"客户端说已发、柜台零收录"
        的单（09-23 隔夜单形态）＝丢弃已被拦成显式拒单，但"被拦住"不等于"没发生"，
        当日发生过就必须留痕在监控面上，不许随日志滚掉。
    纯函数、零副作用，沙箱侧与脑侧共用同一张表。
    """
    out: list[str] = []
    if any(count > 1 for count in duplicate_remarks.values()):
        out.append(ALARM_DUPLICATE_REMARKS)
    if phantom_rejected_total > 0:
        out.append(ALARM_PHANTOM_REJECTED)
    return tuple(out)


__all__: Final[list[str]] = [
    "ACTION_CANCEL",
    "ACTION_ORDER",
    "ALARM_DUPLICATE_REMARKS",
    "ALARM_PHANTOM_REJECTED",
    "BridgeProtocolConfig",
    "CycleReport",
    "DEFAULT_PROTOCOL",
    "ExecutorState",
    "BridgeInstructionRow",
    "MARK_DONE",
    "MARK_FAIL",
    "MARK_SENDING",
    "claim_lines",
    "duplicate_remark_violations",
    "is_counter_confirmed",
    "parse_instruction",
    "parse_instructions",
    "protocol_alarms",
    "run_executor_cycle",
    "should_hold_cancel",
    "unconfirmed_claims",
]


def atomic_write_lines(path: Path, lines: Sequence[str]) -> None:
    """原子落盘（临时文件 + os.replace）——指令文件的写侧唯一姿势。"""
    import os
    import tempfile

    text = "\n".join(lines) + ("\n" if lines else "")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="ascii", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError:
        try:
            Path(tmp).unlink()
        except OSError:
            pass
        raise
