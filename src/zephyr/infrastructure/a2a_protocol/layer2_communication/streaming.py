# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.streaming
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_streaming | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Streaming — A2A 流式传输"""

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
