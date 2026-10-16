---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-13
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-8-全景图状态流转designproduction + 附录 D 锚块
---

# SD14-13 全景图状态流转 design→production（policy Step 8）

## 1. 定义

Step 7 文档更新完成后触发，含场景分流（2026-08-14 裁定）：worktree 隔离施工（默认）=会话内只登记不流转（design 态+设计态边，merge 回 dev 后无需手工动作——#ARCH-70 同身份 UPDATE 通道在第一次重建时自动转 production）；主工作区直接施工=手工流转（`--transition-design-maturity <NODE_ID> production`）+build_status 六态单调推进链（planned/generated/testing/stable/deprecated/production，`--transition-build-status` 仅 stable 可转 production，禁跳态）+sync 派生+battle_map/path_tree 重生成+三方对齐+diagnose。架构升级期禁 `generate_project_depgraph.py --force`。verified_scope=production（骨架 ✅）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 文档已对齐（D14-12）；NODE_ID 与目标态；场景分流判定（worktree vs 主区） | 政策 L513-566；图 rollback_to=D14-12（对齐失败回文档，回边 B12） |
| 输出面 | depgraph 双态字段更新（PG depgraph.nodes 两列：design_maturity+build_status）+对齐通过报告+diagnose exit 0 | 图 store_refs（图 YAML #D14-13）；`scripts/governance/apply_depgraph.py#--transition-design-maturity/--transition-build-status`（本批选项集实证命中） |
| SSOT 真源 | `trae_080#panorama_alignment`（转正流程）+`trae_054#planned`（六态词表）+`trae_056#phase_9`+`trae_035#task_003_panorama_alignment`；build_status 六态由 DB CHECK 强制 | rules 四件；图 evidence（DB CHECK 六态） |
| 代码模块 | `scripts/governance/apply_depgraph.py`（两 transition 选项实证）+`scripts/governance/d5_architecture/diagnose_depgraph.py`（真身，module_ref；政策所指 `scripts/governance/diagnose_depgraph.py` 旧路径不存在=D14-G04，本批 ls 复证）+`scripts/governance/generate_project_path_tree.py` | 三件在盘 |
| 门禁约束 | `DEPGRAPH-FRESHNESS`（in_process+gate_registry 在册，本批实证）；HIGH drift pre-merge 阻断（宪法 RULE-DEPGRAPH） | 两册；`AGENTS.md` §1 规则 4 |
| 自动化触发 | worktree merge 后同身份 UPDATE 通道自动转 production（node_id 不变/edges 不断链/build_status 按 production+test→stable 推导）——生成器通道 `scripts/governance/generate_project_depgraph.py` §restore_design_data :396-428（图 evidence）；boot 钩子 triple_alignment_on_verified | 图 YAML #D14-13 note |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 双场景分流条款完整（policy L520-539） |
| 输出面 | pass | 双态字段 PG 两列+报告+诊断 exit 码 |
| SSOT 真源 | pass | 四册+DB CHECK 词表 |
| 代码模块 | pass | transition 选项+诊断件真身实证（政策旧路径失效已在缺口节收口） |
| 门禁约束 | pass | DEPGRAPH-FRESHNESS 双册在册 |
| 自动化触发 | pass | merge 后自动转 production 通道实证（2026-08-14 SELL 4 节点+POS-020/021 实证在案） |

## 4. 缺口与建议

- 缺口1（D14-G04）：政策两处+frontmatter 一处指诊断件旧路径 `scripts/governance/diagnose_depgraph.py`（不存在，本批复证）；真身=d5_architecture 子目录。建议：政策路径纠偏（总包落），图已按真身锚（fallback 条款正常工作）。
- 缺口2：worktree 分流下"merge 执行人实证核验节点双态"零留痕面（图 note：人工核验零留痕）——建议核验结论进 handoff 包或 commit message 尾注（现有面零新建）。
- 缺口3：production 词表跨 design_maturity/build_status 两字段正交，`--transition-build-status <ID> production` 与 `--transition-design-maturity <ID> production` 同值不同义——易混。建议：capability_cards 出一张双态字段对照卡。
