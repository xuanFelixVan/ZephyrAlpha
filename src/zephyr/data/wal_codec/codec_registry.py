# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=L
# [TTL] permanent
r"""
Codec 注册表——按 magic number 路由到对应编解码器。

设计：
- 每个 codec 有唯一的 magic number（4 字节前缀）
- TSV 无 magic（b""），因此纯文本段文件默认按 TSV 解码
- Proto 段以 PB\x01 开头（P3 远期实现）
- drain 线程根据 magic number 自动选择解码器

Usage::

    from zephyr.data.wal_codec import get_registry
    registry = get_registry()
    codec = registry.get_codec(data)
    rows = codec.decode(data)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: codec_registry.py
# 层: 算法
# - id: A1
#   name_zh: ① CodecProtocol
#   name_en: CodecProtocol
#   intro: 编解码器协议。
#   desc: 编解码器协议。；公共方法（定义序）: encode, decode；源码 L76-L83
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② CodecRegistry
#   name_en: CodecRegistry
#   intro: Codec 注册表——按 magic number 路由。
#   desc: Codec 注册表——按 magic number 路由。 线程安全：注册表在初始化后只读（运行时不动态注册新 codec）。；公共方法（定义序）: get_codec, encode, decode；源码 L86-L…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ get_registry
#   name_en: get_registry
#   intro: 获取全局 CodecRegistry 单例。
#   desc: 获取全局 CodecRegistry 单例。；源码 L173-L178
#   inputs: 无参数
#   outputs: CodecRegistry
# 层: 输出
# - id: O1
#   name_zh: CodecRegistry
#   name_en: CodecRegistry
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from typing import Protocol

from zephyr.data.wal_codec.tsv_codec import TsvCodec

log = logging.getLogger(__name__)

# 预留的 Proto magic number（P3 远期实现时使用）
_PROTO_MAGIC = b"PB\x01"


class CodecProtocol(Protocol):
    """编解码器协议。"""

    MAGIC: bytes

    def encode(self, rows: list[tuple]) -> bytes: ...

    def decode(self, data: bytes) -> list[tuple]: ...


class CodecRegistry:
    """Codec 注册表——按 magic number 路由。

    线程安全：注册表在初始化后只读（运行时不动态注册新 codec）。
    """

    def __init__(self) -> None:
        self._codecs: list[tuple[bytes, CodecProtocol]] = []
        self._tsv_codec = TsvCodec()
        # TSV 是默认 codec（magic=b""，放在列表末尾作为 fallback）
        self._codecs.append((_PROTO_MAGIC, _ProtoCodecStub()))
        self._codecs.append((b"", self._tsv_codec))

    def get_codec(self, data: bytes) -> CodecProtocol:
        """根据数据前缀选择 codec。

        无 magic 匹配时降级到 TSV（向后兼容）。

        Args:
            data: WAL 段文件字节数据

        Returns:
            对应的 Codec 实例
        """
        for magic, codec in self._codecs:
            if magic and data.startswith(magic):
                return codec
        # 无 magic 匹配 → TSV（默认）
        return self._tsv_codec

    def encode(self, rows: list[tuple], codec_name: str = "tsv") -> bytes:
        """编码行列表。

        Args:
            rows: 行列表
            codec_name: codec 名称（"tsv" 或 "proto"）

        Returns:
            编码后的字节数据（含 magic 前缀，TSV 除外）
        """
        if codec_name == "proto":
            # P3 远期实现，当前返回 TSV
            log.warning("Proto codec 未实现，降级到 TSV")
            return self._tsv_codec.encode(rows)
        return self._tsv_codec.encode(rows)

    def decode(self, data: bytes) -> list[tuple]:
        """解码字节数据（自动选择 codec）。

        Args:
            data: WAL 段文件字节数据

        Returns:
            行列表
        """
        codec = self.get_codec(data)
        # Proto 段需跳过 magic 前缀
        if codec.MAGIC and data.startswith(codec.MAGIC):
            return codec.decode(data[len(codec.MAGIC) :])
        return codec.decode(data)


class _ProtoCodecStub:
    """Proto codec 桩——P3 远期实现时替换。

    当前仅记录 magic number，编解码降级到 TSV。
    """

    MAGIC = _PROTO_MAGIC

    @staticmethod
    def encode(rows: list[tuple]) -> bytes:
        """Proto 编码（未实现，降级到 TSV）。"""
        log.warning("ProtoCodec.encode 未实现，降级到 TSV")
        return TsvCodec.encode(rows)

    @staticmethod
    def decode(data: bytes) -> list[tuple]:
        """Proto 解码（未实现，降级到 TSV）。"""
        log.warning("ProtoCodec.decode 未实现，降级到 TSV")
        return TsvCodec.decode(data)


# 全局单例
_registry: CodecRegistry | None = None


def get_registry() -> CodecRegistry:
    """获取全局 CodecRegistry 单例。"""
    global _registry
    if _registry is None:
        _registry = CodecRegistry()
    return _registry
