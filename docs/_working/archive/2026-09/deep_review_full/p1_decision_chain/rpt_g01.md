---
ttl: task_bound
title: 深度审查报告——G01 基本面信号合成器（SignalSynthesizerBase + combiner 域）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：G01 基本面信号合成器（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 抽象基类+combiner 域（stub 嫌疑专项）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/synth/signal_synthesizer.py:58`；旁及 `combiner/__init__.py`、`combiner/impl/__init__.py`、`gen/aggregator_base.py`
- 生产调用方: **零具体实现、零直接消费**（F01 pipeline 仅消费基类 _registry，而 registry 恒空）；作业簿预填 tests/trading/integration/test_signal_synthesizer_contract.py 未在仓内确认（grep tests/ 无该文件名命中）
- 测试文件: 未发现有效测试
- 变更热力: 2026 年 **23 commits**（第二高热）——高频返工于一个零实现基类
- 材料包缺项: 运行时证据包缺（对象不运行）

## 1 对象快照

SignalSynthesizerBase：抽象 synthesize()+归一化 [-3,3]+方向阈值+默认幂等键+__init_subclass__ 注册表。combiner 域=两层 __init__（54+34 行）纯 re-export facade（SignalAggregatorBase/CapitalAllocatorBase/SynthesizedSignal 等）。排除项：gen/implementations/default_signal_aggregator.py 数学本体（真实聚合实现在 gen 域；本审读其关键分支作 D 轴对照）。**stub 嫌疑结论：确认**（见 C-01/D-01）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **幂等键含 uuid 违反幂等（复算实锤）**：default_idempotency_key=`syn-{symbol}-{ts}-{uuid4}`，同 symbol+时间戳两次调用键不同（已实测 False）——INV-007"幂等键"契约失效，下游不可去重不可重放对账 | signal_synthesizer.py:116-120 | **P1** | 复算脚本（已实测：k1==k2 → False） |
| C | **全仓零具体合成器（stub 确认）**：grep `SignalSynthesizerBase)` 子类化零命中；`__synthesizer_id__` 全仓零定义→_registry 恒空→F01 管线 _run_synthesis 永远走伪合成兜底（G01↔F01 联动 P1）；combiner/impl 只有 DefaultSignalAggregator（gen 域）+DefaultCapitalAllocator 的 re-export，无 synthesizer | signal_synthesizer.py:76-79; combiner/impl/__init__.py:26-30; grep 全仓 | **P1** | grep `__synthesizer_id__` 与 `SignalSynthesizerBase)` |
| D | **双承载漂移（模式#4）**：synth/SignalSynthesizerBase 与 gen/SignalAggregatorBase 两个"多因子信号聚合"抽象基类并存：签名 synthesize(factor_signals,symbol,as_of) vs aggregate(factor_signals,symbol,idempotency_key)；方向判定阈值 0.2（:108-114）vs >0/SHORT<0（default_signal_aggregator.py:139-140）；归一化 [-3,3] 两处实现——同一概念两处算、两处口径 | signal_synthesizer.py:102-114 vs gen/implementations/default_signal_aggregator.py:126-140 | **P1** | 对读两基类公共 API |
| B | F01 调用契约违约埋雷：pipeline._run_synthesis 传 symbol=""/as_of_timestamp=None（pipeline.py:441）——基类签名要求 datetime（:91-98）；一旦未来注册具体合成器，default_idempotency_key(None) → AttributeError | pipeline.py:441 vs signal_synthesizer.py:91-98, 117-120 | P2 | 造最小合成器注册后跑 F01 pipeline.run() |
| E | **静默不注册**：子类漏写 `__synthesizer_id__` 不报错不注册（:76-79 条件 `in cls.__dict__`）——对比 F05 register 显式 raise；扩展点失败无声 | signal_synthesizer.py:76-79 vs indicator_base.py:197-207 | P2 | 定义无 id 子类，list_synthesizers() 不含且无告警 |
| D | header 漂移：MATURITY=production / [TESTS] 空 / [CONSUMERS] 空 / INVARIANTS none——零实现零测试零调用标 production | :6-14 | P3 | 对读 |
| A | 归一化/方向工具（normalize_signal/direction_from_value）数学简单 ✓；threshold=0.2 无出处锚（经验值无裁定引用） | :102-114 | P3 | grep 裁定注册表 |

## 3 SOTA 对照

- 工程接口件（无算法核心）：等权/置信度/IC 加权聚合策略业界常规（qlib 信号组合惯例）——**受阻未搜**（检索预算用于数学核心；真实数学在 gen 域 DefaultSignalAggregator，其三分支等权/置信/IC 加权为对等常规实现）。
- 结论：受阻如实记。

## 4 缺陷清单

1. **P1 stub 链确认（C-01+D-01）**：合成器基类 23 commits 返工、零实现、registry 恒空、F01 伪合成兜底、gen 域平行实现口径漂移——整条 synth→combiner 链是"有地基无楼宇"。爆炸半径=F01 管线产出失真（若被复活）；治理面=双真源漂移持续发生。建议：Owner 裁定 synth 基类退役（孤儿裁定）或指定 DefaultSignalAggregator 适配注册，二选一终结双承载。验证法：§2 C/D grep+对读。
2. **P1 幂等键违反幂等（复算实锤）**：uuid 分量使键必唯一。建议：键=symbol+as_of+策略 ID 确定性哈希；uuid 只作冲突后缀可。验证法：§2 A-1 复算。
3. **P2 契约违约埋雷 + 静默不注册**。
4. **P3** header 漂移、threshold 无锚。

## 5 挂起疑问

- combiner/__init__.py 的 DegradationMonitorBase `__getattr__` 跨域 re-export（combiner/__init__.py:37-42）消费方未 grep 到——兼容层是否仍有存量消费者待收口方确认。
- MOD-UNK-combiner 的 module_id 未登记态（header 行 1 MOD-UNK 前缀）与"新建 .py 模块须登记大白话简介"铁律的合规性——登记缺失还是有意豁免待查。

## 6 完备性自评

六轴全查（F 受阻记）。stub 专项（作业点题）三重证据闭合：零实现+零调用+双承载。长尾：①CapitalAllocatorBase/default_capital_allocator 属 combiner 域但未列入本对象审查范围（资金分配归 P0 域另批）；②gen/implementations 其余聚合器变体未逐个审。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
