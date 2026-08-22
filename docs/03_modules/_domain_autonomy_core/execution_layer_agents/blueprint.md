---
blueprint_id: MOD-EXE-AGENTS
module_name: execution_layer_agents
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-EXE-AGENTS execution_layer_agents 蓝图

> 紧凑版（SOP Step 4 补建，四入口合一份）。设计真源：14号文 §3.1~§3.4 / §4 Phase 0 S0.2~S0.5 + 18号清单 §6 波4-14 + #ARCH-168。
> 代码：`src/zephyr/autonomy_core/agents/`（governance_agent_entry.py / business_agent_entry.py / algorithm_agent_entry.py / self_iteration_agent_entry.py + 共享件 _run_store.py）

## 0. 定位

执行层四类 Agent 薄入口（Phase 0 手动形态地基）：每张 <200 行纯组装入口，零新业务逻辑，复用既有判定/注册表/实验跟踪件；人手动 CLI 触发（`python -m zephyr.autonomy_core.agents.<role>_agent_entry --ticket <path>`），产出 100% 落盘 `.runtime/agent_runs/<role>/<run_id>/`。SAFETY：governance=H，business/algorithm/self_iteration=M；全部 human_gated、L0_manual。

## 1. 四入口职责与接口

| 入口 | 子 ID | 输入工单 | 处理（纯组装） | 产出件 |
|---|---|---|---|---|
| governance | MOD-EXE-GOV-001 | ticket_id + targets 路径列表 | 逐 target 调 AutonomyBoundaryGate（MOD-AU-001）三分类判定，聚合 verdict | gate_verdicts.json（overall=passed/escalated/blocked） |
| business | MOD-EXE-BIZ-001 | kind=registration_status / factor_candidate_eval | 只读 factor/strategy 注册表（REG-FCT-001/REG-STR-001）出状态汇总/候选评估建议 | registration_status.json / factor_candidate_eval.json（advice_only=true + 免责声明） |
| algorithm | MOD-EXE-ALGO-001 | ticket_id/experiment_type/target_id/run_id | ①登记先于执行（落 experiment_registration.pending.json，注册表本体交统筹）→ ②显存守卫（≥90% 拒启动）→ ③只读既有实验记录出评估 | experiment_registration.pending.json / vram_guard.json / evaluation_report.json |
| self_iteration | MOD-EXE-ITER-001 | ticket_id + evidence_paths | 只读解析落盘证据（白名单 .runtime/logs/docs），汇总 gate 分布与实验通过情况，模板化出建议 | iteration_suggestion.json（逐条 human_gated/advice_only） |

共享件 `_run_store.AgentRunStore`：统一落盘 schema——ticket.json（输入快照）+ 角色产出件 + run.json + audit.jsonl 追加；信封强制 schema_version/agent_role/run_id/ticket_id/triggered_by=human_manual/ai_autonomy=human_gated/created_at。

## 2. 输出契约

- 落盘 IO 失败只告警不阻断入口返回（审计缺口如实记 status=audit_failed/degraded）
- 各入口返回运行报告 dict：governance→overall + decision_counts；business→status=completed/evidence_missing；algorithm→status=completed/refused_vram/evidence_missing（steps 顺序留痕）；self_iteration→suggestions + skipped_evidence

## 3. 不变量

- 产出 100% 落盘且带 human_gated 标记；零自治运行时（61号文 §4.1 边界内，人手动触发）
- business：零交易执行路径——不 import 任何下单/执行域包（ex_core/ex_sor/trading），测试 AST 断言此不变量；产出一律"仅建议"
- algorithm：实验登记先于执行（无 pending 登记片段不进执行步）；单卡显存 ≥90% 硬上限拒启动；Phase 0 不新起训练/评估进程
- self_iteration：只读形态，证据路径白名单（.runtime/logs/docs）越界跳过；零代码自改路径（不 import 执行/编辑链模块，测试断言）；不做权重自更新/自进化搜索/自动改架构
- 工单缺必填字段 → ValueError（入口输入校验 fail-closed）

## 4. 降级行为

- governance：单 target 判定异常不中断整单（fail-closed 语义由 MOD-AU-001 保证）
- business：注册表不可读/条目不存在 → 产出如实标 status=evidence_missing，不抛
- algorithm：显存采集不可用 → 守卫降级 not_available 放行并如实留痕；实验记录缺失 → evidence_missing 不抛
- self_iteration：证据越白名单/不可读/解析失败 → 跳过记 skipped_evidence，不抛

## 5. 边界（不做）

- 不修改规则/注册表本体（修订走治理流程；REG-EXP-001 登记交统筹）
- 不做全自动策略搜索（30号文 §5 暂缓）、GPU 多卡/集群抽象（约束二）、STOP 模式与 Meta-Harness（Phase 1+）
- MODIFY-GUARD：Owner approval required；变更须同步 14号文 §4 对应 S0.x 验收口径

## 6. 测试

tests/autonomy/test_execution_layer_agent_entries.py（16 用例，四样例 CLI 端到端跑通留痕 .runtime/agent_runs/）。
