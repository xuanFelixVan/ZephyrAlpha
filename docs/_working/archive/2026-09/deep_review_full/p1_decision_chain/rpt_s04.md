---
ttl: task_bound
title: 深度审查报告——主线概率（S04）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：主线概率（S04）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/mainline_probability.py:111`（MainlineProbabilityConfig）/ `:389`（compute_mainline_probability 主入口）
- 生产调用方: position_sector_context.py:243、limit_up/war_pool_generator.py:312（两件自身再无上层调用方=观测层链顶，self-declared "观测层消费不接交易" :35）
- 测试文件: tests/signal_ashare/test_mainline_probability.py（405 行 18+ 用例，已审）
- 备注: MATURITY=testing 诚实；本域他会话在途件 sector_ecology_judge 引用本件"lead_streak<2"口径（:38 注释一致）

## 1 对象快照

- **范围**：`mainline_probability.py` 全文 496 行——MOD-SIG-061 主线候选榜内每板块四因子（RRG 象限/接力阶段/资金持续性/梯队完整度）启发式合成 0-100 相对分；缺维按可用权重重归一；PIT（SCD-2 成分+窗口 ≤ trade_date）。
- **排除项**：mainline_candidates（MOD-SIG-061，上游另件）；sector_leader（MOD-SIG-062，上游另件）；sector_momentum_persistence（兄弟件，仅对口径）。
- **测试覆盖概况**：四因子子分/降档/缺维重归一/全缺 None/overrides 白名单 fail-closed/候选降级传播/资金腿独立降级/龙头榜降级/无客户端降级/日期契约 fail-closed——覆盖面好。信任度：**信任（盲区=NULL 折叠与重复行）**。
- **材料包缺项声明**：无运行时证据包；money_flow 表 NULL 率/重复粒度未画像（列入挂起疑问）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 合成数学健全：pct=Σw·s/Σw(可用)×100，子分均 ∈[0,1]、权重正 → pct∈[0,100]；缺维重归一不留 0 拉低（INVARIANTS 兑现）；全缺→None 不出伪分；wsum≤0 兜底 | mainline_probability.py:301-311 | —（已查无） | test_full_weights_static / test_missing_factor_renormalize / test_all_factors_missing_gives_none |
| A | **money_flow NULL 折叠 0.0**：`float(row[2] or 0.0)` 使"真实零流入"与"缺数/NULL"不可区分——NULL 率高的窗口 → 板块日序列存在且 ≥5 样本 → fund_score=0.0（非缺维），资金维被静默压 0（**checklist#6 D10 断更恒 0 同症的子分辨率版**：全表断更→空序列→None 正确降级；值断更(NULL)→恒 0 静默） | mainline_probability.py:371、:219-223 | **P1** | `score_fund_persistence([0.0]*10)` → 0.0（非 None）；对照 `score_fund_persistence([])` → None；再查 money_flow 表 main_net_inflow NULL 率即证现实暴露面 |
| A | 重复 (trade_date, symbol_canonical) 行覆盖不聚合：flow_by_symbol_day 字典直写，money_flow 若有日内多笔/多类型行则静默取末行——表粒度契约（一 symbol-day 一行？）未验证未文档化 | mainline_probability.py:369-371 | P2 | `SELECT symbol_canonical, trade_date, count() FROM c1_market.money_flow GROUP BY 1,2 HAVING count()>1 LIMIT 5` 有行即证 |
| A | 排序平分决胜 sector_code **降序**：`reverse=True` 使同分板块按代码 Z→A，与 S02 候选池"名称升序"约定相反——跨模块口径不一致（微小但同题两序） | mainline_probability.py:482-485 vs sector_strength_aggregator.py:154 | P3 | 构造两同分 items 观察 sort 输出序 |
| A | fund_lookback_days≤0 边界：`[-0:]` 等价全序列（Python 切片陷阱），配置误置 0 时窗口静默失效（min_periods 仍兜底） | mainline_probability.py:221 | P3 | `MainlineProbabilityConfig(fund_lookback_days=0)` + 20 样本 → 取全 20 条非 0 条 |
| A.3 | weight_overrides 部分覆盖=整体替换语义（未覆盖键权重清零）**有测试固化**（"覆盖权重键外的因子按 0 处理"）——非缺陷，登记口径防调用方误解 | test_mainline_probability.py:240-257、mainline_probability.py:266 | P3（口径登记） | 读测试注释+用 overrides={"rrg":1.0} 对照 |
| B | 上游三腿防御好：候选榜 degraded→整体 degraded 传播（:422-423）；龙头榜 degraded→relay/echelon 双维缺位重归一（:440-442）；ch 客户端不可得→degraded（:416-419）；trade_date 非法 fail-closed ValueError（:412）——逐腿"上游错→本对象表现"明确 | mainline_probability.py:411-451 | —（已查无，正面记录） | test_candidates_degraded_propagates 等 4 用例 |
| B | PIT 正面：sector_constituent SCD-2 时点过滤（valid_from≤d<valid_to）、money_flow 窗口 ≤trade_date——checklist#7 正面命中 | mainline_probability.py:97-107 | —（正面） | 读 SQL 常量 |
| C | 下游：position_sector_context（MOD-SIG-065 持仓板块语境）与 war_pool_generator（45 号 W2 战法池）消费；**两者自身在 src/scripts 无任何上层调用方**（grep -l 零命中）→ 本链为"链上有件、全链未接编排"的观测层叶子。probability_pct=None 条目可进入 items（全缺维板块）→ 前端契约须处理 None（:149 已标注） | position_sector_context.py:243、war_pool_generator.py:312；全仓 grep 两模块名仅自身+本件 | P2 | grep 命令实录 |
| C | 静默吞掉审计：数据层异常 broad except → notes 留痕+logger.warning（:340-341、:366-367）——**可审计的降级是良设计**；但无心跳/告警通道，持续断供将无限期 degraded 而无人知（系统级问题非本件独有） | mainline_probability.py:334-342、:366-367 | P3 | 造 client.execute 抛错 → notes 含降级说明（test_fund_leg_failure_degrades_independently 已固化） |
| D | **资金持续性公式双承载**：本件 score_fund_persistence（0.6×正流入占比+0.4×尾部连正）与 sector_momentum_persistence 声明"资金子分对齐 MOD-SIG-064 F3 口径"（同公式重实现）——两处承载，改一处必漂移（checklist#4），当前口径一致 | mainline_probability.py:214-232 vs sector/sector_momentum_persistence.py:8 | P3 | 对照两处公式行 |
| D | 兄弟口径引用一致：sector_ecology_judge :38 引"lead_streak<2=无主线混沌"反向口径与本件 INVARIANTS :8 一致 | mainline_probability.py:8、core/sector_ecology_judge.py:38 | —（一致） | 对照两行 |
| E | 幂等/时序：纯读 SQL+纯函数合成，重跑安全；降档语境 rotation_state 来自候选榜快照（同日重放同结果）；无竞态面 | mainline_probability.py 全文 | —（已查无） | test_happy_path_ranking 重跑 |
| E | 墙钟卫生：trade_date=None 且降级时 `(d or date.today())` 用墙钟——仅进 notes 字符串不进评分，PIT 风险极低但违反"生成器禁 datetime.now"精神 | mainline_probability.py:418 | P3 | 读 :418 |
| F | RRG 象限评分（LEADING 1.0/IMPROVING 0.7/WEAKENING 0.3/LAGGING 0.1）——RRG 是成熟商业分析框架（Relative Rotation Graph），象限优先序与本件映射方向一致；本次未检索验证（额度已尽） | 本件 :83-88 | 受阻（方向性对等初判） | 收口方可补检 relative rotation graph quadrant definition |
| F | 连板梯队/龙头接力评分——A 股特有打板生态启发式，业界无标准化模型（中文卖方金工族，本战役检索受阻） | 本件 :189-207 | 受阻 | 同上 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 四因子缺维重归一加权合成 | **对等已有**：加权合成+可用维重归一是多因子合成的标准手法（与本战役已检索确认的 sector momentum 轮动评分同族） | [Quantpedia — Sector Momentum Rotational System](https://quantpedia.com/strategies/sector-momentum-rotational-system)（方法族对照，非逐条复刻） |
| RRG 象限→子分映射 | **受阻**：RRG 框架真实存在且象限语义方向一致，本次无检索额度验证具体映射惯例 | 本战役检索记录 2026-09-18 |
| 涨停梯队接力启发式 | **受阻**（A股特有，无英文文献族；中文研报检索 429） | 本战役检索记录 2026-09-18 |

## 4 缺陷清单（按严重级排序）

1. **P1｜money_flow NULL→0.0 折叠使资金维可被静默压 0**
   - 现状：`float(row[2] or 0.0)` 折叠；序列存在且 ≥5 样本即计分，全 0 序列 → fund_score=0.0 而非缺维。
   - 证据：mainline_probability.py:371、:219-232。
   - 影响与爆炸半径：main_net_inflow 供应端故障但表有行（上游 ETL 空跑/字段断供留行）→ 全候选板块资金维归 0 → 主线概率分系统性下偏（决策观测偏移）；对比 D10（F4 断更恒 0）同症。
   - 建议修法：折叠处区分 None（缺）与 0.0（真零）——缺数占比超阈值 → 该板块序列置 None 走缺维；或 NULL 行剔除并按有效样本数过 min_periods。
   - 验证法：`python -c "from zephyr.signal_ashare.mainline_probability import score_fund_persistence, MainlineProbabilityConfig as C; print(score_fund_persistence([0.0]*10, C()), score_fund_persistence([], C()))"` → `0.0 None`；辅以 DB NULL 率查询。
2. **P2｜money_flow 日粒度契约未验证**（重复行末位覆盖）：聚合前先验证唯一性或改 SUM 聚合；验证法=§2 轴 A 行 SQL。
3. **P2｜下游链未接编排**（观测层叶子）：通电时须补空榜/None 条目的消费方契约测试；验证法=grep 上层调用方。
4. **P3｜平分决胜序与 S02 相反**：统一两模块同分决胜约定；验证法=构造同分对照。
5. **P3｜fund_lookback_days≤0 切片陷阱**：config 校验 >0；验证法=置 0 对照。
6. **P3｜资金持续性公式双承载**：抽取共享实现或加口径一致性对账测试；验证法=对照两文件公式。

## 5 挂起疑问

- money_flow 表 main_net_inflow NULL 率与 (symbol, day) 唯一性未实测（需 DB 只读查询，收口方执行——决定 P1/P2 的现实暴露面）。
- MOD-SIG-061/062 两上游件的算法本体未在本次边界内深审（各自建议单列对象）。
- weight_overrides 动态权重未来接"按 sector 注入"时的并发/一致性设计未定义（接口位仅留）。

## 6 完备性自评

- 六轴全查：是（F 轴 3 条：1 方法族对等+2 受阻）。
- 长尾：①money_flow 数据画像（NULL 率/粒度）；②MOD-SIG-061/062 本体审查；③war_pool/position_sector_context 消费侧契约审查。
- 变更热力：5 commits——创建批+平铺搬家+algo_flow 锚点批（与 S03 同族治理性变更），无算法返工史=低危。
- 测试审查结论：信任（18+ 用例覆盖降级矩阵与 fail-closed；无日期依赖；盲区=NULL 折叠与表粒度，恰为 P1/P2 所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
