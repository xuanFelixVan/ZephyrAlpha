---
card_id: TC-02
title: 夜班遗留件处置（rule_audit_campaign 5 件 staged + .runtime 临时件 + 孤儿工棚）
verdict: 部分存活+变形（置信度高：5 件原样 staged 零提交，但处置权已被 WO-15/w15 判语预判为"留暂存待提交"；乙删除路线已死；工棚部分移交 TC-09）
category: C类-文书收口批
priority: P1
size: 小（1-2 个提交批）
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 149-238 行（"二："节）
investigated_at: 2026-09-21
head_at_investigation: 83329aef38
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-02 夜班遗留件处置

## 0. 一句话结论

A 组 5 个文件跨三个班次存活（仍 staged、HEAD 无、无人 claim），但原文的"甲提交归档 vs 乙删除"二选一已被后继班次改写：WO-15/w15 判语（6a6e77c8f0，09-20 23:58）逐条判这 5 件"C 类真未落地，留暂存待提交，交总包统一处置"，且引用面已扩到 19 处——**乙（删除）已死，甲（提交归档）存活但必须变形**（.patch/.json 过不了 DIRECTORY-CONTRACT 门禁）。悬空 token 从原文说的 1 条涨到 3 条。B 组临时件 4/5 已自然消亡。C 组工棚的 git 层已被 final3 W9-6 收口，只剩磁盘残骸，移交 TC-09。

## 1. 背景与来龙去脉

09-19 夜班（规则审计战役）产出后留下三类无人认领的尾巴：A 组 5 个进了暂存区但从未提交的交接文件、B 组 .runtime/tmp 下夜班自己的临时件、C 组手工注销后剩下的孤儿工棚 .worktrees/st-auditdoc-v4-20260918。原文要求先跑 classify_workspace_wip.py 等六步复审判据，再走甲（提交归档）或乙（删除）分叉。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| A 组 5 件 staged 未提交无人 claim | 全部属实且仍存活：5 件均 A 状态，git cat-file -e HEAD:各路径全 fatal，全 git 历史仅 stash index commit 9bd63d3e8d 含它们，54 把锁无一指向这些路径 | git status --porcelain + git log --all + lock_files.py list | A |
| 在途暂存约 496 件 | 涨到 563 件（动态值），且同目录今晨新增第 6 件 staged：2026-09-21-tails-handover-prompt.md（TC-09 的正式交接令） | git diff --cached --name-only 统计 | A |
| token 15 条命中，genpatch.py 悬空 | 注册表现 21 命中；genpatch.py 悬空 token 实锤且已进 HEAD 册（40596 行）；**另发现 2 条同类悬空**：dossiers_v2_index.json（40608）、dossiers_v2_summary.json（40612）——盘上只有 .yaml 版没有 .json 版 | grep 注册表 + 盘上 ls | A |
| 引用 10+ 处 | 现 19 处/11 文件。三处已入库引用健在；净增 2 处已入库正式产物：final3_campaign/w9_triage_ledger.md:185（判"保留，在飞/真源"）和 rule_audit_campaign/w1_f_judgment_book.md:64（验收命令直接引用 patch 路径） | grep -rn a2_handoff docs/ | A |
| patch 已 does not apply、内容作废 | 佐证强化：档案副本头注自述"产物已随 rules 批落地 48acb99c46"；裁定册第 372 号确认 M1 三分 rules 统一批落地 | head 档案副本 + ruling_registry | A（未复跑 apply --check，遵原文实测记录） |
| B 组五件临时件 | a3/、a7/、redlab_a1b/、cf1/ 四件已被 .runtime 清理消亡；仅 a2_genpatch_archived_20260920.py 仍在盘 | for 循环探测 | A |
| C 组工棚待拆 | 目录仍在但确认为空壳（无 .git 指针、git worktree list 无条目、被 gitignore 忽略）；heartbeat PID 7240 已死；session 目录无 staging 独有成果；git 层已被 final3 W9-6 收口（分支已删、四证 ALLOWED 存档于 .runtime/gate_audit/worktree_abort.jsonl 09-18 20:51） | ls + git worktree list + gate_audit 日志 | A |
| 挖根：#385 是否吸收这 5 件 | **未覆盖**。#385（a03179e2fa）处置对象是旧 N-5 的 137 件三分法+旧 stash（aa43e3b530），其台账全文零提及 rule_audit_campaign。真正预判处置的是更晚 13 分钟入库的 WO-15/w15 判语（w15_hanging_accounts_verdict.md，台账表行号 164-168=文件第 198-202 行）：逐条判"留暂存待提交，处置动作一律未执行，交总包统一处置" | ruling_registry 5127-5146 行 + w15 台账 + 台账 grep 零命中 | A |

> 注：staged 总数/引用命中数/锁数均为快照动态值（复验时 staged 已 581、a2_handoff 引用 28 处/14 文件、锁 50），方向性结论不受影响，以开工实测为准。

### 病根

1. **处置权漂移链**：原文写于 09-20 前后，其后 Max 日班判案、final3 落地（48acb99c46）、丙线 WO-15 判"留暂存待提交"接连发生——原文的"复审后二选一"已被降格为"执行 w15 既判"，但 w15 把处置动作明确推给了"总包统一处置"，本卡执行前必须先对表（步骤 0），否则就是双处置。
2. **账实分裂**：token 注册面已入库（6 条对 0 条入库文件），文件本体滞留暂存区 48 小时以上；其中 3 条永久悬空。
3. **甲路线的硬墙（原文没测出来）**：GATE-DIRECTORY-CONTRACT（gate_registry.yaml:242）+ directory_contract.yaml:405-411 规定 docs/_working/ 仅允 .md/.csv/.yaml/.html，且门禁用 git ls-files 递归扫描**管子目录**——.patch/.json 原样提交必被 DCR-005/008 error 级阻断。n5 台账第 5 节的 sim-memo .json 剔除先例与此互证。
4. 5 件被今晨 WO-13续 salvage stash 的 index commit 复制了一份（9bd63d3e8d），stash 条目存活——任何对 stash@{0} 的 drop/pop 都会搅浑取证链，那是他会话资产。

## 3. 上下游

- 前置依赖：步骤 0 与"总包统一处置"对表（Max/总包裁定）；capability_canonical_file_registry.yaml 是热文件且调查窗口刚有他会话改过——提交必走队列正门 + safe_write_text CAS 错峰。
- 下游消费方：capability 注册表悬空清零后 CREATE-GUARD 账实相符；w15 C 类余量 165 件的后续处置沿用本卡模式；TC-09 拆工棚可直接引用本卡 C 组实测。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 0 | 与总包对表：w15 判 C 类 168 件"交总包统一处置"，本 5 件是子集——确认由本卡执行还是并入总包批，避免双处置 | docs/_working/code_doc_gov_campaign/p4_ledgers/w15_hanging_accounts_verdict.md（台账表行号 164-168=文件第 198-202 行，"交总包统一处置"在第 8 行） | 总包台账有本 5 件认领记录或让渡回执 | Max/总包裁定 |
| 1 | 三件 .md（两个 index.md + A2_M5_prescriptions.md）保留提交；在 a2_handoff/index.md 顶部加注记"superseded by 48acb99c46（本 patch 已不适用，仅存历史证据）"（safe_write_text CAS）。注意父目录 index.md 是 #356 口径必需品（HEAD 已有 7 个 tracked 文件，删它=新增红） | docs/_working/rule_audit_campaign/index.md、docs/_working/rule_audit_campaign/a2_handoff/index.md、docs/_working/rule_audit_campaign/a2_handoff/A2_M5_prescriptions.md | check_index_integrity.py 无新增红；注记在盘 | Flash 可执行 |
| 2 | patch 与 json 二选一：(a) 推荐——内容转 .md 附录后删原文件，零门禁变更；(b) 原样提交需先在 directory_contract.yaml 加 allowed_exceptions（门禁面变更） | docs/_working/rule_audit_campaign/a2_handoff/rules_m1_repoint.patch、rules_repoint_rows.json；docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml 第 405 行附近 | GATE-DIRECTORY-CONTRACT 绿；文件或其 .md 载体入库 | (a)=Flash；(b)=Max 裁定 |
| 3 | 收 3 条悬空 token（genpatch.py 40596、dossiers_v2_index.json 40608、dossiers_v2_summary.json 40612），与上同批提交 | docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | registry 内零悬空（逐条 cat-file 盘上存在）；YAML 可解析 | 注册表净删属 Owner 门位敏感面——随裁定留痕或 Owner 确认 |
| 4 | 已入库引用处置：w1_f_judgment_book.md 末尾**追加**处置行（历史行不改写惯例）；夜班报告与 w9_triage 判"保留"无需动 | docs/_working/rule_audit_campaign/w1_f_judgment_book.md 第 64 行后 | git log -1 --name-only 归属正确 | Flash |
| 5 | B 组残留 a2_genpatch_archived_20260920.py：无门禁无引用，随 .runtime TTL 自然消亡，默认不动（如需保留历史复现能力则登记坐标一行） | .runtime/tmp/a2_genpatch_archived_20260920.py | 无需动作 | Flash（默认不动） |
| 6 | C 组工棚：移交 TC-09 任务一（同一对象，勿重复动手） | .worktrees/st-auditdoc-v4-20260918 | TC-09 回执 | TC-09 班组 |
| 7 | 交付回执按原文三清单格式：①裁定面（A 组判甲向变形、3 条悬空 token 收法、C 组让渡 TC-09）；②执行面（命令原文+退出码+git log -1 --name-only）；③复查面（复核命令+期望输出）。每条结论标[亲验]/[转报]/[推断]；自写盘点脚本先证明能红（防假绿） | 会话回复 | 三清单齐全、证据等级逐条在案 | Flash |

## 5. 与其他任务卡的关系

- **TC-09 任务一 = 同一个工棚**（TC-09 优先，本卡让渡）。
- TC-03 的 N-5 段已由 #385 收口，本卡已证实 #385 不覆盖 A 组——TC-03 无需再查这一面。
- TC-08 若吸收 w15 C 类全量，则本卡步骤 0 对表必须先行。
- TC-01：本卡 B 组清理已自然消亡大半，且必须豁免 memo_recon_20260920/（TC-01 输入件）。

## 6. 风险与避让红线

1. 暂存区 563 件他会话在途：一切写操作限点名 pathspec，永禁全目录 restore/reset。
2. 注册表热文件撞 HOT-FILE-BASE-FRESHNESS 概率高：走 commit_queue 正门。
3. 勿 drop/pop stash@{0}（他班 salvage 资产）。
4. Owner 冻结令"Working 文件夹内容先不要动"仍生效——本 5 件的处置授权来源=w15 判语+本卡，执行回执需引用两者。
5. 删 token 属注册表净删边缘，宁可多一道 Owner 确认勿硬闯。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；提交必经 scripts/git_commit.py 或 commit_queue.py --enqueue；改前 claim 毕后 release，claim/release/queue 一律在主仓 cwd，lock_files.py acquire TTL=30min、跨批复用必死信；提交后 git log -1 --name-only 核归属。
