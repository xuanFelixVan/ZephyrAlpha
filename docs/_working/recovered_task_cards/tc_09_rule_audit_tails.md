---
card_id: TC-09
title: 规则审计战役收尾三件（拆工棚 / index.md 尾巴 / 宪法 A/B 班）
verdict: 部分存活变形（置信度高：任务一 git 层已被 final3 W9-6 收口、只剩磁盘残骸待 Owner 拆；任务二已被丙线裁定 #384 WO-14 取代变形、且"豁免未登记"的前提本身是误判（06-22 就已登记）；任务三宪法 A/B 班整块零开工）
category: E类-施工批（审计车道）+ D类裁定项
priority: P2（任务三为 P2 大件；任务一/二为小件）
size: 一小 / 二小到中 / 三大
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 686-762 行（"九："节）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-09 规则审计战役收尾三件

## 0. 一句话结论

三件事里只有任务三（宪法文档 A/B 班）是完整存活的真活。任务一（拆工棚）的 git 层已被 final3 W9-6 在 09-19 做完（分支删除、staging 清点、四证 ALLOWED 存档），只剩 15,533 个文件的磁盘残骸，而删除动作被 OPS-GUARD 禁止会话内进行——归 Owner 门位。任务二（#356 尾巴）已被丙线 WO-14（裁定 #384）取代变形：design_memos 的 index.md 其实早已生成，现在整个目录正被 st-code-doc 会话以"README 替代 index.md"新惯例归置中（staged 在途，不可碰）；原文"三豁免面未登记"是误判——生成器 EXCLUDE_NAMES 早在 2026-06-22 就含 _archive 与 _。另有新发现：09-21 凌晨暂存区里躺着本任务的正式交接令（2026-09-21-tails-handover-prompt.md，staged 未提交，无人认领）。

## 1. 背景与来龙去脉

规则审计战役主体完结（夜班取证、Max 判案 #340-#360、final3 逐批落地）后，收尾班令列三件：任务一=拆陈旧工棚 st-auditdoc-v4-20260918（W5 遗留）；任务二=#356 尾巴（最后 1 个真缺 index.md+3 个豁免面登记）；任务三=W6 记忆文档 A/B 班（AGENTS.md 140 行现行版 vs 简化版的 A/B 双盲对抗测试，判断宪法能否内收）。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 任务一：工棚待拆 | 目录实体仍在（15,533 文件，mtime 全 09-18 晚），但 git worktree list 无条目、无 .git 指针、被 gitignore 忽略=纯磁盘残骸；W9-6 已实证分支产出全在 dev、分支已删、staging 交付件 TTL 已过且内容经 R-A6..R-A11 调查入台账 | git worktree list + w9_6_branch_cleanup.md:63,101-125 | A |
| 任务一：四证 | 已有据：.runtime/gate_audit/worktree_abort.jsonl 三连记录，09-18 20:51 ALLOWED（四证齐全）——回执可直接引用 | grep worktree_abort.jsonl | A |
| 任务一：4 个新工棚 | AI-GOVA-001/AI-TD2-GOV-001/AI-TD2-SEC-001/AI-VCFIX-001 都在，同样全是磁盘残骸；无会话在拆 | ls + find | A |
| 任务二：design_memos 缺 index.md | **已被取代**：#356 批 3/3（4a651a9552）当时已生成 index.md 且至今在 HEAD；现在该目录正被 WO-14（裁定 #384）归置中——49 件 staged 重命名（R）+README.md(doc_type:index) staged A，st-code-doc-20260921 的会话存活存疑（keepalive 心跳到 01:27 但 heartbeat.jsonl 末条记 pid 24952 status=exited）——动前先重测；此刻再生成 index.md 会与归置直接冲突 | git status 该目录 + README 头部 + keepalive + heartbeat | A |
| 任务二：三豁免面未登记 | **误判**：generate_missing_index_md.py 的 EXCLUDE_NAMES 含 _archive（:116）与 _（:118），系 2026-06-22 commit cb3abd9fe6 加入；dry-run 实证三面均不入缺失清单 | 读脚本 + blame + dry-run | A |
| 任务二：check_index_integrity | 零写盘检查器（读码证实后跑了 --warn-only）：2100 条 findings 全为存量噪音，与本任务零关联；**复验更正**：implementation_plans/ 并非新缺口——HEAD 的 17 件本就含 index.md（另有 00_index.md），且整个目录已随 WO-14/#384 同批归置（16 件+index.md 已 staged 重命名至 archive，盘上仅剩 README.md staged A）——主权在 WO-14，无需本卡补齐 | 读码 203 行 + dry-run + staged 实态复测 | A |
| 任务三：W6 A/B 班 | 零开工：rule_audit_campaign 无 A/B 产出；前置全就绪——adversarial_validation 模块 28 件在盘（WP17 已修）、AGENTS.md 实测 140 行、project_rules.md 实测 520 行、双过期镜像仍在（agent_constitution_l0.md 146 行 + legacy_v1.md 1651 行）、四盘点面全实存 | grep + ls + wc -l | A |
| 挖根：交接令被认领了吗 | 正式版未认领：docs/_working/rule_audit_campaign/2026-09-21-tails-handover-prompt.md（staged A，frontmatter session=st-maxday-20260919）与桌面原文同任务；作者会话无目录无心跳=已消失 | Read 对照 + grep | A |
| （新发现）CAS 残留 | scripts/governance/d1_structure/generate_missing_index_md.py.tmp.20724.7b5bf0a63634——safe_write 残留临时件躺在正式脚本旁 | ls | A |

### 病根

1. **交接令时效竞速**：任务二的标的目录在任务下达前数小时已被更高裁定（#384 WO-14）以"归档+README 替代"处置——收尾班各令彼此不读对方战役的 staging 区，任务粒度越细撞车概率越高。
2. **两套目录索引惯例并存**：生成器产 index.md（#355/#356 口径）vs 丙线放 README.md(doc_type:index)（#384 口径）——check_index_integrity/generate_missing_index_md 只认 index.md，README 替代面会永久计"缺"，需一次口径裁定收敛，否则每轮扫描都出假红。
3. .worktrees 残骸是系统性欠账：5 个棚全部无 git 注册（W9-6 清了注册与分支），但 OPS-GUARD 禁会话内删 .worktrees/**，磁盘体只能走 Owner/外部通道——"git 干净、磁盘 5 万文件"成为常态形态。
4. 派单前未 grep 被引路径（"豁免未登记"误判），与该战役自己坑册第 4 条自相矛盾。

## 3. 上下游

- 前置：任务一依赖四证（已有 09-18 ALLOWED 存证可引用）；任务二依赖 WO-14 归置件先落地（他会话在途，勿抢）；任务三依赖 WP17 已修的 adversarial_validation（已就绪）。
- 下游：CONSTRUCTION_LEDGER.md 战役总台账（三件回执落点）；任务三报告供 Max/Owner 决定宪法族收敛（WP13）。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 1（任务一残余） | 纯磁盘拆除：.worktrees/st-auditdoc-v4-20260918（15,533 文件）+.runtime/sessions/st-auditdoc-v4-20260918/（仅 heartbeat.jsonl）+.runtime/locks/heartbeat_st-auditdoc-v4-20260918.pid；回执记 W9-6 与 09-18 ALLOWED 四证为前置已完成项 | 上述三路径 | 三路径消失+回执入 CONSTRUCTION_LEDGER | Owner 门位（OPS-GUARD 禁会话内删 .worktrees；4 个 AI-* 新棚仍不拆除非 Owner 核台账后点头） |
| 2（任务二残余） | 先向 Max 提"index.md vs README.md 双惯例"口径裁定（涉 2100 条存量 findings 判定面收敛）；裁定后确认 WO-14 落地、按 README 替代惯例核销（implementation_plans 已随 WO-14 归置，无需本卡补齐）；可选：CONSTRUCTION_LEDGER 补记"豁免三面早已于 cb3abd9fe6 生效"的事实修正 | design_memos 与 implementation_plans 两目录（WO-14 主权）；generate_missing_index_md.py 口径 | dry-run 非 _working 缺失=0 且 check_index_integrity 不因本次动作新增红 | Flash 裁定（口径）+机械施工；**WO-14 在途期间本步冻结** |
| 3（任务三整块） | A/B 班开工：B 组简化版产出、三组双盲（A=现行 140 行 / B=简化版 / C=阳性对照砍冷启动）各答同一套 10 实战场景、按 xtreme-redblue-v3 计分口径出报告；判定硬线=C 组必须显著差于 A，B 缺口数小于等于 A 且连续两轮零新增才许切换 | 产出落 D:\ZephyrAlpha\docs\_working\rule_audit_campaign\（新子文件，报告+数据）；盘点面四路径 | A/B 报告在盘+adversarial_validation 门禁面回归通过+C 组显著差于 A | Max 确认方案后施工；宪法改动回流带 [ARCH-APPROVAL:ISSUE_ID]（本班只出报告不改宪法）；l0.md 分叉清单先回执勿删（WP13 未落地） |
| 4 | 清理 CAS 残留临时件 | scripts/governance/d1_structure/generate_missing_index_md.py.tmp.20724.7b5bf0a63634 | 删除后正式脚本完好 | Flash |

## 5. 与其他任务卡的关系

- **TC-02 C 组 = 同一个工棚**：本卡任务一优先，TC-02 已让渡，勿重复动手。
- TC-05：两个"W6"无关——本卡任务三=宪法 A/B 班，TC-05=词表战役轮次扫描；两者都产终态报告但落点不同。
- TC-04：D3 蓝图晋升同在 docs/03_modules 域，与 WO-14 归置避让在途件。
- 暂存区的 2026-09-21-tails-handover-prompt.md 是本任务正式交接令：执行时可先读它并考虑随本批落袋（防丢失）。

## 6. 风险与避让红线

1. 仓库实时推进（调查窗口 777 到 781 条脏条目）：任何动作前必须重测 HEAD 与 status。
2. st-code-doc-20260921 会话存活状态存疑（keepalive 心跳到 01:27，但 heartbeat.jsonl 末条记 pid 24952 status=exited）——动该目录前必须先重测会话存活与 staged 实态；其 staged 重命名含 design_memos/index.md——禁重生成 index.md、禁吸收禁 reset。
3. 任务三不碰宪法正文：只出 A/B 报告与建议；AGENTS.md 是受保护路径。
4. 拆除类操作走 Owner 通道，禁会话内 rm .worktrees/**。
5. A/B 班的 C 组阳性对照必须显著差于 A，否则废卷重出题（判定硬线，不可放水）。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；A/B 班的子代理全新双盲、互不共享上下文；计分真源=docs/_working/2026-09-13-xtreme-redblue-v3-plan.md 计分节。
