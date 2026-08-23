---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=construction_ledger · owner=ZephyrAlpha-Owner · status=active · version=1.0.0 · date=2026-08-23 · topic=construction_order_master（长城任务） · scope=全项目。
>
> **定位**：四份待施工账单的**合并排序总账**——任务一第 1 步产物。施工会话领任务看本表 + 点进引用账单。

# 施工顺序总清单（长城任务 2026-08-23）

## 0. 合并口径与裁定记录

**来源四账**：
| 账 | 文件 | 内容 |
|---|---|---|
| 测试账 | [.runtime/construction_backlog.md](file:///d:/ZephyrAlpha/.runtime/construction_backlog.md) | 全量 sweep 实测：真红 4 + flaky 3 + 假死豁免 1 |
| 回测账 | [construction_backlog.md](file:///d:/ZephyrAlpha/docs/_working/construction_backlog.md) | 回测启动 A/B/C 三阶段 |
| 设计态账 | [design_state_backlog.md](file:///d:/ZephyrAlpha/docs/_working/design_state_backlog.md) | 76 未施工 + 2 修门禁 + 4 半建成 |
| 后端总单 | [2026-08-22-backend-construction-master-list.md](file:///d:/ZephyrAlpha/docs/_working/2026-08-22-backend-construction-master-list.md) | 44 GAP-F + 5 类 BFE 通道 |

**排序裁定**（第一性原理：信任底座 → 核查定界 → 风险优先 → 便宜先行 → 依赖拓扑 → 远期殿后）：
1. **测试网修复排最前**——回归网不可信则后续所有施工的"验证"无意义（风险优先原则的元层）。
2. **D 类核查第二**——只读半小时出报告，决定 GAP-F-08/17/21/23 派单范围（master-list 既定原则）。
3. **Regime/风控插队在作战室之前**——宪章 §3 约束三命门 + §6 风险优先，高于页面功能。
4. **C 类接线紧随 P0 核心链**——最便宜但依赖 GAP-F-12，故排板块链后。
5. **🔒 外部依赖项不施工、登记挂起**——无真实环境/数据验证的 speculative 代码是债不是资产（量化社区惯例：unvalidatable code = negative EV）。

**挂起登记（本任务不施工，原因锁定）**：
| 项 | 挂起原因 |
|---|---|
| EX-007/008/012/021/029/030/031/032/033/042、BT-025、RPT-015 | 🔒 等实盘环境/Broker 回调/执行数据≥30 天/EX-SOR（外部依赖，不可自主解除） |
| EX-059 execution_mcp_server | 生态未成熟，账单已定"无限期搁置" |
| EX-060 rl_optimal_executor | 需 90 天执行数据 |
| GAP-F-27 绩效归因 | CTR-P1-007 阻塞 + CAND-GOVAUDIT-003 待 Owner 裁定 |
| BT-B1/B2/B5（QMT 登录/DDL/cron） | Owner 窗口人工项，AI 无权执行；B3/B6 连带挂起 |
| C2 残余（FLE gates #61/trend_analyzer/Dashboard 死数据） | 另案执行中，不重复派单 |

**半建成 4 项裁定**：INF-035 缩减为轻量三层骨架补齐；INF-050 不另立 sentinel 版，intelligence/ 下建薄封装复用 orchestrator/hallucination_detector；CONTEXT_ENGINE 按蓝图补齐核心方法；INF-033 转候选库 CAND（行为审计专职引擎边际价值低，code_dedup 已部分承载）。

**已发现的结构修复（本任务顺手治本）**：#ARCH-171 capability 注册表 creation_tokens 段错位（131 条被吞入 di_seam_exemptions）——已修复并提交 29b62908。

---

## 1. 施工顺序总表

### 阶段 0：测试信任底座（测试账）
| 序 | 内容 | 证据 |
|---|---|---|
| 0.1 | 命名门禁拦截 commit_queue_landing.py（改名或白名单，裁定：门禁白名单登记——该脚本是 landing 核心件，改名全链路引用排查成本高于白名单登记，且 validate_/detect_ 前缀语义不符其"落地执行"职能） | tests/governance/security/test_security_scripts.py |
| 0.2 | Ollama 探活测试 ×2 环境解耦（mock 探活请求） | tests/model/test_local_model.py |
| 0.3 | path_tree 设计保护测试播种 D-TEST 域 | tests/path/test_path_tree_generator_design_protection.py |
| 0.4 | flaky×3 固化：commit_gates 共享状态排查 ×2 + token bucket 注入时钟 | tests/governance/commit_gates/, tests/trading/test_admission_controller.py |
| 0.5 | commit_queue_integration 假死治本尝试（worktree 无管道/Popen 墙钟）；败则保持豁免并登记 | tests/governance/test_commit_queue_integration.py |

### 阶段 1：核查类 D（后端总单波次 0，只读）
| 序 | 缺口 | 内容 |
|---|---|---|
| 1.1 | GAP-F-D1 | analyst_forecast/research_report ClickHouse 覆盖核查 |
| 1.2 | GAP-F-D2 | auction_snapshot/auction_book 9:15-9:25 覆盖核查 |
| 1.3 | GAP-F-D3 | us_index/kline_us_daily 标的清单核查 |

### 阶段 2：Regime 生死线（设计态账波次 0，宪章 §3 命门）
MOD-SIG-036 market_state_sensor → SIG-039 regime_change_detector → SIG-037 next_day_8state_forecast → SIG-038 cross_market_conduction_sensor → SIG-040 adjustment_cycle_tracker → SIG-041 market_lifecycle_phase（均落 signal_ashare/）

### 阶段 3：风控/合规（设计态账波次 1，宪章 §6 P0）
| 序 | 模块 | 备注 |
|---|---|---|
| 3.1 | MOD-RK-25 risk/core/risk_data_pipeline.py | 风控数据底座，先行 |
| 3.2 | MOD-RK-22 risk/core/agent_risk_monitor.py | |
| 3.3 | MOD-RK-24 risk/core/risk_veto_engine.py | |
| 3.4 | MOD-EX-024 ex_core/pre_execution_checker.py | |
| 3.5 | MOD-L10-001 compliance/async_intercept_queue.py | |
| 3.6 | MOD-CMP-003 compliance/compliance_tech_enabler.py | |
| 3.7 | MOD-CMP-004 compliance/compliance_continuous_ops.py | |
| 3.8 | MOD-L08-001 default_approval_gateway.py + default_notification_manager.py | 前端域审批/通知载体 |

### 阶段 4：作战室 P0 核心链（后端总单波次 2）
4.1 GAP-F-07 预案三维归因+Brier 校准 → 4.2 GAP-F-09 结构化今日交易计划 → 4.3 GAP-F-02 候选股边界批量计算 → 4.4 GAP-F-01 情景概率分布（**前置：GAP-F-07 落库数据 + GAP-F-34 密度头**，排阶段 8 后）

### 阶段 5：板块链 P0 + B 类字段（后端总单波次 3）
5.1 GAP-F-12 主线概率综合评分（先静态权重 MVP）→ 5.2 GAP-F-13 梯队个股明细字段扩充（limit_up_pool 明细表+采集器）

### 阶段 6：便宜 C 类接线（后端总单波次 1 + §4）
6.1 GAP-F-04 相关性净额查询接口 → 6.2 GAP-F-30 持仓×板块语境（前置 5.1）→ 6.3 GAP-F-32 渲染器全量接入（持续） → 6.4 BFE-01 T分析页接 MOD-SIG-024 → 6.5 BFE-28/32/25/26/27/30/31 查询接口群

### 阶段 7：信号/因子（设计态账波次 3，14 个）
SIG-042~049 八件（causal_inference_engine 有测试桩待激活）、SIG-054、SIG-009/010（signal_fundamental）、L02-026、L00-005/006（data/connectors+normalizers 目录）

### 阶段 8：仓位/卖出（设计态账波次 4，15 个）
POS-005/011/012/013/018/015/019 + SELL-002/010/011/012/013/014/017/018

### 阶段 9：执行链路未阻塞（设计态账波次 2 + 修门禁 2 项）
先修门禁描述（EX-035 删 OKX、EX-014 降级 TWAP/VWAP），再施工：EX-058 miniqmt_channel_manager → EX-014 order_splitter → EX-035 live_simulation_switcher → EX-062 execution_strategy_selector → L06-001 live_portfolio

### 阶段 10：GAP P1 补全（后端总单波次 4）
GAP-F-03 多空辩论 → GAP-F-06 作战池（前置12）→ GAP-F-05 禁做清单（前置06）→ GAP-F-08 竞价命中持久化（前置 D2）→ GAP-F-11 筛选漏斗 → GAP-F-14 涨停归因 → GAP-F-15 分时贡献度 → GAP-F-21 新闻双标签（前置 D1）→ GAP-F-23 外盘补齐（前置 D3）→ GAP-F-25 做T点位 → GAP-F-28 告警聚合器 → GAP-F-31 指数共振评分

### 阶段 11：ML 域（后端总单波次 5 + 设计态账波次 5 ML 六件）
GAP-F-34 密度预测 MVP（LightGBM 分位数头）→ GAP-F-35 三候选 → ML-001 training_pipeline → ML-002 ai_operator → ML-003 training_dataset_manager → ML-004 gray_release_shadow_deployer → ML-007 meta_learning_evolution → ML-009 learning_effect_feedback →（回头解锁 4.4 GAP-F-01）

### 阶段 12：GAP 波次 6 截图反推族（先补 CAND 登记）
GAP-F-42 证据链结构 → GAP-F-36 蒙特卡洛 → GAP-F-39 信号强度合成 → GAP-F-37 缠论 → GAP-F-38 因子聚类（前置 32）→ GAP-F-40 AI 复盘结语 → GAP-F-41 跨资产比价 → GAP-F-43 LLM 因子挖掘（前置 34）→ GAP-F-44 多 Analyst（前置 03）

### 阶段 13：GAP 波次 7 P2 长尾
GAP-F-18 板块属性标注（半天活先做）→ GAP-F-19 昨涨停今表现 → GAP-F-20 量能异动 → GAP-F-10 四指数分市场 → GAP-F-16 逆势榜（前置15）→ GAP-F-17 板块详情（前置 D1）→ GAP-F-22 新闻影响分级 → GAP-F-24 对A股影响判定（前置23）→ GAP-F-26 执行偏差归因（前置09）→ GAP-F-29 实盘净值曲线 → GAP-F-33 趋势线后端化（先核查）

### 阶段 14：AI 自治残余 + 远期未阻塞
INF-049 venra_double_lock_anchor → INF-050 薄封装 → CONTEXT_ENGINE 补齐 → INF-033 转 CAND → INF-035 缩减补齐 → DS 波次6：EX-036 轻量实现 → SIG-050~053/055 → ML-005/006/008 → INF-048

### 阶段 15：回测启动 BT-A（回测账，数据依赖，尽力而为）
A4 首批策略激活（可并行先做）→ A1 行情追平（网络依赖）→ A2 北交所补缺 → A3 指数成分回填 → A5 首份回测报告。A 外 Owner 项挂起登记。

---

## 2. 并发分片表（子代理目录互斥所有权）

| 批次 | Agent | 领地（互斥） | 任务 |
|---|---|---|---|
| B1 | T0FIX | tests/ 指定 5 处 + scripts/governance 白名单 | 阶段 0 全部 |
| B1 | REGIME | src/zephyr/signal_ashare/（6 新件）+ tests/signal_ashare/ | 阶段 2 |
| B1 | RISK | src/zephyr/risk/core/ + src/zephyr/compliance/ + ex_core/pre_execution_checker.py + 前端 L08 两件 | 阶段 3 |
| B1 | WARROOM | src/zephyr/plan_engine/ + 归因/Brier 新件 | 阶段 4 的 4.1-4.3 |
| B2 | SECTOR | signal/sector 相关 + limit_up_pool | 阶段 5 + 6.2 后端接口 |
| B2 | SIGNAL | DS 波次 3 各件 + tests | 阶段 7 |
| B2 | POSSELL | position/ + sell/ + tests | 阶段 8 |
| B2 | CWIRE | 前端 mockup + 后端查询接口 | 阶段 6（6.2 除外） |
| B3 | EXEC | ex_core/（EX-058/014/035/062 + L06-001）+ 门禁描述修正 | 阶段 9 |
| B3 | GAPP1A | GAP-F-03/05/06/08/11 | 阶段 10 前半 |
| B3 | GAPP1B | GAP-F-14/15/21/23/25/28/31 | 阶段 10 后半 |
| B3 | ML | ml_train/ + GAP-F-34/35 | 阶段 11 |
| B4 | GAP6 | 波次 6 九件 | 阶段 12 |
| B4 | GAP7 | 波次 7 十一件 | 阶段 13 |
| B4 | INFRA | INF-049/050、CONTEXT_ENGINE、INF-035、DS 波次6 | 阶段 14 |
| B4 | DVERIFY | 只读核查 ×3 + A4 策略激活 | 阶段 1 + 15-A4 |
| B5 | BTDATA | 数据采集/回测 | 阶段 15 A1-A3/A5 + 解锁项收尾 |

## 3. 施工纪律（子代理契约，违反=返工）

1. **禁碰共享注册表**——creation_token/CAND/翻译/ARCH 条目一律写片段文件 `.runtime/construction_20260823/fragments/<agent>_registry.yaml`（格式照 capability 注册表 creation_tokens 条目），主代理串行合并提交。
2. **禁 git commit**——所有提交由主代理经 GitCommitGateway 串行执行。
3. **新 .py 先 depgraph 登记**：`python scripts/governance/apply_depgraph.py --add-design-node <path> <blueprint_id> <domain_id> planned --granularity file`（domain_id 抄同目录既有节点），并发冲突则重试一次，再败记入报告交主代理。施工+测试完成后 `--transition-build-status <node_id> generated`→`testing`。
4. **测试先行**：先落单测桩再写主码；自测 `python -m pytest <own test files> -n 0`（**禁 `-p no:xdist`**）。
5. **字段头部**：trae_047 规范 14 字段（__init__.py 最低 3 字段）。
6. **既有门禁教训**：模块级可变容器（含 __all__）必须 Final 标注；新模块须被 import 可见（ORPHAN-MODULE，lazy 映射包用 TYPE_CHECKING）；>7 参数收 dataclass；错误消息禁含 session_id；永久脚本禁 while True 无界循环。
7. **宪章红线**：回测成本完整（佣金+印花税+滑点+冲击+做T成本）；策略三维解耦；禁过拟合参数生效实盘。
8. **完成后写报告** `.runtime/construction_20260823/reports/<agent>_report.md`：建成清单/测试结果/depgraph node_id 列表/遗留问题。

## 4. 验收标准

1. 每批次：子代理自报测试全绿 + 片段文件齐全 → 主代理合并注册表 → 网关分域提交。
2. 全批次后：全量 sweep（簇内串行 `-n 0` × 簇间 3 路并发 + 假死簇 300s 强杀，剔除已知豁免文件）连跑两轮，**连续两轮问题=0** 方算通过；否则修复子代理循环。
3. 临时文件清理：`.runtime/construction_20260823/` 片段与报告核对完毕后清理（.runtime 本不入 git）。

## 5. 修订记录

| 日期 | 版本 | 内容 |
|---|---|---|
| 2026-08-23 | 1.0.0 | 首版：四账合并排序 16 阶段 + 挂起裁定 + 5 批并发分片 + 纪律契约（长城任务一-1 产物） |
