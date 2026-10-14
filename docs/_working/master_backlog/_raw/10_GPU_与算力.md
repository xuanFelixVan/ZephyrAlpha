---
ttl: task_bound
completes_when: 清单内问题全部施工完成、或 Owner 叫停、或清单整体被替代时
title: "GPU 与算力 — 原样底稿"
---

# GPU 与算力 — 原样底稿

> 机器从 `docs/_working/**` 抽取的「遗留 / 待办 / 未完成 / 待裁 / 缺口 / 风险」类段落。
> **逐字复制，未作任何改写、删减或归纳**（超长段落标注 [TRUNC]）。
> 用途：归档 `docs/_working` 前的零丢失兜底；正文文档只给核实后的结论，底稿给原文。


---

## 来源：`docs/_working/2026-09-30-four-chain-handover.md`

### L23 · §0 · 10-14 收口复核（14 天后的现状）

## §0 · 10-14 收口复核（14 天后的现状）

主树已从 `9938b2ed8b` 推进到 `c100cb43c3`，660 个未提交改动在途。三条关键复核：

| 09-30 时的状态 | 10-14 现状 | 判定 |
|---|---|---|
| gpu_core 锁在 worktree 未合入主树（299 行） | **`src/zephyr/backtest/gpu_core.py` 已入主树，68,568 字节（10-13 21:59），已 git 跟踪，9+ 处生产消费方** | ✅ **已解决且远超预期** |
| `c4_batch_due` 自 09-16 积压 2 条 attempts=0 | 旧 2 条**已清除**；但新增 3 条（10-01 85 件 / 10-08 2 件 / 10-12 4 件）attempts 仍=0 | ⚠️ **部分缓解，仍在积压** |
| `GRADUATED_PACKAGES` 恒空（裁定#305） | **仍恒空**（`daily_decision_orchestrator.py:125`） | ❌ **未变，整装回测仍结构性空转** |

### GPU 侧的重大进展（值得单独说）

`gpu_core.py` 已从 299 行膨胀到 68KB，且**不再是"写了没接线"**：

- 已 git 跟踪（`git ls-files` 命中）
- 生产消费方 9 处：`_c4_engine.py:192/649/719/779`、`factory_grid_executor.py:994/1001/2196/2541/3071`、
  `src/zephyr/backtest/__init__.py:60`
- 头注 `[CONSUMERS]` 明示三路：`_c4_engine`（P1 接线/L2-B）、`factory_grid_executor`（L2-C --engine 三态透传）、
  `l2_bench_probe`（L2 终验探针）
- **已进入 L2 阶段**：RawKernel 融合扫描 `fillability_gate_scan`（一 thread 一列、时间轴寄存器内推进，
  T 次小 kernel → 1 次）——**正面解决**了 09-30 那份基准里"hs300/zz500 反而慢 0.25-0.53x"的
  kernel-launch 税问题；MOD-BT-232 god 区收编、L2-E 双核归一
- 测试已从 `tests/backtest/` 迁到 `tests/research/backtest/`（parity + l2_gpu_landing）

→ **09-30 那份"小尺寸上 GPU 反而慢"的基准已经过时**，新架构专治此病。若还要引用加速比，
请以 `docs/_working/gpu_rewrite/` 下的 L2 新基准为准。

### 新增的一条故障（09-30 时不存在）

```
PIPE-20261011-084204-336356  kind=t0_condition_pack_due
attempts=4  poison=true
last_error: AttributeError: 'NoneType' object has no attribute 'close'
```
这条**已被标记为 poison（死信）**，不会再自动重试，需要人工介入。属新发现的遗留项。

---

### L409 · §7 · 剩余任务执行序（10-14 更新版）

## §7 · 剩余任务执行序（10-14 更新版）

| 序 | 动作 | 前置 | 工作量 | 解锁下游 |
|---|---|---|---|---|
| **R0** | 处理 poison 死信 `PIPE-20261011-084204-336356` | 无 | S | t0_condition_pack 链 |
| **R1** | drain 三条新 c4_batch_due（85+2+4 件） | 无 | 分钟级 | E4 考试链 |
| **R2** | 修车道 C 崩溃并重跑 | 无 | S-M | 候选侧供给 |
| **R3** | cost_qualified_list 落主区 | 无 | S | 池基、GPU 搜索 |
| **R4** | 批 D 新鲜窗重考 | R3 | M-L | 整装 v2 池基 |
| **R5** | 落地器 fail-closed 治本 | 无 | M | 产物落库安全 |
| **R6** | 双引擎成本口径对照表 | 无 | M | 成绩单可信度 |
| **R7** | BP-5 清泄漏报告 + 首次自动入库验证 | R1 | S-M | E5/E6 链路 |
| **R8** | BP-1/BP-4 接线 | R7 | M | 假说轨、车道 F |
| **R9** | 整装回测 v2 正式启动 | R3+R4+R6 | —— | 决策链出真结论 |
| **R10** | 裁定 torch CPU/CUDA 依赖口径 | 无 | 裁定 | 环境一致性 |

**关键判断**：R0/R1 是"解锁型"动作（低工作量、高杠杆），当前最优先。
R9 是终点，但在 R3/R4/R6 完成前启动只会重演空转。

---


---

## 来源：`docs/_working/archive/2026-09/design_memos/36_var_es_monitoring.md`

### L879 · §4.17 ReSGA 检索增强自分组自编码器尾部风险大模型（远期，2026-08-10 新增）

### §4.17 ReSGA 检索增强自分组自编码器尾部风险大模型（远期，2026-08-10 新增）

**方案**：[arXiv:2606.04576](https://arxiv.org/abs/2606.04576) Zhang, Zhu & Zhu 2026-06 "ReSGA: A Large Tail Risk Model for Learning Value-at-Risk and Expected Shortfall"（港大+厦门大学）：百万参数级检索增强自分组自编码器——编码器映射潜在表示，检索器按特征相似性分组，解码器组内联合预测 VaR/ES。实证：1926-2023 美股月度 + 153 公司特征，改进主要由数据复杂度而非模型复杂度驱动，展示组重要性可解释性与跨市场迁移能力。

**远期登记理由**：① 过度工程风险：百万参数级模型与 §2.3 算力约束冲突；② 轻量化提取价值：按特征相似性分组+组内联合估计可脱离大模型实现（k-NN/层次聚类替代深度检索器，<50 行无 GPU）；"数据复杂度比模型复杂度更重要"印证 §3.1 取 max 在特征充分时已足够；③ 与 §4.16 正交（横截面分组 vs 时序），远期可组合；④ 与 §3.1 的关系：当前单标的独立计算无分组共享，Phase 2 可按行业/因子暴露聚类分组共享样本池（panel data 思路）提高小样本稳定性；⑤ Phase 3+ 远期（需 GPU + 153 维特征库，与 §4.16 同批次）。


---

## 来源：`docs/_working/audit_all/LEDGER.md`

### L146 · 心跳 2026-09-24 01:52 CST（本轮收束）· 在干=depgraph 轴 4 条发现定档+01:38 自审更正 · 卡住=R3#2 让窗(他包 13 行在途)/0005 待 gpu 批收敛 · 下一步=gpu 批落 HEAD→requeue 0005；SOP 那批落→4 行标注；红蓝+终报按 R3#3 推进

## 心跳 2026-09-24 01:52 CST（本轮收束）· 在干=depgraph 轴 4 条发现定档+01:38 自审更正 · 卡住=R3#2 让窗(他包 13 行在途)/0005 待 gpu 批收敛 · 下一步=gpu 批落 HEAD→requeue 0005；SOP 那批落→4 行标注；红蓝+终报按 R3#3 推进
- 队列盘面（事实，非本包职责）：total 1027，pending 5 / processing 4 / done 870 / dead 151；head=`q-...st-sweep-tail-20260923-0053` 等待≈95min，drain 租约活跃（pid 16632，renewed 13s，state=drain-active），daemon online；同期 HEAD 三笔（00:38 st-gpu-final / 00:43 st-k4 / 01:02 integrity）皆直连侧落 → 直连与队列并存期，队列头件未随直连推进（k=4 池化 00:43 刚入 HEAD，疑与在跑批相关，交 st-commitsys 观测，本包不判）。
- align：现算硬=3（ruling #383/#387，等 R3#1 合并器修好后 0004 重投）；soft warn≈987 存量。本包工作树自有件：LEDGER/REPORT + battle_map 2 行修（claim 持有，TTL 已续）。
- 反查未做项（诚实登记）：`MOD-L02-001`×43 是否同为错挂（同 MOD-INF-037 判法需逐 ID 比注册表身份，本轮只坐实 MOD-INF-037 一条，余留待终报前补齐或按 ID 上报口径=待判）。


---

## 来源：`docs/_working/cmd_ledger/automation_plan_discussion.md`

### L111 · 六、Owner 桌上待办（自动化不碰）

## 六、Owner 桌上待办（自动化不碰）

prereg v2 签字+factors 白名单审定（M2 席签约后才能实跑）｜凭据 R4 轮换裁决｜压测 PhaseB hold 区处置｜GPU 三案（Owner 自己的 GPU 对话内完成，09-25 12:00 点火）。


---

## 来源：`docs/_working/decision_map_campaign/07_pending_work_master_list.md`

### L6 · 07 · 全量待办总清单（Owner 09-24 午间原单 23 条 + 本对话新增，四类分栏）

# 07 · 全量待办总清单（Owner 09-24 午间原单 23 条 + 本对话新增，四类分栏）

> 状态基线：2026-09-24 22:00。原单 22 条已核销项不再列（见 Owner 原单存档）；本单=仍待办全量。

## A. 在飞自动消化（有属主，勿干预）

| 项 | 属主 | 状态/卡点 |
|---|---|---|
| GPU T1 3700 格跑批 → T2 900 自动晋级 | st-cmd（本班守望） | 跑批中，预计周六午前 T1 完 |
| 做T 3 批 46 件落地 | st-t0-matrix | 队列 pending；**甲位待 Owner 一句话**（auto_mount.py 写回准否） |
| W-M1 72h 双轨 | st-wm1-wave0 | Phase 0 PASS+双轨已启；六批在队；切主=周日到期后首工作窗 |
| cleanup ①②④⑥⑦ | st-cleanup-final | 在队/连锁（③ 等 ④ 落后自愈；⑤ 凭据已落 cb6b4bfc0e；⑧ 压测=空转死信实锤不追；⑨ 分钟K码面净，数据面归数据车道） |
| AI 层 245 件 | st-ailayer-final | 等"队列畅通"广播（判据=E2E 完成+pending<5）；监控自动化被删，广播=人工（本班守望） |
| audit-fix 收尾 | st-audit-fix | base_head 治本已落（c58da6cb06）但新闸失明待补；gate_registry 计数 174 vs 180 待生成器包 |
| 图书馆收官 | st-cmd（代） | #410① 三袋在队（q-0003-0005）+终态行（q-0008）；落齐即收官 |
| 方法论十册+#413 原子批+台账 R40-R43 | st-cmd | q-0013/0014/0015 在队 |

## B. 本班施工（st-cmd-20260924，GPU 跑批期间并行）

| 项 | 排期 |
|---|---|
| **P1 三张条件概率表** | 09-25 白天交付（04 号文） |
| T2 发车守望+完赛验收 | 周六 |
| 蒸发源追凶（四例 reset--hard+clean-fd，查 schtasks/守护进程日志执行源） | 09-25 |
| AI 层广播（判据达即发） | 队列 pending<5 时 |
| 队列消化监控（本班 9 件在队） | 持续 |
| 09 环节骨架总表（挖矿班在挖：D/S/G 册+TDM+battle_map 抽干） | 09-25 |
| **881xxx 行业指数补采**（Owner 09-25 深夜问询立卡：880 表只有 880 前缀 469 板块，881xxx 行业族 0 行——通达信全家桶 800+；sector_attribute_labels.yaml 08-22 已登记"TDX 可用时补采"待办；补采后 P1 表重跑覆盖行业族） | GPU 后首批数据施工 |

## B2. 先进件引入排期（机构对照"可直接引入"5 件——06 号文清单的派活版，GPU 后依次）

| 件 | 落点 | 排期建议 |
|---|---|---|
| PBO+缩水夏普消费面扩展 | GPU 考试验收链（e7_defense 已有 DSR 浮动门槛，补 PBO 与 CPCV 报告面） | 本轮成绩单出来即用（下周） |
| CPCV 组合净化交叉验证 | 考试卡体系（替代单一闭卷的多轮留出） | 退役重考预注册时一并立 |
| 分层贝叶斯收缩 | P1 三张表 v2（薄格子借邻居样本） | P1 v1 交付后 |
| contextual bandit 上岗引擎 | 条件共振选策略规则 v2（替代静态查表） | 静态表+上岗规则 v1 验证一个交易日循环后 |
| tick 盘口失衡执行信号 | 做T执行增强（tick L1 3s 在库） | 做T材料线样本达标后 |

## C. Owner 门位（一句话裁决清单）

| 项 | 等什么 |
|---|---|
| t0 "甲位"：auto_mount.py 写回准否 | 一句话（字节口径已钉死） |
| emoreplay 死会话两处方（推荐①：骨架维持在途+注释挂接随情绪线复职批） | 一句话 |
| 修宪挂图书馆入口（AGENTS.md 加一行） | 不急 |
| Tushare key 轮换 | 不急（其他 key 风险低） |
| 12 项 AI 层批文 | 已登记不阻塞 |
| 六段分叉 6 步修复（施工按真源对齐，无需重裁） | 施工批文即可 |
| 方案①升级案开工令（下一窗口，代码已列 03 号文 §三） | 窗口排期时 |

## D. 假期/日历（不挡 GPU，按原单 defer）

vhdx 压缩（需停 VM，假期禁做）｜feature_flags.jsonl 1.43G 轮转（停窗）｜266 件真改动 Owner 点名（月批）｜10-05 F 盘旧备份链摘除（526G）｜10-18/10-20/10-21 E/G 删｜数据源 4 空表｜因子策略 0/24（24 挂图策略因子集齐备数）｜产业链 12 硬｜实盘准入 live O-2~O-9（等模拟盘绿天数）｜C2 晋级率缺陷（2027-03 前）｜情绪指数全史补史（两融深史 G5，需新外部 API 通道）｜板块分钟K真值源验证（tqcenter 活体/东财 BK 备选）。

## E. 本对话新增且已闭合（存档防重复开工）


---

## 来源：`docs/_working/decision_map_campaign/08_watch_and_risks.md`

### L6 · 08 · 看守时点表 + 风险登记 + 巡检规程

# 08 · 看守时点表 + 风险登记 + 巡检规程

## 一、时点表

| 时点 | 事项 |
|---|---|
| 09-24 22:00 | GPU T1 已发车（grid_20260924-213246） |
| 09-25 白天 | P1 三张概率表交付；蒸发追凶报告 |
| 09-25 全天 | 队列消化（本班 9 件+他班在队）；pending<5 且 E2E 完成 → AI 层广播 |
| 周六 08:00-14:00 | T1 预计完赛 → 验收（manifest=3700/negatives/net_returns/dead=0）→ T2 900 格发车 |
| 周六 14:00/18:00 | c4_exam/model_exam 例行跑（与 GPU 完赛天然错开；若 GPU 拖过 14:00，按 #413③ 改签周一 08:00） |
| 周日 09:00 | 59h 窗收 → GPU 战役总成绩单（cost_adjusted_sharpe+negatives 台账+DSR） |
| 下周 | 方案①升级案/T2 后主效应分析/退役重考预注册/72h 双轨切主评估 |

## 二、风险登记（在册在办）

| 风险 | 状态 | 对策 |
|---|---|---|
| **主区蒸发连环（四例）**：untracked+index reset--hard+clean-fd 特征，机制未定位 | 🔴 追凶在办（09-25 报告） | 对策已制度化：交付即落 HEAD（本包/台账全走队列）；t0 班另见 index 9 条暂存删除待查执行源 |
| 队列瓶颈：pending 30+，吞吐 12-14/h | 🟡 常态 | k=4 池化在跑；AI 层广播以 pending<5 为判据即为此设 |
| f18d34c8（18:00 收班巡检自动化）状态矛盾（completed/runCount=31 但 nextRunAt 指向当日） | 🟡 | 不重建防双发；本班兜底亲跑 |
| t0 5 封死信（TABLE-NAME-REGISTRY+NO-BARE-SQL 内容可修型） | 🟢 包活自修（§3.4 不代修） | 观察 |
| 跨班收官互清（图书馆班两度被清理） | 🟡 文化性 | 停手公共面不对抗；交付即落 HEAD |
| 共享 index 战场（620 件 staged，含外来 BLUEPRINT 违规件） | 🟡 | 直连提交会被连坐——**一律走队列**（快照语义免疫） |
| GPU 单卡互斥（exclusive_group=gpu_default vs 本地 LLM 21.6GB 硬顶） | 🟡 | 跑批期间禁起本地大模型 |

## 三、巡检操作规程（每轮 10 分钟）

1. `python scripts/commit_queue.py status`（pending/processing/done/dead 四数+心跳）；
2. `tail .runtime/logs/grid_t1_20260924.log`（进度/异常）+ `tasklist | grep python`（进程存活）；
3. `nvidia-smi`（显存≤18GB 配额/温度）；
4. 产物目录增长抽查（data/strategy_intake/grid_*/）；
5. 死信箱（.runtime/commit_queue/dead/）新增验尸；
6. 本包状态仪表盘（README）核对更新——变更走 CAS。

## 四、继任指引

继任会话：读本 README → 02 号文（防重裁）→ 07 号文（待办全量）→ 本文件（看守）。指挥台账=cmd_ledger/overnight_decisions_20260924.md（R39 起）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/19_gpu_plan_and_master_backlog.md`

### L6 · 19 · GPU 提速三档方案 + 全量剩余工作总清单

# 19 · GPU 提速三档方案 + 全量剩余工作总清单

> 背景：实测 T1 为 CPU 引擎（pandas 表运算），GPU 仅当内存仓（1.8GB/利用率 1-7%）；单格 35.33s 中 83% 花在五档成本扫描（纯 CPU）；引擎一格一算串行设计天然只吃 ~10 核（全机 20）。**GPU 满载=把计算核心搬上 GPU 重写，是排期工程非开关。**

## 一、GPU 提速三档（+分片）

| 档 | 做法 | 收益 | 代价 | 状态 |
|---|---|---|---|---|
| ① 两轮制 | T1 轻档成本粗筛→幸存者全套终审 | 等效 2 倍（4,640→9,600） | 零新工程（代码已建），红蓝达标即切 | **红蓝标定已发车**（T0 200 格轻/全对拍；达标线 Spearman≥0.99+top50 重合≥90%）；达标→T1 切两轮制重启+prereg 重签（#413 附属裁定） |
| ② 热点向量化 | 五档成本扫描循环→向量运算（83% 热点） | 3-5 倍 | 1-2 天工程 | **下窗口立项施工**（本轮成绩单出来后与①叠加） |
| ②' 分片并行 | 3,700 格切两半双进程各算一半 | CPU 吞吐 ~2 倍 | 半天（分片装配+合并对账+内存防挤） | 下窗口与②同批 |
| ③ 真 GPU 满载 | 回测核心 GPU 重写（CuDF/全 tensor 化） | 10 倍+ | 大工程立项 | **等本轮成绩单产出密度再定**——避免为饱和而饱和 |

本轮节奏：T1 保稳定跑完（排名已有效，窗口有 ~10h 余量）→ 红蓝达标切①重启（完赛周六深夜→周六下午）→ 成绩单出 → ②+②' 下窗口 → ③ 视产出密度立项。

## 二、全量剩余工作总清单

### A. 本轮自动推进（在跑，勿干预）

| # | 项 | 预计 |
|---|---|---|
| A1 | GPU T1 3,700 格→T2 900 格（守望器自动交接+验收） | T1 09-26 深夜→T2 09-27 早 |
| A2 | 做T多周期引擎（1/5/15/30/60min×全市场×状态匹配；Decimal 修复后冒烟中） | 全量 ~23h CPU |
| A3 | 红蓝标定 → 达标切①两轮制重启 | 今晚 |
| A4 | 落地总执行班死信循环（9 批 78 件，已落 881/哨兵等 8+ commits，余 5 pending） | 今晚收网 |
| A5 | W-M1 72h 双轨 → 09-26 中午 24h 三判据评估 → 全绿提请 P-3 提前翻转 | 明天中午 |

### B. 明天（09-26）

| # | 项 | 前置 |
|---|---|---|
| B1 | AI 层广播（pending<5）→ 245 件落地+pytest+红蓝 | 队列收网 |
| B2 | GPU 成绩单解读包：垃圾判据六线+IBT-D01 口径对照表（先于解读存在） | T2 完赛 |
| B3 | ②向量化+②'分片并行 立项开工 | 红蓝结论 |
| B4 | 蒸发治本 EV-02~06（EV-01 黑匣子已上线） | 已批 |
| B5 | 清道三袋：ARCH-RULES-CLEAN-410 议题注册+带 [ARCH-APPROVAL] 标记重投 | — |
| B6 | t0 甲位解封（三版本分叉确认→写回 auto_mount.py）→ 0033 批 20 件（含六段全史） | 版本确认 |

### C. 本周内（09-26~28）

| # | 项 | 来源 |
|---|---|---|
| C1 | 方案① prereg 重签（两轮制字段，#413 附属） | 红蓝达标 |
| C2 | 六段剩余步：历史重算（占位口径结论标注+重算）+锚定表语义裁定呈报 | 切源已落 |
| C3 | 上岗规则 v1 Owner 追认→state_matrix 六空格填报（原料=GPU 成绩单） | L06-C01 稿已备 |
| C4 | 仲裁序 v1 Owner 追认（保守者胜并集原则） | L08-C01 稿已备 |
| C5 | L08-C02 真实 HALT 全流程首演（手册 §7 已备，Owner 前置确认） | rebuild 已接 |
| C6 | L06-C03 成绩单↔整装口径对照表落地 | IBT-D01 |
| C7 | DU-07 consensus 补采立项执行（已批补） | 12 号文 |
| C8 | L08-C03 MOD-RK-049 三选一（接线/收编/退役）→ Owner | SKEL L08 |
| C9 | emoreplay 复职批验收（q 批落地后 10 测+悬空引用复查） | L02-C01 |
| C10 | ②②' 施工+红蓝（向量化后对拍原引擎逐位语义） | B3 |

### D. 下周（GPU 后首批，09-29~）

| # | 项 | 来源 |
|---|---|---|
| D1 | 881xxx 下游三件：sector_state 881 维重放 / sector_constituent 8803/8804 补挂 / P1 v3 重跑出对比报告 | DU-01/02 |
| D2 | 退役策略重考：预注册（CPCV 框架）→ 在册 139 candidate 先考 → 聚宽 322 按族分批 | 三纪律 |
| D3 | DU 补采批：DU-03 两融深史（G5 新外部通道）/DU-04 tick 过渡/DU-05 pdf 五年真空/DU-11 daily_valuation 病根/kline_cb 宇宙/news_sentiment_score 停摆/kline_futures+hk 断链/crypto 缩水 | 12 号文 |
| D4 | 情绪成分真值窗累积监控（全成分真值仅 16 日→120 日门槛） | D28 |
| D5 | IBT 高优：D01 口径统一施工 / F01 批 D 新鲜窗收口 / H02 落地器快照对账 fail-closed | 11 号文 |
| D6 | TRD 高优：A10 桥两缺陷修复（隔夜单+竞态）/A02 周末校准错日/A06+15 告警消费+准入计数器 | 13 号文 |
| D7 | CNS：01 指标→因子接线首批 20/04 宏观族总裁决/05 基本面 10 零客表四态/08+09 alpha_sources 机械回填 | 14 号文 |
| D8 | L04：候选池三来源接线（selection_funnel→negative_veto→aggregator，register_pool_bundle_source 已备） | L04-C02 |
| D9 | L09：BT-P1-031 编排器收拢裁定（蓝图版 vs 双轨转正）/C03 日刊双账合流 | L09 |
| D10 | L01：C06 alt_regime_signal 消费端接线 / C03 行数口径治理+双写去重 | L01 |
| D11 | 蒸发治本验收：连续 7 天零新案+黑匣子定位演练复盘 | 17 号文 §九 |

### E. 先进件排期（06 号文 B2 栏+18 号文对表）

| 件 | 落点 | 时机 |
|---|---|---|
| PBO+缩水夏普消费面 | GPU 成绩单验收链（DSR 已有） | 成绩单出来即用 |
| CPCV | 退役重考预注册 | D2 时 |
| 分层贝叶斯收缩 | P1 v3 薄格子 | P1 v2 验收后 |
| contextual bandit | 上岗规则 v2 | v1 跑通一个日循环后 |
| tick 盘口失衡信号 | 做T执行增强 | 材料线样本达标后 |

### F. Owner 门位（一句话清单，按急缓）

| # | 项 | 时机 |
|---|---|---|
| F1 | 密钥轮换执行（tushare.pro 重置→我接 secrets 更新+旧 key 失效验证） | 本周 |
| F2 | W-M1 翻转确认（明天中午三判据全绿后提请） | 明天 |
| F3 | 上岗规则 v1 + 仲裁序 v1 追认 | 稿件+成绩单齐 |
| F4 | L08-C03 三选一 / G9 板块升格边界 / 六段锚定表语义 | 各自前置齐 |
| F5 | GPU ③ 立项决策（等产出密度数据） | 成绩单后 |
| F6 | 修宪挂图书馆入口 / 12 项 AI 层批文 | 有空 |

### G. 假期/日历（defer 不变）

vhdx 压缩（停 VM）｜feature_flags.jsonl 轮转（停窗）｜266 件真改动点名（月批）｜10-05 F 盘摘除 526G｜10-18/20/21 E/G 删｜数据源 4 空表｜因子 0/24 齐备｜产业链 12 硬｜实盘准入 live O-2~O-9（等模拟盘绿天数+计数器）｜C2 晋级率（2027-03 前）。

## 三、总账口径

- 施工项总池：IBT 31 + TRD 22 + DU 15 + CNS 14 + LK 16 + L01~L09 环节项 ~90 + 先进件 5 + GPU 三档 3 ≈ **196 项**；已闭合 ~40（本轮），在飞 ~12，其余按本清单排期。
- 每项验收判据=17 号文；专业标准=18 号文；防重裁=02 号文。

## 四、编目有排产无余项并入记录（C341，2026-10-07）

- **排产唯一真源** = `docs/_working/total_command_closeout/10_wave_plan.md`（八波排产册 W 册）：本册 §二 总清单凡已入波次表的项目，其排期/车道/出口判据一律以 W 册为准，本册不另立排期口径（内收原则，禁第二真源）。
- **无余项并入**：总清单中已闭合项不再逐项陈列，以本行代账——闭合凭证=W 册各波出口判据+对应批次 commit 链；后续新增闭合按同口径并入本节，不回改 §二 正文。
- **余项口径**：§二 计数（总池 ≈196/已闭合 ~40/在飞 ~12）保持登记面快照原样（历史审计面不回写）；实时余量以 W 册波次表勾销态为准。
- 本节只做"指向+并入记录"，§一 GPU 三档与 §二 清单正文零字节改动。

### L21 · 二、全量剩余工作总清单

## 二、全量剩余工作总清单

### A. 本轮自动推进（在跑，勿干预）

| # | 项 | 预计 |
|---|---|---|
| A1 | GPU T1 3,700 格→T2 900 格（守望器自动交接+验收） | T1 09-26 深夜→T2 09-27 早 |
| A2 | 做T多周期引擎（1/5/15/30/60min×全市场×状态匹配；Decimal 修复后冒烟中） | 全量 ~23h CPU |
| A3 | 红蓝标定 → 达标切①两轮制重启 | 今晚 |
| A4 | 落地总执行班死信循环（9 批 78 件，已落 881/哨兵等 8+ commits，余 5 pending） | 今晚收网 |
| A5 | W-M1 72h 双轨 → 09-26 中午 24h 三判据评估 → 全绿提请 P-3 提前翻转 | 明天中午 |

### B. 明天（09-26）

| # | 项 | 前置 |
|---|---|---|
| B1 | AI 层广播（pending<5）→ 245 件落地+pytest+红蓝 | 队列收网 |
| B2 | GPU 成绩单解读包：垃圾判据六线+IBT-D01 口径对照表（先于解读存在） | T2 完赛 |
| B3 | ②向量化+②'分片并行 立项开工 | 红蓝结论 |
| B4 | 蒸发治本 EV-02~06（EV-01 黑匣子已上线） | 已批 |
| B5 | 清道三袋：ARCH-RULES-CLEAN-410 议题注册+带 [ARCH-APPROVAL] 标记重投 | — |
| B6 | t0 甲位解封（三版本分叉确认→写回 auto_mount.py）→ 0033 批 20 件（含六段全史） | 版本确认 |

### C. 本周内（09-26~28）

| # | 项 | 来源 |
|---|---|---|
| C1 | 方案① prereg 重签（两轮制字段，#413 附属） | 红蓝达标 |
| C2 | 六段剩余步：历史重算（占位口径结论标注+重算）+锚定表语义裁定呈报 | 切源已落 |
| C3 | 上岗规则 v1 Owner 追认→state_matrix 六空格填报（原料=GPU 成绩单） | L06-C01 稿已备 |
| C4 | 仲裁序 v1 Owner 追认（保守者胜并集原则） | L08-C01 稿已备 |
| C5 | L08-C02 真实 HALT 全流程首演（手册 §7 已备，Owner 前置确认） | rebuild 已接 |
| C6 | L06-C03 成绩单↔整装口径对照表落地 | IBT-D01 |
| C7 | DU-07 consensus 补采立项执行（已批补） | 12 号文 |
| C8 | L08-C03 MOD-RK-049 三选一（接线/收编/退役）→ Owner | SKEL L08 |
| C9 | emoreplay 复职批验收（q 批落地后 10 测+悬空引用复查） | L02-C01 |
| C10 | ②②' 施工+红蓝（向量化后对拍原引擎逐位语义） | B3 |

### D. 下周（GPU 后首批，09-29~）

| # | 项 | 来源 |
|---|---|---|
| D1 | 881xxx 下游三件：sector_state 881 维重放 / sector_constituent 8803/8804 补挂 / P1 v3 重跑出对比报告 | DU-01/02 |
| D2 | 退役策略重考：预注册（CPCV 框架）→ 在册 139 candidate 先考 → 聚宽 322 按族分批 | 三纪律 |
| D3 | DU 补采批：DU-03 两融深史（G5 新外部通道）/DU-04 tick 过渡/DU-05 pdf 五年真空/DU-11 daily_valuation 病根/kline_cb 宇宙/news_sentiment_score 停摆/kline_futures+hk 断链/crypto 缩水 | 12 号文 |
| D4 | 情绪成分真值窗累积监控（全成分真值仅 16 日→120 日门槛） | D28 |
| D5 | IBT 高优：D01 口径统一施工 / F01 批 D 新鲜窗收口 / H02 落地器快照对账 fail-closed | 11 号文 |
| D6 | TRD 高优：A10 桥两缺陷修复（隔夜单+竞态）/A02 周末校准错日/A06+15 告警消费+准入计数器 | 13 号文 |
| D7 | CNS：01 指标→因子接线首批 20/04 宏观族总裁决/05 基本面 10 零客表四态/08+09 alpha_sources 机械回填 | 14 号文 |
| D8 | L04：候选池三来源接线（selection_funnel→negative_veto→aggregator，register_pool_bundle_source 已备） | L04-C02 |
| D9 | L09：BT-P1-031 编排器收拢裁定（蓝图版 vs 双轨转正）/C03 日刊双账合流 | L09 |
| D10 | L01：C06 alt_regime_signal 消费端接线 / C03 行数口径治理+双写去重 | L01 |
| D11 | 蒸发治本验收：连续 7 天零新案+黑匣子定位演练复盘 | 17 号文 §九 |

### E. 先进件排期（06 号文 B2 栏+18 号文对表）

| 件 | 落点 | 时机 |
|---|---|---|
| PBO+缩水夏普消费面 | GPU 成绩单验收链（DSR 已有） | 成绩单出来即用 |
| CPCV | 退役重考预注册 | D2 时 |
| 分层贝叶斯收缩 | P1 v3 薄格子 | P1 v2 验收后 |
| contextual bandit | 上岗规则 v2 | v1 跑通一个日循环后 |
| tick 盘口失衡信号 | 做T执行增强 | 材料线样本达标后 |

### F. Owner 门位（一句话清单，按急缓）

| # | 项 | 时机 |
|---|---|---|
| F1 | 密钥轮换执行（tushare.pro 重置→我接 secrets 更新+旧 key 失效验证） | 本周 |
| F2 | W-M1 翻转确认（明天中午三判据全绿后提请） | 明天 |
| F3 | 上岗规则 v1 + 仲裁序 v1 追认 | 稿件+成绩单齐 |
| F4 | L08-C03 三选一 / G9 板块升格边界 / 六段锚定表语义 | 各自前置齐 |
| F5 | GPU ③ 立项决策（等产出密度数据） | 成绩单后 |
| F6 | 修宪挂图书馆入口 / 12 项 AI 层批文 | 有空 |

### G. 假期/日历（defer 不变）

vhdx 压缩（停 VM）｜feature_flags.jsonl 轮转（停窗）｜266 件真改动点名（月批）｜10-05 F 盘摘除 526G｜10-18/20/21 E/G 删｜数据源 4 空表｜因子 0/24 齐备｜产业链 12 硬｜实盘准入 live O-2~O-9（等模拟盘绿天数+计数器）｜C2 晋级率（2027-03 前）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/HANDOVER.md`

### L60 · GPU 战役收尾（本周末）

### GPU 战役收尾（本周末）
1. 红蓝标定达标线：Spearman≥0.99+top50 重合≥90%→达标即切两轮制（prereg 重签裁定触发）
2. T1→T2→成绩单→17 号文六线垃圾判据检查
3. 成绩单解读（考尺口径相对排名；口径对照 IBT-D01 先行）
4. L06-C01 上岗规则 v1 激活（填 state_matrix；前置=euphoria/distribution 无 r 态来源的结构性问题）
5. GPU 重写挖矿班交卷→呈 Owner 裁 L1/L2/L3 路线


---

## 来源：`docs/_working/e2e_integration/LEDGER.md`

### L74 · ⑦ 周五早 GPU 终验+可点火结论 —— 未开工

### ⑦ 周五早 GPU 终验+可点火结论 —— 未开工

### L114 · 心跳 07:5x（st-gpu-final）| 状态：干完（W6 两面机检+契约钉入队） | 下一步：等 q-0009 落地核对+16:45 日循环圈实证+批注响应

### 心跳 07:5x（st-gpu-final）| 状态：干完（W6 两面机检+契约钉入队） | 下一步：等 q-0009 落地核对+16:45 日循环圈实证+批注响应
- **⑤ W6 两面机检全绿**：TDM 面 run_checks=182 节点/0 fail/404 warn（较 precheck 450 降）；排班面 schedule_overview consistency=0 ERR/9 WARN（资源画像缺口类，非阻断）；策略生产图 validate PASS（nodes=16/edges=16）。两面硬判据零失败。
- **契约钉 4 件已入队** q-20260924-st-gpu-final-20260924-0009（tests 豁免 CREATE-GUARD，走队列正道避 pipeline-final 暂存面互斥），落地后核对。
- 监控自动化运行中（automation-f8db602f，每 30 分钟，下次 08:18）。

### L118 · 心跳 08:05（st-gpu-final）| 状态：在干（T0 标定 200 格后台跑，E0 门实测放行，预计 ~25 分钟）| 下一步：T0 完→实测 per_point_seconds 回填 prereg→解锁 T1/T2 预算；q-0009 契约钉 4 件排队中

### 心跳 08:05（st-gpu-final）| 状态：在干（T0 标定 200 格后台跑，E0 门实测放行，预计 ~25 分钟）| 下一步：T0 完→实测 per_point_seconds 回填 prereg→解锁 T1/T2 预算；q-0009 契约钉 4 件排队中
- T0 命令：factory_grid_executor --stage t0 --start 2019-01-04 --end 2025-09-09（闭卷窗实长口径；n 钳制 200；成本门全程在）。
- 防重入：T0 在跑期间（.runtime 日志 /tmp/t0_final.txt）后续心跳轮只读进度不重发。

### L121 · 心跳 09:5x（st-gpu-final）| 状态：在干（T0 ~130/200 格，节奏慢于 6.8s/格预算估——T0 存在意义即抓此数） | 下一步：T0 完→backfill_per_point.py 回填→T1/T2 规模按实测重排；q-0009 契约钉 4 件已落 HEAD（done）

### 心跳 09:5x（st-gpu-final）| 状态：在干（T0 ~130/200 格，节奏慢于 6.8s/格预算估——T0 存在意义即抓此数） | 下一步：T0 完→backfill_per_point.py 回填→T1/T2 规模按实测重排；q-0009 契约钉 4 件已落 HEAD（done）
- 注意：T0 每格点含五档成本门真跑（修门后第一次真实工作量测定），预算表的 6.8s 系 CPU 合成面板外推——实测值出来后 24,990 格总量、T1=17100/T2=13000 配比可能要按 budget 重排，回填时一并评估。

### L124 · 心跳 10:1x（st-gpu-final）| 状态：干完（T0 标定完成+实测回填） | 下一步：等总指挥裁 T1/T2 重排方案；16:45 日循环圈观察

### 心跳 10:1x（st-gpu-final）| 状态：干完（T0 标定完成+实测回填） | 下一步：等总指挥裁 T1/T2 重排方案；16:45 日循环圈观察
- **T0 标定完成（首个点火硬前置闭合）**：grid_20260924-080309，200/200 全活（backtest_dead=0/eval_dead=0/degraded=0），全闭卷窗 1,622 日，N_eff=12，成本门五档全程真跑（修门后首次真实工作量测定）。
- **实测 per_point=35.33s/格（回填 prereg 完成，fail-closed 解除）**——为预算估 6.8s 的 5.2 倍。
- **预算影响（裁定请求，呈总指挥）**：59h 窗×0.8 占空÷35.33s ≈ **4,640 格**有效容量（原计划 24,990 格的 18.6%）。T1=17,100/T2=13,000 配比不可执行。本包建议方案：①点火前先做 1 小时 profiling（定位 35s 构成：因子重算 vs 五档扫描 vs IO——若五档扫描占大头可对 T1 粗扫档用 0/40 两档近似、入围者才全五档，可省 ~60%）；②按 4,640 格重排：T0 已完 200 + T1≈2,900（9 达标胞×主轴分层）/T2≈1,500（主效应前 20% 展开+4440 复验）；③或压缩 T1 面板域（流动性 top-3000）降单点耗时。三案裁一即开工。
- 待清理：grid_20260924-080007/080047 两个被中止的残目录（我建的临时产物，本轮未删避免误伤 T0 正跑）。

### L135 · 心跳 10:2x（st-gpu-final）| 状态：干完（两档粗扫≈全五档的实证完成，方案①证据闭环） | 下一步：等批注裁三案；16:45 圈观察

### 心跳 10:2x（st-gpu-final）| 状态：干完（两档粗扫≈全五档的实证完成，方案①证据闭环） | 下一步：等批注裁三案；16:45 圈观察
- **实测证据（T0 真数据，非断言）**：200 格点上，按 sharpe 与"sharpe−换手惩罚"排秩，Spearman=0.9998~1.0000、top50 重合 50/50（惩罚强度跨 20 倍带稳定）。成本档排序对本族配方（FACT 低换手，均值 0.107）**不构成排名扰动**；E7 换手门 8x 线 0/200 触发。
- **结论**：方案①（T1 两档粗筛+T2 全五档终审）的统计前提成立，容量 ~9,600 格有实测背书。三案裁定材料齐备：①两档粗筛（9,600 格）②朴素重排（4,640 格）③压面板域（正交乘子）。
- 本轮无新批注、无"队列畅通"、无在跑任务。

### L150 · 心跳 11:25（st-gpu-final）| 状态：干完（落地耐久性抽检 8/10→两 FAIL 分诊→prereg 回填件 q-0011 在队） | 下一步：q-0011 落地核对；16:45 圈；等裁定批注

### 心跳 11:25（st-gpu-final）| 状态：干完（落地耐久性抽检 8/10→两 FAIL 分诊→prereg 回填件 q-0011 在队） | 下一步：q-0011 落地核对；16:45 圈；等裁定批注
- **落地耐久性抽检（k4 吞并模式红蓝复查）10 项**：8 PASS / 2 FAIL→分诊：①prereg per_point=35.33 系盘面回填未提交（非覆盖）→已入队 q-20260924-...-0011 落库；②schedule_gate_policy gpu:12=未跟踪活配置（HEAD 本无此文件，盘面生效中，维持"不入 git"判，非回归）。
- 结论：无他班覆盖我的件；耐久性零流失。


---

## 来源：`docs/_working/factory_flow/E0_算力调度.md`

### L15 · 机制清单（机制 17 台：built 15/pending 2；主干 1 台 partial；purpose_tag=重活夜里干×15+图有人守×2；图例=Owner 2026-10-03 终审冻结）

## 机制清单（机制 17 台：built 15/pending 2；主干 1 台 partial；purpose_tag=重活夜里干×15+图有人守×2；图例=Owner 2026-10-03 终审冻结）

| node_id | 名称 | module_ref | build_status | purpose_tag |
|---|---|---|---|---|
| FAC-E0（主干） | 算力调度心跳 | MOD-BT-151 | partial | — |
| node_id | 名称 | module_ref | build_status | purpose_tag |
|---|---|---|---|---|
| FAC-E0-M-001 | 算力调度闸门 | MOD-BT-151 | built | 重活夜里干 |
| FAC-E0-M-002 | 批次窗口预检（Batch Window Preflight） | MOD-BT-226 | pending | 重活夜里干 |
| FAC-E0-M-003 | GPU Core（回测 GPU 薄核） | MOD-BT-233 | pending | 重活夜里干 |
| FAC-E0-M-004 | 资源优化引擎——GPU 监控/进程池化/自愈 | MOD-RESOURCE_OPTIMIZATION_ENGINE | built | 重活夜里干 |
| FAC-E0-M-005 | 系统大脑三层运行时——节律调度与工厂夜批同机竞争算力 | MOD-INF-035 | built | 重活夜里干 |
| FAC-E0-M-006 | 排班冲突检测闸（互斥组/内存天花板/E0 三查） | MOD-RESCHED-GATE | built | 重活夜里干 |
| FAC-E0-M-007 | 资源画像注册表+生成器（排班真源） | MOD-RESCHED-PROFILE | built | 重活夜里干 |
| FAC-E0-M-008 | 资源实测采样器 | MOD-RESCHED-SAMPLER | built | 重活夜里干 |
| FAC-E0-M-009 | 排班冲突告警桥 | MOD-RESCHED-ALERT | built | 重活夜里干 |
| FAC-E0-M-010 | 资源调度器 | dir:_domain_infrastructure_runtime/resource_scheduler | built | 重活夜里干 |
| FAC-E0-M-011 | NSSM+5 进程架构与 Supervisor（工厂夜批宿主） | MOD-INF-066 | built | 重活夜里干 |
| FAC-E0-M-012 | SLI/SLO+Token Budget——算力容量守护 | MOD-INF-001 | built | 重活夜里干 |
| FAC-E0-M-013 | GPU 上岗热交换模型（两档显存画像） | MOD-INF-069 | built | 重活夜里干 |
| FAC-E0-M-014 | GPU 资源管理 | dir:_domain_data_eng/gpu_resource_manager | built | 重活夜里干 |
| FAC-E0-M-015 | 交易日历（E0 闸门数据源） | code:src/zephyr/data/trading_calendar.py | built | 重活夜里干 |
| FAC-MAP-M-001 | 策略工厂图结构校验器（FACTORY-MAP 本图守卫） | MOD-BT-080 | built | 图有人守 |
| FAC-MAP-M-002 | 本图对抗测试件 | MOD-BT-081 | built | 图有人守 |

主干 algo_note 抄图：交易日白天只许轻任务，重算力（挖掘训练/批测/遗传优化）全排收盘后和休市日；trade_calendar 当闸门；事件触发禁定时器；已建=MOD-BT-151 拉式闸门（classify_window+gate_decision 四枚理由码，日历缺失 fail-closed，收盘缓冲 15:30）。


---

## 来源：`docs/_working/fullcirc_closeout_chief/90_execution_log.md`

### L39 · 10-06 深夜 Owner 令并行化：六路并发 T1 全收+两新缺陷类治本+T2 在飞

## 10-06 深夜 Owner 令并行化：六路并发 T1 全收+两新缺陷类治本+T2 在飞
- Owner 现场令"用 GPU+并发"。诊断：GPU 3% 系包围圈主导（pandas 因子面/合成/定尺寸+五档成本扫描，GPU 只加速内层回测环）+等形守卫挡回（CPU 点 100% 集中于 mkt_cap/kelly）。落两修：①mkt_cap_w 考窗基对齐（warm 基行并集变形，230≠120 行）②_sizing 消费口切列（mkt_cap_w/rets60 全 5055 列面 × cols 秩面=**列并集**变形=行修列没修的主犯，kelly 之谜同根因）——切列=额外列全 NaN 下游丢弃逐位恒等，净零漂移 GPU 资格恢复。vram.concurrency=1 本批偏离=Owner 令（VRAM 6×1.3G≪18G 配额，判据面零影响），判决书预算偏差位如实入。
- 并发战役弯路如实记：①& 后台孤儿化（壳回收，改受管 run_in_background）②秒级时间戳目录名撞车（6 分片同秒启动两进程互写同 out_dir=产物互覆污染→分片目录强制 _s{i}of{k} 后缀）③TaskStop 只杀壳不杀 python 子进程（三僵尸烧半小时，PowerShell 按 cmdline 精确点名后强杀）④六路同启装载共振挤爆内存杀一路（后改稳态补燃）。分片 0/2 残卷 ~4.5h 算力沉没=并行化代价，如实入账。
- **T1 收官：六分片并集 7400/7400 恰达冻帽，7399 活+1 死**（唯一死=18:2x 内存挤压窗 MemoryError，基建瞬态负例如实入册非考语义）。判决管线两修后出真数：net parquet 列名退化 0..n（concat(values()) 丢键="产物不自描述"读端债今踩响）→dict-concat 治本+六卷位序修复；**104 对配对、覆盖 2.8%、CRISIS MaxDD 改善均值 +3.48pp/中位 +4.47pp（<5pp 冻结门）→T1 干跑如实 FAIL**；冠军=off 腿 cost-adj Sharpe 1.81（DSR 0.984 显著）——J 帽护回撤但牺牲收益画像清晰，T2 补对后终判。
- 心跳守护教训：17:59 起的守护进程被本会话当僵尸误杀（1s CPU 小进程≠僵尸）→SESSION-REQUIRED 复发三连；立"register+enqueue 同命令"模式续命。


---

## 来源：`docs/_working/fullcirc_closeout_chief/99_delivery.md`

### L49 · 六、T3b-T0 标定出数（20261007 开工令，呈批件=卡 v2 草案）

## 六、T3b-T0 标定出数（20261007 开工令，呈批件=卡 v2 草案）

- **实测 5.08s/点**（T0=grid_20261007-095504：200 采样/199 活/1 结构负例 insufficient_net（dd20 全关账=净值零方差），1015.4s）——挖矿文档 35.33s/格 恐惧值的 1/7：列切修复后 **GPU 199/200=99.5%**（Owner"用 GPU"令在 T3b 面完全兑现）+overlay 纯向量化。
- **卡 v2 草案要点**（Owner 批后落冻结文件再开 T1/T2，先冻卷后开考）：空间 phase=3（X_stop 3×X_breaker 2 展开，N_raw=4,354,560，J 双腿继承）；窗/种子沿 T3a（2020-2023/20260915）；预算结构沿 T3a（T0 200 已消耗/T1 7400/T2 1800）；wall clock：T1≈10.4h 单卷（贴 12h 帽线）→**建议 3 路并发分片 ≈3.5h 收卷**（沿 Owner 并行令）；判据=主干沿 17 号文+成本门全档，新增离场判据（stop/breaker 档 vs off 档同配对 cost-adj Sharpe 与 CRISIS MaxDD）=**新维度新判据须 Owner 批**（非挪旧门柱）；honesty 新增：overlay 收盘判定失真/cATR close-only 代理/breaker 五帽带≠live 机/X 无预热语义；序钉=J帽→stop→breaker。
- 接线施工袋：schema X 维（phase>=3 门控，存量零漂移）+evaluate_recipe 接线+`--context-json` 标定通道+unstack 标签错位真 bug 修复（trail20/linear/pyramid 三处同型，测试烧算力前钓出）——q-0031/0032。


---

## 来源：`docs/_working/fullconnect_campaign/a_data_foundation/16_f127_data_eng_engineering.md`

### L48 · 四、缺口清单

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 全族生产零消费（装饰）；9 件能力对业务链贡献=0 **〔09-29 退役标记已落（方向已裁），见刷新批注〕** | 施工：逐件判"接入 or 退役"，禁整包留置为潜在第二真源；接入须给红样（先测后接），退役走净零声明 | P1 |
| 2 | 冷储双实现：`cold_data_archive_manager.py` vs F08 `scripts/ch/archiver.py`，且本件自称另立 SQLite 归档索引 **〔09-29 successor 方向注记已落（=F08 链），净删待 Owner 门〕** | Owner 门位：收敛方向（保 F08 删本件 / 或本件取代 F08）涉及生产归档链路，属根宪法 §5 high 域；本卷只提交判据不代裁 | P1 |
| 3 | 头部 `[MATURITY] production`/`[CONSUMERS]` 与实盘相反的三处假声明在册 **〔包级退役标记已落，件级头注未更正〕** | 施工：随接入或未接入实况更正头部；并评估把"头注自述 vs 实测消费者"做成一把 own-scope 尺（防同形复发） | P1 |
| 4 | M1 机采 symbol 尺产生 `ArchivePlan` 假阳性 | 施工：M1 采集器补同名消歧（须 import 面共证才计消费） | P2 |
| 5 | GPU 配额族与 G 段回测 GPU 线的归属边界未定 | 挂起：待 G 段卷交叉确认，避免两卷各记一次 | P2 |
| 6 | 告警出口（`data_anomaly_alerter.py`）与 F114 通知路由未接 | 施工：接入批的一部分，随缺 1 决策 | P2 |


---

## 来源：`docs/_working/fullconnect_campaign/l_methodology_routing/04_f119_dual_engine_automation_master_plan.md`

### L40 · 四、缺口清单

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 真源册 10-08 归档后的 F119 真源接任 | Owner 在收官总报批文中一并指定继任真源（随 §7 呈裁项走） | P1 |
| 2 | 总册 F119 行缺 task_bound/继任括注 | 骨架侧下次修总册时补一行括注（热文件 CAS） | P2 |
| 3 | 总计划册与 SOP automation 族无互引 | automation_crew_policy 或总计划册一侧补互引行（单侧即可，净零） | P2 |
| 4 | 今日 23:00 GPU 收窗对账（W-M1 72h） | 归 L3/L0 车道本日夜执行，本卷只登记不代做 | P1（时效） |


---

## 来源：`docs/_working/fullscore_night/10_coordination/NIGHT_STATE.md`

### L42 · 五、待办（按序）

## 五、待办（按序）
1. 从袋快照恢复 GPU 五件/前端 8 件/工厂 16 件/密钥 2 件到工作区→直投。
2. 重写 test_c4_cost_model_tiers.py（合同：LegacyFlat 零漂移 vs HEAD 逐位/Calibrated 五档单调/Participation 冲击单调/resolve_from_env/fail-closed）→与成本批直投。
3. GPU L2 重建：矿图没了但 L2 战报在案（本文件 §六）+god 区 .worktrees/st-gpu-god-20260928 源件还在（只读）→按战报重做 A/B/C/D→直投。
4. fresh_pool_v2 再生成（从 recovery2 268KB 报告或 CH）→填 prereg 附录 A sha256→IBT v2 四窗发车（W_IS→W_OOS→sensitivity→W_HOLDOUT 单次）。
5. 测试隔离+CI（W2）：conftest 守护 fixture+三类写真仓测试收编+coverage 基线+CI yaml（上两班 600s 超时阵亡，重派时拆小步禁长阻塞调用）。
6. 循环检查→连续两次零→红蓝对抗→修复。
7. 收尾：临时文件清（_c4_engine.py.tmp.18376 在成本接线落地后删）+worktree 大扫除 dry-run 清单+终报。


---

## 来源：`docs/_working/gpu_rewrite/p1_wiring_benchmark.md`

### L68 · 五、余量与下一步（供 L2 决策，本批不做）

## 五、余量与下一步（供 L2 决策，本批不做）

1. GPU 侧最大税=串行闸循环（`_apply_gate_serial`，T 次小 kernel）——若 L2 将其
   GPU 融合或分段批处理，hs300/zz500 尺寸 GPU 有反超空间（普查 L2-a 判定仍成立：
   改动风险 vs 收益需另测）。
2. hoisted-cpu 剩余面=ffill/pct_change 之外的逐格张量（shift/mul/sum/abs）+掩码
   to_numpy 转换（SU/SD 逐格重复转换，约 1–3ms/格量级）。
3. 35.33s/格 旧世界基线的治本主力=已落地的掩码去重（74–95%）+本批 L1（残余 2x）
   ——全批次墙钟收益以 T1 重跑实测为准（本件 task_bound 不含批级跑批）。


---

## 来源：`docs/_working/gpufeed_campaign/01_gpux_t0_profile.md`

### L199 · 六、在册矛盾与缺陷登记（不自决，逐条给凭据）

## 六、在册矛盾与缺陷登记（不自决，逐条给凭据）

| # | 类型 | 事实 | 处置 |
|---|---|---|---|
| D-A | **在册政策自相矛盾** | `new_asset_gpu_cpu_checklist.md §二.2`（Owner 令 2026-09-28）"FP64 红线绝对，禁 float32/TF32/FP16" vs `verification_framework.md §一·补`"GPU 重写必须走 FP32＋容差，FP64 仅争议格仲裁" | 本班按 FP64 施工（§三 实测支持），矛盾**不自裁**，提请两件的属主车道对齐或走裁定通道 |
| D-B | 文档↔代码漂移 | `p1_wiring_benchmark.md §四` 写 `_GPU_AUTO_MIN_CELLS=8e6`，代码=500_000（`_c4_engine.py:532`），且 `test_l2_gpu_landing.py` 的 INVARIANTS 已钉 5e5 | 代码与试件一致、战役文档陈旧——只登记，不改他人文档 |
| D-C | 悬空引用三处（同一件 `gpu_core.py`） | `[TESTS]` 指 `tests/backtest/test_gpu_core_parity.py`（真身=`tests/research/backtest/`）；`[CONSUMERS]` 指 `scripts/backtest/l2_bench_probe.py`（`git ls-files` 零命中=不存在）；docstring 验收出处指 `docs/_working/fullscore_night/06_gpu_compute/`（该子目录不存在，其父目录只有 02/03/10） | **定性已修正**（原写"盲区待查"，查出在案出处后改判）：后两处是 `c4c7960bb8d`（st-fullscore-20260930）commit message 明写的 defer 项——"l2_bench_probe.py+04_L2_landing_benchmark.md+deferred_claims.md 随 capability 册批跟车（staging 暂存，册被 datasop/w3h 在途）"，即**已知待跟车件未随册落地**，非无人知晓；`[TESTS]` 的目录名错则是本件自身笔误。本班只登记不改他人头部 |
| D-D | 资源互让面空转 | `config/search_space_prereg.yaml:106 vram.concurrency: 1`（注"单卡禁共存，与本地 LLM 21.6GB 硬顶互斥：exclusive_group=gpu_default"）而 `config/resource_profile_registry.yaml:1039-1046 manual_factory_grid_executor` 的 `exclusive_group: []`；今晚实跑 6 路并发＝靠临时看门狗让路（`yield_watchdog.py`，已随分片退役） | **处置已改判**（总统统筹 2026-10-11 05:3x 裁定③直接授权册面改：并发数按 NVML 实测入册＋executor 挂 exclusive_group，禁"册上写 1 实际跑 6"的漂移态继续）：本班已随袋把 vram 块补 `per_path_budget_mib: 2100`/`concurrency: 6`/`concurrency_basis`，executor 挂 `exclusive_group: [gpu_default]`，并在 `factory_grid_executor._dev_xp` 把预算变成**真准入闸**（只改 yaml 不接消费方＝又一个空转面） |
| D-E | 预存红 6 支（非本班） | `tests/research/backtest/test_l2_gpu_landing.py::test_executor_*` 6 支红，根因=`7961b3ec880`（2026-10-06）给执行器加了 `_load_mkt_cap_wide(...).reindex(...)` 而该试件的桩返回 None | 双证为预存：在**纯净 dev 字节**复跑同 6 支同样红（09 时点记录见本班终报），且本班两支改动对 dev 均纯新增。归执行器属主车道，不代修。6 支点名（06:0x 复跑逐支实录，便于按名对账）：`test_executor_engine_passthrough[cpu-cpu]`／`[gpu-gpu]`／`[auto-None]`、`test_executor_manifest_backend_degrade_columns`、`test_executor_gpu_wave_failclosed_rerun`、`test_executor_cpu_wave_negative_semantics` |
| D-F | **本班自犯缺陷（资源足迹顶零 RAM，判据面被污染）** | 05:36 六路×25,000 格上卡实测：s1/s2/s3/s5 四路跑完 4,167 格各负 8–12 支，其中 **22 支是 `eval/eval_fail:MemoryError`**（detail 实写 "Unable to allocate 37.4 MiB for an array with shape (970,5058) and data type float64" 等），s0/s4 两路更在 1,768/1,794 格处整波 MemoryError→按既定 fail-closed 整波重跑 CPU；同参纯 CPU 基线 p2（`grid_20261010-233721_s*of6`，25,000 格）eval 层阴性 **0 支**，其 39 支阴性全为 `backtest/backtest_fail:RuntimeError`（净值不足的真判决）。主机侧读数：单路 heartbeat.rss_mb 峰值 4,316–4,424MiB，六路合计≈26.4GB，05:52 实测 GlobalMemoryStatusEx 可用仅 23.7GB（总 63.9GB，另有夜矿/LLM/桌面在飞） | 定性=**算力面缺陷变成判决**（与本班 §〇.7 的 `bool(codes)` 案同族，只是抛点换到了未保护的 CPU 段）。两条腿都已补：①`_dev_xp` 准入闸加**主机腿**（册 `budget_caps.host_mem.per_path_peak_mib: 4600`，可用 RAM 不足即本路不上卡并计 `host_mem_refused`；水位读不到只计 `host_mem_unmeasured` 不拦路；读数口=在册唯一 `host_resource_governor.probe_system_watermark`，禁自造 ctypes/psutil 第二份探测）；②eval 调用外套 `_eval_cell_mem_retry`=首次 MemoryError 先卸设备面板缓存+置本批停卡旗+计 `memory_pressure`，**重试一次**，二次仍败照旧上抛既有记账口（真耗尽不禁静默）。配试件 2 支（`test_host_mem_admission_gate_refuses_and_agrees_with_registry` 四面钉＋`test_eval_memory_pressure_degrades_to_cpu_not_cell_death` 三面钉）。**残余不自掩**：只有 05:36 那一轮的 22 支已被记成阴性，历史产物不回填（only-add），改后需下一轮配对复跑证实 eval 阴性回落到基线同形（0 支）才算闭环 |
| D-G | **本班自犯计量盲区**（零计数被读成"跑过但没上卡"） | 06:32 一轮 `--eval-backend gpu` 的产物里 `summary.eval_gpu` 十项全零、`engine_degrade` 缺席，看着像"整批走 CPU 是准入闸决定的"；实为该子进程 **PYTHONPATH 未指车道 ⇒ `zephyr` 解析到主区旧字节**（在册同类教训：worktree 裸 python 导主区包=假绿），`from zephyr.backtest.gpu_core import nvml_device_memory` 抛 ImportError 被 `_dev_xp` 末尾宽 `except` 吞成降级，**只在 stderr 留一行**（`l3_gpu.log` 里 1,050 行同款）。发现路径=**旁证异常**（"GPU"侧 eval_s 0.445 与 CPU 侧 0.452 逐位同速），不是计量面 | 已随袋补：`_dev_xp` 两条静默出口各加计数器（`resolve_not_gpu` / `dev_attempt_failed`）+ 试件 `test_device_attempt_failure_is_never_silent_in_counters`（四相钉，计数器漏加即红）；纪律面新增硬规则自约束=**跑前先在同命令行断言 `zephyr.__file__` 落在车道**（本班 driver 已加，且今后任何"配对"必须先证明两侧的 `eval_gpu.cell_gpu>0` 与 argv 一致才允许进容差判定）。该轮产物**降级为 CPU-vs-CPU 对照**使用（见 02 件 级 3 与 03 件 §八），不得当 GPU 证据 |

 05:36 六路×25,000 格上卡实测：s1/s2/s3/s5 四路跑完 4,167 格各负 8–12 支，其中 **22 支是 `eval/eval_fail:MemoryError`**（detail 实写 "Unable to allocate 37.4 MiB for an array with shape (970,5058) and data type float64" 等），s0/s4 两路更在 1,768/1,794 格处整波 MemoryError→按既定 fail-closed 整波重跑 CPU；同参纯 CPU 基线 p2（`grid_20261010-233721_s*of6`，25,000 格）eval 层阴性 **0 支**，其 39 支阴性全为 `backtest/backtest_fail:RuntimeError`（净值不足的真判决）。主机侧读数：单路 heartbeat.rss_mb 峰值 4,316–4,424MiB，六路合计≈26.4GB，05:52 实测 GlobalMemoryStatusEx 可用仅 23.7GB（总 63.9GB，另有夜矿/LLM/桌面在飞） | 定性=**算力面缺陷变成判决**（与本班 §〇.7 的 `bool(codes)` 案同族，只是抛点换到了未保护的 CPU 段）。两条腿都已补：①`_dev_xp` 准入闸加**主机腿**（册 `budget_caps.host_mem.per_path_peak_mib: 4600`，可用 RAM 不足即本路不上卡并计 `host_mem_refused`；水位读不到只计 `host_mem_unmeasured` 不拦路；读数口=在册唯一 `host_resource_governor.probe_system_watermark`，禁自造 ctypes/psutil 第二份探测）；②eval 调用外套 `_eval_cell_mem_retry`=首次 MemoryError 先卸设备面板缓存+置本批停卡旗+计 `memory_pressure`，**重试一次**，二次仍败照旧上抛既有记账口（真耗尽不禁静默）。配试件 2 支（`test_host_mem_admission_gate_refuses_and_agrees_with_registry` 四面钉＋`test_eval_memory_pressure_degrades_to_cpu_not_cell_death` 三面钉）。**残余不自掩**：只有 05:36 那一轮的 22 支已被记成阴性，历史产物不回填（only-add），改后需下一轮配对复跑证实 eval 阴性回落到基线同形（0 支）才算闭环 |


---

## 来源：`docs/_working/gpufeed_campaign/02_gpux_equivalence_ladder.md`

### L30 · 一、T4 施工面（三处，全部缺省关）

## 一、T4 施工面（三处，全部缺省关）

1. `src/zephyr/backtest/gpu_core.py`（MOD-BT-233 原位扩面，**+456/−0 纯新增**）
   * 新 eval 节：`normalize_rows`（raw/zscore/rank/industry_neutral/size_neutral）、`industsize_rows`、
     `_rank_rows`（升/降/pct 三形，平均档并列组走既有 scatter_add 机）、`_row_mean/_row_std`（ddof=1 skipna，
     复用既有 `_neumaier_nansum_axis1` 补偿和）、`_group_mean_rows`/`_demean_rows`、`_regress_out_rows`、
     `ic_pair_rows`、`weighted_combine`、`orth_equal_rows`、`norm_rows_div`、`sizing_weights`（七形态）、
     `periodic_hold_rows`、`cap_clip`、`eval_cell_gpu`。
   * 单码路径纪律：每个函数只写一份，`xp=numpy|cupy` 由后端决定（文件头 INVARIANTS 既有要求）。
   * 新 `nvml_process_util()`：逐进程 SM 归因（ctypes 直调 `nvml.dll`，零新依赖）——见 01 件 §四。
2. `scripts/backtest/factory_grid_executor.py`（+421/−52，删除面全部逐行对上账，见 §三）
   * 新 `--eval-backend cpu|gpu|auto`，**缺省 cpu=原路逐字节零漂移**；
   * 新 `_prefix_eval_gpu`（前缀面）与 `_cell_eval_gpu`（单格定尺寸链）＋ `_cell_device_able`（叠加族判否）；
   * 抽 `_ic_weight_frame`（从 `_combine` 原样搬出，CPU/GPU 两条前缀路共用——禁复制第二实现面）；
   * 抽 `_FREQ_STEPS`/`_LAMBDA_PEN` 为模块常量（原两处内联字典上提，内容逐字同）；
   * 心跳并记归因三键（NVML 不可用时整键不出）；`summary.json` 的 `eval_gpu` 键仅在后端非 cpu 时出现。
3. `tests/research/backtest/test_l2_gpu_landing.py`（+644/−0，就地追加 20 支试件函数
   （dev 12 支→本道 32 支；参数化展开后采集面 51 支用例，其中新增 37 支），不新建试件册）


---

## 来源：`docs/_working/gpufeed_campaign/03_gpux_final_report.md`

### L95 · 四、呈批与不自决项（三清单之三）

## 四、呈批与不自决项（三清单之三）

Owner 只需在下面几格里回话；本班一律不自裁：

| # | 事项 | 为什么需要您 | 不回话的后果 |
|---|---|---|---|
| ① | 验收未达标要不要**续投一晚**（N-1 批并行核是 1-2 天工程，非 tweaks） | 涉及排产优先级：今晚的结论是"方向对、家伙不对"，续投=再造一层 | GPU 化停在"等价但更慢"的半成品态；缺省关着不出错，但 24G 卡继续闲着 |
| ② | `max_drawdown` 相对线（1e-4）要不要补一条**绝对地板**并写明"top_n 敏感格另判" | 这是**判据面/容差线**，改它必须您或裁定通道点头，本班不碰 | 级 2 永远因 1/199 的近并列翻转不绿；有人可能为了"过线"去动卡（错的方向） |
| ③ | 执行器是否挂进 `exclusive_group=gpu_default`，或把 `vram.concurrency` 改成"允许多路"并写明预算 | 排班资源政策（6 路实测已在发生，但册上仍写 1，属纪律与现实的矛盾） | 并发跑批继续靠临时看门狗让路，在册口径与现实不符 |
| ④ | `#ARCH-TORCH-CPU-ONLY` 与本机实装 torch 2.13.0+cu126 的漂移要不要处理 | 架构裁定面；本班已按 CuPy 施工，未用 torch | 后人可能误以为 torch 可用而绕开在册载体 |

**05:3x 总统统筹转 Owner 四选裁后的处置态（追加，不改上面四问原文）**：

| # | 裁定 | 本班执行态与凭据 |
|---|---|---|
| ① | **「续」**：N-1 批并行核 + N-2 权重直供 bt + N-3 六分片×25,000 格双后端配对（日历窗问闸照办） | N-3 **已跑完并按 §七 判废其跨夜配对法**（吞吐终数在 §一 表，用同日同在窗 i<1700 控住并发：1.61–1.73x）；日历窗闸照走（`_ask_compute_window_gate`，未用 `--skip-compute-gate`）。N-1/N-2 **本班未动工**——见下方"下一棒入口"的量化设计，属 1–2 天工程，不在本袋半开一面 |
| ② | 地板已给：max_drawdown **相对 1e-4 或绝对 1e-5 任一即过**；另立"近并列翻转标组合等价、另判、不挂红线"，**禁为过线去动卡** | 已入真源 `verification_framework.md` §一·补 + §二 层2 同行（逐字可 diff），并新增 **§二·补** 四条处置规则（披露五元组必列/禁动卡/先容差后条款/边界格数须随 n 计数披露）；级 2 已按新线重判并保留裁定前原文（02 件 §二） |
| ③ | 册面改：vram.concurrency 按 NVML 实测显存定预算上限（逐路 ≤实测安全值、并发数入册），executor 挂 exclusive_group；**禁"册上写 1 实际跑 6"的漂移态继续** | 已落袋：`per_path_budget_mib: 2100` + `concurrency: 6` + `concurrency_basis`，executor `exclusive_group: [gpu_default]`；**并且把预算变成真闸**（`_dev_xp` 显存准入），因原 `vram:` 块零消费方＝改了也是空转。N-3 实测又暴露**只有显存腿不够**→ 同袋补主机腿（`budget_caps.host_mem.per_path_peak_mib: 4600`，实测 rss 4,316–4,424MiB/路 × 6 撞零 64GB 主机 RAM） |
| ④ | **转维护二班**（torch +cu126 vs 在册 +cpu 漂移＝架构裁定面，登记环境债） | 本班**不自裁**，按令登记移交：①事实=torch 2.13.0+cu126 已实装而 `#ARCH-TORCH-CPU-ONLY` 在册 +cpu；②本班一切 GPU 施工载体=CuPy 14.2.0（未 import torch）；③去向=维护二班（sid st-maint2-20261011，注册表内其在册条目 idle 2,662s 仍活）；④**在册无"在用"的环境债台账**（`docs/01_policies_and_standards/_registry/catalogs/` 下无 debt/env 类册；
  唯一同名物=`docs/_archive/architecture_debt_registry_v2.md` 已在归档区＝退役件，"环境债台账"四字只见于
  裁定#416 行文与其两处 `_working` 转述，未指真源路径）⇒ 本班不新建册（净零增长），登记处=本件 +
  `.runtime/handoffs/handoff_st-gpux-20261011.json`，并提请维护二班或裁定通道**先指定该台账的唯一真源**
  （否则"入台账"这句无落点，下一个班还会撞同一堵墙）；⑤禁把"本班没用 torch"读成"漂移已解决" |
| ⑤（**级 3 实测后新增，非 05:3x 四问之一**） | 册上 FP64 判据"net 序列逐日相对差 ≤1e-8"要不要**按实测噪声底重定** | 级 3 实测：同数据态**纯 CPU 对自身**就有 1,049 列零逐位等、17 列(1.62%)违反该线；设备面 26 列(2.48%)。这条线现在**先被引擎自己判红**，拿它当 GPU 等价性判据＝判据失灵（要么改成"设备差分 ≤ CPU 自对照底同量级"，要么调线并注明底=实测）。**属判据面，本班一字不改** | 级 3 的"全精度日线"面永远只能报"越线 N 格"而给不出 PASS/FAIL 语义；后人可能为过线去动归约序（正是裁定②禁的方向） |


**第二令（四格裁＋⑤，本班 2026-10-11 13:4x 前后收悉即行）与执行态（追加，随令逐条对账）**

> 时钟更正自白：前稿把本令标为 "07:2x"、把开工标为 "07:4x"，均为本班体感钟漂移所致的**臆写时刻**（在册教训：时间锚必须 date 实测）。实测锚点=本班 bag -0014 建于 07:16:35、落地后主区静默至 13:4x，`date` 实测 13:47:34 才投第二令的账袋；凡本件内文出现"07:2x/07:4x"者一律以本行的实测窗为准（袋 -0015 因心跳 daemon idle 自退被判 ghost_session 死信，亦发生在这段静默里）。：

| # | 令文（总统统筹，本班 13:4x 收悉） | 本班执行态与凭据 |
|---|---|---|
| ① | **续 N-1/N-2 批**：批并行核（**紧凑索引 23MB/路路线**）+ 权重直供 bt，**同批做**——通往 70%+3x 的唯一入口 | 本班 13:4x 起开工（同批=同一袋内落地，禁先做一件再等）；前置读数已备好：单进程稳态 tot 0.213s/格（CPU 0.520）、逐格成本随进程数上升（0.158→0.230s）⇒ 批内并行、少进程；稠密 (50,970,5217)×8B≈2.0GB/路 与 紧凑 (T,top_n) 索引对≈23MB/路 的算术在 §四 末表 |
| ② | **1e-8 按实测底改**：以"同日背靠背+成分指纹"协议的 CPU 自噪实测**重定线**（推导入册；**实现等价线非考试判据**） | 已入真源 `verification_framework.md` §二·丙（甲=聚合五项线硬闸不变；乙=1e-8/1e-6/1e-4 三档各做一次双侧两比例 z 检验，三档全 p≥0.05 才判等价，任一档 p<0.05 必须逐格归因）；旧 1e-8/1e-5 两值在 §一·补 与 §二 层2 同行**逐字保留但标注"降为披露位"**，授权通道与日期注明；推导（17→26 与 4→13 两组 z/p）随件入册，署名 adjudicator=st-gpux-20261011（本班代推导，非 Owner 亲笔数值） |
| ③ | 排班超限**Owner 已裁"调"，维护二班执行**；本班不动，互斥组行随排班下调后重试 | 本班遵令不动他人实体。`exclusive_group` 那一行仍留车道未提交（N-5 入口在册）；重试触发条件=维护二班把 2026-10-12 09:35/09:40 两档内存和调到 ≤ `mem_ceiling_gb=10.0` 并落地，之后本班（或下一班）随袋重投该一行 |
| ④ | 换手率**暂给相对 1e-6 线**，随②自噪重定一并终定 | 已入 §一·补 新行（标"暂给线"）+ §二 层2 对象清单同口径；**随令附一条本班实测的硬约束**：manifest 的 `avg_turnover` 列只存 4 位小数，1e-6 相对线**在 manifest 位不可判**（四舍五入自身就是 1e-4 台阶，1,049 格里就 1 格差 1e-4 纯属舍入）⇒ 该线必须在全精度位取数（同进程双后端 harness 比 `stats` 原值），本班**不自扩列宽**（那是判据列改动） |
| ⑤ | 环境债台账归维护二班定落点；**本班三条自纠（零计数器／同 seed≠同输入／空收 rc=0）验收入册**；torch 漂移已转维护二班 | 三条已入册：⑴零计数盲区=01 件 §六 **D-G** + 代码计数器 `resolve_not_gpu`/`dev_attempt_failed` + 试件 `test_device_attempt_failure_is_never_silent_in_counters`（已落 dda797cca9）；⑵同 seed≠同输入=03 件 **§七** 三路对照 + 新协议"背靠背+成分指纹 drift_free 才准进容差判定"（已入 §二·丙 乙 条前置）；⑶空收 rc=0=03 件 **§五 第 8 条**（pytest collected 0 items 而管道后 `$?` 量的是 tail）；环境债台账落点不自定，等维护二班；torch 漂移在 01 件 D-行与本件 §四 第一令 ④ 双处在册 |

**三问裁定（总统统筹 2026-10-11 13:5x，本班 `date` 实测；呈 on §四 第二令表 ⑤ 行与 §一 阶梯附注②）与执行态**：

| # | 裁定 | 本班落地处与凭据 |
|---|---|---|
| ① | **「扩，同条同款」**：调仓触发日翻转 13 格并入"组合等价、另判、不挂红线"（已证=1-ULP 离散选择的合法形态，与 top-N 近并列同族） | 落为 `verification_framework.md` **§二·补 第 5 条**（原第 1–4 条 Owner 措辞**一字未改**，只做追加）：定名 `tie_amplified_selection` 与 `near_tie_selection` 并列同款；披露口径对本类**由五元组增为七元组**（+触发载体与阈值档、+边界间隙/并列组规模）；**第 3 条判定顺序与第 2 条禁令一字未松**；并写死**边界自识**——机制证据不成立者（combined 面差 >1 ULP／aux 取值不同／单侧 NaN）属实现缺陷，**不在豁免内**，用尺=集合归因＋维度归因＋合成面板机制三步全过才允许定名 |
| ② | **维持现制**：换手率线永久规定"仅同进程双后端 harness 全精度位判"，**不加宽产物列**（不动判据面）；N-1 落地后如需列宽再呈 | 落为 §一·补 `avg_turnover_1side` 行（状态由"暂给线"改"**线值终定**"，线值 1e-6 不变），理由与实测据同格注明（manifest 4 位小数⇒舍入本身 1e-4 台阶，级 3 那 1 格差纯属舍入；把线挂在判不了它的面上＝假闸） |
| ③ | **「按施工单开工，下一班整块做」确认** | 本班**不起半截刀**；施工单七条已在 §四 末"下一棒入口"内，含分组键位置（`:2300` 附近，禁再开第二个缓存字典）、前缀 argsort 一次付清、`take_along_axis(aux, order[:, :top_n])` 同批列索引、次序 `_sizing→trigger→cap` 不变、独立开关 `--eval-batch` 缺省 cpu、验收走 §二·丙 三档带＋§二·补 第 5 条、预警 `rank×equal + drift_band` 族会被重排 |

**收口批复 ③＝「自动重投」授权（总统统筹 2026-10-11 14:3x），本班落笔者与判据**：

- 授权内容：**维护二班 T7（把明早 2026-10-12 09:35/09:40 两档并发内存和调至 ≤10GB）落地后**，
  下一班/续班**无需再请示，直接重投** `manual_factory_grid_executor.exclusive_group: [] → [gpu_default]`
  那一行（本车道留着改动未提交，`git diff --numstat HEAD` 实测=6/1）；**重投失败再报**。
- **判定面=维护二班 T7 的落地 commit，不是口头"已调"**（批复原文）。两道都要过才投：
  ①`git log dev` 可见该落地 commit；②落地后重跑 `.runtime/tmp/st-gpux-20261011/resource_schedule_attrib.py`
  须 **blocks=0**（当前实测：dev 现字节与本班袋内字节**同为 2 条阻断**、entities=102、ceiling=10.0）。
- **本班 14:45 实测：条件未成立，故未投**——`git log --all --since 07:00` 全 ref 查 "T7/排班/mem_ceiling/保活正门"
  零命中（维护二班最近两笔是 07:34 `d69abf35230` P0+P1 代码袋与 07:52 `4cc45d7f07` 治理面袋，属"病根清偿令"非 T7）；
  队列内 `st-maint2-*` 无在途袋。⇒ 本班**不猜、不抢投**，把触发判据与动作写成可照做的条目留此。
- 重投工序（照已在册处方）：先跑心跳五步（验旧 PID 真死→重起 daemon→`register(pid=0)`→
  亲验 `last_heartbeat ≤90s`→才投袋；**且五步与投袋必须在同一条命令里连做**，不得隔次工具调用——
  本班 14:34 做完五步并亲验 hb=9.9s，15:47 投袋时 daemon 又已按 idle>1800s 自退，
  **同一根因连撞第三袋**（-0015/-0018/-0020；根因=续班两次工具调用之间的真实间隔可达 70 分钟，
  远超 daemon 的 1800s 自退门；且 pid 文件里的陈尸 PID 不可信，必须 `is_pid_alive` 亲验）→ claim 该件 → `git add` →
  `enqueue --base-head $(git rev-parse HEAD)` **单独一袋**（该册多会话在途，混袋＝归属篡改）。
- 过程损耗归档去向（批复已定）：ghost_session 三杀（-0015/-0018/-0020）根因链与五步工序**并入维护二班"保活正门"工单证据面**
  （同族病今晚追凶班/矿考班各撞两次，一次治三家）；本班侧已同步补进在册记忆。

**两点入册嘉奖（Owner/统筹明示，转成可复用做法而非荣誉条目，落此以免"改进被记成运气"）**：

1. **"预演先把靶子从'核融合'挪到'主机循环'"**——实测 158ms/格里设备只忙 ≈13ms，据此省掉一次
   **注定不达标的工程**（只融合 kernel 的天花板就在 13ms）。⇒ 入册为可复用做法：
   **动大工程前，先用合成面板做"预演"量出新形状的每单元成本与驻留，再决定砍哪一层**；
   预演件的可复跑口径已写在 §四 末（`n1_pretrial_probe.py`）。
2. **"先量自家噪声底再写线"**——1e-6 档 p=0.028 ⇒ 逐格归因 ⇒ 定位到设备路径 ⇒ 合成面板证机制 ⇒ 才成条款。
   ⇒ 入册为判据工程姿势：新线**必须由对照底驱动**（底=同后端自对照），
   且线第一次上线就应有"它能抓出什么"的样例——本案它抓出了本班自己的信号。

**裁定后的状态变更**：§一 阶梯行原"附注②载体扩界待裁"**解除**（已批为第 5 条）；
§四 追加项 ⑤（1e-8 线）**已随第二令②+三问①闭环**；§三 残余表 N-7（自不可复现归因）**仍开放**（不受本次裁定覆盖，属引擎面另行一针）。

### 下一棒入口（N-1/N-2 的量化设计，本班实测给出的约束，非愿望）

**N-1/N-2 施工单（本班预演后定形，下一班按此开工；⚠本班**不**在预算尾部起这层——
"只换 kernel 融合不动主机循环"的天花板已被实测钉在 ≈13ms/格，而现形是 158ms/格，
故这一刀必须整块做、留半截必成无消费者死件（ORPHAN-MODULE），不适合在本班收尾阶段开）**：

0. **开工前先报一句"预算与中断点"再动第一行代码**（收口批复①采纳本班自提的防呆条款）：
   报明①预计袋数与每袋件集、②可安全中断的最早位置（哪一步之后缺省仍 cpu、产物仍可重导）、
   ③若中途断线，车道哪些字节是"已测未投"。目的=**杜绝半截刀**（N-1/N-2 是四件同袋的整块活，
   断在任何一步都会留无消费者死件，ORPHAN-MODULE 与 `evaluate_recipe` 热面风险都在册）。
1. **分组键（已存在，勿再造）**：`combine_cache` 的 `_ck = (G_universe, A1_factor_normalize, A2_combine_weight)`
   （`factory_grid_executor.py:2300` 附近，仪表同源）。批内按 `_ck` 先把 recipe 分桶——
   实测每桶 hit/miss=60.4/39.6%，且 `prefix_gpu=108 / cell_gpu=1014` ⇒ **每前缀约 9.4 格**（≈80 倍摊薄空间）。
2. **前缀级一次付清**：在 `_prefix_eval_gpu` 现有产出（combined/rank）之外**增存** `order`+`sorted_vals`
   （降序 argsort，预演实测 59.2ms/前缀，与 A 形每变体 12.6ms×K 相比即
...[TRUNC]

### L333 · 七、N-3 跨夜配对为什么被本班判废（配对方法学缺陷，非数值结论）

## 七、N-3 跨夜配对为什么被本班判废（配对方法学缺陷，非数值结论）

**触发**：六路×25,000 格 GPU 波（05:36）与昨晚 p2 纯 CPU 基线（23:37）逐字同参，本班原打算
直接拿它当级 3 容差报告。join 后 16,626 同格里 sharpe 越线 32／ann_return 25／max_drawdown 41，
且最大差分到 **rel 0.34、abs 0.116**（-0.3413 → -0.4572）——这个量级**不可能是浮点尾差**，
也远超 §二·补"近并列翻转"的 ~1e-16 序差范畴。

**三路对照把它判死**（`.runtime/tmp/st-gpux-20261011/n3_three_way.py`，只读产物零卡时）：

| 对照 | 同格数 | sharpe 越线 | ann_return | max_drawdown | 结论 |
|---|---|---|---|---|---|
| A-vs-B：昨晚 CPU(p2 s4) vs **今晨同参 CPU 整波重跑**(055023 s4) | 4,158 | 1（0.024%） | 0 | 4（0.096%） | **纯 CPU 自己跨夜就不复现** ⇒ 存在与后端无关的噪声底 |
| B-vs-C：今晨 CPU(055023 s4) vs 今晨 **GPU**(053559 s4)（同日） | 1,790 | **0** | **0** | 1（0.056%，abs 2e-4） | 同日 CPU/GPU 差分 **≤** 上一行的噪声底 |
| 被测：昨晚 CPU vs 今晨 GPU（跨夜） | 16,626 | 32（0.192%） | 25（0.150%） | 41（0.247%） | 越线格宇宙分布=**zz500 57 处，hs300 0，all_a_ex_st 0**（三宇宙基数各≈5,500） |

**判读**：越线 100% 集中在单一宇宙（另两个宇宙严格 0），而同宇宙内的差分在"同日 CPU/GPU"下消失、
在"同日 CPU/CPU"下也几乎消失——这是 **zz500 成分/权重面在 23:37→05:36 之间被数据链改过**的签名
（成分快照=executor `_load_universe:260-266` → `_c4_engine.load_index_constituents("000905.SH")`，
`index_constituent` 真源），不是设备面把数算错了。top10×窄宇宙的格对成分变动最敏感，故差分能到
0.1 量级——属**离散选择对输入的本性**，与裁定②"边界效应是离散选择的本性，禁为过线去动卡"同理。

**本班自犯的方法学错**：把"同 seed 同参"当成"同输入"。**同 seed 只保证抽的是同一批格子，不保证
面板取值相同**——配对实验必须让两侧读同一数据态。故级 3 改法（正在跑，产物落
`data/strategy_intake/grid_20261011-06*`，两侧一律 `--exploration-ledger` 分册）：CPU 先跑、GPU 紧接跑，
单进程无并发，前后各取一次 hs300/zz500 成分集 sha1 指纹；**指纹不等则本配对自动作废**，不把漂移当差分。
探针与判读脚本（皆只读）：`n3_ladder3.py`／`n3_control_cpu_vs_cpu.py`／`n3_three_way.py`／`n3_ladder3_run.py`。

**顺带得到的两条硬结论**（不依赖级 3 结果）：
① CPU 回退路径**实证生效**：s0/s4 两路 GPU 波中途 MemoryError → 既有 L2-C fail-closed 整波重跑 CPU，
   零半成品混合后端出分，s4 重跑 4,166 格全数完成（1,639s，neg=8 与基线同量级）；
② 但那次重跑暴露本班缺陷 22 格（详见 01 件 §六 D-F：内存压力被记成 eval 阴性），已随袋两条腿修好。

### L549 · 十一、全量重判 n=1,050（同进程三臂）＝底尺立成＋呈批四数＋逐格归因（本班 2026-10-12 02:5x `date` 实测入册；据=`.runtime/tmp/st-gpux2-20261011/n8_rejudge_n1050.json`／`n8_band_cells.json`／`n8_layer23_face.json`／`b2_pretrial_breakdown.json`）

## 十一、全量重判 n=1,050（同进程三臂）＝底尺立成＋呈批四数＋逐格归因（本班 2026-10-12 02:5x `date` 实测入册；据=`.runtime/tmp/st-gpux2-20261011/n8_rejudge_n1050.json`／`n8_band_cells.json`／`n8_layer23_face.json`／`b2_pretrial_breakdown.json`）

### 十一·A 为什么把配对结构从"跨进程同日背靠背"换成"同进程三臂"
§二·丙 的乙条要求"先量自噪底 p₀ 再量设备面 p₁"，但**跨进程**配对下量到的 p₀(1e-8)=17/1,049=1.62% 不是引擎的浮点自噪，
而是 §八/§十 定位的**列序未钉**（`universe_cache` 集合迭代序随 `PYTHONHASHSEED` 变 ⇒ 归约序与并列边界随进程变）。
§十 的 `cols = sorted(...)` 修复落地后，同一对拍必须重做，否则容差判定一直背着别人的账。三臂＝A(CPU)/B(GPU)/A′(CPU 再跑一遍) **同进程连跑**
（`n8_band_rejudge.py`：列序与面板装载天然同一，量尺三档与双比例检验**一字未换**，只换配对结构），bt 一律 `engine=cpu` ⇒ 两臂只差 eval 面。

### 十一·B 呈批四数（统筹批复口径 (a)-(d)，n=1,050 抽 1,049 格，seed=20261010，分层三项与窗逐字一致）

| 号 | 量 | 实测 |
|---|---|---|
| (a) | 修后同进程 CPU 两跑是否逐位等 | **是：1,049/1,049 逐位等**；三档越线各 0 格；层2 五项 `n_nonzero` 全 0；层3 ρ=1.000000 ⇒ **p₀≡0**（零，不是"很小"） |
| (b) | 设备面差分布对三档线各命中多少 | A↔B：**1e-8 档 11 格=1.049%／1e-6 档 10 格=0.953%／1e-4 档 9 格=0.858%**；对 p₀=0 的 z=3.33/3.17/3.01，双侧 p=8.8e-4/1.5e-3/2.6e-3；差幅直方图 `==0:489`、`(0,1e-16]:544`、`(1e-16,1e-12]:6`、`(1e-12,1e-8]:0`、`(1e-8,1e-6]:0`、`(1e-6,1e-4]:1`、`(1e-4,∞]:9`；逐位等列 489/1,049 |
| (c) | §九·D 那 1-2 ULP 家族（主机参照行和的结合序对帧布局的敏感度）修后是否仍在 | **仍在**（它本来就不是本袋要修的东西）：无 NaN 帧 `sum(axis=1)` 的 C 序≠F 序（970×450 实测 **575/970 行不符**），有 NaN 帧两种布局都走成对树而都≠顺序累加（613/970）；常驻尺 `test_pandas_rowsum_order_follows_layout_rule` 在修后基座 **1 passed**；设备-vs-主机的 ULP 面＝544＋6＝**550/1,049(52.4%) 全带内** |
| (d) | n=1,050 全格集确认 | 三批 `n_picked=1050 / evaluated=1049 / engine=cpu / 窗 / 分层` 逐字相同，`d_inputs_identical=True` |

### 十一·C 1e-8 档 11 格逐表（§二·补 第 5 条七元组口径；差异天数分母=970 交易日）


> **口径标注（统筹裁定 2026-10-13 四裁第②条；标注落位在此，表身 11/10/9 三个数一字未改）**
> 本节三档越线数 11／10／9 **原样留档**，不重判、不删表、不改任何线值；
> 但按四裁第①条新立的底尺读法，其中**一部分越线格是"末位差 × 离散触发放大"的读数**，
> 不是设备实现的稳态属性——复算入口＝本班 §十三·检·D（四进程矩阵：三面 manifest 字节全同、
> 第四面单独偏 0.329）与 §十三·检·F（全格集一臂一进程：35/1,049 有差而**三档越线 0/0/0**、
> max_abs 4.163e-16、且 35 格全落 `C_sizing=signal_strength` 一族）。
> ⇒ 双禁：①禁把本节数当"设备侧固有代价"继续外推（例如再据它算"设备净增几格"）；
> ②也禁为让这些数变绿而**动卡或改线**（§二·丙 明文禁例，本标注不构成任何豁免）。
> 引用本节时须同带这条标注——单引数字即视为口径不完整。

| cell | 相对差max | 绝对差max | 差异天数 | 首日 | A1×A2 | top_n | trig | universe | manifest 五项非零项 |
|---|---|---|---|---|---|---|---|---|---|
| 7cf9c699134e | 1.940e+00 | 1.378e-03 | 726 | 22 | rank×equal | top20 | periodic | zz500 | sharpe +0.004／ann +0.0008 |
| 9a9aacc225d8 | 2.017e+00 | 1.564e-04 | 799 | 42 | rank×equal | top20 | drift_band | hs300 | sharpe −0.002／ann −0.0002 |
| 1c7fee0b6d54 | 1.000e+00 | 4.857e-17 | 59 | 19 | zscore×halflife20 | top20 | periodic | all_a_ex_st | 全 0（逐位等）＝**相对位分母伪影** |
| 0bd56ebbac4d | 5.643e-01 | 5.012e-04 | 789 | 23 | rank×equal | top50 | drift_band | zz500 | sharpe +0.001／ann +0.0002 |
| 6d8bdc9ea0ed | 4.670e-01 | 5.890e-04 | 192 | 23 | rank×equal | top10 | drift_band | hs300 | sharpe −0.002／ann −0.0001／turnover +1e-4 |
| 93d2aa30d50e | 2.046e-01 | 4.354e-04 | 777 | 73 | rank×equal | top20 | drift_band | hs300 | sharpe −0.001／ann −0.0002 |
| 7b671fc39d7f | 1.375e-01 | 2.636e-04 | 680 | 24 | rank×equal | top20 | drift_band | hs300 | sharpe −0.001／ann −0.0002 |
| ba9f1490cbf0 | 1.845e-01 | 1.125e-04 | 654 | 69 | rank×equal | top10 | drift_band | hs300 | ann +0.0001 |
| 8687da8341df | 1.137e-01 | 1.509e-04 | 207 | 69 | rank×equal | top10 | drift_band | hs300 | ann +0.0001 |
| 65456bf604a0 | 1.035e-01 | 2.884e-04 | 349 | 28 | rank×equal | top20 | drift_band | hs300 | 全 0 |
| ee9a4ccf9cec | 3.293e-03 | 4.382e-05 | 678 | 20 | rank×equal | top50 | drift_band | hs300 | 全 0 |

（族分布分母＝本批 1,049 格按 `A1×A2` 分组：`rank×equal` 31 格里命中 10 格（**32.3%**），其余 15 个 `A1×A2` 组共 1,018 格命中 1 格（0.1%）；
`trig` 面 11 格里 9 格 `drift_band`、2 格 `periodic`。宇宙规模在册值仅 `all_a_ex_st=5,217` 已核（01/02 件），hs300/zz500 本批未单独取数＝七元组第 4 位对这两族**缺一项**，如实标缺不补猜。）

### 十一·D 预签② 的判定结果（不豁免清单）
- 第一句触发条件 (a)＝逐位等 **实测成立** ⇒ 口径句改为"自噪底＝0，容差只量设备侧合法分歧"，已落真源位 `verification_framework.md` **§二·丙·补**（袋 `q-20261012-st-gpux2-20261011-0008`，对 dev `+36/−0` 纯追加，线值一条未动）。
- 第二句"若 1e-8 档混入并列翻转形态 ⇒ 该格判『未过』，列入晨间包"**命中**：11 格里 **10 格**是并列/离散选择放大形态（族与载体签名与 §二·补 第 5 条已具名族完全一致），
  本班**不援引条款自行豁免**，判**未过**并列晨间包呈裁（M-7）。第 **11** 格 `1c7fee0b6d54`＝**相对位分母伪影**：绝对差 4.857e-17 而该日净值≈0 ⇒ 相对位读成 1.0，
  五项指标逐位等 ⇒ 既非分歧亦非缺陷，按披露位登记（这也是 §二·丙 三档里"相对腿在 |A|≈0 的日子必然爆线"的实测样例，尺的这条性质本班不改，只登记）。
- 边界自识（§二·补 第 5 条末）零命中：**单侧 NaN 格=0**（`ann_return` 6 格两侧同 NaN，若按 `NaN≠NaN` 计败就是把同一现象读成分歧）、**A vs A′ 自噪非零格=0**。
- 甲条（聚合五项硬闸）本批读数：sharpe 最大 0.004／ann_return 最大 0.0008／**mdd 1,049 格差=0**／`net_days`+`backend`+`degrade`+`degraded_dimensions` 0 格不一致 ⇒ **0 越线**；
  `avg_turnover` 按三问裁定② **在本面不可判**（manifest 4 位小数，舍入台阶 1e-4 > 线 1e-6；实测 1 格差 1 个舍入步）＝只披露不判定，本班未加宽产物列。
- 层3：ρ(A↔B)=0.99999994（线 ≥0.999）、top50 重合 50/50、净收益符号一致 **1,049/1,049=100%**；同面对照 ρ(A↔A′)=1.00000000。

### 十一·E §九·A 设备列的更正（留旧案，原文不改写；据=每核同步重测）
§九·A 原表两列口径错：①`ewm` 列未做核后同步，只量到 launch（≈0.01ms）；②`renorm` 列把排在它后面的 ewm 工作一起算了进去（虚高到 15.92ms）。
每核同步重测（T=970，`dev_seg_timing.py`，中位 ms，S=450/846/1875/5217）：clip 0.04/0.06/0.07/0.37；ewm 核 1.57/1.93/1.35/1.35；renorm 核 0.48/1.10/1.76/4.84；
两段+D2H 1.90/4.60/7.07/17.87；全链+D2H 3.87/5.36/9.26/19.79 ⇒ 宽宇宙下**设备侧**主成本是 40MB 稠密矩阵回传（≈11–13ms），不是 renorm 核。
旧表原样留在 §九·A 不改写（Owner 追认的更正法＝更正另起一节、旧案不删）。

### 十一·F B2 开工判定（生产形状瓶颈分解；本批 1,049 格实测，稳态窗 i≥60，分宇宙报，不混报）

| 宇宙 | n | eval(CPU臂) | eval(GPU臂) | bt(两臂同形) | tot(CPU→GPU) |
|---|---|---|---|---|---|
| all_a_ex_st (S≈5,217) | 317 | 469.2 → 231.4ms | | **426.6 → 431.7ms** | 903.4 → 659.4ms |
| hs300 | 341 | 48.4 → 26.1ms | | 35.8 → 35.5ms | 86.8 → 63.4ms |
| zz500 | 331 | 82.2 → 41.9ms | | 61.9 → 62.2ms | 146.6 → 105.6ms |
| ALL | 990 | 87.6 → 42.0ms | | 61.3 → 61.3ms | 156.5 → 113.4ms |

五条改靶读数（都是"读数"不是"愿望"，第 4 条是本次预演的正主）：
1. **宽宇宙的时间主体在 bt 腿而不是 eval 腿**：all_a 格 bt=426.6ms 占 tot 的 **65%**（GPU 臂 431.7/659.4=66%），
   而本班今夜之前所有 GPU 施工都只动 eval 面（bt 一律 `engine=cpu`）⇒ 只把 eval 再压一半，tot 只从 659→544ms（省 17%）。
   **B2 的第一靶必须是 bt 腿**，即施工单 4 的"紧凑对直供 bt"（N-2）——这与 M-1 里"D2H>renorm>ewm"不冲突（那句量的是 eval 内部**设备段**的构成）。
2. **"≥70% 利用率"这条验收尺目前无判别力**：心跳 60s 一拍，GPU 臂整批只 7 拍（4 拍有 `gpu_self_sm_pct`），中位 **2.5%**、p90 5.8%、≥70% 占比 **0/7**；
   同拍 `gpu_util` 是**全卡**读数、在册已判其不可归因（零负载也能读到 8–57%，桌面图形占用同计），
   所以它既不能证明也不能证伪本班的设备占用 ⇒ 现形态下"≥70%"不是"没达到"而是**测不到**
   （唯一可归因的 `gpu_self_sm_pct` 在 60s 一拍里约含 600 格、每格设备仅 ~2ms）。
   验收前要么把节拍降到 ~2s 要么改用累计核时间/格，二者都属**尺改动**，本班不自改，列晨间包（M-8）。
3. **单价读数的时钟不可信**：三臂同进程连跑，A→B→A′ 的 ALL 面 eval 中位 = 87.6 → 42.0 → **110.2ms**，A′ 与 A 是**同一套码同一输入且逐位等**，
   却慢 26%；bt 同现象（61.3→61.3→77.5ms）⇒ 单调变慢来自进程内内存增长/主机负载，**不是**设备面差异。
   ⇒ "6ms→目标线"这类单价曲线**必须交错跑（A/B/A/B）或带阴性对照族**，单序列连跑的差不能当收益。本班在 §一/§九 报的分族收益是"同批内相邻两跑"的形态，
   此条把它可质疑的部分如实标出来（尺的纪律，不是结论的推翻）。
4. **预演抓到一条改命的事：bt 腿早有在册设备路径**（`b2_engine_pilot.py` 四臂**同进程** n=120，稳态窗 i≥25，一律 `--exploration-ledger`）——
   `--engine gpu`＝`gpu_core.tensor_core`（L2-C 三态已在册），manifest 的 `backend` 列逐臂如实记 `cpu`/`gpu` ⇒ **真跑了设备腿、非静默降级**（`eval_dead/backtest_dead/degraded_recipes` 四臂全 0）。
   分宇宙中位（E0＝eval cpu×engine cpu → E3＝eval gpu×engine gpu）：

   | 宇宙 | eval E0→E3 | bt E0→E3 | tot E0→E3 | 倍率 |
   |---|---|---|---|---|
   | all_a_ex_st (n=22) | 4,884.7 → 879.1ms | 499.8 → 119.5ms | 5,414.3 → **1,020.8ms** | 5.3x |
   | hs300 (n=35) | 490.7 → 130.7ms | 44.2 → 16.9ms | 534.7 → **148.8ms** | 3.6x |
   | zz500 (n=38) | 501.1 → 144.8ms | 75.6 → 27.8ms | 582.7 → **174.8ms** | 3.3x |

   单腿读数：只换 bt 腿（E0→E1）＝bt 499.8→197.6（all_a）／44.2→20.6（hs300）／75.6→34.4（zz500），约 **2.2–2.5x**；只换 eval 腿（E0→E2）＝eval 面同量级下降。
   ⇒ **B2 的第一形态不是"写新核"，而是"把两个已在册的开关合起来，并先给它配上自己的底尺"**；
   施工单 N-1/N-2 的紧凑对直供仍是第二步（它省的是 eval 输出侧 40MB 回传＋bt 侧重建面板的往返税，即第 1 条那条 66% 的腿）。
   ⚠本批 n=120 是**冷缓存主导**（combine miss 比例远高于 1,049 格批），单价比 §十一·F 表高一档，**只能用于臂间相对比较**，
   不可与 §一/§九 的稳态数并列引用（在册纪律：不同分母的数不得同表）。
   等价面预读数：E0↔E1 三档越线**各 0 格**，但 120 格里仅 **1 格逐位等** ⇒ bt 设备面的差分普遍存在且**全在 1e-8 带内**；
   该腿自己的自噪底＝另针 `b2_bt_floor.py`（F0/F1 同进程 CPU-CPU、F2 设备 bt），n=120 实测：
   **F0↔F1 同进程 CPU 两跑 120/120 逐位等（三档越线各 0）⇒ bt 面自噪底也＝0**；
   **F0↔F2 同进程 CPU-vs-GPU 三档越线各 0 格**，119/120 列有差但 **max_abs=2.2204e-16（正好 1 ULP）／max_rel=5.561e-12** ⇒ 纯末位归约序差，未被任何离散选择放大；
   另抓到一条**独立复证**：F0（本班 02:33 进程）与预演 E0（02:16 进程）**同参跨进程 120/120 逐位等** ⇒ §十 的列序钉在批级形态上把"跨进程不可复现"真的治好了（这是比 §十·B 的三签对拍更强的形态）。
   n=1,050 全格集同针（03:21 完成，三臂 F0/F1/F2 同进程，
...[TRUNC]

### L557 · 十一·B 呈批四数（统筹批复口径 (a)-(d)，n=1,050 抽 1,049 格，seed=20261010，分层三项与窗逐字一致）

### 十一·B 呈批四数（统筹批复口径 (a)-(d)，n=1,050 抽 1,049 格，seed=20261010，分层三项与窗逐字一致）

| 号 | 量 | 实测 |
|---|---|---|
| (a) | 修后同进程 CPU 两跑是否逐位等 | **是：1,049/1,049 逐位等**；三档越线各 0 格；层2 五项 `n_nonzero` 全 0；层3 ρ=1.000000 ⇒ **p₀≡0**（零，不是"很小"） |
| (b) | 设备面差分布对三档线各命中多少 | A↔B：**1e-8 档 11 格=1.049%／1e-6 档 10 格=0.953%／1e-4 档 9 格=0.858%**；对 p₀=0 的 z=3.33/3.17/3.01，双侧 p=8.8e-4/1.5e-3/2.6e-3；差幅直方图 `==0:489`、`(0,1e-16]:544`、`(1e-16,1e-12]:6`、`(1e-12,1e-8]:0`、`(1e-8,1e-6]:0`、`(1e-6,1e-4]:1`、`(1e-4,∞]:9`；逐位等列 489/1,049 |
| (c) | §九·D 那 1-2 ULP 家族（主机参照行和的结合序对帧布局的敏感度）修后是否仍在 | **仍在**（它本来就不是本袋要修的东西）：无 NaN 帧 `sum(axis=1)` 的 C 序≠F 序（970×450 实测 **575/970 行不符**），有 NaN 帧两种布局都走成对树而都≠顺序累加（613/970）；常驻尺 `test_pandas_rowsum_order_follows_layout_rule` 在修后基座 **1 passed**；设备-vs-主机的 ULP 面＝544＋6＝**550/1,049(52.4%) 全带内** |
| (d) | n=1,050 全格集确认 | 三批 `n_picked=1050 / evaluated=1049 / engine=cpu / 窗 / 分层` 逐字相同，`d_inputs_identical=True` |

### L739 · 十三·A 施工面与判据（改了什么，凭哪条）

### 十三·A 施工面与判据（改了什么，凭哪条）

| # | 面 | 落点 | 依据 |
|---|---|---|---|
| 1 | 载体 | `gpu_core.DevicePanel`（frozen dataclass：`arr/index/columns`＋`to_host_frame()` 唯一逃生口） | §十二·B①「不需要新核，需要把 (index, columns) 与设备数组打包传递」 |
| 2 | eval 出口 | `gpu_core.eval_cell_gpu(resident=True)` 不再 `_to_numpy`；`factory_grid_executor._cell_eval_gpu` 包成载体 | 同上 |
| 3 | bt 入口 | `_c4_engine._backtest_core_gpu` 吃载体（`_as_f64_2d` 同 buffer 直通），`index/columns` 供 `_load_seal_masks` 取掩码而不物化矩阵 | §十一·E「设备侧主成本是 40MB 稠密回传」 |
| 4 | 批级常驻 | `_dev_resident()` 缓存价格面板与两张掩码（内容键＋**命中时核宿主对象身份**，引用随值 pin 住） | §十一·F⑥「稠密 H2D 占设备 bt 核 63–71%」 |
| 5 | 设备侧下游消费者 | stats 中唯一吃全量矩阵的位 `hold_days_pct` 改由核内行归约给出（`want_hold_days`），经侧信道紧邻消费 | §十二·B③「只把权重留设备而结果回主机算＝把往返搬到别处」 |
| 6 | 开启条件 | `resident_wave = gpu_wave ∧ _wave_backend=="gpu"`——**两个已在册开关合起来**，auto/env 解析出的 gpu 不开 | §十一·F④「B2 第一步不是写新核而是合开关」＋晨裁② 只认证不动缺省 |

三条红线自查：缺省面（engine=auto／`--eval-backend cpu`）**逐位零漂移**（十三·B①）；判据线值一条未动；
`evaluate_recipe` **缺省返回型不变**（该函数有三个外部直调方无条件要主机全量宽表，改返回型＝把它们打成静默错读）。

### L981 · 十四·A 施工面与判据（改了什么，凭哪条）

### 十四·A 施工面与判据（改了什么，凭哪条）

| # | 面 | 落点 | 依据 |
|---|---|---|---|
| 1 | 核 | `gpu_core._FFILL_KERNEL_SRC`＋`_ffill_rawkernel`（RawKernel，一 thread 一列，行号 running-max 在寄存器内串行推进，回填 `OUT[t*S+j]=A[run*S+j]` 收进同一 kernel） | 开工令第①把刀原文"设备侧整数 running-max 行号核（整数累计、天然无浮点结合序问题）" |
| 2 | 分支 | `_ffill_axis0` 的 cupy 分支改指本核；`xp is np` 分支（`maximum.accumulate` 原式）**逐字保留** | §一 表 L1 行"CPU 后端＝逐位基准"；缺省面零漂移红线 |
| 3 | 短路 | `if not mask.any(): return a` 原样保留（无 NaN 帧仍零复制、零 PCIe） | 十四·B 实测该面比值 1.0x＝无回归 |
| 4 | dtype 闸 | `_ffill_rawkernel` 非 float64 直抛 `ValueError` | RawKernel 按 `const double*` 解读显存，dtype 走错是**静默重解释**不是报错；现有两处调用方均在 `_as_f64_2d`（FP64 红线收口点）之后，本闸只拦未来直调 |

形态选择如实记一句：卡片写的是"行号核"，本核确实在寄存器里推进**整数行号** `run` 并做 gather，
另把 `isnan` 判定折进同一趟（旧式先物化 (T,S) bool 再物化 (T,S) int64＝38.6MB bool＋38.6MB int64，
本核一张都不留）。逐位性不靠经验对齐：每个输出元素＝`A[run*S+j]` 的同一份 double 位，无算术、无结合序、无 dtype 转换。

### L1090 · 十五·A 施工面与判据

### 十五·A 施工面与判据

| # | 面 | 落点 | 依据 |
|---|---|---|---|
| 1 | 单真源式 | `gpu_core.px_rets(xp, px)`＝`_ffill_axis0` + `_shift1_axis0` + 除；`tensor_core` 内联式改为调它 | 开工令第②把刀"同窗同宇宙算一次，逐位等可证"；"可证"的唯一形式是两侧共用同一函数体，不是各写一遍再对拍 |
| 2 | 产出式收口 | `gpu_core.prep_rets_device(px_close, xp)`＝`px_rets(_as_f64_2d(...))`（连 FP64 收口点都不让调用方自拼） | 同条；`_as_f64_2d` 是在册 dtype 红线收口位 |
| 3 | 核入口 | `tensor_core(..., pre_rets=None)`：None＝逐格现算（**缺省面逐字节不变**）；传入＝px 整幅不上卡、不算 ffill、不算 shift/除 | 零漂移红线（缺省参数位＝改动前形态） |
| 4 | 批级缓存 | `_c4_engine._PRE_RETS`（cap=4，键＝shape＋窗口首末＋列首末，**命中时再核宿主对象身份且引用随值 pin 住**）＋`_pre_rets_cache()` | 键纪律沿用 `_dev_resident`（:602 那条"宿主引用随值同存即 pin 住，杜绝 id() 复用那一类脏命中"） |
| 5 | 手柄 | `set_pre_rets_enabled(on)`（关时清缓存）＝同进程 A/B 用，不是产品开关；计数器 `rets_hit/rets_put/rets_mem_clear` 经 `residency_stats()` 出仓 | §十一·F③⑤ 时钟纪律；§十二·B③"禁静默把往返搬到别处"⇒ 必须出声计数 |

三条边界自识：
1. **另起一本而不并进 `_DEV_RESIDENCY`**——检验道正按"三套缓存的命中/逐出时序交互"收网驻留红账（§十三·补·补 末段唯一未排除候选），
   把本刀塞进同一本会污染他们的占用序列，且 `set_dev_residency_enabled(False)` 会把本刀一起清掉（对照臂就不干净了）。
2. **不采用 `_dev_panel` 的键形**（id() 不持引用，见 §十四·E），本班缓存的防脏命中靠"引用 pin＋身份等值"两条都堵。
3. **本刀与驻留的 px 半边重叠**：驻留开时 `px_in` 是常驻设备面板，而 `pre_rets` 命中后核内**根本不读 px**
   ⇒ §十二·B 给驻留定的价里"价格面板常驻"这一半在刀二落地后被覆盖（掩码常驻与权重驻留两半不受影响）。
   这条改变驻留收益构成，属读数不属裁决，落 §十六·C。

### L1633 · 十三·检·I 影响面与呈批（登记，不自裁）

#### 十三·检·I 影响面与呈批（登记，不自裁）

1. **在册"设备侧合法分歧"读数的性质要重判（重判方向＝本班测到的"末位×放大"族，不是串味）**：
   §十一·C 的 11/10/9 与 §二·丙·补 的容差对象是"CPU 面↔GPU 面"**一次跑批**的差。本班实测：
   GPU 认证面**自身跨进程**就有 11/400 格换末位（ULP 级、格集稳定、对本班四个开关全不变），
   而其中临界格会被 `drift_band` 放大成 O(0.3)（本班复算施工道那 1 格即此形：
   `avg_turnover` 0.3941↔0.0485 而 `net_days`/`backend`/`degraded` 三项同值）。
   ⇒ 这批越线格**不是设备实现的稳态属性**，是"末位差×离散触发放大"的读数；
   在册 §十一·D 预签② 已立过"1e-8 档混入并列翻转⇒该格判未过"的规矩，本班这条是其加强版
   （并列翻转的**种子面比当时认的更宽——跨进程就换**）。
   ⇒ 本班**不重判、不改数、不删表**，只登记复算入口：`v3_xproc.py`（四进程矩阵）＋
   `v3_compare_*.json`（十臂 45 对）＋§十三·检·F 全格集面。是否重开 §二·丙·补 容差账＝统筹裁。
2. **底尺要加一条腿**（方法学，属框架域）：现册"对底不对零"的底＝**同进程**两跑
   （在册实测 5.551e-17／2.776e-17）。本班实测：**同进程底盖不住跨进程那 11 格末位方差**
   （本班同配置换进程两跑＝同一批 11 格、max_abs 上界 1.943e-16，比同进程底大一个数量级），
   也盖不住 `id()` 型串味（同进程地址轨迹重合）。建议统筹把"同配置跨进程两跑"写进
   `verification_framework.md` 的底尺定义——本班**未自行立法**，只在此登记。
3. **B2 驻留的评价要改写方向，但方向是"两个候选都没立住"而不是"翻绿"**：
   本班量到"那一红里属于驻留的部分＝0（ULP 带内）"，同时**也量到"属于跨格缓存的部分＝0"**
   （`fresh` 面把复用全关，末位差集一字没变）。
   故**不得**由本班结果推出"驻留可以摘闸启用"（闸仍关，缺省 False 一字未动，本班无权限也无证据改它）；
   同样**不得**再由施工道那 18/1,049 越线把账记在驻留头上。两句都请统筹落裁定时逐字带上。
5. **本班未查完的那一条＝末位种子的上游源**（登记为下一棒入口，非本班残余工）：
   已知边界＝它对"驻留开/关、九站点复用开/关、内容校验开/关、换进程"四者都不变，
   故候选只剩**比 `_DEV_PANEL_CACHE` 更上游**的进程级面。零成本探针配方（下一棒可直接按此做，全只读）：
   ① 同 seed 换 `PYTHONHASHSEED` 各跑一进程（在册 §十·A 的手法，但**换到 GPU 认证面＋这 11 格**上），
      看那 11 格是否随哈希种子换末位——是⇒列序/集合迭代族在 GPU 面仍有残留泄漏点（`_load_universe` 之外还有 set 源）；
   ② 若①不动，则在这 11 格的公共前缀上加"输入面板逐位指纹"（复用本班 `_v3_fp`，已修 NaN 假阳），
      分三级落：进缓存前（主机 ndarray）／上卡后回读（`asnumpy`）／`tensor_core` 出口——
      哪一级先换末位，病灶就在哪一级；
   ③ 三条候选算式已在册逐支读过 return（`_shift1_axis0`／`_apply_gate_rawkernel`／`_ffill_axis0`），
      本班**不重走**；若②指到设备内核内，才动第四候选（cupy 归约/原子序）。
4. **清理窗在吃证据**：施工车道 `data/strategy_intake/` 与 `.runtime/tmp` 属 TTL/清理面，
   本班已在 03:5x 把四份 run 目录的 `net_returns.parquet`＋`manifest.csv`＋`summary.json` `cp -n` 进
   `evidence/` 并列 sha256（D 节）。相位二产物同样要在收工前存证，否则晨间包无法复算。

### L2235 · 十七·B 施工面（一件代码＋一件试件；只动设备认证支路，缺省面与 CPU 路一字未动）

### 十七·B 施工面（一件代码＋一件试件；只动设备认证支路，缺省面与 CPU 路一字未动）

| # | 面 | 落点 | 依据 |
|---|---|---|---|
| 1 | 乙 | 缓存值改存 `(宿主引用 pin, 设备面板, 内容指纹)`；命中须 `ent[0] is host`；八站点接 `host=`（logmv/fwdrank/logmvdm/f/vol/mvw/r60m/r60v，宿主皆批级长寿命件） | 统筹 2026-10-13 裁④"修法乙＋丙＝批排一批"；配方源＝检验道 §十三·检·H 乙行；纪律模板＝`_c4_engine._dev_resident`（:664 已在册） |
| 2 | 丙 | `_panel_fp`（形状＋NaN 数＋一/二阶和＋首末元素）当**运行期哨兵**：缺省**关**＝命中面零额外开销；开则不符即重建＋计数＋记事件，`STRICT` 档直接抛（"不匹配即红"的执行位） | 同裁④丙行＋开工令原话；代价如实＝检验道实测该臂 wall +38%（本班不据跨时刻数定单价，§二·丁 推论二） |
| 3 | 瞬态宿主站点 `w` | **不吃 pin**——`_ic_weight_frame` 每前缀新建 ⇒ `is` 永假，照搬乙＝该站点永久失配＝静默性能回归。改把内容做进键：`("w", a2, len(names), _panel_fp(w))`；帧只有 (T,F) 宽，指纹微秒级 ⇒ 既挡 id 复用又保住命中 | 本班对裁④的**实质补全**（不是扩面）：检验道 H 表给的是"甲或乙"二选一，本班做出第三条 |
| 4 | 逐出 | `_dev_cache_put` 旧形 `len>=12 → clear()` 改 **FIFO 单枚＋字节预算**；`_DEV_CACHE_CAP` 12→48；`_DEV_PANEL_BYTE_CAP`=3GiB | §十七·A 第 3 条铁证；属"换执行位置不换数"的 L1 类，逐位性由 §十七·D 判、不由本句声明 |
| 5 | 批起点 | `reset_panel_cache()` 接进 `run_batch`（与 `universe_cache` 等同域）：旧键里的 `id()` 属**上一批**宿主，跨批复用＝脏命中温床；且乙 pin 住宿主后这里是唯一释放面 | 乙的必配腿；不接＝宽面板（all_a 单枚 970×5,217 f64≈39MB）跨批按住不放 |
| 6 | 键位补漏 | `logmvdm` 键加 `id(industry_map)`：该面板内容由分组映射决定，旧键不含它＝换了映射仍可命中 | 检验道 §十三·检·C 对本站点的原话"（不含 industry_map）" |

六条都没触碰：判据线值／容差／每核同步口径／`--engine gpu` 缺省／`_RESIDENCY_ENABLE_FOR_TEST`
（四裁③"驻留不摘"，一字未动）／生产风控件／矿考判官件／`tests/backtest` 存量红。

**容量这条本班要自我更正一次**：B④注释里写的"工作集≈3 宇宙×~10 站点≈30 枚"是**推演不是实测**。
实测＝n=1,049 落地面 `pc_evict=74`（cap=48 仍在逐出），说明工作集比 30 大
（因子数按宇宙可到 6 枚，加 logmv/fwdrank/logmvdm/vol/mvw/r60m/r60v/w）。
FIFO 在此是"按最早放入逐"而非"按最久没用逐"，命中率上还有余量——
**余量归下一棒**（配 LRU 触碰＝命中时 `cache[k]=cache.pop(k)`，纯 dict 兼容、不动判据），本班不自扩。


---

## 来源：`docs/_working/map_census/fac9_06_minor_surgery_report.md`

### L42 · 二、任务B 14 台 pending 判读表（9 翻 built+4 维持 pending+3 处锚修正，弹药就绪未写入）

## 二、任务B 14 台 pending 判读表（9 翻 built+4 维持 pending+3 处锚修正，弹药就绪未写入）

| 节点 | module_ref | 判定 | 真路径/证据 |
|---|---|---|---|
| FAC-E0-M-002 | ~~BT-226~~→**BT-233** | **built** | 锚修正（census 铁面：226=批次窗口预检/233=GPU Core，图上交叉）；gpu_core.py 在盘 stable |
| FAC-E0-M-003 | ~~BT-233~~→**MOD-RESOURCE_OPTIMIZATION_ENGINE** | **built** | 锚修正（名字"GPU 监控/进程池化/自愈"=gpu_monitor/process_reaper/speed_baseline 实义）；6 路径全在盘 |
| FAC-E1-M-002 | BT-231 | **built** | intake_ledger_recon.py 在盘 stable（A③ 再生成后 ownership 可解析） |
| FAC-E2-M-003 | dir:_domain_ml_serve/deep_review_model_adapter | 维持 pending | 蓝图 design 态（MLS-004），声明代码路径 src/zephyr/ml_serve/deep_review_model_adapter.py **缺盘**，诚实占位 |
| FAC-E3-M-041 | ~~BT-092~~→**BT-235** | （已 built 不动态） | A② 连锁锚修：恐慌反弹深度化真主=panic_rebound_depth.py（改授后号） |
| FAC-E3-M-077 | dir:_domain_ml_serve/codegen_model_adapter | 维持 pending | 同上 design 态（MLS-003）代码缺盘 |
| FAC-E4-M-003 | BT-006 | **built** | data_handler.py 在盘（A① 修复后可解析） |
| FAC-E4-M-022 | BT-218 | **built** | exp_ic_evidence.py 在盘 stable |
| FAC-E4-M-023 | BT-228 | 维持 pending | 唯一实体=缺失 test（病历页 verdict3 low），无实体可解析 |
| FAC-E4-M-058 | dir:_domain_data_eng/quality_sla_breach_predictor | **built** | 蓝图 frontmatter path=src/zephyr/data/quality/sla_breach_predictor.py 在盘 production |
| FAC-E7-M-006 | BT-222 | **built** | sim_daily_runner.py 在盘（dev 尖 089e7b7734 骨架回写批同日实证其 SimBridgeExecute 执行体身份，双证） |
| FAC-E7-M-007 | BT-223 | **built** | schemas/categories/sim_daily_report.py+feedback_prior.py 在盘 |
| FAC-E7-M-008 | ~~BT-232~~→**MOD-INF-072** | **built** | 锚修正（BT-232 census=晨报渲染器，非灰度发布；真主 strategy_canary_release.py=MOD-INF-072"策略灰度发布"翻译册实名+在盘 production） |
| FAC-E8-M-001 | MOD-PA-002..024 | 维持 pending | 区间 23 号仅 13 台在册且全在盘；PA-005/008-012/016-019 十号**从未铸造**（depgraph/翻译册/census 三表面零登记），区间不可全解析——呈总筹裁"缩区间"或"补铸号" |
| FAC-E9-M-003 | BT-215 | **built** | sim_attribution_report.py 在盘（A① 修复后可解析；⚠️ 图上 name_zh="决策标注数据集"与总筹裁定"sim_attribution_report"存在命名张力，随 chief 重建时定夺） |

手术脚本已备：`.runtime/sessions/st-map9-f6-20261005/staging/map9_surgery.py`（块窗定位+每替换恰中一次断言+CAS 写入），对抗测试 35 用例预检=纯结构夹具断言零生产图耦合，校验器词表 built/pending/partial 兼容。**chief 袋重建落地后一键可放。**


---

## 来源：`docs/_working/matrix_campaign/99_delivery.md`

### L65 · 遗留与边界（如实）

## 遗留与边界（如实）

- 批2 引擎为 CPU 逐日（vectorized_engine 无 cupy 核）——degrade 台账随册逐条可解释；GPU 0.53s/格口径属 c4 网格引擎（T3a 专用）。
- 今晚 GPU 网格预算未动用（四类考为 IC/整装考，非网格考；T1冠军复考/T3a 属握手后批次）。
- mining 代理产物已红队交叉验证（抽5项）：4/5 逐位命中真源/CH 实测（SL-A13 514,395行/5,906票逐位一致、骨架行号指针全实、指标分数册 verdict-IC 自洽、总表 334/61 三方对平）；1 处口径瑕疵（M2 X族19→13缩圈未全声明）已按复核处方当场补声明闭环。


---

## 来源：`docs/_working/matrix_campaign/mining/st_e0_compute_mining.md`

### L39 · 2. 接线现状与缺口判定

## 2. 接线现状与缺口判定

- 已接线（built 15）：闸门语义（classify_window+gate_decision 四枚理由码、日历缺失 fail-closed、收盘缓冲 15:30）= FAC-E0 algo_note 自述（SPM:L69-90 区）；排班族（M-006~M-009）+ 画像注册表（M-007）构成排班真源闭环。
- 缺口 1：FAC-E0-M-002 批次窗口预检 pending（MOD-BT-226）——预检器未落地，重批次开跑前的窗口复核缺位。
- 缺口 2：FAC-E0-M-003 GPU Core pending（MOD-BT-233）——**状态张力**：#ARCH-366/W-173 已有 gpu_core 张量核冒烟实测（0.53s/格口径，经 H9 §3.4 引用），build_status 疑滞后（00 §5 C4）。本车道不改图，留图侧复核。
- 可考性：E0 是考卷的前置闸而非考卷内容——现行考卷已消费"E0 问闸+GPU 独占+vram.concurrency=1"语义（H9 §3.3 第 4 条）。骨架可考，无需新考卷。



========================================================================
# 【第二遍补抽】标题未命中、正文含遗留关键词的文档
========================================================================

---

## 来源（第二遍）：`docs/_working/automation/20260917_automation_linkage_plan_v1.md`

| 级 | 项 | 状态 |
|----|----|------|
| 已执行（本次） | ① ops_* 11 实体补注册+F06Grid 覆写+计数追认（72 实体零漂移 8/8 测试绿）② 本方案+四工单落盘 ③ 审计发现六条登记（§3） | ✅ |
| 等施工队收工 | GPU-01 夜窗批接线（scripts/backtest 红线区）、GPU-02 Kronos 打分施工、晨报生成器施工 | ⏸ |
| Owner 门位 | ① 4 个测试遗留任务处置（§3-④）② CH-OptimizeMerge register ps1 化+任务名规范化（改活任务）③ RL 真训练 B-007 ④ 外网搜索 agent 启用 ⑤ F06Grid/C4Exam 同刻错窗处置 | ⏳ 待批 |

| # | 项 | 门位 | 建议时点 |
|---|----|------|---------|
| 1 | 4 个测试遗留任务处置（§3-④，每日白烧 CPU+Ollama） | Owner | 随时可裁，建议先裁（白烧最实） |
| 2 | F06Grid/C4Exam 周六 14:00 错窗（§3-①） | Owner/资源线 | 下周六 14:00 前 |
| 3 | CH-OptimizeMerge register ps1 化+任务名下划线规范化（§3-②治本） | Owner（改活任务） | 排班线收工后 |
| 4 | GPU-01 夜窗挖矿批接线+模型档位 A/B 定版 | 施工（等收工）+结果报备 | 红线解除后 |
| 5 | GPU-02 Kronos 批量推理打分（含预测表 DDL+B-007 消费门申请） | 施工+B-007 | 红线解除后 |
| 6 | GPU-03 SFT→GGUF 回灌链首跑（数据集核实+窗登记后可跑） | 中风险自动，窗冲突闸拦 | 随时（走闸） |
| 7 | GPU-04 RL trainer 施工+B-007 真训练审批 | B-007 | 排期后 |
| 8 | 外网论文/策略搜索 agent 启用（外呼边界） | Owner | 对话⑥收口时 |
| 9 | 全链晨报生成器施工 | 施工（低风险） | 红线解除后 |
| 10 | tilib 积压池排程化建议 | tilib 线 | 传值即可 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign/README.md`

| 战线 | 状态 | 下一步 |
|---|---|---|
| GPU 搜索 T1（3700 格全档门） | 🟢 **跑批中**（grid_20260924-213246，21:32 发车） | 预计周六 08:00-14:00 完 → T2 900 格自动接棒 |
| 裁定 #413 | ✅ 已注册+落队（q-0014） | 方案①列下窗口升级案 |
| 方法论总册十件 | ✅ 已落队（q-0013） | 按册消费进施工 |
| P1 三张条件概率表 | ⚪ 待开工（数据面已验） | GPU 跑批期间并行，详见 04 |
| AI 层 245 件落地 | ⏸ 等"队列畅通"广播 | 判据=E2E 完成+pending<5，本班守望 |
| 蒸发案 | ✅ 已破案+治本已批（EV-01~06 开工，EV-01 黑匣子先行） | 10 号文取证+15 号文治本方案 |
| 退役策略重考 | 📋 纪律已立+开工令已批（09-26） | 排 GPU 第一轮条件骨架之后；CPCV 框架 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/README.md`

| 战线 | 状态 | 下一步 |
|---|---|---|
| GPU 搜索 T1（3700 格全档门） | 🟢 **跑批中**（grid_20260924-213246，21:32 发车） | 预计周六 08:00-14:00 完 → T2 900 格自动接棒 |
| 裁定 #413 | ✅ 已注册+落队（q-0014） | 方案①列下窗口升级案 |
| 方法论总册十件 | ✅ 已落队（q-0013） | 按册消费进施工 |
| P1 三张条件概率表 | ⚪ 待开工（数据面已验） | GPU 跑批期间并行，详见 04 |
| AI 层 245 件落地 | ⏸ 等"队列畅通"广播 | 判据=E2E 完成+pending<5，本班守望 |
| 蒸发案 | ✅ 已破案+治本已批（EV-01~06 开工，EV-01 黑匣子先行） | 10 号文取证+15 号文治本方案 |
| 退役策略重考 | 📋 纪律已立+开工令已批（09-26） | 排 GPU 第一轮条件骨架之后；CPCV 框架 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/GPU_merge_audit.md`

| A 版原文行号 | A 版引文片段（摘） | 并入后的落位 |
|---|---|---|
| `gpu_landscape.md:16-20` | "qlib（microsoft/qlib）——MIT，活跃（pushed 2026-09-22，48.8k stars）…GPU 加速只覆盖 **ML 模型层**；回测面（Exchange 模拟＋`NestedExecutor` 日内→日间双层执行）是纯 CPU pandas…业界最主流的 AI 量化平台**选择不为回测核做 GPU**" | 表第 1 行（URL×2：GitHub＋官方 backtest 文档 `qlib.readthedocs.io/en/v0.5.1/component/backtest.html`；两版 stars 并列 48.8k／48,844） |
| `:22-26` | "hftbacktest（nkaz001，MIT，4.8k stars，pushed 2025-12-23）…实证三连：①README 全文 **271 行零 GPU/CUDA 字样**；②官方 'Accelerated Backtesting' 教程页 **233KB** 全文零 GPU/CUDA；③PyPI **v2.4.4 `requires_dist` 仅 `numba~=0.61`**…真正的强项：**L2/L3 tick 级全订单簿重建＋限价单排队位＋延迟建模**" | 表第 2 行（三连细证逐字入格；docs URL 保留） |
| `:28-32` | "vectorbt 开源版（polakowo/vectorbt，**自定义许可证 NOASSERTION**，9.2k stars）：**Numba CPU JIT 加速，无 GPU**" | 表第 3 行（vectorbt.dev＋GitHub 双 URL；并注明 PRO 的 JAX 说已由 B 版 §四 更正1 降为待验证） |
| `:60` | "nautilus_trader/backtesting.py/**LEAN 均无 GPU 回测模块**（2026-09 搜索实证）" | 表第 4、5 行——**LEAN 行系本次新增（合并前五册零命中该词）**；nautilus 行注明 B 版 A2 取证更强（README 零 GPU/CUDA/RAPIDS＋官方 AI/ML out of scope） |
| `:64-70` | 裁定五条：理由2 "没有现成框架有 **GPU 回测核**（qlib/vectorbt/hftbacktest/nautilus/LEAN 五家实证全 CPU）——改造现成框架改造不出 GPU，只能改造出又一个 CPU 引擎"；理由5 许可证风险面（Spectre GPL-3.0 传染／vectorbt PRO 闭源付费／开源 vectorbt NOASSERTION／自研＋CuPy MIT＋numba BSD=干净） | 该节末"总结论（一句话）"＋许可证面依据段 |


---

## 来源（第二遍）：`docs/_working/finalclean2_campaign/wave3/25_wave3_drain_wedge_note.md`

| 面 | 读数 |
|---|---|
| `pending` | 44 袋；最老 **131.2 min**；最近写 1.3 min ⇒ 入队侧仍在活跃进料 |
| `processing` | **1 袋 = `q-20261012-st-gpuwo-20261011-0006`，已挂 133.2 min** |
| `done` | 746 袋；**最近写 7.6 min** ⇒ 排水并未全线停摆 |
| `dead` | 1,456 袋；最近写 18.1 min |
| `.git/index.lock` | **不存在**（非锁毒型卡位） |
| 活体排水工 | PowerShell `Get-CimInstance` 全表 grep `0006|drain|convoy|serializer|reconcile_launch`＝**零命中**，即无存活进程指向该袋 |
| 该袋字段 | 仅 `base_head/branch/created_at/files/meta/qid/session_id`，**无 `claimed_by/attempt/state/pid` 位**（袋体本身不带租约字段） |


---

## 来源（第二遍）：`docs/_working/finalclean2_campaign/wave3/26_wave3_reply_acceptance_and_broadcast.md`

**三条结论**：
1. 统筹"排水活着"＝**实测成立**（四批落地可数），本班原登记件的"非全局楔死"判断也成立；
2. 但**卡位是真实的、且换人了**：首测时占位的是 GPU 工单班 0006，复测时占位的是**死信四班 0016**（不是 0013，且其 `meta` 既非 stale 也无 `dead_reason`，mtime 就是它的 `created_at`）⇒ 该面**确有一枚被取入 processing 后 3 小时无活体消费者**（03:35 `Get-CimInstance` 全表 grep `drain|convoy|serializer|reconcile_launch` 零命中），同时队列仍能推进他袋——**"有袋卡死"与"链在推进"并存**，这正是失败形态与正常形态同形的又一例；
3. ⚑ **顺带查到一件要紧事（他班资产，本班不代修）**：`gpuwo-0006` 已进 `dead/`，死因＝**`COMMIT_FAILED`→`GATE-PRECOMMIT-RUN` ruff `I001` import block un-sorted**，落点 `tests/research/backtest/test_kronos_score_only.py:23`。该袋 9 件未落地。在册处方明确"**`RUFF-PRECLEAN` 可在入队前自跑**"（`python -m ruff format <files>` ＋用 `git diff dev` 证明没顺手重排他人行）⇒ 归 GPU 工单班自修重投；本班不 requeue、不改判据。


---

## 来源（第二遍）：`docs/_working/gpu_rewrite/industry_gpu_landscape.md`

| 家 | 仓库／发布方 | 许可证 | stars | 活跃度（访问／pushed） | GPU 覆盖到哪一层（该版实证） | URL |
|---|---|---|---|---|---|---|
| **qlib** | microsoft/qlib | **MIT** | 48.8k（前一轮四舍五入口径）／本文 A1 实取 48,844 | pushed **2026-09-22**，GitHub API 2026-09-25 | **回测面无 GPU**：GPU 只覆盖 **ML 模型层**（PyTorch 训练/推理）；回测面＝`Exchange` 模拟＋`NestedExecutor` 日内→日间双层执行，纯 CPU pandas（`qlib/backtest/executor.py`）。前一轮原话："业界最主流的 AI 量化平台**选择不为回测核做 GPU**——这本身就是一个答案" | https://github.com/microsoft/qlib ＋ [官方 backtest 文档](https://qlib.readthedocs.io/en/v0.5.1/component/backtest.html)（Order Executor/Exchange 分层） |
| **hftbacktest** | nkaz001/hftbacktest | **MIT** | 4.8k／本文 A4 实取 4,777 | pushed **2025-12-23** | **主线现状零 GPU**，前一轮实证三连（本表补齐本文 A4 的粗表述）：①**README 全文 271 行零 GPU/CUDA 字样**（GitHub API raw 2026-09-25 抓取 grep）；②官方 "Accelerated Backtesting" 教程页 **233KB 全文零 GPU/CUDA 字样**（curl 同日抓取 grep）；③**PyPI v2.4.4 `requires_dist` 仅 `numba~=0.61`（CPU JIT），无 cuda 依赖**（PyPI JSON API 实核）。v2.1.0 文档时代曾把 "GPU multi-asset" 列进 roadmap 方向，截至 v2.4.4 **未落主线**。**它真正的强项＝L2/L3 tick 级全订单簿重建＋限价单排队位＋延迟建模**（Python Numba JIT＋Rust 双实现） | https://github.com/nkaz001/hftbacktest ＋ [docs](https://hftbacktest.readthedocs.io/en/latest/) |
| **vectorbt**（开源版） | polakowo/vectorbt | **自定义许可证（GitHub API license 字段＝NOASSERTION）** | 9.2k／本文 A4 实取 9,180 | pushed **2026-09-17**，活跃 | **无 GPU**：加速路径＝**Numba CPU JIT**（前一轮原话"Numba CPU JIT 加速，无 GPU"）。PRO 版（闭源付费）的"GPU 路线＝JAX jitter"一说本文 §四 更正1 已复核失败降为待验证，两版一致不据此立项 | https://vectorbt.dev ＋ https://github.com/polakowo/vectorbt |
| **nautilus_trader** | nautechsystems/nautilus_trader | **LGPL-3.0** | 29,385（本文 A2 实取） | pushed **2026-09-25** | **无 GPU 回测模块**（前一轮 2026-09 搜索实证；本文 A2 取证更强：README 全文零 GPU/CUDA/RAPIDS 字样＋官方明示 AI/ML tooling out of scope） | https://github.com/nautechsystems/nautilus_trader |
| **LEAN** | QuantConnect/Lean | **两版均未实取许可证／stars／pushed → 标"待验证"，禁凭记忆补**（本车道禁 GPU 作业亦禁联网重采之外，此项属长尾复采义务，已登记） | 待验证 | 待验证 | **无 GPU 回测模块**（前一轮 `gpu_landscape.md` §一.7 与 nautilus／backtesting.py 同批搜索实证结论） | 前一轮来源清单未列 LEAN URL → 本表不补 URL（缺证即标缺证） |

1. **"vectorbt PRO 的 GPU 路线=换 JIT 后端到 JAX"** —— 本轮直取 [Performance 页](https://vectorbt.pro/features/performance/)（2026-09-25）只看到 NumPy/Numba/Rust 三后端，检索具名短语亦未命中官方页 → **改判：待验证（不入图）**。影响：③文 L2 载体推荐不再引用 vectorbt PRO 作为"JAX 回测可行"的背书。
2. **"QuantPits = GPU 暴力组合回测"** —— GitHub API 实取描述无 GPU 字样、17 stars、许可证 NOASSERTION → **改判：仅登记边界，不采**。
3. **受阻记录（不编造替代引用）**：①[blogs.nvidia.cn 宽邦科技 RAPIDS 案例](https://blogs.nvidia.cn/blog/kuanbang-technology-accelerating-ai-with-nvidia-rapids/) 取回 404（原搜索快照命中、正式链接失效）→ 商业 A 股 GPU 实践这一脉**本窗口受阻**，只留 PyQuant News（C2）与 cuDF 官方页（C1）；②`rapidsai/cudf` releases 页经代理取回 403；③Polars 官方 GPU 用户指南页 `docs.pola.rs/user-guide/gpu/` 404（README 表述已足够，标单源→待验证其"限制清单"细节）；④中文 A 股回测性能/掩码文章全部落在 CSDN/聚合站与营销号，按闸1 一律不采。
4. **单源结论登记**：NVIDIA B4 的 "114x（一个月时间跨度，H200）"与"路径并行×时间串行几何"目前**只有 1 个一手来源** → 状态=待验证，只可作"量级参照"，不可作收益承诺依据（⑤文 N4/Phase 4 立项线已按此约束写）。

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 开源框架是否已有 GPU 回测核 | signal | 结论 A（4 来源）＋qlib exchange.py 的 `limit_threshold` 实源码核 |
| R2 | GPU/CPU 数值等价与确定性公开口径 | signal | 结论 B（4 来源，含 2026-03-05 CCCL 新文与 v13.4 CUDA FP 文档） |
| R3 | 数据面 GPU 收益带与 OS 可行域 | signal | 结论 C（cuDF/PyQuant 9x；RAPIDS 不支持原生 Windows；CuPy 支持 Windows） |
| R4 | A 股特有约束的外部同题文献 | signal | arXiv:2507.07107（2025）51x + 不可成交掩码为主因——**本轮最有价值单条** |
| R5 | 前一轮引文复核（vectorbt PRO JAX / QuantPits） | signal（否定性） | §四 更正1/2：一条降"待验证"、一条改判"不采" |
| R6 | 商业机构 A 股 GPU 实践 | 受阻 | NVIDIA 中文博客 404 + cudf releases 403 → 如实记录，不用聚合站凑数 |
| R7 | JAX/taichi 作为回测载体 | 待验证 | 本窗口未取到一手合格来源 → 不入图（前一轮断言降级） |
| 长尾 | 未挖 | — | ①NVIDIA 之外（AMD ROCm）GPU 回测生态；②RAPIDS 在 WSL2 下与本项目 ClickHouse(HyperV VM) 共存可行性实测（涉 GPU 作业，T1 独占期内禁做）；③Spectre 之外 GPL 因子库扫描 |

---
ttl: task_bound
title: LANE-GPU② 业界 GPU 回测／向量化方案全景（全网实查，含对前一轮结论的更正）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
evidence_grade: A-（外部论断逐条带 URL+发布方+年份+访问日期；未复核项一律标"待验证"不入图；搜索受阻如实记"受阻"）
supersedes: docs/_working/gpu_rewrite/gpu_landscape.md（同名义前一轮产物；本轮新增 4 条结论级来源并更正其 2 条未能复核的引文；2026-09-26 双版合并：前一轮**逐家实证表**（含 LEAN 与 URL/stars/许可证/hftbacktest 三连细证）已补入本文 §一「结论 A 补」，取代关系自此为实）
---

| 件 | 许可证/stars/pushed | 与本项目关系 | 评级 |
|---|---|---|---|
| [Heerozh/spectre](https://github.com/Heerozh/spectre) | **GPL-3.0** / 826 / 2025-04-15（休眠） | PyTorch+CUDA 因子引擎＋组合回测；README 实测口径：Quandl 5 年 3,196 标的 3,637,344 bar，i9-7900X + RTX 3090/2080 Ti，vs zipline.pipeline **最高 77.7x**（多指标 rank 组合）；自述"normally using float32 for GPU performance"并警告全 bar 一次算=**look-ahead bias 风险需自带测试** | 仅借鉴思想（**GPL 传染=禁采码**；float32 与本项目对拍纪律冲突；数据源 QuandlLoader 停更） |
| [microsoft/qlib](https://github.com/microsoft/qlib) | MIT / 48,844 / 2026-09-22 | A 股友好（`limit_threshold`、T+1 式撮合语义在 exchange 层）；回测核 CPU | 参考架构（其数据面板/工作流/成本与换手约束建模方式对③文掩码语义对拍有用） |
| [nkaz001/hftbacktest](https://github.com/nkaz001/hftbacktest) | MIT / 4,777 / 2025-12-23 | L2/L3 订单簿重放＋排队位＋延迟建模，Numba/Rust CPU | 直接用（但对象=未来 tick 回放语义对表，非本战役 GPU 重写；本仓 L07 SKEL §5 已采其语义） |
| [rapidsai/cudf](https://github.com/rapidsai/cudf) | Apache-2.0 / 9,763 / 2026-09-25（极活跃） | 数据面 GPU 首库；**Windows 原生不可用** | 参考架构（若未来经 WSL2/Linux 侧车，可承接"掩码构建=join/比较"的 GPU 化） |
| [cupy/cupy](https://github.com/cupy/cupy) | MIT / 12,343 / 2026-09-23 | NumPy 直译 GPU，Windows 有二进制 | **直接用（L2 首选载体）** |
| [numba/numba](https://github.com/numba/numba) | BSD-2-Clause / 11,160 / 2026-09-24（本仓已装） | `@cuda.jit` 核 + CPU 同源语义；NVIDIA 交易模拟文（B4）即用此路径 | 直接用（kernel 载体候选，**未在本机实跑 GPU——T1 单卡独占**） |
| [pola-rs/polars](https://github.com/pola-rs/polars) | MIT / 39,858 / 2026-09-25（本仓已装 1.41.2，20 线程） | 本机实测对同形面板工作负载**不优于 pandas**（0.43s vs 0.35s，见①文 R5） | 不采（作为本热点的解法被实测否定） |
| [nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | **LGPL-3.0** / 29,385 / 2026-09-25 | 事件驱动生产引擎，零 GPU | 参考架构（口径真源候选，非加速候选） |
| [DarkLink/QuantPits](https://github.com/DarkLink/QuantPits) | NOASSERTION / **17 stars** / 2026-09-12 | API 实取描述="An advanced, production-ready quantitative trading system built on top of Micros…"（**并非"GPU 暴力组合回测"**） | 待验证→仅登记边界（前一轮描述有误，见 §四 更正2） |


---

## 来源（第二遍）：`docs/_working/gpufeed_campaign/00_gpufeed_report.md`

- **M-7（预签② 第二句命中，10 格并列/离散放大）**：证据=§十一·C 逐表（七元组齐 5 位，hs300/zz500 的宇宙规模本批未取数＝缺 1 位，如实标缺不补猜）
  ＋族签名与 §二·补 第 5 条已具名族完全一致。可选处置：①按 §二·补 第 5 条标 `tie_amplified_selection` 另判、不挂红线（**本班建议**，理由=同款形态已有 Owner 亲批先例，且甲条五项 0 越线）；
  ②判实现缺陷要修（代价=要先造出能区分"1-ULP 放大"与"实现缺陷"的新尺，现无）；③给离散选择放大单独立线（属判据面新增）。不回话的后果=这 10 格挂着"未过"，级 4 不能判全绿。
- **M-1′（B2 靶二次改写＋两格可选动作）**：A＝只做规模化认证（n=1,050 底尺＋单价曲线），缺省仍关，B2 视为"认证工程"；
  B＝认证后把 `--engine gpu` 纳入排产（改的是**生产缺省面**，属 Owner 门位，且需 `exclusive_group`/显存预算同时到位——后者正被 M-4 卡着）。
  本班建议 A（代价=今晚到明晚吞吐不动，但零生产风险），并**不自取 B**。
- **M-8（验收尺无判别力）**：`gpu_self_sm_pct` 心跳 60s 一拍，GPU 臂整批只 7 拍（4 拍有值），中位 2.5%/p90 5.8%/≥70% 占比 0/7 ⇒
  "批形下 ≥70% 的采样应出现"这条验收**现在测不到**（每拍 60s 内约 600 格、每格设备 ~2ms）。改拍（~2s）或改累计核时间/格＝**尺改动**，待裁，本班不改尺。
- **M-9（两把线并存）**：见第 11 项 ⚠ 行。待裁是否给"累计后净值面"一条自己的线；本班不动任何线值。
- **M-10（提交链楔死，归维护三班，本班只报数不动他人袋）**：`commit_queue.py health` 02:55 实测 `pending=46 / oldest_pending_hours=2.41 / oldest_processing_hours=2.44`，
  在 processing 的那袋属 `st-deadcure3b-chief-20261011`（8 件，created 00:29），lease holder pid=15100 `drain-active`。
  本班三袋（0006/0007/0008）排其后 ⇒ **若晨间包未落地，不是没写，是被这条楔住**；解除面=维护三班的队列存活处方（在册五查），非本班权限。
- **M-2 更新**：03 件 §十一（四数＋11 格表＋B2 预演三件读数）已写进车道，等 0006 落地后另袋投；本 00 件续段以**严格超集**重投并取代在飞 0007
  （同会话同件后袋效应，在册病案，逐字登记于此以免被读成"条目被吞"）。

- **M-1 刀二终态（本班按判据取"开"，若您要更保守可点关）**：两层证据都绿——段面/端到端/批形三层逐位＋全格集一臂一进程六对三档越线全 0；
  故本班让 `_PRE_RETS_ENABLED` 缺省 True（设备支路生效），手柄与 `rets_hit/put/mem_clear` 计数器在册，
  关闸回退命令＝`_c4_engine.set_pre_rets_enabled(False)`（一行，清缓存不留混态）。
  ⚠ 本班**不援引"PASS"去碰缺省引擎面**：`--engine gpu` 仍只认证不动缺省（晨裁② 一字未改），
  本刀生效面＝`engine=auto` 解析到设备的那条既有路（改动前后同路，只换实现与求值次数）。
  若您判"仍需第二班复核再开"，点关＝把上面那行置 False，接线与尺全部留着（沿用 §十三·补·补 的关闸法）。
- **M-2 GPU-01 档位 A/B 今晚为何没起**（两条都是实测，不是推演）：
  ①**分母为 0**——三指标里的"入考通过率"，其可考面现器为零：`docs/_working/examunlock_campaign/04_target_face_channel_census.yaml`
  第 7 行 `preregistered: 177`／第 13 行 `blocked_on_target_face: 118`／**第 14 行 `supported_today: 0`**（本班按 `git show dev:` 取字节后 grep 命中，非转述）；
  ②**夜窗装不下**——`config/gguf_vram_budget.yaml` 第 46–48 行 night 段 `inference_quota_gb: 4.0`，而三档最小者 qwen3:8b 在册 `vram_gb: 5.4`（第 57 行），14b 档 9.2（第 69–81 行）⇒ 必须走手动窗＋临时配额，
  而手动窗与本班的 GPU 全格集针/吞吐针互斥（单卡 `vram.concurrency: 1`，§一·补 硬件红线）。
  默认取向＝**待解锁班把 A 面打开、且排一个不与网格批争卡的手动窗**后由下一班跑；本班只交首夜读数＋这两条堵点的行号级证据。
  （若只要"产出量"单指标先跑，本班可做，但那是把三指标实验降成一指标——属改实验设计，不属本班自裁面。）
- **M-3 SM≥70% 线：本班按铁律④ 用逐进程真尺、不改拍重测后，"测不到"改判为"测得到且没达到"**（167/226 拍非空，中位 6–9%，≥70% 占比 0/167）。
  于是这道题从"尺有没有效"变成"要不要为达线改形态或改尺"：
  甲＝维持现尺现形态，接受逐格形态下 SM 就是个位数，**≥70% 这条验收线在网格批形下永久不可达**（它描述的是常驻大核形态）；
  乙＝改形态（N-1 批内并行），达线由占空比自然抬升，代价＝那是另一把刀、且归约序改动会重排 §十一·C 那 10 格；
  丙＝改尺（"累计核时间/格"替代瞬时 SM，或把拍从 1s 降到 ~2s），代价＝晨裁③ 明写"不改拍"，需您点头。
  默认取向＝**甲＋把 ≥70% 从验收线降为披露线**（本班不自裁降线）。
  ⚠ 另有一条归因边界须您或尺主班定性：CPU 臂也拿到 13 拍非空（紧接 GPU 臂之后的十几秒），
  ⇒ **"在不在计算表"不能当二值闸用**；本针未据此断言机制。
- **M-4 前班采样器键错位**（`b2_throughput_sm.py:61` 存 `r.get("sm_pct")`，而 `nvml_process_util()` 实测返回键是 `sm_util_pct`，无 `sm_pct`）
  ⇒ 其 `sm_unavailable` 恒等于总拍数，那句"171／87 枚采样命中 0 枚"**是尺的空读，不是现场事实**。
  本班已用对键复跑并三口径分计（总拍／在表／非空），数在 03 件 §十六·D②。
  待裁＝是否要求前班那两支依赖此数的在册结论做一次复核（本班只报复现，不改他人账）。
- **M-5 驻留收益构成改写**：刀二命中后核内**不再读 px** ⇒ §十二·B 给驻留定的价里"价格面板常驻"这一半被覆盖（掩码常驻＋权重驻留两半不受影响）。
  属读数不属裁决；请检验道在收网时按新构成重算，别拿旧表当上界。

- **三袋在飞**：`q-20261013-st-gpux4-20261013-0001`（刀一袋）＝processing；`-0002`（刀二＋验收）pending ahead=15；
  `-0003`（终袋＝红蓝对抗＋声明不变式＋自犯改实数）pending ahead=17。**0003 是同五件的严格超集**，按序落地即终态。
  队列合并器两次报"共享注册表路径不可信合并——拒绝压缩，两袋保留"⇒ **不存在同会话后袋静默取代前袋**那种风险。
- **claim held=5 未放**（`gpu_core.py`／`_c4_engine.py`／`test_gpu_core_parity.py`／03 件／00 件，
  均按**车道绝对路径** claim——相对路径会 0/8 零告警，在册病型）；**袋在飞禁放锁**。
  保活经 `register_heartbeat_keepalive` 复授至 **07:51**（reason 在册），心跳 daemon pid 见 `.runtime/sessions/st-gpux4-20261013/heartbeat.jsonl`。
- **落地只认字节**（`done` 计数与 `[enqueue]` 回显都不算证据）：

- **P-9（新，请统筹／维护线裁）＝接管命中面缺一条"落后件"识别腿**。
  这是什么：维护五班批①的剔除口径是"盘字节 == 落地面才移出命中面"，它按"只缩不扩"设计，本班不翻；
  但它**结构上看不见"车道面 ⊆ 落地面而字节不等"**——即死车道停在旧落地面、dev 之后被别的班往前推。
  为何要点头：后果不是一次性的，是**每班一撞**——本班 03 件撞死一袋，解完后 00 件立刻进面（因为本班 18:43 那＋101 行
  把 dev 推前了），下一班碰这两卷任意一卷还要再撞；GPU 战役的班账卷天生是追加型共享件，所以只会越来越密。
  不点会怎样：每班各自花一轮做"内容级取证＋对齐车道面＋单口刷新"（本班这一轮＝两针＋一次刷新＋四步口），
  并且每班都可能选错路（有人可能直接 `--resolve` 抹掉整条目可见性，或改判据白名单＝那才是事故）。
  本班建议形（**不实施一字**）＝加性判据：跟踪件若同时满足"`车道 HEAD 是 dev 祖先` ∧ `Counter(车道面)−Counter(dev 面) 行数＝0`"
  则同批移出命中面，条目里记 `excluded_lagging_behind_landing=n` 与原因串；
  必留反对照两支＝"真未落地件仍被拦"＋"车道 HEAD 非 dev 祖先时不移出"。成本＝台账收集口一次多重集运算（只对跟踪件）。
  本班已把 00 件那一枚也按同一四步口对齐了（同证：572 行、独有行数 0、dev 严格前缀），
  刷新受台账 600s 节流窗约束，本班不自造 `now` 绕窗。
  ⚠ **并且实测到这条病灶会来回翻**：本班 03 袋 19:17 落地（dev 2162→2684）后，
  11:22:51Z 那次刷新的读数就是"`00` 已移出命中面、**`03` 又回到命中面**"——
  两枚件随 dev 前推轮流进面，与本节 P-9 是同一条病；本班后续不再投 03 件，故不受它挡。
  **下一棒若见这两卷中任意一卷在某条命中面上，先按 §十七·M 的四条只读判据量它是落后件还是未落地件，再决定动哪一侧**
  （勿直接 `--resolve`：`--resolve` 是**整条目**终态，会把那 18 枚未跟踪目录的可见性一并抹掉）。
  另记一条副作用实测（不推定"字节未变"那种话）：本次刷新前后台账 open 行数 **185→185**，
  带最新 ts 的行**恰 1 枚**且 sid＝`st-gpux4-20261013`；期间新增的第 185 枚条目是 11:17:14Z 由别的写方生成的
  `st-condaxis-20261013`，与本班无关，本班未动它。

| # | 嫌疑 | 判定 | 证据 |
|---|------|------|------|
| 1 | CH N+1 往返 | 无罪（残余隐患在案） | 数据面整批一次（:1401/:1411/:1453/:1459）；循环内全带批级缓存。残余：掩码 CH 异常 fail-open 不落缓存（_c4_engine.py:483-485），CH 抖动会退化——本案无证据触发 |
| 2 | 每格 spawn | 无罪 | 每批 1 次 python（run_f06_grid.ps1:39）；循环同进程，零 subprocess/multiprocessing |
| 3 | 单线程编排串行化 | 有罪（放大器） | `for r in picked:` 严格串行（:1476）；单核吃满（cpu 93.2%）；GPU 单流阻塞提交+每格 D2H 收口 → util 28.59% |
| 4 | 同步写盘 | 计时无罪/可观测性有罪 | 四件套批末才写（:1685-1778）→16.7h 零 manifest 根因；循环内唯一写点=j_regime_schedule.csv |
| 5 | 无预取/缓存失效 | **主犯** | 批级预取齐备，但 combine_cache 预算 24M cells（:726）按 3.5M/条估算，全市场实际 ~10.2M/条 → 装 2 条；~168 prefix 交错访问 → 抖动。铁证=2202 miss≈格数 |

1. 台账修正建议：2fb2976b0d"死因未知/新失败形态"→"11:59:35 外部定点处决，高置信=夜矿续战班停批，证据链见本报告 §二"（裁定通道，adjudicator 署名随本 commit）。
2. backfix 交接：11:59:30-35 tick 已列入备选案卷；若其常驻审计排除夜矿班嫌疑，升格案 #11。
3. v3 设计输入：T2-D 多 worker 喂单 GPU 流；executor 增逐格时间戳日志（本班 stderr 无时间戳教训）。
4. 遗留：批A 真实均速 54-60s/格 vs 账面 44.8 的口径差，建议随 T1 标定以完整三元组回填修正（裁定通道）。


---

## 来源（第二遍）：`docs/_working/gpuwo_campaign/00_ledger.md`

- **G-1 GPU-03B 卡点走哪条**（证据＝09 册）：①册主车道出一个净增 8 行的投影 render 袋（今夜可解，最便宜）
  ②给 TRANSLATION-COVERAGE 的查询面加 PG 账本第三源（治本，先例＝CREATE-GUARD 已于 10-10 打过同一剂；
  动的是判官件，须治理车道）③继续等。默认推荐＝**①今夜先走、②立成治理续单**。
  另附赠一条卫生发现待判：账本里 6 条形如测试夹具的条目（degraded/layered/lying/new_mod/orphan/with_extras.py）
  在投影重打时会被一起带进 HEAD——清或留不由我判。
- **G-2 金标冻结**：04:00 后我出抽检包（≥50 条）＋扩充草稿；**Owner 抽检点头＝冻结线**，点头前我不冻结、不训。默认＝不动。
- **G-3 GPU-03 真训练按钮**：R-2② 已归档为"链在位、窗在位、按钮在 Owner"；`sft_authorization.txt` 旗在位待 Owner 落字。默认＝不跑。
- **G-4 B-007（RL 真训练＋执行侧消费接线）**：影子腿已能出可比重数（分歧率/成本差/完成率），真训练与接线仍等 Owner。默认＝不训不接。
- **G-5 机械四步的执行者**：计划任务注册×3＋资源册再生（必须主区根跑，车道跑＝丢 sch_* 假绿）＋冲突闸零红证明。
  默认＝**袋一落地我继续跑**；若我那时已停摆，下一班照 03 册 review_commands 逐条跑。
- **G-6 W-1 开不开**：今夜给的是覆盖率与可联比例两个数；数出来之前"档级重建 obs"不拍。默认＝不开（W-3 态）。
- **G-7 GPU-01 档位 A/B 首夜**：等 0006/0013 落地＋23:00 自然触发；本班不改 FactoryLaneC 任务本体（授权扩面只覆盖那两件）。默认＝只观察。
- **G-8 提交链吞吐**：03:0x 实测 pending=47、队头他班件已等 146 分钟、本班 8 袋全未落地。
  今夜所有代码成果的"落地面"都卡在这一个数上。若 Owner 要"今夜必上"，需给提速或加急通道——我不自裁动队列机制。
- **G-9 LaneC 时限**：批复要求 10-12（周一）20:00 前落地。修件在队 q-…-0008。
  若届时仍未落地，默认＝按 G-8 走加急；否则 20:00 那一夜仍会跑旧口径（可再产一夜假绿）。

- 落地速率实测（done/ 里 landed_at 聚合）：30 分钟 2 袋、3 小时 13 袋＝**4.33 袋/小时**、6 小时 4.83、24 小时 3.38。
- backlog：pending=55（03:26），最老 172 分钟，中位 94.6 分钟；83 分钟内从 40 涨到 55（他班入队速率≈净 +11/小时）。
- 按 FIFO×15 分钟/袋估我的 9 袋落地时刻：0008≈06:15、0009≈09:45、0011≈11:45、0012≈12:15、0013≈12:30、
  0014≈14:00、0015≈14:15、0017≈17:00、0018≈17:15。
  两条前提写明：①新袋进队尾不推挤我的位次；②带 `--priority` 的会插队 ⇒ 上表是无插队口径。
- 结论对两条时限的意义：**LaneC 修件赶得上周一 20:00**（估 06:15）；
  而"机械四步"依赖的 0012/0013 要中午才落 ⇒ 我醒来时点建不了表、注册不了任务，这不是我没做，是链速决定的。

- 6.4 那句"LaneC 修件按估 06:15 落地，赶得上周一 20:00"**作废**：它是按 4.33 笔/小时外推的健康态估计，
  而实测 03:2x 后 45 分钟落地 0 笔。楔死未解前，"赶得上"不成立，我先前据此给您的那条时限判断是错的。
- 6.5 三项实测不受影响（数字与产物都在盘上：冒烟 5/5、0.43 秒/标的、142MiB；
  execution_report 1 行＋档级 10 月 0 行；金标草稿 360 条＋抽检包 60 行）。
- 本班在队 10 袋：0008 0009 0011 0012 0013 0014 0015 0017 0018 0019（另有已死 0001 0002 0005 0006 按死因处置，0006 不重投）。
- 新增一条待裁 **G-14**：若楔死持续，"机械四步＋建表"应改为**下一班接手**而非本班收尾——
  这四步的前置是"件已在 HEAD"而不是"件已在队"。默认＝我不自行改令，等您或统筹一句话。


---

## 来源（第二遍）：`docs/_working/matrix_campaign/gpu_survey_v1.md`

1. 无本机 profiler 复测——耗时证据继承 archive hotspot_census，实跑可能漂移。
2. cupy 本机可用性未验证（纪律禁触发 import）；09-25 普查"未装"vs 09-30 L2 落地，状态未复核。
3. 3826 py 未全集扫描：ml_train/alt_data/nlp 大域只抽查。
4. 热度=静态证据，无 runtime 频次日志。
5. #2 假设计算主导，CH 读写占比未实测——IO 主导则 GPU 收益缩水（探针前置）。
6. #7/#9 无 import 消费方，GPU 先行=产能等接线，装配批不落地即空转。
7. Decimal 撮合"不可 GPU"是形态判断；float64 镜像双轨方案未展开（Owner 呈批级，只登记）。
8. bootstrap 对拍受 RNG 约束：索引注入法本身未试跑验证。
9. CPCV 判 C 锚在当前规模；万策略×千折需重评。
10. 指标册 143 列考试读表不计算——算力面在 CH 侧回填链，勿误记热度。
11. eval_prefix_equal_gpu 只覆盖 equal 合成；IC 加权/正交/lasso 长尾合成留 CPU（未盘新面）。
12. 本道只读：本册由总包落盘，token 随收割批登记。


---

## 来源（第二遍）：`docs/_working/night_sweep/ledgers_archive/00_orchestration.md`

> Owner 令：审计清单全部未完成项今晚开工；另有 4 个施工大队并发（实测=st-zc9 系活跃落地中 + GPU 队 st-gpu-conv2 袋在队 + chief7 尾袋在队）；数据库 CH 已复活（9000 OPEN 实测）。目标=全流通全链路打通+循环检查连零×2+红蓝对抗+端到端交付。


---

## 来源（第二遍）：`docs/_working/night_sweep/ledgers_archive/SW7_ledger.md`

- id: 卡2_GPU死袋代修归还原主
    verdict: CROSSCHECK-不触发
    detail: |
      原主已自救：dead q-20260929-st-gpu-conv2-20260928-0001（死因 BLUEPRINT-FORMAT，测试件头 module_id 用路径）
      → 原主 st-gpu-conv2-20260928 自行重投 conv3 袋（q-20260929-st-gpu-conv3-20260928-0001，04:51 在队 pending），
      测试件 blob 已换（295fe863→9011efa6），新头='# [BLUEPRINT] MOD-BT-233-T | docs/03_modules/_domain_backtest/blueprint.md' 合规格式。
      三件中另两件 blob 与死袋逐字节同（gpu_core.py 6c13ddc0/checklist b727c780）。代修协议不触发（修了必撞车），让路。
    evidence: "conv3 在队 blob 9011efa6f90c 首行核验 MOD- 前缀 ✓；避让图 GPU 领地零触碰"


---

## 来源（第二遍）：`docs/_working/night_sweep_20260929/00_orchestration.md`

> Owner 令：审计清单全部未完成项今晚开工；另有 4 个施工大队并发（实测=st-zc9 系活跃落地中 + GPU 队 st-gpu-conv2 袋在队 + chief7 尾袋在队）；数据库 CH 已复活（9000 OPEN 实测）。目标=全流通全链路打通+循环检查连零×2+红蓝对抗+端到端交付。

