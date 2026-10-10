---
ttl: task_bound
title: RX-A 交叉复挖车道台账（对 L1 板块层 / L4 持仓层已收口车道的 20% 复挖）
created: "2026-10-10"
sid: st-nightmine-20261010-RXA
lane: RX-A
campaign: NIGHTMINE-CAMPAIGN
---

# RX-A 交叉复挖台账

工作根=`D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。
被复挖车道台账=`L1_ledger.md`（entry_flow/L2 板块层 30 节点，自报 22 个 mined_out）、
`L4_ledger.md`（position_flow 18 节点，自报 8 个 mined_out / 10 个未封矿）。
方法论=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.7.0
（§2 六向、§3 枯竭结构判据、§5 防噪音四闸、§7.5 资产状态断言纪律）。
作业簿=`docs/_working/nightmine_campaign/01_mining_brief.md`（§二 可运行判据、§四 探针形）。

## 0. 复挖法与本车道立法

**漏矿的唯一合法来源=②向对表**：TDM 节点原文里写了、而对方已立卡的 hypothesis/pillars 未考的判据性陈述。
禁以"我觉得还能加一张"立项（=污染覆盖尺与 DSR 分母）。
每节点三步逐留痕：
① 读对方卡（hypothesis/pillars/data_binding/status）→ 列"已覆盖的判据性陈述"清单；
② 回 `config/trading_decision_map.yaml` 该节点**全字段**逐句对表 → 列"节点写了、卡没考"清单（净新增候选）；
③ 对方标 blocked_on_data/blocked_on_impl 的卡 → 独立复核阻塞判据（实测表覆盖 / 代码实读行号），可翻案。

三态结论口径（本车道只用这三个词）：
- `漏矿 N 张`：②向找到未覆盖判据陈述并落真卡；
- `复挖零新增（六向已尽，理由一句）`：②向对表全部命中已入卡陈述；
- `翻案`：③向实测证明对方 blocked 判据不成立（附命令原文+输出数字）。

**禁区遵守**：不改对方任何既有卡字节；不碰 `generated: true` 骨架件；不改 TDM/注册表/分数册；无 git 写操作；
不跑生成器。新卡 NN 一律接对方已用号段之后（ls 实扫最大值+1）。

## 1. 逐节点三态结论表（骨架，逐节点回填）

| node_id | 车道/自报态 | ①对方已覆盖陈述 | ②节点原文有卡未考陈述 | ③blocked 复核 | 三态结论 |
|---|---|---|---|---|---|
| TDM-E-L2-01 | L1 / mined_out（ablation/02 两路面 preregistered，四路全量面挂 blocked） | 四路子分等权 0.25 合成边际、clamp[0,100]、市场级调节 ±10 腿、fallback 归一化+degraded 标注、"等权先验待 IC 重校"的改权提案 | **两条**：①节点 2026-09-20 UP-4 段整条未考——"六指数（000001/000016/000300/000905/000852/399006）独立分位数回归（PIT q05/q50/q95），按预测收益-风险比排序出板块优先序列表（DAL-SECTOR-DIST/MOD-PA-023），作本节点强度分的排序叠加通道"（对方 §1 的①上游一句只写"四路子分+市场调节"，未读到本段；`algo_refs=[DAL-SECTOR-DIST]` 是该段的机读指纹）；②"总分**前 15%** 进候选池"这一择优阈值从未被当判据考（对方 secondary=秩持续性，非分位阈值剂量-响应） | 四路全量 blocked 的根因=成分口径⇒本车道 §2-P3 独立实测复证成立（as-of 2022-06-30 命中 0 行） | **漏矿 1 张**（`TDM-E-L2-01__ablation__03_六指数分布选优通道与候选池分位.yaml`；两陈述同一对象=候选池择优规则，故并为一卡多臂，不摊薄） |
| TDM-E-L2-02-1 | L1 / mined_out（calibration/02 preregistered） | 四象限位置/迁移方向对次日指数与"新进>持续"的单调预测力、RS/RRI 带宽=5 钉死、禁直读 sector_state.rrg_quadrant、迁移矩阵"纯描述性登记不做门柱" | **两条**：①节点 `invalidation` 原文="象限转移须连续 **2-3 日确认**，单日跳变不采信；transition 概率**<10% 异常路径加 1 日确认**"——对方把迁移面显式降为描述性登记，于是"要不要这道确认滤波"本身从未被考（这是节点对实现的一条硬约束，非扩档）；②`fallback` 原文="板块日K 不足 **62 日**（DualEma 最小数据量）→该板块不参与序列排名"——门槛的信息量从未被考（本车道实测：IS 内 <62 日者仅 8/729 codes，62-180 日 22 个，宇宙 266→677→728 在漂，见 §2-P6） | 该卡无 blocked 面；其"宇宙漂移"防护与本车道实测同向（对方用 sector_state 376→729，本车道用 880 日截面 266→677→728，两套独立口径都证宇宙在扩） | **漏矿 1 张**（`TDM-E-L2-02-1__ablation__03_象限迁移确认腿与稀有路径护栏.yaml`；②作为本卡的宇宙护栏柱并入，不另立薄卡） |
| TDM-E-L2-04 | L1 / mined_out（ablation/02 preregistered，梯队连击真口径挂 blocked 用代理） | 三态封闭判定（高潮≥90/连击≥2+Top2≥30%/混沌）、优先级顺序消融、"次日"时滞、熊段同号、梯队真口径缺席以代理并声明 | 对表结果=**无未考陈述**：decision_question 的五态（高潮/主线/分歧/派发/混沌）中"分歧/派发"二态由同车道近邻卡 `TDM-E-L2-04-1__calibration`（五态+调节分）覆盖，不属本节点漏矿；`fallback=null`、`module_mounts=[MOD-SIG-061]` 无判据性文字 | **梯队连击真口径的 blocked 判据：本车道独立复核=部分成立、须拆开表述**。实测（§2-P4/P5）：以 stk_limit×kline_daily 价格面重建"日频涨停家数/连板"成立——2026-09-01..04 自算 86/55/46/42 vs limit_up_pool 83/52/44/39（相对偏差 ≤3.6%）；历史抽查 2024-02-05 跌停 1526、2024-10-08 涨停 893 与公开行情史相符。⇒ "**市场级**连板梯队/涨停家数"自 2019-01-04 起可算（2015-2018 每年仅 ~240 symbols，广度面不可用），但本节点要的是"**板块内**行业内连板≥2 的家数"，需个股↔板块归属，而 §2-P3 实测 sector_constituent 的 valid_from 仅 2026-07-23..2026-10-01（6 个值）、as-of 2022-06-30 查询=0 行 0 symbols ⇒ 板块级仍不可算，**不改判**。对方 blocked 文案把"无封板时点"（真，日内时点仅 2026-09 起）与"时序不可判"（假，日频时序 2019 起可判）混谈，登记为文案精度问题而非判据错误 | **复挖零新增**（六向已尽：节点每条判据陈述或入本节点卡、或入近邻卡；blocked 判据经独立实测复证成立） |
| TDM-E-L2-06 | L1 / mined_out（ablation/02 preregistered 可考窗，长窗挂 blocked） | 层级隔离两字段、off/two_field_only/rank_override 三臂、"只调分不重排名"的 isolation_invariant（违反即判卡无效而非 fail）、乘数 10→+15%/6→+5%/<6→−10%、龙头字段降为单字段并声明 | 对表=**无未考陈述**：节点全字段仅一条判据陈述束（只传两字段+只调分不重排名+乘数封闭表），三条已逐一入卡（乘数档的响应曲线形状在同链 `TDM-E-L2-06-3__calibration__02`，不重复挖）；`data_refs=[]` 无自有数据面 | 长窗 blocked 根因=成分口径⇒ §2-P3 复证成立（个股↔板块映射无历史） | **复挖零新增**（六向已尽，节点唯一陈述束与乘数面分别由本卡+06-3 卡覆盖） |
| TDM-E-L2-09 | L1 / mined_out（calibration/02 密度 + 03 评级上调聚集，政策/事件文本腿挂 blocked） | 催化剂"关注度密度"与"评级方向共识"两腿、>95 分位透支反向腿、"加权 20% 幅度由响应曲线给出"、与 L2-09 同表一次读取的分工声明、DS-107 缺失降级未考但已在 note 声明 | **一条**：节点原文把催化剂分为**三类**——"政策（部委文件/产业规划）、业绩（行业龙头超预期）、事件（涨价/突破/签约）"。对方 02/03 两张卡都建在 `research_report`（卖方研报=关注度/评级代理）上，其 blocked 名单只登记了"政策/事件文本腿"，**"业绩超预期"整条腿既未入卡也未进 blocked 名单=漏登记**。本车道实测：`c3_fundamental.earnings_forecast` 125,582 行/1999-01-08..2026-07-03/5,707 symbols，`forecast_type` 十类（预增 34,846/略增 19,145/首亏 14,945/续亏 14,647/预减 14,343/扭亏 11,441/略减 9,027/续盈 5,563/不确定 1,569/其他 56），且带 `announce_date` 与 `first_announce_date` 双日期=PIT 可守；`express_report` 2005-01-08 起 28,708 行可作"兑现复核"辅轴 ⇒ 该腿有长史，不是无料 | 政策/事件文本腿 blocked 复证成立（§2-P2 news_data 2025 年仅 31,425 行=断供，与对方 P14 同数）；**但"催化剂类别覆盖"的完整性判据被推翻**：三类中有一类（业绩）可用自有长史表直接考，不需等文本/图谱补史 | **漏矿 1 张**（`TDM-E-L2-09__calibration__04_业绩预增催化剂腿.yaml`）+ **翻案（部分，针对"业绩腿无面可考"的隐含登记）** |
| TDM-E-L2-10 | L1 / mined_out 名义下实为 blocked_on_data（calibration/02 一卡挂 blocked，两腿均缺史） | 补涨驼峰（3-5 日峰位合取判据形）、"<20%"的截面化定义、胜率低于龙头+MAE 双条件、同题材腿与同链腿分列出数、龙头启动=强度榜 Top10 首日 | 对表候选=节点"龙头股**翻倍**后"这一触发口径与卡内"榜进 Top10 首日"不同。判定为**非漏矿**：对方已在 frozen_note 里显式声明口径替代（"<20% 的截面化定义，写死"），属"已登记的口径差异"而非"未考的判据陈述"；再建一卡将与既有卡同撞同一根因（板块/链条归属），只增加 DSR 分母不增加覆盖面。**建议（不改对方件）**：补史后以节点原文"翻倍(+100%)"触发重跑该卡，并把本条差异提请 TDM/考卷对齐 | blocked_on_data 两腿复证：成分口径无历史（§2-P3 实测）；图谱 ig_* 无 PIT 版本（依对方 P15 实测，本车道未重复打，属同一表族且结论与 §2-P3 的"快照表全部 2026 起"一致） | **复挖零新增**（六向已尽；口径差异已登记非漏矿，另立卡=凑数） |

| TDM-P-P1-02 | L4 / 自报收回封矿（threshold_delta 反馈环列长尾，见其 §2.1 补记） | ATR 带宽尺的单调/三档排序/缺失子样本单独披露（calibration/02）；abs 对称化案底双臂与告警膨胀（comparison/03，blocked_on_impl） | **两条**：①节点分级判据是**两把尺的合取**——"WATCH（**浮亏>3% 或**临近止损）/ MONITOR（**浮盈浮亏 3% 内**）/ HOLD（深度浮盈安全区）"，而对方两卡的 buckets 全是**纯 ATR 带宽**，盈亏百分比尺从未入任何判据面；②节点 `fallback`="**ATR 数据缺失→按盈亏百分比粗分级**"，对方只做了"缺失样本单独计数披露"，**没考这条降级路径本身可不可接受** | comparison/03 的 blocked_on_impl（缺双臂分级统计件）复核=成立；另正查 `position_triage.py`（L62-63/L148-149 实读，无 pnl/3% 常数）⇒ 节点这两句是"地图有、码内无"（§3-A2） | **漏矿 1 张**（`TDM-P-P1-02__calibration__04_盈亏百分比腿与ATR缺失降级.yaml`，含合取臂 vs 纯 ATR 臂边际柱 + fallback 可接受性柱） |
| TDM-P-P1-05 | L4 / 自报收回封矿（相关性扎堆帽列长尾 #4） | 三查逐一入卡：单票 cap 三档（comparison/02）、漂移带 25% vs 10% 口径冲突（comparison/03）、同题材>3 只帽（ablation/04 blocked_on_impl）、体检帽影子（shadow/05） | 对表=**无未考陈述**：`decision_question` 的"相关性扎堆"对方已自列长尾且判"与只数帽不同对象"正确⇒属"已登记未挖"，不是漏矿，本车道不代写他车道在途题以免虚增 DSR 分母 | ablation/04 的 blocked_on_impl 复核=成立（引擎确无只数帽 overlay）；**但复挖出两条对方未见的硬事实**：其 `risk_limit_refs` 带数值锚（RLM-CONCENTRATION-003=0.7 相关性敞口合并、-004=20.0 单板块上限）与 **industry_class 无历史 PIT**（§5①②） | **复挖零新增**（六向已尽；交付=长尾的数值锚 + 一条静默前视风险，非新卡） |
| TDM-P-P2-01 | L4 / **mined_out（自报封矿）** | 三道门逐腿开闭 + 两门互斥诊断 + 常数逐条实读（3% 振幅/0.3% 价差/0.15% 成本/前置率 0.30/30 对土规）+ DEVICE_INCOMPATIBLE 三态出口 | **一条**：节点 `invalidation`="**盘中转单边（跌停潮/板块崩塌）→当日做T资格全部作废**"=与准入门不同类的判据（事中撤权），对方六向①只读了 algo_note 那句三道门，**invalidation 整条未进任何臂**；`fallback`（成本模型不可用→人工判定）判"已查无"（live 运维面不可回测） | 依 §3 结构判据（六向须全部"已入卡/已查无"）**本节点未达⇒其"封矿"自报在本车道复核下不成立，改判未封矿**；跌停潮腿数据可得性由本车道独立实测成立（重建家数 vs limit_up_pool 偏差 ≤3.6%、IS 窗 ≥100 家日 38 日，§2-P4），板块崩塌腿 blocked_on_data 复证成立（§2-P3） | **漏矿 1 张**（`TDM-P-P2-01__comparison__03_盘中单边失效腿对照.yaml`；市场级跌停潮 preregistered，板块崩塌子腿卡内写死缺段） |
| TDM-P-P3-01 | L4 / 未封矿（③亲和度、④熔断两腿列长尾 #7） | ①红线腿双臂（comparison/02 blocked_on_impl：向下摊平无 mode）；②段权限腿（comparison/03 preregistered，六段样本先证 ignition=2 天） | **一条**：④"非熔断禁加期"未立卡且**三处实现口径互斥**（枚举真源 L1=日亏≥2% 禁加仓 vs 加仓码 _CIRCUIT_BAN_LEVELS={L2,L3,L4}≥4% vs TDM 文本 4% vs 止损引擎 daily_loss_limit=0.02）⇒"2%-4% 区间的加仓笔该不该禁"从未被考；③亲和度腿对表=**非漏矿**（节点无算法口径、全项目无计算件，真 blocked_on_impl，与对方判断一致，不另立薄卡） | **翻案（④腿不需施工）**：对方"层位映射未考"正确（X_breaker 状态量=回撤，:1204-1234 实读，不可当日亏替身，本车道不推翻），但其隐含"要施工才能分层出数"不成立——日亏序列可由既有 run 的 net_returns 派生（:1226-1229 同口径），分层正门 `condition_attribution.py:attribute_run` 对方在同一节点 03 卡已用过⇒装置已在可即考；comparison/02 的 blocked_on_impl 判据抽验成立（ramp_mode 合法值仍无向下档） | **漏矿 1 张**（`TDM-P-P3-01__comparison__04_日亏熔断禁加期分层对照.yaml`）+ **翻案 1 条** |

## 1b. 复挖附带发现（非卡、供总报告与纠偏）

1. **`risk_limit_refs` 里藏着未读的数值锚**（"节点全字段逐句对表"的直接收获；两条车道都没打开过 risk_limit_registry）：
   `docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml`
   - L1170 `RLM-CONCENTRATION-001`「不梭哈一只」`threshold_value: 0.10`（=引擎基线 cap10，与 TDM 的 20% 并存；对方已在 comparison/02 点出该冲突）
   - L1242 `RLM-CONCENTRATION-003`「相关性矩阵敞口合并」`threshold_value: 0.7`
     ⇒ 对方把"相关性扎堆帽"记为**无锚长尾**，注册册里其实有硬阈值（rho≥0.7 敞口合并），
     且该腿**不需板块归属**（个股收益相关矩阵，hfq 1990 起可算）⇒ 长尾解锁成本显著低于登记值，下一轮可直接立卡（本车道不代写）。
   - L1278 `RLM-CONCENTRATION-004`「单板块上限20%（风险预算+凯利）」`threshold_value: 20.0`
     ⇒ **第三种约束对象**（单板块合计权重帽）：既非单票 cap（已考）也非同题材只数帽（已立 blocked 卡），
     对方卡片与长尾清单均未提及；但补考前须先解决下述②的归属 PIT，否则一考即撞静默前视。
2. **潜在静默前视（本车道实测，波及 L4 以 industry_class 作历史归属的臂）**：
   `c1_market.industry_class` 列集含 `valid_from/valid_to/industry_level/industry_sw/industry_zsi` 看似 PIT 表，实测其
   `valid_from` **唯一年份=2026**（46,228 行/10,472 symbols/min=2026-08-03/valid_to 全空），as-of '2021-06-30' 条件查询=0 行
   ⇒ 是**当期快照**而非历史归属；而 `config/position_recipe_grid_schema.yaml:110-121` 的
   `industry_anchor.membership_table=c1_market.industry_class` 被回测引擎用于 IS 窗（2019-2023）的行业聚合类读数
   ⇒ 等于**用 2026 年快照给 2019 年持仓贴行业标签**。影响如实限定：一级行业跨年改写率低，但更名/重分类/新股三类会引入前视。
   对方 P1-05 卡 evidence 只登记了该表的"符号格式混用/坏行 1/冲突 1"质量画像，未登记"无历史 PIT"⇒ 建议凡以之为历史归属的臂加 as-of 折扣标注或改判 blocked_on_data（本车道不改他车道卡，仅登记）。
3. **L1 车道硬结论的一条例外边界**：L1 §7 结论①"板块层可考面上限=2021-08-02"对**以 880 为底座**的卡成立；
   TDM-E-L2-01 的 DAL-SECTOR-DIST 通道底座是 `kline_index` 六指数（交集 2010-06-01，实测 §2-P7）⇒ 该单腿可前推至 2013-01-04，
   不受 2021-08-02 约束。属车道级结论的**作用域限定**，不是推翻。
4. **连坐预防观察**：`git status --porcelain -- docs/03_modules/_domain_backtest/exam_cards` 实测 `M` 7 张**全在 entry_flow/L1**
   （TDM-E-L1-S0-1/S2 系列 calibration 卡），非本车道所改；本车道对他车道既有件的字节改动=**零**
   （Write 仅用于 6 张新卡路径，Edit 仅用于 RX_A_ledger.md 与本车道自己的新卡）。依根宪法 §3.4 只登记不代修。
5. **六向①的机械缺陷（建议升 SOP）**：L1 抽 6 中 3 出漏矿、L4 抽 4 中 3 出漏矿，**全部同一根因**——
   ①向"读 TDM 节点"实际只读了 `algo_note_zh`+`data_refs`，而 `invalidation`/`fallback`/`algo_refs`/`risk_limit_refs`
   四类字段里的判据陈述成批漏读（L2-01 UP-4 通道、L2-02-1 确认腿、L2-09 业绩腿、P1-02 盈亏尺+fallback、
   P2-01 invalidation、P3-01 ④腿口径，共 6 条）。⇒ 建议 mining_sop §2 把①向改为**八字段打勾清单**
   （algo_note_zh/decision_question/invalidation/fallback/data_refs/factor_refs/algo_refs/risk_limit_refs），逐字段"已入卡/已查无"才准封矿。

## 2. ③向阻塞判据独立复核日志（本车道命令原文+输出数字）

> 探针全部经 `scripts/backtest/fexam/ch_data.py`（HTTP 只读，禁裸 duckdb），工作根=工棚，执行于 2026-10-10。
> 临时件=`D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/rxa_dump.py`、`rxa_dump.txt`（节点原文全字段快照）。

- **P1 节点原文快照**：`config/trading_decision_map.yaml` → `nodes` 为 **list**（非 dict），
  取节点须按 `node_id` 建索引（本车道首跑即因 `nodes.get(t)` 抛 `AttributeError: 'list' object has no attribute 'get'` 而失败一次，
  修后 10 节点全采到；留痕=禁凭记忆读图的具体教训）。
- **P2 `news_data` 断供复证**：与对方 P14 同口径，2025 年行数显著低于邻年（对方实测 31,425 行）⇒ 政策/事件文本腿 blocked 成立。
- **P3 成分口径（本战役 L1 车道 8 张 blocked 卡的共同根因）独立复核=成立**：
  `SELECT name FROM system.columns WHERE database='c1_market' AND table='sector_constituent' GROUP BY name`
  → `valid_to, sector_name, data_source, ingest_ts, updated_at, update_date, stock_code, sector_code, valid_from, fetched_at`
  ⇒ 该表**有 PIT 列（valid_from/valid_to）**，这是"历史归属或可回放"的正查题眼，故必须实测其取值跨度而非停在 update_date：
  `SELECT min(valid_from),max(valid_from),min(valid_to),max(valid_to),uniqExact(valid_from) FROM c1_market.sector_constituent`
  → `2026-07-23 / 2026-10-01 / \N / \N / 6`
  `SELECT count(), uniqExact(stock_code), uniqExact(sector_code) FROM c1_market.sector_constituent WHERE valid_from<='2022-06-30' AND (valid_to>='2022-06-30' OR valid_to IS NULL)`
  → `0 / 0 / 0`
  ⇒ **PIT 列存在但无历史值**（valid_from 全部落在 2026-07-23 之后）⇒ as-of 回放到 2022 得 0 行。
  对方"缺 2021-08-02..2026-07-21 板块成分口径"判据**经独立复核成立，不翻案**。
- **P3b 行业归属另一候选源=`industry_class`（对方 §3-P7 只测了首末日，未测 PIT 列）=同样不可回放**：
  列集含 `valid_from/valid_to/industry_sw/industry_zsi/industry_level/symbol_canonical`；
  `SELECT toYear(valid_from) y, count(), uniqExact(symbol), min(valid_from), max(valid_to) FROM c1_market.industry_class GROUP BY y`
  → 唯一行 `2026 / 46228 / 10472 / 2026-08-03 / \N`；
  `SELECT count(), uniqExact(symbol) FROM c1_market.industry_class WHERE valid_from<='2021-06-30' AND valid_to>='2021-06-30'` → `0 / 0`
  ⇒ 行业归属**两个候选源都无历史 PIT** ⇒ 板块级聚合类读数的 blocked 根因经两条独立路径复证（对方结论可信度↑）。
  附带发现：`industry_class` 有 `industry_level`=1/2/3 三层（各 ~10471 symbols）与 `industry_sw`+`industry_zsi` 两套口径列，
  对方 §5 长尾 #2/#10（口径对卡）之"三套行业口径映射未做"缺口在本车道实测下更具体：**三层×两口径×无历史**，
  对卡义务在补史时一并做，否则占比类读数分母族无法唯一。
- **P4 涨停/跌停日频时序可重建（对 L1 "涨停时序不可判"文案的精度校正）**：
  列集 `stk_limit`：`symbol, board, st_flag, exchange, limit_up, limit_down, limit_pct, pre_close, valid_from, valid_to, trade_date, symbol_canonical`
  ⇒ **per-trade_date 的 limit_up/limit_down 在册**（不是只有 PIT 区间），故"哪天收盘涨停/跌停"日频可判。
  分年密度：`SELECT toYear(trade_date) y, count(), uniqExact(symbol) FROM c1_market.stk_limit GROUP BY y ORDER BY y`
  → `2015:56331/239 2016:56646/234 2017:57183/240 2018:57156/237 2019:886711/3770 2020:969361/4358 2021:1088470/4840 2022:1181713/5179 2023:1260985/5380 2024:1296931/5436 2025:1317121/5498 2026:1026164/5591`
  ⇒ **2015-2018 仅 ~240 symbols/年（广度面不可用），2019-01-04 起才是全市场**（3770→5591 扩张，宇宙漂移须进占比类卡的分母族）。
  校验（自算 vs 在册池，2026-09-01..04）：`kline_daily.close` 对 `stk_limit.limit_up/limit_down`（±0.011 容差，同 symbol+trade_date join）
  → 自算涨停 **86/55/46/42**，同期 `c1_market.limit_up_pool`（该表列含 `consec_limit/first_seal_time/last_seal_time/industry/limit_stat`）
  → 池 **83/52/44/39** ⇒ 最大绝对差 3 家/日、相对偏差 ≤3.6% ⇒ **重建口径validated**。
  历史极值抽查：`2024-02-05` 自算 涨停 20 / **跌停 1526**；`2024-10-08` 涨停 **893** / 跌停 12；`2020-09-30` 涨停 31 / 跌停 12（与公开行情史实相符）。
  IS 窗（2019-01-01..2023-12-31）跌停潮频次：`交易日 1214 / 跌停家数≥100 的日 38 / ≥300 的日 7 / ≥500 的日 3`
  ⇒ "盘中转单边（跌停潮）"腿**样本门可满足**（≥100 档 38 日），这是本车道 TDM-P-P2-01 新卡的数据依据。
- **P5 `limit_up_pool` 列含 `industry`**（板块级连板在 2026-09 起的 28 日窗内可直接算）
  ⇒ 与对方 §3-P8（daban_engine_load 板块级涨停家数已采集 19 日）同向：补史起点候选多了一个表，
  但仍 <300 交易日地板 ⇒ 不翻案，登记为解锁成本进一步下降的证据。
- **P6 880 宇宙与热身门槛（进 TDM-E-L2-02-1 新卡的宇宙护栏柱）**：
  列集=`period, trade_date, timestamp, sector_code, sector_name, open, high, low, close, volume, amount, forward_factor, data_source, fetched_at, ingest_ts`
  ⇒ **键列=`sector_code`（不是 symbol/code）**；本车道首跑用 `symbol`/`code` 连错 5 次（网关以 HTTP 404 形式抛列不存在，
  依作业簿 §四"空结果先判静默失败"逐条排查后改对，留痕=404 不等于无数据，本例=列名错）。
  `countDistinct(sector_code) WHERE period='1d'` → `2021-08-02: 266 / 2023-12-29: 677 / 2026-10-08: 728`
  ⇒ 行业+概念族 IS 内宇宙 **+155%**（266→677），任何"占比/分位/家数阈值"类读数都须冻结分母族（对方 §0 立法据此，本车道独立复证且给出更陡的 880 面数字）；
  `<62 日`的 code 数（IS 内，trade_date≤2023-12-31）= **8**；62-180 日 = **22**；全 code 总数 = **729**
  ⇒ 节点 fallback 的"62 日 DualEma 最小数据量"门槛实践影响面=1.1% codes（可判但预期 no_binding，如实写成护栏柱而非主判据）。
- **P7 六指数覆盖（进 TDM-E-L2-01 新卡的 data_window_evidence）**：
  `SELECT symbol, min(trade_date), max(trade_date), count() FROM c1_market.kline_index WHERE symbol IN (...) GROUP BY symbol`
  → `000001 1990-12-19..2026-10-08/8738（实为 ..2026-10-09）`、`000016 2004-01-02../5527`、`000300 2005-01-04../5284`、
  `000852 2005-01-04../5284`、`000905 2007-01-15../4790`、`399006 2010-06-01../3970`
  ⇒ 六指数交集自 **2010-06-01** 起齐（最晚者 399006），叠件内 `train_window=500` 热身 ⇒ 分布通道臂可自 ~2012-07 起算，
  远早于 L1 全车道统一的 880 行业族 2021-08-02 上限（该上限只约束强度分腿，不约束分布腿）⇒ 本卡主窗与同车道对齐（2021-08-02 起），
  另设长窗副跑面（2013-01-04 起，仅分布通道单腿）——这是 L1 车道"板块层可考面上限=2021-08-02"硬结论的一条**例外边界**，
  须在总报告标注：该结论对"以 880 为底座"的卡成立，对"以 kline_index 指数族为底座"的卡不成立。
- **P8 业绩/预告与快报面在册（推翻 L2-09 业绩腿的隐含不可得判断）**：见 §1 表 L2-09 行数字原文
  （`earnings_forecast` 125582/1999-01-08..2026-07-03/5707 symbols/forecast_type 十类；`express_report` 28708/2005-01-08..2026-07-02）。
  样本行抽查（2024 年 4 行）显示 `profit_change_min/max`、`last_year_profit`、`reason`（全文变动原因）、
  `announce_date` 与 `first_announce_date` 分列 ⇒ 首次披露 PIT 可守、修订不外泄。
  行业聚合的映射源实测：`research_report` `uniqExact(symbol)=4709`、`uniqExact(industry)=207`、2017-01-02..2026-09-30/146940 行
  ⇒ 以"≤T 最近一次研报的 (symbol→industry)"构造 PIT 映射**可行但宇宙=研报覆盖 4709 只（偏机构票）**，
  故本车道新卡把市场级 series 定主轴、行业级定为"派生映射辅轴+宇宙偏差声明"，不冒充板块真口径（避触 L1 §0"裸扩口径=造回归"红线）。

## 3. 断言正查日志（mining_sop §7.5）

- **A0 工具不可用与降级阶梯（本车道独立实测）**：`python -m zephyr.library.lookup state "<关键词>"` 在工棚版
  实测**无 `state` 子命令**（依对方 L1 台账 §4-A0 同结论；本车道复核=直接跑 `state "熔断 加仓"` 一次，零输出，
  故不重复消耗）。降级手工阶梯（本车道实际使用）：
  ①`git ls-files | grep -i <关键词>` 定位件是否存在（用于 `ashare_stop_loss_engine.py`）；
  ②`git grep -n <常量/枚举名> -- src scripts` 读实码行号（用于 `_WATCH_ATR_MULTIPLIER`、`CircuitLevel`、`_apply_dd_breaker_overlay`、`MOD-PA-023`）；
  ③`system.columns/system.tables` 实测表/列在册性；
  ④`Glob/ls` 枚举 `exam_cards/**` 判"是否已做过同类卡"。⇒ 本台账所有"有/无"断言均带行号或实测数字，无凭记忆项。
- **A1「DAL-SECTOR-DIST / MOD-PA-023 无承载」= 负向断言证伪**（重要：若凭 TDM 只写"建议通道"就判未施工会错）：
  `git grep -ln "MOD-PA-023\|DAL-SECTOR-DIST" -- src scripts config` → `config/trading_decision_map.yaml`、
  **`src/zephyr/pf_alloc/core/sector_distribution_comparator.py`**；该件头注实读
  `# [MODULE] zephyr.pf_alloc.core.sector_distribution_comparator` / `[CONSUMERS] TDM 板块流（UP-4 分布比较选优）；策略工厂 E1D 车道`
  /`[INVARIANTS] PIT（特征 ≤T-1，预测 T+1）；板块=index（kline_index）`/`[STABILITY] experimental`/`[SAFETY] L`/`[TESTS] tests/pf_alloc/...`，
  且 `INDEX_POOL` 六指数与 `QUANTILES=(0.05,0.50,0.95)`、`FEATURE_LAGS=(1,5,10,20)`、`train_window=500/warmup=30` 逐值在册（L32-41、L54-55）
  ⇒ **通道已在码**，TDM 该段"（2026-09-20 UP-4 接线）"属实 ⇒ L2-01 该漏矿是可考面而非 blocked_on_impl。
- **A2「position_triage 有盈亏百分比尺」= 负向断言证伪（地图有、码内无）**：
  `grep -n "PCT|0.03|pnl|浮亏" src/zephyr/sell_decision/core/position_triage.py` → 仅
  `_WATCH_ATR_MULTIPLIER=1.5`(L62)、`_HOLD_ATR_MULTIPLIER=3.0`(L63)、`watch_abs/hold_abs ... - delta_abs`(L148-149)
  ⇒ 码内分级只有 ATR 一把尺 + delta 扣阈；TDM 本节点的"浮亏>3%/浮盈浮亏 3% 内"与 fallback"按盈亏百分比粗分级"**在码内无载体**
  ⇒ 该面既是漏矿（卡从未考）也是治理产出（地图承诺无实现），新卡按可算面 preregistered 并把"码内无该腿"写进 evidence。
- **A3「日亏熔断档=4% 才禁加仓」三处口径互斥（进 TDM-P-P3-01 新卡的剂量-响应双臂依据）**：
  ①`src/zephyr/position/core/defensive_asset_whitelist.py:54-61`（`class CircuitLevel`，真源声明=X-R1-01 drawdown_state_machine）：
  `L1 警戒（日亏≥2% **禁加仓**）`、`L2 禁开仓（日亏≥4%：白名单窄门开启）`、`L3 减仓（≥6%）`、`L4 保命（清仓+Owner 接管）`；
  ②`src/zephyr/position/core/pyramiding_rules.py:79-81` `_CIRCUIT_BAN_LEVELS={L2,L3,L4}`＋`:22` 注释"日亏 4% 熔断=L2 触发时全禁"
  ⇒ 加仓码把"禁加仓"挂在 **≥4%**；③TDM 本节点原文亦写"日亏 4% 熔断触发时全禁"；
  而枚举真源写 **2% 就禁加仓**；另 `src/zephyr/risk/core/ashare_stop_loss_engine.py:141` `daily_loss_limit: float = 0.02`（-2%）
  ⇒ **同一约束四处实现=2% 与 4% 并存**，"2%-4% 区间的加仓笔该不该禁"从未被任何卡面考过 ⇒ 净新增判据陈述，本车道立卡出数。
- **A4「X_breaker 可当禁加仓腿的替身」= 否定**（防误翻案）：实读 `factory_grid_executor.py:1204-1234`
  ⇒ `X_breaker=dd20` 的状态量是**组合权益回撤**（nav/cummax−1），帽带 NORMAL 1.0/WARN dd≤5% 0.75/DANGER≤10% 0.5/CRISIS≤15% 0.25/KILL≤kill_dd(0.20) 0，
  与 TDM ④腿的**日亏**熔断是不同状态量 ⇒ 不可等价顶替（对方"层位映射未考"的判断正确）。
  **但**其"需施工才能分层"的隐含前提不成立：日亏序列可由 run 产物 `net_returns` 直接派生
  （引擎同口径写法实读 `:1226-1229` `port=(weights.shift(1)*rets).sum(axis=1)`），
  而分层归因正门 `scripts/backtest/condition_attribution.py:attribute_run` 接受任意条件包（date/cell_id/cell_eligible），
  **对方在同一节点 TDM-P-P3-01/comparison/03 已用过该正门**做情绪段分层 ⇒ 装置已在，无需新件=**翻案（施工判据→可即考）**。
- **A5「L4 的 blocked_on_impl 卡判据是否成立」抽验**：
  `factory_grid_executor.py:839-841` 实读 → `breaker_mode=v.get("X_breaker","off")` 且 `if breaker_mode != "off": weights,_=_apply_dd_breaker_overlay(...)`
  ⇒ 熔断维**已接线**（与对方台账 §一"已接线"结论一致，无异议）；
  对方 P3-01/comparison/02 标 blocked_on_impl 的理由=B 臂（向下摊平）无 mode ⇒ 本车道未推翻（`ramp_mode` 合法值仍为 lump/linear_20d/linear_60d/pyramid），
  **仅推翻同一节点 ④腿"需施工"的隐含判断**（见 A4）。


## 4. 收尾（三态计数与枯竭判据可信度）

- **复挖节点数=10**（L1×6：TDM-E-L2-01/02-1/04/06/09/10；L4×4：TDM-P-P1-02/P1-05/P2-01/P3-01），全部走完三步。
- **三态计数**：
  | 态 | 节点数 | 名单 |
  |---|---|---|
  | 漏矿 | **6** | TDM-E-L2-01、TDM-E-L2-02-1、TDM-E-L2-09、TDM-P-P1-02、TDM-P-P2-01、TDM-P-P3-01（各 1 张，共 **6 张新卡**） |
  | 复挖零新增 | **4** | TDM-E-L2-04、TDM-E-L2-06、TDM-E-L2-10、TDM-P-P1-05 |
  | 翻案 | **2 条** | ①L2-09 业绩腿"仅剩研报代理可考"→实测有 `earnings_forecast` 1999 起 125,582 行自有长史 PIT 面；②P3-01 ④腿"需施工才能分层"→装置已在（condition_attribution 正门对方自己用过+日亏序列可从 run 派生） |
  | blocked 判据复证（不改判） | 5 处 | 成分口径（两源独立复证均无历史 PIT）、news_data 2025 断供、只数帽 overlay 缺件、向下摊平无 mode、X_breaker 不可当日亏替身 |
  10=6+4 全覆盖，无悬置。
- **新卡清单（NN 均接对方已用号段之后；机检=本车道实跑 yaml.safe_load 6/6 可解析、必填面齐、problems: 0）**：
  1. `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-01__ablation__03_六指数分布选优通道与候选池分位.yaml`
  2. `.../entry_flow/L2/TDM-E-L2-02-1__ablation__03_象限迁移确认腿与稀有路径护栏.yaml`
  3. `.../entry_flow/L2/TDM-E-L2-09__calibration__04_业绩预增催化剂腿.yaml`
  4. `.../position_flow/P1/TDM-P-P1-02__calibration__04_盈亏百分比腿与ATR缺失降级.yaml`
  5. `.../position_flow/P2/TDM-P-P2-01__comparison__03_盘中单边失效腿对照.yaml`
  6. `.../position_flow/P3/TDM-P-P3-01__comparison__04_日亏熔断禁加期分层对照.yaml`
  族分布=ablation 2 / calibration 3 / comparison 1；status 全 `preregistered`
  （L2-09 卡的行业辅轴、P2-01 卡的板块崩塌子腿各自在卡内明列 blocked_on_data 缺段，不作主轴）。
- **一句判断：L1 的枯竭判据"方向可信、判据有系统性侧盲区"**。
  可信面=其根因级结论（个股↔板块归属无历史 PIT）被本车道**两条独立路径复证**（sector_constituent valid_from 仅 6 个值、
  as-of 2022=0 行；industry_class valid_from 全部 2026-08-03、as-of 2021=0 行），8 张 blocked_on_data 无一被推翻；
  盲区=六向①实际只读了 `algo_note_zh`+`data_refs`，`invalidation`/`fallback`/`algo_refs` 里的判据陈述成批漏读
  （抽 6 个 mined_out 就有 3 个出漏矿）⇒ 按其同样方法全量抽查，"22 个 mined_out"预计还会再掉若干；
  建议把"①向须按八类字段逐字段打勾（algo_note/decision_question/data_refs/factor_refs/algo_refs/invalidation/fallback/risk_limit_refs+module_mounts）"
  升为 mining_sop 的机械步骤（本车道两次翻案与 6 张漏矿全部来自这一条）。
- **一句判断：L4 的枯竭判据更可信**。抽 4 个节点里 3 个出漏矿，但**真正"误封"只有 TDM-P-P2-01 一个**
  （P1-02/P1-05/P3-01 对方已自报收回封矿并列了长尾，属诚实登记）；其 11 条 blocked_on_impl 抽验 3 条**全部成立、无一翻案**
  （向下摊平无 mode、只数帽无 overlay、X_breaker 已接线），唯一翻案是其"④腿需施工"的隐含判断。
- **禁区遵守自证**：未跑生成器、未做任何 git 写操作、未改 TDM/注册表/分数册/他车道卡；
  临时件全部在 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/`（rxa_dump.py、rxa_dump.txt、fix.txt、三个探针 .py 由本车道另存）；
  CH 读取全部经 `scripts/backtest/fexam/ch_data.py`（禁裸 duckdb 遵守），404/500 失败逐条留痕并按"空结果先判静默失败"排查
  ——本车道 404 的三类真实原因：kline_sector_880 键列是 `sector_code`（误用 symbol/code）、
  earnings 表日期列是 `announce_date`（误用 publish_date）、网关拒某些子查询 HAVING 形（改条件查询绕开），
  **无一条被判成"数据不存在"**。

