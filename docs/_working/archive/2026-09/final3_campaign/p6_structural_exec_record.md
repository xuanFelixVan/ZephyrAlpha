---
ttl: task_bound
completes_when: P14 终局报告落盘
session: st-maxexec-20260920
issue: MAXEXEC-P6
---

# P6 结构性签字件执行批终版记录（st-maxexec-20260920；P6 前班+续班+总包合力）

## 执行清单（裁定#374 八项 vs 实况）

| # | 项 | 状态 | commit/证据 |
|---|---|---|---|
| ①主题三 | A12+B3 归档 git mv | ✅ | 7f1b68f384（125 文件：12 目录+handoff/xt_lab3+HANDOFF-PROMPT；depgraph --force 同批；24 件归档 index doc_type 剥离；1 件危险文本隔字；naming skip 补 archive 区配套——归档历史命名不追溯） |
| ②主题四 | ig bak 92 表清理 | ✅ | 1725ee4a0c（80 张旧份 DROP 执行+前后计数红证，每族留最近 1 份+活表） |
| ③主题五 | 自启方案 B | ✅ | 2bc52c77e4（壳 Startup 快捷方式+serve_docs keep 补缺+验证） |
| ④主题六 | #342 B① a 案+B② | ✅ 批在途 | directory_contract 运行态数据目录条目+B② fail-closed 核实在案（P6x 遗作已编辑，0065 死信随本记录批重提；若仍阻列 P14 遗留） |
| ⑤主题七 | 两分支终裁 | ✅ | 裁定#373：报告并入 8a1730c159+token 批 7f9d8fbfc；分支/worktree 已拆 |
| ⑥主题十 | W1 遗留 2 件 | ✅ 批在途 | 10-1 index.md（断引用已消解）+10-2 GATE-21 已知限制（0065 批内） |
| ⑦master FF | DEBT-BRANCH-001 | ✅ | d92ea66538→7f1b68f384（git fetch . dev:master 非检出式 FF，主区脏不阻断） |
| ⑧13 棚三裁 | worktree 终态 | ✅ | worktree list 22→5（主仓+st-maxexec+st-tilib-clear 活会话+pool/serializer 锁定基建）；P6x 完成 sowner002/tv2terrain/final3 等 17 棚拆除；salvage 件在 p6_shed_salvage*/ |

## 台账联动

w9_triage_ledger.md 15 行销账（12 A 行+3 B 行→已归档态）；C 类计数相应下降（P11 台账终数以 P14 复扫为准）。

## 本批新坑入册（供 P9 治本池）

1. 归档区 gate 三连坑：EXEMPT-ZONE-FM（归档 index 带 doc_type）→ 剥离；N-13/N-16 对搬运件追溯 → skip 补 archive 区（check_naming 双位+trae_028 同步，#344 同族）；DOC-REF-BROKEN 对 gitignore 派生区盲 → 纯文本化。
2. 序列器 worktree 残留四件（integrity_db/manifest/rule_catalog/architecture_model index）致连环 mutation 死信 → `git -C .runtime/commit_queue/worktree checkout -- <四件>` 配方。
3. git fetch . dev:master=脏树下的正门 FF 等价物。
