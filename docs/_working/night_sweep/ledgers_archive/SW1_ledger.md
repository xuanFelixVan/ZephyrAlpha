---
gate_selfdoc: GIT-DANGEROUS
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW1_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW1 字节抢救与队列车道 · 夜战台账（st-nightsweep-sw1-20260929）
# 总筹=st-nightsweep-chief-20260929 | 更新=2026-09-29 04:2x（收尾前最后复核）
session: st-nightsweep-sw1-20260929

cards:
  C1_战情室落库:
    verdict: DONE-LANED-PENDING
    detail: >
      docs/_working/night_sweep_20260929/00_orchestration.md（补 frontmatter ttl:task_bound）已落盘；
      CREATE-GUARD token 2 件已登记。token 批 q-0001 被队列 dedup-supersede 吸收进 q-0011 后，
      按 commit_navigation_playbook"token 批与内容同批"正门改投同批袋：q-0012（registry+总纲）已 ENQUEUED。
    next: q-0012 落地后 git log -1 --name-only 核验
    evidence: >
      q-0012 ENQUEUED files=2（同批通道预检通过）；q-0012.meta.supersedes=[]（与 q-0011 并行无害，
      registry insert-only 幂等）

  C2_骨架补干册:
    verdict: DONE-LANED-PENDING
    detail: >
      00_skeleton_nightsweep.md 产出 132 行一行不缺（F001-F132）；
      状态轴=已通64/开口57/等Owner11（机械判定规则写死册头）；
      开口项映射审计卡（canonical.json 534 卡词边界机判，57 环节挂卡）+接线清单四层缺口标注；
      处方指针 132/132 指 fullconnect per-F 卷（docmap 机生）；生成器=.runtime/tmp/st-nightsweep-sw1-20260929/gen_skeleton_nightsweep.py（四真源可复跑）。
    next: 随卡1 内容批落地（同前置）
    evidence: >
      行数复核 rows:132 missing:[]；分母复核 122(F01-F122)+10(F123-F132 verified L72)；
      基态分布 built81/partial30/design5/missing6 与接线清单§1.4 全等

  C3_C38雷:
    verdict: DONE-LANED
    detail: >
      scripts/governance/next_ruling_id.py + tests/governance/test_next_ruling_id.py 暂存区 D+untracked ?? 双态甄别：
      HEAD 有件（bfdd84a440 波5.2 落地）；全 registry 无会话 claim（含 17 活跃会话逐一查 held_files）=无主误删；
      untracked 副本均与 HEAD 有差（py=整体重写异版 303 vs 340 行；test 仅 6 处空行差）→双副本移
      .runtime/tmp/st-nightsweep-sw1-20260929/c38_evidence/ 留证；两路径精准 restore --staged+--worktree，
      恢复后与 HEAD diff=空。净变化=零（回归 HEAD 态），无 commit 需要。
    evidence: >
      git log --oneline -3 = bfdd84a4402；status --porcelain 两路径=空；
      git diff --stat HEAD -- 两路径 = 空；c38_evidence/ 两副本 md5 留存

  C4_q0167重投:
    verdict: DONE-LANED-PENDING
    detail: >
      原袋已在 dead/（死因=GATE-PRECOMMIT-RUN/gate-detect-git-dangerous 拦 redblue_robust.md 正文
      'git reset --hard' 报告文本 1 处）。两 blob sha256 验真取出落盘；按总包裁定 A3 加
      gate_selfdoc: GIT-DANGEROUS frontmatter（正文 hit 1≤上限10），双检测器本地复跑 0 findings；
      以当前 HEAD 为 base 换新袋 q-20260929-st-nightsweep-sw1-20260929-0002 重投，
      message 首行=[代投自死信恢复·原袋0167]。token 已在 HEAD 册（L36291/36296 实证）。
      旧袋 q-0167 留 dead/ 原处（内容落地后按卡6判据可归档）。
    next: q-0002 落地后 git log 验证两件在 HEAD
    evidence: >
      sha256 两 blob 全验 True；detect_git_dangerous 修后 rc=0（GATE-SELFDOC 豁免留痕）；
      q-0002 ENQUEUED 04:07 files=2

  C5_队列看板:
    verdict: DONE-LANED
    detail: >
      .runtime/tmp/st-nightsweep-sw1-20260929/queue_watchboard.yaml 机生：快照 28 袋逐袋
      qid/属主/件数/base_head/与我方卡关系。chief7-0253(40件)/0293(36件)=核销对象在队勿动；
      st-zc9 系/st-c8-rulings/st-matrix-revive/st-secbatch/st-tailwork2/st-zcloseout=他队领地只看不动；
      GPU 袋 st-gpu-conv2-0001 已转 dead/（属主自责任，未代投）；st-s52 不在队；死袋禁投清单（ec2-p0 系+0021）隔离未动。
    evidence: >
      pending 实测 28（开战简报 19+期间新增）；watchboard yaml 28 bags 全记

  C6_死信批次1:
    verdict: DONE-LANED
    detail: >
      1086 封全量机扫（逐封逐件 git cat-file -e HEAD:path）：769 封全件在 HEAD=可归档；
      317 封有缺件留原处（dead_scan_blocked.txt 台账，后续代投池）；保守剔除禁投清单 26 封
      （st-ec2-p0 系+0021 尾号）。实归档 743 封→dead_archive_final/，75 批每批≤10 批批验证全 True，零删除。
      目标≥100 实达 743。q-0167 在缺件桶（其报告件随 q-0002 在途，落地后下轮可归档）。
    evidence: >
      run_dead_archive.py moved:743 errors:0 all_verified:True；
      dead 剩 343=317 缺件+26 剔除；archive_final 计 743

  C7_rules_integrity_db出库:
    verdict: DONE-LANED-PENDING
    detail: >
      Owner 批②：git rm --cached -f（暂存第三态=派生哈希 churn，staged 2c0ba5fb vs HEAD cff0dbc5 纯 hash 差，
      随出库废止；盘面 3551 bytes 保留）；删除袋 q-0003 已入队。
      顺序假设=队列 FIFO：st-zcloseout-0083（同路径 post-flush re-register，04:07 创建）先于 q-0003 落地，
      终态=出库；若 0083 死信则 q-0003 独立生效，两分支终态一致。message 已留痕。
    next: q-0003 落地后核 git ls-files 该路径为空
    evidence: >
      git rm --cached -f 成功；git status = D(index)+??(盘面)；q-0003 ENQUEUED files=1

  C8_blob归档:
    verdict: DONE-LANED
    detail: >
      dry-run（--json）：在盘 23264 块；桶分布 A live 344/38MB、B dead_only 2271/650MB(禁碰)、
      C2 done_only 1402/435MB、C1 混引 652/115MB、D archive_only 9501/1.3GB(phase2 挂起禁碰)、
      Z 孤儿 7333/1.5GB（其中 mtime>7d 候选 7050/1.2GB）、混引 1757/308MB；
      幻影引用 216。实弹第一批 --archive：7050 块孤儿→blobs_archive/ + manifest.jsonl 留痕，
      竞态重扫跳过 0，禁删只归档（D 类/B 类未触碰）。
    evidence: >
      blob_gc.py --archive 输出"已归档 7050 个；manifest 落盘"；blobs_archive/ 计 7051 文件（含 manifest）

  C9_107件文档落库:
    verdict: DONE-LANED-PENDING
    detail: >
      git status 实测 107 A + 1 M（M=99_skipped_for_owner.md 非 f83/f97，无 claim，不属本卡不动）。
      token 覆盖甄别：93 件在 HEAD 册→5 批（20×4+13）q-0005..q-0010 全部 ENQUEUED
      （事故自愈：批1 重复投出 q-0005+q-0006，队列 dedup-supersede 自动吸收，q-0006.supersedes=[q-0005]）；
      14 件 index.md 缺 token→补批登记（capability=fullconnect_campaign 14 条 CAS OK），
      原 token 袋 q-0004 被 q-0011 supersede 吸收；14 件内容遇 EXEMPT-ZONE-FM 拦截
      （frontmatter doc_type 豁免区禁带，gate 处方剥离 doc_type 14 件各 1 行）后，
      依"token 批与内容同批"正门 q-0014（registry+14 index）ENQUEUED。
    next: q-0006..q-0010/q-0014 落地后 git log 验证 107 件全在 HEAD
    evidence: >
      5+1 批 ENQUEUED 实证；batch_creation_tokens OK 14 条；
      EXEMPT-ZONE-FM 修复后预检通过（q-0014 files=15）

  C10_du881:
    verdict: DONE-LANED-PENDING
    detail: >
      data/strategy_intake/du881_verdict_case/ ?? 态两件：盘面已是 .yaml（st-ddup 按 DCR-005 .txt→.yaml
      内容零变更中断半途：HEAD 册 token 还是 .txt 旧名，casefile.md 引用还是 .txt）。
      check_directory_contract 实测：.txt 在 data/ 违 DCR-005（.yaml PASS）→.yaml 转换为正解。
      处置=补 .yaml token（1 条 CAS OK）+casefile.md 2 处 .txt 引用改 .yaml（git diff 4++--）+
      三件+registry 增量同袋 q-0011 入队。FMS deadref 基线/清单 CSV 记录态不碰（SW6 领地）。
      旧 .txt token 为 append-only 册内历史条目，未动（登记废止属 Owner/注册表车道）。
    next: q-0011 落地后核 data/ 两件在 HEAD+casefile 引用解析有效
    evidence: >
      DCR-005 双向实测 rc(.yaml)=0 rc(.txt)=1 error；q-0011 ENQUEUED files=4

concurrency_notes:
  - 队列 dedup-supersede 机制实证：新袋同文件集自动 supersedes 旧 pending 袋（q-0011 吸收 q-0001/0004；q-0006 吸收 q-0005），token 前置集中于 q-0011 一袋
  - 队列消化中（lease pid 38828 活跃，zc9 三件已落地 edf0788dfb/fe3d981cfc/1cf01067f5）；我方 8 袋在 pending（ahead 20-30）
  - 让路登记：f83/f97 M 态=无（实测仅 99_skipped_for_owner.md M 态无 claim 不属卡内）；st-zcloseout-0083 同路径先序袋按 FIFO 让路并留痕

handoff_to_chief:
  - 待队列落地后补收尾：卡1 内容两批+卡9 14 件 index 内容批（message 文件与清单均已备好，见 tmp 目录）
  - dead 缺件 317 封清单=dead_scan_blocked.txt（后续代投池）；禁投 26 封未归档
  - q-0167 旧袋+GPU dead 袋留 dead/ 原处未动

final_queue_state:
  snapshot: "2026-09-29 ~04:50"
  my_bags_pending: [q-0002(红蓝报告2件), q-0003(ridb出库), q-0006..q-0010(fc 93件5批), q-0011(du881+registry), q-0012(总纲+registry), q-0013(骨架+registry), q-0014(index14+registry)]
  my_bags_absorbed_by_supersede: [q-0001→q-0011, q-0004→q-0011, q-0005→q-0006]
  drain_note: >
    belt 在岗消化中（sw6 三件已落地 984c1787f8/9abbe6f1bc/9a2c6402d4/06dc31b719）；
    chief7 核销对象 0253/0293 在我方袋前（ahead~5/9），我方 11 袋排其后；
    落地验证义务移交 chief 波次复核：git log 验证各袋首件+dead_archive_final 743 计数不变式。
  ledger_evidence_files:
    - .runtime/tmp/st-nightsweep-sw1-20260929/queue_watchboard.yaml
    - .runtime/tmp/st-nightsweep-sw1-20260929/dead_scan_archivable.txt
    - .runtime/tmp/st-nightsweep-sw1-20260929/dead_scan_blocked.txt
    - .runtime/tmp/st-nightsweep-sw1-20260929/dead_archive_log.json
    - .runtime/tmp/st-nightsweep-sw1-20260929/c38_evidence/
    - .runtime/tmp/st-nightsweep-sw1-20260929/gen_skeleton_nightsweep.py
```
