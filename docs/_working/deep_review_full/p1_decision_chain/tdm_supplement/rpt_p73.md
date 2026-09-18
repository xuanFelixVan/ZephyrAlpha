---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——强制清仓绕过通道
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：强制清仓绕过通道（P73）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/strategy_abnormal_exit_orchestrator.py:153`（StrategyAbnormalExitOrchestrator.execute:190）
- TDM 节点: TDM-X-S1-06（stage，config/trading_decision_map.yaml:3402，自注红节点"编排缺口"）
- 生产调用方: **零**（grep `StrategyAbnormalExitOrchestrator(` 零命中；header 自认 design+"运行时装配批接线"；finalizer/stop_gate 消费均为待接线声明）
- 测试文件: tests/trading/test_strategy_abnormal_exit_orchestrator.py（114 passed 同批）

## 1 对象快照

- 范围：StrategyAbnormalExitOrchestrator 全文件（396 行）——策略级异常退出五步编排（冻结新信号→优先级撤单/平仓→仓位核对→置 EXITED→告警审计）：CRASH/TIMEOUT/RISK_TRIGGERED 三触发、Fail-Closed（冻结失败不宣称 EXITED 但清理继续）、幂等重放缓存、纯编排端口注入。
- 排除项：券商网关/信号网关端口实现（生产接线侧）；X-S1-06 四触发的信号产生端（KillSwitch=P69 域/黑天鹅/K≥3=P52 域/主力弃庄）。
- 测试覆盖概况：五步/失败腿/幂等/并发覆盖好；**无 EXIT_FAILED 后重试成功的解除场景**（恰为本报告状态机发现）。
- 材料包缺项声明：运行时证据包未取（design 态）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **module_ref 语义错位：节点要"单仓强清四触发通道"，模块是"策略进程异常退出编排"**（对账主发现）：TDM-X-S1-06 声明「四触发（风控 KillSwitch 组合级/黑天鹅立案暴雷/K≥3 连续破位失败/主力弃庄龙虎榜）任一=**绕过全部评分直接市价清仓**，紧迫度 1.0 直送 S2 执行路由；与 R1 分工=本节点管单仓强清」——本模块的四触发是 **CRASH/TIMEOUT/RISK_TRIGGERED（策略生命周期异常）**，产出是策略级 EXITED 置态，**无市价清仓/紧迫度/单仓强清语义**；四触发信号（黑天鹅/K≥3/主力弃庄）全仓零承载（K≥3 断链已在 P52 实证）。红节点自注在案（"X 流三空白之三：S1-06 绕过通道编排"未建），但 module_ref 把"策略异常退出"错挂到"强制清仓通道"节点上，两件事名字近、职责远 | config/trading_decision_map.yaml:3402-3436 vs strategy_abnormal_exit_orchestrator.py:28-37,80-86；grep 黑天鹅/主力弃庄/紧迫度 于模块零命中 | P1 | 对照四触发逐条 grep；读模块 ExitTrigger 枚举比对 |
| A | **EXIT_FAILED 无解除路径（stop_gate 永久堵塞）**：has_unresolved_exits=任一历史报告 EXIT_FAILED 即 True（:358-361），**无 resolve/retry-success 清除 API**——人工修复后重试成功的新报告不会清除旧失败记录，stop_gate 类消费方将永久读到"存在未决退出"而卡死后续流程；状态机只有累积没有收敛 | strategy_abnormal_exit_orchestrator.py:358-361 | P2 | 构造失败报告→成功重试→has_unresolved_exits 仍 True（探针） |
| A | 五步编排 Fail-Closed 链（已核，质量高）：冻结失败→CRITICAL 告警+清理继续（安全方向，:241-256）；核对异常→__VERIFY_UNAVAILABLE__ 哨兵→不得 EXITED（:278-284）；置态失败也 Fail-Closed（:302-305）；单腿异常隔离继续（:260-275）；幂等键重放返回缓存（:206-214） | strategy_abnormal_exit_orchestrator.py:241-307 | —（已核） | — |
| E | 幂等键跨 trigger 复用风险：缓存仅按 idempotency_key（:207）——同 key 不同 trigger/reason 的第二次请求返回首次报告（可能掩盖二次事故的真实触发原因）；key 生成规约未定义（调用方自由拼） | strategy_abnormal_exit_orchestrator.py:190-214 | P3 | 同 key 不同 trigger 两次 execute 看返回首次报告 |
| A | _cache/_reports 无界内存（进程生命周期累积，:187-188）+__VERIFY_UNAVAILABLE__ 魔法哨兵混入 remaining_positions（消费方须知哨兵约定，:284） | strategy_abnormal_exit_orchestrator.py:187-188,284 | P3 | 长跑压测看内存；读哨兵消费契约 |
| A(亮点) | 端口全注入纯编排可单测；告警/审计端口故障不阻断编排（:384-396）；frozen 报告+锁保护缓存；finalizer 永不抛语义（:368-382） | strategy_abnormal_exit_orchestrator.py:143-149,368-396 | — | — |

## 3 SOTA 对照

- 策略异常退出编排（liquidate on crash/timeout/risk）：**对等已有**——模块 docstring 自引对标（Lean 算法异常 liquidate、vnpy 策略停止回收——quantconnect.com/lean 文档，2026；vnpy.com，2026；本项目 TDM-X-S2-04 已引 vn.py 范式）；五步冻结→撤→平→核→置态与业界策略停止回收流程同构且更严格（Fail-Closed 置态）。
- 强制清仓绕过通道（信号面绕过融合直执行）：**对等已有（声明侧）**——风控指令旁路正常信号仲裁直达执行是风控工程标准（双车道 risk-reduction lane 设计，TDM-F-C2-01 D85 已引同构；ClearEdge hard-stop flatten+block re-entry，clearedge.trading，2026，同 P69 引）——**业界有此通道、本项目无此码**（红节点自认），本报告量化其缺口。
- 幂等重放：**对等已有**——幂等键去重是执行系统标准（本仓 git_commit_async/做T 配对同范式，项目内一致）。

## 4 缺陷清单

1. **[P1] module_ref 语义错位+X-S1-06 四触发强清通道零承载**。建议修法：TDM-X-S1-06 拆注两承载面（本模块=策略进程异常退出编排，属运维面；四触发市价强清=市场面待建件），module_ref 增补或改挂；黑天鹅/K≥3/主力弃庄三信号源列入施工清单（K≥3 联动 P52 修复）。验证法：§2 轴 D 对照。
2. **[P2] EXIT_FAILED 无解除 API（stop_gate 永久堵塞）**。建议修法：增加 resolve(report_id, resolution) 或 has_unresolved_exits 改为"存在 EXIT_FAILED 且无后续同 strategy 成功报告"；补重试成功解除测试。验证法：本报告探针。
3. **[P2] 孤儿（design 诚实）**。建议修法：随运行时装配批接线（finalizer/stop_gate 注册）；接线前维持 design。验证法：grep。
4. **[P3] 幂等键跨 trigger 复用/cache 无界/哨兵字符串**。建议修法：缓存键加入 trigger+reason 摘要或文档约束 key 规约；cache 上限或落盘；哨兵改独立字段 verify_available: bool。验证法：各自探针。

## 5 挂起疑问

- X-S1-06 市场面强清通道与 R1 组合熔断（X-R1-01/P69）的分工声明（R1 组合级/本节点单仓级）在两节点注释一致性已核；真正缺口是市场面编排件立项——建议与 P52 的 K≥3 接线、P71 的风控 provider 同批收口。
- "主力弃庄（龙虎榜机构清仓式卖出）"触发源的数据面（SEAT-INST/YOUZI 座席引用）在 X-S1-04 声明——数据源是否在网未审（data 域对象）。

## 6 完备性自评

六轴全查（A 数学四问：排序键/优先级/缓存语义逐个过（无统计公式）、边界=空腿/全失败/重放已测；B 上游=七端口契约+StrategyLifecycleEvent 已查；C 下游=零调用方判孤儿+finalizer/stop_gate 声明面核读；D=与 X-S1-06 四触发对账（主发现）+与 R1 分工核读；E 五问：静默失败=无（CRITICAL 告警全面）、假阳性=幂等键复用掩盖、断供=无（编排本身即断供处理件）、重复触发=幂等重放（含跨 trigger 缺陷已立）、时序=clock 注入）。长尾：①MOD-INF-035 finalizer/stop_gate 未审；②券商网关端口生产实现不存在故清理语义无从实测；③黑天鹅/主力弃庄数据面归 data/seat 域。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
