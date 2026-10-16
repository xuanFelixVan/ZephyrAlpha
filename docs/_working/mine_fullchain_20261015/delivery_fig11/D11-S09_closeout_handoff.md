---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S09
name_zh: 收尾注销与 handoff 交接
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S09
---

# D11-S09 收尾注销与 handoff 交接

## 1. 定义
会话车道第九环节（车道终点）：跨会话状态交接。决策问题=「注销前 claim 全放了吗？handoff 包落盘让下一会话可续吗？」路径=SessionHandoff schema（政策 §4 契约）→网关 commit finally 自动写 session shutdown handoff→close-door 序列（merge/abort→release claim→promote 或确认 TTL→写 handoff→archive --execute 就地清）。

## 2. 六向台账

### 2.1 输入面
- commit finally 钩子（成功/失败路径都触发 shutdown handoff）
- 收班序列输入：宪法 §2.9 六步收尾+parallel_session_coordination_policy.md close-door 真源

### 2.2 输出面
- 交接包：`.runtime/handoffs/`（2026-10-15 实查 206 件；图记 09-25 为 242 件——TTL/轮换后仍在产）
- crash recovery 面：session shutdown handoff（P4-T2）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S09`（wired/production，MOD-INF-018）
- 政策真源：`docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md` §4（SessionHandoff 契约文本，图引用不复制）

### 2.4 代码模块
- `src/zephyr/security/access_control/session_concurrency.py:786` `class SessionHandoff`（实存在盘）
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:4499-4513`（图记 :3538-3545，行锚漂移 +961：finally=红蓝触发+session shutdown handoff+pathspec 清理+环境变量复位；handoff 失败 logger.warning 不阻断）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=收班即清铁律（宪法 §2.9：车道/工棚/staging 不清=给下一班留第六态）+handoff 是跨会话状态交接唯一格式真源（图层 handoff_zh）

### 2.6 自动化触发
- commit finally 自动写 handoff（异常吞掉不阻断提交）；archive --execute 含会话壳与影子指令面清理

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | finally 钩子+收班序列输入在案 |
| 输出面 | pass | handoffs 206 件在产 |
| SSOT真源 | pass | 图/政策/骨架齐 |
| 代码模块 | pass | 双锚点实存（行锚漂移 +961，gateway 高频演化） |
| 门禁约束 | pass | 收班即清铁律+格式唯一真源 |
| 自动化触发 | pass | finally 自动写+archive 清理 |

## 4. 缺口与建议
- 【行锚滞后】gateway 行锚漂移已近千行，图内 13 处 gateway 锚点建议一次性重扫批更新。
- 【观测建议】handoffs 206 件无 TTL 注记（retention=留档），建议补 handoff 包消费侧标记（被下一班读过=可归档），区分活交接与死留档。
