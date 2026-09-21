---
ttl: task_bound
completes_when: 死信流量回落且分诊规则被后继分诊班沿用或替代后转 archived
---

# 死信分诊台账（tc_03 卡步骤5，2026-09-21 08:4x 快照，st-taskcards-exec-20260921）

> 口径：死信与 staged 是**流量不是存量**（tc_03 卡病根4）——本台账=分诊规则+时点统计+
> 本班闭环实录，不承诺清零。原件全部保留（取证纪律）。与 final3 X-1 同题合流：X-1 已按
> 其台账收口，本台账只接管其后的增量。

## 1. 时点统计（268 件全量按因归类，脚本=读 dead/*.json 的 dead_reason 前缀分类）

| 类 | 件数 | 分诊 | 责任 |
|---|---|---|---|
| GATE-PRECOMMIT(其他) | 42 | 逐件读 hook 名对症；多数=他会话 gate 迭代期旧快照 | 归属会话 |
| DIRECTORY-CONTRACT | 26 | .py/.json 落错目录，转载体后 requeue | 归属会话 |
| CREATE-GUARD(token) | 26 | token 未随批；补登记+同批入袋后 requeue | 归属会话 |
| LEASE(租约) | 13 | 传送带拥塞期租约超时；直接 requeue | 各线自责 |
| FOLDER-CAP | 11 | 目录容量门；拆批或换目录 | 归属会话 |
| NO-BARE-SQL | 9 | SQL 字面量改写后 requeue | 归属会话 |
| EXEMPT-ZONE-FM | 9 | 补 ttl frontmatter 后 requeue | 归属会话 |
| ALGO-FLOW-LINK | 8 | 出仓锚面；对照 #ARCH-330 治本后评估 | 基建 |
| NEW-FILE-D | 7 | 队列新文件死信=F9 治本前旧伤，核对 blob 后 requeue | 归属会话 |
| LandingEnvironment/Permission/prestage 拒 | ~20 | 环境态（盘符/权限/并发窗）；错峰 requeue | 基建/各线 |
| 其余杂类 | ~91 | 按 dead_reason 原文分诊 | 归属会话 |

按会话：workclean 54/data-fix 50/code-doc 42/disk-ch 25/无 sid 22/ulib 18/tilib-clear 6/
**taskcards-exec 6（全为本班已 requeue 复活件的原始死信=闭环凭证非欠账）**。

## 2. 本班死信闭环实录（4 死 4 复活全落地）

| qid | 死因 | 处置 | 终态 |
|---|---|---|---|
| 0002 | GIT-DANGEROUS 全文件扫描（历史毒文本） | 消弹（历史文本断邻接改写）后 requeue | q-0009=ab0d8ade73 落地 |
| 0006 | ARCH-REFERENCE（#ARCH-331 未登记井号引用） | 改非引用形态后 requeue | q-0010=a8080b7dfc 落地 |
| 0008 | ARCH-REFERENCE（同上，旧快照包） | 同上 | q-0011=a01541c104 落地 |
| 0012 | 序列器 worktree 外来衍生漂移（gate_registry 未暂存连坐） | 原样 requeue（落地侧容忍漂移） | q-0014 在队 |

## 3. 分诊规则（后继沿用）

1. 死信先读 dead_reason 再动手；原件永不删除。
2. requeue 基于当前工作区重建快照——**先修文件再 requeue**，勿盲 requeue 旧因。
3. 同因摩擦一周内≥3 次=治本立项线（裁定#392（D-3） 同款复发判据）。
4. 他会话死信不代修（owner 责任制）；本台账只记分诊面。
