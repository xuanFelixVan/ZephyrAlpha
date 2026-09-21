---
oid: V05
对象: 决策闸（DecisionGate，IS→WFA→OOS 三段+DSR 三线裁决+Phase5 双闸）
入口: src/zephyr/backtest/core/decision_gate.py:539（DecisionGate）
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 本对象零漂移）
材料包: 源码+两测试文件全读；churn；消费方 grep（fw_backtest/两 engine wrapper）；运行时证据=logs 抽查
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V05 决策闸（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：evaluate_dsr/evaluate_strategy_risk_admission 单一判定源（L98-222）、Phase5 双闸（regime 适配+参数收缩，L225-370）、DecisionGate 三段（check_is/check_wfa/check_oos L558-813）、evaluate 编排 L815-943、plateau/cliff 判定 L1013-1172、偏差监控 L1174-1213。
- 排除项：fw_backtest 编排层本体（只审接缝）；alert_threshold_registry 内容正确性（只验加载机制）。
- 测试：tests/backtest/test_decision_gate.py（约 40 用例）+ test_decision_gate_regime.py（17 用例），实测全绿。
- 变更热力：15 commits（活跃热区）：0cbf503a8f 口径 A4/A5→bc2e79866f 车道 L 默认 fail-closed→8b43e762b8 撤假声称（诚实纠错）→c8db841e2e H5-B 真接线。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | 三线 DSR 裁决语义完备（significant/overfitting/review/unavailable，None 与中间带全 fail-closed）；两轨一致性由测试钉死 | decision_gate.py:98-148 + tests:470-476 | 已查无 | 读 evaluate_dsr + 对拍测试 |
| A | **WFA 灾难否决对缺 max_drawdown 字段静默失效（fail-open）**：`window.get("max_drawdown", 0.0)`——窗口字典漏带回撤时按 0 处理=永远不触发灾难否决；契约注释说字段"可包含"，即灾难否决是数据完备性 opt-in。触发剧本：上游 WFA 汇总器重构后漏传 max_drawdown → 全部窗口"无灾难"→WFA 通过 | decision_gate.py:694-699 | **P2** | `gate.check_wfa_stage([{"sharpe":0.8}]*4)` 现 passed=True（无 dd 字段）——一行复现；建议=缺字段记 reason 并降权/显式告警 |
| A | 边界语义一致偏严：IS>0.5 严格、WFA>50% 严格（2/4 不过，测试钉）、OOS 比率≥0.7（含等号）、IS≤0 比率判 0 不过、灾难取 abs 兼容正负 | :595,699,703-704,768-774 | 已查无 | tests:65-68,173-179,231-234 |
| A | plateau 窗口负 center（lo>hi）回退相邻点、sharpe 全负判非高原（保守）、cliff 对 center≤0 不判——边界都有出路且方向保守 | :1124-1172 | 已查无 | 构造负值扫描推演 |
| A | 偏差监控 bt=0 显式抛错（不除零）✓ | :1202-1203 | 已查无 | tests:410-413 |
| A.3 | TestStrategyRiskAdmission 里 test_non_numeric_raises/test_registry_defaults 是 TestDeviationMonitor 同名用例的复制粘贴（死重，不假阳但暗示复制时未审题） | tests:478-486 vs 415-423 | P3 | diff 两段 |
| B | 阈值 SSOT：偏离阈值 import 期 fail-closed 直读 alert_threshold_registry（THD-DEVIATION-001/002），注册表缺失=import 即炸（设计声明"禁码内第二真源"）；DSR 常量唯一真源 MOD-SIM-024；OOS 比率 0.70 复用 overfitting_detector（实测常量存在=0.70） | :388-401,438,445 + overfitting_detector.py:62 | 已查无 | grep 常量定义 |
| C | 消费方：strategy_pipeline/fw_backtest 真接线（evaluate_strategy_risk_admission L357 + DecisionGate().evaluate L470，S11 验收判定源）；两 engine wrapper evaluate_decision_gate **全仓零调用**（grep `.evaluate_decision_gate(` 零命中）——与文件头"实测全仓零调用"声明一致，属已登记孤儿（checklist#8 已知项） | fw_backtest.py:357,470 | P3（孤儿已登记） | grep 复现 |
| C | 爆炸半径：错放行→伪策略进 acceptance.ok→上线候选（钱路径直达）；错拒绝→策略饿死。can_deploy 后仍需人工审批（双层）✓ | :912-918 | 已核 | 读码 |
| D | 单一判定源纪律：evaluate_dsr 被三段闸与准入谓词共用（禁两算两判，INVARIANTS 明写）；第三轨（实盘准入端口）诚实登记为"缺件非漏传"（8b43e762b8 撤回假声称） | :68-76,180-188 | 已查无 | 读 ruling 链接文档 |
| E | 五问：静默失败=P2 一条（WFA 缺 dd）；假阳性过关=同一处；断了没人知道=import 期炸够响 ✓；重复触发=evaluate 纯函数幂等 ✓；时序=无内部状态 ✓；Phase5 checker 启用但缺上下文=raise fail-closed ✓ | :969-1011 | 见 A 行 | 读码 |
| E | 文档漂移：check_oos_stage 两处 docstring 仍写"DSR 可选判定器(默认关闭)"（:738,782-784），而 dsr_threshold 默认已翻转为 0.95 开启（:445）——维护者读旧注释可能误信"默认不拦"而省略 dsr 注入（行为上 fail-closed 兜底仍在，但语义误导） | :738,782 vs 445 | P3 | 读三行对照 |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| 三段 IS→WFA→OOS + OOS/IS 衰减比 | 对等已有（walk-forward 分析业界标准编排；0.70 衰减线为保守实践值，非文献普适常数——预注册即可） | 检索限流，walk-forward 通说记"受阻"；框架本体属业界通行 |
| WFA 多数通过+灾难否决 | 对等已有（单折最差否决=本件实现比"多数通过"更严的 fail-closed 变体） | 同上受阻注记 |
| 过拟合判定补强方向 | 立卡候选：CSCV/PBO（Bailey, Borwein, López de Prado, Zhu 2015）比"fold 衰减比"更系统——建议作为 WFA 段补充证据（与 V06/V08 立卡同源） | Bailey et al., "The Probability of Backtest Overfitting" (2015)：https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf ；SSRN 2326253 |

## 4 缺陷清单（按严重级）

1. **P2｜WFA 灾难否决可因缺字段静默旁路**：现状=max_drawdown 缺省 0.0；证据=decision_gate.py:694-699；爆炸半径=三段闸第二段（伪策略 WFA 全绿→进 OOS）；建议=缺字段时 append reason"回撤证据缺失"且该窗按 passed=False 计（或至少 has_disaster 判定独立于窗口通过计数告警）；验证法=`DecisionGate().check_wfa_stage([{"sharpe":0.8}]*4).passed==True` 现状复现。
2. **P3｜docstring "默认关闭" 漂移**：:738,782 vs 445；建议=同步注释；验证法=三行对照。
3. **P3｜复制粘贴测试死重**：tests:478-486；建议=删除或改写。
4. **P3｜两 engine wrapper 孤儿（已登记）**：grep 零调用；建议=随下次重构摘除或标 experimental。

## 5 挂起疑问

- fw_backtest 传入的 walk_forward_results 是否保证含 max_drawdown（若上游有 schema 校验则 P2 触发面收窄）——待主力会话核 fw_backtest 窗口构造处（_evaluate_staged_gate 链）。
- Phase5 双闸默认 None=跳过不阻断（向后兼容）与"闸默认开"哲学相反——已有意设计（11号文⑨），不立缺陷，仅提示 wiring 完整性靠装配批纪律。

## 6 完备性自评

六轴全查。长尾：①fw_backtest 上游窗口 schema 未逐行核（P2 触发前提）；②test_decision_gate_regime.py 只计了用例数未逐条审（17 条，覆盖 regime 矩阵）。运行时证据：近 3 日 logs 无本对象 error。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 WFA 缺 dd fail-open: 确认→治本(缺字段窗口强制未通过+留痕)。既有 3 测试契约同步收紧+新回归。复检 99/99。生产两引擎桥接恒带 dd,生产行为不变。
- 修复提交: 队列 q-20260918-st-deeprev-20260918-0007。
