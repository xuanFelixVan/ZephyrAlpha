---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-03
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-15-创建前搜索仅新建模块触发 + 附录 D 锚块
---

# SD14-03 创建前搜索（policy Step 1.5）

## 1. 定义

仅新建模块/蓝图/代码文件/门禁时触发（conditional=true）：三重搜索（SearchCodebase+Grep+注册表精确匹配）+ 复用决策（覆盖率四档：完全覆盖→直接用 / 80%→扩展 / 50%→重构+扩展 / 不覆盖→进 Step 2）。通过判据=[REUSE-DECISION] 标注+覆盖率证据。修改已有文件场景跳过本步（走 RULE-ZERO 锁协议）。宪法对应=RULE-CAPABILITY-LOOKUP（施工前能力反查留审计，逃生=no-lookup 白名单）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 拟新建对象的关键词/能力描述；注册表索引（ROOR→对应 REG-*） | `docs/registry_of_registries.yaml`；`docs/library/FRONT_DOOR.md`→lookup 单口 |
| 输出面 | 复用决策记录（政策口径=对话内）；能力反查审计流水（结构留痕实存） | `.runtime/lookup_audit/<sid>.jsonl`（图 store_refs 在册，簿01 实测 363 件）；`src/zephyr/governance/capability_lookup.py` `write_lookup_audit_log`（L331 实证） |
| SSOT 真源 | 政策 Step 1.5 + 锚块；规则册 `trae_002_anti_orphan_search_first.yaml#search_first`（政策 2026-10-04 已更正原误引 §rule_eight）+ `trae_056_module_creation_workflow.yaml#phase_1_search`；配套 trae_083 设计意图三分法/trae_060 向内收三原则 | 政策 L195-212；`docs/01_policies_and_standards/rules/trae_002_anti_orphan_search_first.yaml`；`trae_056`/`trae_083`/`trae_060` 同目录 |
| 代码模块 | `src/zephyr/governance/capability_lookup.py`（module_id=MOD-INF-037；find() L944 + 审计写入 L331 本批 grep 实证） | 同左 |
| 门禁约束 | `CAPABILITY-LOOKUP-REQUIRED`（双册在册：in_process=1 条 + gate_registry=3 处，本批 grep 实证）；逃生=no-lookup 白名单理由 | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`；`.../gate_registry.yaml`；`AGENTS.md` §1 规则 9 |
| 自动化触发 | 提交期 gate 强制（无反查审计则拦）+ 审计流水自动落 jsonl | 图 exec_source=gate:CAPABILITY-LOOKUP-REQUIRED |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | ROOR/FRONT_DOOR/lookup 查询入口链全在册 |
| 输出面 | warn | 审计流水半结构留痕实存；但"复用决策标注"政策只说对话内，无结构落点 |
| SSOT 真源 | warn | 政策正文已更正锚引（R-09 闭合中），但图仍挂 D14-G11 且其 invalidation 条款已满足（政策锚已补齐）——gap 未按条款作废，账实漂移 |
| 代码模块 | pass | capability_lookup.py 双函数实证在位 |
| 门禁约束 | pass | CAPABILITY-LOOKUP-REQUIRED 双册在册实证 |
| 自动化触发 | pass | 提交期 gate 强制+审计自动落盘 |

## 4. 缺口与建议

- 缺口1（新发现，账实漂移）：D14-G11（trae_002#rule_eight 断链）的政策侧修复已于 2026-10-04 落地（政策 L200 更正注记），按 G11 自身 invalidation 条款"对应政策锚被补齐 ⇒ gap 节点作废，须回写骨架后重生成"应已作废，但 2026-10-15 重生成的图仍带 G11——锚块维护链路未跟上政策改版。建议：锚块同批维护纪律入生成器校验（gap invalidation 条款满足时生成器告警）。
- 缺口2：复用决策无结构落点。建议：随 D14-02 留痕面裁定一并解决（同一会话 staging 留痕机制可复用）。
