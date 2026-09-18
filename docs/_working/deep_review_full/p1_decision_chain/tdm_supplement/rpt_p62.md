---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——组合级持仓体检
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：组合级持仓体检（P62）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/position_drift_monitor.py:159`（PositionDriftMonitor.check）
- TDM 节点: TDM-P-P1-05（stage，config/trading_decision_map.yaml:2717，risk_limit_refs=RLM-CONCENTRATION-001/003/004）
- 生产调用方: **零**——PositionDriftMonitor 全仓无实例化（grep 命中的 check_drift 均为 governance/task_repo 无关函数）；header 声明的 MOD-POS-004 再平衡引擎/D-PF-CORE/D-GOVERNANCE 零实际调用
- 测试文件: tests/position/test_position_drift_monitor.py（14 测试，54 passed 同批）

## 1 对象快照

- 范围：PositionDriftMonitor 全文件（299 行）——两级漂移检测（组合总仓位差 ±2%/单标的 ±3%）+分级标注（WATCH/MONITOR/HOLD）+E-POS-02 事件+监听隔离。
- 排除项：SELL-00 持仓分级（triage 输入方）；P2-04 减仓指令下发（下游边）。
- 测试覆盖概况：两级阈值/输入校验/事件覆盖；**无"actual 有 target 无的持仓"场景、无组合内部换仓（总量不变）场景**（两处为本报告探针点）。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点"三查"仅承载一查的参数口径**（checklist #4 同族）：TDM-P-P1-05 声明「单票>20% 总仓位（超集中）/实际权重偏离目标>25%（漂移越带）/同题材持仓>3 只（扎堆）」——模块实现的是**另一套**：组合总量差 ±2%+单标的绝对差 ±3%（TDM 注释已自认"漂移带阈值由模块自带承载"）；但三查中的 **20% 超集中查、25% 越带查、题材扎堆查全部零代码**，且 25%（相对偏离）与 3%（绝对偏离）是不同数学轴（见轴 F 5/25 法则）——两套口径并存互不覆盖 | config/trading_decision_map.yaml:2717-2760 vs position_drift_monitor.py:8,173-175,224-257；grep 集中/20%/题材 于模块零命中 | P1 | 对照 TDM 三查逐条 grep；核对 25% 相对 vs 3% 绝对口径差 |
| A | **标的级检测遍历 target 集合，actual 独有持仓零告警（实测盲区）**：`for symbol in target_weights`（:242）——已从目标清单移除但仍持有的仓（target 删除、position 仍在）永不触发标的级漂移告警；探针实测 actual={'KEPT':0.10,'AAA':0.05} vs target={'AAA':0.05} → KEPT 无 symbol alert（仅组合总量差间接显影，若总量恰好持平则完全隐身）。此类"清单遗忘仓"恰是漂移监控最该抓的形态 | position_drift_monitor.py:240-257；探针实测 | P2 | 本报告探针复跑（KEPT 场景看 symbol_alerts 为空） |
| A | 组合级漂移=总量差而非结构差（设计自洽）：实测内部换仓 X:15→30/Y:45→30（总量 0.60 不变）→ 无组合级告警——与 docstring"组合总仓位漂移"一致，**但组合内结构漂移全靠单标的 3% 兜底**（配合上一条 KEPT 盲区=结构漂移存在漏检面） | position_drift_monitor.py:224-238；探针实测 | P3 | 本报告换仓探针复跑 |
| B | 权重校验 [0,1] 逐标的但无总和校验：actual 总和>1（杠杆/双计）静默通过且组合级漂移必然触发——误报源而非漏报，危害低 | position_drift_monitor.py:283-292 | P3 | 总和 1.2 输入看告警语义失真 |
| E | 事件只在 has_drift 时发（无漂移=无事件）——"监控活着"的心跳不存在：监控断供（check 长期不被调用）与"无漂移"外部不可辨（checklist #6 同族：断了没人知道）；TDM fallback"监控缺→盘前人工核对权重表"是纸面兜底 | position_drift_monitor.py:264-275 | P3 | 停调 check 后查任何心跳输出=无 |
| A(亮点) | 输入校验完备（越界/target⊆actual 全拦）；有符号漂移+超配判定语义清晰；分级标注透传；监听异常隔离；时钟注入可测 | position_drift_monitor.py:283-292,101-121,294-299 | — | — |

## 3 SOTA 对照

- 漂移带再平衡（band/threshold rebalancing）：**对等已有**——业界 5/25 法则=绝对 5pp **或**相对目标 25% 先触先发（Guardfolio 5/25 Rule Guide，guardfolio.ai，2026；Nauma Absolute vs Relative Thresholds，nauma.ai，2026；Raymond James Rebalancing Fundamentals，raymondjames.com，2020-2026）；Resonanz Capital ±5-10% 带内不动手（resonanzcapital.com，2026）；Princeton Asset 回测证据支持阈值法省成本（princetonasset.com，2026-06）。
- 本模块口径定位：单标的 ±3% 绝对带比业界 5pp 更紧（触发频率更高、换手更高）；TDM 的 25% 相对带恰为 5/25 法则的相对腿——**两口径应按 5/25 双腿并存而非互斥**（立卡候选：单标的告警条件改 `abs_drift > 3pp OR abs_drift/target > 25%`）。
- 题材扎堆/单票集中查：**对等已有（声明侧）**——集中度限制是组合风控标准层（CAIS multi-strategy 框架，caisgroup.com，2025-2026，同 P54 引）；题材扎堆与 P55 相关性聚类同族（实现一并缺位）。

## 4 缺陷清单

1. **[P1] 节点三查（20% 集中/25% 越带/题材扎堆）零承载+模块 ±3% 绝对带与 25% 相对带未按 5/25 双腿整合**。建议修法：施工批次补三查中缺的两查（题材扎堆依赖 industry_map，可与 P55 聚类合并立项）；单标的告警加相对带条件。验证法：§2 轴 D grep+5/25 双腿探针。
2. **[P2] actual 独有持仓无标的级告警（清单遗忘仓盲区）**。建议修法：遍历 `set(target) | set(actual)`，actual-only 视 target=0 判漂移。验证法：本报告 KEPT 探针。
3. **[P2] 孤儿死码**（header production 不实；P1-05 节点体检在图上持续、码上无人跑）。建议修法：接线（P1-06 体检编排或盘前批）或降 draft+节点补红。验证法：grep。
4. **[P3] 无心跳事件+权重和未校验**。建议修法：定期 NONE 级心跳或由装配层监控 check 调用时效；总和>1+ε 显式拒绝。验证法：停调探针/总和探针。

## 5 挂起疑问

- 阈值口径归一：±2%/±3%（模块）与 20%/25%（TDM 三查）四值并存，谁是单标的"越带"真阈值请 Owner 终裁（建议 5/25 双腿+20% 集中独立查）。
- 题材扎堆查（>3 只同题材）与 P55 相关性扎堆（ρ>0.70）是否一查两表（行业映射法 vs 相关矩阵法）——建议合并立项避免双承载。

## 6 完备性自评

六轴全查（A 数学四问：总量差/逐标的差公式+边界=零/越界/缺失已测、隐含假设=总量差≠结构差已审；B 上游=权重字典契约已查；C 下游=零调用方判孤儿；D=与 TDM 三查对账（主发现）+与 SELL-00 分级、P2-04 下游边核读；E 五问：静默失败=KEPT 盲区+无心跳、假阳性=总和失真、断供=无心跳、重复触发=check 幂等、时序=clock 注入）。长尾：①SELL-00 triage 分级产生端未审；②P2-04 减仓指令消费本模块告警的接线面（未接线故无从审）；③14 测试逐断言抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
