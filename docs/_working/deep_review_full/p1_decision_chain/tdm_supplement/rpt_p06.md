---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——宏观环境传感器（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：宏观环境传感器（P06）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/alt_data/policy_expectation_analyzer.py`
- TDM 节点: TDM-E-L1-S0
- 生产调用方: **生产代码零调用方**（孤儿，见 C-1）
- 测试文件: tests/alt_data/test_policy_expectation_analyzer.py（实跑通过）

## 1 对象快照
MOD-ALT-010 全文件（360 行）：政策表态采集+关键词扫描+事件日历+LLM 预期打分（[-1,1] 闭合）+ETF 份额异动（国家队语义）+人工审核队列。全依赖注入纯内存件。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 变动率 (new-old)/old 分母正校验；关键词命中词表序确定性；LLM 打分 [-1,1] 闭合+bool 拒+NaN 拒；边界（空语料/乱序快照/同日异额冲突）全 fail-closed | :137-147,263-267,302-318 | 已查无 | 传 float 1.5/NaN/bool 逐项应抛 |
| A 深度 | 持仓异动=逐期相邻比较：两期各 +6% 累计 +12% 永不触发（阈值语义是"环比"非"较基线"）——口径自洽但需 Owner 知情 | :319-331 | P3 | 造 1.06/1.1236 两快照看无 change |
| B 上游 | 全注入设计（statement_source/llm_scorer 无内嵌）；llm_scorer 为裸 callable，**接线层必须包装 LSGSecurityGateway（宪法 §9.2）本件无强制**——误接裸 LLM 则 GATE-20 拦截在别处发作 | :123-127 | P3 | 接线评审时核对 llm_scorer 包装链 |
| C 下游 | **孤儿**：`grep -rln "PolicyExpectationAnalyzer" src/ scripts/` 零命中（仅本文件）；CONSUMERS"运行时装配批"未落码；signal 漏斗/人工审核路由不存在消费端 | grep 实证 | **P2** | grep 命令如上 |
| D 旁系 | 与 policy_registry/policy_theme_mapper/llm_market_interpreter/sentiment_engine 分工文档化（:27-30），无双承载 | :27-30 | 已查无 | 读四邻居 blueprint |
| E 对抗 | 五问：①review_sink 异常吞（留痕丢失 P3）②幂等去重（statement_id）好 ③审核队列纯内存——进程重启队列清零且无人知（无持久化）④重复采集安全 ⑤clock 默认 naive now（同 P03 时区疑点）；另 statements() 排序遇 tz-aware/naive 混存 TypeError | :148,278-282,195 | P3 | 注入 review_sink 抛异常；重启进程查 pending_review |
| F 新鲜度 | **受阻**：中文金融政策情绪 NLP 口径检索遭服务限流（429），按纪律如实记受阻不算查无 | — | — | — |

## 3 SOTA 对照
受阻（检索限流，见轴 F）。

## 4 缺陷清单
1. **P2 孤儿**：MATURITY=production 但全仓零调用，政策预期差信号链整体未运转（采集→打分→人工审核全悬空）。建议：装配接线或降级 maturity 标注。验证法：grep。
2. P3 审核队列无持久化（重启丢失）。
3. P3 llm_scorer 无 LSG 包装强制。
4. P3 环比口径/naive clock/tz 混存排序（低危组合）。

## 5 挂起疑问
- "国家队持仓"语义（ETF 份额异动≥10%）的推断属性强（份额变动≠国家队增减仓），is_inferred 标注只在 ExpectationSignal，HoldingChange 无类似标注——建议 Owner 评审是否补标注。

## 6 完备性自评
六轴全查。长尾：statement_source 真实数据源形态未审（未接线无对象）。
