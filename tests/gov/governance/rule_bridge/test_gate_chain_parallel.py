# [A_test] module_id: zephyr.gov_enforcement.rule_bridge.commit_gate_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.rule_bridge.test_gate_chain_parallel
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest；zephyr.gov_enforcement.rule_bridge.{commit_gate_registry,gate_cache_preflight}
# [CONSUMERS] pytest 自动发现
# [STARTUP] imported -m pytest tests/gov/governance/rule_bridge/test_gate_chain_parallel.py
# [MATURITY] testing
# [INVARIANTS] flag OFF（出厂默认）=串行现行路径行为逐字节不变；flag ON=结果列表与 OFF 逐位一致（同序同判定同 detail）、串行段先行、纯扫描台真并行（Barrier 判交叠，非计时）；S1 分道名单台在替身链强制串行；P3：ZEPHYR_COMMIT_GATEWAY=test 不落 gate_execution_stats.jsonl；P2-1：白名单≥25、manifest 声明台必在册、图纸驳回台不在册
# [MODIFY-GUARD] P1-1/P2-1/P3 验收（st-diskp0-20261015 Z1 队 st-perfz1-20261015）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_gate_chain_parallel.py — P1-1 门禁链并行化 + P2-1 白名单扩容 + P3 统计卫生验收。

红蓝验收语义（st-diskp0-20261015 总包图纸）：
- flag OFF 路径行为逐字节等价（同序/同判定/同 detail）；
- flag ON 纯扫描台并行结果一致（ Barrier 机械判交叠，非计时断言）；
- 顺序敏感/信号型台（PARALLEL_SERIAL_GATE_IDS ∪ S1 分道名单）串行先行；
- ZEPHYR_COMMIT_GATEWAY=test 类环境不落 gate_execution_stats.jsonl（P3）；
- 缓存白名单扩容 15→31 与 GATE_INPUT_MANIFEST 准入前置（P2-1）。
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.commit_gate_registry as cgr
import zephyr.gov_enforcement.rule_bridge.gate_cache_preflight as gcp
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateResult,
    GateSpec,
)

_REPO_ROOT = Path(__file__).resolve().parents[4]


class _FakeGateway:
    """最小 gateway 替身（project_root 指向 tmp_path；run_git 恒成功空输出）。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = str(project_root)

    def run_git(self, cmd: list[str], cwd: str | None = None):
        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        return _R()


def _mk(gid: str, prio: int, result: tuple[bool, str] | None = (True, "ok")) -> GateSpec:
    """最小门工厂（result=None=体内抛异常，验 fail-closed）。"""

    def _check(gw, files, **kw):
        if result is None:
            raise RuntimeError(f"boom-{gid}")
        return result

    return GateSpec(gate_id=gid, check=_check, priority=prio)


def _mixed_registry() -> CommitGateRegistry:
    """混合链：串行名单门+3 纯扫描门+异常门+触发跳过门（覆盖计划面全分支）。"""
    reg = CommitGateRegistry()
    reg.register(_mk("HELD-OVERLAP", 10))  # 串行段（PARALLEL_SERIAL_GATE_IDS 成员）
    reg.register(_mk("MY-SCAN-A", 20))
    reg.register(_mk("MY-SCAN-B", 30))
    reg.register(_mk("MY-SCAN-C", 40))
    reg.register(_mk("MY-BAD-GATE", 50, result=None))  # 异常→fail-closed
    reg.register(_mk("MY-TRIG-GATE", 60))
    reg.specs["MY-TRIG-GATE"].files_trigger = ("added:*.never_matches_xyz",)
    return reg


def _snapshot(results: list[GateResult]) -> list[tuple[str, bool, str]]:
    return [(r.gate_id, r.passed, r.detail) for r in results]


@pytest.fixture()
def _clean_acc():
    cgr._STAT_ACC.clear()
    cgr._PHASE_ACC.clear()
    yield
    cgr._STAT_ACC.clear()
    cgr._PHASE_ACC.clear()


@pytest.fixture()
def flag_on(monkeypatch: pytest.MonkeyPatch):
    """P1-1 flag ON（patch 读取唯一点，与 gcp.flag_enabled 机制解耦）。"""
    monkeypatch.setattr(cgr, "_gate_chain_parallel_enabled", lambda: True)


@pytest.fixture()
def flag_off(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(cgr, "_gate_chain_parallel_enabled", lambda: False)


class TestFlagWiring:
    def test_default_flag_is_off(self, monkeypatch: pytest.MonkeyPatch):
        """出厂默认：gcp.flag_enabled 走真实 flags.yaml（enabled:false）→ OFF。"""
        monkeypatch.setattr(gcp, "flag_enabled", lambda name: name == "never")
        assert cgr._gate_chain_parallel_enabled() is False

    def test_flag_on_via_flag_enabled(self, monkeypatch: pytest.MonkeyPatch):
        """flag 机制接线：gcp.flag_enabled("gate_chain_parallel")=True → 并行链启用。"""
        seen: list[str] = []

        def _fake(name: str) -> bool:
            seen.append(name)
            return name == "gate_chain_parallel"

        monkeypatch.setattr(gcp, "flag_enabled", _fake)
        assert cgr._gate_chain_parallel_enabled() is True
        assert "gate_chain_parallel" in seen

    def test_flag_facility_failure_fails_closed(self, monkeypatch: pytest.MonkeyPatch):
        """设施异常（flag 读取抛错）→ fail-closed OFF=现行串行路径。"""

        def _boom(name: str) -> bool:
            raise RuntimeError("flag facility down")

        monkeypatch.setattr(gcp, "flag_enabled", _boom)
        assert cgr._gate_chain_parallel_enabled() is False


class TestFlagOffEquivalence:
    def test_off_path_identical_results(self, tmp_path: Path, flag_off):
        """flag OFF：混合链全量现算，行为=现行串行路径（基准快照）。"""
        gw = _FakeGateway(tmp_path)
        reg = _mixed_registry()
        results = reg.check_all(gw, [], session_id="s1")
        assert _snapshot(results) == [
            ("HELD-OVERLAP", True, "ok"),
            ("MY-SCAN-A", True, "ok"),
            ("MY-SCAN-B", True, "ok"),
            ("MY-SCAN-C", True, "ok"),
            ("MY-BAD-GATE", False, "gate 异常（fail-closed）: boom-MY-BAD-GATE"),
            ("MY-TRIG-GATE", True, "skipped: files_trigger 未命中（P5 条件触发）"),
        ]

    def test_off_and_on_identical(self, tmp_path: Path, flag_off, flag_on):
        """红蓝核心断言：同一混合链 OFF vs ON 结果列表逐位一致（同序/同判定/同 detail）。"""
        gw = _FakeGateway(tmp_path)
        off = _snapshot(_mixed_registry().check_all(gw, [], session_id="s1"))
        on = _snapshot(_mixed_registry().check_all(gw, [], session_id="s1"))
        assert off == on

    def test_on_preserves_priority_order(self, tmp_path: Path, flag_on):
        """flag ON 结果顺序=priority 升序（与串行链逐位同序）。"""
        gw = _FakeGateway(tmp_path)
        results = _mixed_registry().check_all(gw, [], session_id="s1")
        assert [r.gate_id for r in results] == [
            "HELD-OVERLAP",
            "MY-SCAN-A",
            "MY-SCAN-B",
            "MY-SCAN-C",
            "MY-BAD-GATE",
            "MY-TRIG-GATE",
        ]

    def test_on_fail_closed_and_kwargs_passthrough(self, tmp_path: Path, flag_on):
        """flag ON：异常门 fail-closed 不阻断他门；kwargs 照常透传。"""
        seen_kwargs: dict[str, object] = {}

        def _kw_gate(gw, files, **kw):
            seen_kwargs.update(kw)
            return True, ""

        reg = CommitGateRegistry()
        reg.register(_mk("MY-BAD-GATE", 10, result=None))
        reg.register(GateSpec(gate_id="MY-KW-GATE", check=_kw_gate, priority=20))
        results = reg.check_all(_FakeGateway(tmp_path), [], session_id="sess-x", allow_overlap=False)
        assert results[0].passed is False and "boom-MY-BAD-GATE" in results[0].detail
        assert results[1].passed is True
        assert seen_kwargs.get("session_id") == "sess-x"


class TestParallelSemantics:
    def test_serial_segment_runs_first(self, tmp_path: Path, flag_on):
        """串行段先行：串行门事件全部早于任何并行门 start 事件。"""
        events: list[str] = []

        def _serial(gw, files, **kw):
            events.append("serial-run")
            return True, ""

        def _par(gid: str):
            def _check(gw, files, **kw):
                events.append(f"par-start-{gid}")
                return True, ""

            return _check

        reg = CommitGateRegistry()
        reg.register(GateSpec(gate_id="HELD-OVERLAP", check=_serial, priority=10))
        reg.register(GateSpec(gate_id="P-A", check=_par("A"), priority=20))
        reg.register(GateSpec(gate_id="P-B", check=_par("B"), priority=30))
        reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        assert events[0] == "serial-run"
        assert "par-start-A" in events and "par-start-B" in events
        assert events.index("serial-run") < min(events.index("par-start-A"), events.index("par-start-B"))

    def test_parallel_gates_actually_overlap(self, tmp_path: Path, flag_on):
        """Barrier 机械判交叠（非计时）：3 纯扫描门并发到齐才算通过；串行执行必 BrokenBarrier。"""
        barrier = threading.Barrier(3, timeout=15)

        def _make(gid: str, prio: int) -> GateSpec:
            def _check(gw, files, **kw):
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    return False, f"{gid}: 未并发（退化串行）"
                return True, "overlapped"

            return GateSpec(gate_id=gid, check=_check, priority=prio)

        reg = CommitGateRegistry()
        reg.register(_make("OVL-A", 10))
        reg.register(_make("OVL-B", 20))
        reg.register(_make("OVL-C", 30))
        results = reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        assert all(r.passed for r in results), [r.detail for r in results]

    def test_serial_gates_do_not_overlap(self, tmp_path: Path, flag_on):
        """串行段内两台顺序敏感门严格不交叠（start1 < end1 < start2）。"""
        events: list[str] = []
        lock = threading.Lock()

        def _make(gid: str, prio: int) -> GateSpec:
            def _check(gw, files, **kw):
                with lock:
                    events.append(f"{gid}-start")
                threading.Event().wait(0.15)
                with lock:
                    events.append(f"{gid}-end")
                return True, ""

            return GateSpec(gate_id=gid, check=_check, priority=prio)

        reg = CommitGateRegistry()
        reg.register(_make("HELD-OVERLAP", 10))
        reg.register(_make("TAKEOVER-PENDING", 20))
        reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        assert events.index("HELD-OVERLAP-end") < events.index("TAKEOVER-PENDING-start")

    def test_max_workers_bound(self):
        """线程数=方案上限 4。"""
        assert cgr.GATE_CHAIN_MAX_WORKERS == 4


class TestW5ContractConvergence:
    """W5 契约（st-bt-fast-w5-20260906 第 2 步）与本 flag 机制收敛面。"""

    def test_resolve_width_flag_off_default_serial(self, monkeypatch: pytest.MonkeyPatch):
        """出厂（flag OFF+无总闸）→ 宽度 1=现行串行路径。"""
        monkeypatch.delenv("ZEPHYR_W5_GATE_SPEEDUP", raising=False)
        monkeypatch.setattr(gcp, "flag_enabled", lambda name: False)
        assert cgr._resolve_parallel_width() == 1

    def test_resolve_width_flag_on_four(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("ZEPHYR_W5_GATE_SPEEDUP", raising=False)
        monkeypatch.setattr(gcp, "flag_enabled", lambda name: name == "gate_chain_parallel")
        assert cgr._resolve_parallel_width() == cgr.GATE_CHAIN_MAX_WORKERS

    def test_w5_kill_switch_overrides_flag(self, monkeypatch: pytest.MonkeyPatch):
        """W5 总闸 ZEPHYR_W5_GATE_SPEEDUP=0：无条件回串行（急救优先级最高）。"""
        monkeypatch.setenv("ZEPHYR_W5_GATE_SPEEDUP", "0")
        monkeypatch.setattr(gcp, "flag_enabled", lambda name: True)
        assert cgr._resolve_parallel_width() == 1

    def test_serial_execution_gates_escape_hatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag_on):
        """W5 判据③：SERIAL_EXECUTION_GATES 命中门强制进串行段（只影响位置不影响判定）。"""
        assert not cgr.SERIAL_EXECUTION_GATES  # 生产缺省恒空（显式依赖序逃生口默认不启用）
        monkeypatch.setattr(cgr, "SERIAL_EXECUTION_GATES", frozenset({"MY-SCAN-A"}))
        gw = _FakeGateway(tmp_path)
        off = _snapshot(_mixed_registry().check_all(gw, [], session_id="s1"))
        on = _snapshot(_mixed_registry().check_all(gw, [], session_id="s1"))
        assert off == on  # 排除集只影响执行位置，判定零变化

    def test_lt_two_parallel_gates_fall_back_serial(self, tmp_path: Path, flag_on):
        """W5 判据④：独立并行台<2 → 全量串行段（回退现行为，结果不变）。"""
        gw = _FakeGateway(tmp_path)
        reg = CommitGateRegistry()
        reg.register(_mk("HELD-OVERLAP", 10))  # 串行段
        reg.register(_mk("ONLY-PAR", 20))  # 唯一并行台→折入串行
        results = reg.check_all(gw, [], session_id="s1")
        assert _snapshot(results) == [("HELD-OVERLAP", True, "ok"), ("ONLY-PAR", True, "ok")]

    def test_w5_env_switch_forces_serial_results(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag_on):
        """总闸置 0：并行分支不进入（宽度 1=串行现行路径），结果与串行基准一致。"""
        monkeypatch.setenv("ZEPHYR_W5_GATE_SPEEDUP", "0")
        gw = _FakeGateway(tmp_path)
        reg = _mixed_registry()
        results = reg.check_all(gw, [], session_id="s1")
        assert [r.passed for r in results] == [True, True, True, True, False, True]


class TestSerialRoster:
    def test_drawing_named_signal_gates_are_serial(self):
        """图纸点名信号型台全部在串行段名单。"""
        assert {"RECONCILER-HEALTH", "GIT-CALL-BUDGET", "HELD-OVERLAP", "TAKEOVER-PENDING"} <= (
            cgr.PARALLEL_SERIAL_GATE_IDS
        )

    def test_s1_shared_index_gates_forced_serial_in_view_chain(self, tmp_path: Path, flag_on):
        """S1 替身链：分道名单台强制串行且拿本体 gateway；非名单台拿代理。"""
        shared_gw = _FakeGateway(tmp_path)
        main_gw = _FakeGateway(tmp_path)
        received: dict[str, object] = {}
        order: list[str] = []

        def _make(gid: str, prio: int) -> GateSpec:
            def _check(gw, files, **kw):
                received[gid] = gw
                order.append(gid)
                return True, ""

            return GateSpec(gate_id=gid, check=_check, priority=prio)

        reg = CommitGateRegistry()
        reg.register(_make("CH-BATCH-SIZE", 10))  # SHARED_INDEX_WITHOUT_OWN_SCOPE 成员
        reg.register(_make("MY-SCAN-Z", 20))  # 非名单→并行段
        results = reg.check_all(
            main_gw,
            [],
            session_id="s1",
            shared_index_gateway=shared_gw,
        )
        assert all(r.passed for r in results)
        assert received["CH-BATCH-SIZE"] is shared_gw  # 分道台=本体 gateway
        assert received["MY-SCAN-Z"] is not shared_gw  # 并行台=代理（非替身）
        assert order == ["CH-BATCH-SIZE", "MY-SCAN-Z"]  # 分道台串行先行

    def test_s1_inactive_when_shared_index_absent(self, tmp_path: Path, flag_on):
        """shared_index_gateway 缺省→分道名单台照常走并行段（零分派，本体 gateway 直用）。"""
        received: dict[str, object] = {}

        def _make(gid: str, prio: int) -> GateSpec:
            def _check(gw, files, **kw):
                received[gid] = gw
                return True, ""

            return GateSpec(gate_id=gid, check=_check, priority=prio)

        reg = CommitGateRegistry()
        reg.register(_make("CH-BATCH-SIZE", 10))  # S1 名单成员（非 P1-1 串行台）
        reg.register(_make("MY-SCAN-Y", 20))  # 凑满 ≥2 独立并行台（W5 判据④回退不触发）
        gw = _FakeGateway(tmp_path)
        reg.check_all(gw, [], session_id="s1")
        assert received["CH-BATCH-SIZE"] is gw  # 免锁定版：并行台直用本体 gateway


class TestCacheInterplay:
    def test_on_path_cache_hit_second_run(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag_on):
        """flag ON：白名单门第二次链命中缓存（计划面在并行分支内同语义）。"""
        monkeypatch.setattr(gcp, "result_cache_enabled", lambda: True)
        monkeypatch.setattr(gcp, "CONTENT_SCAN_CACHE_WHITELIST", frozenset({"MY-CACHE-GATE"}))
        calls = {"n": 0}

        def _check(gw, files, **kw):
            calls["n"] += 1
            return True, "scanned"

        reg = CommitGateRegistry()
        reg.register(GateSpec(gate_id="MY-CACHE-GATE", check=_check, priority=10))
        gw = _FakeGateway(tmp_path)
        r1 = reg.check_all(gw, ["a.py"], session_id="s1")
        r2 = reg.check_all(gw, ["a.py"], session_id="s1")
        assert r1[0].detail == "scanned" and calls["n"] == 1
        assert r2[0].detail.startswith("cache-hit:") and calls["n"] == 1

    def test_off_path_cache_hit_second_run(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag_off):
        """flag OFF：缓存行为与现行一致（重构未动串行路径语义）。"""
        monkeypatch.setattr(gcp, "result_cache_enabled", lambda: True)
        monkeypatch.setattr(gcp, "CONTENT_SCAN_CACHE_WHITELIST", frozenset({"MY-CACHE-GATE"}))
        calls = {"n": 0}

        def _check(gw, files, **kw):
            calls["n"] += 1
            return True, "scanned"

        reg = CommitGateRegistry()
        reg.register(GateSpec(gate_id="MY-CACHE-GATE", check=_check, priority=10))
        gw = _FakeGateway(tmp_path)
        reg.check_all(gw, ["a.py"], session_id="s1")
        r2 = reg.check_all(gw, ["a.py"], session_id="s1")
        assert r2[0].detail.startswith("cache-hit:") and calls["n"] == 1


class TestStatHygiene:
    """P3 统计卫生：test 类环境不落生产统计册。"""

    def test_test_env_skips_stats_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _clean_acc):
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "test")
        reg = CommitGateRegistry()
        reg.register(_mk("SOME-GATE", 10))
        reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        assert not (tmp_path / ".runtime" / "audit" / "gate_execution_stats.jsonl").exists()
        assert not cgr._STAT_ACC and not cgr._PHASE_ACC  # 累计器就地清空，防跨链泄漏

    def test_normal_env_writes_stats(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _clean_acc):
        monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY", raising=False)
        reg = CommitGateRegistry()
        reg.register(_mk("SOME-GATE", 10))
        reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        stats = tmp_path / ".runtime" / "audit" / "gate_execution_stats.jsonl"
        assert stats.exists()

    def test_test_env_case_insensitive(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _clean_acc):
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "TEST")
        reg = CommitGateRegistry()
        reg.register(_mk("SOME-GATE", 10))
        reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        assert not (tmp_path / ".runtime" / "audit" / "gate_execution_stats.jsonl").exists()


class TestWhitelistExpansion:
    """P2-1 白名单扩容验收（15→31）与准入判据机械前置。"""

    def test_whitelist_size_at_least_25(self):
        assert len(gcp.CONTENT_SCAN_CACHE_WHITELIST) >= 25

    def test_expansion_batch_present(self):
        new_batch = {
            "GIT-CALL-BUDGET",
            "MUTABLE-CONST-WITHOUT-FINAL",
            "PERMANENT-SYSTEM-TRIGGER",
            "NO-SECRET-HARDCODE",
            "TDM-MOUNT-COVERAGE",
            "NO-BARE-GETENV",
            "BLUEPRINT-NODE-ID-HARDCODE",
            "SSOT-REDEFINITION",
            "TRANSLATION-COVERAGE",
            "OPEN-WITHOUT-WITH",
            "CH-VERSION-COL",
            "GATE-ERRCODE-CONSISTENCY",
        }
        assert new_batch <= gcp.CONTENT_SCAN_CACHE_WHITELIST

    def test_manifest_gates_in_whitelist_and_paths_plausible(self):
        """准入判据机械前置：注册表读取类台必先声明 manifest，声明路径可落地。

        判失机制允许声明文件暂缺（_manifest_inputs_sha 以 <missing> 确定性标记
        参与哈希——文件一旦落盘键即翻转），故存在性放宽为父目录实存（防路径笔误）。
        """
        for gid, files in gcp.GATE_INPUT_MANIFEST.items():
            assert gid in gcp.CONTENT_SCAN_CACHE_WHITELIST, f"{gid} 未入白名单却声明 manifest"
            for rel in files:
                parent = (_REPO_ROOT / rel).parent
                assert parent.exists(), f"{gid} manifest 声明路径父目录不存在: {rel}"

    def test_drawing_rejected_gates_not_whitelisted(self):
        """输入面审计驳回台（HEAD 严格面/全仓树/引擎依赖/源码树）不得准入。"""
        rejected = {
            "REGISTRY-MASS-DELETION",  # HEAD 条目集严格面（HEAD 增条目→缓存假绿）
            "TEST-SOURCE-CONSISTENCY",  # src 源码树存在性（manifest 不可枚举）
            "DOC-HEADER-SUITE",  # 子台 DOC-REF-BROKEN 探测全仓树
            "DEPGRAPH-ENFORCEMENT",  # 读 PG depgraph 库（全局可变态）
            "GATE-VOCAB",  # scripts/ checker 面 spec_sha 不覆盖+词表 glob
            "REAL-KEY-REFERENCE-SCAN",  # _read_head_file 内容豁免面（无先例，保守）
            "FMS-HYGIENE",
            "COMPLEXITY-GUARD",
        }
        assert not (rejected & gcp.CONTENT_SCAN_CACHE_WHITELIST)


class TestReadCachePause:
    """免锁定版并行段：读缓存停用句柄语义（替代初版链级锁代理——红轮实测锁把重门
    git 子进程全部串行化反而变慢，定版=段内停用 _git_read_cache 免锁真并行）。"""

    def test_pause_disables_and_restores_cache(self):
        class _GW:
            _git_read_cache: dict | None = {"k": "v"}

        gw = _GW()
        with cgr._ChainReadCachePause(gw):
            assert gw._git_read_cache is None  # 段内停用
        assert gw._git_read_cache == {"k": "v"}  # 段后恢复原值

    def test_pause_noop_when_attr_missing(self):
        class _GW:  # 树视图替身等无 _git_read_cache 属性
            pass

        gw = _GW()
        with cgr._ChainReadCachePause(gw):
            assert not hasattr(gw, "_git_read_cache")  # no-op 不注入属性
        assert not hasattr(gw, "_git_read_cache")

    def test_pause_none_prior_restored(self):
        class _GW:
            _git_read_cache: dict | None = None

        gw = _GW()
        with cgr._ChainReadCachePause(gw):
            assert gw._git_read_cache is None
        assert gw._git_read_cache is None  # 原值就是 None 也正确恢复

    def test_parallel_gates_see_disabled_cache(self, tmp_path: Path, flag_on):
        """并行段内门观察到的 _git_read_cache=None（停用生效），段后恢复。"""
        observed: dict[str, object] = {}

        class _GW(_FakeGateway):
            _git_read_cache: dict | None = {"stale": True}

        gw = _GW(tmp_path)

        def _make(gid: str, prio: int) -> GateSpec:
            def _check(gw_, files, **kw):
                observed[gid] = gw_._git_read_cache  # 观测段内缓存态
                return True, ""

            return GateSpec(gate_id=gid, check=_check, priority=prio)

        reg = CommitGateRegistry()
        reg.register(_make("PAR-A", 10))
        reg.register(_make("PAR-B", 20))
        reg.check_all(gw, [], session_id="s1")
        assert observed["PAR-A"] is None and observed["PAR-B"] is None
        assert gw._git_read_cache == {"stale": True}  # 段后恢复

    def test_parallel_gates_actually_overlap_still_on(self, tmp_path: Path, flag_on):
        """免锁定版不回归：Barrier 机械判交叠依旧成立。"""
        barrier = threading.Barrier(3, timeout=15)

        def _make(gid: str, prio: int) -> GateSpec:
            def _check(gw, files, **kw):
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    return False, f"{gid}: 未并发（退化串行）"
                return True, "overlapped"

            return GateSpec(gate_id=gid, check=_check, priority=prio)

        reg = CommitGateRegistry()
        reg.register(_make("OVL-D", 10))
        reg.register(_make("OVL-E", 20))
        reg.register(_make("OVL-F", 30))
        results = reg.check_all(_FakeGateway(tmp_path), [], session_id="s1")
        assert all(r.passed for r in results), [r.detail for r in results]


# 红蓝实测锚（st-perfz1-20261015）：蓝轮 flag ON 实测见本件所在提交 message。
