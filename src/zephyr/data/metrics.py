# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.metrics
# [DOMAIN] D_DATA
# [DEPENDENCIES]
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Prometheus 文本格式指标采集；不依赖 prometheus_client 库；输出 data/metrics.prom；线程安全
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有方法不抛异常（写文件失败→log warning）
# [TESTS] tests/zephyr/data/test_metrics.py
# [A_module] module_id=MOD-L00-004-metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""可观测性指标采集（MOD-L00-004 §11）。

不依赖 prometheus_client 库，直接按 Prometheus 文本格式写入 data/metrics.prom。
被 Prometheus Node Exporter 的 textfile collector 采集，或被 Grafana 读取。

6 个核心指标（蓝图 §11.1）：
- task_total：任务执行总次数（counter, labels: task_id/source/status）
- task_duration_seconds：任务耗时分布（histogram, labels: task_id/source）
- rows_fetched_total：拉取行数总计（counter, labels: task_id/source）
- rate_limit_hits_total：限流命中次数（counter, labels: source）
- retry_total：重试次数总计（counter, labels: task_id/source）
- session_uptime_seconds：会话运行时长（gauge）

用法：
    from zephyr.data.metrics import get_metrics
    m = get_metrics()
    m.record_task("kline_daily_incremental", "ifind", "SUCCESS", 12.5, 5500)
    m.record_rate_limit("ifind")
    m.record_retry("kline_daily_incremental", "ifind")
    m.set_uptime(3600.0)
    m.flush()  # 写入 data/metrics.prom
"""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Optional

from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

_DEFAULT_METRICS_FILE = REPO_ROOT / "data" / "metrics.prom"

# task_duration_seconds 直方图桶（蓝图 §11.1）
_DURATION_BUCKETS = [0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 900.0, 1800.0, 3600.0]


class IntegratorMetrics:
    """数据源集成器可观测性指标采集器。

    线程安全（用 Lock 保护计数器写入）。
    """

    def __init__(self, output_file: str | Path | None = None):
        """初始化指标采集器。

        Args:
            output_file: 输出 .prom 文件路径，默认 data/metrics.prom
        """
        self._output_file = Path(output_file) if output_file else _DEFAULT_METRICS_FILE
        self._lock = threading.Lock()
        # 计数器 / 直方图 内部存储
        self._task_total: dict[tuple[str, str, str], int] = {}
        self._task_duration_count: dict[tuple[str, str], int] = {}
        self._task_duration_sum: dict[tuple[str, str], float] = {}
        self._task_duration_buckets: dict[tuple[str, str], list[int]] = {}
        self._rows_fetched: dict[tuple[str, str], int] = {}
        self._rate_limit_hits: dict[str, int] = {}
        self._retry_total: dict[tuple[str, str], int] = {}
        self._uptime: float = 0.0
        self._start_ts: float = time.time()
        # 自动设置 uptime（初始化时为 0）
        self._uptime = time.time() - self._start_ts

    # ============== 记录接口 ==============

    def record_task(
        self,
        task_id: str,
        source: str,
        status: str,
        duration_sec: float,
        rows: int = 0,
    ) -> None:
        """记录一次任务执行。

        Args:
            task_id: 任务 ID
            source: 数据源
            status: 状态（SUCCESS/FAILED/BLOCKED）
            duration_sec: 耗时秒
            rows: 拉取行数
        """
        with self._lock:
            # task_total
            key = (task_id, source, status)
            self._task_total[key] = self._task_total.get(key, 0) + 1
            # task_duration_seconds
            dkey = (task_id, source)
            self._task_duration_count[dkey] = self._task_duration_count.get(dkey, 0) + 1
            self._task_duration_sum[dkey] = self._task_duration_sum.get(dkey, 0.0) + duration_sec
            # 直方图桶（Prometheus 累积桶：每个 le 桶包含所有 <= le 的样本）
            buckets = self._task_duration_buckets.setdefault(
                dkey, [0] * (len(_DURATION_BUCKETS) + 1)
            )
            # 该样本进入所有 le >= duration 的桶（含 +Inf）
            for i, bound in enumerate(_DURATION_BUCKETS):
                if duration_sec <= bound:
                    buckets[i] += 1
            buckets[-1] += 1  # +Inf 桶总是 +1
            # rows_fetched_total
            if rows > 0:
                rkey = (task_id, source)
                self._rows_fetched[rkey] = self._rows_fetched.get(rkey, 0) + rows

    def record_rate_limit(self, source: str) -> None:
        """记录一次限流命中。"""
        with self._lock:
            self._rate_limit_hits[source] = self._rate_limit_hits.get(source, 0) + 1

    def record_retry(self, task_id: str, source: str) -> None:
        """记录一次重试。"""
        with self._lock:
            key = (task_id, source)
            self._retry_total[key] = self._retry_total.get(key, 0) + 1

    def set_uptime(self, uptime_sec: float) -> None:
        """设置会话运行时长（gauge）。"""
        with self._lock:
            self._uptime = uptime_sec

    def update_uptime(self) -> None:
        """根据 start_ts 自动更新 uptime。"""
        with self._lock:
            self._uptime = time.time() - self._start_ts

    # ============== 输出 ==============

    def render(self) -> str:
        """渲染为 Prometheus 文本格式字符串。"""
        with self._lock:
            lines: list[str] = []

            # task_total
            lines.append("# HELP integrator_task_total 任务执行总次数")
            lines.append("# TYPE integrator_task_total counter")
            for (task_id, source, status), val in sorted(self._task_total.items()):
                lines.append(
                    f'integrator_task_total{{task_id="{task_id}",source="{source}",status="{status}"}} {val}'
                )

            # task_duration_seconds
            lines.append("# HELP integrator_task_duration_seconds 任务耗时分布")
            lines.append("# TYPE integrator_task_duration_seconds histogram")
            for (task_id, source), buckets in sorted(self._task_duration_buckets.items()):
                labels = f'task_id="{task_id}",source="{source}"'
                for i, bound in enumerate(_DURATION_BUCKETS):
                    lines.append(
                        f'integrator_task_duration_seconds_bucket{{le="{bound}",{labels}}} {buckets[i]}'
                    )
                lines.append(
                    f'integrator_task_duration_seconds_bucket{{le="+Inf",{labels}}} {buckets[-1]}'
                )
                lines.append(
                    f'integrator_task_duration_seconds_count{{{labels}}} {self._task_duration_count[(task_id, source)]}'
                )
                lines.append(
                    f'integrator_task_duration_seconds_sum{{{labels}}} {self._task_duration_sum[(task_id, source)]:.4f}'
                )

            # rows_fetched_total
            lines.append("# HELP integrator_rows_fetched_total 拉取行数总计")
            lines.append("# TYPE integrator_rows_fetched_total counter")
            for (task_id, source), val in sorted(self._rows_fetched.items()):
                lines.append(
                    f'integrator_rows_fetched_total{{task_id="{task_id}",source="{source}"}} {val}'
                )

            # rate_limit_hits_total
            lines.append("# HELP integrator_rate_limit_hits_total 限流命中次数")
            lines.append("# TYPE integrator_rate_limit_hits_total counter")
            for source, val in sorted(self._rate_limit_hits.items()):
                lines.append(
                    f'integrator_rate_limit_hits_total{{source="{source}"}} {val}'
                )

            # retry_total
            lines.append("# HELP integrator_retry_total 重试次数总计")
            lines.append("# TYPE integrator_retry_total counter")
            for (task_id, source), val in sorted(self._retry_total.items()):
                lines.append(
                    f'integrator_retry_total{{task_id="{task_id}",source="{source}"}} {val}'
                )

            # session_uptime_seconds
            lines.append("# HELP integrator_session_uptime_seconds 会话运行时长")
            lines.append("# TYPE integrator_session_uptime_seconds gauge")
            lines.append(f"integrator_session_uptime_seconds {self._uptime:.2f}")

            return "\n".join(lines) + "\n"

    def flush(self) -> bool:
        """写入 .prom 文件。失败时 log warning 不抛出。

        Returns:
            是否写入成功。
        """
        try:
            self._output_file.parent.mkdir(parents=True, exist_ok=True)
            content = self.render()
            tmp = self._output_file.with_suffix(".prom.tmp")
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(self._output_file)
            return True
        except Exception as e:
            log.warning(f"metrics.flush 失败: {e}")
            return False


# ============== 模块级单例 ==============

_metrics: Optional[IntegratorMetrics] = None
_metrics_lock = threading.Lock()


def get_metrics(output_file: str | Path | None = None) -> IntegratorMetrics:
    """获取全局 IntegratorMetrics 单例。"""
    global _metrics
    if _metrics is None:
        with _metrics_lock:
            if _metrics is None:
                _metrics = IntegratorMetrics(output_file)
    return _metrics


def reset_metrics() -> None:
    """重置全局单例（测试用）。"""
    global _metrics
    with _metrics_lock:
        _metrics = None
