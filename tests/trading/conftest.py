# [A_test] module_id: SRC-TST-TRADING-CONFTEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.conftest
# [INVARIANTS] 每个测试获得独立 event loop，避免跨测试 event loop 污染
# [MODIFY-GUARD] none
# [CONSUMERS] pytest tests/trading/
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent
"""trading 测试共享 fixture——event loop 隔离.

治本(2026-07-20): trading 测试中部分文件（test_admission_controller.py 等）使用
``asyncio.get_event_loop().run_until_complete(...)`` 手动调用 async 代码，而非使用
pytest-asyncio 的 ``@pytest.mark.asyncio`` 装饰器。当其他测试文件（如 extreme/）关闭
event loop 后，``get_event_loop()`` 返回已关闭的 loop，导致 "Event loop is closed" 错误。

本 conftest 通过 autouse fixture 在每个测试前创建新 event loop 并设为当前 loop，
测试后关闭，确保跨文件测试隔离。
"""

from __future__ import annotations

import asyncio

import pytest


@pytest.fixture(autouse=True)
def _isolate_event_loop():
    """每个测试获得独立 event loop，避免跨测试 event loop 污染.

    治本(2026-07-20): 每个测试前创建全新 event loop 并 set 为当前 loop，
    测试后关闭。确保 ``asyncio.get_event_loop()`` 始终返回可用的 loop。
    """
    # 保存旧 loop（若有）以便恢复
    policy = asyncio.get_event_loop_policy()
    old_loop = policy.get_event_loop()

    # 创建全新 loop
    loop = asyncio.new_event_loop()
    policy.set_event_loop(loop)

    try:
        yield loop
    finally:
        # 关闭本测试的 loop
        if not loop.is_closed():
            loop.close()
        # 恢复旧 loop（若存在且未关闭），否则设为 None 让下次创建新的
        if old_loop is not None and not old_loop.is_closed():
            policy.set_event_loop(old_loop)
