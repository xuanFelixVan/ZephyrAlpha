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
"""

WAL 段编解码模块（MOD-L00-006）。

P2-9：WAL 段文件编解码层。

当前状态：仅实现 TSV codec（从 wal_writer 提取）+ codec_registry 接口。
Protobuf codec 为 P3 远期备选（蓝图 §2.1 标注"仅在 TSV 性能不满足时启动"）。

设计要点：
- magic number 区分格式：TSV 段无 magic（纯文本），Proto 段以 PB 开头
- codec_registry 按 magic number 路由到对应 codec
- 混合格式段文件可共存（渐进迁移）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: WAL 段 tick 记录 / 段文件原始字节
#   fields: 待编码 tick 记录（编码方向）+ 待解码段文件字节（解码方向，magic number 区分格式）
#   code: tsv_codec.encode_tsv/decode_tsv（__init__ 再导出 L29）
# 层: 算法
# - id: A1
#   name_zh: ① TSV 编解码
#   name_en: TsvCodec/encode_tsv/decode_tsv
#   intro: 把 tick 记录编成 TSV 纯文本段、或把 TSV 段解回记录，格式向后兼容
#   desc: 包公共面再导出 tsv_codec 的 TsvCodec/encode_tsv/decode_tsv（L29）；TSV 段无 magic 纯文本；编码失败返回空 bytes+log、解码失败返回空 list+log（[ERROR_CONTRACT]）；当前唯一已交付 codec，Protobuf 为 P3 远期备选（docstring L21-22）
#   inputs: I1
#   outputs: TSV 字节 / tick 记录列表
#   invariant: TSV格式向后兼容
# - id: A2
#   name_zh: ② 编解码器路由注册表
#   name_en: CodecRegistry/get_registry
#   intro: 按段文件开头的 magic number 自动选对应 codec 解码，不认识的按 TSV 兜底
#   desc: 包公共面再导出 codec_registry 的 CodecRegistry/get_registry（L30）；Proto 段以 PB\\x01 开头、TSV 段无 magic，按 magic 路由；未知 magic number 按 TSV 降级；混合格式段文件可共存支持渐进迁移（docstring L24-27/[INVARIANTS]）
#   inputs: I1
#   outputs: 按 magic 路由的解码结果
#   invariant: magic number区分格式；混合格式段文件可共存
# 层: 输出
# - id: O1
#   name_zh: WAL 编解码公共 API 面（6 符号）
#   name_en: __all__（TsvCodec/encode_tsv/decode_tsv/CodecRegistry/get_registry）
#   intro: WAL 段文件编解码层的统一 import 面，供 wal_writer 写盘与回放读取
#   downstream: zephyr.data.wal_writer MOD-GOV-wal_writer（可选接入，[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> O1
# A2 --> O1
"""

from zephyr.data.wal_codec.codec_registry import CodecRegistry, get_registry
from zephyr.data.wal_codec.tsv_codec import TsvCodec, decode_tsv, encode_tsv

__all__ = [
    "TsvCodec",
    "encode_tsv",
    "decode_tsv",
    "CodecRegistry",
    "get_registry",
]
