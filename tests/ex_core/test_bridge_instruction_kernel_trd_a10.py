# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.test_bridge_instruction_kernel_trd_a10
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.bridge_instruction_kernel; pytest
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 证尺先红后绿：本文件任何一条测试都必须能在"修复前"的协议实现上转红（红证日志=.runtime/tmp/trd_a10_red_before_fix.log）
# [MODIFY-GUARD] TRD-A10 桥客户端两缺陷案卷
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-BIK | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TRD-A10 桥客户端两缺陷复现用例 + 撤单竞态压测（真源判据=17 号文§四）。

禁实盘四禁：全程假文件（tmp_path）+ 假时钟 + 假柜台挂单集 + 假 passorder，
零 socket、零交易通道、零生产 data/ 写入。
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from zephyr.ex_core.bridge_instruction_kernel import (
    ALARM_DUPLICATE_REMARKS,
    ALARM_PHANTOM_REJECTED,
    MARK_DONE,
    MARK_FAIL,
    MARK_SENDING,
    BridgeInstructionRow,
    BridgeProtocolConfig,
    ExecutorState,
    duplicate_remark_violations,
    parse_instruction,
    protocol_alarms,
    run_executor_cycle,
    should_hold_cancel,
    unconfirmed_claims,
)

CFG = BridgeProtocolConfig(sending_timeout_ms=90_000, max_retry=3, phantom_grace_ms=180_000)
_HEADER = "order_id,action,symbol,side,qty,pricetype,price"


class FakeBridgeFile:
    """假指令文件（真源语义=orders_{env}.csv，盘上一份行文本）。"""

    def __init__(self, path: Path, lines: list[str]):
        self._path = path
        self._path.write_text("\n".join(lines) + "\n", encoding="ascii")

    def read(self) -> list[str]:
        text = self._path.read_text(encoding="ascii")
        return [ln for ln in text.splitlines() if ln]

    def commit(self, lines: list[str]) -> None:
        self._path.write_text("\n".join(lines) + "\n", encoding="ascii")

    def raw_lines(self) -> list[str]:
        return self.read()

    def mark_of(self, order_id: str) -> str | None:
        for row_text in self.read():
            row = parse_instruction(row_text)
            if row is not None and row.order_id == order_id:
                return row.mark or "BARE"
        return None


def order_line(oid: str, symbol: str = "510300.SH", qty: int = 100, price: str = "4.50") -> str:
    return f"{oid},order,{symbol},buy,{qty},limit,{price}"


class FakeCounter:
    """假柜台：只认"哪些 remark 真的进了柜台"，以及由此产生的合同数。"""

    def __init__(self, visible: Iterable[str] = ()):
        self.visible = set(visible)
        self.contracts: dict[str, int] = {}

    def record_submit(self, oid: str) -> None:
        self.contracts[oid] = self.contracts.get(oid, 0) + 1

    @property
    def remarks(self) -> set[str]:
        return set(self.visible)

    def duplicates(self) -> dict[str, int]:
        return duplicate_remark_violations(self.contracts)


class TestOvernightSilentDrop:
    """缺陷①：隔夜单静默丢弃（盘外 passorder 不报错→客户端自盖 #DONE）。

    09-23 实测形态：04:45 落单→08:53 客户端重登拾取→本地 #DONE+ack(SENT)→
    09:15 竞价、09:30 开盘后柜台零收录。正解=#DONE 只能由柜台可见性驱动，
    拿不到柜台凭证必须走 #FAIL 显式拒单。
    """

    def test_pre_market_order_never_self_marks_done_and_ends_fail(self, tmp_path: Path) -> None:
        f = FakeBridgeFile(tmp_path / "orders_sim.csv", [_HEADER, order_line("OVN-1")])
        counter = FakeCounter(visible=())  # 柜台永不收录（隔夜单真实形态）
        state = ExecutorState()
        acks: list[str] = []

        def send(row: BridgeInstructionRow) -> bool:
            counter.record_submit(row.order_id)
            return True  # passorder 未抛异常——这正是"静默"的来源

        seen_marks: list[str | None] = []
        now = 1_000
        for _ in range(CFG.max_retry + 2):
            run_executor_cycle(
                read=f.read,
                commit=f.commit,
                counter_remarks=counter.remarks,
                now_ms=now,
                state=state,
                send=send,
                cfg=CFG,
                ack=acks.append,
            )
            seen_marks.append(f.mark_of("OVN-1"))
            now += CFG.sending_timeout_ms

        assert MARK_DONE not in "".join(f.raw_lines()), f"客户端在无柜台凭证时自盖 #DONE：{f.raw_lines()}"
        assert MARK_DONE not in seen_marks, f"任一周期都不得出现 #DONE：{seen_marks}"
        assert f.mark_of("OVN-1") == MARK_FAIL, f"超预算必须显式拒单 #FAIL，实得 {f.mark_of('OVN-1')}"
        assert any("FAIL" in a for a in acks), f"拒单必须落 ack 供脑侧与台账看见：{acks}"

    def test_confirmed_order_reaches_done_only_after_counter_visible(self, tmp_path: Path) -> None:
        f = FakeBridgeFile(tmp_path / "orders_sim.csv", [_HEADER, order_line("OVN-2")])
        counter = FakeCounter(visible=())
        state = ExecutorState()

        def send(row: BridgeInstructionRow) -> bool:
            counter.record_submit(row.order_id)
            return True

        first = run_executor_cycle(
            read=f.read, commit=f.commit, counter_remarks=counter.remarks, now_ms=0, state=state, send=send, cfg=CFG
        )
        assert first.submitted == ("OVN-2",)
        assert f.mark_of("OVN-2") == MARK_SENDING, "已下发但未获柜台凭证=仍挂 #SENDING"

        counter.visible.add("OVN-2")  # 柜台导出跟上
        second = run_executor_cycle(
            read=f.read,
            commit=f.commit,
            counter_remarks=counter.remarks,
            now_ms=3_000,
            state=state,
            send=send,
            cfg=CFG,
        )
        assert second.done == ("OVN-2",)
        assert f.mark_of("OVN-2") == MARK_DONE


class TestStaleSnapshotRace:
    """缺陷②：submit→cancel<5s 竞态触发陈旧快照回写→重复申报（09-22 同 remark 36 张）。

    v16 形态：主线程 handlebar 入口读快照→_mark_sending 另起一次读写→passorder→
    周期末把**入口快照**整文件回写，抹掉后台线程刚落的 #DONE，那行退回裸行，
    下一周期被再次下发。
    """

    def test_concurrent_done_must_not_be_clobbered_by_stale_snapshot(self, tmp_path: Path) -> None:
        f = FakeBridgeFile(tmp_path / "orders_sim.csv", [_HEADER, order_line("RACE-1")])
        counter = FakeCounter(visible=("RACE-1",))
        state = ExecutorState()
        submits: list[str] = []

        def send(row: BridgeInstructionRow) -> bool:
            submits.append(row.order_id)
            counter.record_submit(row.order_id)
            # 并发写手（后台线程）在本周期中途把该行推进为 #DONE 并落盘
            latest = [ln for ln in f.read() if parse_instruction(ln) is not None]
            f.commit([f"{MARK_DONE} {row.body}" if ln.strip() == row.raw.strip() else ln for ln in latest])
            return True

        run_executor_cycle(
            read=f.read, commit=f.commit, counter_remarks=counter.remarks, now_ms=0, state=state, send=send, cfg=CFG
        )
        assert f.mark_of("RACE-1") == MARK_DONE, f"陈旧快照回写抹掉了并发写手的终态：{f.raw_lines()}"

        for step in range(6):
            run_executor_cycle(
                read=f.read,
                commit=f.commit,
                counter_remarks=counter.remarks,
                now_ms=10_000 * (step + 1),
                state=state,
                send=send,
                cfg=CFG,
            )
        assert submits.count("RACE-1") == 1, f"重复申报（同 remark 多张合同）：{submits}"
        assert counter.duplicates() == {}

    def test_bare_line_reappearing_is_not_resent(self, tmp_path: Path) -> None:
        """外部写手把已下发的行改回裸行（人工/回滚事故）也不得二次下发。"""
        f = FakeBridgeFile(tmp_path / "orders_sim.csv", [_HEADER, order_line("RACE-2")])
        counter = FakeCounter()
        state = ExecutorState()
        submits: list[str] = []

        def send(row: BridgeInstructionRow) -> bool:
            submits.append(row.order_id)
            return True

        run_executor_cycle(
            read=f.read, commit=f.commit, counter_remarks=counter.remarks, now_ms=0, state=state, send=send, cfg=CFG
        )
        f.commit([_HEADER, order_line("RACE-2")])  # 行退回裸行
        for step in range(5):
            run_executor_cycle(
                read=f.read,
                commit=f.commit,
                counter_remarks=counter.remarks,
                now_ms=200_000 * (step + 1),
                state=state,
                send=send,
                cfg=CFG,
            )
        assert submits.count("RACE-2") == 1, f"已下发过的 remark 被二次下发：{submits}"


class TestCancelRaceStress100:
    """撤单竞态压测 100 次 0 漏单（17 号文§四 TRD-A10 验收线，假时钟/假 ack/假柜台）。

    两个方向各 100 轮：
      (a) 正常受理腿——submit→cancel<5s（09-22 暴露竞态的真实节奏），要求
          每轮恰好一次下发（零重复合同）+ 两行都落终态（零漏单）；
      (b) 盘外/零收录腿——柜台永不受理（隔夜单真实形态），要求零 #DONE、
          每轮 #FAIL 显式拒单、柜台合同数 0（重试有预算且全部留痕）。
    """

    @staticmethod
    def _run_round(
        tmp_path: Path,
        round_no: int,
        *,
        counter_accepts: bool,
        cadence_ms: int,
        cycles: int,
        cancel_at_step: int | None,
    ) -> dict:
        oid = f"STRESS-{round_no:03d}"
        cid = f"C{oid}"
        f = FakeBridgeFile(tmp_path / f"orders_r{round_no}.csv", [_HEADER, order_line(oid)])
        acknowledged: set[str] = set()  # 柜台已受理过的委托 remark（终态证据源）
        state = ExecutorState()
        acks: list[str] = []
        submits: list[str] = []
        contracts: dict[str, int] = {}

        def send(row: BridgeInstructionRow) -> bool:
            submits.append(row.order_id)
            if row.action == "order":
                if counter_accepts:
                    contracts[row.order_id] = contracts.get(row.order_id, 0) + 1
                return True  # v16 实测：盘外 passorder 同样不抛异常（"静默"的来源）
            # 撤单：目标未上柜台=撤不到，如实返回 False（v16 hit is None 分支）
            return row.target in acknowledged

        now = 0
        for step in range(cycles):
            if cancel_at_step is not None and step == cancel_at_step:
                f.commit([*f.read(), f"{cid},cancel,{oid},,0,,0.0"])
            if counter_accepts and step >= 1:
                acknowledged.add(oid)
            run_executor_cycle(
                read=f.read,
                commit=f.commit,
                counter_remarks=acknowledged,
                now_ms=now,
                state=state,
                send=send,
                cfg=CFG,
                ack=acks.append,
            )
            now += cadence_ms

        marks = {r.order_id: r.mark for r in _rows(f)}
        order_submits = [s for s in submits if s == oid]
        return {
            "oid": oid,
            "cid": cid,
            "marks": marks,
            "order_submits": order_submits,
            "contracts": contracts,
            "acks": acks,
            "file_lines": f.raw_lines(),
        }

    def test_hundred_rounds_cancel_race_zero_duplicate_zero_lost(self, tmp_path: Path) -> None:
        bad_submit_count: dict[str, int] = {}
        lost: list[str] = []
        for round_no in range(100):
            r = self._run_round(
                tmp_path,
                round_no,
                counter_accepts=True,
                cadence_ms=5_000,  # submit→cancel<5s 的真实节奏，远小于超时预算
                cycles=8,
                cancel_at_step=1,
            )
            if len(r["order_submits"]) != 1:
                bad_submit_count[r["oid"]] = len(r["order_submits"])
            if r["marks"].get(r["oid"]) != MARK_DONE:
                lost.append(f"{r['oid']}={r['marks'].get(r['oid'])}")
            if r["marks"].get(r["cid"]) != MARK_DONE:
                lost.append(f"{r['cid']}={r['marks'].get(r['cid'])}")
        assert bad_submit_count == {}, f"撤单竞态引发重复申报：{bad_submit_count}"
        assert lost == [], f"存在未落终态的漏单：{lost}"

    def test_hundred_rounds_silent_drop_never_self_marks_done(self, tmp_path: Path) -> None:
        done_any: list[str] = []
        not_failed: list[str] = []
        contracts_total = 0
        for round_no in range(100):
            r = self._run_round(
                tmp_path,
                round_no,
                counter_accepts=False,  # 柜台零收录（隔夜单真实形态）
                cadence_ms=CFG.sending_timeout_ms,
                cycles=CFG.max_retry + 2,
                cancel_at_step=None,
            )
            contracts_total += sum(r["contracts"].values())
            if r["marks"].get(r["oid"]) == MARK_DONE:
                done_any.append(r["oid"])
            if r["marks"].get(r["oid"]) != MARK_FAIL:
                not_failed.append(f"{r['oid']}={r['marks'].get(r['oid'])}")
        assert done_any == [], f"零柜台凭证却自盖 #DONE：{done_any}"
        assert not_failed == [], f"未走显式拒单终态：{not_failed}"
        assert contracts_total == 0

    def test_every_dropped_round_leaves_fail_ack(self, tmp_path: Path) -> None:
        missing: list[str] = []
        for round_no in range(100):
            r = self._run_round(
                tmp_path,
                round_no,
                counter_accepts=False,
                cadence_ms=CFG.sending_timeout_ms,
                cycles=CFG.max_retry + 2,
                cancel_at_step=None,
            )
            if not any(",FAIL," in a for a in r["acks"]):
                missing.append(r["oid"])
        assert missing == [], f"拒单未落 ack（脑侧与台账看不见）：{missing}"


def _rows(f: FakeBridgeFile) -> list[BridgeInstructionRow]:
    from zephyr.ex_core.bridge_instruction_kernel import parse_instructions

    return parse_instructions(f.read())


class TestKernelDecisionHelpers:
    """协议判定纯函数（脑侧与沙箱共用同一张表）。"""

    def test_phantom_claim_after_grace_is_flagged(self) -> None:
        out = unconfirmed_claims(
            {"R-1": 1_000, "R-2": 1_000},
            counter_remarks=["R-2"],
            terminal_oids=(),
            now_ms=1_000 + CFG.phantom_grace_ms,
            mirror_fresh=True,
            cfg=CFG,
        )
        assert out == ("R-1",)

    def test_stale_mirror_disables_phantom_judgement(self) -> None:
        out = unconfirmed_claims(
            {"R-1": 0},
            counter_remarks=(),
            terminal_oids=(),
            now_ms=10**9,
            mirror_fresh=False,
            cfg=CFG,
        )
        assert out == (), "柜台导出停摆期间禁判幽灵单（不误杀活单）"

    def test_terminal_order_exits_phantom_watch(self) -> None:
        out = unconfirmed_claims(
            {"R-1": 0},
            counter_remarks=(),
            terminal_oids=("R-1",),
            now_ms=10**9,
            mirror_fresh=True,
            cfg=CFG,
        )
        assert out == ()

    def test_duplicate_remark_alarm_threshold(self) -> None:
        assert duplicate_remark_violations({"A": 1, "B": 36}) == {"B": 36}

    def test_cancel_held_only_before_counter_and_only_inside_window(self) -> None:
        assert should_hold_cancel(counter_confirmed=False, age_ms=0, cfg=CFG) is True
        assert should_hold_cancel(counter_confirmed=False, age_ms=CFG.cancel_confirm_wait_ms, cfg=CFG) is False
        assert should_hold_cancel(counter_confirmed=True, age_ms=0, cfg=CFG) is False

    def test_parse_instruction_marks_and_body(self) -> None:
        row = parse_instruction(f"{MARK_SENDING} T1,order,510300.SH,buy,100,limit,4.50")
        assert row is not None
        assert (row.mark, row.order_id, row.action) == (MARK_SENDING, "T1", "order")
        assert row.body == "T1,order,510300.SH,buy,100,limit,4.50"
        assert parse_instruction(_HEADER) is None
        assert parse_instruction("") is None


class TestSilentDropAlarmSurface:
    """丢弃/重复申报的"必须有人看见"面（LANE-BUILD2 补口 2026-09-26）。

    为什么要有这一类：缺陷①的治法把静默丢弃转成了显式 #FAIL/REJECTED，
    但"转成显式"只到日志为止的话，下次换个值班人照样静默——判据要求的是
    零静默，那就得有一个不依赖人翻日志的消费面（健康/告警侧读得到的一张表）。
    本类锁的是这张表的**语义边界**：既不漏报（既成事实必亮），也不误报
    （在途声称不算事故，否则天天狼来了=真出事没人看）。
    """

    def test_clean_state_raises_no_alarm(self) -> None:
        assert protocol_alarms(duplicate_remarks={}, phantom_rejected_total=0) == ()

    def test_duplicate_contracts_raise_alarm(self) -> None:
        out = protocol_alarms(duplicate_remarks={"R-1": 36}, phantom_rejected_total=0)
        assert out == (ALARM_DUPLICATE_REMARKS,)

    def test_confirmed_silent_drop_raises_alarm(self) -> None:
        out = protocol_alarms(duplicate_remarks={}, phantom_rejected_total=1)
        assert out == (ALARM_PHANTOM_REJECTED,)

    def test_single_contract_is_not_duplicate(self) -> None:
        assert protocol_alarms(duplicate_remarks={"R-1": 1}, phantom_rejected_total=0) == ()

    def test_both_defects_report_together(self) -> None:
        out = protocol_alarms(duplicate_remarks={"R-1": 2}, phantom_rejected_total=3)
        assert set(out) == {ALARM_DUPLICATE_REMARKS, ALARM_PHANTOM_REJECTED}

    def test_grace_period_claims_never_alarm(self) -> None:
        """判定期内的"客户端声称已发"是正常在途态，不得进零容忍告警面。

        红证口径：本例锁的是 unconfirmed_claims（在途观察）与 protocol_alarms
        （既成事故）之间的墙——若有人图省事把 unconfirmed_count 也接进告警表，
        每笔正常下单都会亮灯，两周后这条告警就废了。
        """
        claims = {f"R-{i}": 0 for i in range(20)}
        in_flight = unconfirmed_claims(
            claims,
            counter_remarks=(),
            terminal_oids=(),
            now_ms=1_000,  # 判定期内
            mirror_fresh=True,
            cfg=CFG,
        )
        assert in_flight == ()
        assert protocol_alarms(duplicate_remarks={}, phantom_rejected_total=0) == ()
