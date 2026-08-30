# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [MODULE] zephyr.data.normalizers.normalizer_base
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.normalizers.ohlcv_normalizer; zephyr.data.normalizers.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] normalize 幂等（同输入同输出）；剔除必留痕（issues）；输入 list 不被修改
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 记录级坏数据不抛错——剔除并记 issues；结构级错误由子类声明
# [TESTS] tests/zephyr/data/test_normalizers.py
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
数据归一化器抽象基类（MOD-L00-006 data/normalizers/ 核心抽象）。

归一化器 = 原始记录 → 统一 schema 记录的变换层：列名归一/类型强转/校验剔除/
排序去重。记录级坏数据剔除并留痕（issues），不抛零散异常中断整批——与
data/quality_gate 的分工：归一化管"形状统一"，quality_gate 管"质量判定"。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: normalizer_base.py
# 层: 算法
# - id: A1
#   name_zh: ① DataNormalizer
#   name_en: DataNormalizer
#   intro: 归一化器抽象：normalize(records) → NormalizeResult。
#   desc: 归一化器抽象：normalize(records) → NormalizeResult。；公共方法（定义序）: name, normalize；源码 L79-L89
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DataNormalizer
#   downstream: zephyr.data.normalizers.ohlcv_normalizer; zephyr.data.normalizers.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Final

__all__: Final = [
    "DataNormalizer",
    "NormalizeResult",
]


@dataclass(frozen=True)
class NormalizeResult:
    """归一化输出。

    Attributes:
        records: 归一化后的记录（统一 schema 的 dict）
        dropped: 被剔除记录数
        issues: 剔除/修正留痕（每条一行原因说明）
    """

    records: tuple[dict, ...]
    dropped: int = 0
    issues: tuple[str, ...] = field(default_factory=tuple)


class DataNormalizer(abc.ABC):
    """归一化器抽象：normalize(records) → NormalizeResult。"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """归一化器标识（留痕用）。"""

    @abc.abstractmethod
    def normalize(self, records: list[dict]) -> NormalizeResult:
        """归一化一批记录。输入 list 不被修改；坏记录剔除并记 issues。"""
