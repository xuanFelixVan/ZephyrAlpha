# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.errors
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
errors.py —— ZephyrAlpha 统一错误层次（Traditional Exception Hierarchy）

补全 ssot_guard.py:L103 标记的「尚未完成的 ZephyrBaseError 体系」。

上下文：
  - contracts/errors/ 目录下是 dataclass 值对象（非 Exception），用于契约层的结构化错误传递
  - money.py / timestamp.py / ssot_guard.py 各自定义了独立的 Exception 子类
  - 本文件提供统一的 Exception 继承树，作为所有模块 throw/catch 的唯一根

设计原则：
  - 每个子类携带明确的模块归属——AI 看到错误类名就知道问题出在哪个子系统
  - 所有错误接受 message: str + details: dict | None ——details 用于附加结构化上下文
  - frozen dataclass 风格的 __repr__ 让 AI 眼读日志效率最高

AI 施工约定：
  - 新增业务模块时，MUST 在此文件中登记对应 Error 子类
  - 禁止在模块内自定义 Exception 基类——全部统一从此继承
  - catch 时从具体到抽象：先 catch TaskError，再 catch ZephyrBaseError

SSoT: MOD-INF-016 §2.3 shared-errors
Version: 0.1.0
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "ConfigError",
    "ContextError",
    "ContractError",
    "DataError",
    "FeedbackError",
    "GateError",
    # 5.151.5 修复: IOError 从 __all__ 移除, 避免覆盖 Python 内建 IOError (3.3+ 为 OSError 别名)。
    # IOError 仍可作为 errors.IOError 直接访问 (向后兼容), 但 import * 不再覆盖内建。
    # 新代码应使用 ZephyrIOError。
    "PipelineError",
    "SecurityError",
    "SessionError",
    "TaskError",
    "UnimplementedError",
    "ValidationError",
    "ZephyrBaseError",
    "ZephyrIOError",
]


class ZephyrBaseError(Exception):
    """ZephyrAlpha 所有业务异常的根。

    Attributes:
        message: 人类可读错误描述。
        details: 可选附加结构化上下文（模块名、参数名、触发值等）。
        error_code: 业务错误码（ZA-XX-NNNN 格式），子类以类属性声明默认值。
    """

    error_code: str | None = None

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.details: dict[str, Any] = details or {}
        if error_code is not None:
            self.error_code = error_code

    def __repr__(self) -> str:
        parts = [f"message={self.message!r}"]
        if self.error_code:
            parts.insert(0, f"code={self.error_code}")
        if self.details:
            parts.append(f"details={self.details!r}")
        return f"{type(self).__name__}({', '.join(parts)})"

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigError(ZephyrBaseError):
    """配置系统错误——YAML 解析失败、Schema 校验失败、路径无效等。"""

    error_code = "ZA-SH-0001"


class ContractError(ZephyrBaseError):
    """数据契约错误——跨层契约不匹配、版本冲突、类型不兼容。"""

    error_code = "ZA-SH-0002"


class SecurityError(ZephyrBaseError):
    """安全相关错误——权限拒绝、Token 无效、沙箱逃逸检测。"""

    error_code = "ZA-SH-0003"


class SessionError(ZephyrBaseError):
    """会话生命周期错误——会话不存在、状态转换非法、会话超时。"""

    error_code = "ZA-SH-0004"


class ValidationError(ZephyrBaseError):
    """输入校验错误——字段缺失、类型错误、值域越界。"""

    error_code = "ZA-SH-0005"


class TaskError(ZephyrBaseError):
    """任务系统错误——Task 状态机非法跳转、Task 构造非法、dependency 死锁。"""

    error_code = "ZA-SH-0006"


class PipelineError(ZephyrBaseError):
    """管线错误——管线装配失败、步骤执行异常、路由错误。"""

    error_code = "ZA-SH-0007"


class GateError(ZephyrBaseError):
    """门禁错误——门禁判决异常、熔断器触发、contract-template 找不到。"""

    error_code = "ZA-SH-0008"


class ContextError(ZephyrBaseError):
    """上下文引擎错误——上下文装配失败、Token 预算溢出、evict 异常。"""

    error_code = "ZA-SH-0009"


class FeedbackError(ZephyrBaseError):
    """反馈循环错误——自进化引擎异常、metrics 采集失败、pattern 分析异常。"""

    error_code = "ZA-SH-0010"


class DataError(ZephyrBaseError):
    """数据层错误——数据库连接失败、查询异常、迁移失败。"""

    error_code = "ZA-SH-0011"


class ZephyrIOError(ZephyrBaseError):
    """I/O 错误——文件读写失败、路径不存在、编码异常。"""

    error_code = "ZA-SH-0012"


# 5.151.5 修复: IOError 作为 ZephyrIOError 的向后兼容别名保留,
# 但新代码应使用 ZephyrIOError 避免与 Python 内建 IOError (OSError 别名) 混淆
IOError = ZephyrIOError


class UnimplementedError(ZephyrBaseError):
    """施工占位——标记尚未实现但已规划的功能入口。"""

    error_code = "ZA-SH-0013"
