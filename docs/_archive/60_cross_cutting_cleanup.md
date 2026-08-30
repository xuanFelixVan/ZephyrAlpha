---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=冲突矩阵清理与事件总线 · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.1.0 · date=2026-08-15 · topic=cross_cutting_cleanup · scope=07_trading_decision_architecture · depends_on=- 30_multi_strategy_concurrency · related_modules=- src/zephyr/shared/event_bus.py - src/zephyr/shared/contracts/contract_bus.py - src/zephyr/position/core/firm_risk_aggregator.py

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-15 第 4 批（会话 AI-XCUT-001，提交 3d68da3ed3 合并回 dev）——三处残留漂移收敛 + 作战地图 §16 真源收敛（31 条跨策略冲突仲裁→3 条公司层硬上限）+ CAND-PFALLOC-002 标 rejected。施工前提"骨架需重建"经实证推翻：v1.0.2 内容完整，无需重建。
>
> **最终成果**：85 项两轮全绿；§16 重生成闭合实证；本档 v1.1.0 定稿。
>
> **未做事项及原因**：无本科目未做项。

# 冲突矩阵清理与事件总线

> 本备忘裁定两项跨切治理议题：①battle_map_12 §16 的 31 条跨策略冲突仲裁在 Model A 下的清理；②事件总线/信号路由在本项目（单机 PC + miniQMT）的形态与边界。
> 性质：永久态讨论记录，可随项目演进而修订。管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G27。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G27 冲突矩阵清理与事件总线 |
| 所属 | 作战地图 12 |
| 依赖 | G04-G13（架构定型后才能清理冲突）——已满足（20/30 号已定型） |
| 对标 | 机构事件驱动架构（EDA）——经审查，单机进程内队列即行业标准，非微服务信号路由（§3.2/§4.1） |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3（架构定型后） |
| 状态 | **已定型（v1.0.0）**——核心裁定均已在 [30_multi_strategy_concurrency §7.3](30_multi_strategy_concurrency.md) 落地，本文档回填 why 并划定事件总线边界 |

## 2. 背景

### 2.1 项目处境

- [battle_map_12_cross_cutting §16](../battle_map/battle_map_12_cross_cutting.md) 留有 **31 条跨策略能力冲突仲裁规则**（设计态，CC_04），是多策略统一优化器（被否决的 A 模型前身方案）时代的遗产
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A（独立账本 + firm 聚合 + regime 风险节流）定型后，sleeve 间无统一优化器、无跨策略仓位竞争——**跨策略冲突的结构性前提已消失**
- 事件总线议题源于 battle_map_12 的"事件总线+共享存储解耦"设计（§14/§16）与 G27 讨论要点③④⑤

### 2.2 核心问题

31 条仲裁哪些保留哪些消失？事件总线/信号注入机制要什么形态？实时计算节奏（盘中 vs 盘后）如何划分？配置驱动做到什么程度？多策略投票降级到哪？

### 2.3 约束条件

- 单机 PC 工作站（i7-12700KF / 64GB RAM），无集群/K8s → 微服务级消息中间件（Kafka/Redis Streams）是过度工程
- miniQMT 10 笔/秒、Tick=3 秒 → 盘中实时性要求低，进程内调用/队列即可满足
- T+1、日频及以上根频率 → 无微秒级事件风暴，背压阈值场景罕见
- 单人 + 100% AI 开发 → 信号链路越直白，AI 归因与故障隔离越容易

## 3. 决策

### 3.1 冲突矩阵清理：31 条 → 仅留 firm-level 硬上限

**裁定**（[30 §7.3](30_multi_strategy_concurrency.md) 已落地，本文记录 why）：31 条跨策略冲突仲裁**大部分消失**——Model A 下每个 sleeve 独立 StrategyBook、独立 PnL、独立下单，跨策略冲突的结构性前提不存在。

**仅保留的 firm-level 硬上限**（继承 battle_map_12 §16 核心原则，收缩为 3 条）：

1. **防御永远优先于进攻**：风控（C-004 族）高于一切 alpha 信号
2. **仓位上限是硬约束**：firm 层求和后超上限即裁剪（FirmRiskAggregator，MOD-POS-021，production），不协商、不投票
3. **卖比买紧急**：同一标的同时出现买卖信号时，卖出（风险释放）优先执行——执行点为 `src/zephyr/sell_decision/core/sell_conflict_arbitrator.py`（MOD-SELL-008，production：强冲突 0 延迟立即执行/弱冲突延迟 1 Tick 观察，仲裁优先级 风控>C-047>市场状态>卖出>买入；depgraph 双态已与源码一致 stable+production，2026-08-15 AI-XCUT-001 实证——v1.0.1 注记的 deprecated 分裂已随 42 号 merge #ARCH-70 通道消解）

**遗留动作**：battle_map_12 §16 的 31 条清单仍按旧设计陈列，与本文裁定不一致——作战地图是生成器派生物，禁止手编；其 §16 真源=`module_translation_registry.yaml` 的 `conflict_matrix` 条目（生成器自该 YAML 派生，sync 重生成只复读真源、不会自动改真源）。2026-08-15 AI-XCUT-001 已将真源收敛（31 条→3 条 firm 硬上限），下次 sync 重生成自动闭合（见 §6）。

### 3.2 事件总线定位：任务系统用总线，交易信号链直连

**已施工设施盘点**：

| 设施 | 状态 | 职责 |
|---|---|---|
| `src/zephyr/shared/event_bus.py`（MOD-INF-016） | production | **任务系统事件总线**：任务生命周期事件（TASK_CREATED/LOCKED/...）发布订阅，背压控制（CAP-006=500 队列深度），与 ContractBus 桥接做 Schema 校验 |
| `src/zephyr/shared/events/`（dlq / event_reactor / event_schemas） | production | 任务事件的死信队列与反应器 |
| 交易信号链（signal_ashare → StrategyBook → FirmRiskAggregator → ex_core） | production | **进程内直接调用**，不经事件总线（ex_core 对 event_bus 零引用，已核验） |

**裁定**：
- **交易信号层不引入事件总线**——信号链路保持进程内直连。理由：miniQMT Tick=3 秒、10 笔/秒的约束下，直连调用延迟与吞吐绰绰有余；直连链路对 AI 归因最友好（一次调用栈即可追溯）
- **事件总线限定在任务/治理系统**——AI 任务编排、治理门禁、生命周期事件继续走 `shared/event_bus.py`（已 production，带背压与 Schema 校验，足够）
- **行业佐证**：事件驱动架构（EDA）确是交易系统行业标准（Nautilus Trader 的 EventRouter、进程内 priority queue 单核可达百万级事件/秒）——但标准形态是**进程内事件队列**，不是跨进程消息中间件。本项目若未来盘中信号源增多（新闻/龙虎榜/异动），可在进程内引入轻量事件队列复用 `shared/event_bus.py`，无需新建中间件

### 3.3 多策略投票降级

**裁定**（[30 §7.3](30_multi_strategy_concurrency.md) 已落地）：
- **BM-SEL-20 多策略投票**（CAND-HARVEST-3225）→ 已标记 **rejected**（2026-08-05）：Model A 的 sleeve 自然叠加替代投票机制。2026-08-15 AI-XCUT-001 实证补刀：archive 条目 rejected 在位，但 2026-08-07 acquisition 补登产生了同名活体候选 CAND-PFALLOC-002（alias BM-SEL-20，status=candidate）——已按本裁定同步标 rejected（防未来 AI 捡起复活候选施工幽灵模块，§4.2）
- **BM-SEL-02-K 多策略投票与加权** → 降级为**策略内部机制**（非跨策略层）
- **BM-SEL-25 双引擎融合** → 保留，定位为**打板策略内部**融合（游资引擎×量化引擎），非跨策略层

why：跨策略投票的本质是"多个弱信号合成一个强信号"，前提是存在统一的组合构建器；Model A 没有统一构建器，sleeve 各自独立下单、firm 层只裁剪不合成，投票无处可挂。投票类机制只在 sleeve 内部（双引擎融合）保留价值。

### 3.4 实时计算节奏：盘中轻、盘后重、周末全量

**已施工设施盘点**：

| 节奏 | 内容 | 设施 |
|---|---|---|
| 盘中（3 秒 Tick） | 打板链信号（评分卡/情绪定位/双引擎融合）、退潮加权、瞬时风控 | signal_ashare 引擎 + strategy_book.py |
| 盘后（每日） | 技术指标增量调度（technical_indicator_incremental）、因子增量、日终风控审计 | `src/zephyr/data/scheduler.py` + `src/zephyr/data/config/schedule.yaml` |
| 周末 | 技术指标全量回算（technical_indicator_full_refresh，覆盖 9 周期）、因子全量、IC/IR 评估 | 同上 |

**裁定**：维持"盘中轻、盘后重、周末全量"三档节奏，不引入流批一体/实时数仓。3 秒 Tick 约束下盘中只算打板必需信号；一切重型计算（9 周期指标、因子评估）放盘后/周末——与硬件约束（单机 64GB）和数据频率（日频根频率）匹配。

### 3.5 配置驱动：参数 config 化已实现，热更新/AB 测试为远期

**已施工设施盘点**：策略参数已普遍 config 化——`YouziEmotionConfig`（阶段阈值 20/40/65/85）、`FusionDecisionConfig`（基准/自适应权重）、`StrategyBook` 退潮加权系数（打板 1.5/事件 1.3/多因子 1.2）等均为 dataclass 默认值，可外部覆盖。

**裁定**：
- **参数 config 化**（当前形态）→ 保留为标准：所有策略参数必须走配置对象，禁止硬编码散落
- **参数热更新 / AB 测试** → **远期愿景，不施工**：单人单账户无并行实验流量，热更新的运维复杂度（版本对齐、回滚、审计）超过收益。参数变更走"改配置→重启→修订记录"的普通流程即可

## 4. 考虑过的替代方案

### 4.1 微服务级事件总线（Kafka / Redis Streams）—— 拒绝
单机 PC 无集群，miniQMT 3 秒 Tick 无事件风暴；引入消息中间件=多一个运维对象+多一类 AI 幻觉面（连接、分区、积压、回放），收益为零。行业 EDA 的标准形态是进程内队列（§3.2），微服务总线是集群场景的解法。

### 4.2 保留 31 条全量冲突仲裁 —— 拒绝
31 条的前提是统一组合构建器下的跨策略资源竞争；Model A 独立账本使该前提消失。保留全量矩阵会让未来 AI 误以为存在跨策略仲裁层而施工幽灵模块。

### 4.3 统一信号路由层（signal_router）—— 拒绝
在信号源与 sleeve 之间加路由层，当前只有打板链一路信号，是单消费者场景的伪抽象；等盘中信号源真实增多（≥3 类）再评估，且优先复用 `shared/event_bus.py`。

## 5. 上限定义

- **仲裁规则上限 3 条**（§3.1 firm-level 硬上限），不新增跨策略仲裁
- **事件总线上限 1 个**（`shared/event_bus.py`），服务任务/治理系统；交易信号层永远直连
- **节奏上限三档**（盘中轻/盘后重/周末全量），不上流批一体
- **配置上限静态 config 化**，热更新/AB 测试显式标注远期

为何是上限：这些上限全部由硬边界直接推出（单机/3 秒 Tick/T+1/单人 AI），任何扩张都需要先证伪约束本身。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| battle_map_12 §16 31 条清单与本文裁定的收敛 | 作战地图是生成器派生物，禁止手编。2026-08-15 AI-XCUT-001 实证：sync 重生成只复读真源不自动闭合，§16 真源=module_translation_registry.yaml `conflict_matrix` 条目——真源已收敛（31 条→3 条，生成器按 len(conflicts) 自动渲染计数） | merge 后下一轮 sync 重生成即闭合；验证标准：重生成后 §16 显示"冲突场景清单（3 条）"。若仍残留，登记 architecture_issue_registry |
| 盘中多信号源事件队列 | 当前仅打板链一路信号，无多源竞争 | 盘中信号源 ≥3 类（新闻/龙虎榜/异动齐备）时复用 shared/event_bus.py 评估 |
| 参数热更新 | 远期愿景，单人无并行实验需求 | 多账户/多实例运行时重评 |

## 7. 待定问题

G27 原讨论要点 ①-⑦ 全部 ✅ 闭合：①-⑥ 2026-08-12 v1.0.0 裁定闭合（①31 条跨策略冲突仲裁→§3.1；②仅留 firm-level 硬上限→§3.1（3 条）；③事件总线/信号注入机制→§3.2（任务系统总线+交易直连）；④实时计算节奏→§3.4（三档节奏）；⑤配置驱动→§3.5（config 化保留，热更新远期）；⑥多策略投票降级→§3.3（BM-SEL-20 rejected / 02-K 内部化 / 25 打板内部））；⑦ firm_risk_aggregator 测试缺口 2026-08-13 闭合（AI-FRA-001 merge 引入 `tests/position/test_firm_risk_aggregator.py`，覆盖 pre_kelly_aggregate/post_kelly_clip/aggregate/A-G 修复验证；2026-08-15 AI-XCUT-001 复跑实证 60 passed）——本节无未闭合项。

## 8. 引用

### 8.1 相关设计备忘与作战地图
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §7.3（需降级/重构的现有设计——本文 §3.1/§3.3 的裁定出处）
- [00_index_trading_decision](00_index_trading_decision.md) §3 G27
- [battle_map_12_cross_cutting](../battle_map/battle_map_12_cross_cutting.md) §14/§16（31 条冲突仲裁与事件总线解耦的当前快照）
- [65_git_safety_governance](65_git_safety_governance.md) / [61_lifecycle_multi_ai](61_lifecycle_multi_ai.md)（跨切治理邻接主题）

### 8.2 相关代码
- `src/zephyr/shared/event_bus.py`（MOD-INF-016，production：任务事件总线，背压 CAP-006，ContractBus 桥接）
- `src/zephyr/shared/events/`（dlq/event_reactor/event_schemas）
- `src/zephyr/position/core/firm_risk_aggregator.py`（MOD-POS-021，production：firm 层求和+裁剪）
- `src/zephyr/data/scheduler.py` + `src/zephyr/data/config/schedule.yaml`（三档计算节奏）

### 8.3 外部实证（2026 年）
- Nautilus Trader（nautechsystems）：专业级事件驱动交易系统，核心为进程内 EventRouter——印证"EDA=进程内事件队列"是行业标准形态，支撑 §3.2/§4.1
- 事件驱动交易系统五层架构（ingestion→normalization→signal→execution→独立风控层）：风控层独立于策略逻辑是行业铁律——与 §3.1"防御永远优先于进攻"及 FirmRiskAggregator 独立裁剪一致

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G27 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active 定型回填 | 核心裁定均已在 30 号 §7.3 落地，本文回填 why 并划边界：§3.1 冲突矩阵 31 条→3 条 firm-level 硬上限；§3.2 事件总线定位（任务系统总线 production+交易信号链直连，核验 ex_core 零引用 event_bus）；§3.3 多策略投票降级；§3.4 三档计算节奏（已施工设施盘点）；§3.5 配置驱动边界（config 化保留/热更新远期）；§4 替代方案（微服务总线/全量仲裁/统一路由层均拒绝）；2026 行业实证（Nautilus 进程内 EDA、风控层独立铁律）入 §8.3。G27 六个讨论要点全部闭合（2026-08-12 三次并发回滚后重建） |
| 2026-08-12 | 1.0.1 | §3.1 澄清 sell_conflict_arbitrator 归属 + §7 登记 firm_risk_aggregator 测试缺口 | AI-19 深度审查：基础设施盘点发现 ①sell_conflict_arbitrator.py（MOD-SELL-008）是 §3.1 第 3 条"卖比买紧急"硬上限执行点，原未明确归属；②firm_risk_aggregator.py 声明测试 tests/position/test_firm_risk_aggregator.py 不存在（B13 测试缺口）。本次 §3.1 补执行点澄清 + §7 补测试缺口登记。无裁定变更 |
| 2026-08-15 | 1.0.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-11）。§7 已闭合要点 ①-⑥ 合并为一行指针（裁定明细真源=§3 各节+修订记录 1.0.0），仅留 ⑦ 待补项 | 已闭合项入修订记录，消除表格与 §3 正文的状态重复；要点→落点映射零丢失 |
| 2026-08-15 | 1.1.0 | AI-XCUT-001 跨切清理施工（第 4 批）：①§7 ⑦ 测试缺口实证闭合（AI-FRA-001 已补建，复跑 60 passed），①-⑦ 全闭合；②§3.1 MOD-SELL-008 depgraph 分裂注记更新（现 stable+production 一致）；③§3.3 补 CAND-PFALLOC-002 复活候选按裁定标 rejected；④§6 battle_map §16 收敛项实证"sync 不自动闭合"，真源 module_translation_registry.yaml conflict_matrix 条目已收敛 31 条→3 条 | 统筹指派"骨架重建"前提经 Step 1 实证推翻（文档 v1.0.2 内容完整非骨架），实际施工=三处残留漂移收敛+唯一待补项闭合；00_index L74/L672 滞后登记同步 |
