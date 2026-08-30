# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.streaming
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Streaming — A2A 流式传输

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: streaming.py
# 层: 算法
# - id: A1
#   name_zh: ① StreamingManager
#   name_en: StreamingManager
#   intro: class StreamingManager 源码 L51-L61
#   desc: 公共方法（定义序）: stream_chunk, assemble_stream；源码 L51-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: StreamingManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from collections.abc import Generator


class StreamingManager:
    BUFFER_SIZE = 4096

    @staticmethod
    def stream_chunk(content: str, chunk_size: int = 256) -> Generator[str, None, None]:
        for i in range(0, len(content), chunk_size):
            yield content[i : i + chunk_size]

    @staticmethod
    def assemble_stream(chunks: list) -> str:
        return "".join(chunks)
