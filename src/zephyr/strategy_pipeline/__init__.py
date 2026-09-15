# -*- coding: utf-8 -*-
"""strategy_pipeline — C6 全自动入库管线（A 方案：自动到 sim，production Owner 门）。

事件驱动五段：C4 落账事件 → C5 自动聚类 → C6 自动入库 → auto_mount 挂图 → sim 流转(FSM)。
方案真源：docs/_working/pipeline-research/2026-09-15-full-auto-pipeline-research.md §2-§3。
治理边界（Owner 2026-09-15 圈定 A）：sim 流转按预授权规则自动执行（本包 FSM+guard）；
sim→production 仍 Owner 门；KillSwitch/月度审计/告警全程保留。
"""

__all__: list[str] = ["bh_fdr", "intake", "lifecycle_fsm", "pipeline_events", "registry_writer", "screen_source"]
