# [A_test] module_id: MOD-TEST-APISERVER-GUARD-ORDER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L08-001 | src/zephyr/frontend/dashboard/api_server.py §AI 层接线批路由 §main 守卫序
# [MODULE] governance.test_api_server_route_guard_order
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] pytest; stdlib(pathlib)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_api_server_route_guard_order.py
# [MATURITY] testing
# [TTL] task_bound
# [INVARIANTS] C10 守卫顺序回归尺（静态源序断言，零导入零副作用）：
#   AI 层四条路由（budget-advisories/schedulegate-queue/schedulegate-skeletons/schedulegate-confirm）
#   的定义必须位于 `if __name__ == "__main__"` 守卫之前——病史：路由段曾被追加在守卫之后，
#   模块导入态（uvicorn module:app）正常，但直跑模式 `python api_server.py` 在 main() 内
#   uvicorn.run 阻塞，守卫后的路由定义永不执行=直跑模式四条路由静默消失。
"""C10 回归尺：api_server 路由段必须在 __main__ 守卫之前定义（直跑模式可达）。"""

from pathlib import Path

API_SERVER = Path(__file__).resolve().parents[2] / "src" / "zephyr" / "frontend" / "dashboard" / "api_server.py"

ROUTE_BLOCK_HEADER = "# ── AI 层接线批路由"
ROUTE_MARKERS = (
    '@app.get("/api/budget-advisories")',
    '@app.get("/api/schedulegate-queue")',
    '@app.get("/api/schedulegate-skeletons")',
    '@app.post("/api/schedulegate-confirm")',
)
GUARD_MARKER = 'if __name__ == "__main__":'


def _source() -> str:
    return API_SERVER.read_text(encoding="utf-8")


def test_route_block_defined_before_main_guard():
    src = _source()
    guard_pos = src.index(GUARD_MARKER)
    assert ROUTE_BLOCK_HEADER in src, "AI 层接线批路由段头注释消失（被移动/改名？）"
    assert src.index(ROUTE_BLOCK_HEADER) < guard_pos, "路由段回退到 __main__ 守卫之后（C10 病灶复发）"
    for marker in ROUTE_MARKERS:
        assert marker in src, f"路由标记消失: {marker}"
        assert src.index(marker) < guard_pos, f"路由回退到守卫之后（C10 病灶复发）: {marker}"


def test_main_guard_tail_still_invokes_main():
    src = _source()
    tail = src[src.index(GUARD_MARKER) :]
    assert "main()" in tail, "守卫体必须仍调用 main()（直跑入口不得失联）"
