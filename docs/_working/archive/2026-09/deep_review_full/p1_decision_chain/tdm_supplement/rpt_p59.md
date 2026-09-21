---
ttl: task_bound
title: 深度审查作业簿——可靠度养成与信号健康
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：可靠度养成与信号健康（P59）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_quality/signal_degradation_monitor.py:123`（SignalDegradationMonitor）
- TDM 节点: TDM-F-C3-05（stage，config/trading_decision_map.yaml:4064，注释自认红节点"F 流三空白之三"）
- 生产调用方: **零**——SignalDegradationMonitor 全仓仅自身+tests；`signal_quality/__init__.py:15` 自认"域内待装配模块"；header [CONSUMERS]"运行时装配批"=尚不存在的装配层
- 测试文件: tests/signal_quality/test_signal_degradation_monitor.py（92 passed 同批）

## 1 对象快照

- 范围：SignalDegradationMonitor 全文件（332 行）——三指标（命中率/IC 均值/窗内前后半 IC 衰减）滚动窗（deque maxlen 有界）+worst-of 四级判定（NONE/MILD/MODERATE/SEVERE）+样本不足不判定+alert_router/mark_sink 全回调注入+降权 weight_hint 查询。
- 排除项：degradation_detector（MOD-SIGQC-001，蓝图声明分工=多维滑窗基线对比，本件=轻量阈值监控）——分工声明在 docstring :25-28；signal_quality_benchmark（MOD-SIGQC-006）。
- 测试覆盖概况：92 passed 覆盖分级判定/边界/回调隔离；**无"持续降级期重复告警频率"场景、无 MILD 与 SEVERE 降权力度无差别的语义场景**。
- 材料包缺项声明：运行时证据包未取（生产零调用）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **TDM 节点声明能力仅落地一小片（红节点自认在案，补充量化）**：节点声明"三档递进（等权→月度判准率加权→粒子滤波时变）+滚动 IC+半衰期 hyperbolic 拟合+三选二衰减报警+反馈 L1-AGG 降权+D87 四扩展"——模块实际交付=滚动 IC/命中率/衰减的**阈值监控器**；加权方案/半衰期拟合/三选二/L1-AGG 反馈边全部零代码。TDM 注释已如实声明"红节点（D7-D13 历史判准率加权 src 零实现）"——诚实度合格，本条转为缺口量化存档 | config/trading_decision_map.yaml:4064-4105（含红节点注释） vs signal_degradation_monitor.py 全文（grep 判准率/半衰期/hyperbolic/粒子 零命中） | P2 | 对照 TDM 逐项 grep |
| C | **孤儿死码**（checklist #8）：零生产调用方；header [MATURITY] production 与"待装配"现实矛盾；消费端"凭 weight_hint 降权"的下游（L1-AGG/信号消费端）不存在 | signal_degradation_monitor.py:7,26-28；grep SignalDegradationMonitor src/ 仅 __init__/benchmark 文档提及 | P2 | grep 三连（类/模块/weight_hint 消费方） |
| A | **告警无去重：降级持续期间每次 evaluate 都重发 alert**：_sync_mark 中 `self._alert(report)` 在 `if report.degraded:` 分支内无条件执行（:256），只有 mark_sink 有 `prev is not report.level` 去重——同一信号同一级别在告警通路上每次评估重发。生产评估若随 tick/分钟级调度=告警风暴；mark 去重与 alert 去重不对称更像遗漏而非设计 | signal_degradation_monitor.py:253-262 | P3 | 固定降级窗口连调 evaluate 三次，数 alert_router 回调次数（=3 而非 1） |
| A | **降权力度与级别无关**：weight_hint 只二值（degraded_weight=0.5 或 1.0），MILD（衰减 0.5-0.8 的早期预警）与 SEVERE（IC 符号翻转）同样砍半——早期预警即全额降权，恢复前无梯度；与 TDM 声明的"判准率加权（下限 10%）"精细档位相距远 | signal_degradation_monitor.py:326-328,144 | P3 | MILD/SEVERE 两信号分别查 weight_hint 均为 0.5 |
| A | decay 指标数学：前后半均值相对回落+|early|≈0 退化为 0（防除零，自注）——正确；但窗口仅 20 条时前半=10 条，IC 噪声下 decay 抖动大（10 样本均值差的置信区间宽），无噪声惩罚/显著性守卫，MILD 阈值 0.5 在小样本下假阳性率可观 | signal_degradation_monitor.py:178-193 | P3 | 蒙特卡洛 iid IC~N(0,0.1) 20 条看 decay≥0.5 频率 |
| B | 观测乱序无守卫：observe 不校验 observed_at 单调——乱序喂入时"前后半"时间语义被破坏（deque 按插入序非时间序），decay 判定失真而静默 | signal_degradation_monitor.py:266-282 | P3 | 倒序时间戳喂入对比 decay |
| E | 回调隔离合格（alert/mark 异常仅日志，:243-244,250-251）；样本不足不判定不告警（:295-305）——两问已防；未知信号 evaluate 抛类型化异常 fail-closed | signal_degradation_monitor.py:243-251,288-292 | —（已防） | — |
| A(亮点) | 参数校验完备（窗长/min_samples/floor/decay 序/degraded_weight 域全查）；frozen dataclass 输出；__init__ 全 DI（clock/router/sink）纯内存可单测——header INVARIANTS 全部兑现 | signal_degradation_monitor.py:149-162,84-120 | — | — |

## 3 SOTA 对照

- 滚动 IC 监控+信号衰减追踪：**对等已有**——IC/rank-IC 多窗口滚动+衰减半衰期是量化信号健康监控标准作业（Alpha Architect《Information Decay: which factors have the longest half-lives?》alphaarchitect.com，2019-2026；QuanterLab IC 诊断 quanterlab.com，2025-2026；Zhang IC 统计性质 arXiv:2010.08601，2020——后者支持"小样本 IC 噪声大"的本报告轴 A 发现）。
- 判准率加权/可靠度递进（等权→性能加权→时变）：**对等已有（声明侧）**—— forecast combination 文献（简单平均稳健性）与 TDM 已引 Fed 实证同向；实现缺位同红节点声明。
- 衰减衰减率（decay）前后半窗对比法：**立卡候选**——业界更常用 IC 序列自相关拟合半衰期（hyperbolic/exponential），前后半均值差是粗近似；作为 MILD 早期预警可用，作量化依据偏弱（对齐轴 A 小样本发现）。

## 4 缺陷清单

1. **[P2] 孤儿+节点能力缺口量化存档**（红节点自认，本条主要为收口提供打勾表）。建议修法：装配批次接线（alert_router 接 alert 路由、mark_sink 接 L1-AGG 降权真源）；接线前 MATURITY 降 draft。验证法：grep。
2. **[P3] 告警无去重（降级期每次 evaluate 重发）**。建议修法：alert 同样加 `prev is not report.level` 守卫或周期性心跳节流。验证法：三连 evaluate 计数探针。
3. **[P3] 降权二值无梯度（MILD=SEVERE 砍半）**。建议修法：weight_hint 按 level 映射（MILD 0.8/MODERATE 0.5/SEVERE 0.2 之类）或文档声明有意保守。验证法：两级对比探针。
4. **[P3] 小样本 decay 噪声+乱序无守卫**。建议修法：min_samples 提示置信度（report 附 sample_size 已有，判定阈值随样本量收缩）；observe 加时间戳单调断言或排序。验证法：蒙特卡洛/倒序探针。

## 5 挂起疑问

- weight_hint 的真消费语义（乘到信号权重还是替换置信度）未定——装配批次设计时与 L1-AGG 对齐。
- 与 degradation_detector（MOD-SIGQC-001）的双件分工在蓝图声明但两件都未接线——接线时是否合并为一件（规范预算净零机会）请裁定。

## 6 完备性自评

六轴全查（A 数学四问：hit/IC/decay 三指标公式+除零边界+小样本假设逐个过；B 上游=QualityObservation 输入校验逐字段查；C 下游=零调用方判孤儿；D=与 TDM 声明打勾+与 MOD-SIGQC-001 分工声明核读；E 五问：静默失败=回调隔离（已防）、假阳性=小样本 decay、断供=样本不足不判定（已防）、重复触发=告警重发（已立）、时序=时间戳乱序）。长尾：①degradation_detector/quality_benchmark 两兄弟件未审；②92 测试逐断言抽查级；③真实信号观测流数据画像无生产数据。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
