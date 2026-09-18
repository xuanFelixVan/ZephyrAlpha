---
ttl: task_bound
doc_type: report
title: 深度审查报告——锚定状态机（D02）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：锚定状态机（D02）

- 状态: **已审**
- 级别: P1｜类型: 算法（裁定#229 锚定风险四档）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/core/anchored_state_machine.py:142(build_states)`（204 行全文通读）
- 生产调用方: `src/zephyr/data/implementations/internal_compute_provider.py:108,472,586-623`（capability "anchored_state"→表 c1_backtest.regime_state_anchored）、`scripts/ch/build_anchored_state_history.py`、`scripts/backtest/validate_p0_discrimination.py`、`compare_state_dualrun.py` 等 P0-002 验收脚本族
- 测试文件: `tests/zephyr/regime/test_anchored_state_machine.py`（134 行，注意在 tests/zephyr/regime/ 而非 tests/regime/）

## 1 对象快照

- 审查范围：纯函数核（classify_state/compute_features/build_states）+ IO 边缘（load_close/run_compute）。排除项：验收脚本族与 DDL（归 P0-002 验收链）；裁定#229 的语义判决本身不在复审范围（本审查只验实现与声明一致）。
- 材料包缺项声明：数据画像未取；验收实况数字（spread IS +0.26/OOS +1.73、全样本 +0.49 未达冻结线 1.0）引自模块 docstring 自述未复算。
- 测试覆盖概况：纯核覆盖良好（四档边界/确定性/全态可达/warmup NaN/态迁移随波动变化）；缺口：classify_state(NaN) 无测试、load_close/run_compute IO 路无测试（可理解，IO 薄）。
- 变更热力：2 次，域内最低——低返工，符合 design 期新模块画像。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 classify_state 对 NaN 判 **r4（高风险）**：NaN 与三阈值比较全 False 落末档——build_states 有 dropna 前置保护，但公开纯函数直调即误判"最高风险"；静默危险方向 | anchored_state_machine.py:98-109 | P2 | `classify_state(float("nan"))` → "r4" |
| A | F-A2 F1 同口径公式**第二份实现**：hv20=log diff 20 日 std×√252 + 250 日 rank(pct) 与 market_features.realized_vol_pct 逐行同构，无双份一致性保障（checklist#4 家族：一处改窗两处漂移） | anchored_state_machine.py:123-125 ↔ market_features.py:73-75 | P2 | 两函数喂同一序列对拍（当前应逐位相等） |
| A | F-A3 _WARMUP 常量定义后代码零引用（仅 docstring 叙述）——warmup 实际由 rolling NaN 自然产生；若未来有人"用 _WARMUP 截断"，max(120,270)=270 恰好正确，纯冗余非缺陷 | anchored_state_machine.py:81,119 | P3 | grep _WARMUP 全文件 |
| A | F-A4 边界语义：阈值含左侧（vol_pct≤0.30 归低档 r3）与测试锁定一致；[0,1] 阈值全覆盖→四态按构造可达，死态清理不变量成立 | anchored_state_machine.py:103-109; tests:44-73 | 已查无 | test_full_coverage_of_feature_space |
| A | F-A5 load_close docstring"热身缓冲到 2019-04"与实际不符：2016-06-01+270 交易日≈2017 年中；疑为验收窗起点口径残文——文档漂移 | anchored_state_machine.py:166 | P3 | pd.date_range 工作日推算 |
| B | F-B1 输入唯一源=000300 收盘（硬编码 start="2016-06-01"），NULL close → float() ValueError 崩=fail-closed（合规）；行情断供 → RuntimeError 拒产出（:173-174 合规，不判中性） | anchored_state_machine.py:165-182 | 已查无 | 空 tsv 场景 |
| C | F-C1 消费方：生产经 internal_compute_provider capability（"anchored_state"登记注记"声明后补（954b15ce9e 批欠账）"——注册滞后已补）；表消费=验收/对比脚本族。爆炸半径=P0-002 验收链与双跑对比，不直接触仓位 | internal_compute_provider.py:108,586 | P3 | grep regime_state_anchored 消费清单 |
| D | F-D1 **r1-r4 词表与 D01 撞名不同义**：D01 锚定后 r3=高波/强趋势、r4=负斜率阴跌；本模块 r3=低风险(≤0.30)、r4=高风险(>0.80)——同域同标签两套语义（INVARIANT 自认"冻结链字母序原样适配"）；跨表 join/归因/报表若按标签直连必错，且无机械拦截 | anchored_state_machine.py:35-39,86-91 ↔ regime_detector.py:42-47,210-218 | P1 | 两模块 STATE 映射并排比对即见冲突；建议词表加前缀（如 a_r3）或登记显式映射表 |
| D | F-D2 与 D01 的关系口径：本模块=裁定#229 "态层只承担风险判别"的替代实现，与 D01 HMM 4 态并行存在（compare_state_dualrun 脚本佐证）——双态系并存是裁定设计而非漂移，但 D01 docstring 锚定节（"跨 refit 态身份可比"）与本模块"零拟合零重估"是同一病灶的两剂药，终局单一真源归属未裁定 | 模块 docstring:25-44 ↔ regime_detector.py:49-67 | P2 | 读 compare_state_dualrun 输出契约 |
| E | F-E1 静默失败排查：run_compute 空结果 RuntimeError 拒产出（fail-closed 好）；build_states 空输入返回空 DF 不抛（CLI 侧是否判空未审，脚本族归验收链） | anchored_state_machine.py:189-190 | 已查无 | — |
| E | F-E2 重跑幂等：全量重建单批 last_key=""，无增量状态——幂等成立；时序依赖 SQL ORDER BY trade_date 升序（:171） | anchored_state_machine.py:185-204 | 已查无 | 双跑 build_states assert_frame_equal（tests:116-120 已锁） |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 波动率分档风险择时（vol regime → 风险敞口） | **对等已有**——vol-managed 组合文献主线（低波减仓→alpha）与本项目"态层只做风险分档"语义一致；本项目离散阈值档 vs 文献连续波动目标化为实现变体 | [Moreira & Muir 2017, Volatility-Managed Portfolios, Journal of Finance](https://amoreira2.github.io/alan-moreira.github.io/VolPortfolios_published.pdf)（JSTOR 页 [26652549](https://www.jstor.org/stable/26652549)；NBER WP [22208](https://www.nber.org/papers/w22208)，2017） |
| 2 | 实时可实施性（PIT）警告 | **对等已有（支持本项目 PIT 选型）**——Cederburg et al. 2020 JFE 指出 vol-managed alpha 对实时可实施性敏感；本项目 rolling rank 严格 PIT 与该警告对齐 | [Cederburg, O'Doherty, Wang & Yan 2020, JFE](https://www.sciencedirect.com/science/article/abs/pii/S0304405X2030132X)（ScienceDirect，2020） |
| 3 | 阈值型锚定替代 HMM | **对等已有**——结构化阈值态（零拟合）回避 label switching，与 rpt_d01 F 轴"emission 参数重标"属同族替代谱系；项目探针实证（波动轴双段稳定/趋势轴不稳）是自有贡献非文献复刻 | 交叉引用 rpt_d01 §3.2（MDPI Wang et al. 2020）；模块 docstring 探针记录 |

## 4 缺陷清单（按严重级）

- **F-D1（P1）r1-r4 撞名不同义**：现状=两套四态系统共用 r1-r4 标签且语义不同（D01 r3=高波趋势 vs D02 r3=低风险）→ 证据=两文件常量区并排 → 影响=跨系统 join/归因/报表标签直连必错、人读报告混淆；爆炸半径=验收链与任何未来把 anchored 表当 D01 态用的消费方 → 建议修法=①本模块产出加来源前缀或独立词表常量；②消费方（validate_p0_discrimination 等）登记显式映射；③capability 卡片写明"非 D01 词表" → 验证法=两常量区并排比对+grep 消费方对 dominant 的解读注释。
- **F-A1（P2）NaN→r4 危险默认**：建议 classify_state 首行 NaN 显式抛/返 None → 验证法=单行复现。
- **F-A2（P2）F1 公式双份承载**：建议 compute_features 改调 market_features.realized_vol_pct（或反之抽公共函数），消灭双真源 → 验证法=同序列对拍当前相等，重构后再对拍。
- **F-D2/A3/A5（P3）**：终局真源归属、死常量、docstring 漂移——常规队列。

## 5 挂起疑问

1. 验收实况"全样本 spread +0.49 未达冻结线 1.0（诚实 pending）"——判据契约变更（收益判别→风险判别）是否已经 Owner 门位裁定落章，docstring 称"留 Owner 门位裁定"，状态未在模块内闭环（裁定#229 登记状态归收口方核）。
2. 与 D01 双态系的终局归属（HMM 锚定 vs 结构阈值）未裁定——compare_state_dualrun 的对比结论去向需验收链确认。

## 6 完备性自评

- 六轴全查：A（阈值数学/warmup/NaN/边界/确定性全过）、B（单源输入+fail-closed）、C（生产注册位+验收消费方）、D（撞名不同义=本报告主发现+双态系并存）、E（幂等/时序/静默失败查无或合规）、F（3 条带来源）。
- 长尾清单：①IO 路（load_close/run_compute）无自动化测试；②验收脚本族（validate_p0_discrimination 等 6 个）未审；③裁定#229 原文与探针数据未复算（材料包缺项）。
