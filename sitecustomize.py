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
# [TTL] permanent
"""
sitecustomize.py — Python 解释器启动时自动加载的运行时 Gate 引导（fallback 机制）。

⚠️ Python 3.11 行为警示（2026-07-19 裁定 #ARCH-PYTHON-SITECUSTOMIZE）：
  Python 3.11 的 site 模块在调用 execsitecustomize() 时，sys.path **不包含 cwd**
  （安全机制）。经 PYTHONVERBOSE=2 实测确认：site 模块搜索 sitecustomize 时遍历
  30 个路径（DLLs/Lib/Python311/site-packages 等），**无一是 cwd**。
  因此 `python -c "..."` 模式下本文件**不会被加载**——它是死代码。

  本文件仅作为以下场景的 fallback：
  - `python script.py`（脚本在仓库根，sys.path[0]=脚本目录=仓库根）→ 生效
  - `python -m pytest`（pytest 可能修改 sys.path 使仓库根可被搜索）→ 部分生效

  **主要机制**：usercustomize.py（位于 USER_SITE，site 模块的 execusercustomize()
  会可靠加载）。usercustomize.py 承担 `python -c` 模式下的 src/ 注入 +
  runtime_interceptor 安装职责。usercustomize.py 不在版本控制中（全局文件），
  由 AI 进项目时一次性配置（见 .trae/rules/project_rules.md FIRST-READ 步骤 0）。

部署位置：仓库根目录（d:\\ZephyrAlpha\\sitecustomize.py）。
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
