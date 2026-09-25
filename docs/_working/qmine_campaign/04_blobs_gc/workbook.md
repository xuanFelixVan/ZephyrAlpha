---
ttl: task_bound
title: QMine作业簿·blobs退役通道（M4）
session: st-qmine-20260925
---
# blobs 退役通道作业簿（M4）

> 只读调查+本簿；未动任何代码/队列/blobs。扫描原型=inline python（未落盘），扫描口径：四态（pending/processing/done/dead）+ **归档史全集**（dead_archive* 7 目录、dead_purged_20260920、dead_triage* 5 个 jsonl、hold_st_gov2、hold_stress manifest.jsonl）逐 files[].blob_sha256 + 全文 64-hex 反查。生产实测 2026-09-25。

## 1 六向台账
### ①上游输入
现状自基线（qcure bag_storage 簿）以来剧变：blobs 19955/3.2GB → **20504 个/3.42GB**；袋总量 1353 → **4486**（dead/ 623、done 810、pending 1、hold 2、dead_archived 2011、triage jsonl 1039 行）。期间发生多波 dead 归档（x1:912 项、w8:505 项、ulib3_zombie:51 项等）与**至少两次 blob purge**（purge_audit_20260911.jsonl 184 行，带 `blobs:[sha...]` 清单 + `why:gate_item_failure:item`；dead_purged_20260920/ 113 项）。cleanup_done（CQ:1949-1994， landed_at 缺则 mtime，TTL=7d `_DONE_TTL_DAYS_DEFAULT` CQ:187）只删 done JSON、明文不碰 blobs——done JSON 删除后其 blob 即失引用，这是孤儿的主生成机制。
### ②下游消费
复查全仓 grep（基线长尾第 5 条闭环）：blob 唯二读者不变=落地 `_apply_snapshot`（LAND:1348-1353）+ requeue `--from-bag`（CQ:1856-1875）；`requeue_dead_item` **只读 `root/dead/<qid>.json`**（CQ:1818-1825）——**dead_archive* 目录机械上不可 from-bag 取回**，除非先把 JSON 搬回 dead/。ops_guard.py:131 注释确认队列数据（pending/blobs/dead）刻意不入删除白名单（误删受保护区拦截），仅 serializer.lease 段级豁免（ops_guard.py:126-131）。
### ③机制现状+业界参照
- Git：不可达对象不即删，`git gc --prune=<date>` 只回收宽限期（`gc.pruneExpire` 默认 **2 周**）外的不可达对象；`git gc --auto` 阈值触发。https://git-scm.com/docs/git-gc 、https://git-scm.com/docs/git-prune
- Borg：prune（按策略标删）与 compact（真正回收空间）**两步分离**，删除可回滚窗口内 repack 可恢复。https://borgbackup.readthedocs.io/en/stable/usage/prune.html 、https://borgbackup.readthedocs.io/en/stable/usage/compact.html
- restic：`forget --dry-run` 预演 → `prune` 两阶段（先标记/重打包后移除），`--max-unused` 控浪费上限。https://restic.readthedocs.io/en/stable/060_forget.html
- 同构结论：**引用计数+宽限期+归档先于删除**三家一致；QCure 差异仅在 blob 可由 worktree 内容再生（`_store_blob` exists 跳过写，CQ:489-494），使"归档挪走"竞态天然自愈。
### ④代码面
CQ 已 2925 行（基线 2400，9 天 +525 行）；LAND 3220 行。blob 写=CQ `_store_blob`（blob 先于袋 JSON 落盘）；清=CQ cleanup_done（仅 done JSON）；读=上述唯二。**blob 退役无任何实现与测试**（同基线归因：功能不存在）。
### ⑤运维/呈现面
`queue_health` 只报 blobs 总数（CQ:1860）；孤儿/幻影/容量零观测。历史 purge 均留审计 jsonl（purge_audit_20260911、dead_triage_*）——退役通道沿用"动作必留 manifest 审计"先例。
### ⑥失败态与数据面（M4 精确账本，2026-09-25 实测）
| 类 | 判定 | 个数 | 字节 |
|---|------|-----|------|
| A 活引用 | live/hold 引用 | 190 | 4.3MB |
| B 仅 dead 活引用 | dead/ 独占 | 2504 | 392.1MB |
| C1 done+归档混引 | done ∧ (archived/triage) | 1620 | 240.0MB |
| C2 仅 done 引用 | done 独占 | 1806 | 410.5MB |
| D 仅归档 dead 引用 | dead_archive*/purged 独占 | 9133 | 1.30GB |
| Z 零引用孤儿 | 无任何 JSON 引用 | 5251 | 1.08GB |
| 幻影引用 | JSON 引用但 blob 缺盘 | 216 | — |
孤儿年龄：7-30d=4978/879.9MB、1-7d=220/166.7MB、<1d=53/34.1MB、≥30d=0。done 独占且全部超 7d TTL 的仅 1 个/0.1MB（cleanup_done 持续跑，done/ 恒新鲜——基线"仅 done 5658"已被 cleanup 消化成孤儿）。幻影归属：215 个=dead_archive_20260830（913 引仅 698 在盘），1 个=done——与 0911 purge 审计互证，**blob 删除史有先例且已造成归档袋缺盘**。死因分布：dead/ 623 项中 COMMIT_FAILED 423、landing 异常 116、NOTHING_TO_COMMIT 31、CLAIM_REQUIRED 15、cascade_stale 15；归档 2011 项同构（COMMIT_FAILED 1493）。

## 2 方案
### ②退役策略分层（定案建议）
1. **A/B 类：禁碰**。B（2504/392MB）是活死信回放面——from-bag 依赖真实（CQ 只认 dead/），且"dead 永不清理"是 66 号 §8 不变量；COMMIT_FAILED 主死因说明仍是可回放积压而非垃圾。
2. **C 类：不动，等 cleanup_done 自然消化**。done JSON 过 7d TTL 被 cleanup_done 删 → C2 自动降级为 Z 类，下一轮 GC 即回收——**不需要 GC 针对 done 做任何事**，只管把 Z 类扫走。C1 混引中归档半边弱化后同理。
3. **D 类（9133/1.30GB，最大矿）：归档不删**。机械论证：requeue 够不着（只读 dead/）、落地只碰 pending/processing ⇒ D 类 blob 当前**零读者**。但它不是"永不可删"的反面——归档 JSON 是 forensics/人工回放记录，激进删会重演 dead_archive_20260830 的 215 幻影。处置：随 JSON 一起语义绑定——blob 挪 `blobs_archive/` + manifest 留 sha/大小/来源归档波次，可逆还原；不删。
4. **Z 类：归档优于删除，宽限 7 天**。`孤儿 ∧ blob mtime>7d` → 挪 blobs_archive/。宽限期建议 **7 天=done TTL**（同构 git gc 2 周口径，取本项目已有节奏；<1d 的 53 个正是"blob 先落、袋后落"入队竞态窗，mtime 宽限天然覆盖）。不选 24h：跨周末批+done TTL 7d 语义统一性优先；不选 14d：回收量差异小（孤儿集中在 7-30d 段）。
5. **删除永远不在此命令默认域**：blobs_archive/ 的 TTL 清空是未来独立裁定（Owner 门位+ops_guard FORCE_ENV，宪法 §5.2），本通道只到归档为止。
### ③竞态防护（四层）
1. mtime>7d 宽限杀掉入队竞态窗（blob 先写必新鲜）；
2. 扫描→候选集→**动前二次重扫取交集**（关掉"扫描后袋刚入队"窗）；
3. 即便漏网：挪走后同 sha 再入队时 `_store_blob` exists 检查失败→从 worktree 内容**重新落一个新 blob**——内容寻址自愈，零丢失仅一重复副本；
4. 全程不持 SerializerLease（长批任务不进队列关键路径；候选集构造上已排除 live/processing 引用）。
### ④施工设计
**独立脚本 `scripts/governance/blob_gc.py`（推荐），不加 CQ 子命令**。理由：①CQ 2925 行且是 enqueue/drain 关键路径+gate 密集区，再碰违反净零内收（宪法 §4）并放大回归面；②先例=LAND 同为队列兄弟子系统、独立住 scripts/governance/；③GC 是长批任务，语义上不能进 drain lease 生命周期（cleanup_done 在 lease 内，GC 反之）；④依赖极薄：只需 `resolve_queue_root`+目录约定，import 单函数即可。
接口：默认 **dry-run** 打印分类计划表；`--execute` 显式旗才动盘（挪=同卷 os.rename，原子）；`--grace-days`（默认 7）；`--phase`（1=仅 Z 类；2=+D 类，D 类须逐袋核对归档 JSON 仍在）；`--json` 机器输出。动作留痕：`blobs_archive/manifest.jsonl` 追加 {sha,size,mtime,class,run_id,src_verdict}——对齐历史 purge 审计先例，还原=按 manifest 反向 rename。
ops_guard 交互：归档=rename 非删除语义，预期不触保护区（**须补测试钉死**）；未来删除阶段才需 FORCE_ENV+Owner 门位。
规模预估：脚本 ~350-450 行 + 测试 ~200 行（tests/，tmp_path 隔离）+ CREATE-GUARD/depgraph 登记；零改动 CQ/LAND。可选后续小件：queue_health 增孤儿计数（import blob_gc 扫描函数，只读）。

## 3 三态裁定
**施工**：blob_gc 归档通道（phase1=Z 类+7d 宽限+dry-run 默认）建议立项，数据/设计/竞态论证全部就绪，规模 ~600 行含测试，低风险。**挂起**：D 类 9133/1.30GB 归档建议随 phase2 排期（须先裁定"归档 JSON 与 blob 绑定保留"口径）；blobs_archive TTL 删除另走裁定。**不施工**：B 类任何回收（违反 dead 永不清理不变量）；done 专项回收（cleanup_done 已自然消化，做=重复建设，净零判据 w5_1 零触发即退役面）。

## 4 长尾清单
- 扫描原型未落盘；blob_gc 正式化时以本簿 §2④ 为蓝本，先走 CREATE-GUARD/depgraph 登记。
- 幻影 216 的善后：dead_archive_20260830 的 215 缺盘引用建议在 phase2 前补一次"幻影标记"（manifest 注记 blob 缺失），防未来人工回放踩空。
- requeue 熔断（requeue_count≥3）后的 dead 项实际不可回放，其 blob 是否可降级归档——留待裁定（涉 66 号 §8 不变量解释权）。
- 20004 文件平铺无分桶（基线矿#4）未变：GC 落地后 blobs/ 一次可减 ~1 万文件，枚举成本顺带缓解，分桶仍登记不挖。
- hold_stress_phaseB manifest.jsonl 30 项引用的 blob 归 A 类保护，无风险；hold 语义若变需复审。
- 本次会话窗口内 pending 1 项在扫——账本数字为该瞬时快照，正式 GC 以其自身扫描为准。
