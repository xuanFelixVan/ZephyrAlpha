---
ttl: task_bound
volume: pending_rulings
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-m5-pending-rulings-20260926
---

# 补挖波_20260925 · 待裁清单（车道 W4-B 补四案，编号 W4B-1…W4B-4）

> 铁律：**本车道不自赋裁定号、不写"Owner 已裁"**；W4B-n 是本车道内部流水，非 `ruling_registry.yaml` 裁定号。
> 案源=`06_f83_automation_crew.md`（自动化班底格）。门位口径依宪法 §5：production 流转／注册表净删／flag 出厂翻转／资金破坏＝Owner（high）；架构取舍＝治理（medium）；纯口径刷新＝AI 可自修（low）。

| # | 问题 | 已试路径（实测） | 选项 | 建议 | 门位属性 |
|---|---|---|---|---|---|
| W4B-1 | **同一文件被两格认领为真源**：`docs/_working/cmd_ledger/automation_master_plan.md` 同时出现在总册 F83 行（:148）与 F119 行（:204，且 F119 标题自称"调度唯一真源 L0-L6"），而 F83 的制度真源 `automation_crew_policy.md` §1 又自带一张与 master_plan §0 同表的引擎窗口表 → 一桩自动化事实被三处各说一遍 | 两册正文对读（master_plan §0 ↔ crew_policy §1，字段近同、各有独占列）；`grep -rln "automation_campaign\|crew_policy" src/ scripts/ config/` = **0**（无代码消费，双写只在散文面）；ROOR 对该文件**查无**条目 | a＝master_plan 归 F119 独占，F83 真源列删除该文件改"引用 F119"；b＝两格合并为一格（环节集合变更）；c＝维持现状＋在两册互挂"共享真源"声明 | **a**（成本最低、不动环节集合；两表按 w5_1 判据①"同真源可派生→必并"收敛为 plan 表＋policy 指针） | 治理门（medium，总筹落地真源列） |
| W4B-2 | **制度类资产是否入 gate 体系**：crew_policy §3"铁律（违者夜班仲裁回滚）"零机件消费、`rule_catalog_registry.yaml:4798` 对该册记 `module_id: ''` → 按判据口径其门禁面＝装饰。要不要为"排班纪律"造尺？ | 见本册 W4B-1 的零命中实测；`gate_registry.yaml` 内无 automation/crew 相关条目；执行主体经核=①席（AI 对话）而非任何门 | a＝把可机械化的两条（Lane 写域互斥／每岗四件套齐件）做成 pre-commit 尺；b＝显式声明"本环节不设机件门"，在 `risk_tier_registry.yaml` 记 human_gate=Owner 席＋①席仲裁；c＝不裁不登记（继续装饰态） | **b 先行**（c 最差：账面把制度当防线；a 须在四件套目录真存在后才有判据，而该目录双仓均不存在） | 治理门（medium；改 `risk_tier_registry.yaml` 属注册表新增非净删） |
| W4B-3 | **四件套机制建还是退役**：crew_policy §4.1 规定产物落 `docs/_working/automation_campaign/<岗>/`，实测该目录在 worktree 与主仓 `D:/ZephyrAlpha` **两处均不存在** → 制度要求与落地完全脱节，夜班 9 席无可审计留痕 | `ls` 双仓验证（§六 复核命令第 3 条）；主仓 `docs/_working/cmd_ledger/` 仅 3 件（plan/discussion/overnight_decisions）；无任何生成器或脚本引用 `automation_campaign` | a＝补目录＋每岗四件套模板生成器（建）；b＝按 w5_1 判据②"零触发零消费→退役"出退役判据清单；c＝窗口到期（Qoder 09-30／GLM 10-08）后随整制自然作废，现在只登记 | **c→b**：本取证日距窗止 4-12 天，建（a）＝为过期制度投产能，违 §4.1 全资产净零；建议登记为"到期随自动化一并退役"，不现在动册 | 若走退役且牵注册表净删（`rule_catalog_registry` 条目）＝**Owner（high）**；本车道**只出判据不删不改名** |
| W4B-4 | **段归属错**：F83 挂在"I 段调度常驻（F76-F85）"，但该格实测无任何常驻件（无 daemon／无计划任务／reconciler 四要素零达成），本质是横切组织制度册 | `m5_scheduling/01_windows_schedtasks.md` 49 个在册任务内无本班底件；`automation_master_plan.md` §0 明写窗口靠对话起，非任务起 | a＝移 M 段横切（与 F119/F116 同段）；b＝留 I 段但改注"制度册，无常驻件"；c＝不动 | **a**（留 I 段会让后续读者按"调度常驻"去找 daemon，反复空挖） | 治理门（medium，环节集合口径，总筹落地） |

## 复核命令（本案源册配套）

```bash
grep -rln "automation_campaign\|crew_policy" --include=*.py --include=*.ps1 --include=*.yaml src/ scripts/ config/ | wc -l
ls docs/_working/automation_campaign/ 2>&1 ; ls /d/ZephyrAlpha/docs/_working/automation_campaign/ 2>&1
sed -n '4797,4801p' docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml
grep -n "automation_master_plan" docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
```
