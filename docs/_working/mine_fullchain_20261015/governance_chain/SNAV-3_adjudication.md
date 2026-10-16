---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-3
excavated: 2026-10-15
ttl: task_bound
---

# NAV-3 审计裁定（nav 七段导航之三：多模型→Final Judge）

## 1. 定义

多模型审计（GLM→Kimi→Qwen→Claude，按 GOV-AI-002 路由）→ Final Judge 仲裁争议 → Owner 裁定结论固化。
SSOT：`config/nav_table_mapping.yaml#seven_stages③`。

## 2. 六向台账

### 2.1 输入面
- NAV-2 结构化草稿。
- check_items 五问：升级版指令集-v4 四步串行流水线？Step 0 动态项目扫描？裁定结论✅/❌/⚠️ 落档？⏳ 待裁定清零？PS-STD-004 五维分类推导链裁决（stability→layer→scope→Owner）？

### 2.2 输出面
- 裁定结论固化文档 → NAV-4 蓝图。
- 深裁呈报侧衔接：`docs/01_policies_and_standards/sop/governance_sop/deep_adjudication_method_policy.md`（实存，图16 boundary 指针同源）。
- 裁定路由全半程：`docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md`（实存；八类路由+生死两轨未成图——骨架缺口批第 12 条）。

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[2]。
- PS-STD-004→`docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml`（实存）。
- GOV-AI-002→`docs/01_policies_and_standards/rules/trae_040_ai_model_routing.yaml`（实存；注：nav 表内 GOV-AI-002 描述写"DeepSeek主力+GLM审查+Claude救援"，与 stage③ 行动列"GLM→Kimi→Qwen→Claude"路由序列不一致——同册内部口径差，登记为注记）。

### 2.4 代码模块
- `scripts/governance/d12_ai_hallucination/validate_session_gate_check.py`（实存核验）。
- 骨架代码指针"d12_ai_hallucination 校验器"成立。
- 人工引用件"升级版指令集-v4.md"：docs/scripts 全仓 find 零命中——会话外挂指令集，仓内不可达。

### 2.5 门禁约束
- 本段产出（裁定结论）落档后受 REFERENCE-INTEGRITY（原 RULING-REFERENCE gate74）约束：文中 裁定#NNN 引用必须在册且同 commit。
- LLM 调用红线：多模型审计的实际 API 调用必经 LSGSecurityGateway（宪法 §9.2；`src/zephyr/security/llm_defense/llm_security/` 实存）。

### 2.6 自动化触发
- validate_session_gate_check.py 为人工/CI 触发校验器；无本段专属定时器。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | NAV-2 交接清晰 |
| 输出面 | pass | 裁定固化→NAV-4+路由政策/深裁政策双实存 |
| SSOT 真源 | warn | 册内 GOV-AI-002 描述与 stage③ 路由序列两口径并存（DeepSeek/GLM/Claude vs GLM/Kimi/Qwen/Claude） |
| 代码模块 | warn | 校验器实存；但 check_items 核心引用"升级版指令集-v4.md"仓内零命中（人工件不可达） |
| 门禁约束 | pass | REFERENCE-INTEGRITY+LSG 双红线覆盖 |
| 自动化触发 | pass | 校验器人工/CI 触发，语义合规 |

## 4. 缺口与建议

- "升级版指令集-v4.md"建议入仓（templates 区）或从 check_items 改为指针化描述，消除不可达引用。
- GOV-AI-002 双口径建议按 ROOR/真源纪律收敛：以 trae_040 YAML 为准回写 nav 行动列描述。
- 裁定路由全半程成图诉求归骨架缺口批第 12 条，不在本段发明环节。
