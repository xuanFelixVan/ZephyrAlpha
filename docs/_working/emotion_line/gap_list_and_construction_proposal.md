---
ttl: task_bound
title: 情绪线缺口清单+施工建议单（交下轮施工讨论）
created: 2026-09-22
sid: st-emomine-20260922
lane: emotion_line
status: draft（建议单，未经 Owner 批示不开工）
doc_version: v1.1（含挖干补遗轮）
---

# 缺口清单+施工建议单

> 依据=内部盘点册四态实证 + 骨架设计稿 v0 需求。规模单位=AI 会话·人日（含门禁/提交开销）。
> 全部为**建议**，逐项等 Owner/Max 批示；本班零施工。

## §1 缺口清单（按阻塞度排序）

| # | 缺口 | 现状证据 | 阻塞什么 | 级别 |
|---|------|---------|---------|------|
| G1 | daban 链断供（09-16 起 5 个交易日） | daban_board_event / daban_engine_load 均停 09-15；上游 kline_daily/stk_limit 都通到 09-22 | C1 涨停温度/C2 晋级率两成分；板块线同受害 | **P0** |
| G2 | cohort 落地闸未合 | c1_backtest.cohort_daily_ledger 表未建+tasks.yaml 无 cohort_ledger_daily；与代码头"已接线 Owner 批"注释矛盾 | 画像挂载位（v0.2）；cohort 五人群产线 | **P0**（归属核对优先） |
| G3 | emotion_index 无产出面 | 输出表/聚合器不存在（本线设计稿 v0 待审） | 情绪指数本体 | **P1**（主体施工） |
| G4 | sentiment_panel 词表漂移 | DDL 注释四 metric 词表 vs 实库第五个 cb_conversion_premium_median | 元数据一致性（不阻塞聚合） | P2 |
| G5 | 两融史浅+近端滞后 | margin_trading 07-20 起、max 09-18 | C5 杠杆成分分位窗（INSUFFICIENT 预登记） | P2 |
| G6 | 新闻情绪单窗+全 rule 法 | news_sentiment_window market 1 行/日、data_source 全 rule | C6 新闻成分质量上限 | P2 |
| G7 | market_breadth_snapshot 极浅 | 139 行/08-24 起 | 盘中 stage（已用 kline_daily 派生绕开） | P3 |
| G8 | PCR 未建 | 期权原料在库（iv_surface 3 万行等），衍生缺 | v0.2 PCR 挂载位 | 外部依赖（小红书班第 3 件在建，勿重复施工） |

## §2 施工建议单（估算规模+依赖）

### S1（P0）daban 周窗复通+监控
- 内容：手动触发 weekend_calibration 周窗重放补 09-16→今；查 09-19 周末窗未跑原因（调度器
  排班 or 任务失败）；复通后接一条"周窗未按时产出"告警。
- 规模：0.5 人日。依赖：无。风险：分钟/tick 富化重跑耗资源，按原任务幂等语义重放即可。

### S2（P0）cohort 矛盾核对+落地闸合拢
- 内容：核对"已接线 Owner 批 2026-09-21"声明的真实落地状态（表 DDL 是否 apply 过/任务登记
  在哪个真源）；缺则补 apply_market_tables_ddl 建 c1_backtest.cohort_daily_ledger+tasks.yaml
  登记 cohort_ledger_daily（走 schema-as-code+调度登记正门）。
- 规模：0.5-1 人日。依赖：Owner 对"接线声明 vs 现状"矛盾表的确认（属登记纠偏，非新裁定）。

### S3（P1）emotion_index 主体施工（建议规模最大的单件）
- 内容：按骨架设计稿 v0（六成分+等权+close_final/pre_open 两 stage+契约字段）施工：
  schema-as-code 新文件→apply→聚合器模块（src/zephyr/alt_data/ 或新域，走
  construction_workflow_policy 十五步+depgraph 登记+能力反查）→调度接线（盘后
  close_final 槽+盘前 pre_open 槽）→两卡冻结后考试。
- 规模：3-5 人日（含红蓝两轮）。依赖：S1（C1/C2 有料）；考试卡 Owner 点头。
- 拆批建议：S3a 表+聚合器 2-3 日；S3b 调度+首跑 1 日；S3c 考试+判档 1 日。

### S4（P2）两融备胎补史
- 内容：margin_trading 深历史（tushare 备胎通道，仓内已有同族配方）回补至≥3 年，凑 C5
  分位窗≥250 日；近端滞后维持 as-of 语义不再追。
- 规模：1 人日。依赖：数据源配额；RULE-DATA-OPS 三步验证。

### S5（P2）新闻情绪 LLM 分支接线
- 内容：nightly_sentiment_window 的 data_source=llm 分支实装（走 LSG 网关）+与 rule 法双轨
  落库对照一周；C6 成分暂仍用 rule 值，LLM 值通过对照期后再切。
- 规模：2 人日。依赖：LSG 通道配额；Owner 对 LLM 打分 prompt 冻结纪律的认可（外部文册 §1.3
  的版本漂移告诫）。

### S6（P2）sentiment_panel 词表漂移登记修正
- 内容：DDL 注释 metric 词表补 cb_conversion_premium_median（或建独立 metric 词表注册），
  schema 文件一处改动，零数据迁移。
- 规模：0.25 人日。依赖：无。

### S7（P3）盘中 stage 升级评估（本期不做）
- market_breadth_snapshot 采样密度达标后再议 intraday_vN；本线维持 close_final 真源。

## §3 交 Owner/Max 的判定项（发现的问题，非本班可自裁）

1. **cohort 接线矛盾**（G2）：代码注释声明已接线 vs 表未建+任务未登记——请确认属"声明超前"
   还是有其他真源（如在别的调度层），纠偏方案二选一。
2. **daban 断供 6 日的运营影响**：板块线与本线 C1/C2 同断——是否授权 S1 立即复通（只读重放
   幂等，但涉及盘后任务手工触发）。
3. **考试卡草案 v0** 两张（见 prereg_exam_cards_v0.md）：开工冻结前请过目判定门与 INSUFFICIENT
   预登记逻辑。
4. **骨架 v0 六成分集与等权方案**：契约 v0.1 框架内的自由度（成分增减/权重）请定调。
5. **fear_greed 异轴**：本班维持禁用红线（t0 判例）；如 Owner 想做"跨市场辅助确认"可选项，
   须显式新裁定，本班不自行开。

## §4 全资产净零声明

本班新增 6 个文档（本目录）+0 代码+0 注册表+0 规则；探针脚本在 .runtime/tmp（会话垃圾，
不入库）。无替代/合并对象（全新战役文件夹）；未新增任何 gate/规则/计划任务。

## §5 挖干补遗轮新增（2026-09-22 深夜）

### 新增缺口

| # | 缺口 | 证据 | 级别 |
|---|------|------|------|
| G9 | **能力反查索引漏报**：capability_lookup 查 "sentiment 情绪" 未命中 sentiment_cycle/market_sentiment_analyzer/youzi_relay_emotion_engine/F23 任一件——若非 Owner 质询触发补挖，emotion_index 差点在不知存量温度函数的情况下重复施工 | 本班实测命中面 vs 代码普查 | **P0**（治理面，影响所有后续反查） |
| G10 | **三情绪模块同域簇待内收判定**：sentiment_cycle（含 compute_sentiment_temperature）/market_sentiment_analyzer/youzi_relay_emotion_engine 三枚举并存+emotion_index 拟新建——按"同真源可派生→必并"铁律，施工前必须判定 | sentiment_cycle 头注释自曝三枚举并存 | **P0**（阻塞 S3 开工） |
| G11 | daban 断供期替代源半解：limit_up_down（→09-22 通）可替代涨停家数，但连板/炸板/晋级率无替代 | 盘点册 §8.4 | 并入 G1 |
| G12 | 竞价情绪成分原料实证通（auction_snapshot 26.6 万行/auction_book 303 万行→09-22），骨架 auction stage 可从预留升 v0.2 挂载 | 盘点册 §8.1 | 并入 S3 v0.2 |
| G13 | 研报评级情绪成分候选：research_report 146,769 行（rating/rating_change 在），机构情绪代理未入 v0 | 盘点册 §8.1 #20 | P3 候选 |

### 新增施工建议

- **S8（P0，前置 S3）情绪资产内收判定会**：Owner/Max 主持，议题=三枚举收敛+emotion_index 与
  sentiment_cycle 合并边界+成分内核共用。产出=判定结论一条（可裁可并可分层）。规模 0.5 人日
  （纯判定，无施工）。

### 交 Owner 判定项追加

6. **G9 能力反查漏报**：sentiment 族五件不在反查索引——请批索引重建（归治理班，本班不施工）。
7. **G10/S8 内收判定**：emotion_index 与 sentiment_cycle 是"温度计与档位计并存（共用内核）"
   还是"必并"，请定调——本骨架稿 §8.3 已备初判框架待批。

## §6 施工班终态（2026-09-22 深夜，全线开工令执行结果）

| 项 | 终态 | 证据 |
|----|------|------|
| S1 daban 复通 | **完成**：integrator run 周窗重放 09-01→09-22，事件表 936→1454 行+负载表 574 行，逐日齐；监控=既有 catchup_guard（weekend_calibration 7 日无 SUCCESS→overdue 检测面已在），零新增件 | CH 探针逐日行数 |
| S2 cohort 闸合拢 | **完成**：admin 通道建表（writer 无 c1_backtest 建表权被 ch_writer 吞错——探针抓出）+tasks.yaml 登记 cohort_ledger_daily+writer Date 列 str 假失败 bug 修复（22 测绿）+首跑 160 行四人群落库 | c1_backtest.cohort_daily_ledger |
| S3 情绪指数主体 | **完成**：builder 模块（277 行纯计算）+schema DDL-as-code+admin 建表+provider 路由分支+双任务接线（close_final/pre_open）+品类/翻译/depgraph 登记+432 测绿+双 stage 首跑 33 行 | c1_market.emotion_index |
| S8/G10 内收判定 | **完成**：裁定#400 入册（并存分层+内核单源化两硬约束；两枚举收敛移交治理班） | ruling_registry |
| 考试 | **完成**：卡冻结 v1.0+实跑判档（卡A 主判 INSUFFICIENT 预期兑现+W_core 观察档反向 RankIC-0.209；卡B C3 KEEP、C4/C6 NO_SIGNAL、C1/C2/C5 INSUFFICIENT） | exam_report_v1.md |
| S4 两融补史 | **登记+跳过**（Owner 框架）：tushare 无 margin 能力，需新建外部 API 通道（配额/限流风险），C5 INSUFFICIENT 已被契约吸收，留数据线另令 | 本节 |
| S5 LLM 分支 | **完成（factory-off）**：news_llm_scorer 适配器（nlp_inference×OllamaChat，LSG 内置）+夜间批接线+3 测绿；旗标 data/runtime/nightly_sentiment_llm.enabled 出厂不存在=规则法零变更；**启闭=Owner 门位** | tests/intelligence |
| S6 词表漂移 | **完成**：data_asset_registry evidence 注记实证；schema 注释修正留 Owner（human_only） | data_asset_registry |
| S7 盘中 stage | **维持不做**（原判定：宽度快照极浅；auction 原料已实证通，v0.2 挂载位升级） | 骨架稿 §8 |
| G9 反查索引漏报 | **移交治理班**（裁定#400 同案）：翻译条目在册（27 处）但 lookup 相关性面不打分——引擎级缺口 | 裁定#400 |

**判据备注**：S4/G9 属"遇到堵塞无法跳过的登记项"与"引擎级治理缺口"，均按 Owner 授权框架
登记处置路径，非本班可终局；S5 启闭属宪法 §5.2 flag 出厂翻转门位，交付物=开关本体。
