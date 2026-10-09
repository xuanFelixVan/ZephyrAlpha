---
ttl: task_bound
completes_when: 三小件+E5施工+E7查因全部消化（DB 回填经复核、E7 处方获批施工）后转归档
title: 图9 F4 后续班报告——三小件定谳+E5 接线+E7 漏斗查因（Owner 令 2026-10-04 全干并发）
owner: ZephyrAlpha-Owner
session: st-map9-f4-20261003
---

# 图9 F4 后续班报告（Owner 令：1、2、3 全干 + 两个目检并发）

> DB 军令状按你 2026-10-04 令解除；所有 DB 操作仍走正门 DatabaseService（reader 角色，零裸连接）。

## 一、①MOD-BT-201 双源考古——定谳：201=前哨对账器（forward_post），high 置信

**结论**：不是互换、不是重挂，是**单向撞号**。闭卷闸（closed_book_gate.py）2026-10-02 出生时，第 1 行被复制粘贴盖了 forward_post 的 `[BLUEPRINT] MOD-BT-201` 模板头；作战图对账报告那行"201=Closed Book Gate"是**三手派生物**（生成器扫到错误头注再生），且该报告文件已 untrack。
**证据链**（git 考古全录）：①201 出生 commit `5dc80204011`（09-16，四大件蓝图明文"号段 201-210 grep 确认空闲"，201=前哨对账器）；②forward_post 族 `dc24e2e8cc8`（09-16）头注至今 201；③closed_book_gate 出生 commit `055ad8cf307`（10-02）diff 第 90 行可见新文件第 1 行=与 forward_post 逐字相同的模板头；④path_ownership_map 两行均指 forward_post 族，无闭卷闸挂 201 行。
**已执行处方**：闭卷闸头注改授 **MOD-BT-205**（201-210 段空闲实查，205 零占用；注释级修正，测试 5 passed）；battle_map 报告是派生物禁手改，下次生成器跑批自愈。

## 二、②ig_fact 真身——定谳：depgraph PG 库裸表名，校验器已升级

**真身**：PostgreSQL depgraph 库的产业链图谱事实表 `ig_fact`（subject/relation/object/value/confidence/market/source/as_of），多源合成：CKG 数据集全量导入（source='ckg_2021'，PIT as_of=2021-10-26）+ LLM 图谱增补（graph_enrich_ingest，source 可溯源）。车道D 真身 three_high_screen.py 走 `get_depgraph_pg_connection` 三 relation 聚合（belongs_to_sector/produces/supplies_to）。
**已执行处方**：①校验器新增 `pg:` 前缀分支（to_regclass 探测；**PG 不可达=warn 降级不阻断**——图结构是本职责，PG 可用性是环境属性）；②图9 FAC-E1D data_refs `ig_fact` → `pg:ig_fact`。**校验器警告 3→2**（余两条均为设计内"待定"占位：E9 入库位、E1 news 表）。

## 三、③DB 化验——8 条处方代跑结果（6 针见血 + 2 针追问针）

| 处方 | 实测结果 | 一句话解读 |
|------|---------|-----------|
| c1_backtest.strategy_screen | **1401 行 / 574 策略 / 最新批 SIM-DEV-2026-09** | E4 考试咽喉真在批量出货 |
| 考试判定分布（追问针） | screened_in 381（358 台）｜deferred_c4 321｜rejected 216（198 台）｜translated_c4 206｜oos_tested 169（81 台） | 漏斗上游健康：358 台进池、198 台被毙 |
| c1_backtest.hypothesis_precheck | 309 行 / 231 候选 | E2 预审在跳 |
| 预审判定分布（追问针） | 毙 155 / 过 114 / 缓 40 | 防噪音总闸称职 |
| c1_backtest.sim_daily_report | 258 行 / **11 天**（日期列=report_date，处方列名笔误已现场纠正） | 模拟盘日刊 11 天的量 |
| c1_backtest.regime_snapshot_history | 3632 行 | E8 元分配输入在积累 |
| c1_backtest.alloc_budget_daily | 30 行 / 11 天 | E8 sleeve 落库刚开始 |
| c1_backtest.decision_daily | 136 行 | 日度决策快照在跑 |
（n_trials/factor_casebook 两处方为磁盘册：前者已计 8 entries，后者盘面无实例维持零。）

**以上数字已回填 `fac9_03_facts.yaml` db_results 附注节。**

## 四、E5 接流水线——施工完成（收敛式接法，零行为漂移）

**验尸反转**：E5 去重功能**一直在流水线里跑**（C6 自动入库编排器 intake.py 的 cluster_heads，事件触发 pipeline_events:432 → run_intake_auto）——但那是管线自带的**复制品**，图上挂的正主 MOD-BT-086 从未被调用（F3 实测仅测试消费的真相）。
**施工**（收敛式，不换算法不换行为）：
1. `synergy_dedup.py`（MOD-BT-086）晋升 **E5 唯一算法核**：corr-pairs 并查集核 `cluster_heads_from_corr` 从 intake.py **逐字迁入**（PIT 活矩阵契约、p 值定簇首、确定性排序全保留）；原 returns+sharpe 星形贪心 API 原样保留（不同输入契约，非克隆，头注 INVARIANTS 已改写双契约声明）。
2. `intake.py` 的 cluster_heads 变**薄委托**（3 行：import 086 核并转发；签名/语义/返回零漂移，保住既有调用面）。
3. 依赖方向合法：strategy_pipeline→pf_alloc 为仓内既定方向（daily_gate_snapshot/orchestrator/pipeline_events 均已如此 import）。
**回归**：test_synergy_dedup 4 passed + test_intake 15 passed。
**能力反查**：CapabilityLookup.find("synergy dedup correlation cluster") 已记账（空结果=无既有同类能力登记，确认非重建）。
**图9 同步**：FAC-E5-M-001 的 consumers/trigger_facts 已翻案（见地图本批 diff）——E5 从"实测零消费"变"管线消费中"。

## 五、E7 漏斗 161:2 查因——根因定谳（侦察兵全链路证据）

**真相一句话：不是及格线太狠，是"复评机"从来没造出来——幂等闸把老候选永远挡在重检门外。**
1. **法定条件链**（lifecycle_fsm）：candidate→sim 需三条件全绿（§8 双窗及格 ∧ BH-FDR q≤0.10 ∧ 无挂起衰减告警），全 fail-closed（缺证据=不过）。
2. **致命死路（代码实证）**：intake.py:291-296 幂等闸在 sim 判定**之前**——已入库的 candidate 在后续批次永远被 skip（"已入库（重放幂等）"）；代码注释承诺"后续批次重检"，但全仓**没有任何** re-screen/re-FDR 巡检事件kind。151 台老候选（多为 09-13 前手工/翻译批登记）结构上不存在复评路径。
3. **那 2 台 sim 的来历**：STR-E-TIMING-001 + STR-VREV-025 = **同一个恐慌反弹想法的原版+翻译克隆**，2026-09-13 由 C4 考试批直接以 sim 写册——早于状态机（09-15）诞生，属历史特批，没走过三条件门。sim_deviation 104 行全来自其一。
4. **sim→production 侧**：链条已建（月度偏离→advisory→Owner 前端拍板）但零实弹（观察期需连续 2 月，最早 11 月；通知唯一出口=前端横幅）。
**处方三连（呈批，按改动面从小到大，未施工待批）**：
- **Rx-1（最小）**：改幂等闸语义——已入库且 lifecycle∈{sim,production} 才 skip；candidate 态改为重评三条件，过则补走 promote_to_sim+开户事件。搭每次 C4 批测便车。
- **Rx-2（中）**：新增 candidate_reexam_due 月度巡检事件（模板照抄 sim_deviation_monthly），对全 candidate 池重跑 FDR+衰减复核——清库存主通道。
- **Rx-3（铺垫）**：证据补课排产——对 evidence 空的候选先排 E4 考试产 §8 双窗行（否则 Rx-1/2 也会在 dual_window_pass 上全灭）。
**一句话**：批准 Rx-1（+可选 Rx-3）= 漏斗开始流水；Rx-2 随后。

## 六、账面变动汇总

- 代码三处：synergy_dedup.py（+核/头注）、intake.py（薄委托）、closed_book_gate.py（201→205 头注）——测试 4+15+5 passed。
- 校验器一处：+pg: 分支（降级安全）。
- 图9 两处：FAC-E1D data_ref 修正；FAC-E5-M-001 血肉翻案。
- 台账/验收件：名实挂账#1（BT-201）销账；E5 最薄结论修正；E7 处方呈批。
- 红账：无新增；验证器 WARN 3→2。

---
> 归档注记（st-map9-chief-20261005 重建班）：本报告为第三次重建件——原件随死袋两次遭队列手术销毁（blob 二次全灭），内容按原会话上下文逐字复原；Rx-1/2/3 已由 Owner 批准并落 HEAD（9980283143/b7eb75cafe/50e48af4b6），§五处方段为历史呈批态留档。