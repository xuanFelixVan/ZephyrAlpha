---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=回测框架对接 · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.4 · date=2026-08-15 · topic=backtest_framework_docking · scope=07_trading_decision_architecture

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**：本篇性质为"已施工框架的 why 回填 + 策略侧复用裁定"，自身承诺的新施工为零。BM-BT-01~07 框架代码（引擎/撮合/PIT/过拟合/WFA/门控/io 三件套/scheduler）均已在更早批次建成 production（2026-08-19 实证：backtest/core 全部在位 + services/scheduler.py + io/decisiongraph_adapter.py 在位）；53 号 §3.1 对本篇 §3.4 的悬空引用已由本版 §3.4 补位闭环。
>
> **最终成果**（2026-08-19 代码实证）：`engine_base.py` / `vectorized_engine.py` / `event_driven_engine.py` / `shrinkage_engine.py` / `matching_logic.py` / `portfolio.py` / `scheduler.py` / `data_handler.py` / `metrics.py`（含 `calculate_dsr`，阈值 0.5）/ `pit_manager.py` / `overfitting_detector.py` / `walk_forward.py`（CPCV 仅配置预留）/ `decision_gate.py` / `tick_replay.py` 全生产态；`simulation/deflated_sharpe_calculator.py`（MOD-SIM-024，阈值 0.95）在位——DSR 双实现并存实证与 §3.6/§7⑤ 登记一致。⚠️ 复核发现 §3.1.1 两处滞后：`services/cache_manager.py` 与 `services/report_generator.py` 均已 MATURITY=production（文中标"design / 不抢先施工 / MD 摘要随首批施工"），系文档滞后于代码，非施工缺口。
>
> **未做事项及原因**：
> - CPCV+PBO / Purged K-Fold / 03-E CRPS / 回测异常诊断（BM-BT-07-F）——§6 已逐条裁定暂缓并给重评条件（变体>50 或 DSR 频繁误报 / 标签重叠窗口策略上线 / regime 密度预测上线 / 故障样本≥10 例），属设计内延期非烂尾；裁定=未来工程-小型（03-E CRPS 依赖 91 号密度预测路线，归未来工程-大型）。
> - 07-H result_deployer——§4 已裁定拒绝门控全自动上线（can_deploy≠部署许可，实盘部署人工审批承载）；裁定=过度工程（当前阶段人工审批即正确上限）。
> - 策略验证流水线编排入口（§7①"随首批上线施工"）——首批策略未上线，等触发；裁定=未来工程-小型。
> - DSR 双实现统编（backtest 版阈值 0.5 vs simulation 版 0.95）——tracker 遗留 #14 ⏳ 等 Owner 裁定唯一 SSoT 或明确分工；裁定=未来工程-小型（裁定后单行收敛）。
> - DSR 接入 DecisionGate 判定链（§7③ 待决策：dsr≥阈值是否加为 OOS 段第四条件）——2026-08-19 实证 decision_gate.py 零 dsr 引用；裁定=未来工程-小型（随上项裁定一并落地）。
> - 四核心模块零单测（walk_forward/decision_gate/overfitting_detector/pit_manager + calculate_dsr 无直接测试，§7 新发现 1，P1）——2026-08-19 实证 tests/ 下无对应测试文件；裁定=未来工程-小型（测试债，建议随下一测试债批清偿）。
> - battle_map_03 滞后同步 / 00_index 版本同步（§7 新发现 2/4/5，越界登记项）——属 battle_map/00_index owner 会话范围；裁定=未来工程-小型（文档治理，随下一治理批顺手）。

# 回测框架对接

> **性质**：决策备忘（G23）。核心事实：BM-BT-01~07 的**框架代码已基本全部 production**（D_BACKTEST 51 模块 = 50 生产 + 1 设计），regime 侧已按 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §2.1 完成对接；本文回填框架 why，并裁定**策略侧**（20 号首批 3 策略）如何复用同一框架。
> **历史说明**：00_index 标本文"active v1.7.4"，磁盘仅存骨架——完整版曾丢失，本版按已施工代码 + 11/53 号设计依据重建为 1.0.0。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G23 回测框架对接 |
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿 v1.2.0） |
| 对标 | 11 号 regime 对接范式 / Morwane walk-forward |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 优先级 | P2（G04 后） |
| 状态 | ✅ active v1.0.0（框架 production；策略侧编排与缺口见 §6/§7） |

## 2. 背景

**项目处境**：D_BACKTEST 域已施工 51 个模块（35 号域文档：50 生产 + 1 设计），覆盖引擎/撮合/PIT/WFA/过拟合检测/门控全链路。regime 侧（11 号）已按"复用同一框架"完成对接并产出 C1 对比器等适配件。策略侧（首批打板/多因子/事件驱动）尚无对等的验证流水线编排。

**核心问题**：策略验证与 regime 验证共用框架，但验证目标相反——策略要证"alpha 显著"，regime 只证"节流有效、不伤害即可"。对接不是接代码（代码已在），而是裁定策略侧逐环节的用法与门控标准。

**约束条件**：A 股 T+1、涨跌停、100 股整手、印花税/佣金——回测必须产生实盘可复现的成交（撮合一致性）；样本量有限（个股历史十余年）——过拟合是最大敌人；单机算力——向量化优先、事件驱动按需。

## 3. 决策

### 3.1 已施工设施盘点（BM-BT-01~07 代码映射）

| 环节 | 代码落点 | 状态 |
|---|---|---|
| BM-BT-01 引擎与撮合 | engine_base.py（ABC+注册表）/ vectorized_engine.py / event_driven_engine.py / shrinkage_engine.py / matching_logic.py（纯函数撮合：市价/限价/5 档 tick，万三佣金+1bp 滑点+印花税，全 Decimal）/ portfolio.py（T+1 锁定/非负约束）/ scheduler.py（网格搜索+并发） | ✅ production |
| BM-BT-02 持仓组合与数据接入 | data_handler.py（BacktestDataHandler/MultiSourceDataHandler+PIT 合并）/ cache_manager / data_quality_checker | ✅ production |
| BM-BT-03 绩效指标与 Tick 回放 | metrics.py（Sharpe 用 10 年期国债 rf=2.5%，样本<60 不算 Sharpe）/ tick_replay.py；03-E 密度预测验证（CRPS）未施工 | 主体 ✅ |
| BM-BT-04 PIT 铁律 | pit_manager.py（AS OF JOIN + Embargo + 一致性测试 + 幸存者偏差检测）；04-C Purged K-Fold 无代码 | 04-A/B ✅ |
| BM-BT-05 过拟合检测 | overfitting_detector.py（三维度+三层）/ walk_forward.whites_reality_check / metrics.calculate_dsr + simulation/deflated_sharpe_calculator.py；05-F/I/J 未施工 | 核心 ✅ |
| BM-BT-06 Walk-Forward | walk_forward.py 三模式（rolling/anchored/expanding，块长自动 T^(1/3)）；06-C 自适应 WF 无代码 | 06-A/B ✅ |
| BM-BT-07 决策门控与上线 | decision_gate.py（IS→WFA→OOS 不可跳级+参数锁定）/ io 三件套（result_sink/repository/decisiongraph_adapter）；07-H result_deployer 设计态（受限需 D-EX-CORE 就绪） | 07-A~G ✅ |

**回测=实盘一致性的核心 why**：`MatchingLogic` 纯函数撮合被 D_BACKTEST 与 D_EX_CORE MiniQmtBroker **共同调用**——回测和实盘走同一段撮合代码，从根上消除行为偏差；`Portfolio` 在组合层强制 T+1/非负，防止回测产生实盘不可能的成交。

#### 3.1.1 辅助组件契约（作战地图环节补丁）

- **BM-BT-01-E 自动回测调度器（production）**——定位：批量参数网格回测的调度入口，落点 `scheduler.py`（网格搜索+并发，已随引擎列 §3.1 表 production）。裁定：✅ 已施工，策略侧批量网格直接复用，不另建调度器；理由：调度与引擎同域共演进，单机约束下进程内队列即为上限；重评条件：批量任务需跨日排队/定时无人值守时，再评外部任务队列。契约：入参=策略类+参数网格（dict[str, list]）+回测配置；队列策略=FIFO worker 池；并发度契约=向量化 preload 全内存模式下 worker 数 ≤ CPU 核数/2，事件驱动逐 tick 模式并发=1；出参=批量 BacktestResult 聚合，单点失败落错误记录不阻断整批。
- **BM-BT-01-F 回测加速架构（design）**——定位：大批量网格搜索的加速层（真源 §20.7 L1 算法/L2 框架/L3 GPU 三层）。裁定：🔨 约束内只做 L1 层——单机向量化优先（向量化引擎+数据预加载复用），Numba/GPU 不引入；理由：首批 3 策略百级网格组合向量化秒级完成，GPU 的驱动/CUDA 运维对个人单机是纯负担（与 64 号向内收口径一致）；重评条件：网格组合 >1 万且单批 >30 分钟时启用 Numba（L2），GPU（L3）仅在其后再评。契约（设计）：并行度=进程级（ProcessPool 绕 GIL，与 FactorDAG 双执行器同范式）；数据预加载=calc_mode=preload 日K 全内存快照 worker 间共享（写时复制），禁止每 worker 各自查库；缓存复用命中率目标 ≥80%（同数据段不同参数组合共享数据层缓存，键构成见 BM-BT-02-C）。
- **BM-BT-02-C 回测缓存管理器（design）**——定位：回测请求→缓存检查→命中/未命中，预定落点 services/cache_manager.py（真源标 planned, P2）。裁定：🔨 设计态不抢先施工；理由：当前耗时主项是撮合/指标计算而非数据加载（preload 已全内存），缓存收益集中在"同数据段反复网格搜索"，随首批调参频率上来再建；重评条件：单策略日回测 >20 次或同数据段重复加载占比 >50%。契约（设计）：缓存键=（数据段 hash + PIT 快照版本 + 引擎配置 hash），**不缓存含撮合结果的终态**（防口径漂移拿旧结果）；策略=内存 LRU（数据快照）+ 磁盘 parquet（数据段物化）；过期=以 ClickHouse `max(ingest_ts)` 为版本戳、数据变更即失效——过期由数据版本驱动而非 TTL 时间驱动。
- **BM-BT-07-D decisiongraph 适配（production）**——定位：BacktestResult→decisiongraph L5 节点，落点 `io/decisiongraph_adapter.py`（已列 §3.1 表）。裁定：✅ 已施工，回测结论进决策图唯一通道；适配器不可用时回测结论不进决策流、人工衔接（真源 degradation 口径）。契约（L5 节点字段映射）：node_id=回测 run_id；node_type=`backtest_verdict`；payload={strategy_id, is_sharpe, wfa_pass_rate, oos_is_ratio, dsr, can_deploy, gate_stage}；timestamp=回测完成时刻；edge 指向策略定义节点（G04 产出物）。
- **BM-BT-07-E 回测报告生成（design）**——定位：BacktestResult+BacktestSinkData→格式化报告，预定落点 services/report_generator.py（planned, P2）。裁定：🔨 分两档——**MD 摘要为必建档**（随策略验证流水线一并施工），HTML/PDF 登记远期；理由：个人消费场景 MD 摘要+Panel 双曲线（51 号）已覆盖阅读需求，PDF 是合规/对外产物本项目无消费方；重评条件：策略数 >5 需定期审计快照时启用 HTML（自包含单文件优先于 PDF）。契约（设计）：MD 摘要必含字段——策略标识/参数快照/回测区间/数据版本戳/IS·WFA·OOS 三段指标表（Sharpe/MaxDD/Calmar/换手率）/过拟合三维结论/DSR 值与 n_trials/门控判定（can_deploy+理由）/人工审批签名位。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-01-A | 引擎基座与契约 | §3.1（engine_base.py ABC+注册表、BacktestResult 契约） | production已建 |
| BM-BT-01-B | 向量化回测引擎 | §3.1（vectorized_engine.py）/ §3.2（多因子/事件驱动用向量化引擎） | production已建 |
| BM-BT-01-C | 撮合引擎 | §3.1（matching_logic.py 纯函数撮合，"回测=实盘一致性"核心 why） | production已建 |
| BM-BT-02-A | 持仓组合管理 | §3.1（portfolio.py T+1 锁定/非负约束） | production已建 |
| BM-BT-02-B | 多源数据接入 | §3.1（data_handler.py BacktestDataHandler/MultiSourceDataHandler+PIT 合并）/ §3.2（统一走 BacktestDataHandler） | production已建 |
| BM-BT-03-C | 事件驱动回测 | §3.1（event_driven_engine.py）/ §3.2（打板用事件驱动引擎） | production已建 |
| BM-BT-06-A | 滚动窗口回测 | §3.1（walk_forward.py rolling/anchored/expanding 三模式） | production已建 |
| BM-BT-07-B | 回测结果Sink | §3.1（io 三件套 result_sink/repository/decisiongraph_adapter） | production已建 |

### 3.2 要点①：BM-BT-01~07 在策略验证中的用法

策略侧复用映射（对标 11 号 §2.1 regime 范式）：

| 环节 | 策略验证用法 |
|---|---|
| 01 引擎 | 多因子/事件驱动用向量化引擎（速度快、网格搜索友好）；打板用事件驱动引擎（Tick/分钟级，撮合真实感优先） |
| 02 数据 | 统一走 BacktestDataHandler，PIT 合并强制开启 |
| 03 指标 | calculate_full_metrics（基础+DSR）为唯一产出口径 |
| 04 PIT | 三件套全开：AS OF JOIN + Embargo 5 个交易日 + 幸存者偏差检测（退市股入池） |
| 05 过拟合 | 三维度全跑 + strict_overfitting_gate=True（引擎层硬阻断，SIM-56） |
| 06 WFA | rolling 为主（A 股非平稳），anchored 对照；White's Reality Check 校正多重比较 |
| 07 门控 | DecisionGate.evaluate 三阶段不可跳级；can_deploy 后仍需人工审批（技术门控≠上线许可） |

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-05-C | 多重比较校正 | §3.2（06 WFA 行：White's Reality Check 校正多重比较）/ §3.6（DSR 多重测试偏差修正） | production已建 |

### 3.3 要点②：策略回测 vs regime 回测差异（裁定）

沿用 11 号 §1.3 六维差异并补策略侧裁定：

| 维度 | 策略回测 | regime 回测 |
|---|---|---|
| 验证目标 | **证 alpha 显著**（Sharpe>0.5 准入） | 证节流有效、不伤害即可 |
| 过拟合风险 | 高（参数多、直接挖收益）→ 三维度+DSR 全负荷 | 低（自由度小）→ 简化 |
| 门控标准 | IS Sharpe≥0.5 + WFA 多数 fold 通过 + OOS/IS≥0.70 | 节流对比实验（C1 对比器） |
| 输出消费 | 上线许可 + budget 分配输入 | Shrinkage 系数 |
| 因果链 | 信号→持仓→PnL 全链 | regime 标签→仓位缩放 |
| 对接模块 | DecisionGate + overfitting_detector 全量 | shrinkage_provider/engine 适配层 |

### 3.4 要点③：策略上线门控 IS→WFA→OOS（已施工，53 号锚点补位）

`decision_gate.py`（791 行 production，不变量："IS→WFA→OOS 不可跳级；参数锁定；Sharpe>0.5 准入"）：
- **IS 段**：Sharpe≥0.5 准入 + 参数稳定性（±10% 窗口 Sharpe 变化<20% 判高原，相邻点降>50% 判悬崖——避悬崖比找峰值重要）；
- **WFA 段**：多数通过（>50% fold）+ 灾难否决（任一 fold MaxDD>50% 一票否决）；WFA 看 fold 相对稳定性而非绝对准入（阈值 0.0）；
- **OOS 段**：参数锁定强制 + OOS/IS Sharpe≥0.70（SSoT 单向导入自 overfitting_detector）；
- `evaluate()` 编排不可跳级，`can_deploy` 仅技术门控，正式上线需人工审批。
本节即 [53_simulation_live_path](53_simulation_live_path.md) §3.1 引用的"52 号 §3.4 IS→WFA→OOS 门控放行"锚点——回测门控通过是 53 号 PARALLEL→SHADOW→GRAY_RAMP 三阶段迁移的前置。2026 年业界共识（WFA+DSR+canary 部署三过滤器）与本链路同构：canary ≈ 53 号 GRAY_RAMP。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-06-B | 样本外验证与参数稳定性 | §3.4（IS 段参数稳定性±10% 窗口裁定 + OOS 段参数锁定/OOS÷IS≥0.70）/ §3.5（三维度①walk-forward 稳定性、③泛化） | production已建 |
| BM-BT-07-A | 三阶段决策门控 | §3.4（decision_gate.py IS→WFA→OOS 不可跳级+参数锁定+人工审批） | production已建 |

### 3.5 要点④：过拟合检测三维度（已施工）

`overfitting_detector.py`：①walk-forward 稳定性（正 Sharpe fold≥60%、CV≤1.5、无灾难 fold）②参数敏感性（±10% 扰动 Sharpe 变化≤30%）③泛化（跨时段/跨标的正 Sharpe≥60%）；三层防线：检测器 → SIM-38 样本内外对比（<0.70 硬否决）→ SIM-56 引擎层 OverfittingGateError 硬阻断。why 三维度而非单维度：单一维度都有绕开路径（WF 稳定可参数刷出来、参数稳定可时段刷出来），三维交叉才构成个人可执行的最低可信标准。

### 3.6 要点⑤：Deflated Sharpe（已施工，双实现待统编）

DSR（Bailey & López de Prado 2014）两处实现：`backtest/core/metrics.py calculate_dsr`（非正态修正+多重测试偏差修正，DSR<0.5 判过拟合）与 `simulation/deflated_sharpe_calculator.py`（MOD-SIM-024，阈值 0.95，有专属测试）。why 必须 DSR：个人开发试错次数多（AI 并发生成策略变体），多重比较偏差是首要过拟合来源——2026 年研究复算：3 次试错即可让零 alpha 策略呈现统计显著假象；`n_trials` 强制调用方传实际试错次数，防默认值自我安慰。双实现口径不一的统编问题登记 §7。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-05-J | p-hacking追踪 | §3.6（DSR `n_trials` 强制传实际试错次数）承载 production 机制；完整试验追踪暂缓裁定见 §5（05-F/I/J 判研究级组件不建） | production已建（n_trials 机制）+ 暂缓裁定（完整追踪） |

## 4. 考虑过的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 策略侧另建独立回测栈 | 拒绝——同一撮合/PIT/门控复用是"回测=实盘一致"与"策略/regime 可比"的前提 |
| 外部回测框架（backtrader/zipline/vectorbt） | 拒绝——A 股 T+1/涨跌停/整手/印花税原生内建比改造外部框架更可靠；且撮合须与 MiniQmtBroker 共享 |
| 门控全自动上线（can_deploy 即部署） | 拒绝——07-H result_deployer 保持设计态，实盘部署必须人工审批（53 号迁移路径亦如此） |
| CPCV+PBO 立即补齐 | 暂缓——2026 金标准但实现重；现有 WFA+White's RC+DSR 已覆盖多重比较主风险，列 §6 待裁定 |
| BM-BT 七环节砍到 3-4 环节 | 拒绝——七环节代码已全部 production，砍环节=删已绿代码且无收益；环节粒度对应"引擎/数据/指标/PIT/过拟合/WFA/门控"各自独立演进轴，合并反而耦合 |

## 5. 上限定义

- **系统上限**：三引擎（向量化/事件驱动/Shrinkage）+ 三维度过拟合 + 三阶段门控 + DSR，对个人 3-5 策略组合已是上限。
- **演进路径**：策略侧编排入口（统一"策略验证流水线"调用 DecisionGate）随首批上线补；CPCV/Purged K-Fold/Permutation Test 按需升级（首批变体数量>50 时多重比较风险升级再启用）。
- **为何是上限**：05-F/I/J（Permutation/组合级/p-hacking 追踪）与自适应 WF 属研究级组件（OE-009 同族），个人系统变体规模不需要。
- **BM-BT-07-I 分层验证门控 V1-V6 显式裁定：不独立施工**——已由 §3.4 三阶段门控 IS→WFA→OOS（≈V1 基础检验/V2 样本外/V3 稳健性）+ [53_simulation_live_path](53_simulation_live_path.md) §3.1 PARALLEL→SHADOW→GRAY_RAMP（≈V5 模拟盘→V6 小仓位实盘）等价承载，V4 压力测试由 BM-SIM-04 压力测试引擎域承接；再建一套 V1-V6 门控=同一防线两套阈值，AI 并发施工时口径必然漂移。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| CPCV + PBO（BM-BT-05 升级） | 实现重；现有组合已覆盖主风险 | 策略变体 >50 或 DSR 频繁误报 |
| Purged K-Fold（BM-BT-04-C） | WFA 的 Embargo 已部分等效；独立实现待 P1-18 | 标签重叠窗口策略（多周期持仓）上线时 |
| 07-H result_deployer（自动部署） | 受限项：涉实盘安全，需 D-EX-CORE 就绪 | 53 号 GRAY_RAMP 完成后 |
| 03-E CRPS 密度预测验证 | 仅 regime 密度预测需要，策略侧无消费方 | regime 密度预测上线时（11 号范围） |
| 回测异常诊断（BM-BT-07-F：诊断规则库+修复建议库） | 故障样本为零，规则库无素材；错误日志字段随 50 号五零件接入顺带落地 | 首批策略回测故障积累 ≥10 例 |

**作战地图环节映射**（暂缓/上限类环节锚定）

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-05-F | Permutation Test 置换检验 | §5 上限定义（研究级组件不建——个人系统变体规模不需要）+ §6 CPCV+PBO 行（变体 >50 或 DSR 频繁误报时随多重比较升级一并启用） | 暂缓裁定 |
| BM-BT-06-C | 自适应 Walk-Forward | §5 上限定义（自适应 WF 属研究级组件，OE-009 同族不建；滚动/锚定/扩展三模式已 production） | 暂缓裁定 |
| BM-BT-07-H | 回测结果部署 | §4 替代方案（拒绝门控全自动上线——can_deploy≠部署许可，实盘部署必须人工审批）+ §6 07-H result_deployer 行（53 号 GRAY_RAMP 完成后重评） | 暂缓裁定（人工审批承载） |

## 7. 待定问题（G23 五要点逐项裁定）

- [x] ① **BM-BT-01~07 策略验证用法**——✅ 已定（§3.2 映射表）；🔨 缺统一编排入口（策略验证流水线），随首批上线施工。
- [x] ② **策略 vs regime 回测差异**——✅ 已裁定（§3.3）。
- [x] ③ **IS→WFA→OOS 门控**——✅ 代码已施工（§3.4）。⚠️ 缺口：regime 适配版门控未启动（11 号 §0.5 Phase 5，归 11 号）；DSR 未接入 DecisionGate 判定链——**待决策**：是否把 dsr≥阈值 加为 OOS 段第四条件。
- [x] ④ **过拟合三维度**——✅ 代码已施工（§3.5）。缺口：05-F/I/J 与 05-H 归因分解（登记 §6）。
- [x] ⑤ **Deflated Sharpe**——✅ 代码已施工（§3.6）。⚠️ **待决策（双实现统编）**：backtest 版（阈值 0.5）vs simulation 版（阈值 0.95）裁定唯一 SSoT，或明确分工（引擎内快速筛查用 backtest 版 / 独立评估报告用 simulation 版）。

**代码层新发现问题**：
1. **四个核心模块零单测**——walk_forward.py / decision_gate.py / overfitting_detector.py / pit_manager.py 均无专属测试（G23 的骨架在裸奔）；backtest 版 calculate_dsr 亦无直接测试。补测试列 P1。
2. battle_map_03 详节滞后——BT-07 metrics 扩展标 planned（DSR 实际已施工）、scheduler 标 planned（已 production），需同步 battle_map 真源（越界，登记在此）。
3. 53 号 §3.1 对"52 号 §3.4"的悬空引用已由本版 §3.4 补位。
4. **00_index 同步（越界登记）**：00_index 标本文"active v1.7.4"，与本版 1.0.0 不一致，需同步（详见 33 号 §7 新发现 7 的统一登记）。
5. **battle_map 真源口径冲突（越界登记）**：BM-SIM-03（场景生成与蒙特卡洛）/ BM-SIM-06（仿真结果分析）design_maturity 标 production，但 code_mapping 为 "D-SIMULATION-05/06（planned）" / "D-SIMULATION-12（planned）"——成熟度标注与代码映射矛盾，需回 battle_map 真源裁定。（BM-BT-01-E scheduler "planned 标注 vs 已 production" 已在第 2 条登记，不重复。）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G23
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §1.3 / §2.1（regime 对接范式）
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [53_simulation_live_path](53_simulation_live_path.md) §3.1（回测→模拟→实盘迁移，引用本文 §3.4）
- 35_d_backtest（D_BACKTEST 域 51 模块清单）
- 代码：`src/zephyr/backtest/core/`（engine_base/walk_forward/pit_manager/metrics/decision_gate/overfitting_detector/matching_logic/portfolio）
- battle_map_03_backtest_validation（BM-BT-01~07 状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G23 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active：回填 BM-BT-01~07 全部代码映射与五要点裁定；§3.4 补 53 号悬空引用锚点；§4 补"七环节不砍"裁定；登记双 DSR 统编等 4 项新发现 | 完整版（v1.7.4）曾丢失，按已施工代码重建；未施工项（CPCV/Purged K-Fold 等）入 §6 待裁定不擅自补齐 |
| 2026-08-12 | 1.0.1 | 作战地图全覆盖补丁——闭合 BM-BT-01-E/01-F/02-C/07-D/07-E（§3.1.1 辅助组件契约）、BM-BT-07-F（§6 待裁定，重评=故障≥10 例）、BM-BT-07-I（§5 显式裁定不独立施工）；§7 补登 BM-SIM-03/06 成熟度口径冲突 | 回测域 7 环节补丁：production 组件补契约、design 组件定暂缓与重评条件，不新施工 |
| 2026-08-12 | 1.0.2 | 作战地图环节映射补强——锚定 BM-BT-01-A/01-B/01-C、BM-BT-02-A/02-B、BM-BT-03-C、BM-BT-05-C/05-J、BM-BT-06-A/06-B、BM-BT-07-A/07-B（§3.1/§3.2/§3.4/§3.6 末各增映射块） | 语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-12 | 1.0.3 | 作战地图环节映射补强②——锚定 BM-BT-05-F / BM-BT-06-C / BM-BT-07-H（§6 待裁定表末映射块，暂缓/上限类环节锚定到 §5 上限与 §4 替代方案裁定） | 同上：环节级可追溯；不改既有正文 |
| 2026-08-15 | 1.0.4 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-04）——§5 上限定义单段巨型散文（>300 字）要点化为 4 条（系统上限/演进路径/为何是上限/BM-BT-07-I 裁定），全文参数/裁定/环节锚点零丢失 | 8 类扫描仅此 1 处（类别 1）；其余章节经复扫已达收敛 |
