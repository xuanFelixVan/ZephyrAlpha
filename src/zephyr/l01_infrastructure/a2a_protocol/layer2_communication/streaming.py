"""Streaming — A2A 流式传输"""

from typing import Generator, Dict, Any


class StreamingManager:
    BUFFER_SIZE = 4096

    @staticmethod
    def stream_chunk(content: str, chunk_size: int = 256) -> Generator[str, None, None]:
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]

    @staticmethod
    def assemble_stream(chunks: list) -> str:
        return "".join(chunks)
