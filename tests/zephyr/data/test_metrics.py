"""IntegratorMetrics 单测（MOD-L00-004 §11 可观测性）。"""
import os
import tempfile
from pathlib import Path

import pytest

from src.zephyr.data.metrics import IntegratorMetrics, get_metrics, reset_metrics


@pytest.fixture
def metrics(tmp_path):
    """每个测试用独立的 metrics 实例 + 临时输出文件。"""
    out = tmp_path / "metrics.prom"
    return IntegratorMetrics(output_file=out)


class TestIntegratorMetrics:
    """IntegratorMetrics 测试。"""

    def test_record_task_counter(self, metrics):
        """record_task 增加 task_total 计数。"""
        metrics.record_task("t1", "ifind", "SUCCESS", 5.0, 100)
        metrics.record_task("t1", "ifind", "SUCCESS", 6.0, 200)
        metrics.record_task("t1", "ifind", "FAILED", 1.0, 0)
        rendered = metrics.render()
        assert 'integrator_task_total{task_id="t1",source="ifind",status="SUCCESS"} 2' in rendered
        assert 'integrator_task_total{task_id="t1",source="ifind",status="FAILED"} 1' in rendered

    def test_record_task_duration_histogram(self, metrics):
        """record_task 更新耗时直方图。"""
        # 3 个耗时样本：0.05s, 2.0s, 100s
        metrics.record_task("t1", "ifind", "SUCCESS", 0.05, 10)
        metrics.record_task("t1", "ifind", "SUCCESS", 2.0, 20)
        metrics.record_task("t1", "ifind", "SUCCESS", 100.0, 30)
        rendered = metrics.render()
        # count=3, sum=102.05
        assert 'integrator_task_duration_seconds_count{task_id="t1",source="ifind"} 3' in rendered
        assert 'integrator_task_duration_seconds_sum{task_id="t1",source="ifind"} 102.05' in rendered
        # le=0.1 桶应含 1 个（0.05）
        assert 'integrator_task_duration_seconds_bucket{le="0.1",task_id="t1",source="ifind"} 1' in rendered
        # le=5.0 桶应含 2 个（0.05+2.0）
        assert 'integrator_task_duration_seconds_bucket{le="5.0",task_id="t1",source="ifind"} 2' in rendered
        # le="+Inf" 桶应含 3 个
        assert 'integrator_task_duration_seconds_bucket{le="+Inf",task_id="t1",source="ifind"} 3' in rendered

    def test_record_task_rows(self, metrics):
        """record_task 累加 rows_fetched_total。"""
        metrics.record_task("t1", "ifind", "SUCCESS", 1.0, 100)
        metrics.record_task("t1", "ifind", "SUCCESS", 1.0, 200)
        rendered = metrics.render()
        assert 'integrator_rows_fetched_total{task_id="t1",source="ifind"} 300' in rendered

    def test_record_rate_limit(self, metrics):
        """record_rate_limit 累加限流命中。"""
        metrics.record_rate_limit("ifind")
        metrics.record_rate_limit("ifind")
        metrics.record_rate_limit("akshare")
        rendered = metrics.render()
        assert 'integrator_rate_limit_hits_total{source="ifind"} 2' in rendered
        assert 'integrator_rate_limit_hits_total{source="akshare"} 1' in rendered

    def test_record_retry(self, metrics):
        """record_retry 累加重试次数。"""
        metrics.record_retry("t1", "ifind")
        metrics.record_retry("t1", "ifind")
        rendered = metrics.render()
        assert 'integrator_retry_total{task_id="t1",source="ifind"} 2' in rendered

    def test_set_uptime(self, metrics):
        """set_uptime 设置会话时长。"""
        metrics.set_uptime(3600.5)
        rendered = metrics.render()
        assert "integrator_session_uptime_seconds 3600.50" in rendered

    def test_flush_writes_file(self, metrics, tmp_path):
        """flush 写入 .prom 文件。"""
        metrics.record_task("t1", "ifind", "SUCCESS", 1.0, 10)
        ok = metrics.flush()
        assert ok is True
        out = tmp_path / "metrics.prom"
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "integrator_task_total" in content
        assert "integrator_session_uptime_seconds" in content

    def test_flush_creates_parent_dir(self, tmp_path):
        """flush 自动创建父目录。"""
        nested = tmp_path / "nested" / "deep" / "metrics.prom"
        m = IntegratorMetrics(output_file=nested)
        m.record_task("t1", "ifind", "SUCCESS", 1.0, 10)
        ok = m.flush()
        assert ok is True
        assert nested.exists()

    def test_render_includes_all_metric_types(self, metrics):
        """render 输出包含所有 6 个指标类型。"""
        metrics.record_task("t1", "ifind", "SUCCESS", 1.0, 10)
        metrics.record_rate_limit("ifind")
        metrics.record_retry("t1", "ifind")
        metrics.set_uptime(60.0)
        rendered = metrics.render()
        assert "integrator_task_total" in rendered
        assert "integrator_task_duration_seconds" in rendered
        assert "integrator_rows_fetched_total" in rendered
        assert "integrator_rate_limit_hits_total" in rendered
        assert "integrator_retry_total" in rendered
        assert "integrator_session_uptime_seconds" in rendered

    def test_get_metrics_singleton(self):
        """get_metrics 返回单例。"""
        reset_metrics()
        m1 = get_metrics()
        m2 = get_metrics()
        assert m1 is m2
        reset_metrics()


class TestIntegratorMetricsThreadSafety:
    """线程安全测试。"""

    def test_concurrent_record_task(self, metrics):
        """多线程并发 record_task 不丢数据。"""
        import threading

        def worker():
            for i in range(100):
                metrics.record_task("t1", "ifind", "SUCCESS", 0.5, 10)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        rendered = metrics.render()
        # 10 线程 × 100 次 = 1000
        assert 'integrator_task_total{task_id="t1",source="ifind",status="SUCCESS"} 1000' in rendered
        # rows: 1000 × 10 = 10000
        assert 'integrator_rows_fetched_total{task_id="t1",source="ifind"} 10000' in rendered
