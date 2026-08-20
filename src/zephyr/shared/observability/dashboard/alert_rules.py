# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [A_module] module_id=MOD-INF-044 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""Grafana / Prometheus 告警规则定义。

告警规则与 P1-5 metrics 指标名对齐，覆盖：
- tick 丢弃速率高（队列满 / 背压）
- 队列水位高（即将 OOM）
- WAL 容量告警 / 危急（磁盘即将满）
- CH 写入失败（TCP+HTTP 均不可达）
- drain 持续失败（WAL 积压无法排空）

Usage::

    from zephyr.shared.observability.dashboard import generate_alert_rules_yaml
    yaml_text = generate_alert_rules_yaml()
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# 告警规则定义（name → Prometheus 表达式 + 级别 + 持续时间）
ALERT_RULES: list[dict[str, str]] = [
    {
        "name": "ZephyrTickDroppedHigh",
        "expr": "rate(zephyr_tick_dropped_total[5m]) > 10",
        "for": "2m",
        "severity": "warning",
        "summary": "tick 丢弃速率过高（>10/5m）",
        "description": "tick 队列满或背压导致数据丢弃，检查 WalWriter 容量",
    },
    {
        "name": "ZephyrQueueWatermarkHigh",
        "expr": "zephyr_tick_queue_size > 80000",
        "for": "1m",
        "severity": "warning",
        "summary": "tick 队列水位高（>80000/100000）",
        "description": "队列即将满，flush 线程可能跟不上，检查 CH 写入延迟",
    },
    {
        "name": "ZephyrWALCapacityWarning",
        "expr": "zephyr_wal_dir_bytes > 1503238553",
        "for": "30s",
        "severity": "warning",
        "summary": "WAL 容量告警（>1.4GB / 2GB 上限的 70%）",
        "description": "WAL 目录积压，CH 可能不可达或 drain 线程失败",
    },
    {
        "name": "ZephyrWALCapacityCritical",
        "expr": "zephyr_wal_dir_bytes > 1932735283",
        "for": "15s",
        "severity": "critical",
        "summary": "WAL 容量危急（>1.8GB / 2GB 上限的 90%）",
        "description": "WAL 即将满，背压已触发，tick 接收暂停，立即检查 CH 状态",
    },
    {
        "name": "ZephyrCHWriteFailure",
        "expr": 'rate(zephyr_ch_write_total{outcome!="committed"}[5m]) > 0',
        "for": "1m",
        "severity": "warning",
        "summary": "ClickHouse 写入失败（TCP+HTTP 均不可达）",
        "description": "CH 写入降级到本地落盘，数据保留待回灌但延迟增大",
    },
    {
        "name": "ZephyrDrainFailed",
        "expr": "rate(zephyr_drain_failed_total[5m]) > 0",
        "for": "5m",
        "severity": "warning",
        "summary": "WAL drain 持续失败（>5m）",
        "description": "WAL 回灌 CH 失败，积压持续增长，检查 CH 连接和表引擎",
    },
]


def generate_alert_rules_yaml() -> str:
    """生成 Prometheus 告警规则 YAML（用于 prometheus rules 文件）。

    Returns:
        Prometheus alerting rules YAML 文本
    """
    lines = [
        "# Prometheus Alerting Rules — 由 alert_rules.py 生成（MOD-INF-044）",
        "# P2-10 双数据源仪表盘告警规则",
        "",
        "groups:",
        "  - name: zephyr-data-layer",
        "    rules:",
    ]
    for rule in ALERT_RULES:
        lines.extend(
            [
                f"      - alert: {rule['name']}",
                f"        expr: {rule['expr']}",
                f"        for: {rule['for']}",
                "        labels:",
                f"          severity: {rule['severity']}",
                "        annotations:",
                f'          summary: "{rule["summary"]}"',
                f'          description: "{rule["description"]}"',
            ]
        )
    return "\n".join(lines) + "\n"
