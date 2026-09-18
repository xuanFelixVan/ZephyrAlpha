---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——执行成本反馈与选型回写
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：执行成本反馈与选型回写（P53）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_sor/services/execution_quality_scorer.py:277`（ExecutionQualityScorer）
- TDM 节点: TDM-E-L4-14（stage，config/trading_decision_map.yaml:2492，algo_note 自我声明三零件断链 2026-09-10）
- 生产调用方: **零**——`ExecutionQualityScorer(` 全仓仅自身与 tests；`ex_sor/services/__init__.py:27-31` 仅包级转出口；slippage_analyzer.py:5 / transaction_cost_optimizer.py:5 头注释宣称被本模块消费（反向声明）；**algo_execution_selector.py（MOD-XS-011 选择器）grep quality/scorer 零命中**——TDM 声明的"选择器反馈环"断链在基线仍未接
- 测试文件: tests/ex_sor/test_execution_quality_scorer.py（511 行 37 测试，同批 77 passed 5.52s）

## 1 对象快照

- 范围：ExecutionQualityScorer 全文件（532 行）——四维评分（PRICE/TIME/COST/IMPACT，score=max(0,1-raw/threshold)）+权重合成+verdict 三档+内存历史。
- 排除项：slippage_analyzer/transaction_cost_optimizer 数学归各自对象（本报告只按上游契约引用）；algo_execution_selector 归 L4-06（P50 已审域）。
- 测试覆盖概况：37 测试覆盖各维评分/权重校验/verdict 边界/历史过滤；**无负滑点（price improvement）语义测试、无部分维度 overall 可比性测试**——恰好绕过本报告两个数学发现。
- 材料包缺项声明：运行时证据包未取（生产零调用）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿死码+反馈环断链延续**（checklist #8/#4 双命中）：TDM-E-L4-14 algo_note 自己声明"质量评分器的消费者行写着'选择器反馈环'，但选择器代码还没消费它（断链实证 2026-09-10）"——本审查确认基线（2026-09-18）仍断：selector 零消费、scorer 零生产调用方，模块 header `[CONSUMERS] MOD-XS-011(算法选择器反馈环)`（:5）与 `[MATURITY] production`（:7）双声明与现实不符；TDM 声明的"某算法连续实测比预估差就降权重"闭环=纸面 | execution_quality_scorer.py:5,7；grep ExecutionQualityScorer src/ 仅 services/__init__；grep "quality\|scorer" algo_execution_selector.py 零命中；config/trading_decision_map.yaml:2492-2520 | P2 | 同左 grep 三连；接线后复 grep |
| A | **滑点取 abs() 把有利滑点当不利计罚（符号错误）**：`abs(float(slippage_bps))`（:363）——业界口径负滑点=price improvement（成交优于基准），本实现实测 slippage_bps=-30 与 +30 得分完全相同（均 0.4）：好执行被罚、坏执行与好执行不可分。若未来按声明喂给选择器，**成交质量最好的算法会被系统性错杀降权**——闭环一旦接通即为决策偏移源。total_cost_bps/impact_bps 同样 abs()（:379,386，成本类取 abs 危害较小但同样抹符号） | execution_quality_scorer.py:363,379,386；探针实测两方向得分相等 | P2 | `python -c`: score(slippage_bps=Decimal('-30')) vs score(Decimal('30')) 比较 overall（本次已实测相等） |
| A | **部分维度重整化使 overall 跨单不可比**：_calc_overall 按"已提供维度的权重和"归一（:488-498）——只传 duration_seconds=0 的单据实测 overall=1.0 verdict="good"，而价格/成本/冲击全未知；不同维度覆盖的订单 overall 直接排序=苹果比橘子，verdict 无维度覆盖警示位。Executor 侧若拿 verdict 做分桶统计将系统性失真 | execution_quality_scorer.py:392-398,488-498；探针实测 time-only→1.0 good | P2 | `python -c`: score(duration_seconds=0.0) 看 overall/verdict 与 dimension_scores 长度（本次已实测） |
| B | 默认阈值未经 A 股算法单口径校准声明：TIME 阈值 300s 硬默认 vs 本项目 TWAP 切片间隔 180s（local_order_queue 默认）——父单级执行>5 分钟即 TIME=0 分；COST 30bps/PRICE 50bps/IMPACT 20bps 无 A 股费率结构（佣金+印花税单边）对照锚。BenchmarkProvider 可注入是逃生门但默认值即声明值 | execution_quality_scorer.py:84-87 | P3 | 对照 CST-ASTOCK-001 费率与 180s 切片参数复算典型单 |
| E | 历史无界内存：_history list 只增不清（clear_history 手动），盘后批量跑全订单历史=内存缓涨；实例有状态但无线程锁——并发 score 下 history append 竞态（GIL 下实际安全，风格违例） | execution_quality_scorer.py:312,411,531-532 | P3 | 万单压测看内存；两线程并发 score 后 len(history) 核对 |
| B | score_from_results 与 score 同参透传（:423-464），未承接 SlippageResult/TransactionCostResult 类型——"消费上游结果"实为文档性包装，上游字段提取仍全靠调用方手写（docstring 示例即手写提取），类型安全未兑现 | execution_quality_scorer.py:423-464 | P3 | 对照 score/score_from_results 签名逐参相同 |
| A(亮点) | 权重和=1.0 校验（1e-6 容差）+负权重拒绝；score=max(0,1-raw/threshold) 单调有界无除零（threshold<=0 分支处理）；InsufficientMetricsError 零指标兜底；四维独立可选 | execution_quality_scorer.py:149-166,468-486,392-396 | — | — |

## 3 SOTA 对照

- 滑点符号语义：**立卡候选（修正依据）**——TCA 业界口径 arrival price 基准下负滑点=price improvement 是好执行（Talos《Execution Insights Through TCA》talos.com，2026；CoinRoutes《Measuring Execution Quality Benchmarks》coinroutes.com，2026："Positive slippage can indicate price improvement"——方向语义两平台相反但**双方向必须区分**是共识）。本模块 abs() 抹方向与全部主流 TCA 实践相悖，接线前必修。
- 执行质量多维评分：**对等已有**——arrival price/VWAP/TWAP/Implementation Shortfall 多基准+价差捕获与市场冲击分项是 ACA/Quod/FactSet 类 TCA 平台标准面（acaglobal.com，2026；quodfinancial.com，2026）；本模块四维结构同构，缺基准可配置化深度（单 threshold 单基准）。
- 部分维度归一：**立卡候选**——业界 TCA 报表对缺失维度标 N/A 而非重整化均分（FE Training TCA 教材 fe.training，2026）；建议 verdict 附 coverage 字段。

## 4 缺陷清单

1. **[P2] 反馈环断链+孤儿**（TDM 自我声明在案，本审查确认基线仍断）。建议修法：按 TDM 注释挂"接线随编排批次"，接线前 header CONSUMERS 行改为"计划消费方"；或先在盘后报告（MOD-EX-CORE 执行质量报告）侧消费起来形成最小闭环。验证法：grep 三连（§2 轴 C）。
2. **[P2] abs() 抹滑点方向**。建议修法：PRICE 维保留符号（score 对负滑点给满分或 1+bonus 封顶 1.0），COST/IMPACT 若上游契约保证非负则改 assert 非 null 而非 abs。验证法：本次探针命令复跑，修后 -30 与 +30 得分必须不同。
3. **[P2] 部分维度 overall 不可比**。建议修法：verdict 附 dimension_coverage（如 "2/4"），或 overall 仅在全覆盖时给出、部分覆盖返回 None+分维明细。验证法：time-only 探针复跑看 coverage 字段。
4. **[P3] TIME 300s 默认阈值与 180s 切片口径冲突**。建议修法：默认阈值改由 config/standards 或 CST 注入，并按父单/切片两级分开评。验证法：对照 config 注入后跑典型 TWAP 父单。
5. **[P3] history 无界+score_from_results 名不副实**。建议修法：history 加 maxlen 或落 DB；score_from_results 改收 SlippageResult/TransactionCostResult 强类型。验证法：读签名 diff。

## 5 挂起疑问

- 断链的修复优先级归口：TDM 注释写"缺把三者接成环的接线"但无施工批次号——请收口方登记到 ex_sor 编排批次或声明暂不接（影响发现 1 是修复还是降级为声明修正）。
- slippage_bps 的上游符号约定（SlippageAnalyzer 产出正=不利还是正=有利）未在两模块间显式对齐——本报告按业界 arrival-price 惯例判定 abs() 为错，若项目自定义相反符号则结论仍成立（abs 同样抹方向），仅修法方向相反。

## 6 完备性自评

六轴全查（A 数学四问：四维公式单调有界/边界零指标与 threshold<=0 已测/隐含假设=raw 非负已证伪/A 股口径=阈值未校准；B 上游=SlippageResult/CostResult 契约已查；C 下游=消费方 grep 全仓判孤儿；D 同族=与 slippage_analyzer/transaction_cost_optimizer 三零件分工在案无重复实现；E 五问：静默失败=无异常吞、断供=零指标显式抛、重复触发=score 幂等、假阳性=good verdict 可在 1 维满分时给出（已立发现）、时序=evaluated_at 可注入）。长尾：①selector 侧评分输入接口应长什么样归 L4-06 对象；②真实执行回报数据画像无生产数据；③37 测试的逐断言强度复核只抽查了绕过区（负滑点/部分维度恰好无测试=本报告两发现的成因之一）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
