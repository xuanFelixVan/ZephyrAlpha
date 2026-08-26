---
ttl: task_bound
---

施工会话 AI-CAL-001。任务：W0 市场日历抽象（CAND-CRYPTO-001 晋升施工，数字货币战线第一地基，Owner 2026-08-26 拍板派单——94 号备忘 Q1-Q6 已拍板翻正 active v1.0.0）。

背景：
- 设计真源：[94_crypto_quant_expansion.md](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md) §4.1（市场日历抽象裁定）+ §5 候选 001 + §6 W0 波次
- 登记真源：candidate_module_registry.yaml CAND-CRYPTO-001 条目（含 upstream/downstream 与 q1 证据）
- 核心矛盾：现有 scheduler/K线聚合/回测时间轴/PIT asof 隐式假设 A股断点日历（交易日历+午休+隔夜+节假日），数字货币 7×24 连续，接入前必须抽象日历接口
- **硬门槛：A股现有逻辑零行为变化**（纯加接口层，回归测试全绿才算完）

范围（三步，顺序执行）：
1. **消费点盘点（先于一切改动）**：四类时间口径消费点全量清单——①scheduler（src/zephyr/data/scheduler.py）②K线聚合（120min 由 60min 两根聚合等，technical_indicator 体系 9 周期）③回测时间轴（src/zephyr/backtest/）④PIT asof（src/zephyr/data/pit_query.py）。产出=盘点报告 docs/_working/reports/2026-08-26-calendar-consumers-inventory.md（每消费点：文件/函数/日历假设形态/改造方式）
2. **market_calendar 接口+双实现**：抽象接口（Market Calendar，定义"什么时间有交易、K线如何切分"的策略对象）+ A股实现（现有交易日历逻辑收编，行为零变化）+ 7×24 连续日历实现（币版，顺带支持 4h 周期——现有 9 周期未含）。四类消费点改注入式，**禁止业务代码 if/else 判市场**
3. **CAND-CRYPTO-001 晋升**：apply_depgraph --add-design-node 登记设计态 + sync_panorama_module + align_panoramas 五图对齐；条目 status→promoted

避让（并发施工面，零触碰）：
- bj-daily：signal_ashare 全域（F16 资金卡接线等）
- ex_core/、risk/core/（其他战线施工面，W0 不涉及）
- candidate_module_registry.yaml 除 CAND-CRYPTO-001 行外区域（并发登记热区）

验收：①盘点报告落盘且四类全覆盖 ②A股实现收编后既有测试零回归（全量姿势：簇内串行 -n 0 × 簇间 3 路并发 + 假死簇逐文件 300s 墙钟强杀——AI-RESIDUAL-001 拓扑教训；串行禁 -p no:xdist）③7×24 日历+4h 周期单测覆盖 ④depgraph 晋升+五图对齐 PASS ⑤全走 GitCommitGateway（[GW:AI-CAL-001]）

完工反馈六要素：commit hash/盘点报告路径/测试轮次/改动清单/晋升证据/遗留项。
