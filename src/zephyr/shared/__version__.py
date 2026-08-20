# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.__version__
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

r"""


__version__.py —— ZephyrAlpha Shared 模块版本常量

Phase 6 新增（盲点 B8）——解决消费者无法在运行时得知 shared/ 版本、
版本不匹配导致微妙 bug 的问题。
Phase 9 增强（盲点 B21）——追加 SemVer 比较函数（版本兼容性矩阵判断）。

设计原则：
  - 单点定义——版本号只在这里改，蓝图/docs/registries 从代码读取或不硬编码
  - 符合 PEP 396 / PEP 440——__version__ 是标准约定
  - 运行时可查询——消费者可做 importlib.metadata.version("zephyr") 或直接导入

对标：
  - numpy: numpy.__version__ -> "1.26.0"
  - pydantic: pydantic.__version__ -> "2.5.0"
  - pip：pip.__version__
  - PEP 396: Module Version Numbers
  - PEP 440: Version Identification and Dependency Specification
  - semver 库：version comparison utilities

SSoT: MOD-INF-016 §2.15 shared-version
Version: 0.14.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: shared 层版本常量
#   fields: __version__="0.14.0" / __version_info__=(0,14,0) / MIN_COMPATIBLE_SHARED_VERSION
#   code: __version__.py L64-66
# - id: I2
#   name: 调用方传入的版本字符串参数
#   fields: required（最低要求版本，如 "0.5.0"）/ a / b（SemVer 字符串 "x.y.z"）
#   code: check_shared_version L89 / version_* L139-188 函数参数
# 层: 算法
# - id: A1
#   name_zh: ① 版本字符串解析
#   name_en: _parse_version / _parse_semver
#   intro: 把 "x.y.z" 字符串拆成可比较的整数元组
#   desc: split(".") 取纯数字段转 int 元组；或正则 ^(\d+)\.(\d+)\.(\d+) 提取 MAJOR/MINOR/PATCH，非法串抛 ValueError
#   inputs: I2
#   outputs: 整数版本元组 tuple[int,...]
# - id: A2
#   name_zh: ② 运行时版本校验
#   name_en: check_shared_version
#   intro: 比对当前 shared 版本是否满足消费者要求的最低版本
#   desc: current >= needed 返回 True；不满足时 strict=True 抛 VersionMismatchError，否则 warning 日志后返回 False
#   inputs: I1 A1
#   outputs: bool 校验结果 / VersionMismatchError
#   invariant: required 为 None 时回退 MIN_COMPATIBLE_SHARED_VERSION
# - id: A3
#   name_zh: ③ SemVer 比较运算族
#   name_en: version_eq / version_lt / version_lte / version_gt / version_gte / version_compatible
#   intro: 两个版本号的大小比较与 MAJOR 级兼容性判断
#   desc: 解析后按元组字典序比较；compatible = 同 MAJOR 且 a >= b（cross_layer_contracts.yaml VER-R1）
#   inputs: A1
#   outputs: bool 比较结果
# - id: A4
#   name_zh: ④ 版本组件提取
#   name_en: version_major / version_minor / version_patch
#   intro: 取出版本号的主/次/补丁三段数字
#   desc: _parse_semver 后按下标 0/1/2 返回对应 int
#   inputs: A1
#   outputs: int 版本组件
# 层: 输出
# - id: O1
#   name_zh: 版本校验与比较结果
#   name_en: bool
#   intro: True 表示版本满足要求 / 比较成立 / MAJOR 兼容
#   downstream: 全项目 shared 消费者启动时版本自检（[CONSUMERS] 头未登记具体 MOD）
# - id: O2
#   name_zh: 版本不匹配异常
#   name_en: VersionMismatchError
#   intro: strict 模式下版本不达标时的硬中断（error_code ZA-SH-0030）
#   downstream: 调用方异常处理逻辑
# - id: O3
#   name_zh: 版本组件整数
#   name_en: int
#   intro: major/minor/patch 数值，供按段判断版本
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# A1 --> A2
# A1 --> A3
# A1 --> A4
# A2 --> O1
# A3 --> O1
# A2 --> O2
# A4 --> O3
"""

from __future__ import annotations

import re
from typing import Final

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

        version_compatible("0.7.0", "0.6.0") -> True  # 同 MAJOR, a >= b
        version_compatible("0.5.0", "0.7.0") -> False  # 同 MAJOR, 但 a < b
        version_compatible("1.0.0", "0.7.0") -> False  # 不同 MAJOR
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
