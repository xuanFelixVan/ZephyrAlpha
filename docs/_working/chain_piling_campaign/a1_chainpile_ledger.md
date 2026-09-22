---
ttl: task_bound
completes_when: 与 00_piling_minutes.md 同归档
title: 定桩战役台账 a1——波次进度/提交/自裁/上报/门禁学费 总账
owner: ZephyrAlpha-Owner
session: st-chainpile-20260922
date: 2026-09-22
---

# 定桩战役台账 a1

> 本文件是 st-chainpile-20260922 的过程总账：波次状态、commit 留痕、自裁清单、上报清单、门禁学费。
> 纪律：凡机械可证自裁必须在此留痕；凡上报待批必须在此挂号。

## §1 波次进度板

| 波 | 内容 | 状态 | 产出/commit |
|----|------|------|------------|
| 冷启动 | 七步宪法序列 | ✅ 完成 | ENV 3.12.8/reaper alive/worktree `D:\ZephyrAlpha\.worktrees\st-chainpile-20260922` 分支 `ai/st-chainpile-20260922/chain-piling`/heartbeat PID 25396/lookup 审计（construction_workflow_sop+mining_sop 命中，question registry 零命中=无重复资产）/ROOR 已读/裁定号实测 max=#399 |
| W0 | 纪要落盘+目录+台账 | ✅ 静窗收口B3v2 批 | 00_piling_minutes.md+a1_chainpile_ledger.md+01_campaign_directive.md |
| W1 | 基建自身挖矿 | ✅ 设计+红蓝完成 | infra_mining/ 五份+红蓝 2 份（43 发现全处置） |
| W2 | 基建四件套施工 | ✅ 代码+测试+登记面 | src/zephyr/governance/meta_question（38 测全绿）+apply_meta_question_ddl.py+blueprint+trae_087+能力卡+ROOR REG-METAQ-001+裁定#400-402（0c3792ec09 已落） |
| W3 | 七层定稿 | ✅ | 01_layer_charter.md（B6 批 d16062c965 已落） |
| W4 | 源线谱 | ✅ | 02_source_line_registry.md（29 条三档，B6 已落） |
| W5 | 图谱谱系 | ✅ | 03_graph_registry.md（5 张，B6 已落） |
| W6 | 原问题挖干入表 | ✅ 批次 283 条暂存落账；PG 实插待重建广播 | question_batch_w6.yaml（B7v2 批）+check_meta_question_batch.py 违规=0 |
| W7 | 施工映射总账 | ✅ | 04_construction_map.md（283 行机生映射，B7v2 批） |
| W8 | 红蓝+循环+终局 | 🔄 待注册表重建广播后收口 | 终局报告 99_final_report.md 待建（token 待广播后登记） |

## §2 提交留痕

| # | commit | 内容 | 队列回执 |
|---|--------|------|---------|
| - | - | - | - |

## §3 自裁清单（机械可证级，留痕即生效）

| # | 自裁事项 | 机械证据 | 影响 |
|---|---------|---------|------|
| S-1 | 纪要§7"16 字段"机械计数=18 项；判读以字段清单原文为准建表 | 逐项点数 18 | 已入裁定#400 呈追认 |
| S-2 | W6 扩展口径：U1-U6 从 10 勾选线扩至 26 在产线（C 档 3 线排除） | W4§5 落选说明真源原文"未入选线仍入通用展开" | 283 条分组合规，已随 B7v2 留痕 |
| S-3 | depgraph blueprint_id 由 CHAINPILE-METAQ 改 MOD-CHAINPILE-METAQ | 裁定#208 三轨制 PG 侧 RAISE 硬拦（blueprint_id format violation） | 六节点重注册成功（14935631-36） |
| S-4 | 裁定号一度误判撞号改 #403-405，后实证 #400-402 为本班 0009 批自己落地，撤回改号 | git show 0c3792ec09 内容比对=本班文本；dev 无重复 | #400-402 有效，无 #403-405 |

## §4 上报清单（待 Owner/Max 批）

| # | 事项 | 状态 |
|---|------|------|
| R-1 | 裁定#400-402（存真判读/schema 收口/参数批）呈 Owner 追认 | 已落 dev（0c3792ec09），待追认 |
| R-2 | W3 遗留：L2 暂无专属问源组，是否增设图谱质量自有问源 | 待 Owner（01_layer_charter §1-L2/§3） |
| R-3 | B/C 档源线渠道复验（X/Reddit/海关总署境外网受限未核实）+外采资金门位 | 待 Owner 侧网络复验+逐线批 |
| R-4 | W6 PG 实插+DDL apply+快照重生成 | 待 Owner"注册表重建完成"广播后执行 |
| R-5 | W8 终局报告 99_final_report.md+handoff | 待重建广播后登记 token 并落地 |
| R-6 | 棚本地队列呆袋 2 件（q-...-0001/0002 旧快照）+旧名 a1_ledger token 条目 | 移交维护班/重建清收 |

## §5 门禁学费（gate 拦截与修正配方）

| # | gate | 病根 | 修正 |
|---|------|------|------|
| G1 | REGISTRY-MASS-DELETION ×4 | 共享册并发战+**棚内 HEAD≠dev**（git show HEAD 在 worktree=旧分支基） | 基底一律换 `git show dev:`；清队窗紧贴重放 |
| G2 | CREATE-GUARD ×5 | token 未先行落地（gate 读 HEAD） | token 最小批严格先行，落地后再发内容批 |
| G3 | N-16 基名重名 | a1_ledger.md 撞 disk_reorg 班同名 | 改名 a1_chainpile_ledger（lane 前缀家法） |
| G4 | MANUAL-ONLY-PERMANENT | DDL 部署器/快照 CLI=manual+permanent | `# noqa: m11-perm-manual-legitimate` 豁免标记（照 commit_queue.py 先例） |
| G5 | PROTECTED-PATHS | rules/*.yaml 须 Owner 审批 | 战役令 W2 明文授权+消息加 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] |
| G6 | DIRECTORY-CONTRACT ×5 | docs/_working 禁 .json/.py | 批次 json→yaml；checker 迁 scripts/governance |
| G7 | NEW-FILE-DEPGRAPH ×2 | module 粒度节点不算文件节点；blueprint_id 违三轨制静默失败 | file 粒度逐件注册+MOD- 前缀（S-3） |
| G8 | TTL-METADATA | 能力卡缺 ttl 字段 | 补 ttl: permanent |
| G9 | OPS-GUARD DeleteBlockedError | 棚内队列簿记 rename 命中 .worktrees 保护区 | 队列根指主区（ZEPHYR_COMMIT_QUEUE_DIR），棚内呆袋留呈维护班 |
| G10 | q-0006/q-0015 蒸发 | 死信/完成态漂移观测窗口竞态 | requeue 前先 find 全态再行动，勿信单次 ls |

## §6 关键实测备忘

- 裁定号：max=#399（worktree HEAD 实测），本班裁定从 **#400** 起，同 commit 原子。
- PG 通道先例：`scripts/ai_layer/apply_ai_intake_ddl.py`（DDL-as-Code，`get_depgraph_pg_connection`，schema ai_intake 五表）+ 写入 API `src/zephyr/ai_layer/intake/`。meta_question_registry 沿此通道。
- CREATE-GUARD：`scripts/scaffold.py` 自动登记 creation_token；批量 `scripts/governance/d3_metadata/batch_creation_tokens.py`。
- 三问停止判据真源：`skeleton_mining_policy.md` §3。
- depgraph 登记：`apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID [BUILD_STATUS] --granularity`（蓝图文件须先存在）。
