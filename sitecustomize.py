# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] sitecustomize
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.runtime_interceptor
# [CONSUMERS]
# [STARTUP] automatic
# [MATURITY] prototype
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 启动失败绝不阻断解释器——任何异常静默吞掉
# [TESTS] tests/llm_security/test_runtime_interceptor.py
"""
sitecustomize.py — Python 解释器启动时自动加载的运行时 Gate 引导。

Python 的 site 模块在解释器启动时自动 import sitecustomize（若 sys.path 上存在）。
本文件利用该机制在进程启动时自动安装 LLM 裸调运行时拦截器（runtime_interceptor），
实现“无需业务代码显式调用”的零侵入自动生效（对标 GATE-20 后备防线需求）。

部署位置：仓库根目录（d:\\ZephyrAlpha\\sitecustomize.py）。
生效场景（cwd=仓库根 或 仓库根在 sys.path 上）：
  - python -m pytest / python -c / python -m zephyr...   → cwd='' 在 sys.path → 生效
  - python foo.py（脚本在仓库根）                          → 生效
  - python scripts/sub/foo.py（脚本在子目录）              → sys.path[0]=脚本目录，
    仓库根不在 path → 不生效（此场景为静态脚本，非业务运行时，GATE-20 静态门禁已覆盖）
    如需覆盖：set PYTHONPATH=<repo_root>

kill-switch：ZEPHYR_RUNTIME_GATE=0 → 完全关闭（install() 内部再次校验，双重尊重）。

铁律遵循：
- 向内收：本文件仅“引导”，拦截逻辑真源在 zephyr.security.llm_defense.llm_security.runtime_interceptor
- 绝不破坏解释器启动：任何异常静默吞掉（即使 src/ 不在 path、即使运行时拦截器模块损坏）
"""

import sys
from pathlib import Path

# kill-switch 快速短路（避免无谓的路径计算与导入）
_KILL_SWITCH = "ZEPHYR_RUNTIME_GATE"
import os as _os

if _os.environ.get(_KILL_SWITCH, "1") == "0":
    # 关闭：什么都不做
    pass
else:
    try:
        # sitecustomize.py 位于仓库根 → src/ = 同级 src/
        _repo_root = Path(__file__).resolve().parent
        _src_path = str(_repo_root / "src")
        if _src_path not in sys.path:
            sys.path.insert(0, _src_path)
        from zephyr.security.llm_defense.llm_security.runtime_interceptor import install as _install

        _install()
    except Exception:
        # 启动期绝不抛异常——宁可漏拦也不破坏解释器
        # （运行时拦截器是后备防线，主防线仍是 GATE-20 静态门禁）
        pass
