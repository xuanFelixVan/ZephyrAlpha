---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——其余sleeve选股链
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：其余sleeve选股链（P39）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_core/strategies/event_driven_sleeve_strategy.py`
- TDM 节点: TDM-E-L3-07-3（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-L05-001；本批对象锚点文件为事件驱动 sleeve（"其余 sleeve"族代表）
- 生产调用方: **有：StrategyRegistry 注册（strategy_base.py:150 子目录扫描）+ framework_composer 成员路由真实接线（:57-59 经 event_sentiment_adapter.build_event_weight_panel 喂载荷，T1A-1）+ decision_gate:233 sleeve 矩阵 + api_server:532 条目（自注"默认参数零成交"）——非孤儿**
- 测试文件: `tests/pf_core/test_eventdriven_sleeve_strategy.py`（10 用例，本班次实跑 10/10 绿）

## 1 对象快照

256 行事件驱动 sleeve：事件评分（compute_event_score 族，design 态依赖已如实标注 #ARCH-NLP-PIPELINE-001）→噪声/利空过滤（score<0.2 剔除）→盘中异动确认（负向异动剔除、降级放行）→Top-N 比例归一+max_single(0.10) 截顶，urgency=next_open。与 P37 同骨架（归一化+截顶只减不增不变量同款）。依赖成熟度声明诚实（INVARIANTS:8 + metadata:243 双处）。测试覆盖：过滤/异动/异常契约。排除项：event_score 与 event_anomaly_detector 内部深审（各自域对象）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：归一化+截顶与 P37 同式正确（:166）；过滤语义：`score<SIGNAL_NOISE_THRESHOLD` 一式合并"|score|<0.2 噪声"+"score<0 利空"两文档条目（负分同样落此支）——输出等价但代码与 docstring 字面不等价 | event_driven_sleeve_strategy.py:197-199 | P3 | 对照 :37-38 docstring 与 :198 |
| A 深度 | 边界②：NaN score 穿过噪声门（NaN<0.2=False）后被外层 `score>0`（:152）静默剔除——fail-safe 但无日志（NaN 事件股无声出局）；EventScoreError/EventAnomalyError 单标的剔除+告警（:191-195,207-209）契约落地好 | :152,191-209 | P3 | 造 NaN score 观察静默剔除 |
| A 深度 | 依赖成熟度③：核心评分引擎 event_score=design 态（NLP 管道未闭环登记 #ARCH-NLP-PIPELINE-001，:29-33,243 双处披露）——**sleeve 生产路由已活而依赖引擎未闭环=带病可运行风险**：design 态评分质量无背书即进 composer 成员面板；声明诚实但风险本身在册 | :29-33,243 | P2(依赖未闭环) | 对照 #ARCH-NLP-PIPELINE-001 状态 |
| B 上游 | checklist #6 断供：事件负载由 event_sentiment_adapter 批产（composer 路由 :59）；异动确认负载可选——缺 intraday_returns 时**跳过确认直接放行**（:204 只查双序列非 None）——确认阶段缺数据=无确认放行（方向：放行而非拦截，与"异动确认"名义语义有落差，声明在 :201 注释） | :201-211 | P3 | 只喂 event 不喂 returns 观察放行 |
| C 下游 | composer 成员面板→组合权重；selection confidence 占位（:248-253 声明诚实）；api_server:532 自注"默认参数零成交"=运行实态披露；上游收敛编排 run_event_funnel 待接线（:76-81 TYPE_CHECKING 可发现性声明——ORPHAN-MODULE 治理手法正确） | :76-81 | 通过 | — |
| D 旁系 | checklist #4 双承载：与 P37 打板 sleeve 骨架级同构（generate/select/_placeholder_confidence 三件套复制式相似约 60 行）——**第三处 multifactor_sleeve 同构=三份 sleeve 骨架复制**（三行相似不抽象，整套重复实现应登记合并建议：BaseSleeveMixin 抽归一化/截顶/占位置信度）；事件过滤 |score|<0.2 与 P28/P35 的置信度门是三套事件阈值承载（0.2 评分/0.7 置信/3% 反应），口径各异用途不同，非双算但族内对齐文档缺 | :123-175 vs daban_sleeve_strategy.py:410-467 | P3(合并建议) | 对照三 sleeve 文件骨架 diff |
| E 对抗 | 五问：①静默失败=NaN 静默出局（上述）；降级放行无日志（:201）②假阳性=design 态评分当真（依赖未闭环案）③断供=事件负载断供→composer 面板空→死成员披露机制（composer:648 矿脉实证已治）④重触发幂等⑤时序=next_open 无盘中时序面 | :152,201 | P2(同依赖案) | — |
| F 新鲜度 | 事件驱动选股（PEAD 谱系）+ 异动确认两段式与业界事件策略常规一致（对照见 rpt_p28/rpt_p30 F 轴同族检索）；**对等已有** | 同族结论（URL 见 rpt_p28 §3） | 通过（同族复用） | — |

## 3 SOTA 对照

- 对等已有：事件评分+负向异动剔除+噪声阈值为事件策略常规结构；无立卡/驳回新增（同 P28 结论）。

## 4 缺陷清单

1. P2：**依赖引擎 event_score=design 态而 sleeve 生产路由已活**（#ARCH-NLP-PIPELINE-001 未闭环）——评分质量无背书进组合面板；建议=composer 侧对该成员加"依赖未闭环"降权/披露标记，或 NLP 管道闭环前排期；验证法=对照登记项与 composer 成员列表。
2. P3：与 P37/multifactor_sleeve 三份骨架复制（归一化/截顶/占位置信度）——登记 BaseSleeveMixin 合并建议（轴 D 整套重复实现条款）；验证法=三文件 diff。
3. P3：NaN score 静默出局无日志；异动确认降级放行无日志——两处补 debug/warning。

## 5 挂起疑问

- event_score design 态的当前评分输出是否有任何实盘/仿真数据背书——若为零，api_server"默认参数零成交"实为依赖未闭环的下游表征，二者应并案。

## 6 完备性自评

六轴全查（F 同族复用）。长尾：①event_score/event_anomaly_detector 内部未审（各自域）②event_sentiment_adapter 载荷映射质量未审（T1A-1 交付物）③10 测试无 NaN/降级放行 case。

## 7 收口裁定（收口方填）
