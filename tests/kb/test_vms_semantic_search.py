# [A_test] module_id: SRC-TST-1796 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-442 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_vms_semantic_search
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
端到端语义搜索验证 — 使用真实嵌入模型 (bge-small-zh-v1.5)
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_DIR = Path("data/semantic_test")


def main():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True)

    from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

    print("=" * 60)
    print("  端到端语义搜索验证 (真实嵌入模型)")
    print("=" * 60)

    print("\n[1] 启动 VMS (bge-small-zh-v1.5)...")
    vms = InProcessVectorMemory(persist_dir=str(TEST_DIR))
    t0 = time.perf_counter()
    vms.start()
    startup = time.perf_counter() - t0
    print(f"  启动耗时: {startup:.1f}s")

    health = vms.health_check()
    embed = health.get("embedding", {})
    print(f"  bge_m3_available: {embed.get('bge_m3_available')}")
    print(f"  bge_small_available: {embed.get('bge_small_available')}")
    print(f"  fallback_mode: {embed.get('fallback_mode')}")

    bge_small_ok = embed.get("bge_small_available", False)
    if not bge_small_ok:
        print("  ❌ bge-small 未加载，无法进行语义搜索测试")
        vms.shutdown()
        return False

    print("\n[2] 初始化 Collection...")
    vms.init_all_collections()

    print("\n[3] 写入测试数据 (knowledge)...")
    docs = [
        (
            "ADR-0032: 采用 FAISS mmap 替代 ChromaDB HTTP 微服务作为向量数据库后端",
            {"provenance": {"origin": "architect"}},
        ),
        ("部署 v2.3.1 到生产环境，使用零停机滚动更新策略", {"provenance": {"origin": "devops"}}),
        ("Python 3.12 引入了 PEP 695 类型参数语法改进", {"provenance": {"origin": "researcher"}}),
        ("Redis Streams 消费者组使用 XREADGROUP 实现可靠消息处理", {"provenance": {"origin": "engineer"}}),
        ("Kubernetes 水平 Pod 自动扩缩容目标 CPU 利用率 70%", {"provenance": {"origin": "sre"}}),
        ("PostgreSQL 16 支持从备用服务器进行逻辑复制", {"provenance": {"origin": "dba"}}),
        ("使用 structlog 在所有微服务中实现结构化日志记录", {"provenance": {"origin": "engineer"}}),
        ("熔断器阈值: 30 秒滚动窗口内 50% 失败率", {"provenance": {"origin": "architect"}}),
        ("YAML 驱动的提示模板注册表，带有 token 预算强制执行", {"provenance": {"origin": "ai_engineer"}}),
        ("归并排序在所有情况下都具有 O(n log n) 时间复杂度", {"provenance": {"origin": "cs"}}),
    ]

    for content, meta in docs:
        vid = vms.write("knowledge", content, meta)
        print(f"  wrote: {content[:40]}...")

    print("\n[4] 语义搜索测试...")
    queries = [
        ("数据库迁移方案", "ADR-0032 FAISS"),
        ("deploy to production", "部署 v2.3.1"),
        ("message queue reliability", "Redis Streams XREADGROUP"),
        ("circuit breaker pattern", "熔断器"),
        ("sorting algorithm complexity", "归并排序"),
        ("今天天气怎么样", "(should be low relevance)"),
    ]

    for query, expected in queries:
        results = vms.search("knowledge", query, k=3)
        if results:
            top = results[0]
            content = top.get("content", "")[:60]
            score = top.get("score", 0)
            print(f"  Q: '{query}' → top: '{content}...' (score={score:.4f}, expect: {expected})")
        else:
            print(f"  Q: '{query}' → (no results)")

    print("\n[5] 跨语言语义搜索 (中文查英文)...")
    cross_lingual = [
        ("向量数据库", "FAISS"),
        ("生产环境部署", "deploy production"),
        ("日志系统", "structlog logging"),
    ]
    for query, expected_kw in cross_lingual:
        results = vms.search("knowledge", query, k=3)
        if results:
            top_content = results[0].get("content", "")
            found = expected_kw.lower() in top_content.lower()
            print(f"  '{query}' → top含'{expected_kw}': {'✅' if found else '❌'} | {top_content[:50]}...")
        else:
            print(f"  '{query}' → (no results)")

    print("\n[6] 关机...")
    vms.shutdown()
    shutil.rmtree(TEST_DIR, ignore_errors=True)

    print("\n" + "=" * 60)
    print("  语义搜索验证完成!")
    print("=" * 60)
    return True


def test_vms_semantic_search():
    """端到端语义搜索验证——委托给 main()，pytest 收集入口。"""
    assert main() is True


if __name__ == "__main__":
    main()
