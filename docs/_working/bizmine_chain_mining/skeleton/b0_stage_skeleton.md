---
ttl: task_bound
completes_when: 16 环节 B2 深挖全回标 + B3/B4 零新枝 + 封顶声明落 a4_sealing_verdict.md
title: 业务层 Alpha 挖掘全链路·环节骨架（路由表+计分板+防腐对象）
owner: ZephyrAlpha-Owner
language: zh
status: B1 批初判已落，B2 逐车道实查中
created: 2026-09-19
session: st-bizmine2-20260919
---

# 引言（骨架四要素，模板取自 `docs/_working/altdata_line/01_data_type_skeleton.md`）

- **目标一句话**：把「数据→假设→构造→筛→正交→预注册→窄考→正考→条件化→组合→转正→在产→监控退役→归因再生」这条业务层 alpha 链的**环节全集**钉成路由表，使任何后续会话可从骨架领条目动工、可度量收敛、可防腐。
- **粒度阶梯**：大类=环节 **16**（本表）→ 中类=完整性检查单元（每环节 4-9 条，B2 回填计数）→ 叶=生产者代表（具体实装/算法/数据源，示例非穷举）→ 数据集=施工产物。
- **标记图例**：✅ 有活跃实装在跑（实查路径必附）｜🔨 已定调在建（有设计/施工令）｜⬜ 空白候选入口｜💰 花钱可解｜🌑 当前形态不可得（点名留档）｜【快】免费+公开+工程量小。
- **复核真源**：`config/strategy_production_map.yaml`（E0-E9 官方阶段轴，本骨架锚）+ `docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`（flow_stage）+ `sop/backtest_system_sop/`（A/B/C 卷）+ `docs/_working/bizmine_night/factor_sop_screen/factor_mining_sop_v0_1.md`（S0-S7）+ 代码实三层。差集全表见 `b1_source_diff_matrix.md`。
- **批次志**：B0 取锚 10 → B1 内部四源差集 +6=16 → B2 逐环节实查（本表回标）→ B3 外部方法学 → B4 三扫收口。增量曲线记在 b1 §4。

# §1 环节表（16 大类；「中类」列=B2 车道必须逐条穷尽的完整性检查单元；状态=B1 初判，B2 以实查改标）

| 环节 | 名 | 锚（E-xx/flow_stage/SOP 段） | 一句话职责 | B2 必查中类 | B1 初判 |
|---|---|---|---|---|---|
| AM-01 | 算力与作业调度闸 | E0 / `compute_window_gate.py` / MOD-BT-151 | 决定何时允许哪种计算（窗口/内存/DB 争用/排班避坑） | 窗口分类器·gate_decision 出口·资源画像注册表·reaper 联动·keep.txt 白名单·与 schedule.yaml 的正源关系·失败重跑语义 | 🔨（map 标 partial） |
| AM-02 | 原料供给与数据可得 | FF-01 / `data_source_onboarding_sop` §1-§10 / G5 G6 G10 | 挖矿的一切输入是否真的可用（可得≠可用） | 复权链（adj_factor≡1 全局债）·PIT 口径与 T-1 落桶·质量画像（缺失率/断更/重复）·known_data_gaps 触发器·tick/分钟/日线/E 盘冷归档家底·universe 与流动性门槛·字段→system.columns 实查 | ⬜+💰（复权归整改队） |
| AM-03 | 假设来源与立项 | E1 进货+E2 假说预审 / S0 矿脉选择+S1 假设登记 / G1 / research_incubation | 从哪来、如何登记、怎么判是否值得立项 | 六类来源（文献/主观手法/另类数据/图形/tick 微观/币圈）·hypothesis_registry·预审逻辑门（重复/不可证伪/功效不足拦截）·LLM 生成假设（LSG 闸）·终局缺口优先选题·负结果不重复立卡 | ⬜（G1 无册）+🔨（lane_b/c/g 实装在） |
| AM-04 | 构造与实现 | E3 构造 / C3 翻译适配 / model_training | 把假设变成可算的序列（含公式挖掘） | 手写因子·TI 宽表 163 列·图形引擎（unified_pattern_engine+candlestick_scanner，11 工单在案）·分钟/tick 构造·公式挖掘（gplearn/MCTS/LLM evolution）·**8 件孤儿实装归口**·克隆无逃生（CLONEGUARD）·前视/单位/时区三雷 | 🔨+⬜ |
| AM-05 | 初筛与宽测（筛≠考） | C2 粗筛+C4 快筛 / S2 IC 大海选 / G8 负结果台账 | 便宜地淘汰，且淘汰本身入账 | IC/IC_IR/分桶条件 IC·事件研究·BH-FDR 位置·宽测资源与时窗·**负/零结果全局台账（查无）**·RED 名单可检索性·筛→待考池升池规则 | 🔨+⬜（G8 无册） |
| AM-06 | 正交化与去重 | E5 协同去重 / variant_of≥0.85 马甲闸 / G7 | 防同一 alpha 被计多次（MID 报 \|ρ\|0.947 无后续即此缺） | 相关性去重件·N_eff 计数·家族归并规则·跨车道去马甲·正交化后 IC 复算·与筛/考之间的插入位置 | 🔨（实装有、链路未钉） |
| AM-07 | 预注册与考试尺子 | REG-BTB-001 / S3 预注册卡 / G4 G6 | 跑数前把口径钉死，并让机器能查你有没有钉 | 卡模板与必填字段·**机器可读卡+校验器（查无）**·frozen 时序证据链（mtime）·桶边界冻结·成本双口径命名（G6）·PIT 锚声明·改卡=日期附录·多重检验预算声明 | ⬜（最高优先缺件之一） |
| AM-08 | 沙箱窄考与过拟合防御 | S4 沙箱三关 / G3 / REG-VALM-001 | 唯一可判 PASS 的统计关 | NW t·bootstrap（聚类口径）·DSR/PBO/CSCV·`c4_deflated_sharpe_runner.py`·**窄考执行器（查无，协议只在 docs）**·严格档与常规档并报·功效门（120 日/桶） | ⬜+🔨 |
| AM-09 | E4 正考（IS→WFA→OOS） | E4 考试咽喉 / `f06_e4_wfa_exam.py` MOD-BT-211 | 全流程咽喉，产 verdict 入册 | 输入契约（intake/卡/宇宙）·输出契约（`data/backtest_artifacts/runs/E4-*`）·verdict 语义（不可跳级）·与窄考/正考门槛一致性·谁消费 verdict·自动化触发（现手工 CLI） | ✅（在跑、E4-* 在册） |
| AM-10 | 灰度状态条件化 | R 车道主轴 / regime 域 / G4 | 先算市场状态再按状态选因子与参数 | 灰度真源选型（vol_pct T-1 vs alt_regime_signal 禁用）·桶边界冻结·条件 IC/条件化 uplift·断供三腿 #ARCH-344·切换器（sowner002 在飞，不 merge）·组合层条件化 vs 因子层条件化分工·状态×因子矩阵的存储件 | 🔨+⬜ |
| AM-11 | 组合装配与资金分配 | E8 / position_management / REG-PFM-001 / G2 G9 | 因子/策略变成账本 | 组队（三档名单）·相关性闸·sleeve 装配落库（E8 未闭环）·风险预算/max-DD 分配·换手与容量·MID 荒漠的组合层解法·弹药账（到 Sharpe 目标还差几条）·**因子→策略组装无册（G2）** | ⬜+🔨 |
| AM-12 | 转正与上产 | E6 入库+E7 模拟盘前哨 / S9 转级 / simulation_validation | candidate→sim→paper→live 的门与登记 | 晋升门（ABS-001/promotion_combo_gate/promotion_advisory）·Owner 门位（宪法 §5 high）·sim/paper 对账（forward_post/sim_*）·TDM 挂接义务·决策时间戳（E9 未闭环）·回写 lifecycle | 🔨（E7 登记滞后=pending 而实装在） |
| AM-13 | 监控·衰减·退役 | E6 后段 / L6 自评估 / D_FBL_* / 五态+resurrected | 在产 alpha 的死与复活由机器判 | decay_monitor（**孤儿件归口**）·factor_lifecycle_runner 五态·策略衰减认证 DS≥0.5∧decay<0.5·死亡快照与 failed_streak·复活双证闸·退役后注册表净删门（Owner）·哨兵与告警（通知面=前端 promotion 页） | ✅+⬜（孤儿未接） |
| AM-14 | 归因反馈与假设再生 | E9 实盘归因 / FF-12 reconciliation→FF-02 | 把结果变成下一轮假设（闭环，现断） | 组合级收益归因（WO-1 欠账）·归因→AM-03 回灌件（查无）·negative_archive 负样本档案·判据修订闭环（S8 自称零机器）·复盘→门槛再校准·与考试尺子的互锁 | ⬜（真遗漏） |
| AM-X1 | 实验账本·注册表·命名统一 | REG-EXP/REG-CAND/trial_ledger/REG-FCT | 全链的单一真源与可审计性 | N 账本（n_trial_ledger）·FDR 预算随试验数收紧·全局 N 账·**三套生命周期命名并存**（因子五态/策略八态/TDM confidence 三态）·考试别名簇（E4=backtest_validation=C4=certified…）·**能力卡零张**（RULE-CAPABILITY-LOOKUP 查不到本链）·ROOR 挂接 | ⬜+🔨 |
| AM-X2 | 自动化编排与无人值守 | 横切（终局全貌主战场） | 让全链在无人参与下自转（Owner 终局只做四类事） | **端到端挖矿编排器（查无）**·事件触发（pipeline_events，禁 cron 化 reconciler）·循环检查仪（连续两轮零问题）·红蓝验收仪（`red_blue_validator` 43 行空壳=虚假锚点）·数据债→自动重考触发（查无）·E7 自动前哨·批次产物晋升 promote·心跳/会话并发 | ⬜（本链最大自动化缺口） |

# §2 归口与状态纪律

1. 归口判据（骨架 SOP §3 三问）：生产者/来源系统变→拆；验证口径（频率/PIT 锚/量纲/成本口径）变→拆；只是标的/参数/标签变→不拆。8 件孤儿实装按此归 AM-04/05/06/13。
2. **✅ 必附实查路径**（表/文件:符号/命令/commit）；接口存在≠✅、存量存在≠✅（股东户数断供两月误标为前车之鉴）。E7「map 标 pending 而 sim_*.py 有测试」=现行状态盲区样本，B2 必须实测改标。
3. 改标留批次号与日期；骨架外新发现条目先回写本表再施工（§7 回写义务）。
4. 叶层不穷举品种；完整性检查停在中类层；中类是否穷尽由 B2 车道逐条六向台账证明。

# §3 三重扫描计划（B4 收口批用）

| 扫 | 视角 | 本链的跑法 |
|---|---|---|
| ① 按生产者 | 每个环节的实装归属逐家过 | factor/research/backtest/strategy_pipeline/pf_alloc/pf_core/regime/signal_ashare/autonomy_core/orchestrator/trading + scripts/backtest/lane_*、factory_grid_*、compute_window_gate、sim_*、f06_* |
| ② 按形态与资产类别 | 同一环节在日线/分钟/tick/另类/币圈/板块各形态是否都存在 | AM-04/05/07/08 四个环节做全矩阵抽查（哪一格缺卡缺件） |
| ③ 按消费者文献 | 机构与学术的链路段划分逐个核（S5 外部源，带 URL） | 差集回填 b1 §5，新增枝须过 §2 三问 |
