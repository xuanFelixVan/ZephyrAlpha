# [A_test] module_id: MOD-GOV_vms_adversarial_injection | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §9
# [MODULE] tests.unit.vector_memory.test_vms_adversarial_injection
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
VMS 红蓝对抗测试 — 向量注入与投毒检测
======================================
蓝图 §9 · §14 F5 · 对抗性检索投毒评估

覆盖:
  - ProvenanceEnforcer 伪造 origin / 篡改 audit_chain / 缺失 arbitration
  - EmbeddingRouter 异常输入防御（空文本/超长文本/SQL注入）
  - CBAC human-gated Collection 拒绝 AI 操作
  - InMemoryFakeVMS 对抗性写入行为
"""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError


class TestAdversarialProvenance:
    """红蓝对抗：ProvenanceEnforcer 投毒检测

    #ARCH-VMS-WRITETRACE-CONSOLIDATE-001 后，WriteTrace schema 已强制
    origin(min_length=1)/audit_chain(min_length=1)——空值在构造时即抛
    ValidationError（fail-fast at construction），比到 ProvenanceEnforcer
    才拒绝更强（防御前置）。以下测试验证 schema 层拦截。
    """

    def test_forged_empty_origin_rejected(self):
        """伪造空 origin → schema 层即拒绝（ValidationError，无需到 Enforcer）"""
        from zephyr.integration.vector_memory.vms_schemas import WriteTrace

        with pytest.raises(ValidationError):
            WriteTrace(origin="", audit_chain=["session-1"], arbitration="autonomous")

    def test_forged_whitespace_origin_rejected(self):
        """伪造纯空格 origin → str_strip_whitespace 后为空，schema 层拒绝"""
        from zephyr.integration.vector_memory.vms_schemas import WriteTrace

        with pytest.raises(ValidationError):
            WriteTrace(origin="   ", audit_chain=["session-1"], arbitration="autonomous")

    def test_tampered_empty_audit_chain_rejected(self):
        """篡改 audit_chain 为空列表 → schema 层 min_length=1 拒绝"""
        from zephyr.integration.vector_memory.vms_schemas import WriteTrace

        with pytest.raises(ValidationError):
            WriteTrace(origin="orc/decision", audit_chain=[], arbitration="autonomous")

    def test_missing_arbitration_rejected(self):
        """缺失 arbitration（空串）→ schema 允许（可选字段），ProvenanceEnforcer 业务拒绝"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer
        from zephyr.integration.vector_memory.vms_schemas import WriteTrace

        trace = WriteTrace(origin="orc/decision", audit_chain=["session-1"], arbitration="")
        assert ProvenanceEnforcer.validate(trace) is False

    def test_none_writetrace_rejected(self):
        """None WriteTrace → 必须拒绝"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.validate(None) is False

    def test_valid_writetrace_accepted(self):
        """合法 WriteTrace → 必须通过"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer
        from zephyr.integration.vector_memory.vms_schemas import WriteTrace

        trace = WriteTrace(
            origin="orc/decision",
            audit_chain=["session-1", "ai-12"],
            arbitration="autonomous",
        )
        assert ProvenanceEnforcer.validate(trace) is True

    def test_provenance_attach_adds_validated_flag(self):
        """attach() 必须将 provenance 绑定到 metadata 并标记 validated=True"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        metadata = {"content": "test"}
        provenance = {
            "origin": "orc/decision",
            "audit_chain": ["session-1"],
            "arbitration": "autonomous",
        }
        result = ProvenanceEnforcer.attach(metadata, provenance)
        assert "provenance" in result
        assert result["provenance"]["validated"] is True
        assert result["provenance"]["origin"] == "orc/decision"
        assert result["content"] == "test"

    def test_provenance_attach_does_not_mutate_original(self):
        """attach() 不得修改原始 metadata"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        metadata = {"content": "test"}
        provenance = {"origin": "x", "audit_chain": ["y"], "arbitration": "z"}
        ProvenanceEnforcer.attach(metadata, provenance)
        assert "provenance" not in metadata


class TestCBACAdversarial:
    """红蓝对抗：CBAC human-gated Collection 防御"""

    def test_cbau_check_rejects_human_gated_for_ai(self):
        """human-gated Collection (rules) → cbau_check 必须拒绝 AI 操作"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.cbau_check("rules", "write", ai_session="ai-12") is False

    def test_cbau_check_allows_autonomous_collection(self):
        """autonomous Collection → cbau_check 必须允许"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.cbau_check("code_context", "write") is True

    def test_cbau_check_allows_supervised_collection(self):
        """supervised Collection → cbau_check 必须允许"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.cbau_check("decisions", "write") is True

    def test_ai_autonomy_gate_rejects_human_gated(self):
        """human-gated Collection → ai_autonomy_gate 必须拒绝 AI session"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.ai_autonomy_gate("rules", session_type="ai") is False

    def test_ai_autonomy_gate_allows_autonomous(self):
        """autonomous Collection → ai_autonomy_gate 必须允许 AI session"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.ai_autonomy_gate("code_context", session_type="ai") is True

    def test_ai_autonomy_gate_allows_human_session(self):
        """human-gated Collection + human session → 必须允许"""
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        assert ProvenanceEnforcer.ai_autonomy_gate("rules", session_type="human") is True


class TestAdversarialEmbeddingInput:
    """红蓝对抗：EmbeddingRouter 异常输入防御"""

    @pytest.fixture
    def in_memory_router(self):
        """创建 InMemory 降级模式的 EmbeddingRouter（不加载真实模型）"""
        from zephyr.integration.local_model.embedding_router import EmbeddingRouter

        router = EmbeddingRouter()
        router.fallback_mode = "in_memory"
        router.bge_small_dim = 384
        return router

    def test_empty_text_embedding_returns_vector(self, in_memory_router):
        """空文本嵌入 → 必须返回向量（零向量），不得崩溃"""
        vec = in_memory_router.embed("", "decisions")
        assert isinstance(vec, np.ndarray)
        assert vec.shape[0] == 384

    def test_super_long_text_embedding_no_crash(self, in_memory_router):
        """超长文本 (>10000字符) → 必须返回向量，不得 OOM"""
        long_text = "A" * 10001
        vec = in_memory_router.embed(long_text, "knowledge")
        assert isinstance(vec, np.ndarray)
        assert vec.shape[0] == 384

    def test_sql_injection_string_no_crash(self, in_memory_router):
        """SQL 注入字符串 → 必须返回向量，不得执行注入"""
        sql_injection = "'; DROP TABLE vectors; --"
        vec = in_memory_router.embed(sql_injection, "lessons")
        assert isinstance(vec, np.ndarray)
        assert vec.shape[0] == 384

    def test_path_traversal_string_no_crash(self, in_memory_router):
        """路径遍历字符串 → 必须返回向量，不得遍历文件系统"""
        path_traversal = "../../../etc/passwd"
        vec = in_memory_router.embed(path_traversal, "code_context")
        assert isinstance(vec, np.ndarray)

    def test_unicode_bomb_no_crash(self, in_memory_router):
        """Unicode 炸弹 → 必须返回向量，不得崩溃"""
        unicode_bomb = "\u200b" * 1000 + "malicious"
        vec = in_memory_router.embed(unicode_bomb, "rules")
        assert isinstance(vec, np.ndarray)

    def test_unknown_collection_in_memory_returns_vector(self, in_memory_router):
        """InMemory 降级模式下未知 Collection → 返回零向量（安全发现：降级模式不校验collection名）"""
        vec = in_memory_router.embed("test", "malicious_collection")
        assert isinstance(vec, np.ndarray)
        assert np.all(vec == 0.0)

    def test_in_memory_fallback_returns_zero_vector(self, in_memory_router):
        """InMemory 降级模式 → 必须返回零向量"""
        vec = in_memory_router.embed("test", "decisions")
        assert np.all(vec == 0.0)


class TestAdversarialWriteInjection:
    """红蓝对抗：InMemoryFakeVMS 对抗性写入行为"""

    @pytest.fixture
    def fake_vms(self):
        from zephyr.integration.vector_memory.in_memory_fake_vms import InMemoryFakeVMS

        return InMemoryFakeVMS()

    def test_unknown_collection_write_rejected(self, fake_vms):
        """未知 Collection 写入 → 必须抛 KeyError"""
        with pytest.raises(KeyError):
            fake_vms.write("malicious_collection", "evil content")

    def test_malicious_metadata_does_not_break_search(self, fake_vms):
        """恶意 metadata → search 不得崩溃"""
        fake_vms.write(
            "knowledge",
            "normal content",
            metadata={"origin": "'; DROP TABLE--", "audit_chain": ["evil"]},
        )
        results = fake_vms.search("knowledge", "normal")
        assert len(results) == 1
        assert results[0]["content"] == "normal content"

    def test_empty_content_write_succeeds(self, fake_vms):
        """空内容写入 → 必须成功（不崩溃），search 返回空"""
        doc_id = fake_vms.write("knowledge", "")
        assert doc_id.startswith("fake::knowledge::")
        results = fake_vms.search("knowledge", "")
        assert len(results) == 1

    def test_write_returns_unique_id(self, fake_vms):
        """多次写入 → 每次必须返回唯一 doc_id"""
        id1 = fake_vms.write("knowledge", "content1")
        id2 = fake_vms.write("knowledge", "content2")
        assert id1 != id2

    def test_shutdown_clears_all_data(self, fake_vms):
        """shutdown → 必须清空所有数据"""
        fake_vms.write("knowledge", "content")
        fake_vms.shutdown()
        assert fake_vms.started is False
        results = fake_vms.search("knowledge", "content")
        assert len(results) == 0

    def test_search_does_not_leak_other_collections(self, fake_vms):
        """search 不得跨 Collection 泄漏数据"""
        fake_vms.write("knowledge", "secret_knowledge")
        fake_vms.write("decisions", "secret_decision")
        results = fake_vms.search("knowledge", "secret")
        assert all(r["content"] == "secret_knowledge" for r in results)
        assert len(results) == 1

    def test_k_limit_enforced(self, fake_vms):
        """k 参数限制 → search 不得返回超过 k 条结果"""
        for i in range(10):
            fake_vms.write("knowledge", f"content_{i}")
        results = fake_vms.search("knowledge", "content", k=3)
        assert len(results) <= 3
