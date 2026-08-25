# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [MODULE] zephyr.data.normalizers
# [DOMAIN] D_DATA
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""Data Normalizers sub-package——原始记录到统一 schema 的归一化层（抽象 + OHLCV 实现）。"""

from __future__ import annotations

from typing import Final

from zephyr.data.normalizers.normalizer_base import DataNormalizer, NormalizeResult
from zephyr.data.normalizers.ohlcv_normalizer import OhlcvNormalizer
# NOTE(P1W08-20260825): scaffold 子包路径斜杠误写已修正（zephyr.data/normalizers → zephyr.data.normalizers），可逆单行修复
from zephyr.data.normalizers.format_transformer import FormatTransformer

__all__: Final = [
    "DataNormalizer",
    "NormalizeResult",
    "OhlcvNormalizer",
]

__all__.append("FormatTransformer")
