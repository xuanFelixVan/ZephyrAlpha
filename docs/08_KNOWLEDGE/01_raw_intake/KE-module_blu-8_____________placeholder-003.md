---
module_id: KE-module_blu-8_____________placeholder-003
title: 8. 文件清单与落位（不留 placeholder）
category: module_blueprint
---

# 8. 文件清单与落位（不留 placeholder）

8. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── feedback_loop/                              # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_fle()
│   │   ├── protocol.py                             # FeedbackLoopProtocol
│   │   ├── action_protocols.py                     # §5.1 下游 Protocol 定义
│   │   ├── in_process.py                           # experimental 实现
│   │   ├── distributed.py                          # beta+ 占位
│   │   ├── schemas.py                              # Metric / Baseline / Anomaly / Action
│   │   ├── sink.py                                 # record_metric / record_batch
│   │   ├── analyzer/
│   │   │   ├── ema.py                              # EMA 实现
│   │   │   ├── trend.py                            # 滑窗斜率
│   │   │   └── flatline.py
│   │   ├── action_router.py                        # §3.2 ANOMALY_ACTION_ROUTING
│   │   ├── dispatcher.py                           # dispatch_action 逻辑
│   │   ├── adapters/
│   │   │   ├── context_engine.py                   # CEAdjustAdapter
│   │   │   ├── orchestrator.py                     # OrcControlAdapter
│   │   │   ├── vms.py                              # VMSControlAdapter
│   │   │   └── lsg.py                              # LSGControlAdapter
│   │   ├── db.py                                   # SQLite schema
│   │   └── config.py
│   └── config/
│       ├── feedback_loop.yaml
│       └── feedback_loop_rules.yaml                # 阈值外置
│
├── .runtime/
│   ├── feedback_loop/
│   │   ├── metrics.db                              # SQLite WAL
│   │   ├── pending_actions.ndjson                  # 下游未注入时的缓冲
│   │   └── baseline_cache.json
│   └── logs/
│       ├── fle_degrade.log
│       └── fle_action_audit.log                    # 所有 Action 审计
│
├── tests/unit/feedback_loop/
│   ├── test_sink.py
│   ├── test_ema.py
│   ├── test_trend_detection.py
│   ├── test_flatline.py
│   ├── test_action_routing.py
│   ├── test_dispatch_with_mock_protocol.py         # 关键：用 Mock 验证 Protocol 解耦
│   ├── test_action_outcome_rollback.py
│   ├── test_cold_start.py
│   └── test_degrade_paths.py
│
└── .gitignore                                      # 已追加 .runtime/
```

---
