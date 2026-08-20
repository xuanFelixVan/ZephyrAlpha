# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""P2-9 WAL 段编解码模块测试。"""

import pytest

from zephyr.data.wal_codec import (
    CodecRegistry,
    TsvCodec,
    decode_tsv,
    encode_tsv,
    get_registry,
)


class TestTsvCodec:
    """TSV 编解码器测试。"""

    def test_encode_empty_rows(self):
        assert encode_tsv([]) == b""

    def test_encode_single_row(self):
        data = encode_tsv([("000001", "10.5", "1000")])
        assert data == b"000001\t10.5\t1000"

    def test_encode_multiple_rows(self):
        data = encode_tsv([("a", "1"), ("b", "2")])
        assert data == b"a\t1\nb\t2"

    def test_encode_none_value(self):
        data = encode_tsv([("000001", None, "1000")])
        assert b"\\N" in data

    def test_encode_nan_value(self):
        import math

        data = encode_tsv([("000001", float("nan"))])
        assert b"\\N" in data

    def test_encode_special_chars_replaced_with_space(self):
        """ch_writer.tsv_escape 将 \\t/\\n/\\r 替换为空格（有损转义）。"""
        data = encode_tsv([("hello\tworld", "test\nvalue")])
        text = data.decode("utf-8")
        # \t 和 \n 被替换为空格
        assert "hello world" in text
        assert "test value" in text
        # 不应包含原始 \t（列分隔符除外）或 \n（行分隔符除外）
        assert text.count("\t") == 1  # 只有一个列分隔符

    def test_encode_control_chars_replaced(self):
        """控制字符（\\x00-\\x1F）替换为空格。"""
        data = encode_tsv([("ab\x00cd", "ef\x01gh")])
        text = data.decode("utf-8")
        assert "\x00" not in text
        assert "\x01" not in text

    def test_decode_empty(self):
        assert decode_tsv(b"") == []

    def test_decode_single_row(self):
        rows = decode_tsv(b"000001\t10.5\t1000\n")
        assert rows == [("000001", "10.5", "1000")]

    def test_decode_single_row_no_trailing_newline(self):
        rows = decode_tsv(b"000001\t10.5\t1000")
        assert rows == [("000001", "10.5", "1000")]

    def test_decode_none_value(self):
        rows = decode_tsv(b"000001\t\\N\t1000\n")
        assert rows[0][1] is None

    def test_roundtrip(self):
        original = [("000001", "10.5", None), ("000002", "20.3", "2000")]
        encoded = encode_tsv(original)
        decoded = decode_tsv(encoded)
        assert decoded[0][0] == "000001"
        assert decoded[0][2] is None
        assert decoded[1][0] == "000002"

    def test_roundtrip_with_ch_writer_consistency(self):
        """编码结果与 wal_writer.serialize_tsv 完全一致。"""
        from zephyr.data import ch_writer

        rows = [("000001", "10.5", None), ("000002", "hello\tworld")]
        # wal_writer.serialize_tsv 的逻辑
        expected = "\n".join("\t".join(ch_writer.tsv_escape(v) for v in row) for row in rows).encode("utf-8")
        assert encode_tsv(rows) == expected

    def test_tsv_codec_class_encode(self):
        data = TsvCodec.encode([("a", "b")])
        assert data == b"a\tb"

    def test_tsv_codec_class_decode(self):
        rows = TsvCodec.decode(b"a\tb\n")
        assert rows == [("a", "b")]

    def test_tsv_magic_is_empty(self):
        assert TsvCodec.MAGIC == b""


class TestCodecRegistry:
    """Codec 注册表测试。"""

    def test_get_tsv_codec_for_plain_data(self):
        registry = get_registry()
        data = b"000001\t10.5\n"
        codec = registry.get_codec(data)
        assert codec is not None

    def test_decode_tsv_via_registry(self):
        registry = get_registry()
        data = encode_tsv([("000001", "10.5")])
        rows = registry.decode(data)
        assert rows == [("000001", "10.5")]

    def test_encode_tsv_via_registry(self):
        registry = get_registry()
        data = registry.encode([("000001", "10.5")], codec_name="tsv")
        assert data == b"000001\t10.5"

    def test_encode_proto_falls_back_to_tsv(self):
        registry = get_registry()
        data = registry.encode([("000001", "10.5")], codec_name="proto")
        # Proto 未实现，降级到 TSV
        assert data == b"000001\t10.5"

    def test_roundtrip_via_registry(self):
        registry = get_registry()
        original = [("a", "1"), ("b", None)]
        encoded = registry.encode(original)
        decoded = registry.decode(encoded)
        assert decoded[0][0] == "a"
        assert decoded[1][1] is None

    def test_get_registry_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2
