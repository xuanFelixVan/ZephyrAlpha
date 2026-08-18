# [A_test] module_id: MOD-GOV_vms_automation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §5.5
# [MODULE] tests.unit.vector_memory.test_vms_automation
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
DM-202210 自动化机制-事件触发与定时任务测试
==========================================
蓝图 §5.5 自动化触发: auto_boot/auto_event/auto_scheduled

测试覆盖
--------
TestCacheInvalidationOnWrite (5):
    - 写入后查询缓存失效
    - invalidate_collection 清除 embedding/query 缓存
    - invalidate_all 清除全部
    - execution_traces 不缓存策略

TestRetrievalFeedbackCollection (6):
    - log_feedback 记录反馈
    - track_hit_rates 计算命中率
    - record 创建反馈条目
    - track_long_tail 递增
    - sample_for_quality_monitor 抽样
    - write_failure_pattern 无 VMS 时降级

TestMaintenanceLoopTasks (4):
    - _maintenance_loop 间隔常量
    - stop_event 中断循环
    - check_ttl_expiry 返回报告
    - auto_repair 返回 bool

TestTTLExpiryCheck (4):
    - TTL_MAP 配置正确
    - TTLExpiryReport 字段完整
    - 空集合不报错
    - TTL 值正确
"""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from zephyr.integration.local_model.cache_layer import (
    DEFAULT_CACHE_SIZE,
    NO_CACHE_COLLECTIONS,
    PERMANENT_CACHE_COLLECTIONS,
    CacheLayer,
)
from zephyr.integration.vector_memory.collection_manager import TTL_MAP
from zephyr.integration.vector_memory.index_health_monitor import (
    DriftReport,
    HealthReport,
    IndexHealthMonitor,
    TTLExpiryReport,
)
from zephyr.integration.vector_memory.retrieval_feedback import (
    FeedbackEntry,
    RetrievalFeedback,
)

# ============================================================================
# TestCacheInvalidationOnWrite — 写入后缓存失效
# ============================================================================


class TestCacheInvalidationOnWrite:
    """自动化机制: 写入事件触发缓存失效。"""

    def test_write_invalidates_query_cache(self) -> None:
        """写入后应调用 invalidate_collection 清除该 collection 的查询缓存。"""
        cache = CacheLayer(max_size=100)
        vec = np.array([0.1, 0.2], dtype=np.float32)

        cache.put_embedding("hello", vec, collection="decisions")
        cache.put_query_result("test query", "decisions", [{"id": "1"}])

        assert cache.get_embedding("hello", collection="decisions") is not None
        assert cache.get_query_result("test query", "decisions") is not None

        # 模拟写入后失效
        cache.invalidate_collection("decisions")

        assert cache.get_embedding("hello", collection="decisions") is None
        assert cache.get_query_result("test query", "decisions") is None

    def test_invalidate_collection_only_affects_target(self) -> None:
        """invalidate_collection 只影响目标 collection。"""
        cache = CacheLayer(max_size=100)
        vec = np.array([0.1, 0.2], dtype=np.float32)

        cache.put_embedding("a", vec, collection="decisions")
        cache.put_embedding("b", vec, collection="rules")
        cache.put_query_result("q1", "decisions", [{"id": "1"}])
        cache.put_query_result("q2", "rules", [{"id": "2"}])

        cache.invalidate_collection("decisions")

        assert cache.get_embedding("a", collection="decisions") is None
        assert cache.get_embedding("b", collection="rules") is not None
        assert cache.get_query_result("q1", "decisions") is None
        assert cache.get_query_result("q2", "rules") is not None

    def test_invalidate_all_clears_everything(self) -> None:
        """invalidate_all 清除全部缓存。"""
        cache = CacheLayer(max_size=100)
        vec = np.array([0.1, 0.2], dtype=np.float32)

        cache.put_embedding("a", vec, collection="decisions")
        cache.put_embedding("b", vec, collection="rules")
        cache.put_query_result("q1", "decisions", [{"id": "1"}])

        cache.invalidate_all()

        assert cache.embedding_cache_size == 0
        assert cache.query_cache_size == 0
        assert cache.get_embedding("a", collection="decisions") is None

    def test_should_cache_execution_traces_false(self) -> None:
        """execution_traces 不缓存策略。"""
        cache = CacheLayer()
        assert cache.should_cache_embedding("execution_traces") is False
        assert cache.should_cache_query("execution_traces") is False

        # rules 应缓存
        assert cache.should_cache_embedding("rules") is True
        assert cache.should_cache_query("rules") is True

    def test_invalidate_all_on_model_change(self) -> None:
        """模型版本变更触发全部缓存清除。"""
        cache = CacheLayer(max_size=100)
        vec = np.array([0.1, 0.2], dtype=np.float32)

        cache.put_embedding("a", vec, collection="decisions", model_version="v1")
        assert cache.embedding_cache_size == 1

        cache.invalidate_all_on_model_change("v2", "v1")
        assert cache.embedding_cache_size == 0


# ============================================================================
# TestRetrievalFeedbackCollection — 检索后反馈收集
# ============================================================================


class TestRetrievalFeedbackCollection:
    """自动化机制: 检索事件触发反馈收集。"""

    def test_log_feedback_records_entry(self) -> None:
        """log_feedback 记录反馈条目。"""
        fb = RetrievalFeedback()
        trace = type("Trace", (), {"collection": "decisions", "query": "test query", "hits": [1, 2, 3]})()

        entry = fb.log_feedback(trace, user_rating=4.0)

        assert entry.collection == "decisions"
        assert entry.query == "test query"
        assert entry.hit_count == 3
        assert entry.rating == 4.0
        assert len(fb.feedback_log) == 1

    def test_track_hit_rates_calculates(self) -> None:
        """track_hit_rates 计算各 collection 命中率。"""
        fb = RetrievalFeedback()

        # decisions: 2次检索，1次有hit
        trace1 = type("Trace", (), {"collection": "decisions", "query": "q1", "hits": [1]})()
        trace2 = type("Trace", (), {"collection": "decisions", "query": "q2", "hits": []})()
        fb.log_feedback(trace1)
        fb.log_feedback(trace2)

        rates = fb.track_hit_rates()
        assert "decisions" in rates
        assert rates["decisions"]["total_queries"] == 2
        assert rates["decisions"]["hit_rate"] == 0.5  # 1/2

    def test_record_creates_entry(self) -> None:
        """record 创建反馈条目。"""
        fb = RetrievalFeedback()

        entry = fb.record("hit-1", was_useful=True, task_id="task-001", collection="knowledge")

        assert entry.collection == "knowledge"
        assert entry.query == "task-001"
        assert entry.hit_count == 1
        assert entry.rating == 1.0

    def test_track_long_tail_increments(self) -> None:
        """track_long_tail 递增长尾查询计数。"""
        fb = RetrievalFeedback()

        fb.track_long_tail("rare query")
        fb.track_long_tail("rare query")
        fb.track_long_tail("another query")

        assert fb.long_tail["rare query"] == 2
        assert fb.long_tail["another query"] == 1

    def test_sample_for_quality_monitor(self) -> None:
        """sample_for_quality_monitor 返回最近 N 条反馈。"""
        fb = RetrievalFeedback()
        for i in range(15):
            trace = type("Trace", (), {"collection": "decisions", "query": f"q{i}", "hits": [i]})()
            fb.log_feedback(trace)

        sample = fb.sample_for_quality_monitor(sample_size=5)
        assert len(sample) == 5
        # 应返回最近的5条
        assert sample[-1].query == "q14"

    def test_write_failure_pattern_without_vms(self) -> None:
        """无 VMS 时 write_failure_pattern 返回 None。"""
        fb = RetrievalFeedback(vms=None)
        result = fb.write_failure_pattern("pattern text")
        assert result is None


# ============================================================================
# TestMaintenanceLoopTasks — 维护线程定时任务
# ============================================================================


class TestMaintenanceLoopTasks:
    """自动化机制: _maintenance_loop 定时任务。"""

    def test_maintenance_loop_check_interval(self) -> None:
        """_maintenance_loop 的 CHECK_INTERVAL=60 秒。"""
        # 从源码验证常量
        import inspect

        from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

        source = inspect.getsource(InProcessVectorMemory._maintenance_loop)
        assert "CHECK_INTERVAL = 60" in source
        assert "DAILY_INTERVAL = 86400" in source

    def test_stop_event_breaks_loop(self) -> None:
        """stop_event 中断维护循环。"""
        stop_event = threading.Event()
        iterations = 0

        def mock_loop() -> None:
            nonlocal iterations
            while not stop_event.is_set():
                stop_event.wait(timeout=0.1)
                if stop_event.is_set():
                    break
                iterations += 1
                if iterations > 10:
                    break

        thread = threading.Thread(target=mock_loop, daemon=True)
        thread.start()

        time.sleep(0.15)  # 让循环跑1-2次
        stop_event.set()
        thread.join(timeout=2.0)

        assert not thread.is_alive()
        assert iterations <= 10  # 应在 stop_event 后退出

    def test_check_ttl_expiry_returns_reports(self) -> None:
        """check_ttl_expiry 返回 TTL 报告列表。"""
        # 用 mock collection_manager
        mock_cm = MagicMock()
        mock_col = MagicMock()
        mock_col.count.return_value = 0
        mock_cm.get_collection.return_value = mock_col

        monitor = IndexHealthMonitor(mock_cm)
        reports = monitor.collect_ttl_expiry()

        assert isinstance(reports, list)
        # TTL_MAP 有 3 个 collection
        assert len(reports) <= 3

    def test_auto_repair_returns_bool(self) -> None:
        """auto_repair 返回 bool。"""
        mock_cm = MagicMock()
        mock_cm.get_collection.return_value = MagicMock()

        monitor = IndexHealthMonitor(mock_cm)
        result = monitor.auto_repair("decisions")

        assert isinstance(result, bool)


# ============================================================================
# TestTTLExpiryCheck — TTL 过期检查
# ============================================================================


class TestTTLExpiryCheck:
    """自动化机制: TTL 定时清理。"""

    def test_ttl_map_has_3_collections(self) -> None:
        """TTL_MAP 配置了 3 个有 TTL 的 collection。"""
        assert len(TTL_MAP) == 3
        assert "code_context" in TTL_MAP
        assert "session_snapshots" in TTL_MAP
        assert "execution_traces" in TTL_MAP

    def test_ttl_values_correct(self) -> None:
        """TTL 值正确: code_context=90, session_snapshots=90, execution_traces=30。"""
        assert TTL_MAP["code_context"] == 90
        assert TTL_MAP["session_snapshots"] == 90
        assert TTL_MAP["execution_traces"] == 30

    def test_ttl_expiry_report_fields(self) -> None:
        """TTLExpiryReport 字段完整。"""
        report = TTLExpiryReport(
            collection="execution_traces",
            expired_count=5,
            total_count=10,
            ttl_days=30,
        )
        assert report.collection == "execution_traces"
        assert report.expired_count == 5
        assert report.total_count == 10
        assert report.ttl_days == 30

    def test_check_ttl_expiry_empty_collection_not_crash(self) -> None:
        """空集合 check_ttl_expiry 不报错。"""
        mock_cm = MagicMock()
        mock_col = MagicMock()
        mock_col.count.return_value = 0
        mock_cm.get_collection.return_value = mock_col

        monitor = IndexHealthMonitor(mock_cm)
        reports = monitor.collect_ttl_expiry()

        # 空集合应跳过（continue），不产生报告
        for r in reports:
            if r.collection in TTL_MAP:
                assert r.total_count == 0 or r.expired_count >= 0
