# [A_test] module_id: SRC-TST-N2GUARD | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-N2GUARD | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.frontend.test_api_server_main_guard_order
# [DOMAIN] D_FRONTEND
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-N2GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_api_server_main_guard_order.py — N2 红蓝哨兵：__main__ 守卫必须位于全部路由注册之后

病根（N2，2026-09-29）：api_server.py 的 ``if __name__ == "__main__": main()`` 曾位于
AI 层接线批路由（budget/schedulegate 五路由）之前——脚本直跑模式（``python api_server.py``）
main() 在路由装饰器执行前启动 uvicorn ⇒ 五路由永不注册（budget/schedulegate 页恒 404）。
模块导入路径不受影响（装饰器 import 时执行、__main__ 块跳过），故只在脚本直跑显形。

判定：源序静态断言（不起端口、不依赖导入副作用）——
- R-N2-1（红/绿哨兵）：每个 ``@app.get/post/...`` 装饰器行号都必须早于 __main__ 守卫行号；
- R-N2-2：守卫存在性（防有人顺手删掉入口）。

测试隔离：纯文本扫描本仓 src 文件，零导入被测模块、零网络、tmp 无关。
"""

from __future__ import annotations

import re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_API_SERVER = _PROJECT_ROOT / "src" / "zephyr" / "frontend" / "dashboard" / "api_server.py"

_ROUTE_RE = re.compile(r'^@app\.(get|post|put|delete|patch)\("', re.M)
_GUARD_RE = re.compile(r'^if __name__ == "__main__":', re.M)


def test_r_n2_1_all_route_decorators_precede_main_guard() -> None:
    """R-N2-1：全部路由装饰器必须早于 __main__ 守卫（脚本直跑模式路由注册完整性）。"""
    text = _API_SERVER.read_text(encoding="utf-8")
    routes = [m.start() for m in _ROUTE_RE.finditer(text)]
    assert routes, "api_server.py 未检出任何路由装饰器——检测器失效（fail-loud）"
    guards = [m.start() for m in _GUARD_RE.finditer(text)]
    assert guards, "R-N2-2：__main__ 守卫缺失——脚本入口被删"
    guard_pos = guards[0]
    late = [
        text[m.start() : text.find("\n", m.start())].strip() for m in _ROUTE_RE.finditer(text) if m.start() > guard_pos
    ]
    assert not late, f"N2 病根再现：存在位于 __main__ 守卫之后的路由装饰器——脚本直跑模式这些路由永不注册: {late[:5]}"
