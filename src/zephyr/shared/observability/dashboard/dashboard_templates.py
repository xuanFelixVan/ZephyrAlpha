# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [A_module] module_id=MOD-INF-044 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""
Grafana Dashboard JSON 模板生成器。

生成 Grafana 11 provisioning 兼容的 Dashboard JSON，覆盖：
- 数据采集健康（tick 接收/写入/丢弃速率 + 队列水位 + WAL 段文件数）
- ClickHouse 写入健康（写入成功率 + 延迟 p50/p99 + 冷却状态）
- Drain 健康（drain 成功/失败速率 + 积压文件数 + WAL 容量水位）

每个 Dashboard 使用 Prometheus 数据源（uid=prometheus）。

Usage::

    from zephyr.shared.observability.dashboard import generate_data_collection_dashboard
    json_obj = generate_data_collection_dashboard()

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: dashboard 参数
#   fields: 参数 dashboard，类型注解 dict[str, Any]
#   code: dashboard_templates.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① generate_data_collection_dashboard
#   name_en: generate_data_collection_dashboard
#   intro: 生成「数据采集健康」Dashboard JSON。
#   desc: 生成「数据采集健康」Dashboard JSON。 面板： 1. tick 接收速率（rate zephyr_tick_received_total） 2. tick 写入速率（…；源码 L139-L163
#   inputs: 无参数
#   outputs: dict[str, Any]
# - id: A2
#   name_zh: ② generate_ch_write_dashboard
#   name_en: generate_ch_write_dashboard
#   intro: 生成「ClickHouse 写入健康」Dashboard JSON。
#   desc: 生成「ClickHouse 写入健康」Dashboard JSON。 面板： 1. 写入成功率（committed / total） 2. 写入失败率（non-committed…；源码 L166-L212
#   inputs: 无参数
#   outputs: dict[str, Any]
# - id: A3
#   name_zh: ③ generate_drain_health_dashboard
#   name_en: generate_drain_health_dashboard
#   intro: 生成「Drain 健康」Dashboard JSON。
#   desc: 生成「Drain 健康」Dashboard JSON。 面板： 1. drain 成功速率 2. drain 失败速率 3. 积压文件数 4. WAL 容量水位（含 70%/90…；源码 L215-L235
#   inputs: 无参数
#   outputs: dict[str, Any]
# - id: A4
#   name_zh: ④ export_dashboard_json
#   name_en: export_dashboard_json
#   intro: 将 Dashboard dict 序列化为 Grafana provisioning JSON 字符串。
#   desc: 将 Dashboard dict 序列化为 Grafana provisioning JSON 字符串。；源码 L238-L240
#   inputs: dashboard
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import json
import logging
from typing import Any

log = logging.getLogger(__name__)

_PROM_DS = {"uid": "prometheus", "type": "prometheus"}

_GRID_POS_FULL = {"x": 0, "y": 0, "w": 24, "h": 8}
_GRID_POS_HALF = {"x": 0, "y": 0, "w": 12, "h": 8}
_GRID_POS_HALF_R = {"x": 12, "y": 0, "w": 12, "h": 8}


def _make_panel(
    panel_id: int,
    title: str,
    expr: str,
    y_pos: int,
    x_pos: int = 0,
    width: int = 12,
    height: int = 8,
    panel_type: str = "timeseries",
    unit: str = "short",
) -> dict[str, Any]:
    """构造单个 Grafana 面板。"""
    return {
        "id": panel_id,
        "title": title,
        "type": panel_type,
        "datasource": _PROM_DS,
        "gridPos": {"x": x_pos, "y": y_pos, "w": width, "h": height},
        "targets": [{"expr": expr, "legendFormat": "{{instance}}", "refId": "A"}],
        "fieldConfig": {
            "defaults": {"unit": unit},
            "overrides": [],
        },
        "options": {"legend": {"displayMode": "table", "placement": "bottom"}},
    }


def _make_dashboard(
    uid: str,
    title: str,
    tags: list[str],
    panels: list[dict[str, Any]],
) -> dict[str, Any]:
    """构造 Dashboard JSON 顶层结构。"""
    return {
        "uid": uid,
        "title": title,
        "tags": tags,
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "10s",
        "time": {"from": "now-1h", "to": "now"},
        "panels": panels,
        "templating": {"list": []},
        "annotations": {"list": []},
    }


def generate_data_collection_dashboard() -> dict[str, Any]:
    """生成「数据采集健康」Dashboard JSON。

    面板：
    1. tick 接收速率（rate zephyr_tick_received_total）
    2. tick 写入速率（rate zephyr_tick_written_total）
    3. tick 丢弃速率（rate zephyr_tick_dropped_total）
    4. 队列水位（zephyr_tick_queue_size）
    5. WAL 段文件数（zephyr_wal_segments_total）
    6. WAL 目录大小（zephyr_wal_dir_bytes）
    """
    panels = [
        _make_panel(1, "Tick 接收速率", "rate(zephyr_tick_received_total[1m])", 0, 0, 12, 8, unit="ops"),
        _make_panel(2, "Tick 写入速率", "rate(zephyr_tick_written_total[1m])", 0, 12, 12, 8, unit="ops"),
        _make_panel(3, "Tick 丢弃速率", "rate(zephyr_tick_dropped_total[1m])", 8, 0, 12, 8, unit="ops"),
        _make_panel(4, "队列水位", "zephyr_tick_queue_size", 8, 12, 12, 8, unit="short"),
        _make_panel(5, "WAL 段文件总数", "zephyr_wal_segments_total", 16, 0, 12, 8, unit="short"),
        _make_panel(6, "WAL 目录大小 (Bytes)", "zephyr_wal_dir_bytes", 16, 12, 12, 8, unit="bytes"),
    ]
    return _make_dashboard(
        uid="zephyr-data-collection",
        title="ZephyrAlpha — 数据采集健康",
        tags=["zephyr", "data-layer", "p2-10"],
        panels=panels,
    )


def generate_ch_write_dashboard() -> dict[str, Any]:
    """生成「ClickHouse 写入健康」Dashboard JSON。

    面板：
    1. 写入成功率（committed / total）
    2. 写入失败率（non-committed）
    3. 写入延迟 p50
    4. 写入延迟 p99
    5. TCP 冷却状态
    6. HTTP 冷却状态
    """
    panels = [
        _make_panel(
            1, "CH 写入成功率", 'rate(zephyr_ch_write_total{outcome="committed"}[1m])', 0, 0, 12, 8, unit="ops"
        ),
        _make_panel(
            2, "CH 写入失败率", 'rate(zephyr_ch_write_total{outcome!="committed"}[1m])', 0, 12, 12, 8, unit="ops"
        ),
        _make_panel(
            3,
            "写入延迟 p50",
            "histogram_quantile(0.5, rate(zephyr_ch_write_latency_seconds_bucket[5m]))",
            8,
            0,
            12,
            8,
            unit="s",
        ),
        _make_panel(
            4,
            "写入延迟 p99",
            "histogram_quantile(0.99, rate(zephyr_ch_write_latency_seconds_bucket[5m]))",
            8,
            12,
            12,
            8,
            unit="s",
        ),
        _make_panel(5, "TCP 冷却状态", 'zephyr_ch_cooldown_active{channel="tcp"}', 16, 0, 12, 8, unit="short"),
        _make_panel(6, "HTTP 冷却状态", 'zephyr_ch_cooldown_active{channel="http"}', 16, 12, 12, 8, unit="short"),
    ]
    return _make_dashboard(
        uid="zephyr-ch-write",
        title="ZephyrAlpha — ClickHouse 写入健康",
        tags=["zephyr", "data-layer", "p2-10"],
        panels=panels,
    )


def generate_drain_health_dashboard() -> dict[str, Any]:
    """生成「Drain 健康」Dashboard JSON。

    面板：
    1. drain 成功速率
    2. drain 失败速率
    3. 积压文件数
    4. WAL 容量水位（含 70%/90% 告警线）
    """
    panels = [
        _make_panel(1, "Drain 成功速率", "rate(zephyr_drain_replayed_total[1m])", 0, 0, 12, 8, unit="ops"),
        _make_panel(2, "Drain 失败速率", "rate(zephyr_drain_failed_total[1m])", 0, 12, 12, 8, unit="ops"),
        _make_panel(3, "积压文件数", "zephyr_wal_backlog_files", 8, 0, 12, 8, unit="short"),
        _make_panel(4, "WAL 容量水位 (Bytes)", "zephyr_wal_dir_bytes", 8, 12, 12, 8, unit="bytes"),
    ]
    return _make_dashboard(
        uid="zephyr-drain-health",
        title="ZephyrAlpha — Drain 健康",
        tags=["zephyr", "data-layer", "p2-10"],
        panels=panels,
    )


def export_dashboard_json(dashboard: dict[str, Any]) -> str:
    """将 Dashboard dict 序列化为 Grafana provisioning JSON 字符串。"""
    return json.dumps(dashboard, ensure_ascii=False, indent=2)
