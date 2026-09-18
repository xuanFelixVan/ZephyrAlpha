---
ttl: task_bound
completes_when: 总包对本册四项给出 R-0NN 裁定并回写 COORDINATION_LEDGER §6
---

# 裁定申请 · wiresafe 车道（st-ff-wiresafe-20260918）四项

## 项 1 · BRK-021 / BRK-072 的施工标的已由**他道未落地件**占据 —— 请改派落地而非重复造

**背景**：任务书要求 BRK-021"接法：危机确认日触发 → 技能生成腿单 → 虚拟成交 → 虚拟 PnL →
平腿 → 留痕，比例 beta×0.5 进 `config/crisis_gate.yaml`"。

**实测（2026-09-18，本车道）**：该链路**已由 residG 车道整体建出**，但**全部未落地**：

| 件 | 状态 | 证据 |
|---|---|---|
| `src/zephyr/risk/paper_hedge_leg.py` | **untracked（`??`）**，不在 HEAD | `git cat-file -e HEAD:src/zephyr/risk/paper_hedge_leg.py` → `fatal: ... exists on disk, but not in 'HEAD'`；文件头 `[CREATION-TOKEN] auto-scaffold-paper_hedge_leg-20260918`，`[CONSUMERS] zephyr.strategy_pipeline.pipeline_events(maybe_run_paper_hedge 唤醒钩子)` |
| `config/paper_hedge.yaml` | untracked（`??`） | 内含 `index_code: IM`（总包预裁 O2）、`portfolio_beta: "1.0"`、`hedge_ratio_of_beta: "0.5"`、`real_channel_locked: true` |
| `pipeline_events.py` 唤醒钩子 | unstaged（` M`，**residG 独占**，§2 所有权） | — |
| `src/zephyr/pf_alloc/crisis_gate.py` + `scripts/backtest/crisis_drill_monthly.py` | staged（`A`），归 landA/z-land | `git status --short` |

**为何本车道不照任务书写**：两条硬约束撞车——
① `crisis_gate.yaml` 的读取方 `src/zephyr/pf_alloc/crisis_gate.py:155-157` 是
**未知键=CrisisGateError 硬错**（防拼写漂移静默不生效）→ 往里加对冲键会**当场打死危机闸主链路**；
`config/paper_hedge.yaml` 头部注释已独立记载同一判断并登记了待裁。
② 另建一份对冲腿编排=CloneGuard extract 级克隆 + RULE-SSOT 双真源，且需改 residG 独占文件。

**选项**：A=本车道重复实现（否决，理由见上）；B=把这四件转交 landA/residG 作为落地批（建议）；
C=本车道代提这四件（越权，禁）。
**建议 = B**，且 BRK-021 裁定为 **黄（他道在途，本车道判定=已建未落地，零重复造）**。
**影响面**：仅派工归属，无代码改动。

## 项 2 · 熔断族净删候选（禁自删，登记交 Owner）

- `src/zephyr/infrastructure/kill_switch_sim.py`：第 6 套 KillSwitch 语义件，GOMAP "KS×5" 口径未含；
  实测 src 内除自身外零 import。是否退役=注册表/模块**净删**（宪法 §5、LEDGER §7 Owner 门位）。
- `capacity_assurance/kill_switch` 与 capacity 域 fuse 语义重叠面（GOMAP GOM-L3 note 在案）。
- 建议：列入 Owner 净删待办；本车道一律未删。

## 项 3 · 应急保命轨"默认启用+自动拉闸"是否可接受（方向=加严，但需 Owner 知会）

`config/emergency_track.yaml` `enabled: true` → 盘内三腿确认失效即拉**系统级**总闸。
已内建四道防误触发（unknown 不计失效 / 4h 证据视界 / 盘外只判不动作 / 连续 2 次确认），
且有测试钉逐道把守。但"自动停交易"仍是资金影响面动作。
**选项**：A=保持 enabled 默认（建议，与 CC_07 蓝图语义一致）；B=首月 `enabled: false` 只观察留痕，
演练 ≥1 次真判后再翻（需 Owner 记一次 flag 翻转门位）。
**证据位置**：`src/zephyr/governance/resilience_governance/emergency_track_guardian.py`（判定与动作）、
`tests/governance/resilience/test_emergency_track_guardian.py`（13 测）、
施工包 `lanes/wiresafe_BRK-078_construction_pack.md` §4。

## 项 4 · 断点普查 §A/§D/§E 存在**系统性陈旧记载**，建议加"普查复测"步

本车道 7 条断点里 **4 条记载已陈旧**：BRK-004/005（A3/A4 已于 `49dde8fda5` 2026-09-16 接线）、
BRK-021（residG 已建未落地）、BRK-072 的危机演练件（已 staged 待落地）。
根因：GOMAP `pipeline.layers[*].disconnected` 是**人工语义层**（生成器保留，见文件头 `ssot_note_zh`），
接线落地后无自动刷新义务 → 普查读它=读到过期断点。
**建议**：①本车道已按实测改写 GOM-L2/L3 四条 note（已随批落地）；②总包在 `FLOWTHROUGH_ACCEPTANCE_SPEC`
§5 的"封矿"步后加一条**普查复测**：每条断点施工前先跑原始证据命令（本车道即因先跑命令才发现陈旧）；
③可考虑给 GOMAP `disconnected` 加"复核日期"字段并由 `generate_governance_map.py` 校验（属新建类，未做）。
