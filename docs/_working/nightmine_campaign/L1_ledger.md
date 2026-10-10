---
ttl: task_bound
title: L1 挖矿车道台账——entry_flow/L2 板块层（30 节点）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L1-entry_flow-L2-sector
campaign: NIGHTMINE-CAMPAIGN
---

# L1 车道台账（板块层 30 节点）

工作根=`D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。共用作业簿=`docs/_working/nightmine_campaign/01_mining_brief.md`。
方法论真源=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.7.0（§2 六向、§3 枯竭结构判据、§5 四闸、§7.5 断言纪律）。
口径先例（必读复用）=`D:/ZephyrAlpha/docs/_working/matrix_campaign/mining/st_l2_sector_mining.md`、
`.../sector_propagation_wiring_v1.md`、`.../layered_spread_kernel_wiring_v1.md`、`.../m2_exit_sector/`。

## 0. 车道立法（本车道新增必填面与红线）

- 卡族分派判据（作业簿 §本车道特别注意）：板块强度/轮动/扩散/资金流入类**读数**→`calibration`
  （响应曲线+时滞+条件稳定性+目标双声明四件套）；把多信号**合成**为一个板块判断的环节→`ablation`。
- 板块口径数据面题眼（在册结论，禁凭记忆）：
  - `sector_constituent` 是三处采集宇宙的**唯一读取源** ⇒ 凡扩宇宙/换行业锚的卡，data 向须先核它。
  - 881/8803 板块指数深史真实上限=**2021-08-02** ⇒ 冻结窗需 2021 前板块数据的卡，
    `data_window_evidence` 必须实测登记覆盖窗+行数；不足即 `status: blocked_on_data` 并写死缺哪段。**裸扩口径=造回归，禁。**
- `data_binding` 段（signal_table/signal_column/signal_derivation/target_source/data_window_evidence）
  = 本战役必填面；写空=卡不可运行=废卡。
- 外部引用按**族级**挖一次跨节点复用（同题型不重复挖），每条须 URL+发布方+年份（闸1）；关键结论 ≥2 源（闸2）。

## 1. 台账总表（逐节点一行，机读优先）

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|
| TDM-E-L2 | ①上游=10 子环节+DS-059/DS-170 已入卡假设 ②下游=L3 个股层（`git grep` 见 §4-A3，X_sector 引擎 arm 已落）③算法=族 S1 整层消融先例（本仓 sector_propagation_wiring_v1）④后端=组骨架无 module_ref，引擎侧 MOD-BT-238 在岗 ⑤呈现=候选池排序列表，只登记 ⑥数据=880 行业指数 2021-08-02 起实测够窗 | 1 | ablation×1 | 已入卡+六向留痕，待 §5 长尾复核后封 | — |
| TDM-E-L2-01 | ①上游=四路子分+市场调节，四路中两路历史不可算 ②下游=L2-06 传导/L2-03 门控/L3 池（§4-A3）③算法=族 S1+S3 等权→IC 加权改权须先出分 ④后端=MOD-SIG-142/144+sector_surface.py 在岗 ⑤呈现=强度榜，只登记 ⑥数据=成分快照仅 6 个刷新日/涨停池仅 28 日⇒四路全量 blocked | 1 | ablation×1 | 部分（两路面已入卡；四路全量面挂 blocked） | 四路全量版缺 2019..2026-07 板块成分口径 |
| TDM-E-L2-01-1 | ①上游=涨停比/梯队/趋势三件（DS-059+DS-082）②下游=L2-01 四路之一 ③算法=族 S2 广度结构先例（Obrask/McClellan，见 §2-S2）④后端=sector_analyzer MOD-SIG-058/095/097/100/101/120 在岗 ⑤呈现=结构分 0-10，只登记 ⑥数据=stk_limit 2015+ 够、kline_daily_hfq 1990+ 够、成分口径 2026-07-22 起不够 | 1 | calibration×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：缺 2019-01-04..2026-07-21 板块成分口径 |
| TDM-E-L2-01-2 | ①上游=成交额占比+环比（DS-059/DS-170）②下游=L2-01 路 A+L2-04-2 虹吸共用同一 amount 面 ③算法=族 S1（量能活跃度）④后端=sector_ranking_engine 在岗（2026-09-18 去 abs 保符号修正已核）⑤呈现=活跃度榜 ⑥数据=880 amount 2021-08-02..2026-10-08 实测 78263+163038 行够窗 | 1 | calibration×1 | 已入卡 | — |
| TDM-E-L2-01-3 | ①上游=q3/q5/q20（DS-170）②下游=L2-01 路 B+L2-08 生命周期共用动量持续性 ③算法=族 S1 多周期动量 ④后端=sector_momentum 在岗 ⑤呈现=主导度标签 ⑥数据=同 880 close 面够；q20 预热 20 日已计入 | 1 | calibration×1 | 已入卡 | —（附带发现：节点文字与在码权重方向矛盾，登记不改 TDM） |
| TDM-E-L2-01-4 | ①上游=3 日累计净流入+当日大单（DS-181/DS-186）②下游=L2-01 路 D（权重 25%）③算法=族 S3 资金流预测力 ④后端=sector_breadth MOD-SIG-088 在岗 ⑤呈现=资金流分+degraded 标记 ⑥数据=个股 money_flow 2021+ 够、板块聚合需成分（2026-07-22 起 55 日）、直读 sector_fund_flow 仅 17 日 | 1 | calibration×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：缺 2021-08-02..2026-07-21 成分口径；直读路样本 17<300 地板 |
| TDM-E-L2-01-5 | ①上游=五态调节分+市场级底稿 ②下游=`git grep` 仅 generate_backtest_backlog.py 一处（下游=backlog 登记面，无实消费）③算法=族 S4 市场态调节 ④后端=market_forecast_fusion MOD-SIG-063/147 在岗（NaN/Inf fail-closed rpt_d04 已核）⑤呈现=调节后强度榜 ⑥数据=emotion_index 1991 起满史，880 底座 2021-08-02 起够窗 | 1 | ablation×1 | 已入卡 | — |
| TDM-E-L2-02 | ①上游=板块价+量移动方向（DS-170）②下游=`git grep` 零命中（除 TDM/骨架卡）⇒ 输出未接线，卡须自证方向对有效性 ③算法=族 S1 轮动 ④后端=sector_divergence 在岗（DEDUP→core/analysis_utils 已核）⑤呈现=接棒榜单 ⑥数据=amount 环比代"资金连进"已声明差异；"资金流"真口径 blocked（见 L2-01-4） | 1 | calibration×1 | 已入卡 | — |
| TDM-E-L2-02-1 | ①上游=板块相对基准 RS/RRI 双轴 ②下游=`git grep` 零命中 ③算法=族 S1 RRG 通行口径（带宽/平滑钉死）④后端=sector_rrg 在岗 ⑤呈现=旋转图四象限 ⑥数据=880 2021-08-02 起 + 000300 2005 起；sector_state.rrg_quadrant 仅作交叉核对（板块宇宙 376→729 在扩，防宇宙漂移冒充信号） | 1 | calibration×1 | 已入卡 | — |
| TDM-E-L2-02-2 | ①上游=RSI+量额+龙头破位三信号（DS-059）②下游=`git grep` 零命中（候选池降级动作未接线）③算法=族 S1 过热反转 ④后端=sector_analyzer MOD-SIG-119/121 在岗 ⑤呈现=见顶预警标记 ⑥数据=日频两信号可算（880 2021-08-02 起）；盘中面 blocked（kline_sector_intraday 仅 2026-07-20 起 ~55 日）；龙头维同成分根因 blocked | 1 | calibration×1 | 已入卡（两信号面），第三维挂 blocked | 盘中面+龙头破位维缺史 |
| TDM-E-L2-03 | ①上游=高点回撤+时间+扩散+量能（DS-170）②下游=`git grep` 命中 adjustment_cycle_tracker（本族两节点共件）③算法=族 S1/S5 调整节奏，倒 U 先验与在码 80% 门控对冲 ④后端=sector_adjustment 在岗（量能缩量维在 TDM 注明"待扩展"，本卡把它算出来）⑤呈现=进度百分比 ⑥数据=880 60 日高点窗够；DS-170 在册口径（2025-10-01 起）会致全窗不可考，改用 880 并登记口径矛盾 | 1 | calibration×1 | 已入卡 | 扩散维 0.3 权重不可算（重归一已声明） |
| TDM-E-L2-03-1 | ①上游=板块内个股 close vs SMA20（DS-170）②下游=L2-03 三维之一 ③算法=族 S2 McClellan/扩散族 ④后端=adjustment_cycle_tracker 在岗 ⑤呈现=进度百分比 ⑥数据=个股价格面 1990 起充分，成分面 2026-07-22 起 ⇒ 板块内扩散度不可算；市场级替代=不同对象，明禁顶替 | 1 | calibration×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：缺 2019-01-04..2026-07-21 板块成分口径 |
| TDM-E-L2-04 | ①上游=高潮分+梯队连击+Top2 集中度（DS-059/DS-170）②下游=`git grep` 命中 sector_ecology_judge/sector_strength_wiring/trading_day_cycle_map（消费=强度接线+日周期图）③算法=族 S4 市场生态阶段 ④后端=MOD-SIG-143 纯函数在岗 ⑤呈现=三态标签 ⑥数据=高潮分/成交额集中度可算（880 2021-08-02 起）；梯队连击真口径仅 2026-09-01 起（limit_up_pool 1426 行、daban_engine_load 19 日）⇒ 价格面代理并声明 | 1 | ablation×1 | 已入卡（代理面），梯队维挂 blocked | 梯队连击真口径缺史（..2026-08-31） |
| TDM-E-L2-04-1 | ①上游=强度截面方差+涨停集中度 ②下游=L2-01-5 注入（与本轮动共用一次重算）③算法=族 S4 状态分类 ④后端=sector_rotation_state 在岗（节点号 `git grep` 零命中）⑤呈现=五态+调节分 ⑥数据=方差/成交额集中度可算；涨停集中度需 limit_up_pool（2026-09-01 起）⇒ 成交额集中度替代并声明 | 1 | calibration×1 | 已入卡 | 涨停集中度真口径缺史（以成交额集中度代） |
| TDM-E-L2-04-2 | ①上游=前 3 板块成交占比（DS-059/DS-181）②下游=`git grep` 零命中（清空池动作未接线）③算法=族 S3/S4 集中度-虹吸 ④后端=sector_siphon MOD-SIG-113 在岗 ⑤呈现=虹吸态标记 ⑥数据=880 amount 2021-08-02 起满配，两腿利差可算；对板块宇宙数敏感⇒分母族已冻结 | 1 | calibration×1 | 已入卡 | — |
| TDM-E-L2-05 | ①上游=水温档+板块强度榜（DS-150）②下游=L2-05-2 三件套（开关的参数落点）③算法=族 S4 状态门控 ④后端=无 module_ref（red_reason=pending_gate），卡考开关存在性不考实现 ⑤呈现=放行比例表 ⑥数据=emotion_index 1991 起满史（逐年 237~257 行无断年）；盘前段仅 2026-09 起⇒以盘后面考并声明；sentiment_panel 仅 52 行不可用 | 1 | ablation×1 | 已入卡 | 盘前档面缺史（activation=premarket 与数据面矛盾，已登记） |
| TDM-E-L2-05-1 | ①上游=日级 S5 读数+月级 7 态（DS-150/DS-082/DS-059）②下游=L2-05/L2-05-2/L2-01-5 共用档序 ③算法=族 S4 水温响应曲线+封顶增益 ④后端=sentiment_cycle 在岗 ⑤呈现=最终档位 ⑥数据=emotion_index 8617 行满史、000300 月级 2005 起可聚合 | 1 | calibration×1 | 已入卡 | — |
| TDM-E-L2-05-2 | ①上游=水温档×强度×象限三件 ②下游=打分池（MOD-SIG-059/094/107/131 挂载）③算法=族 S4 状态→参数查表 ④后端=sector_gate 在岗 ⑤呈现=三件套取值 ⑥数据=TDM data_refs=[]⇒无自有数据面，全靠 880/emotion_index/kline_index 重算；象限真口径有 sector_state.rrg_quadrant（2022-09 起）但禁直读 | 1 | ablation×1 | 已入卡 | — |
| TDM-E-L2-06 | ①上游=板块强度调节分+龙头定位两字段 ②下游=L3 个股打分池（G05，sector_conduction 头注"待接线"在册）③算法=族 S5 层级隔离/叠加边际 ④后端=MOD-SIG-136 + 引擎 X_sector（MOD-BT-238）已在，真数 smoke 42 日×31 行业留档 ⑤呈现=调节后分 ⑥数据=成分映射仅 2026-07-22 起⇒长窗 blocked、可考窗 arm 对比 preregistered（两态并存如实登记） | 1 | ablation×1 | 已入卡（可考窗），长窗挂 blocked | 缺 2021-08-02..2026-07-21 个股↔板块成分 |
| TDM-E-L2-06-3 | ①上游=板块强度 10 分制×个股 score ②下游=combined 分值→Top-N（引擎 evaluate_recipe）③算法=族 S5 响应曲线/拐点错位检验（含节点两主张交叉项）④后端=MOD-SIG-136+sector_surface 查表；活体插值变体不同源已披露 ⑤呈现=乘数档 ⑥数据=880/000300/个股 hfq 三面对齐，唯成分映射 2026-07-22 起⇒长窗响应曲线 blocked | 2 | calibration×2 | 已入卡（02 阶梯形状+03 时滞曲线），长窗挂 blocked | 缺 2021-08-02..2026-07-21 成分口径（响应曲线长窗面） |
| TDM-E-L2-06-1 | ①上游=板块强度关+个股强度关+流动性关 ②下游=G05 打分池（先 gate 后 weight）③算法=族 S5 门槛边际/顺序信息量 ④后端=sector_gate MOD-SIG-104 + sector_surface 引擎侧（gate 三关单测逐值在册）⑤呈现=池成员标记 ⑥数据=关2/关3 全窗可算（个股 hfq 1990 起）、关1 需成分（2026-07-22 起）⇒ 双态登记 | 1 | ablation×1 | 已入卡（关2/3 长窗+三关可考窗），关1 长窗 blocked | 缺 2021-08-02..2026-07-21 成分口径（板块关） |
| TDM-E-L2-06-2 | ①上游=板块内涨停时序+市值+涨幅 ②下游=L2-06 两字段之一（龙头定位）+止损宽度分级 ③算法=族 S2 龙头/跟风结构（A 股特有）④后端=sector_leader 在岗（DEDUP→analysis_utils）⑤呈现=四态标签 ⑥数据=limit_up_pool 仅 2026-09-01 起 1426 行/28 日、daban_board_event 1767 行/28 日、daban_engine_load 19 日 ⇒ 四态×60 不可达 | 1 | calibration×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：缺 2019-01-04..2026-08-31 涨停时序（"最先涨停"不可判；stk_limit 价格面 2015 起够用但无封板时点） |
| TDM-E-L2-07 | ①上游=回踩分级+仓位映射 ②下游=L4 仓位分配（A 满额/B 半仓/C 观望）③算法=族 S6 离散化 vs 连续映射 ④后端=sector_pullback MOD-SIG-116 在岗（pullback_action 在码）⑤呈现=ABC 等级 ⑥数据=板块对象可算（880 OHLC+amount 2021-08-02 起），个股对象需成分（另属 L3，未越界） | 1 | ablation×1 | 已入卡 | — |
| TDM-E-L2-07-1 | ①上游=Fib/量能/强度/时间四因子 ②下游=L2-07 定级 ③算法=族 S6 Fib 买点+倒 U 时间窗 ④后端=sector_pullback 在岗，**在码三维 vs 地图四维（缺时间窗）口径不一致已登记** ⑤呈现=四因子 0-1 分 ⑥数据=880 OHLC 满配；宇宙漂移防护=冻结 industry_l1∪industry_ths(189 codes) | 1 | calibration×1 | 已入卡 | —（实现/地图口径矛盾登记给施工侧） |
| TDM-E-L2-08 | ①上游=强度持续性+涨停潮/炸板率（FCT-MOM-005/022、DS-059/DS-170）②下游=STR-MOMTREND-003 挂载（proposed 无 evidence）③算法=族 S2 生命周期状态机 ④后端=sector_momentum_persistence 在岗 ⑤呈现=四段标签 ⑥数据=价格面可算；确认面 limit_up_pool/daban 仅 28 日 ⇒ blocked 声明 | 1 | calibration×1 | 已入卡（价格面），确认面挂 blocked | 缺 2021-08-02..2026-08-31 涨停池/打板事件史（高潮/熄火确认） |

| TDM-E-L2-09 | ①上游=政策/业绩/事件三类催化剂（DS-107）②下游=L2-01 加权+L3 池 ③算法=族 S7 研报评级聚集/PEAD ④后端=event_driven_screener MOD-SIG-106 在岗 ⑤呈现=催化剂标签 ⑥数据=**本车道唯一有长历史的板块级催化剂源** research_report 2017 起 146940 行/207 industry；文本面 news_data 2025 断供⇒政策腿 blocked | 2 | calibration×2 | 已入卡（02 密度+03 上调聚集，同表一次读取），政策/事件文本腿挂 blocked | 政策/事件文本腿：news_data 2025 断供 + 无板块级事件标注表 |
| TDM-E-L2-09-1 | ①上游=新闻实体/事件词+情绪（DS-224/DS-225）②下游=09-2 冲击标的 ③算法=族 S7 新闻→资产 ④后端=news_chain_node_linker（testing，55 单测+端到端 dry-run 在册）⑤呈现=命中+置信 ⑥数据=图谱 ig_* 仅 2026-08-28..09-24 构建记录且**无版本化/PIT**⇒回放即前视 | 1 | calibration×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：ig_* 无 2026-08-28 前历史+无 PIT 版本；news_data 2025 断供 |
| TDM-E-L2-09-2 | ①上游=受击节点+图谱边 ②下游=L3-04 负面否决、L0-02 盘中偏离（TDM 文字在册）③算法=族 S8 经济链条传染（Cohen-Frazzini 族）④后端=chain_impact_resolver（testing，23 单测）⑤呈现=冲击清单+方向 ⑥数据=同 09-1 根因+样本窗仅 ~1 个月⇒八臂消融不可行 | 1 | ablation×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：图谱无史+无版本；解锁需版本化+≥300 交易日事件积累 |
| TDM-E-L2-10 | ①上游=龙头板块+同链标的（DS-186/DS-170）②下游=L3 补涨候选 ③算法=族 S8 领先-滞后/补涨驼峰 ④后端=supply_chain_momentum 在岗 ⑤呈现=补涨候选清单 ⑥数据=龙头板块识别可全窗（880 2021-08-02 起）、"同板块内未涨股"需成分（2026-07-22 起）、"同链"需图谱（2026-08-28 起）⇒ 两腿均 blocked | 1 | calibration×1 | 六向留痕齐，blocked 于数据 | blocked_on_data：缺 ..2026-07-21 成分 与 ..2026-08-27 产业链图谱 |
| TDM-C-L2 | ①上游=山寨季指标+赛道资金流（TDM data_refs=[]）②下游=`git grep` 零命中（预留框架未施工）③算法=族 S9 BTC 主导率/山寨季轮动 ④后端=module_ref=null、red_reason=not_built⇒blocked_on_impl ⑤呈现=赛道前 3 榜 ⑥数据=crypto_kline_daily 2025-08-08..2026-10-08/19801 行/141 币×431 日，**无赛道标签列、TableRegistry 内 crypto 仅 2 表**⇒赛道腿样本 0 | 1 | calibration×1 | 六向留痕齐，blocked 于数据+实现 | blocked_on_data+blocked_on_impl：无赛道映射表（从未采集）、431 日样本不足、无市值面（山寨季不可算） |

## 2. 族级外部矿脉日志（挖一次，跨节点复用）

> 判定=signal/noise；来源全部带 URL+发布方+年份（闸1）；关键结论均 ≥2 独立来源（闸2），
> 单源者已标"待验证"不入图；A 股适配（闸3）逐条注明。查询词原文附后（供复挖/修正搜索策略）。

| 族 | 覆盖节点 | 轮次/矿脉 | 判定 | 关键产出（来源：发布方·年份·URL） | A 股适配/入图结论 |
|---|---|---|---|---|---|
| S1 板块相对强度·多周期动量·RRG | L2,01,01-2,01-3,02,02-1,02-2,08 | R1 | signal | ①《Momentum: what do we know 30 years after Jegadeesh and Titman's seminal paper?》Springer Financial Markets and Portfolio Management·2022·https://link.springer.com/article/10.1007/s11408-022-00417-8 ②《Sector Rotation Strategies in the TSX 60》MDPI Journal of Risk and Financial Management·2026·https://www.mdpi.com/1911-8074/19/1/70 ③《基于动量与风险优化双重视角的ETF行业轮动策略研究》汉斯出版社（金融）·2026·https://pdf.hanspub.org/fin_1141372.pdf ④《Analysis of China's A-shares Based on Industry Rotation Strategy》ResearchGate·2022·https://www.researchgate.net/publication/360012304 | 三源交叉（①综述+③中文行业轮动+④A 股实证）⇒ "行业/板块动量在跨市场与 A 股均有正 IC 但需 T+1 与涨跌停改造"入图；支撑 L2-01-2/01-3/02/02-1 卡的单调性+时滞先验。RRG 四象限口径取自实务族（Parete/Lilienthal 系），本仓在码 sector_rrg 为真源，外部只作"是否值得考"的依据，不作参数来源（禁引外部参数挪门柱） |
| S2 涨停/梯队/扩散/广度结构 | L2-01-1,02-2,03-1,06-2,08 | R1 | signal | ①《Advance Decline Difference Indicators (Chapter 4, Part 2)》StockCharts·2015·https://articles.stockcharts.com/article/articles-difference-indicators-chapter-4-part-2 ②《What Is the McClellan Oscillator?》Capital.com·2024(更新至)·https://capital.com/en-int/learn/technical-analysis/mcclellan-oscillator ③《Advance/Decline》thinkorswim Learning Center（TD Ameritrade）·年份未标·https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/A-B/AdvanceDecline ④《我回测了 A 股 10 年的"追涨停"策略》量化阅读/同花顺 quant·2026·https://quant.10jqka.com.cn/view/article/4Z81JJGR1F1581529UVWQAK744 ⑤《涨停板次日表现因子怎么挖掘》CSDN·2026·https://m.blog.csdn.net/leisoo8097/article/details/163804107 | ①②③=广度/扩散指标族（McClellan 系）交叉支持"扩散度水平 vs 一阶差分"二维分离（进 L2-03-1 卡判据形）；④⑤=A 股追涨停族，**发布方为社区博客级=待验证**（不入图作参数，只支撑"涨停结构在 A 股有独立信息"的方向性主张）。闸3：A 股 T+1+涨停不可买 ⇒ 广度类卡一律以"次日"为前向单位，不用日内 |
| S3 资金流与成交集中度 | L2-01-4,04-2,01-2 | R1 | signal（弱，多为中文实务） | ①《Mutual fund net flows in China: A co-holding network perspective》Frontiers in Physics·2023·https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2023.1142905/full ②《基金极端收益与资金流动》上海财经大学期刊·2020·https://qks.sufe.edu.cn/mv_html/j00001/202009/49bcbdb7-cec7-4b3c-b397-c5660b2605e0_WEB.htm ③《A股投资情况与板块变动之间联系的分析——基于行为金融学视角》fcipub·2025·https://www.fcipub.org/articleDetail/1659?periodicalId=30 | ①②交叉支持"资金流—收益存在反向因果混杂、须用滞后结构判定"⇒ 写进 L2-01-4 卡的 lag_profile（资金流峰值应迟于价格）；③单源=待验证。**注意**：三只均为"基金份额流"而非"主力净流入"口径，方向性借用、不外推为同口径证据（闸1/闸2 严守） |
| S4 市场状态/水温/情绪门控 | L2-04,04-1,04-2,05,05-1,05-2,01-5 | R1 | signal | ①《RBC 财富管理：一个被人忽视但准确率极高的指标（涨跌家线/广度）》投研周报转载·2023·https://m.sohu.com/a/642383312_557006/ ②《一个极其罕见的指标发出信号：美股前景一片大好》汇通网·2024·https://m.hstong.com/news/detail/24071819260149063 ③同题另源：金十数据·2024·https://xnews.jin10.com/details/143718 | ①②③交叉=情绪/广度极端档对中期收益有预测力（非日频），故本族卡把门控判据定为"态间利差+半衰期 >=1 日"而非强 IC 主张，并把"极端档反向"写成条件稳定性判据。闸3：A 股水温用本仓 emotion_index 自算，不外借美股阈值 |
| S5 因子叠加/门槛/消融与过拟合 | L2,01,01-5,06,06-1,07 | R1 | signal | ①《A Rigorous IS–WFA–OOS Protocol for Mitigating Overfitting》arXiv·2026·https://arxiv.org/pdf/2603.09219 ②《回测陷阱：前视偏差、过拟合、数据窥视》quant67·2026·https://quant67.com/post/quant/20-backtest-pitfalls/20-backtest-pitfalls.html ③《策略过拟合诊断工具集介绍》聚宽 JoinQuant·2026·https://www.joinquant.com/view/community/detail/3cf8435f4a772fc2f702589704db44db | 三源交叉=消融/IS-OOS 分离是防过拟合标准做法 ⇒ 支撑本车道"合成环节走 ablation"的车道立法与试次记账（n_trial_ledger）。②③明确警告"前视"，直接支撑 L2-09-1/09-2 卡拒绝用无 PIT 图谱回放（本车道最重要的两条 blocked 之一） |
| S6 回踩/Fibonacci 买点 | L2-07,07-1 | R1 | signal（学术证据薄，标待验证） | ①《What Are Fibonacci Retracement Levels》Investopedia·2025·https://www.investopedia.com/terms/f/fibonacciretracement.asp ②《Testing the performance of technical analysis》Journal of International Financial Markets（ScienceDirect）·2022·https://www.sciencedirect.com/science/article/abs/pii/S1062940818302250 ③《The performance analysis of chart patterns: Monte Carlo simulation》Springer·2009·https://link.springer.com/chapter/10.1007/978-3-7908-1992-2_9 | ②③交叉=图表形态类规则的可测性靠 Monte Carlo/基准对照，而非直接显著性 ⇒ 本族卡把"Fib 38.2% 必要条件"写成单因子 IC 排序 + 时间维倒 U 的双判据（而非硬阈因果）。①实务级来源，只作口径定义（23.6/38.2/50/61.8 档位），不作效果证据 |
| S7 研报评级/事件催化剂 | L2-09,09-1 | R1 | signal | ①《When Are Analyst Recommendation Changes Influential?》（学术转载，百度学术索引）·2025 转载·https://xueshu.baidu.com/usercenter/paper/show?paperid=b378e0216b3b316a6fd5f705ee001fc0 ②《Post-Earnings Announcement Drift: A Multi-Factor Explanation》同上索引·2025 转载·https://xueshu.baidu.com/usercenter/paper/show?paperid=05632489ae024951ad8a2e261e8fe764 ③《Analysts' cash flow forecasts and the underreaction to earnings forecast revisions》Discovery Researcher·2025·https://discovery.researcher.life/article/analysts-cash-flow-forecasts-and-the-underreaction-to-earnings-forecast-revisions/27cd0dbd5a9b3387aee4f8dbabc043a3 | 三源交叉=评级变动/研报密度存在反应不足（漂移），但"在何种条件下才有效"是开放问题 ⇒ 写进 L2-09 卡的 lag_profile（峰值 t+1、半衰期 >=2 日）与 density>95 分位反向腿。**题眼**：本族只认"信息扩散慢"这一条，不据此主张 20% 加权幅度（幅度由卡出分）。①②为检索转载页（原题发布方/年份需在开考阶段核对，已标待验证） |
| S8 产业链传染/领先滞后 | L2-09-2,10 | R1 | signal | ①《Climate Change and Adaptation in Global Supply-Chain Networks》Review of Financial Studies (OUP)·2024·https://ideas.repec.org/a/oup/rfinst/v37y2024i6p1729-1777..html ②《Fragility of a multilayer network of intranational supply chains》Springer Networks and Spatial Economies·2020·https://link.springer.com/article/10.1007/s41109-020-00310-1 ③《南橘北枳：A 股市场的经济关联与股票回报》中国经济/期刊网·2025 转载·https://economy.alljournals.cn/view_abstract.aspx?aid=0677DA8E81D857F73EAAA8377EB89347 | ①②③交叉=供应链关联确可传导股价冲击，且**传导强度随跳数衰减、A 股经济关联效应存在但方向依链条角色而变** ⇒ 直接支撑 L2-09-2 的 hop 递减判据与"全链同向 vs 成本反号"两臂消融；支撑 L2-10 的"补涨滞后驼峰"先验（滞后 3-5 日、增益递减）。闸3：③为 A 股证据（本党适配已过） |
| S9 加密赛道轮动/山寨季 | TDM-C-L2 | R1 | signal（实务级，不入图） | ①《Understanding Altcoin Season in 2026》Bitcoin Foundation news·2026·https://bitcoinfoundation.org/news/altcoins/understanding-altcoin-season-in-2026-what-are-altcoin-market-cycles/ ②《2026 山寨季前瞻：比特币主导率与 ETF 墙下的资本轮动信号》数字头刊 qklgw·2026·https://www.qklgw.cn/post/26502.html ③《Bitcoin Dominance Explained: 2026 Guide》kj17·2026·https://kj17.com/bitcoin/245567.html | 三源均为行情门户/自媒体级（无学术发布方）⇒ 按闸1 判"只登记题录、不入图作依据"。结论=TDM-C-L2 的算法主张（赛道前 3）在本仓既无实现也无口径，外部又无可采信源 ⇒ 该节点枯竭判据只能靠"数据面 blocked+实现面 not_built"闭环，已入卡并明列解锁条件 |
| S10 板块内聚合读数的数据不可得（本车道原创矿脉） | L2-01-1,01-4,03-1,06-1,06-2,06-3,08,10 | R1 | signal（内部矿脉，非外部） | 内部反查（见 §3 实测 + §4 断言日志）：sector_constituent 仅 6 个刷新日、snapshot 表仅 19 个交易日、limit_up_pool/daban 仅 ~28 日、880 行业指数上限 2021-08-02 | 结论入图=**板块层"个股聚合类"读数（涨停占比/扩散度/资金流聚合/龙头时序）在冻结窗结构上不可考，而"板块指数面"读数（价/量/RSI/集中度）自 2021-08-02 可考**。这一条决定本车道 8 张卡走 blocked、7 张卡走 preregistered，是本车道对全战役的最大贡献（供 L3 车道复用同一判据） |

## 3. 数据面实测日志（命令原文+输出摘录）

> 全部经 `scripts/backtest/fexam/ch_data.py`（TableRegistry 表名 + HTTP 只读），禁裸 duckdb；
> 每条命令均在 2026-10-10 本机执行，工作根=`D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。
> 空结果判读：`ch_query` 出错可能返回空串（在册事故）⇒ 本轮所有失败均以 CHAccessError/HTTP 异常显式抛出的形式留痕，
> 其中 2 次真实报错见 P14（research_report 无 trade_date 列→改用 publish_date）与 P18（typeof() 被 CH 拒 404→弃该探测）。
> 探针脚本（临时件）=`D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/probe2.py`、`probe3.py`、`dump_l2.py`。

- **P1 表枚举**：`SELECT database, table, name FROM system.columns WHERE name ILIKE '%sector%' OR '%industry%' ...`
  → 板块族在册：`kline_sector`、`kline_sector_880`、`kline_sector_intraday`、`sector_constituent`、
  `sector_constituent_snapshot`、`sector_code_name_map`、`sector_snapshot`、`sector_state`、`sector_preference`、
  `sector_fund_flow`、`sector_meta`、`sector_list`、`concept_board(_constituent)`、`concept_sector`、`industry_class`、
  `v_kline_sector_880_named`；视图/映射表的存在本身是矿（口径字典）。
- **P2** `SELECT min(trade_date),max(trade_date),count(),uniqExact(symbol) FROM c1_market.kline_sector`
  → `2025-07-18 / 2026-09-30 / 86033 / —`（列 code；DS-170 在册口径同源）⇒ **板块 K 线主表只有 14 个月**，
  凡按 DS-170 建窗的卡必 blocked（本车道改用 880，见 P5）。
- **P3** `... FROM c1_market.kline_sector_880` → `2020-03-17 / 2026-10-08 / 785204`；
  `GROUP BY period` → 唯一 period='1d'，codes=729；`countDistinct(trade_date)=1590`（经视图）。
- **P4** 按 code_family 分组首末日（join `sector_code_name_map`）：
  industry_l1(61 codes)=`2021-08-02..2026-10-08/78263`；industry_ths(128)=`2021-08-02..2026-10-08/163038`；
  industry_l2(71)=`2021-08-02..2026-10-08/91093`；concept_or_style(426)=`2020-03-17..2026-10-08/818080`；
  region(32)=`2022-08-01..2026-10-08/66688`；mkt_index(11)=`2022-07-29..2026-10-08/20852`。
  ⇒ **在册结论"881/8803 板块指数深史真实上限=2021-08-02"实测复证成立**（8803→industry_l1、881→industry_ths），
  且概念/风格族更早（2020-03-17），区域族 2022-08-01 ⇒ 本车道统一用"行业族 2021-08-02"为冻结上限（保守口径）。
- **P5** `SELECT code_family, coverage_status, count() FROM c1_market.sector_code_name_map GROUP BY ...`
  → named 1198 行中 concept_or_style=850、industry_ths=128、industry_l2=71、region=64、industry_l1=61、
  mkt_index=22（其中 unresolved=18）⇒ 口径字典有 18 个未解析市场级条目，登记为质量画像缺口（不阻断行业族卡）。
- **P6** `... FROM c1_market.sector_constituent` → `2026-07-22 / 2026-10-01 / 323175`，
  uniq(sector_code)=727、uniq(stock_code)=6229、**countDistinct(update_date)=6**
  ⇒ 板块成分仅 6 个刷新日 = 本车道根因级缺口。
- **P7** 其余采集面：`sector_constituent_snapshot`=2026-09-14..2026-10-09/1922366/19 日；
  `money_flow`=2021-01-04..2026-10-09/5993328/5782（分年 2021=1058846…2026=483807）；
  `sector_fund_flow`=2026-09-15..2026-10-09/10536（17 交易日）；`market_fund_flow_daily`=2026-03-27..2026-10-09/148；
  `sector_snapshot`=2026-08-14..2026-10-08/122746；`kline_sector_intraday`=2026-07-20..2026-10-09/11628577（~55 日）；
  `limit_up_pool`=2026-09-01..2026-10-09/1426/789；`limit_up_down`=2026-07-20..2026-10-09/5397/1841；
  `daban_board_event`=2026-09-01..2026-10-09/1767/975；`daban_engine_load`=2026-09-01..2026-09-28/1701/19 日；
  `stk_limit`=2015-01-05..2026-10-09/9254772/5831；`industry_class`=2026-08-03..2026-10-08/46228/10472；
  `sector_list`=2026-09-03..2026-10-09/10443/5226；`stock_profile_ths`=仅 2026-09-09/5217；
  `concept_board_constituent`=2026-08-10..2026-10-09/37891/4927；`concept_board`=750；`concept_sector`=375（单日快照）；
  `sector_meta`=2026-08-10..2026-10-08/2790；`sector_preference`=2026-09-23..2026-10-09/**仅 5 行**。
- **P8** `daban_engine_load` 列集含 `sector_limit_up_count / market_limit_up_count / market_breadth_ratio`
  ⇒ 板块级涨停家数**已有采集**（19 个交易日）；登记为"补史起点候选"，不足以建响应曲线。
- **P9** `sector_state` 列分年非空计数（关键质量画像）：
  `momentum_pct/rrg_quadrant/watch_score/components` 2022..2026 全部满配
  （分年行 29927/96298/105176/111658/89029；codes 376/418/451/465/729）；
  **`strength` 2022-2025 全 0、2026 才 25317/89029；`net_inflow_pct` 2026 才 24927；`capital_score` 全史 0**；
  stage 分布 close_final=429432 / pre_open=2656（仅 2026-09 起）。
  ⇒ 结论：在册列 ≠ 已落地列；`capital_score` 为"有列无值"（勿当可得），
  板块宇宙数从 376→729 在扩 ⇒ 占比/分位类读数必须冻结分母族（多张卡据此写死 universe 口径）。
- **P10** 目标面 `kline_index`：`symbol='000300'` → 2005-01-04..2026-10-09/5284 行；
  000001=1990-12-19..8738、399001=1991-04-03..8693、000016=2004-01-02..5527、000852/000905=2005-01-04..5284/4790；
  `advance_count` 非空计数=全行数（该列非 Nullable，值分布待开考阶段核，不作断言）。
  个股目标面 `kline_daily_hfq`=1990-12-19..2026-09-30/10098785/5916 ⇒ **2026-09-30 之后 9 日缺口**（已登记，不影响 OOS 终点 2025-09-09 的卡）。
- **P11** `emotion_index`：close_final=1991-06-10..2026-09-30/8617 行，version 单值 v0.1.0，
  逐年 237~257 行（1991 半年 145 行）无断年，值域 [0.012,1.0]；pre_open 27/auction 17 仅 2026-09 起。
  `sentiment_panel`：fear_greed_index 40 行（2026-09-01 起）、cb_conversion_premium_median 12 行 ⇒ 不可作水温源。
- **P12** `news_sentiment_window`：window_date=2019-01-04..2026-10-08/22257 行；
  scope×window_type 分布 symbol/night=19635、market/night=**201**、market/1d=2421 ⇒ 市场级夜窗仅 201 条（L1-S0-1 面，本车道只作旁证）。
- **P13** `research_report`：`SELECT min(publish_date),max,count(),uniqExact(industry),uniqExact(org_name)`
  → 2017-01-02 / 2026-09-30 / 146940 / 207 / 116；逐年 2017=10933…2023=22019、2024=19900、2025=16237、2026=8319；
  industry Top=半导体 6456/汽车零部件 5545/电池 4822/软件开发 4631/白酒Ⅱ 4119 ⇒ **板块级催化剂唯一长史源**。
  （首次以 trade_date 探测报 HTTP 404 → 该表日期列为 publish_date，已如实记录为 P14 的失败-修正）
- **P14** `news_data`：2010-01-02..2026-10-10/8219185 行；逐年 2023=1062308、2024=759512、
  **2025=31425**、2026=259401 ⇒ 2025 年断供（不足上年 4.1%），事件/催化剂类窗必须避开 2025。
- **P15** PG 图谱（只读，经 `DatabaseService().get_depgraph_conn()`，禁裸连）：
  ig_chain=873、ig_node=5560、ig_edge=1726、ig_node_company=25559；
  `min/max(created_at) FROM ig_node_company` = 2026-08-28 04:08:55+08:00 / 2026-09-24 15:47:33+08:00
  ⇒ 图谱无版本化历史（先 `get_governance_conn()` 试得 'no such table'=ig_* 不在治理库，改走 depgraph 成功，两次尝试均留痕）。
  与 DS-224 在册快照 830/3328/1378/16900 已漂移——该条自注"计数以实时查询为准，禁引用快照数"，本处依约以实测为准。
- **P16** `crypto_kline_daily`：2025-08-08..2026-10-08/19801 行/141 symbols，每币 431 行；
  列集含 base_asset/is_universe_eligible/universe_rank，**无 sector/track/category**；
  `crypto_shadow_gate`=20 行；TableRegistry 全表枚举中 crypto 相关仅此 2 张 ⇒ 赛道腿不可算。
- **P17 失败留痕**：`SELECT typeof(col) ...` 连续 20 表报 HTTP 404（CH 拒该探测形式）⇒ 弃 typeof 法，
  改为按列名后缀选日期列（probe2.py）。`typeof(trade_date)` 类断言未用于任何卡结论。
- **P18 在册 DS 口径 vs 实测**（供 TDM/资产册纠偏，本车道不改）：
  DS-170 在册"7 万行、2025-10-01..2026-09-01"=实测 kline_sector 86033 行/2025-07-18..2026-09-30（同表，量级一致，窗更宽）；
  DS-181 在册"24 万行、2026-08-01..2026-09-01"=**实测 money_flow 599 万行/2021-01-04..2026-10-09**
  （在册数显著低估，资金流历史面比登记可用得多——本车道据此把 L2-01-4 的缺口定位到"成分"而非"资金流"）；
  DS-186 在册"24 万行、2026-07-01..2026-09-01"=实测 sector_constituent 32 万行/2026-07-22..2026-10-01（量级一致）。

## 4. 断言正查日志（§7.5 资产状态断言纪律）

- **A0 工具不可用与降级阶梯（明列）**：作业簿/§7.5 指定 `python -m zephyr.library.lookup state "<关键词>"`。
  本工棚版本 `zephyr.library.lookup` 的 `--help` 实测**无 `state` 子命令**（参数集=
  query/--kind/--owner-domain/--tags/--status/--home-prefix/--backtest/--feeds/--strategy/--since/--until/--session），
  直接传 `state "板块轮动 RRG 考卷"` 两次执行均 exit 0 且**零输出**（后台任务输出文件为空，路径
  `C:/Users/fanzi/AppData/Local/Temp/qoder-cli-cn/D--ZephyrAlpha/.../tasks/b02inlmwm.output`、`b1ozyot4y.output`）。
  ⇒ 依 §7.5"工具不可用时降级手工阶梯"，本车道所有状态断言改用：
  ①`git grep -ln <node_id> -- src scripts config`（消费方反查，A3）
  ②TableRegistry 枚举 + `system.columns/system.tables`（表/列在册性）
  ③`docs/_working/` 与 `docs/03_modules/**/exam_cards/` 文件枚举（是否已做过同类卡）
  ④data_asset_registry.yaml 逐条 dataset 解析（DS 在册口径）
  ⑤DS-224 快照数依其自注不引用（改用 P15 实测）。
- **A1「板块层无真卡，仅机生骨架」**：成立。证据=
  `Glob docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/*` 实扫 30 件，全部为
  `__comparison.yaml`/`__ablation.yaml` 且件首两行含 `# [GENERATED by MOD-BT-244 generate_exam_card_skeleton]`
  与 `status: empty`、`generated: true`（例：`TDM-E-L2-06-3__comparison.yaml` 全文核对）。
  本车道新卡另建文件、未触碰骨架件（禁区遵守）。
- **A2「sector_constituent 是三处采集宇宙的唯一读取源」**：依作业簿为在册结论，本车道做正向复证：
  `system.columns` 全库枚举中含板块成分语义的物理表仅 `sector_constituent`、`sector_constituent_snapshot`、
  `sector_list`、`concept_board_constituent`、`industry_class`（P1/P7），而四者首日期均 ≤2026-10、起点最晚
  `stock_profile_ths`=单日 ⇒ "板块口径唯一可回溯读取源"这一条在任何历史窗都指向 sector_constituent，
  扩宇宙必先核它的义务成立。
- **A3 消费方反查（`git grep -ln`，命令原文=
  `for n in ...; do git grep -ln "$n" -- src scripts config | grep -v trading_decision_map.yaml; done`）**：
  L2-01-5→`scripts/backtest/generate_backtest_backlog.py`；L2-03/L2-03-1→`src/zephyr/signal_ashare/adjustment_cycle_tracker.py`；
  L2-04→`config/trading_day_cycle_map.yaml`、`generate_backtest_backlog.py`、
  `generate_trading_day_cycle_map.py`、`src/zephyr/signal_ashare/__init__.py`、`core/sector_ecology_judge.py`、
  `core/sector_strength_wiring.py`；L2-02/L2-02-1/L2-02-2/L2-04-1/L2-04-2/TDM-C-L2→**零命中**
  ⇒ 这六节点的输出未接线（②向结论按"已查无消费方"登记进表，非"卡不需要"）。
- **A4「币圈赛道映射表不存在」**：正向查证=P16（TableRegistry 全枚举 crypto 仅 2 表 + crypto_kline_daily 列集无赛道列）
  + `grep -rn "赛道" src/zephyr | grep -i "crypto\|usdt"` 零命中。⇒ 断言带双指针成立。
- **A5「板块层无 IC/校准考卷先例」**：正向查证=A1 的文件枚举 +
  `Glob exam_cards/entry_flow/L1/*` 实扫 L1 已有 25+ 张真卡（涨停家数/跌停家数/炸板率/封板率/连板高度/净广度/
  期权 IV 等）⇒ **修正为"板块层无、大盘层有"**，且 L1 先例即本车道模板真源；
  不得表述为"全仓无 calibration 卡先例"（正向断言同纪律）。
- **A6「sector_state.strength 有历史值」**：负向断言证伪成立——P9 分年非空计数显示 2022..2025 全 0。
  ⇒ 任何依赖该列历史值的卡必须 blocked（本车道未依赖，改用 880 重算）。

## 5. 未挖长尾清单（明列，不降格封矿）

1. **880 概念/风格族（850 codes，2020-03-17 起）**：本轮只用行业族。概念族起点更早（多 17 个月），
   可把部分卡的 IS 前推到 2020-03-17——需先做"概念宇宙漂移"质量画像（850 codes 的新增/消亡史），
   否则=宇宙扩张冒充信号。属族 S1/S10 复挖。
2. **`sector_code_name_map.tdx_type/tdx_level/coverage_status` 口径字典深挖**：18 个 mkt_index unresolved 条目、
   industry_l1 61 vs 板块表 727 codes 的对账关系未理清（本车道只做前缀级口径）。
3. **`kline_sector_880.forward_factor`（复权因子）与 `data_source` 断供史**：未做年度缺口扫描（本车道只测首末日与分年计数）。
4. **`sector_preference`（5 行）/`sector_meta`（2790 行）/`concept_board`（750 行）三小表消费面**：
   未反查其生产方与在册 job 关系（④后端的"休眠采集面"矿，属 §8 失败模式表"内部矿脉被忽略"的反向自查）。
5. ~~L2-06-3 传导时滞曲线专卡~~ **已落件**（`TDM-E-L2-06-3__calibration__03_传导时滞曲线.yaml`，2026-10-10 本车道第 31 件）；
   同批另落 `TDM-E-L2-09__calibration__03_评级上调聚集.yaml`（第 32 件）。
6. **L2-01-2 换手率维（需流通股本 sector_meta.float_share × 成分）专卡**：本轮未挖。
7. **L2-02-2 盘中面**：activation=intraday 与 kline_sector_intraday（2026-07-20 起）的"短窗专卡"是否值得，
   已登记为交叉复挖候选（不降格为已挖完）。
8. **念想引擎（LSG qwen）向**：本车道未调用（≤8 次调用预算内优先留给实测取数）；
   登记为"受阻=未尝试"而非"查无"，供复挖轮使用（真用法需先 `git grep -n "provider='qwen'"` 核对）。
9. **DS-181 在册行数显著低估（P18）**：资金流历史比登记充分，应反向提交 TDM/资产册纠偏（本车道无权改）。
10. **行业族指数与申万/同花顺一级行业的对卡**：880 industry_l1(61) vs research_report industry(207) vs
    stock_profile_ths l1 三套行业口径的映射表未做——这是 L2-09 卡辅轴（板块超额）落地的前置缺口。

## 6. 建议交叉复挖 20% 名单（供其他车道/复挖轮）

按"矿脉富集度×可解锁性"排：
1. **TDM-E-L2-01-2 / TDM-E-L2-04-2**（共用 880 amount 面，一表两题，且都能随概念族解锁更早窗）；
2. **TDM-E-L2-06-3 / TDM-E-L2-06-1**（引擎侧 X_sector 已在，卡出分即可直接进考卷 arm，反馈环最短）；
3. **TDM-E-L2-09**（research_report 207 行业×2017 起是本轮最大意外富矿，值得加挖"评级上调聚集"与
   "研报覆盖度变化"两独立题）；
4. **TDM-E-L2-01-3 / TDM-E-L2-08**（动量持续性同一矿脉两问，与在码权重/文字矛盾同批解决效率高）；
5. **TDM-E-L2-04-1 / TDM-E-L2-01-5**（态分类与态注入成对，两卡出分才能定改不改）；
6. **TDM-E-L2-02-1**（RRG 与 sector_state 满配列的口径对卡，是唯一能用"交叉核对"提质量的卡）；
7. **TDM-E-L2-03**（与 L2-03-1、L2-07-1 共用重算，三维权重改法要一起判）；
8. **TDM-C-L2**（若 Owner 侧建赛道映射，本卡立刻可解，解锁成本最低）。

## 7. 收尾汇总（本车道）

- **节点总数**：30（entry_flow/L2 板块层，含 TDM-C-L2 币圈预留框架节点）。
- **已挖数**：30/30（每节点六向全部留痕，见 §1 表）。
- **新卡总数**：32（30 节点全覆盖；L2-06-3 与 L2-09 各 2 张——02/03 分工写死在卡内 note，
  未凑数摊薄；机检=临时件 `validate_cards.py` 实跑输出 `ours cards: 32 problems: 0`）。
- **族分布**：calibration 22、ablation 10、comparison 0（对照题在本层被 ablation 吸收，避免与骨架件重复）。
- **status 分布**：preregistered 24、blocked_on_data 8、blocked_on_impl 1（与 blocked_on_data 交叠：TDM-C-L2）。
- **mined_out 名单（22，六向全部"已入卡/已查无"且无本节点级未挖长尾）**：
  TDM-E-L2, TDM-E-L2-01（四路全量面另挂 blocked）, TDM-E-L2-01-2, TDM-E-L2-01-3, TDM-E-L2-01-5,
  TDM-E-L2-02, TDM-E-L2-02-1, TDM-E-L2-02-2（盘中面另挂 blocked）, TDM-E-L2-03, TDM-E-L2-04,
  TDM-E-L2-04-1, TDM-E-L2-04-2, TDM-E-L2-05, TDM-E-L2-05-1, TDM-E-L2-05-2, TDM-E-L2-06,
  TDM-E-L2-06-1, TDM-E-L2-06-3, TDM-E-L2-07, TDM-E-L2-07-1, TDM-E-L2-08, TDM-E-L2-09。
  （注：这 22 个的"枯竭"=结构判据达成，不等于无进一步题；§5/§6 列的是跨节点长尾与复挖建议，
  依 §3 禁降格原则，本车道不以"已挖一张卡"冒充封矿，也不以"候选多"作停止判据。）
- **blocked 名单与原因（8）**：
  | node | status | 缺什么（写死） |
  |---|---|---|
  | TDM-E-L2-01-1 | blocked_on_data | 2019-01-04..2026-07-21 板块成分口径（sector_constituent 仅 6 刷新日；snapshot 仅 19 日） |
  | TDM-E-L2-01-4 | blocked_on_data | 同上（聚合路）；直读路 sector_fund_flow 仅 2026-09-15 起 17 交易日，个股 money_flow 本身 2021-01-04 起充分 |
  | TDM-E-L2-03-1 | blocked_on_data | 2019-01-04..2026-07-21 成分口径（个股价格面 1990 起充分，SMA20 可算，缺的是归属） |
  | TDM-E-L2-06-2 | blocked_on_data | 2019-01-04..2026-08-31 涨停池/打板时序（limit_up_pool 1426 行/28 日；stk_limit 价格面 2015 起但无封板时点） |
  | TDM-E-L2-09-1 | blocked_on_data | ig_* 无 2026-08-28 前记录且无 PIT 版本；news_data 2025 年断供（31425 行） |
  | TDM-E-L2-09-2 | blocked_on_data | 同 09-1 根因 + 图谱可回放窗 <1 个月，八臂消融样本不足 |
  | TDM-E-L2-10 | blocked_on_data | 同题材腿缺 ..2026-07-21 成分；同链腿缺 ..2026-08-27 图谱历史 |
  | TDM-C-L2 | blocked_on_data + blocked_on_impl | 无赛道映射表（TableRegistry crypto 仅 2 表，列集无 sector/track）；历史仅 2025-08-08 起 431 日/141 币；无市值面（山寨季不可算）；TDM 侧 module_ref=null、red_reason=not_built |
- **本车道对全战役的两条硬结论**：
  ①板块层可考面=**板块指数面（价/量/RSI/集中度/RS 象限），冻结上限 2021-08-02**（P4 实测复证在册结论）；
  ②板块层**个股聚合类读数（涨停占比/扩散度/资金流聚合/龙头时序/补涨）结构性不可考**，
  根因单一=成分口径（sector_constituent 6 个刷新日）——L3 车道凡"板块内个股"题都会撞同一堵墙，
  解锁只需一次补史（2021-08-02 起日频或月频 SCD2 成分），收益覆盖本车道 8 张卡。

