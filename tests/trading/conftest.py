# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

治本(gc-leak-finalizer, 2026-08-02): 修复原实现的 ProactorEventLoop 泄漏。
原实现调用 ``policy.get_event_loop()`` 保存 "旧 loop"——但 Python 3.12 下无 current
loop 时该调用会**创建**新 ProactorEventLoop 并返回，该 throwaway loop 在 finally 中
仅被 ``set_event_loop`` 恢复而从**不关闭**。其 ``__del__`` 触发 "unclosed event loop"
+ 2 个 self-pipe socket ResourceWarning，被 ``filterwarnings=["error"]`` 升级为测试
error（ExceptionGroup），并因 loop 残留在全局 policy 中污染后续非 trading 测试
（如 test_p3_integration_smoke / test_gct_006）。修复两点：
  1. ``@pytest.mark.asyncio`` 测试跳过——pytest-asyncio 自管 loop，本 fixture 干预
     会导致两个 loop 管理器冲突（原泄漏的直接触发点）。
  2. sync 测试禁用 ``get_event_loop()``（避免创建 throwaway loop），改用
     ``new_event_loop()`` + finally 显式 ``close()`` + ``set_event_loop(None)``。
"""

from __future__ import annotations

import asyncio

import pytest


@pytest.fixture(autouse=True)
def _isolate_event_loop(request):
    """每个测试获得独立 event loop，避免跨测试 event loop 污染.

    - ``@pytest.mark.asyncio`` 测试：由 pytest-asyncio 管理 loop，本 fixture 不干预
      （干预会导致 loop 冲突 + ProactorEventLoop 泄漏，见模块 docstring）。
    - sync 测试：创建全新 loop 并 set 为当前，测试后关闭并清空 current loop。
    """
    # asyncio 测试由 pytest-asyncio 管理 loop，不干预
    if request.node.get_closest_marker("asyncio") is not None:
        yield
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        if not loop.is_closed():
            loop.close()
        # 清空 current loop（不恢复 throwaway，不残留泄漏的 loop）
        asyncio.set_event_loop(None)
