# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [MODULE] zephyr.data.normalizers
# [DOMAIN] D_DATA
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
Data Normalizers sub-package——原始记录到统一 schema 的归一化层（抽象 + OHLCV 实现）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, Final, FormatTransformer, DataNormalizer, NormalizeResul…
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 annotations, Final, FormatTransformer, DataNormalizer, NormalizeResult, Ohl…
#   desc: __init__ import L38；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（6 符号）
#   name_en: __all__
#   intro: annotations, Final, FormatTransformer, DataNormalizer, NormalizeResult, OhlcvNo…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

# NOTE(P1W08-20260825): scaffold 子包路径斜杠误写已修正（zephyr.data/normalizers → zephyr.data.normalizers），可逆单行修复
from zephyr.data.normalizers.format_transformer import FormatTransformer
from zephyr.data.normalizers.normalizer_base import DataNormalizer, NormalizeResult
from zephyr.data.normalizers.ohlcv_normalizer import OhlcvNormalizer

__all__: Final = [
    "DataNormalizer",
    "NormalizeResult",
    "OhlcvNormalizer",
]

__all__.append("FormatTransformer")
