"""回魂治理回归（2026-10-03 deadletter-cure 战役）。

病根：V5 register 频率护栏的第三门 ``_is_session_alive(prev, now)`` 在条目**已判死**时
整段跳过护栏 → 走 FULL 分支把 start_time/last_heartbeat/last_activity/last_register_ts
四锚无条件重置为 now。保活循环（实测 c10 keeper：bash while-true + sleep 25 + register）
只需把节拍拉到 > ``_HEARTBEAT_TIMEOUT_SECONDS``(90s)，即可让条目周期性
"死 → 放行 → 续命 → 再死"，实测节拍 ~105s、连续 1202 次、永不判死，呈现
"看起来在干活但没有工作面"的假活方波。

治本：新增 ``SessionRegistry._is_reanimation`` 五元判据，命中时**即使条目已死**也走
降级路径（状态字段照常重建、四时间锚冻结）。
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from zephyr.security.access_control.session_concurrency import (
    _HEARTBEAT_TIMEOUT_SECONDS,
    SessionInfo,
    SessionRegistry,
)

# 会话合理寿命上限（类常量，回魂年龄判据）
_MAX_SESSION_LIFETIME_SECONDS = SessionRegistry._MAX_SESSION_LIFETIME_SECONDS

# 一个远超过会话合理寿命（-8h）且已判死（心跳 -3h）的条目 —— keeper 回魂现场形态。
_OLD = 8 * 3600.0
_STALE_HB = 3 * 3600.0


class TestReanimationGuard:
    """回魂判据（pid / held / task / heartbeat 硬前提 + 投胎次数 或 年龄）。"""

    def test_young_start_time_but_many_reincarnations_is_blocked(self, tmp_path: Path) -> None:
        """核心回归：start_time 被保活循环刷成"年轻"，投胎次数仍须把它钉死。

        这是**纯年龄判据会漏判**的场景（2026-10-03 实测：四只 c10 条目在被判定的
        瞬间 age=0.0h，因为 keeper 刚把 start_time 重置过）。年龄锚可被 register
        自身覆盖 ⇒ 循环论证；reincarnation_count 只在 FULL 自增、降级透传，是保活
        循环自己抹不掉的反证。删掉这条等于把病根放回去。
        """
        reg = SessionRegistry(str(tmp_path))
        sid = "st-fresh-aged-ghost"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - 60.0,  # 故意年轻（不足 6h，年龄判据不成立）
            held_files=[],
            task_files=[],
            last_heartbeat=now - 30.0,  # 心跳也未过期（原 _is_session_alive 判活）
            last_activity=now - 30.0,
            logical=False,
            last_register_ts=now - 30.0,
            reincarnation_count=SessionRegistry._REINCARNATION_LIMIT,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=0, held_files=[], task_files=[])

        assert got.start_time == seed.start_time, "年轻但反复投胎的幽灵未被冻结"
        assert got.last_activity == seed.last_activity
        assert got.last_heartbeat == seed.last_heartbeat

    def test_below_reincarnation_limit_is_allowed(self, tmp_path: Path) -> None:
        """阈值以下（正常会话的合理重启次数）必须放行，宁放不杀。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-under-limit"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - 60.0,
            held_files=[],
            task_files=[],
            last_heartbeat=now - 30.0,
            last_activity=now - 30.0,
            logical=False,
            last_register_ts=now - 4000.0,  # 超窗 → 合法 FULL 放行条件
            reincarnation_count=SessionRegistry._REINCARNATION_LIMIT - 1,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=0, held_files=[], task_files=[])

        assert got.start_time > seed.start_time, "阈值以下的正常会话被误杀"

    def test_undead_keeper_loop_is_downgraded(self, tmp_path: Path) -> None:
        """keeper 回魂现场：老 pid=0 空荷条目被 register → 四锚必须冻结。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-keeper-ghost"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=[],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
            reincarnation_count=7,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=0, held_files=[], task_files=[])

        assert got.start_time == seed.start_time, "start_time 被重置=回魂未堵住"
        assert got.last_heartbeat == seed.last_heartbeat, "last_heartbeat 被续期"
        assert got.last_activity == seed.last_activity, "last_activity 被伪造"
        assert got.last_register_ts == seed.last_register_ts, "频率锚被拖长（护栏失效）"
        # 降级重建不算投胎——沿用既有计数，不得自增也不得清零
        assert got.reincarnation_count == 7

    def test_undead_loop_repeated_100x_never_rejuvenates(self, tmp_path: Path) -> None:
        """连打 100 次（模拟 keeper 通宵）→ 条目必须随时间自然衰老而非保持年轻。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-keeper-loop"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=[],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
        )
        reg._write_own(sid, seed.to_dict())

        for _ in range(100):
            got = reg.register(sid, pid=0, held_files=[], task_files=[])

        assert got.start_time == seed.start_time
        assert (time.time() - got.start_time) > _MAX_SESSION_LIFETIME_SECONDS, (
            "连打 100 次后条目仍被判为年轻——回魂未根治"
        )

    def test_entry_becomes_judgeable_dead_after_freeze(self, tmp_path: Path) -> None:
        """冻结后条目应可判死（活动性锚不再刷新），这是"能收尾"的关键回归。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-keeper-dead"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=[],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
        )
        reg._write_own(sid, seed.to_dict())
        reg.register(sid, pid=0, held_files=[], task_files=[])

        entry = reg._get_entry(sid)
        assert isinstance(entry, dict)
        # 心跳锚停在过去 → 远超时（90s）判活阈 → list_active 会把它算进 expired
        assert (time.time() - float(entry["last_heartbeat"])) > _HEARTBEAT_TIMEOUT_SECONDS


class TestNoFalsePositive:
    """反向：任何一种"在干活"的信号都必须放行，禁止误杀真实会话。"""

    def test_old_entry_with_claim_is_allowed_full(self, tmp_path: Path) -> None:
        """老会话但持 claim（在干活）→ 必须放行 FULL register。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-old-worker"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=["src/a.py"],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=0, held_files=["src/a.py"], task_files=[])

        assert got.start_time > seed.start_time, "持 claim 的老会话被误判回魂"
        assert got.reincarnation_count >= 1

    def test_old_entry_with_task_files_is_allowed_full(self, tmp_path: Path) -> None:
        reg = SessionRegistry(str(tmp_path))
        sid = "st-old-tasker"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=[],
            task_files=["docs/x.md"],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=0, held_files=[], task_files=["docs/x.md"])

        assert got.start_time > seed.start_time

    def test_old_entry_with_fresh_heartbeat_is_allowed_full(self, tmp_path: Path) -> None:
        """心跳守护在岗（heartbeat.jsonl 新鲜）→ 真实工作面，放行。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-old-chief"
        now = time.time()
        hb_dir = tmp_path / ".runtime" / "sessions" / sid
        hb_dir.mkdir(parents=True, exist_ok=True)
        (hb_dir / "heartbeat.jsonl").write_text("{}\n", encoding="utf-8")
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=[],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=0, held_files=[], task_files=[])

        assert got.start_time > seed.start_time, "心跳在岗的老会话被误判回魂"

    def test_old_entry_with_live_pid_is_allowed_full(self, tmp_path: Path) -> None:
        """pid>0 且有真进程 → 一律认为真活（pid 门最优先）。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-old-pidbound"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=1,
            start_time=now - _OLD,
            held_files=[],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
        )
        reg._write_own(sid, seed.to_dict())

        got = reg.register(sid, pid=1, held_files=[], task_files=[])

        assert got.start_time > seed.start_time, "有进程绑定的会话被误判回魂"

    def test_young_session_first_register_counts_zero(self, tmp_path: Path) -> None:
        """新会话（年龄 < 合理寿命）→ 首次 FULL，reincarnation_count 从 0 起。"""
        reg = SessionRegistry(str(tmp_path))
        got = reg.register("st-fresh", pid=0, held_files=[], task_files=[])
        assert got.reincarnation_count == 0

    def test_immediate_reregister_is_downgraded_not_reincarnated(self, tmp_path: Path) -> None:
        """窗内立即重注册 = 降级重建（锚冻结，count 沿用）——不是投胎。

        这是「重注册 ≠ 回魂」的关键区分：同一试剂(immediate)重复 register 属既有
        V5 语义（状态重建），不算重新投胎，故 reincarnation_count 不自增。
        """
        reg = SessionRegistry(str(tmp_path))
        sid = "st-fresh2"
        first = reg.register(sid, pid=0, held_files=[], task_files=[])
        second = reg.register(sid, pid=0, held_files=[], task_files=[])

        assert second.reincarnation_count == first.reincarnation_count == 0
        assert second.last_activity == first.last_activity, "窗内重注册不应续期活性锚"

    def test_reincarnation_count_increments_on_full_reset(self, tmp_path: Path) -> None:
        """超窗（>1860s）后的 FULL 重置 = 一次投胎，计数自增。"""
        reg = SessionRegistry(str(tmp_path))
        sid = "st-reborn"
        first = reg.register(sid, pid=0, held_files=[], task_files=[])
        assert first.reincarnation_count == 0

        # 把 last_register_ts 与心跳锚回拨到窗外，制造"合法 FULL 放行"条件
        entry = reg._get_entry(sid)
        assert isinstance(entry, dict)
        entry["last_register_ts"] = time.time() - 3600.0
        entry["last_heartbeat"] = time.time() - 3600.0
        entry["start_time"] = time.time() - 60.0  # 年轻条目，绕开回魂年龄判据
        reg._write_own(sid, entry)

        second = reg.register(sid, pid=0, held_files=[], task_files=[])
        assert second.reincarnation_count == 1, "FULL 重置应计入投胎次数"


class TestAuditTrail:
    """回魂必须留痕——把下一轮排查从"时间差反推"降为"查表"。"""

    def test_reanimation_writes_audit_jsonl(self, tmp_path: Path) -> None:
        reg = SessionRegistry(str(tmp_path))
        sid = "st-audited-ghost"
        now = time.time()
        seed = SessionInfo(
            session_id=sid,
            pid=0,
            start_time=now - _OLD,
            held_files=[],
            task_files=[],
            last_heartbeat=now - _STALE_HB,
            last_activity=now - _STALE_HB,
            logical=False,
            last_register_ts=now - _STALE_HB,
            reincarnation_count=3,
        )
        reg._write_own(sid, seed.to_dict())

        reg.register(sid, pid=0, held_files=[], task_files=[])

        audit = tmp_path / ".runtime" / "session_registry_audit" / "register_reanimation.jsonl"
        assert audit.exists(), "回魂未留痕（取证基建缺失）"
        rows = [json.loads(ln) for ln in audit.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(rows) >= 1
        rec = rows[-1]
        assert rec["event"] == "register_reanimation_blocked"
        assert rec["session_id"] == sid
        assert rec["anchors_frozen"] is True
        assert rec["reincarnation_count_before"] == 3
        assert rec["evidence"]["entry_pid"] == 0
        assert rec["evidence"]["entry_age_seconds"] > _MAX_SESSION_LIFETIME_SECONDS

    def test_clean_session_writes_no_reanimation_audit(self, tmp_path: Path) -> None:
        reg = SessionRegistry(str(tmp_path))
        reg.register("st-clean", pid=0, held_files=[], task_files=[])
        audit = tmp_path / ".runtime" / "session_registry_audit" / "register_reanimation.jsonl"
        assert not audit.exists(), "干净会话被误记回魂审计"


class TestSessionInfoRoundTrip:
    """新增字段的序列化闭环（分片读写不能丢字段）。"""

    def test_to_dict_from_dict_preserves_reincarnation_count(self) -> None:
        info = SessionInfo(session_id="x", pid=0, start_time=1.0, reincarnation_count=42)
        back = SessionInfo.from_dict(info.to_dict())
        assert back.reincarnation_count == 42

    def test_missing_field_defaults_zero(self) -> None:
        """旧分片无该字段 → 默认 0，不得炸 from_dict。"""
        back = SessionInfo.from_dict({"session_id": "legacy"})
        assert back.reincarnation_count == 0

    def test_null_value_does_not_raise(self) -> None:
        """JSON null 防御（对齐 held_files 的 5.147.9 同型坑）。"""
        back = SessionInfo.from_dict({"session_id": "n", "reincarnation_count": None})
        assert back.reincarnation_count == 0
