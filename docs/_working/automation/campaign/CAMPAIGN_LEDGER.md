---
ttl: task_bound
completes_when: 全线施工完毕+循环检查连续两次 0 问题+红蓝通过+终局交付，或 Owner 叫停
---

# 夜班施工战役台账（st-autolnk-20260917，Owner 总令"全部施工"）

> 总令要点：线内先挖后干、线间并行流水；挖干判据=本台账六向台账+自审三态；循环检查至连续两次 0 问题；红蓝对抗；GitCommitGateway 全落地；临时文件清理；无遗留无待办（无法裁定→登记+跳过，堵死可停）。
> **持久规则：每完成一个有意义的步骤就更新本台账**（防上下文压缩失忆——压缩后从本文件恢复全部状态）。

## 0. 边界与分工（已定，不再议）

- 红线维持：禁写 docs/03_modules/**（新模块蓝图暂存 campaign/blueprints/，解冻后晋升=挂单 H-01）、pf_core/backtest、TDM、AGENTS.md。
- 排班分法（Owner 确认 AI 层转达案）：规则/schema=治理+Owner 钉死；**运营（值守/采样/建议器）=AI 层**；使用=各层自助走登记接口。业务层不自建排班逻辑，③的"自动排班"=写 schedule.yaml/tasks.yaml 正门登记。
- 挖干判据：每线六向台账（目标/证据/块/依赖/三态/下一步）填实且自审三态=挖干，才开工。

## 1. 关键情报摘要（两路侦察 03:40，防重挖）

### L2 输入件（转正建议书）
- **promotion_advisory.py 已存在**（MOD-BT-199，src/zephyr/strategy_pipeline/）：合并 SCR-SIMGOV 建议+SCR-DEV 偏离月史+fw-auto/latest.json+sim_memo 指针→`data/strategy_intake/promotion_advisories/<advisory_id>.json`；CLI=`python -m zephyr.strategy_pipeline.promotion_advisory [build|list|preauth <STR-ID>]`。**勿重建**。
- 平台四件落点：`c1_backtest.sim_trade_log`（事件流水）+`sim_pocket_daily`（钱包日账）+`sim_platform_journal`（日刊三检）+sim_deviation/sim_governance 跑档 `data/backtest_artifacts/runs/SCR-DEV-*/SCR-SIMGOV-*/04_wide/*.json`；E4 正考=`scripts/backtest/f06_e4_wfa_exam.py`→`data/backtest_artifacts/runs/E4-F06-*/{verdict.md,summary.json}`；成绩台账=`c1_backtest.strategy_screen`（is_sharpe/oos_sharpe/deflated_sharpe/num_trials/verdict）。
- **真缺口**=组合门打分器（OOS Sharpe≥1.5+回撤≤15%+容量证明+DSR>0）+一页式建议书 markdown。阈值来源：docs/_working/trading_vision/2026-09-16-owner-vision-system-mapping.md L57（草案在案，硬编码+引用出处）。
- 写作范本：scripts/backtest/sim_promotion_memo.py（只读生成/缺失降级不阻断/[CREATION-TOKEN] 头）；测试范本 tests/backtest/test_sim_promotion_memo.py。

### L1 输入件（上架流水线）
- DDL-as-Code：schemas/categories/market/<name>.py（XXX_DDL+TABLE_NAME+INSERT_COLUMNS）；DateTime64(3) 业务列 Asia/Shanghai、系统列 UTC；ReplacingMergeTree+PARTITION BY toYYYYMM(trade_date)+自然键 ORDER BY。
- 登记接口：schedule.yaml 槽位字段=cron/executor(default/heavy/realtime/intraday_minute/intraday_sector)/description/max_instances/type+seconds；**启动时加载不热载→新槽/新任务需调度器重启**；tasks.yaml 任务字段=task_id/table/source/schedule/incremental/capability/date_col/extra。
- 写入正道：`from zephyr.data.ch_writer import write_result, query`；FetchResult(table,columns,rows) never-raise；限频=SourcePolicy(config/policies.yaml)；robots 尊重有先例（rss_provider RobotFileParser）。
- 表名必须走 TableRegistry（docs/03_modules/business_data_categories.yaml）——**该文件在冻结区**→v0 变通：直连 ch_writer 写 c1_market 表+registry 注册列挂单（H-02），或验证 TableRegistry 是否硬拦。
- 调度器：python -m zephyr.data.scheduler，单例锁 tmp/scheduler_instance.lock，:9100 监控；安全重启窗=04:00-05:00（05:30 前无班次）。

### 战场态
- 03:39 时出仓波次（algo-flow P2-1 03:24）与排班 v2（st-govmap 03:34：api_server/ops_alert_feed/incubator/auto_runtime）在飞；st-qoder-t1a 持若干 test 文件 claim。我方新文件避开上述足迹。

## 2. 各线六向台账

### L2 转正建议书汇总器（P0）【三态：施工中】
- 目标：组合门打分器+一页建议书（消费 advisory JSON+strategy_screen+sim_pocket_daily）。
- 块：B1 打分纯函数+报告渲染（scripts/backtest/promotion_combo_gate.py）；B2 测试（tests/backtest/test_promotion_combo_gate.py）；B3 登记（token/translation/depgraph）+提交。
- 下一步：写 B1。裁定：promotion_advisory 不重建只消费；阈值硬编码+引用出处；CH 不可达→降级仅 advisory 证据（沿 sim_promotion_memo 不变量）。

### L1 数据源上架流水线（P0）【三态：挖干→施工中】
- 目标：`scripts/data/onboard_source.py`（源卡片驱动：probe 沙箱/apply 建表+登记/verify 计数核验）+首个真实免费源端到端上柜（选定：frankfurter.app ECB 汇率日频，免 key，表 c1_market.alt_fx_rate_ecb，自然键 trade_date+base+quote）。
- 块：B1 卡片 schema+probe；B2 DDL 渲染+建表（直连 ch_writer.query）；B3 采集任务（新 thin provider 或独立脚本走 write_result）；B4 schedule.yaml 槽位+tasks.yaml 任务登记；B5 调度器安全重启激活（04:00-05:00 窗）；B6 verify+台账。
- 依赖裁定：TableRegistry 在冻结区→表名直写+H-02 挂单；AkshareAltProvider 不动（1448 行他线资产）→新独立薄脚本。
- 下一步：B1-B3 先行。

### L3 搜索设备 v0（胃地基）【三态：挖干（轻）→待施工】
- 目标：`scripts/automation/intel_harvester.py`：arXiv API(q-fin)+RSSHub 现役源→关键词过滤→OllamaChat 摘要（LSG 内置）→inbox `docs/_working/automation/inbox/intel-<date>.md`+候选源卡片。
- 依赖：Ollama 在跑（9 模型）；RSSHub pm2 常驻。只搜不入册（红线）。

### L4 ⑨骨架体检月度任务【三态：待施工】
- 目标：`scripts/governance/generators/generate_skeleton_health.py` 只读盘点（注册表 72 实体+TDM 只读+采样 JSONL+覆盖审计产物 bb230c4f44）→月度建议书（血肉级/骨架级分节）。
- 注：TDM 只读不写（红线）。

### L5 标准库 v0【三态：待施工】
- 目标：`config/standards_registry.yaml`（standard_id/version/threshold/scope/status/why）+`scripts/governance/standards/standards_lib.py`（loader+freeze 核验+重考历史 diff 报告 v0）+种子数据（准入组合门四条为首批标准）。

### L6 实盘红线执行器 v0【三态：待施工】
- 目标：规则引擎（分级红线表 4h 熔断/日黄红线/周月红线/黑天鹅 48h 缓冲 regime 仲裁接口）纯函数+合成数据测试。落位 src/zephyr/ex_sor/risk_redline.py（域安静）。

### L7 A/B 联赛编排 + ④AI 判净站【三态：挂起待 L2/L1 落地后接】
- 理由：编排依赖 promotion 机制与模拟盘长周期数据（6 个月判定窗，今夜无数据可编）；判净站依赖 L1 表落位。挂起≠放弃，登记依赖图。

## 3. 挂单（解冻/ Owner 项，不阻塞）

- H-01 新模块蓝图晋升 docs/03_modules（冻结解除后）
- H-02 首个上架源表名进 business_data_categories.yaml+TableRegistry（冻结解除后）
- H-03 GPU-01/02 施工（scripts/backtest 红线区+预测表 DDL，等 pf_core 手术收针）
- H-04 GPU-04 RL trainer（B-007 Owner 门）
- H-05 CH-OptimizeMerge register ps1 化（改活任务，需值守窗执行，Owner 已批待安全窗）

## 4. 循环检查与红蓝

- 每线提交后自检：pytest 该线测试+--help 冒烟+产物目检。
- 全线完成后：整体循环检查×2（连续两次 0 问题）→红蓝对抗（子代理攻击：输入异常/空数据/CH 断连/路径越界/幂等重跑）→修复→终局端到端演示（源→表→任务登记→报告生成全链实录）。

## 5. 提交账本

- （逐笔追加）03:xx L2/L1/... hash 待填
