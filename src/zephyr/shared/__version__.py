# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.__version__
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
# [A_module] module_id=MOD-SHR___version__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
__version__.py —— ZephyrAlpha Shared 模块版本常量

Phase 6 新增（盲点 B8）——解决消费者无法在运行时得知 shared/ 版本、
版本不匹配导致微妙 bug 的问题。
Phase 9 增强（盲点 B21）——追加 SemVer 比较函数（版本兼容性矩阵判断）。

设计原则：
  - 单点定义——版本号只在这里改，蓝图/docs/registries 从代码读取或不硬编码
  - 符合 PEP 396 / PEP 440——__version__ 是标准约定
  - 运行时可查询——消费者可做 importlib.metadata.version("zephyr") 或直接导入

对标：
  - numpy: numpy.__version__ → "1.26.0"
  - pydantic: pydantic.__version__ → "2.5.0"
  - pip：pip.__version__
  - PEP 396: Module Version Numbers
  - PEP 440: Version Identification and Dependency Specification
  - semver 库：version comparison utilities

SSoT: MOD-INF-016 §2.15 shared-version
Version: 0.14.0
"""

from __future__ import annotations

from typing import Final
import re

__all__ = [
    "MIN_COMPATIBLE_SHARED_VERSION",
    "VersionMismatchError",
    "__version__",
    "__version_info__",
    "check_shared_version",
    "version_compatible",
    "version_eq",
    "version_gt",
    "version_gte",
    "version_lt",
    "version_lte",
    "version_major",
    "version_minor",
    "version_patch",
]

__version__ = "0.14.0"
__version_info__ = (0, 14, 0)
MIN_COMPATIBLE_SHARED_VERSION: Final[str] = "0.14.0"
"""最低兼容的 Shared 版本。

消费者应校验 shared.__version__ >= 此值。
如果蓝图要求的最低版本高于运行时的 shared 版本，说明需要更新 shared 层。
"""


class VersionMismatchError(Exception):
    """版本不匹配异常。"""
    error_code = "ZA-SH-0030"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def _parse_version(version_str: str) -> tuple[int, ...]:
    parts = version_str.split(".")
    return tuple(int(p) for p in parts if p.isdigit())


def check_shared_version(
    required: str | None = None,
    *,
    module_id: str = "unknown",
    strict: bool = False,
) -> bool:
    """校验当前 shared/ 版本是否满足消费者要求。

    Args:
        required: 消费者要求的最低版本（如 "0.5.0"）。None = 使用 MIN_COMPATIBLE_SHARED_VERSION
        module_id: 校验失败的日志中显示的模块 ID
        strict: True = 版本不匹配抛出 VersionMismatchError。False = 仅返回 False + 日志

    Returns:
        True = 版本满足要求

    Raises:
        VersionMismatchError: strict=True 且版本不满足

    用法:
        from zephyr.shared.__version__ import check_shared_version
        check_shared_version("0.5.0", module_id="MOD-GT-003", strict=True)
    """
    required = required or MIN_COMPATIBLE_SHARED_VERSION
    current = _parse_version(__version__)
    needed = _parse_version(required)

    if current >= needed:
        return True

    msg = (
        f"Shared 版本不匹配: 当前 {__version__} < 要求 {required}。"
        f"  (模块: {module_id})"
        f"  请更新 shared/ 层到至少 {required}。"
    )
    if strict:
        raise VersionMismatchError(msg)
    import logging

    logging.getLogger(__name__).warning(msg)
    return False


def _parse_semver(version_str: str) -> tuple[int, int, int]:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", version_str)
    if m is None:
        raise ValueError(f"invalid semver string: {version_str!r}")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def version_eq(a: str, b: str) -> bool:
    """a == b——精确匹配。"""
    return _parse_semver(a) == _parse_semver(b)


def version_lt(a: str, b: str) -> bool:
    """a < b——严格小于。"""
    return _parse_semver(a) < _parse_semver(b)


def version_lte(a: str, b: str) -> bool:
    """a <= b——小于等于。"""
    return _parse_semver(a) <= _parse_semver(b)


def version_gt(a: str, b: str) -> bool:
    """a > b——严格大于。"""
    return _parse_semver(a) > _parse_semver(b)


def version_gte(a: str, b: str) -> bool:
    """a >= b——大于等于。"""
    return _parse_semver(a) >= _parse_semver(b)


def version_compatible(a: str, b: str) -> bool:
    """a 与 b 是否在 MAJOR 版本层面兼容（同 MAJOR 且 a >= b）。

    cross_layer_contracts.yaml VER-R1：同 MAJOR 版本 MUST 前后兼容。

    Usage::

        version_compatible("0.7.0", "0.6.0") → True  # 同 MAJOR, a >= b
        version_compatible("0.5.0", "0.7.0") → False  # 同 MAJOR, 但 a < b
        version_compatible("1.0.0", "0.7.0") → False  # 不同 MAJOR
    """
    a_parts = _parse_semver(a)
    b_parts = _parse_semver(b)
    return a_parts[0] == b_parts[0] and a_parts >= b_parts


def version_major(version_str: str) -> int:
    return _parse_semver(version_str)[0]


def version_minor(version_str: str) -> int:
    return _parse_semver(version_str)[1]


def version_patch(version_str: str) -> int:
    return _parse_semver(version_str)[2]
