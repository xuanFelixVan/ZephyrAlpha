# [BLUEPRINT] MOD-GOV_CREATE_GUARD | tests/gov_enforcement/test_create_guard_lookup_singleton.py | §create-guard-lookup-singleton
# [MODULE] tests.gov_enforcement.test_create_guard_lookup_singleton
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.create_guard, zephyr.governance.capability_lookup
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] S4-C 红证（手术簿 s4_c_p90_cache.md）：R-C1 复用断言——registry 与扫描根未变时连续两次 _build_capability_lookup 必须 scan_disk_headers 计数=1 且返回同实例（现码每次全量构造计数=2，必红）；R-C2 失效判别——touch registry（mtime_ns 变）必重建、touch 无关文件仍复用、分片变体（只变一片概⏐另一片 parse 计数不增）；差分矩阵——env kill-switch 一键回退、失效设施异常 fail-safe 回退每次新构造、双线程同抢构造锁收敛单次、预热与 commit 竞争不双建、解析失败不缓存；测试隔离——全部 tmp_path+monkeypatch（REGISTRY_YAML/SCAN_ROOTS/REPO_ROOT/两级缓存），禁跑全库扫描
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""test_create_guard_lookup_singleton.py — S4-C：CREATE-GUARD p90 缓存尾红证。

病根（手术簿 s4_c_p90_cache.md §1-2）：CREATE-GUARD 门级 p90=55.3s（reused=0 结构性）——
有新建 .py 的 commit 每次 ``_build_capability_lookup()`` 全量构造（实测 ~86-109s/实例）。

覆盖（对应手术簿 §4 红测两针 + §5 差分矩阵）：
  R-C1  test_rc1_reuse_same_instance_single_scan —— 复用断言（实现前必红）；
  R-C2  test_rc2_registry_mtime_change_rebuilds —— registry mtime 变→重建；
        test_rc2_unrelated_touch_still_reuses —— 无关文件 touch→仍复用；
        test_rc2_shard_isolation —— 只变一片概要→另一片不重扫（分片重扫计数=1）；
  矩阵  kill-switch 回退 / 失效设施异常 fail-safe / 双线程锁收敛 / 预热不双建 /
        解析失败不缓存 / 测试隔离（缓存清零）。

纪律：不改任何既有测试/阈值/skip；全部 tmp_path 隔离；禁写主仓 .runtime。
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import zephyr.governance.capability_lookup as cl  # noqa: E402
from zephyr.gov_enforcement.commit_gates import create_guard as cg  # noqa: E402

_MINI_REGISTRY = """
capabilities:
  - capability_id: __s4c_mini_cap
    description: "S4-C 单例红证在册能力（tmp 注册表）"
    aliases: []
    canonical_override: src_a/mod_a.py
creation_tokens: []
"""


class _ScanCounter:
    """scan/parse 计数器（monkeypatch 包装既有方法，不替换语义）。"""

    def __init__(self) -> None:
        self.scan_calls = 0
        self.parse_by_root: dict[str, int] = {"src_a": 0, "src_b": 0}


@pytest.fixture()
def s4c_env(monkeypatch, tmp_path):
    """单例环境隔离：REGISTRY_YAML/SCAN_ROOTS/REPO_ROOT 指向 tmp；两级缓存清零。"""
    reg = tmp_path / "registry.yaml"
    reg.write_text(_MINI_REGISTRY, encoding="utf-8")
    root_a = tmp_path / "src_a"
    root_b = tmp_path / "src_b"
    root_a.mkdir()
    root_b.mkdir()
    (root_a / "mod_a.py").write_text("# [MODULE] tests.s4c.mod_a\n", encoding="utf-8")
    (root_b / "mod_b.py").write_text("# [MODULE] tests.s4c.mod_b\n", encoding="utf-8")
    monkeypatch.setattr(cl, "REGISTRY_YAML", reg)
    monkeypatch.setattr(cl, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(cl, "SCAN_ROOTS", [root_a, root_b])
    # raising=False：红证阶段符号尚未实现（S4-C 实现前），fixture 不抢在断言前报错
    monkeypatch.setattr(cl, "_DISK_HEADER_SHARD_CACHE", {}, raising=False)
    monkeypatch.setattr(cg, "_LOOKUP_SINGLETON_CACHE", {}, raising=False)
    monkeypatch.delenv(getattr(cg, "_LOOKUP_SINGLETON_ENV", "ZEPHYR_CG_LOOKUP_SINGLETON"), raising=False)
    return SimpleNamespace(reg=reg, root_a=root_a, root_b=root_b, tmp=tmp_path)


def _install_counters(monkeypatch) -> _ScanCounter:
    counter = _ScanCounter()
    orig_scan = cl.CapabilityLookup.scan_disk_headers
    orig_parse = cl.CapabilityLookup.parse_header

    def counting_scan(self):
        counter.scan_calls += 1
        return orig_scan(self)

    def counting_parse(cls, py, rel):
        top = Path(rel).parts[0] if Path(rel).parts else ""
        if top in counter.parse_by_root:
            counter.parse_by_root[top] += 1
        return orig_parse(py, rel)

    monkeypatch.setattr(cl.CapabilityLookup, "scan_disk_headers", counting_scan)
    monkeypatch.setattr(cl.CapabilityLookup, "parse_header", counting_parse)
    return counter


# ---------------------------------------------------------------- R-C1


class TestRC1Reuse:
    """R-C1 复用断言：registry 与扫描根未变 → 第二次调用返回同实例且不再扫描。"""

    def test_rc1_reuse_same_instance_single_scan(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        first = cg._build_capability_lookup()
        second = cg._build_capability_lookup()
        assert second is first, "失效键未变必须复用同一实例（进程级单例）"
        assert counter.scan_calls == 1, (
            f"两次 _build_capability_lookup 只允许一次全量扫描（现码每次构造=2）: {counter.scan_calls}"
        )


# ---------------------------------------------------------------- R-C2


class TestRC2Invalidation:
    """R-C2 失效判别：registry mtime 变→重建；无关 touch→复用；分片隔离。"""

    def test_rc2_registry_mtime_change_rebuilds(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        first = cg._build_capability_lookup()
        # touch registry：mtime_ns 前移 1ns（NTFS 100ns 精度内可辨）
        st = s4c_env.reg.stat()
        os.utime(s4c_env.reg, ns=(st.st_atime_ns, st.st_mtime_ns + 100))
        second = cg._build_capability_lookup()
        assert second is not first, "registry mtime_ns 变化必须重建（陈旧册=漏拦第二真源）"
        assert counter.scan_calls == 2, f"重建必须真实重构造（计数=2）: {counter.scan_calls}"

    def test_rc2_unrelated_touch_still_reuses(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        first = cg._build_capability_lookup()
        # 无关文件（非 registry、非扫描根内 .py）
        unrelated = s4c_env.tmp / "unrelated.txt"
        unrelated.write_text("noise", encoding="utf-8")
        os.utime(unrelated)
        second = cg._build_capability_lookup()
        assert second is first, "无关文件变化不得作废单例"
        assert counter.scan_calls == 1, f"复用路径不得重扫: {counter.scan_calls}"

    def test_rc2_shard_isolation_only_changed_root_rescanned(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        cg._build_capability_lookup()
        base_a = counter.parse_by_root["src_a"]
        # 只变 src_b 片概要：新增 .py 文件
        (s4c_env.root_b / "mod_b2.py").write_text("# [MODULE] tests.s4c.mod_b2\n", encoding="utf-8")
        cg._build_capability_lookup()
        assert counter.parse_by_root["src_a"] == base_a, "src 片概要未变不得重扫（分片隔离）"
        assert counter.parse_by_root["src_b"] > 0, "src_b 片概要变化必须重扫该片"


# ---------------------------------------------------------------- 差分矩阵


class TestDifferentialMatrix:
    """手术簿 §5 差分矩阵抽样：kill-switch / fail-safe / 锁收敛 / 预热 / 撕读。"""

    def test_env_kill_switch_falls_back_to_fresh_construction(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        monkeypatch.setenv(cg._LOOKUP_SINGLETON_ENV, "0")
        first = cg._build_capability_lookup()
        second = cg._build_capability_lookup()
        assert second is not first, "kill-switch=0 必须回退每次新构造（现行为）"
        assert counter.scan_calls == 2

    def test_invalidation_facility_failure_failsafe_no_cache(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        monkeypatch.setattr(cl, "scan_root_summary", lambda root: None)
        first = cg._build_capability_lookup()
        second = cg._build_capability_lookup()
        assert second is not first, "概要设施失效→键不可得→回退每次新构造（fail-safe）"
        assert counter.scan_calls == 2, "fail-safe 路径不得缓存半失效实例"

    def test_registry_parse_failure_not_cached(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        cg._build_capability_lookup()
        good = s4c_env.reg.read_text(encoding="utf-8")
        s4c_env.reg.write_text("capabilities: [broken", encoding="utf-8")
        with pytest.raises(Exception):
            cg._build_capability_lookup()
        s4c_env.reg.write_text(good, encoding="utf-8")
        rebuilt = cg._build_capability_lookup()
        assert rebuilt is not None, "解析恢复后必须能重建（失败不缓存）"
        assert counter.scan_calls == 2

    def test_concurrent_double_build_converges_single_scan(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        barrier = threading.Barrier(2)
        results: list[object] = []
        errors: list[BaseException] = []

        def _worker() -> None:
            try:
                barrier.wait(timeout=10)
                results.append(cg._build_capability_lookup())
            except BaseException as exc:  # noqa: BLE001 — 测试收集线程异常
                errors.append(exc)

        threads = [threading.Thread(target=_worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60)
        assert not errors, f"并发构造不得异常: {errors}"
        assert len(results) == 2 and results[0] is results[1], "双线程同抢必须收敛同一实例"
        assert counter.scan_calls == 1, f"锁收敛后只允许一次全量扫描: {counter.scan_calls}"

    def test_warmup_rebuilds_stale_cache_without_double_build(self, s4c_env, monkeypatch) -> None:
        counter = _install_counters(monkeypatch)
        cg._build_capability_lookup()
        st = s4c_env.reg.stat()
        os.utime(s4c_env.reg, ns=(st.st_atime_ns, st.st_mtime_ns + 100))
        cg.warm_capability_lookup_async()
        # 预热是后台 daemon——轮询等待其收敛（上限 10s）
        import time

        deadline = time.monotonic() + 10.0
        entry = None
        while time.monotonic() < deadline:
            entry = cg._LOOKUP_SINGLETON_CACHE.get("entry")
            if entry is not None and entry[1] is not None:
                key_now = cg._lookup_invalidation_key()
                if key_now is not None and entry[0] == key_now:
                    break
            time.sleep(0.05)
        assert entry is not None, "预热必须重建陈旧缓存"
        assert counter.scan_calls == 2, f"预热重建恰好一次扫描: {counter.scan_calls}"
        # 预热完成后主线程构造必须直接命中（不双建）
        warm_instance = cg._build_capability_lookup()
        assert warm_instance is entry[1], "预热后主路径必须命中预热实例（不双建）"
        assert counter.scan_calls == 2, "命中预热实例不得再次扫描"

    def test_singleton_does_not_leak_across_tests(self, s4c_env, monkeypatch) -> None:
        """pytest 隔离：fixture 清零两级缓存后必须冷建（矩阵 11）。"""
        counter = _install_counters(monkeypatch)
        cg._build_capability_lookup()
        assert counter.scan_calls == 1, "缓存清零后首次调用必须真实构造"
