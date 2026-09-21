---
status: active
title: "W8 第二圈 working 大清理总台账"
module_id: ""
blueprint_id: ""
version: "1.0.0"
created: "2026-09-21"
updated: "2026-09-21"
ttl: "task_bound"
completes_when: "全部批次落地+循环检查两轮零问题+红蓝对抗零未修复发现；随后本目录随批归档 archive/2026-09/working_cleanup_campaign/"
---

# W8 第二圈 working 大清理总台账（st-workclean-20260921）

> 机制真源=archive/2026-09/final3_campaign/w9_triage_ledger.md（W8-0 四态机+W8-4 归档硬门禁循环）第二圈执行。
> 授权=Owner 2026-09-21 总攻令（自主裁定六条已交付：archive 冻结层续用/断链同晚闭环/fullflow 转裁立案/final3 证据保护/哲学四件晋升/woff2 哈希定生死）。

## §一 批次流水（全部走 GitCommitGateway 队列正门）

| 批 | qid | 内容 | 状态 |
|---|---|---|---|
| 补记批 | q-20260921-st-workclean-20260921-0001 | gate 名册对账治本：LIBRARY-COVERAGE 两段式第二段（st-dloop 死会话遗物，113→114+字段补齐，门文件+冒烟测试同批） | 入队 |
| 单0 | q-20260921-st-workclean-20260921-0002 | final3 18 条终态件证据保护（含 p14 onepager 作废更正） | 入队 |
| 归档批A | q-20260921-st-workclean-20260921-0003 | 11 目录→archive/2026-09/（649 files+11 deletes），终局状态块已随册 | 入队 |
| 归档批B | q-20260921-st-workclean-20260921-0004 | 散件 11 件归档+woff2×3 删除（sha256 与在役版相同，机械可证） | 入队 |
| 内容批C | （本批） | SOP 晋升 4 件+sop/README 指针+creation_token 册同步 | 待入队 |
| 报告批D | （本批） | 结案报告 5 份落盘+本台账 | 待入队 |
| 归档批E | （本批） | collection_intake（含其结案报告）→archive/2026-09/collection_intake/ | 待入队 |
| 立案批F | （本批） | fullflow 22 项+A00 入 architecture_issue_registry+裁定登记 | 待入队 |
| 改链批G | （本批） | 活文档引用改新路径（死亡证明映射执行） | 待入队 |
| 收尾批H | （本批） | index 全量重生成+路径树刷新 | 待入队 |

## §二 死亡证明映射表（旧路径→新路径；tombstone 原则：本表即查证入口）

| 旧路径 | 新路径 | 依据 |
|---|---|---|
| docs/_working/tilib_clearance/ | docs/_working/archive/2026-09/tilib_clearance/ | 3424a718e7 收官 |
| docs/_working/dataqa_audit/ | docs/_working/archive/2026-09/dataqa_audit/ | d2d2e0eb6a |
| docs/_working/tdchain_mine/ | docs/_working/archive/2026-09/tdchain_mine_closeout/ | **改名**：archive/2026-09/tdchain_mine/ 已被 W8 第一圈占用 |
| docs/_working/factory/ | docs/_working/archive/2026-09/factory/ | 09-15 交接包 |
| docs/_working/pattern_line/ | docs/_working/archive/2026-09/pattern_line/ | 两线合并对账收口 |
| docs/_working/pipeline-research/ | docs/_working/archive/2026-09/pipeline-research/ | 09-15 交接包 |
| docs/_working/resource_schedule/ | **撤回归档（勘正）**：初判 A 有误——生产代码（采样器/晨报/config 33 处引用）功能性写入本目录，W8-0 原台账 D 类判定正确；留场 |
| docs/_working/deep_review_full/ | docs/_working/archive/2026-09/deep_review_full/ | 台账自标归档候选+0cc5b32aa5 |
| docs/_working/bizmine_night/ | docs/_working/archive/2026-09/bizmine_night/ | 成果双路归位 |
| docs/_working/kimi_audit/ | docs/_working/archive/2026-09/kimi_audit/ | 裁定全在册（**证据锚引用改链见 §四**） |
| docs/_working/final3_campaign/ | docs/_working/archive/2026-09/final3_campaign/ | p14 终局+onepager 作废 |
| docs/_working/2026-08-30-l3-snapshot-datasource-adjudication.md | docs/_working/archive/2026-09/2026-08-30-l3-snapshot-datasource-adjudication.md | **以本件（09-15 结案版）取代 archive/2026-08/ 同名旧版**（09-14 版作废） |
| docs/_working/reviews/ | docs/_working/archive/2026-08/reviews/ | 单件裁定档案（FLE gates 裁定书），按战役月份归早不归晚（循环检查补登） |
| docs/_working/daily_loop_campaign/ | （留场围栏） | 丁线挖矿死会话遗物，Owner 已派线（循环检查补登） |
| docs/_working/collection_intake/ | docs/_working/archive/2026-09/collection_intake/ | 批E（README 状态块+结案报告随册） |
| docs/_working/archive/2026-09/pipeline-research/ | **撤回归档（勘正二）**：promotion_advisory/intake 运行时写入面（红队 P1-1），比照 resource_schedule 判生产面留场；生产子目录拆分挂账 | |
| 散件 10 件（clearance-review/ai-native×2/gate-perf/xtreme/ch-redblue/ruling234 html/pattern_session/disk_reorg_plan v1/l3 结案版） | archive/2026-09/ 及 c_class_scattered、redblue 子桶 | 批B+批E |
| docs/_working/OKXSans-{Regular,Medium,Bold}.woff2 | （已删除） | sha256 与 src/zephyr/frontend/dashboard/web/assets/ 在役版逐一相同；恢复=git checkout 该三件 |

围栏禁碰（本班零触碰，15；其中 altdata_line/guides 兼入留场清单=围栏即留场口径）：ultimate_library / recovered_task_cards / unified_campaign / disk_reorg_campaign / code_doc_gov_campaign / data_fix_campaign / flash_speedup / 2026-09-18_vocab_consolidation_campaign / automation / rule_audit_campaign / bizmine_chain_mining / altdata_line / guides / full-auto-chain / **daily_loop_campaign（丁线挖矿，st-dloop 死会话遗物回收件，Owner 已派线，循环检查补登）**。
留场（未施工/服役中/生产面）：ai_layer_vision / trading_vision / cold_backup_automation / altdata_line / guides（迁政策区建议挂账）/ fullflow_campaign（待裁载体）/ **resource_schedule（D 在飞生产数据面，撤回归档勘正——改链批G 误扩 1155 处替换中 33 非文档文件已字节级回滚，教训=L2 证据面与生产行为面必须分级处置，改链只限散文锚点）**。
根目录活文档留场 4 件：2026-09-18-gate-identity-root-fix-plan.md、2026-09-18-rule-audit-master-construction-plan.md、2026-09-19-overnight-handover-max-shift.md、2026-09-19-overnight-scope-lock-report.md（rule_audit 收尾班真源链，随其战役归档）。

## §三 方法论晋升记录（净零：收编原册，零新增平行册）

| 正典 | 来源 | 落点 |
|---|---|---|
| construction_sop/lane_construction_discipline_policy.md | fullflow CONSTRUCTION_DISCIPLINE.md（原册随 fullflow 留场冻结） | +sop/README 指针 |
| governance_sop/construction_ledger_method_policy.md | rule_audit CONSTRUCTION_LEDGER.md（原册服役至收尾班完成） | +sop/README 指针 |
| governance_sop/deep_adjudication_method_policy.md | kimi_deep_adjudication.md + s3_pending_rulings_inventory.md（随 kimi_audit 归档） | +sop/README 指针 |
| mining_sop/indicator_mining_sop_policy.md | tilib_clear_a3_mining_report.md（随档）+与 factor_mining_sop 分工声明 | +sop/README 指针 |

方法论范本随档标注：w9_triage_ledger（四态机）/bizmine_night owner_package §5/collection_intake README（A-E 判定口径）/tilib a5 数值证据链。

## §四 已知引用断链与改链清单（批G 执行；冻结层内引用不改写历史）

1. rule_audit_campaign/2026-09-21-tails-handover-prompt.md 必看#15 指向 2026-09-13-xtreme-redblue-v3-plan.md → 实际在 archive/2026-09/c_class_scattered/（**该件在围栏目录，本班不改，留收尾班自愈**；此条仅登记）。
2. ARCH 注册表/backtest_backlog/ruling_registry 等对 kimi_audit、deep_review_full、bizmine_night 旧路径的锚点 → 批G 机械改新路径。
3. unified_campaign p2_workorders/p2_backlog 对 collection_intake 真源指针 → 批G 改 archive 新路径（围栏文件**不改**，登记由其战役自愈；此处仅入映射）。
4. trading_vision 留场，tdchain 归档件回指本目录路径不变，无改链。

## §五 挂账（非待裁定，均已入册或有明确承接）

- C-3 阴性审查 5 份保留至 2026-09-30 到期复核（承接：本台账到期行+issue registry 挂账批F）。
- woff2 替代字体残留索引（_working/index.md 旧条目）→ 批H index 重生成消除。
- altdata_line 结案报告因 scaffold SSoT 别名闸禁 "data" 词根路径，寄存本目录 w8r2_line_closeout.md（内容完整，指针即此）。
- altdata_line 00_index L23 状态口径滞后（07 实态=执行中待收尾）→ 其文件夹留场自愈，本班不改围栏件。

## §六 端态验收（S7 硬门禁：working 任务书清零归档循环）

_working 根最终形态 = 15 围栏 + 5 留场蓝图/方案 + archive/（冻结层）+ index.md（重生成）+ 4 件 rule_audit 活文档 + 本目录。归档 12 目录 + 11 散件 + 3 字体删除，全部有死亡证明行。
