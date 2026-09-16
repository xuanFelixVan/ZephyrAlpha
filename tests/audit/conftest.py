# [A_test] module_id: MOD-INF-033_conftest | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §（test-support conftest）
# [MODULE] tests.audit.conftest
# [INVARIANTS] 逐用例边界后事件循环策略槽位无未关闭 loop; 已关闭残留槽位清空; 收割失败不掩盖用例结果
# [CONSUMERS] pytest（tests/audit 全目录自动生效）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 清理异常一律吞掉（保收失败绝不掩盖用例结果）
# [TESTS] pytest tests/audit -q -W error::pytest.PytestUnraisableExceptionWarning（连跑 4 轮 0 失败）
# [TTL] task_bound

"""tests/audit 事件循环泄漏治本 conftest（GW9 测试基建稳定化 st-stab-20260916）。

背景（F-06 通宵班实测）：tests/audit 循环检查每轮恒 1 个顺序依赖伪失败，
受害者随机，签名 = PytestUnraisableExceptionWarning: BaseEventLoop.__del__
（未关闭事件循环 GC 落点随机）+ 1 次共享 state cap 污染。

根因（gc 强制收割 + referrer 持链实证）：本目录 5 个 @pytest.mark.asyncio 用例
（test_detector_dispatcher 3 个 + test_detector_dispatcher_drain 2 个）每个
teardown 后都会在全局 event loop policy 槽位残留 1 条【未关闭】的
ProactorEventLoop（pytest-asyncio 0.26 finalizer 链 _provide_clean_event_loop /
_restore_event_loop_policy 与 Python 3.12 get_event_loop 自动创建语义交互的
副产品；referrer = {'_set_called': True, '_loop': <ProactorEventLoop closed=False>}，
创建栈落在 pytest fixture teardown 帧）。这些 loop+socketpair trio 被自动分代
GC 在随机时点回收 → BaseEventLoop.__del__ 发 ResourceWarning →
pytest unraisable 收集 → 全局 filterwarnings=["error"] 把警告升级为错误 →
GC 落点处的无辜用例（随机受害者）失败。

治本（本文件，制造者侧 fixture 级 teardown 保收，受害者零改动）：每个用例
协议结束后检查 policy 槽位，对残留未关闭 loop 显式 close 并清空槽位——
泄漏在产生点即被回收，不再等待随机 GC。
"""

from __future__ import annotations

import asyncio

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """用例协议结束后保收 policy 槽位中的事件循环。"""
    yield
    try:
        policy = asyncio.get_event_loop_policy()
        local = getattr(policy, "_local", None)
        loop = getattr(local, "_loop", None)
        if loop is not None:
            try:
                if not loop.is_closed() and not loop.is_running():
                    loop.close()
            except Exception:  # noqa: BLE001 — 收割失败绝不掩盖用例结果
                pass
        # 清空槽位：已关闭/外部 loop 不残留为"当前 loop"，
        # 后续 asyncio.get_event_loop() 走 3.12 自动创建语义拿全新 loop
        asyncio.set_event_loop(None)
    except Exception:  # noqa: BLE001
        pass
