# [A_module] module_id=MOD-CMP-audit_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

Re-export wrapper: audit-orchestrator has migrated to zephyr.gov_audit.

5.60.8 治本（2026-07-20）：替代 ``from ... import *``，改用 PEP 562 惰性转发，
保留向后兼容（``from zephyr.compliance.audit_orchestrator import X`` 仍可用），
同时消除 namespace 污染并避免 eager import 副作用。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 调用方访问的符号名（str）
#   fields: name——旧 import 路径下被访问的属性名，双下划线名直接拒绝
#   code: __getattr__(name)（__init__.py L18）
# - id: I2
#   name: 转发目标模块（模块对象）
#   fields: _TARGET 常量指向的 canonical 包全部公开符号
#   code: _TARGET = "zephyr.gov_audit"（__init__.py L15）
# 层: 算法
# - id: A1
#   name_zh: ① PEP 562 惰性符号转发
#   name_en: __getattr__
#   intro: 旧包路径被访问时才 import 新包并取同名符号，取到就缓存
#   desc: name 以 __ 开头抛 AttributeError（L20-21）→ importlib.import_module(_TARGET)（L22）→ getattr 取符号失败转 AttributeError（L23-28）→ setattr 缓存进模块属性（L29）→ 返回符号
#   inputs: I1 I2
#   outputs: 转发后的符号对象 Any
#   invariant: 同一 name 仅转发一次，结果缓存于 sys.modules[__name__]
# - id: A2
#   name_zh: ② 目录清单合并
#   name_en: __dir__
#   intro: 列属性时把本包全局名和目标包 __all__ 合并去重排序
#   desc: sorted(set(globals()) | set(target.__all__))（L33-36）
#   inputs: I2
#   outputs: 排序后的属性名列表 list[str]
# 层: 输出
# - id: O1
#   name_zh: 向后兼容的符号再导出
#   name_en: re-exported symbols
#   intro: 让 from zephyr.compliance.audit_orchestrator import X 的旧写法继续可用
#   downstream: 无下游/内部使用（5.60.8 迁移兼容壳，仓内0消费者；canonical 包 zephyr.gov_audit）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O1
"""
from __future__ import annotations

import importlib
import sys
from typing import Any

_TARGET = "zephyr.gov_audit"


def __getattr__(name: str) -> Any:
    """PEP 562 惰性转发：从目标模块获取符号并缓存到模块属性。"""
    if name.startswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    target = importlib.import_module(_TARGET)
    try:
        value = getattr(target, name)
    except AttributeError as exc:
        raise AttributeError(
            f"module {__name__!r}: re-export target {_TARGET!r} has no attribute {name!r}"
        ) from exc
    setattr(sys.modules[__name__], name, value)
    return value


def __dir__() -> list[str]:
    target = importlib.import_module(_TARGET)
    target_all = getattr(target, "__all__", [])
    return sorted(set(globals()) | set(target_all))

__all__: list[str] = []
