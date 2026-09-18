---
ttl: task_bound
doc_type: report
title: 深度审查报告——F01 Alpha信号管线（AlphaSignalPipeline）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：F01 Alpha信号管线（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 管线编排
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/pipeline.py:102`（类 AlphaSignalPipeline）
- 生产调用方: **无**（仅 re-export shim，见 C-01；作业簿预填的 `_g04_ops_check`/risk cross_asset 均为 shim 或幽灵映射，tests/pipeline/test_alpha_signal_pipeline.py 未在仓内确认存在，grep tests/ 无 AlphaSignalPipeline 行为测试命中）
- 测试文件: **未发现有效专属测试**（pipeline.py header [TESTS] 为空）
- 变更热力: 2026 年以来 **29 commits**——本批 12 对象中最高热文件
- 材料包缺项: 运行时证据包/数据画像缺（对象疑似不运行，见 C-01，日志取证无对象）

## 1 对象快照

五阶段管线（discovery→compute→synthesis→validation→capital_allocation）：线程池并行算因子、内置篡改守卫、置信度聚合、极端检测、降级路由。排除项：FactorSignal/SynthesizedSignal 契约本体（shared/contracts，另件）；SignalSynthesizerBase（G01 另审）。测试覆盖：零专属测试——对 29 commits 热文件，覆盖空洞本身即发现。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **run() 信号产出被丢弃**：synthesized 是局部变量，run() 只返回 PipelineResult（计数/置信度），信号本体不返回不落库——"算了就扔" | pipeline.py:248-260, 86-99 | P1 | 读 run() 返回类型字段清单 |
| A | **AS-CT-002 幂等性契约违反**：idempotency_key 仅透传 compute_with_key，同 key 重放全量重复执行，无去重/状态 | pipeline.py:222-231, 418-424 | P1 | 同 key 双跑比对 factors_computed |
| A | **跨 run 状态污染（复算实锤）**：_degraded_reasons 不随 run() 重置；复算：run1 极值信号→run2 全正常仍 degraded=True 且 errors 带 run1 的 5000 极值原因 | pipeline.py:126, 254, 365, 389 | P1 | 复算脚本（本审查已跑通）：极值因子+直通合成器连跑两次 |
| A | **极端检测 dict 盲区（复算实锤）**：getattr(s,"signal_value",0.0) 只认属性对象，dict 载荷（含伪合成兜底 dict）全部漏检；复算：signal_value=99999 的 dict 信号 degraded=False | pipeline.py:358-369, 449-464 | P1 | 复算脚本：dict 返回合成器 99999（已实测） |
| A | 伪合成兜底伪造置信度：空置信列表默认 0.5——无中生有的质量分进 confidence/degraded 判定 | pipeline.py:456, 466-478 | P2 | 造无 confidence 属性的信号跑 run() |
| E | builtins 守卫归因错位：快照一次全局比对，并发下他线程篡改算在刚完成因子头上 | pipeline.py:301, 320-333 | P2 | 双因子并发+延迟篡改，看归因 |
| B | _compute_single 优先无参 compute()，FactorBase.compute(data) 协议必 TypeError；register_factor 不做协议预检（:276 注释自认不兼容却仍放注册） | pipeline.py:276-284, 418-424 | P2 | 注册 FactorBase 子类后 run() 看 factors_failed |
| C | **生产链路裁定弃用本管线**：backtest.py 裁定注释"跳过已坏的 AlphaSignalPipeline"；其余引用全为 re-export shim（factor/alpha_signal_pipeline.py、signal_fundamental/__init__.py） | backtest.py:441; factor/alpha_signal_pipeline.py:26-40 | P1 | grep 生产调用方=0（本审查已 grep） |
| C | **幽灵引用（模式#9）**：cross_market_data_adapter lazy map 指向已删除模块 zephyr.shared._cross_layer.alpha_signal_pipeline，访问即 ModuleNotFoundError | cross_market_data_adapter/__init__.py:27; shared/_cross_layer/ 目录现仅 ml_experiment_pipeline.py | P2 | `python -c "import zephyr.risk.cross_asset.cross_market_data_adapter as m; m.AlphaSignalPipeline"` |
| D | Stage5 资金分配纯标记无逻辑；AS-CT-001~005 契约 vs 实现度漂移；MATURITY=production vs 骨架实质 | pipeline.py:24, 256-259 | P3 | 读 CAPITAL_ALLOCATION 分支 |
| D | 黑名单=类名子串匹配，改名即绕过；_SUSPICIOUS_FACTORS 只写不读 | pipeline.py:109-118, 199-209 | P3 | grep 消费方=0 |
| E | _SUSPICIOUS_FACTORS 类级可变状态 + degraded_reasons 实例级累积：多实例/多 run 交叉污染 | pipeline.py:119, 126 | P2 | 双实例交替 run 观察串扰 |

## 3 SOTA 对照

- 管线编排件（非数学算法核心）：与业界因子-信号编排对照（qlib 信号流等）——**受阻未搜**（本批检索预算用于三个数学核心 WQ101/保形/TA-Lib；且本件已裁定弃用，立卡无意义）。
- 结论：**驳回**（建议按孤儿裁定走退役而非修复）。

## 4 缺陷清单（按严重级）

1. **P1 孤儿+信号丢弃双证**：生产调用方=0（唯一非 shim 引用是"跳过已坏"裁定注释 backtest.py:441）+ run() 不交付信号本体（:248-260）。爆炸半径：无（不运行）；但 29 commits 持续维护死管线=持续成本+MATURITY=production 误读风险。建议：登记退役（孤儿裁定），或最小修复=PipelineResult 增加 synthesized 载体+每 run 重置 degraded_reasons。验证法：grep 全仓生产 import。
2. **P1 幂等契约违约**：AS-CT-002 明文幂等，实现零去重。验证法：同 key 双跑。
3. **P1 状态污染 + dict 盲区**（均复算实锤）：降级机制两个核心通道双双失真，修复前任何"降级=安全"的下游解读不可信。验证法：§2 复算脚本。
4. **P2 幽灵引用**：cross_market_data_adapter/__init__.py:27 死映射。验证法：惰性访问该属性。
5. **P2 组**：伪合成 0.5 伪造、builtins 归因错位、FactorBase 协议错配、类级可变状态。
6. **P3 组**：Stage5 空转、子串黑名单、production 标注漂移。

## 5 挂起疑问

- "跳过已坏的 AlphaSignalPipeline"（backtest.py:441）未检索到 ruling_registry 对应条目——"已坏"事故本体待 Owner 补锚。
- builtins 守卫原始威胁模型（5.135 治标注释）无裁定锚，去留待裁定。

## 6 完备性自评

六轴全查（F 记受阻）。长尾：①PipelineResult 字段多线程写竞态未深究（as_completed 主线程收集，风险低）；②5.76.1 PipelineError 统一修复的调用方回溯未展开。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
