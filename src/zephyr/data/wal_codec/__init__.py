# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [MODULE] zephyr.data.wal_codec
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.local_replay(WAL段文件格式来源)
# [CONSUMERS] zephyr.data.wal_writer(可选接入)
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] TSV格式向后兼容; magic number区分格式; codec_registry路由解码器; 混合格式段文件可共存
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 编码失败->返回空bytes+log; 解码失败->返回空list+log; 未知magic number->按TSV降级
# [TESTS] tests/zephyr/data/test_wal_codec.py
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""WAL 段编解码模块（MOD-L00-006）。

P2-9：WAL 段文件编解码层。

当前状态：仅实现 TSV codec（从 wal_writer 提取）+ codec_registry 接口。
Protobuf codec 为 P3 远期备选（蓝图 §2.1 标注"仅在 TSV 性能不满足时启动"）。

设计要点：
- magic number 区分格式：TSV 段无 magic（纯文本），Proto 段以 PB\\x01 开头
- codec_registry 按 magic number 路由到对应 codec
- 混合格式段文件可共存（渐进迁移）
"""
from zephyr.data.wal_codec.tsv_codec import TsvCodec, encode_tsv, decode_tsv
from zephyr.data.wal_codec.codec_registry import CodecRegistry, get_registry

__all__ = [
    "TsvCodec",
    "encode_tsv",
    "decode_tsv",
    "CodecRegistry",
    "get_registry",
]
