# [A_test] module_id: MOD-CONTEXT_ENGINE_injector_real_backend | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §4 Phase 1 P1-1
# [MODULE] tests.context.test_context_injector_real_backend_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""ContextInjector 真实后端集成验证（07 号文 §4 Phase 1 P1-1 验收补充）。

与 test_context_injector_memory_wiring.py（fake client / 内存后端）不同，
本文件走**真实生产路径**：``get_unified_memory_api()``（prefer_vms 默认 True）
+ ``ContextInjector()`` 懒加载默认适配器，验证 VMS 后端可用时
``inject_by_keyword()`` 返回非空 InjectedContext 且 provenance 可解析为
``unified_memory:{topic}:{chunk_id}``。

降级纪律（不假绿）：VMS 后端在测试环境不可用时，``get_unified_memory_api()``
静默降级内存后端（空），inject 必然返回空——此时模块级 skipif 整体跳过，
不把"降级空结果"冒充集成验证通过。探针写入共享真实后端（CBAC 关闭，
CBAC 校验由 unified_memory_api 自身测试覆盖）；探针检索为空
（embedding/索引链路不可用）同样 runtime skip。
探针数据落盘 topic=ce_integration_probe（VMS "knowledge" 集合兜底路由），
内容含唯一 token，可与生产数据区分。
"""

from __future__ import annotations

import uuid

import pytest


def _build_real_api():
    """按生产路径构造 UnifiedMemoryAPI 单例（VMS 优先，不可构造返回 None）。"""
    try:
        from zephyr.intelligence.model_evaluation.unified_memory_api import get_unified_memory_api

        return get_unified_memory_api(reset=True)
    except Exception:  # noqa: BLE001 — 收集期探测，任何构造失败都降级为 skip
        return None


def _real_vms_active(api) -> bool:
    """真实 VMS 后端是否激活（降级到内存后端则为 False）。"""
    if api is None:
        return False
    backend = getattr(api, "backend", None)
    return bool(getattr(backend, "is_vms_available", False))


_REAL_API = _build_real_api()
_REAL_VMS_ACTIVE = _real_vms_active(_REAL_API)

pytestmark = pytest.mark.skipif(
    not _REAL_VMS_ACTIVE,
    reason="VMS 后端不可用——get_unified_memory_api() 静默降级内存后端（inject 必为空），跳过真实后端集成验证而非假绿",
)


class TestRealBackendInjectIntegration:
    """真实后端（VMS）下 inject 段非空 + provenance 格式可解析。"""

    def test_inject_non_empty_and_provenance_parseable(self) -> None:
        from zephyr.autonomy_core.context.context_injector import ContextInjector
        from zephyr.intelligence.model_evaluation.unified_memory_api import (
            UnifiedMemoryAPI,
            build_provenance,
            get_unified_memory_api,
        )

        api = get_unified_memory_api()  # 复用模块级探测构造的单例（真实后端）
        token = f"CE-INTEGRATION-PROBE-{uuid.uuid4().hex[:12]}"
        prov = build_provenance(
            origin="test:ce_inject_real_backend",
            audit_chain=["T-CE-INJECT-REAL-BACKEND"],
        )
        # 探针写入共享真实后端实例；CBAC 关闭——权限校验归 unified_memory_api 自身测试，
        # 本测试聚焦 inject 段检索-装配链路。
        writer = UnifiedMemoryAPI(backend=api.backend, enforce_capability=False)
        writer.write(
            topic="ce_integration_probe",
            content=f"集成探针 {token}：inject 段真实后端验证（上下文引擎注入链路）",
            provenance=prov,
        )

        hits = api.search(token, k=3)
        if not hits:
            pytest.skip(
                "VMS 检索无命中（实测 2026-08-30：count()=0 集合为空 / embedding 检索链路不可用），"
                "inject 将降级为空——跳过而非假绿"
            )

        injector = ContextInjector()  # 无 search_client → 懒加载默认 UnifiedMemoryAPI 适配器（生产路径）
        result = injector.inject_by_keyword(token)

        assert result.context != "", "真实后端检索命中时 inject 不得返回空上下文"
        assert token in result.context
        assert result.retrieval_mode == "keyword"
        assert result.provenances, "provenances 不得为空"
        for p in result.provenances:
            assert p.startswith("unified_memory:"), f"provenance 前缀漂移: {p}"
            topic, sep, chunk_id = p[len("unified_memory:") :].partition(":")
            assert sep and topic and chunk_id, f"provenance 须可解析为 unified_memory:{{topic}}:{{chunk_id}}: {p}"
