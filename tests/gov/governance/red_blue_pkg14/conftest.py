# [A_test] module_id: MOD-TEST-RB14-BASE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | docs/_working/commit_speedup_campaign/90_verification/red_blue_pkg14_report.md | §
# [MODULE] governance.red_blue_pkg14.conftest
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; governance.red_blue_pkg14._common
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/governance/red_blue_pkg14/
# [MATURITY] testing
# [INVARIANTS] fixture 只做转发；实现真源=_common.py（全 tmp 沙盒，绝不触生产活体）
# [MODIFY-GUARD] 包14 红蓝极限对抗 7 场景（st-commitspeed-tbl-20260924）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本目录
# [TTL] task_bound
"""red_blue_pkg14 conftest — pytest fixture 转发层（实现真源=_common.py）。

新家注册注记（st-mastertc-loop 收编补件）：旧家 tests/governance/ 有 __init__.py
basedir 链使 top-level ``governance`` 包名可解析；10-04 旧路径删除波后该链不在，
新家 tests/gov/governance/red_blue_pkg14/ 的 ``from governance.red_blue_pkg14._common
import ...`` 需仿 tests/conftest.py 的 governance.d7_code 先例显式注册 sys.modules。
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent

# --- governance.red_blue_pkg14 包名注册（先于 fixture 转发导入） ---
_gov = sys.modules.get("governance")
if _gov is None:
    # namespace 占位：仅当真 ``governance`` 包尚未被任何路径解析时兜底
    _gov = types.ModuleType("governance")
    _gov.__path__ = []
    sys.modules["governance"] = _gov

if "governance.red_blue_pkg14" not in sys.modules:
    _init = _PKG_DIR / "__init__.py"
    _spec = importlib.util.spec_from_file_location(
        "governance.red_blue_pkg14",
        _init,
        submodule_search_locations=[str(_PKG_DIR)],
    )
    _pkg = importlib.util.module_from_spec(_spec)
    sys.modules["governance.red_blue_pkg14"] = _pkg
    if _spec.loader and hasattr(_spec.loader, "exec_module"):
        _spec.loader.exec_module(_pkg)
    _gov.red_blue_pkg14 = _pkg

from governance.red_blue_pkg14._common import sb_queue, sb_repo  # noqa: E402,F401 — fixture 转发
