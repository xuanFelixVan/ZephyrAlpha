---
ttl: task_bound
doc_type: log
title: L09-S2 子模块挖矿簿 · 盘前链
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
status: MINE 完成（六向封口；"双实现"口径本册实测升级为"三实现"）
---

# L09 · S2 盘前链

**① 职责一句话**：在 T 日开盘前把"数据齐了没、隔夜发生了什么、今天按什么预案打"三件事收敛成一个**可被盘中引用的就绪态**。

**② 现状实测（2026-09-26 本机复测）**

本块核心结论一句话：**晨间"数据"有电，晨间"工作流"没电；且工作流侧不是两套实现而是一套半 + 三套未接电的编排件。**

盘前实现的**三**套（SKEL/13 号文 TRD-A04 记为"双实现治理"，本册实测为三套，须更正口径）：

| # | 件 | module_id | 实码 | 装配方实测 | 触发面 | 判定 |
|---|---|---|---|---|---|---|
| 甲 | `src/zephyr/plan_engine/premarket_workflow.py` | MOD-PLAN-021 | 08:00-09:15 三段式**分钟级排程 DAG**（复用 `zephyr.trading.work_dag` 的 WorkDAG/WorkNode/WorkEdge，`:61` import） | 全仓 grep `premarket_workflow\|PremarketWorkflow` = 7 命中：自身 / `premarket_workflow_engine.py`（仅文档性提及）/ `plan_engine/__init__.py` / `work_dag.py`（**被依赖方向反了**——是 021 依赖 work_dag，非 work_dag 装配 021）/ error_code_registry / 两个 test | **无**（`[CONSUMERS]` 自注"运行时装配批"= 计划中的批次，非在册消费方） | **覆盖未接电**（production 名下的休眠件） |
| 乙 | `src/zephyr/plan_engine/premarket_workflow_engine.py` | MOD-PLAN-023 | 盘前标准**六工序 handler 编排**（数据同步→隔夜复盘→情绪扫描→预案生成→盘前检查→就绪确认；`:8` INVARIANTS 词表闭合/Fail-Closed/人工接管点 WAITING_MANUAL/逐工序耗时） | 全仓 grep `premarket_workflow_engine\|PremarketWorkflowEngine` = **3 命中**：自身 / 其 test / error_code_registry ⇒ **零生产装配方** | **无**；`[AI_AUTONOMY] human_gated` | **缺失（连"覆盖"都无消费面）**：纯函数库形态的引擎，六工序 handler 一个都没绑 |
| 丙 | dloop `premarket` 相位（5 段） | MOD-PLAN-033 子段 | `daily_loop_master_switch.py:338` `["data_readiness","regime_freshness","warroom","daily_plan","llm_premarket"]`，注册表 `:405-419` | 真跑 | `dloop_post` 16:45 cron（`schedule.yaml:249-253`）+ 事件链 | **已接电——但跑在 T-1 傍晚** |

关键时序错位（本册实测的核心事实）：丙这套唯一在产实现，其"盘前"段实际执行时刻=**T-1 日 16:45**，产出 `target_date=T` 的预案。于是：
- 预案本身**有**（H1 的产物 T-1 夜就在库里）；
- 但 **T 日 08:00-09:15 的"隔夜重评 + 盘前检查 + 就绪确认"整段没有任何触发面**。
- 本册实测 `schedule.yaml` 晨间槽：`pre_market` 08:30（`:24-28`，JOB-077 盘前**元数据层**）、`nightly_sentiment` 08:20（`:173-181`）、`sector_pre_open` 09:15（`:263`）、`daily_crypto` 08:30（`:77`）、auction 档 09:25（`:37`）——**全是数据落库槽，零编排器晨间槽**；
- schtasks 实测晨间段（08:00-09:15）只有 `ZephyrAlpha_QMTWatchdog` 08:45 / `ZephyrAlpha_PatternMining` 09:01 / `ZephyrAlpha_PaperSession` 09:25，均非盘前工作流。
⇒ 隔夜突变（美股/期货/公告）在 T 日开盘前**不会**被重新评一次。这就是 TRD-A04 后半"晨间窗无人上班"的机读证明。

新鲜度与旁证：
- 情绪窗真源 `nightly_sentiment` 08:20 槽在产；但 `data/runtime/` 实测残留 `nightly_sentiment.disabled.by-st-data-fix-20260921.bak`（禁用标记的备份件），且 schtasks `ZephyrAlpha_NightlySentiment` 下次运行 2026-09-25 22:30 仍在册 ⇒ **同一逻辑任务 APscheduler 槽 + schtasks 双通道并存**，TRD-A03"双通道确认项"未销口。
- `llm_premarket` 段（`:249-261`，经 `LSGSecurityGateway.infer("premarket_analysis", prompt)`）为晨间分析唯一 LLM 出口，实测在 dloop 内（T-1 16:45 跑）——**分析的是"次日开盘"，但生成时点在收盘后 75 分钟，隔夜 9 小时信息不在窗口内**。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：`pre_market` 08:30 元数据槽 / `nightly_sentiment` 08:20 / `sector_pre_open` 09:15（schedule.yaml）；T-1 16:45 dloop 产的预案。外部：已查无（"盘前检查清单/就绪确认"属券商与自营内部 SOP，公开侧只有 checklist 体裁，无标准件） |
| ②下游 | 内部：**零**——MOD-PLAN-021/023 均无生产消费方；实际"盘前就绪"由 dloop `data_readiness` 段 fail-closed 兼任（13 号文环节②）；盘中消费方（intraday_l1 / auction_hit / 风控门）读的是 T-1 夜预案而非晨间重评。外部：已查无 |
| ③算法 | 内部：021=排程算法（拓扑分层+循环拒绝，`work_dag` 语义）；023=工序编排+人工接管状态机（WAITING_MANUAL/confirm_manual 批准续跑/否决阻断，fail-closed 词表闭合）。二者自身注释已写死**查重分工**（021 重排程窗口与段序、023 重 handler 注入与耗时统计，"不重造排程 DAG"）⇒ 两件设计上互补、现实上并存且都不跑。外部：工作流引擎人工接管点=approval gate 范式（Temporal signal / Camunda user task 同构），本仓 023 已自建等价物，无需引入 |
| ④后端 | 内部：①三套实现同域并存，无"哪套是正身"登记面；②021/023 均标 `[MATURITY] production` 但零装配 ⇒ **production 标签与在产事实脱钩**（这是 maturity 词表被污染，不是本块缺陷，但由本块实测暴露）；③023 `[AI_AUTONOMY] human_gated` 意味着转正需 Owner 参与节拍；④晨间重评若开工，需新 cron 槽或新事件唤醒词（60min bar / 隔夜行情到齐），当前两者皆无。外部：已查无 |
| ⑤前端 | 内部：无盘前专用人机界面；Owner 面=warroom 组件（S5 册）。就绪态不可见 ⇒ "没电"这件事本身也无人能看见。外部：已查无 |
| ⑥数据字段 | 内部：universe 元数据/涨跌停/停复牌/ST、隔夜新闻情绪窗、隔夜参照（美股/期货）、`premarket_constraint_loader` 约束。**"字段在"≠"数据可得"落点**：预案表有 `target_date` 列且能取到 T 日行，只证明 T-1 夜产过它，**不证明 T 日晨间它仍然成立**——本块全部缺口都浓缩在这一句 |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| TRD-A04 | ①双实现治理 ②晨间窗无人上班 | 在册；本册补：**"双实现"→"三实现"（增 MOD-PLAN-023）**，且 023 连消费面都不存在，比 021 更靠前一格 |
| TRD-A03 | NightlySentiment APScheduler 槽 + schtasks 双通道 | 在册，本册实测两腿均在（schedule.yaml:178 + schtasks 下次 09-25 22:30）+ 禁用标记 .bak 残留 |
| L09-C09 | MOD-PLAN-021 复用/退役随 L09-C01 裁定 | 在册；本册扩容为 **L09-C09′：三件（021/023/dloop premarket 相位）一次性收拢**，见 ⑤ |
| L09-S2-G1（新） | **production 标签空转**：021/023 挂 production 却零装配，`[CONSUMERS]` 写"运行时装配批"这类**未来时态**充当消费方登记 | 新增 |
| L09-S2-G2（新） | **晨间隔夜突变无重评**：分析时点与开盘时点差 9 小时（美股/期货/公告全在窗外），当前链上无任何件负责闭合这段 | 新增 |
| L09-S2-G3（新） | `data/runtime/nightly_sentiment.disabled.*.bak` 孤儿标记件（禁用标记改名存档而非删除，实查闸若按 `.disabled` 精确匹配则已失效，属"僵尸闸"候选） | 新增 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 / 解锁条件 |
|---|---|---|
| TRD-A04 前半（三实现治理） | **挂起排期 + 解锁条件**：随 L09-C01 一并裁 | 不可逆点=退役任何一件都会删掉已写的 handler/测试资产；且"选哪套当正身"与"编排器权威节拍"是同一次选择，拆开裁必返工。**注**：本册不改 L09-C01 的 (a)/(b) 选项，只把"盘前三套"作为裁定的必答子问题附卷 |
| TRD-A04 后半（晨间窗） | 施工（P1） | 终局全貌判据：Owner 一人 + 100% AI 自制下，"开盘前没人上班"不成立。最小施工=在权威节拍表上补一个 T 日晨间唤醒（先不新建件，直接调 021 的三段式或 dloop `phase="premarket"` 复用丙套实码）——**这是"复用已有实码补触发面"，不是新造，符合净零内收**；若裁定不开工，则须 Owner **显式豁免并留痕**（现状=既没施工也没豁免，属"默许未接电"） |
| L09-S2-G1 production 标签 | 施工（P2，非本块独占） | 属 maturity 词表治理域（06/07 车道），本块只供实证；解锁=标签定义需明确"production"是否要求"有生产触发面"（本册主张：要求，否则一律降 trial） |
| L09-S2-G2 隔夜重评 | 施工（P1，随晨间窗同批） | 同一施工的实质动机；单独做没意义 |
| L09-S2-G3 僵尸闸 | 施工（P3 卫生项） | 一次 grep 可清；禁顺手改，登记即可 |
| MOD-PLAN-023 六工序引擎 | **不封矿** | 禁止以"当前零消费、规模小"封矿（方法论明令）：六工序词表本身就是盘前终局全貌的需求说明书。裁定=挂起排期，解锁条件=L09-C01 定了权威节拍后，把六工序 handler 绑到既有实码（数据同步=pre_market 槽产物、情绪扫描=nightly_sentiment、预案生成=daily_plan、就绪确认=新增门）——**它天然是晨间窗的实现骨架，不是重复建设** |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | 021 头注 + `work_dag` 依赖方向核（`:61` import 而非被装配） | signal | 排除"work_dag 已在产所以 021 在产"的假阳性 |
| R2 | 全仓 grep 021/023 装配方 | signal | **发现第三套实现 023 且零消费**（SKEL 未计） |
| R3 | `schedule.yaml` 晨间槽逐条读 | signal | 确认晨间全为数据槽、零编排槽；顺带实见 daily_crypto executor 漂移治本注（08:30 从未自动跑成过的先例）——**"有名无实假通道"在盘前域有前科** |
| R4 | dloop premarket 5 段与相位注册表 `:405-419` | signal | 坐实"盘前跑在 T-1 16:45"的时序错位 |
| R5 | `data/runtime` disabled 标记实扫 + schtasks NightlySentiment 在册复核 | signal | TRD-A03 双通道 + G3 僵尸闸 |
| R6 | 外部对表 | 未做 | 延至全部落盘后统一一轮；候选=Temporal signal / Camunda user task（人工接管点范式）、券商盘前 checklist SOP 体裁。登记为"未做外部对表" |

**本册封矿判据**：六向封口；"双实现"口径纠正为"三实现"并各给装配方实测；晨间窗真空给出 schtasks+schedule.yaml 双证。⇒ **子模块封矿（TRD-A04 裁定随 L09-C01）**。
