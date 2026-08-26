# [BLUEPRINT] MOD-INF-075 | docs/03_modules/_domain_infrastructure_runtime/shared_memory_zero_copy/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-075 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_shared_memory_zero_copy
# [TESTS] src/zephyr/infra_runtime/shared_memory_zero_copy.py
"""MOD-INF-075 单元测试：shared_memory_zero_copy 共享内存零拷贝通道。

蓝图验收（B10-01807/CAND-H1FS-008，A1交易决策架构 §29.1）：
create/attach/write/read/detach/free 生命周期状态机 + 命名空间隔离
（前缀校验）+ 超限降级（注入 fallback 回调 + downgraded 标记）。
真实 shared_memory 小 buffer（<1MB）验证读写一致性；命名空间按 pid+序号
隔离避免段名冲突，每个用例终态全量 free。
"""

from __future__ import annotations

import itertools
import os

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.shared_memory_zero_copy",
    reason="shared_memory_zero_copy not importable",
)

from zephyr.infra_runtime.shared_memory_zero_copy import (  # noqa: E402
    ChannelState,
    ZeroCopyChannelManager,
    ZeroCopyError,
)

_COUNTER = itertools.count()


@pytest.fixture()
def mgr():
    """每用例独立命名空间管理器，终态全量 free 防段泄漏。"""
    m = ZeroCopyChannelManager(
        namespace=f"zatest_{os.getpid()}_{next(_COUNTER)}",
        size_threshold=4096,
        clock=lambda: 1000.0,
    )
    yield m
    for full in m.channel_names():
        short = full.split("/", 1)[1]
        if m.info(short).state is not ChannelState.FREED:
            m.free(short)


# ──────────────────────────────────────────────────────────────────────────────
# 构造与命名空间校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_namespace_raises(self) -> None:
        with pytest.raises(ZeroCopyError):
            ZeroCopyChannelManager(namespace="", size_threshold=1024)

    def test_namespace_with_slash_raises(self) -> None:
        with pytest.raises(ZeroCopyError):
            ZeroCopyChannelManager(namespace="a/b", size_threshold=1024)

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ZeroCopyError):
            ZeroCopyChannelManager(namespace="ns", size_threshold=0)
        with pytest.raises(ZeroCopyError):
            ZeroCopyChannelManager(namespace="ns", size_threshold=-5)


# ──────────────────────────────────────────────────────────────────────────────
# 生命周期：create/attach/detach/free
# ──────────────────────────────────────────────────────────────────────────────


class TestLifecycle:
    def test_create_returns_info(self, mgr) -> None:
        info = mgr.create("factors", 1024)
        assert info.name.endswith("/factors")
        assert info.size == 1024
        assert info.state is ChannelState.CREATED
        assert info.downgraded is False
        assert info.created_at == 1000.0

    def test_create_duplicate_raises(self, mgr) -> None:
        mgr.create("dup", 128)
        with pytest.raises(ZeroCopyError):
            mgr.create("dup", 128)

    def test_create_invalid_name_raises(self, mgr) -> None:
        with pytest.raises(ZeroCopyError):
            mgr.create("", 128)
        with pytest.raises(ZeroCopyError):
            mgr.create("a/b", 128)

    def test_create_invalid_size_raises(self, mgr) -> None:
        with pytest.raises(ZeroCopyError):
            mgr.create("s0", 0)
        with pytest.raises(ZeroCopyError):
            mgr.create("sneg", -1)

    def test_attach_detach_roundtrip(self, mgr) -> None:
        mgr.create("ch", 256)
        assert mgr.attach("ch").state is ChannelState.ATTACHED
        assert mgr.attach("ch").state is ChannelState.ATTACHED  # 幂等
        assert mgr.detach("ch").state is ChannelState.DETACHED
        assert mgr.detach("ch").state is ChannelState.DETACHED  # 幂等
        assert mgr.attach("ch").state is ChannelState.ATTACHED  # 重开句柄

    def test_free_then_ops_raise(self, mgr) -> None:
        mgr.create("gone", 128)
        mgr.free("gone")
        assert mgr.info("gone").state is ChannelState.FREED
        with pytest.raises(ZeroCopyError):
            mgr.free("gone")  # 重复 free
        with pytest.raises(ZeroCopyError):
            mgr.write("gone", b"x")
        with pytest.raises(ZeroCopyError):
            mgr.read("gone")
        with pytest.raises(ZeroCopyError):
            mgr.attach("gone")
        with pytest.raises(ZeroCopyError):
            mgr.detach("gone")

    def test_unknown_channel_raises(self, mgr) -> None:
        with pytest.raises(ZeroCopyError):
            mgr.info("ghost")
        with pytest.raises(ZeroCopyError):
            mgr.attach("ghost")
        with pytest.raises(ZeroCopyError):
            mgr.write("ghost", b"x")
        with pytest.raises(ZeroCopyError):
            mgr.free("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 读写一致性（真实小 buffer）
# ──────────────────────────────────────────────────────────────────────────────


class TestReadWrite:
    def test_write_read_roundtrip(self, mgr) -> None:
        mgr.create("rw", 256)
        payload = b"\x01\x02\x03" * 10
        mgr.write("rw", payload)
        assert mgr.read("rw", len(payload)) == payload

    def test_write_with_offset(self, mgr) -> None:
        mgr.create("off", 16)
        mgr.write("off", b"abcd", offset=4)
        assert mgr.read("off", 4, offset=4) == b"abcd"
        assert mgr.read("off", 4, offset=0) == b"\x00" * 4  # 其余保持零

    def test_read_full_default(self, mgr) -> None:
        mgr.create("full", 8)
        mgr.write("full", b"12345678")
        assert mgr.read("full") == b"12345678"

    def test_read_after_reattach(self, mgr) -> None:
        mgr.create("persist", 64)
        mgr.write("persist", b"factor-values")
        mgr.detach("persist")
        mgr.attach("persist")
        assert mgr.read("persist", 13) == b"factor-values"

    def test_io_on_detached_raises(self, mgr) -> None:
        mgr.create("det", 64)
        mgr.detach("det")
        with pytest.raises(ZeroCopyError):
            mgr.write("det", b"x")
        with pytest.raises(ZeroCopyError):
            mgr.read("det")

    def test_write_overflow_raises(self, mgr) -> None:
        mgr.create("ovf", 8)
        with pytest.raises(ZeroCopyError):
            mgr.write("ovf", b"123456789")
        with pytest.raises(ZeroCopyError):
            mgr.write("ovf", b"12", offset=7)
        with pytest.raises(ZeroCopyError):
            mgr.write("ovf", b"x", offset=-1)

    def test_read_overflow_raises(self, mgr) -> None:
        mgr.create("rovf", 8)
        with pytest.raises(ZeroCopyError):
            mgr.read("rovf", 9)
        with pytest.raises(ZeroCopyError):
            mgr.read("rovf", 2, offset=7)
        with pytest.raises(ZeroCopyError):
            mgr.read("rovf", -1)


# ──────────────────────────────────────────────────────────────────────────────
# 超限降级（fallback 注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestDowngrade:
    def test_oversize_create_downgraded(self, mgr) -> None:
        info = mgr.create("big", 4097)  # > threshold=4096
        assert info.downgraded is True
        assert info.state is ChannelState.CREATED

    def test_threshold_boundary_not_downgraded(self, mgr) -> None:
        assert mgr.create("edge", 4096).downgraded is False

    def test_downgraded_readwrite_via_fallback(self, mgr) -> None:
        received: list[tuple[str, bytes]] = []
        m = ZeroCopyChannelManager(
            namespace=f"zatest_{os.getpid()}_{next(_COUNTER)}",
            size_threshold=16,
            fallback=lambda name, data: received.append((name, data)),
            clock=lambda: 1000.0,
        )
        m.create("dg", 32)
        m.write("dg", b"hello-downgrade")
        assert m.read("dg", 15) == b"hello-downgrade"
        assert received == [(m.info("dg").name, b"hello-downgrade")]
        m.free("dg")

    def test_downgraded_overflow_still_raises(self, mgr) -> None:
        mgr.create("dgovf", 8192)
        with pytest.raises(ZeroCopyError):
            mgr.write("dgovf", b"x" * 8193)


# ──────────────────────────────────────────────────────────────────────────────
# 查询与确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestQueryDeterminism:
    def test_channel_names_sorted(self, mgr) -> None:
        mgr.create("b", 64)
        mgr.create("a", 64)
        mgr.create("c", 64)
        names = mgr.channel_names()
        assert names == tuple(sorted(names))
        assert len(names) == 3

    def test_namespace_isolation_between_managers(self, mgr) -> None:
        other = ZeroCopyChannelManager(
            namespace=f"zatest_{os.getpid()}_{next(_COUNTER)}",
            size_threshold=4096,
            clock=lambda: 1000.0,
        )
        mgr.create("shared_name", 64)
        with pytest.raises(ZeroCopyError):
            other.info("shared_name")  # 命名空间隔离互不可见

    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple[bytes, tuple[str, ...], bool]:
            m = ZeroCopyChannelManager(
                namespace=f"zadet_{os.getpid()}_{next(_COUNTER)}",
                size_threshold=4096,
                clock=lambda: 7.0,
            )
            m.create("x", 32)
            m.write("x", b"deterministic")
            out = (m.read("x", 13), m.channel_names(), m.info("x").downgraded)
            m.free("x")
            return out

        r1 = _run()
        r2 = _run()
        assert r1[0] == r2[0]  # 载荷一致
        assert r1[1][0].split("/", 1)[1] == r2[1][0].split("/", 1)[1]  # 短名一致
        assert r1[2] == r2[2]
