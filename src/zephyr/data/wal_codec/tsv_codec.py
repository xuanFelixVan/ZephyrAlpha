# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""TSV 编解码器——WAL 段文件的当前格式。

从 wal_writer._serialize_tsv 提取逻辑，统一编解码入口。

格式规范（与 ch_writer.tsv_escape 对齐，单一真源）：
- 每行一个记录，列以 \\t 分隔
- None / NaN → \\N（ClickHouse NULL 标记）
- 字符串中的 \\t / \\n / \\r 替换为空格（CH TabSeparated 默认行为）
- \\x00 及控制字符替换为空格
- 反斜杠转义
- 无 magic number（纯文本，向后兼容）

Usage::

    from zephyr.data.wal_codec import encode_tsv, decode_tsv
    tsv_bytes = encode_tsv(rows)
    rows = decode_tsv(tsv_bytes)
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


def _escape_value(v: object) -> str:
    """转义单个值为 TSV 格式（委托 ch_writer.tsv_escape，单一真源）。

    Args:
        v: 值（None/数字/字符串/浮点/NaN）

    Returns:
        TSV 编码后的字符串

    注意:
        转义逻辑与 ch_writer.tsv_escape 完全一致——ch_writer 是 TSV 转义的
        生产真源（裁定 #ARCH-TSV-SOT-001），wal_codec 不得自行实现转义逻辑。
    """
    from zephyr.data import ch_writer

    return ch_writer.tsv_escape(v)


def _unescape_value(s: str) -> str:
    """反转义 TSV 值。

    ch_writer.tsv_escape 是有损转义（\\t/\\n/\\r → 空格），无法原样还原。
    此函数仅处理反斜杠转义，用于 best-effort 解码（如调试/验证）。
    """
    return s.replace("\\\\", "\\")


def encode_tsv(rows: list[tuple]) -> bytes:
    """将行列表编码为 TSV 字节。

    与 wal_writer._serialize_tsv 输出完全一致（无尾部 \\n）。

    Args:
        rows: 行列表，每行是一个 tuple

    Returns:
        TSV 格式字节数据（UTF-8 编码，无尾部 \\n）
    """
    if not rows:
        return b""
    lines = ["\t".join(_escape_value(v) for v in row) for row in rows]
    return "\n".join(lines).encode("utf-8")


def decode_tsv(data: bytes) -> list[tuple]:
    """将 TSV 字节解码为行列表。

    None 值还原为 None，其他值保持字符串形式（类型转换由调用方负责）。

    Args:
        data: TSV 格式字节数据

    Returns:
        行列表，每行是一个 tuple（值可能为 None 或 str）
    """
    if not data:
        return []
    text = data.decode("utf-8")
    rows = []
    for line in text.rstrip("\n").split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        row = tuple(None if p == "\\N" else _unescape_value(p) for p in parts)
        rows.append(row)
    return rows


class TsvCodec:
    """TSV 编解码器——实现 Codec 协议。

    协议方法：
    - encode(rows) -> bytes
    - decode(data) -> list[tuple]
    - magic -> bytes（TSV 无 magic，返回 b""）
    """

    MAGIC = b""  # TSV 无 magic number（纯文本格式）

    @staticmethod
    def encode(rows: list[tuple]) -> bytes:
        """编码行列表为 TSV 字节。"""
        return encode_tsv(rows)

    @staticmethod
    def decode(data: bytes) -> list[tuple]:
        """解码 TSV 字节为行列表。"""
        return decode_tsv(data)
