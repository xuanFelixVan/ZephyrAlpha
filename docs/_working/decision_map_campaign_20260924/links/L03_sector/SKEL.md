---
ttl: task_bound
title: L03 板块状态与轮动·挖干作业簿（环节3 八子块六向台账）
created: 2026-09-25
sid: st-mining-L03-20260925
lane: decision_map_campaign
status: SEALED（6/8 子块封矿；B4/B5 MINING 见 §9；禁 commit；CREATE-GUARD 由总指挥统一登记）
doc_version: v1.0
mining_sources: 09_link_skeletons.md §环节3；docs/_working/sector_line/ 全目录 14 件；src/zephyr/signal_ashare/sector/ 18 文件头+CONSUMERS；src/zephyr/data/sector_state_pipeline.py；config/sector_attribute_labels.yaml；config/trading_decision_map.yaml:545-1393；12 号文 DU-01/02；04 号文+data/strategy_intake/conditional_tables/（v1 已交付实测）；22_sector_rotation_spec.md；wiring_proposals_L2_sector_gate.md；ruling_registry.yaml（至裁定#413）
---

# L03 · 板块状态与轮动——挖干作业簿

> **一句话总判定**：本环节是九环节中**唯一"供料端已上线、消费端全悬空"的环节**——sector_state
> 985 日 42.6 万行在产、两调度槽在 HEAD、供料 API 实测全绿，但①L2 门消费端 HEAD 仍是 v1 absent
> stub（比"恒 not_evaluated"更早一态：not_evaluated 版从未进 git）②动量主判 S10=NO_EDGE 使
> 五成分中第一成分的"强弱排序"消费口径失效③宇宙缺 881 行业族 260 板（35.8%）致全链产出
> 坐标系偏航。**薄在集成不薄在原料**的盘点结论成立，且供料端已由 09-23/24 两班补齐——
> 剩余工程全部集中在"接线+追认+补采+重考"四类。

## §0 子块全树（8 子块）

```
L03 板块状态与轮动
├─ B1 板块指数族数据底座（880 主供 / 881 缺席 / intraday 真值腿）      [SEALED]
│   └─ 算法层 17 件 src/zephyr/signal_ashare/sector/（B4 详列）
├─ B2 sector_state + sector_preference 状态输出层（五成分+回放 985 日） [SEALED]
├─ B3 板块资金维（sector_fund_flow 短史 + money_flow×成分聚合主路径）   [SEALED]
├─ B4 板块轮动序列（22 号 L2-02：RRG 四象限/5 状态/电风扇/龙头梯队）    [MINING]
├─ B5 拥挤度·估值·景气标尺（G14 三标尺升维原料，在库未入骨架）          [MINING]
├─ B6 S66 L2 门三原料供料与接线（top/retained/score→daily_gate_snapshot）[SEALED]
├─ B7 sector_constituent SCD-2 成分映射（聚合上溯的枢纽轴）             [SEALED]
└─ B8 P1 板块×相位条件表（T1/T2/T3 v1 已交付 09-24）                    [SEALED]
```

与 TDM/骨架对位：TDM-E-L2-01～05（config/trading_decision_map.yaml:545-1393）+ SKL2（30 节点
1 接电/28 覆盖未接电，audit §二）+ BM-SEL-08/09/10；升格独立层定桩 2026-09-22，边界追认 G9
未落（ruling_registry 至 #413 无板块升格条目——grep "升格"仅 #41x 无关命中，本簿实测）。

---

## §1 B1 板块指数族数据底座

- **①上游输入**：tqcenter 唯一活采集腿（mootdx ext 已死，data_sources_registry 实测注记
  2026-07-22；tdx 免费行情协议栈 09-10 起系统性死亡=MORNING_REPORT §二.2）；tqcenter 自动
  16:30 槽（tasks.yaml:2374 kline_sector_880_incremental）。
- **②数据原料**：c1_market.kline_sector_880 **437,204 行/469 码/2020-03-17→09-24 当日到**
  （12 号文行 52）；kline_sector 78,785 行/596 码——**128 个 881 行业族日线本体在此表活着**
  （594/日满量，tasks.yaml:947-955）；kline_sector_intraday 真值腿判死+synth 补齐
  （09-11→09-22 连续，data_source='synth_sh'）；sector_snapshot 596 码 A 态；sector_meta
  90 行业；sector_code_name_map 469 行。**881 族在 880 表 0 行，缺 260 板（727 真值−469，
  35.8%）**（12 号文 DU-01）。
- **③状态输出**：无（纯底座）；唯一下游可见产物=名称映射 sector_code_name_map（生成器 07:16 日更）。
- **④下游消费**：sector_momentum/sector_rrg 的 q3/q5/q20 与 RS 序列（sector_state_aggregator.py
  面板 SQL）；sector_state_pipeline._PANEL_SQL；P1 表 _cache_880.parquet；S10/D2/v2 三代考试
  面板；dashboard 表字典（盘点册 §12.3）。
- **⑤自动化挂点**：kline_sector_880_incremental 16:30 在产满量 468/日；kline_sector_incremental
  594/日（09-15 串行错峰修 tqcenter SDK 单例竞争）；kline_sector_1min_incremental 在册在调
  零产（真值腿死，req_sentinel_02 待裁）。
- **⑥缺口债**：**DU-01**（881 族 0 行，补采=capability 扩面+名称映射扩族，非从零挖源）、
  **DU-02**（sector_state/name_map/constituent 同源 881 缺席连带）、G2 残段（分钟真值腿收口）、
  G5（469/596/90/499 四坐标系未裁定）。881 补采待办早在 config/sector_attribute_labels.yaml
  头注登记（"TDX 可用时补采 881xxx"），07 号文行 33 已立卡"GPU 后首批数据施工"。

## §2 B2 sector_state + sector_preference 状态输出层

- **①上游输入**：kline_sector_880（75 交易日回看窗）、limit_up_pool×成分、money_flow×成分、
  regime_state_anchored（偏好第一轴）、emotion_index（偏好第二轴，真值 v0.1.0 自 09-15）、
  index_kline（盘前窗）——sector_state_pipeline.py:61-70 表注册全列。
- **②数据原料**：算法层 sector_state_aggregator.py（AGGREGATOR_VERSION=0.1.0 纯函数零 IO，
  算法全指认 22 号 spec §3.1①④⑧⑨）+ 编排层 src/zephyr/data/sector_state_pipeline.py
  （MATURITY=testing，:1-26 头注 stage 契约+防循环红线+幂等）+ DDL
  schemas/categories/sector_state+sector_preference。**存量：回放后 425,787 行/985 日**
  （statreplay/replay_report.md，968/968 零失败，880 链 hash 对拍两轮 MATCH）。
- **③状态输出**：c1_market.sector_state 每板块每日五行（momentum_pct/rrg_quadrant/strength/
  net_inflow_pct/rotation_state）+观察列 capital_score/watch_score+components JSON 逐成分
  status；c1_market.sector_preference（preference_label 5 档+tilt 0.8~1.2+banned_quadrant+
  emotion_version 追溯列）。NULL 普查：capital_score 100% NULL、strength/net_inflow 早期
  原料缺、momentum_pct 仅 2,175 NULL（replay_report §回放后普查）。
- **④下游消费**：load_l2_admission（本管道 :571，**写好但全仓零消费方**——grep 实证仅
  sector_state_pipeline 自身）；condition_package.py:20,190（板块腿 observational-only 禁入
  统计判据）；GPU 输入包 grid_gpu_sectorcond_20260924-0834（momentum_pct/rrg_quadrant/
  watch_score/is_holdout 四 .npy）；G05 选股链=待。考试判定后果（exam report §判档后果）：
  momentum_pct 排 Top-N 消费口径未获支持、preference_label/tilt 不作权重输入、
  banned_quadrant 保留保守过滤——**两表继续产数（事实记录+集成验证）**。
- **⑤自动化挂点**：**在产**——scheduler.py:438-458 特殊双槽 sector_close_final（15:10）/
  sector_pre_open（09:15）已进 HEAD（schedule.yaml:258-268）；总闸
  data/runtime/sector_state_pipeline.disabled 未挂=启用态（本簿 ls 实测）。
- **⑥缺口债**：**LK-03**（S10 NO_EDGE 后有效成分集未定，调权=下轮新卡）、D2 双轴主判悬于
  情绪真值窗 ≥120 日（约 2027-03，v2 卡 §0 一次性考完）、run_pre_open 不可历史驱动
  （dossier §3 T1）、state_vocabulary_registry 未登记 sector stage 四态且未进 git
  （dossier §4①——词表先行受阻项）、回放行与未来回补同键"后写者胜"残留风险（dossier §5）。

## §3 B3 板块资金维（sector_fund_flow）

- **①上游输入**：东财 fflow 行业资金流（implementations/sector_fund_flow_collector.py）；
  money_flow 个股五层净流入（tushare 腿，A 态）。
- **②数据原料**：c1_market.sector_fund_flow 90 行业（09-15 开采，改判 **B=在产+短史**，
  350-450 行/日，盘点册 §12.5）；c1_market.money_flow 5,579 股 2026-06-01→（A）；
  market_fund_flow_daily 09-18 东财 CDN 掐灭→hybrid 回填（data_source='em_fflow_hybrid'，
  MORNING_REPORT 批 0b）。
- **③状态输出**：sector_state.net_inflow_pct 截面分位（percentile_ranks 通用归一）；
  capital_score（资金性质分，**活表从未落值**，dossier §1 NULL 普查）。
- **④下游消费**：sector_state 聚合第五成分；无独立下游（HHI/集中度历史分位因短史受限）。
- **⑤自动化挂点**：sector_fund_flow 日槽在产（盘点册 §12.2 产奶量表）；聚合路径在
  close_final 槽内。
- **⑥缺口债**：**G7 双轨已部分执行**（增补令 c14ac74c7e7：close_final 回补 09-01→09-21
  15 日×469 板全成功）；深度实测硬约束=成分 valid_from 2026-07-23 起/涨停池 09-01 起——
  07-23→08-31 窗涨停池缺史按禁硬凑不补（等回源后下轮新卡）；**"个股聚合≈大盘资金流"
  假设已证伪**（money_flow 与东财大盘口径不同源不同众，MORNING_REPORT §二.4②）；
  东财字段面 CDN 级掐灭为持续性外部风险。

## §4 B4 板块轮动序列（22 号 spec L2-02 族）

- **①上游输入**：kline_sector_880 日K 序列（RRG 需 ≥62 日）、板块内涨停/梯队截面、
  market-level 领涨史。
- **②数据原料**（模块族，全部在盘）：sector_rrg.py（DualEma 10/26 四象限+whipsaw 连续 2 日
  确认）、sector_rotation_state.py（5 状态+HHI+watch_score）、sector_divergence.py
  （电风扇速度计 rotation_velocity>75 分位+5 状态+CONSENSUS_CLIMAX，1141 行）、
  sector_momentum.py（q3/q5/q20=0.4/0.3/0.3）、sector_momentum_persistence.py、
  sector_leader.py（龙头/中军/跟风）、sector_siphon.py（HHI 虹吸）、sector_analyzer.py
  （六方法，MATURITY=production）。P1-T2 辅表=相位内 top quintile 持续性/换手率（04 号文 §一）。
- **③状态输出**：rrg_quadrant/rotation_state/watch_score（经 B2 落库）；rs_ratio/rs_z
  （防御/进攻族相对强度，sector_divergence.py:257-258，族归属=config/
  sector_attribute_labels.yaml，881 族成分等权聚合口径）。
- **④下游消费**：**唯一实证生产接线=src/zephyr/plan_engine/boundary_revision_engine.py**
  （:92 import SectorDivergenceResult、:139 TRIGGER_SECTOR_TOP_RISK、:338/424-439 电风扇
  >75 分位降档，缺注入=skipped 降级如实）；sector_rotation_score_mapping.py（象限→score，
  头注"待 G06 板块轮动定型后接线"，当前 sector_overlay_active=False 不参与打分）；BM-SEL-08
  无生产触发面。
- **⑤自动化挂点**：缺位——轮动序列无独立产槽（仅随 close_final 槽间接出数）；
  TDM-E-L2-02 节点无 module 接电。
- **⑥缺口债**：G5（坐标系——RRG/动量全按 880 宇宙，881 行业维轮动态从未产出）、
  G9（升格边界追认：22 号 spec:26,60 "板块=特征非独立层" vs Owner-Max 独立层定桩，
  两真源打架中）、G13（ETF 载体执行，待 S10/D2 出档后议）、龙头领先偏差登记
  （外部方法论册 #17："龙头早于概念指数"）。

## §5 B5 拥挤度·估值·景气标尺（G14 三标尺升维）

- **①上游输入**：stock_daily_basic 7.1M 行（换手/量→拥挤度原料）、analyst_forecast 104k
  （景气维）、dragon_tiger_seat 618k 行 4.5 年深史+margin_trading+daily_valuation
  （资金维新增）、northbound_hold_snapshot（停 3 个月 C，北向披露规则调整同族风险）——
  盘点册 §12.1 反向扫描 7 张漏网原料表。
- **②数据原料**：全部**在库未入骨架**（G14：v0 保持五成分不动，预注册纪律）；
  config/sector_attribute_labels.yaml（防御/进攻族归属 0.1.0）已为此轴的板块族真源。
- **③状态输出**：无（未设计）。
- **④下游消费**：无；潜在=板块强弱复合打分替代失效的动量单尺（见 §11 标准件：外部复现
  实证"拥挤度是三标尺中唯一方向符合预期"）。
- **⑤自动化挂点**：无。
- **⑥缺口债**：G14（升维=下轮预注册新卡）、G15（图书馆别名轴+potential_consumers 维度——
  裁定#410 已批 potential_consumers 增枝 DDL 五步，板块 16 模块挂接走此通道）、
  S10-6.2 预承诺（动量腿禁本轮调权，改尺=新卡）。

## §6 B6 S66 L2 门三原料供料与接线

- **①上游输入**：c1_market.sector_state（pre_open 当日行）→ sector_state_pipeline.
  load_l2_admission()（:571，fail-open 恒 absent 不炸门）。
- **②数据原料**：供料端**实测全绿**（batch2_consumer_wiring_patch.md §2：top=5 板/
  retained=294 板/score=57.0/pref=OFFENSIVE tilt=1.2，09-23）；sector_gate.py
  water_temp_response（5 档查表 :82-88）+admission_gate（三级放行 :117-150，v2.1
  0.60/0.80）+apply_rrg_filter（:153）——纯函数件零副作用；水温另一上游备选=
  daily_condition_sensor.py:45 WaterTempTier 五档（wiring_proposals §一 实证）。
- **③状态输出**：l2.gate_level=evaluated/not_evaluated+admission dict（top/retained/score/
  preference_label/tilt/banned_quadrant）。
- **④下游消费**：daily_gate_snapshot._collect_l2 → daily_decision_orchestrator._s3_gate_leg
  （:561-579）→ D2 降级矩阵。**现状与总表记载不同（本簿改判）**：主区 HEAD :156-162 仍是
  v1 硬编码 stub 恒 `{"status":"absent","error":"no_persisted_gate_state_v1"}`（9098c65245，
  09-17）；"恒 not_evaluated"是 09-23 观察到的**未提交水位桥 WIP** 的行为——该 WIP（+249 行）
  现既不在 HEAD、不在工作区（git status 干净）、也不在任何 stash（git stash list 空），
  其唯一 committing 路径是 secbuild 分支 ai/st-secbuild-20260923/sector-line-construction
  的 f44c1bfd742（18 件，merge 回 dev 被主区 gate 文件 WIP 阻断，MORNING_REPORT §七.1）。
  拍板行 degraded=D2_gate_absent:L2 的根因即此 stub（wiring_proposals §一）。
- **⑤自动化挂点**：缺位——补丁 ready_to_apply 未贴（batch2 patch 全文在
  docs/_working/sector_line/batch2_consumer_wiring_patch.md）；无任何事件/槽触发 l2 评门。
- **⑥缺口债**：**G4**（消费端接线，现拆两步：先落水位桥方案甲【Owner 已批，真源
  wiring_proposals_L2_sector_gate.md】再贴 batch2 五行补丁）、**G8**（阈值全 proposed：
  v2.1 0.60/0.80、水温响应、tilt 0.8~1.2——校准入口=考试制勿双轨）、S10 NO_EDGE 令
  "top=momentum Top-N、score=strength 归一"供料口径未获考试支持（score 成分集待 C06 重考）。

## §7 B7 sector_constituent SCD-2 成分映射

- **①上游输入**：同花顺/通达信成分采集（自动槽）。
- **②数据原料**：c1_market.sector_constituent FINAL 95,124 行/595 板块（880 族+881 行业 128 码，
  8803/8804 缺）；valid_from 2026-07-23 起 4 批次（07-23/07-28/08-01/09-03）；**valid_to
  95,124 行全 NULL**；现行快照 236,836 行（frozen §F.2）。概念轴：concept_board 375 概念→
  4,829 股 A 态（valid_from/valid_to 版本化，盘点册 §1）。
- **③状态输出**：as-of 成分集合（管道 _CONSTITUENT_SQL 真谓词：valid_from≤T AND
  (valid_to IS NULL OR valid_to>T)）。
- **④下游消费**：涨停比分母（sector_breadth）、money_flow 板块聚合上溯（22 号 spec §3.1⑥
  裁定主路径）、sector_state_pipeline 聚合、881 族归属真源（sector_attribute_labels.yaml
  实证：银行=881386 n=15、半导体=881319 n=182 等 7 板锚定）。
- **⑤自动化挂点**：采集在产；概念轴 concept_sector_refresh 在册（tasks.yaml:1033）。
- **⑥缺口债**：**非真 PIT 归属**——T≥2026-09-03 起 42 日内 constituent_count 重复计数
  （4 批次叠加，dossier §2 量化，缺陷归数据线）；8803/8804 缺（DU-02 连带）；
  **G12 硬 gate**：概念成分接口只回当前态无历史快照（外部方法论册 #27），启用概念轴前
  必须自建带时戳快照存档，否则=前视偏差回测虚高。

## §8 B8 P1 板块×相位条件表（消费端）

- **①上游输入**：regime_snapshot_history（3,629 日 PIT）→六段相位全史 v1（t0 班 0033 批
  物化 1,816 日/路由 1,054 日，r1/r2 不路由宁漏勿误）；kline_sector_880（2020-03 起）。
- **②数据原料**：**v1 已交付**（data/strategy_intake/conditional_tables/，09-24 23:50，
  本簿 ls+抽行实测）——T1 主表 p1_sector_by_phase.csv 469 板×6 相位=2,806 格（可考 1,837/
  不可考 969，每格 n/raw_win_rate/wilson_lb/mean_bp/分位/t_stat/exam_ok，MIN_OBS=30）；
  T2 p1_phase_momentum.csv（trailing20d×fwd5d 池化相关：**退潮/分化/亢奋=负=高低切结构，
  扩张/蓄积≈0**）；T3 p1_phase_transition.csv 36 行转移矩阵；p1_phase_stay.csv（expansion
  均值 8.8 日/euphoria 3.3 日）；p1_top5_by_phase.txt（排序只认 Wilson LB+exam_ok）。
  GPU 侧输入包 grid_gpu_sectorcond_20260924-0834 四通道已落盘。
- **③状态输出**：CSV+parquet 落 strategy_intake（未升 CH 表）；README.md 口径+重算命令齐备。
- **④下游消费**：GPU 网格条件轴（factory_grid_executor→condition_package）；BM-SEL-08
  轮动序列查询原料；22 号 spec 查询面；P1-T2 即轮动持续性查询表。
- **⑤自动化挂点**：缺位——重算脚本 .runtime/tmp/p1_conditional_tables.py 一次性
  （README 自述"长期重估再转正 scripts/"）。
- **⑥缺口债**：469 宇宙=881 缺席连带（DU-01 补后重跑即 **P1 v2**）；sector_name 全空
  （880 表该列为空串）；ignition 相位仅 1 路由日/euphoria 38 日稀薄；价格收益未扣成本
  （README 已注）；**产物登记图书馆资产（04 号文 §三.3 Librarian.act+potential_consumers）
  本簿未见落实证据**；T2 负相关与 S10 NO_EDGE 互证——"追强势板块"与"相位内动量延续"
  双双反向，高低切（反转）结构在 A 股板块层成立，是 v2 重考换尺的定量依据。

---

## §9 自审闸三态

| 子块 | 三态 | 依据/余留清单 |
|---|---|---|
| B1 指数族底座 | **SEALED** | 六向全填；指针全读；缺口全转施工项 C01/C04/C10 |
| B2 状态输出层 | **SEALED** | 含回放/考试/NULL 普查对表；余留=LK-03+C06 |
| B3 资金维 | **SEALED** | G7 增补令执行实录对表（c14ac74c7e7）；余留=C07 |
| B4 轮动序列族 | **MINING** | 余留未逐行对表清单：sector_divergence.py(1141 行)/sector_leader.py(614)/sector_momentum_persistence.py(360)/sector_analyzer.py(420)/sector_volume_anomaly.py(283)/sector_crowding_launch.py(296)/sector_detail_enricher.py(452)/sector_attribute_rules.py(273)——CONSUMERS 头与算法指认已核，公式级逐行对表未做 |
| B5 三标尺 | **MINING** | 原料四态已盘（盘点册 §12.1）；标尺算法定义未探（复现配方见外部方法论册 #9：拥挤度=换手/波动/beta 三比率 zscore，景气=财务 zscore 等权） |
| B6 L2 门 | **SEALED** | wiring_proposals+batch2 补丁+HEAD 实测三方对表；水位桥 WIP 下落已查证（不在 HEAD/工作区/stash） |
| B7 成分映射 | **SEALED** | dossier §2 缺陷量化+labels.yaml 锚定实证对表 |
| B8 P1 表 | **SEALED** | v1 产物落盘逐文件实测+README 对表 |

**总裁定：SEALED 6 / MINING 2 / BLOCKED 0。** 本簿封矿（B4/B5 余留已列清单，不阻断施工项
进入执行队列——README 挖干即开工条款）。红线遵守：S10/D2 判档数字逐位引自
exam/prereg_exam_results_v1.yaml；水位桥 WIP 下落为"未证实在何容器"如实表述，未断言丢失
（对照宪法 §2.8 stash 检查已做，stash 空）。

## §10 施工项（L03-C01 起；编号接续既有账本 DU/G/LK/req）

| # | 项 | 内容与替代声明 | 既有账本 |
|---|---|---|---|
| **L03-C01** | **881xxx 行业族补采工程** | tqcenter capability 扩面（881 族 128+8803/8804 号段入 kline_sector_880 清单）+sector_code_name_map 生成器扩族（tdxzs.cfg 132 条主数据派生）+历史 days=500→1000 回补（复用 09-11 配方，一次客户端会话）；完成后连带重跑 sector_state/sector_constituent 挂接。**净零声明：不新采源**（881 日线本体在 kline_sector 活着，缺的是 880 表通道与映射）；替代=消解 G5 四口径之一半 | DU-01/DU-02（07 号文行 33"GPU 后首批"） |
| **L03-C02** | **L2 门消费端接线（两步）** | 步1=水位桥方案甲落地（Owner 已批：`_collect_l2` 复用 L1 dominant→七键映射→water_temp_response 查表，零新表）；步2=贴 batch2_consumer_wiring_patch.md 五行（load_l2_admission 注入+编排器注记）。前置核实：水位桥 WIP 现不在主区（本簿 §6④），需先定位其容器（secbuild 分支或原会话）防双落。验收=collect_gate_snapshot l2.gate_level evaluated（sector_state 当日有 pre_open 行时） | G4/S66/D15 |
| **L03-C03** | **P1 v2 重跑升版** | 触发=C01 落地：881 行业族入宇宙重跑 T1/T2/T3；同时①补 sector_name（C01 连带）②产物登记图书馆资产 Librarian.act+potential_consumers（补 04 号文 §三.3 欠账）③重算脚本转正评估（.runtime/tmp→scripts/）④README 增 T2 高低切结构注记（与 S10 互证） | 04 号文 §四/P1 |
| **L03-C04** | 板块坐标系裁定页 | 一页裁定 469(880)/596(kline_sector)/90(sector_meta)/499(申万)+128(881 补采后) 口径：主口径=880+881（22 号 spec 公式全按 880xxx 定，扩 881 需声明）；其余登记映射或声明不消费；G12 概念轴硬 gate 同页重申 | G5 |
| **L03-C05** | G9 升格边界追认呈 Owner | 唯一硬呈报项：22 号 spec §2.3"板块=特征非独立层" vs 2026-09-22 独立层定桩——走裁定登记（RULE-RULING 同 commit 原子），spec 加升格注记或修订边界条目；追认前本环节按独立层走、属在途定桩 | G9 |
| **L03-C06** | v2 考试卡实跑判档 | 卡已冻结（statreplay/sector_prereg_exam_cards_v2_frozen.md，985 日窗+条件分解：轮动态分层后 Q5−Q1）；判档即解 LK-03"有效成分集未定"之半（另一半悬于情绪窗 D2 一次性重考）；多重检验族=v1 主判+本卡全量入台账 | LK-03/裁定#407 |
| **L03-C07** | 资金窗补批（下轮新卡） | 涨停池深史回源后补 07-23→08-31 窗 strength 维（禁硬凑纪律已留痕）；G7 选项表（短窗降档 vs money_flow 回溯）交 Owner 定案收口 | G7 |
| **L03-C08** | 板块资产 capability 挂接 | 16 模块+两表反查零在编（盘点册 §10 实测"编排器惨案"温床）；走裁定#410 已批 potential_consumers 增枝 DDL 五步通道+别名补 sector/板块/轮动/ETF/881 关键词；移交图书馆班执行、本线清单已备（盘点册 §7） | G6/G15/裁定#410 |
| **L03-C09** | 三标尺升维预注册新卡 | G14 v0.2 候选转正论证：动量单尺 NO_EDGE+T2 相位内动量负相关双重证据下，拥挤度标尺（外部复现唯一方向符合预期，§11-#7）+波动率缩放动量（§11-#9 Daniel-Moskowitz）为优先候选；启用前按考试制预注册新卡、禁复活 S10 | G14/S10-6.2 |
| **L03-C10** | 板块分钟真值腿收口 | req_sentinel_02 裁定二选一：tqcenter 1m/5m 盘中活体验证通过→tasks.yaml 5 分钟任务切源；否→synth_board_minute 供给常态化+正式停用 tdx 五盘中任务；board_index_tick（单日试点 C 态）一并处置 | G2 残段/req_sentinel_02/G10 边界 |

**施工项数：10。前 3 优先：C01（881 补采——Owner 已立卡、性价比最高、全链连带解锁）→
C02（L2 门接线——供料端已全绿只差 5 行+水位桥，接线即终结"门从未评过"）→
C06（v2 卡实跑——LK-03 解扣前置，卡已冻结零准备成本）。**

## §11 标准件（全网搜；接 README"不自造"纪律）

1. **JdK RS-Ratio/RS-Momentum 方法论（RRG 原厂）**：[StockCharts ChartSchool – RRG Relative Strength](https://chartschool.stockcharts.com)（JdK RS-Ratio=相对强度趋势、RS-Momentum=其加速度，四象限 Leading/Weakening/Lagging/Improving）；[RelativeRotationGraphs.com – Building Blocks for RRG](https://relativerotationgraphs.com)（作者 Julius de Kempenaer 官方拆解：RS 比值→平滑→归一化 100 轴）；[OpenBB – Building a Relative Rotation Graph](https://openbb.co)（Python 参考实现：price÷benchmark→动量平滑出双坐标）；[CMT Association 文章](https://cmtassociation.org)。**对表点**：本仓 sector_rrg.py 用 DualEma 10/26，JdK 原厂默认平滑窗与归一化基准不同——B4 逐行对表时须核对平滑器选型并留差异注记（不构成改参数理由，改=新卡）。
2. **板块轮动量化（最新/可复用）**：[Quantpedia – Sector Momentum Rotational System](https://quantpedia.com)（学术动量+相对强度+波动管理合成的动态板块轮动模板）；[SSGA – Sector ETF Momentum Map](https://ssga.com)（机构板块相对强度轮转可视化口径）；Meb Faber《Relative Strength Strategies for Investing》(2010, Cambria)——RS 策略风险调整改进的奠基实证；[LuxAlgo – Sector Momentum Rotation Explained (2025-03)](https://luxalgo.com)（排名期/持有期/再平衡频率三参数框架，最新 2025 级综述）。
3. **Momentum Crash 防护（S10 NO_EDGE 的对症药）**：Daniel & Moskowitz, "Momentum Crashes", JFE 2016（[NBER w20439](https://www.nber.org) / [Columbia PDF](https://business.columbia.edu) / [SSRN](https://papers.ssrn.com)）——动量崩溃可由市场波动率状态预测；constant-volatility 缩放动量 unconditional Sharpe 显著优于 1$-long/1$-short；dynamic momentum（按状态预测均值/方差调仓）更高。[Scientific Beta – Rebuilding Momentum and Managing Crash Risk](https://www.scientificbeta.com)（高波动期暴露缩放的工程化）；[Alpha Architect – Avoiding Momentum Crashes (2022)](https://alphaarchitect.com)（牛市定波动+崩溃态方差缩放双轨）。**接线建议**：C09 新卡设计直接内置"高波动/退潮相位动量降权"——P1-T2 实测退潮/分化/亢奋相位动量负相关（高低切）即该文献在 A 股板块层的同构证据。
4. **A 股卖方三标尺（拥挤度优先）**：国盛《行业轮动的三个标尺》（原报，搜索级；[知乎复现含诚实负结果](https://zhuanlan.zhihu.com/p/698648408)——复现结论"拥挤度是唯一方向符合预期的标尺、动量最小组合反而最好"）；华泰金工拥挤度体系（成交额占比/换手/波动/一致预期偏离，搜索级汇总）。与仓内 sector_external_methodology.md #9/#10 同源互补，不重复收录。
5. **开源可复用实现（许可待核，防 C3 型文档-代码不符须锚代码）**：[hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook)（100+ 券商金工研报复现，含海通 RRG 行业轮动/华福 NH-NL/华西量价轮动——外部方法论册 #5 已正文级核实；license 本簿未核验，采纳前须查）；[AdroitAnandAI/RRG-Sector-Rotation-India](https://github.com/AdroitAnandAI/RRG-Sector-Rotation-India)（RRG 计算+可视化参考，license 未核验）。README 要求标注许可证——两仓库许可证字段因搜索限流未能核到，登记为采纳入口的**前置核验项**（如实披露，未虚构）。

---

## §12 挖掘执行附记

- 本簿与总表（09_link_skeletons §环节3）的**三处增量改判**：①L2 门态"恒 not_evaluated"
  →实为 HEAD v1 absent stub（not_evaluated 版从未进 git，见 §6④）；②sector_state"回放
  985 日"→行数级对表 425,787 行+NULL 普查+对拍 hash 双 MATCH（§2）；③P1 表"09-25 交付中"
  →**v1 已交付**（09-24 23:50 落盘，逐文件实测，§8）。
- G3（daban 断供）已销口（总表 §8 汇总行同记）；G10 board_index_1m 已 DROP 执行
  （c14ac74c7e7），board_index_tick 维持 C 态待批（C10 一并处置）。
- 未重测数据面：全部行数/时戳引自 12 号文（09-24 探针）与 sector_line 各册实测，本簿
  零 DB 写、零重测（只读纪律）。
