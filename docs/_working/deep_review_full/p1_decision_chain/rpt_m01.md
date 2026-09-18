---
ttl: task_bound
doc_type: report
title: 深度审查报告——M01 次日概率闸（NextDayProbabilityGate）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：M01 次日概率闸（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1（决策链第一道门）｜类型: 闸门
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/ml_forecast/next_day_probability_gate.py:90(ProbabilityGateConfig)(:214 引擎)`
- 生产调用方: **仅 signal_ashare/__init__.py:38 re-export**——grep 全仓无生产 evaluate() 调用方；header [CONSUMERS] 自认"候选（决策链第一道门装配层、模块13）"未接线
- 测试文件: tests/signal_ashare/ml_forecast/test_next_day_probability_gate.py（存在）
- 变更热力: 2026 年 1 commit（新件，低热）
- 材料包缺项: 运行时证据包缺（未接线对象）

## 1 对象快照

动作分档概率门（5 动作封闭集）+8 项动态偏移叠加+钳制 [0.50,0.95]+拦截归因+内存统计+可选 sink 回写；门语义=passed/reason 不抛错。排除项：上游概率生产方（M02/M03，另审）、brier_calibration。数学核心简单（查表+钳制比较），四问聚焦边界与契约。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿（模式#8，已声明型）**：生产调用方=0；模块 docstring 自认"深挖批 min_build_spec 明示缺口，本模块落地"——装配层待集成批。决策链第一道门实际不在链上 | next_day_probability_gate.py:5, 24-26; grep 消费方 | P2 | grep 生产 import（本审查已做） |
| E | **block_sink 异常不隔离**：evaluate() :297-298 sink 异常直接上抛——决策已算出但调用方拿到异常，门语义"拦截不抛错"（:38）被 sink 路径破坏；对比 F02 audit_sink 显式吞（factor_factory.py:356-359），同类两裁 | :296-298 vs factor_factory.py:356-359 | P2 | 注入 raise 的 sink，evaluate 抛异常（决策丢失） |
| A | 数学四问：方向概率口径 t_minus=1−p_up ✓（:264）；偏移求和后钳制 [floor,cap] ✓（:267）；p_up∈[0,1] 含端点+有限校验 ✓（:258-260）；牛熊/量能冲突 fail-closed ✓（:162-168）；基准门槛查表封闭 ✓（:139-146）——**已查无** | 各锚点 | ✓ 查无 | 单测已覆盖主要分支 |
| A（口径） | 牛市 −5% 使放行更容易：方向正确（偏移作用在门槛而非概率上）但语义反直觉——门槛降低=牛市宽松，为 memo 既定口径，留档即可 | :98-99, 30-33 | P3（留档） | 对读 docstring 口径表 |
| B | 上游 p_up 语义未约束校准来源：任何 0-1 标量放行——未校准概率直接进门（Brier 校准在上游 brier_calibration，本件不查）——隐含契约"p_up 须已校准"未文档化 | :254-260 | P3 | 代码走查 |
| A.3/E | 统计 _stats 为内存 dict 无 reset/持久化：block_rate 长周期统计随进程清零（header :8 已声明"内存累计"✓ 一致）；evaluate 非线程安全（dict 累加） | :219-221, 292-296 | P3 | 多线程并发 evaluate 比对 stats |
| D | "对标 Man Group 裁定口径"（:34）外部断言无 URL/裁定锚——引用不核真源风险（模式#15 边缘） | :34-36 | P3 | 检索 ruling_registry 无 Man Group 锚（本审查 grep 未命中） |

## 3 SOTA 对照

- "对标 Man Group"口径：**受阻**——检索预算内未定位到具体公开文献锚（Man Group 旗下 AHL/学术页无既定"拦截归因"公开标准）；记受阻，引用锚缺失转挂起疑问。
- 概率门槛分档（按动作风险敞口分档阈值）为交易风控常规做法，无单一权威源——受阻记。

## 4 缺陷清单

1. **P2 孤儿（已声明型）**：第一道门未上链。爆炸半径：当前无；接线后即决策链核心。建议：装配批接线时同步补集成测试。验证法：grep。
2. **P2 sink 异常击穿门语义**：建议 try/except+审计记录（对齐 F02 audit_sink 纪律）。验证法：§2 E 行。
3. **P3 组**：p_up 校准前提未文档化、内存统计口径、Man Group 引用无锚、线程安全。

## 5 挂起疑问

- "Man Group 裁定口径"的出处（裁定号/文献）待 Owner 补锚，否则应删引用（防模式#15）。

## 6 完备性自评

六轴全查（F 受阻记）。数学四问逐项过（简单查表件，全部 ✓）。长尾：①GateDecision.to_dict 大规模序列化性能（无关紧要）；②stats 的 shortfall 口径（仅拦截样本）与回测门槛合理性分析的衔接未展开。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
