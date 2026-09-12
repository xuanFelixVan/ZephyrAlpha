# [A_test] module_id: MOD-GOV_streaming | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_streaming
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_streaming.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer2_communication.streaming import StreamingManager


class TestStreamingManager:
    def test_buffer_size_constant(self):
        assert StreamingManager.BUFFER_SIZE == 4096

    def test_stream_chunk_default_size(self):
        content = "a" * 600
        chunks = list(StreamingManager.stream_chunk(content))
        assert len(chunks) == 3
        assert len(chunks[0]) == 256
        assert len(chunks[1]) == 256
        assert len(chunks[2]) == 88

    def test_stream_chunk_custom_size(self):
        content = "abcdefghij"
        chunks = list(StreamingManager.stream_chunk(content, chunk_size=3))
        assert chunks == ["abc", "def", "ghi", "j"]

    def test_stream_chunk_exact_size(self):
        content = "abcdef"
        chunks = list(StreamingManager.stream_chunk(content, chunk_size=3))
        assert chunks == ["abc", "def"]

    def test_stream_chunk_empty(self):
        chunks = list(StreamingManager.stream_chunk(""))
        assert chunks == []

    def test_stream_chunk_single_char(self):
        chunks = list(StreamingManager.stream_chunk("x"))
        assert chunks == ["x"]

    def test_assemble_stream(self):
        chunks = ["abc", "def", "ghi"]
        result = StreamingManager.assemble_stream(chunks)
        assert result == "abcdefghi"

    def test_assemble_stream_empty(self):
        result = StreamingManager.assemble_stream([])
        assert result == ""

    def test_roundtrip(self):
        content = "Hello, World! " * 100
        chunks = list(StreamingManager.stream_chunk(content, chunk_size=50))
        reassembled = StreamingManager.assemble_stream(chunks)
        assert reassembled == content
