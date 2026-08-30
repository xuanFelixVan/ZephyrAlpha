# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.env
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: env.py
# 层: 算法
# - id: A1
#   name_zh: ① current_env
#   name_en: current_env
#   intro: current_env() 源码 L169-L175
#   desc: 源码 L169-L175
#   inputs: 无参数
#   outputs: Env
# - id: A2
#   name_zh: ② is_dev
#   name_en: is_dev
#   intro: is_dev() 源码 L178-L179
#   desc: 源码 L178-L179
#   inputs: 无参数
#   outputs: bool
# - id: A3
#   name_zh: ③ is_staging
#   name_en: is_staging
#   intro: is_staging() 源码 L182-L183
#   desc: 源码 L182-L183
#   inputs: 无参数
#   outputs: bool
# - id: A4
#   name_zh: ④ is_prod
#   name_en: is_prod
#   intro: is_prod() 源码 L186-L187
#   desc: 源码 L186-L187
#   inputs: 无参数
#   outputs: bool
# - id: A5
#   name_zh: ⑤ is_test
#   name_en: is_test
#   intro: is_test() 源码 L190-L191
#   desc: 源码 L190-L191
#   inputs: 无参数
#   outputs: bool
# - id: A6
#   name_zh: ⑥ is_debug
#   name_en: is_debug
#   intro: 仅在 dev 环境下为 True——生产环境永远 False。
#   desc: 仅在 dev 环境下为 True——生产环境永远 False。；源码 L194-L196
#   inputs: 无参数
#   outputs: bool
#   （注：A6 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: Env
#   name_en: Env
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

from typing import Self

"""
env.py —— 环境检测工具（Phase 9 新增 | 盲点 B20 修复）

痛点修复：AGENTS.md 要求环境隔离，但没有代码层面的工具——
  1. if os.getenv("ENV") == "production" 散落在各模块
  2. AI 在环境判断时容易写反 or 漏掉条件
  3. 测试环境的标志位不统一——有的用 pytest 有的用环境变量

设计对标：
  - Spring Profiles（dev / staging / prod）
  - 12-Factor App §III（Config stored in environment variables）
  - Django settings（DEBUG / TESTING flags）

设计原则：
  - 统一环境判据——所有模块通过本模块判断当前环境
  - 优先级：ZEPHYR_ENV 环境变量 > pytest 自动检测 > default "dev"

AI 施工约定：
  - 任何环境相关判断 MUST 使用 is_dev()/is_prod()/is_test()——禁止裸 os.getenv("ENV")
  - 新增环境类型时 SHOULD 在 Environmental 中追加

SSoT: MOD-INF-016 §2.19 shared-env
Version: 0.1.0
"""


import os
import sys
import threading
from enum import Enum, unique

__all__ = [
    "Env",
    "current_env",
    "is_debug",
    "is_dev",
    "is_prod",
    "is_staging",
    "is_test",
]


@unique
class Env(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "production"
    TEST = "test"


_ENV_KEY = "ZEPHYR_ENV"


def _detect_env() -> Env:
    explicit = os.environ.get(_ENV_KEY)
    if explicit:
        try:
            return Env(explicit)
        except ValueError:
            pass

    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST"):
        return Env.TEST

    return Env.DEV


_CURRENT_ENV: Env | None = None
_CURRENT_ENV_lock = threading.Lock()


def current_env() -> Env:
    global _CURRENT_ENV
    if _CURRENT_ENV is None:
        with _CURRENT_ENV_lock:
            if _CURRENT_ENV is None:
                _CURRENT_ENV = _detect_env()
    return _CURRENT_ENV


def is_dev() -> bool:
    return current_env() is Env.DEV


def is_staging() -> bool:
    return current_env() is Env.STAGING


def is_prod() -> bool:
    return current_env() is Env.PROD


def is_test() -> bool:
    return current_env() is Env.TEST


def is_debug() -> bool:
    """仅在 dev 环境下为 True——生产环境永远 False。"""
    return current_env() in (Env.DEV, Env.TEST)
