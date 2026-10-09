---
ttl: task_bound
title: 终局战役临时文件清理台账 20260930
session: st-finaldel-clean-20260930
---

# 终局战役 .runtime/tmp 清理台账（20260930）

会话 st-finaldel-clean-20260930。范围：仅 `.runtime/tmp/` 下 st-finaldel-* 与总筹明确创建的本战役临时产物；活动度防线=目录 mtime 与目录内文件最新 mtime 双查，2 小时内活跃一律不动（夜间五队在飞，宁可少清不清错）。

## 1. 清理执行（11 目标，全部确认不活跃后删除）

| 目标 | 体积 | mtime | 内容 |
|------|------|-------|------|
| st-finaldel-redblue-20260929/ | ~21 MiB（498 文件） | 09-29 22:46 | 红蓝对抗夹具：rx1/rx2 攻击现场、2×10.5MB 生成巨文件、tree_f_* 7 字节文件群、rx34repo 合成 git 仓、rx34_mutation_test.py |
| st-finaldel-chops-20260930/ | 3,883 B | 09-30 02:41 | c344_valuation_gapfill.py（chops 车道脚本） |
| st-finaldel-final/ | 1,614 B | 09-30 00:46 | msg_bagD.txt（提交词草稿） |
| st-finaldel-retire-20260930/ | 4,072 B | 09-30 02:53 | commit_msg2.txt + seal_dead_archives.py |
| commit_speed_audit/ | 85,474 B | 09-29 17:18 | analyze.py + gate_catalog.json + gate_stats.py（提交提速审计） |
| finaldel_drydemo_queue/ | 464 B | 09-29 23:58 | dead/q-20260915-drydemo-0001.json（死队列项） |
| finaldel_carch_commit.log / commit2 / commit3 | 4,163+3,794+5,943 B | 09-29 21:56-21:59 | carch 车道提交日志 |
| finaldel_carch_hits.txt | 15,478 B | 09-29 21:41 | carch 车道命中清单 |
| finaldel_refresh_files.txt | 2,511 B | 09-29 15:31 | 刷新文件清单 |

- 执行注记：redblu 首轮 rmtree 因合成 git 仓只读对象 PermissionError 中断（大头含两个 10.5MB 生成文件已清），第二轮以 chmod 重试句柄收尾；末轮精确计量 FREED=133,769 B，两轮合计释放 ≈21.2 MiB（du 逻辑量）。删除脚本带路径断言（非绝对路径、禁 `..`）与删后存在性复核。
- 全量逐文件清单（510 行，含字节数）存档：`evidence_archive/tmp_cleanup_inventory_20260930.csv`。

## 2. 证据归档（删前已存，防"证据丢失"争议）

- `evidence_archive/tmp_small_evidence_st-finaldel_20260930.md`（152,056 B，17 件全文证据束）：carch 提交日志×3、carch_hits、refresh_files、commit_speed_audit 全部 3 件、drydemo 死队列项、chops/final/retire 脚本与提交词、redblu 攻击脚本 4 件。每件含原路径、字节数与 sha256。
  - sha256 = 6edb5805e0ff92db7c586ddc57a540ae71cd89b863c55abbbe21a49c0eeab3cf
- `evidence_archive/tmp_cleanup_inventory_20260930.csv`（510 数据行：size_bytes/epoch_mtime/path）
  - sha256 = a2936ba46b98daa0bb29c4afd169cff6a2b8cd992aa726f7938f488280f853a6
- 格式改制注记：初版 zip+txt 归档因 DIRECTORY-CONTRACT（docs/_working/ allowed=[.md,.csv,.yaml,.html]）阻断，改制为 .md 证据束（全文内嵌）+ .csv 清单后合规，中间态 zip/txt 已删未入库。
- redblu 对抗测试正式结论已由案卷区 `redblue_report.md` 承载，其 tmp 夹具（生成巨文件/微文件群/合成仓）无独立保留价值，未归档仅留清单。

## 3. 保留清单与原因

| 目标 | mtime | 保留原因 |
|------|-------|---------|
| st-finaldel-c98-20260930/（2.3 MB，67 文件） | 09-30 05:30 | 活跃窗口内（c98 车道仍在收尾，最新战役袋 4817b8c4f4 即其产物）；重放对拍证据仍被台账注记 ad9b653807"重放证据目录指针"引用 |
| st-finaldel-final2-20260930/（空） | 09-30 06:01 | 活跃窗口内 |
| c98_trigger_surface_census.py（散件） | 09-30 02:33 | 属活跃 c98 车道，连带不碰 |
| campaign_hold/（1.2 MB，15 件） | 09-25 20:54 | 名义 campaign 但创建于 0925，归属无法确证为本次总筹——宁保留不误删 |
| campaign_msgs/（空） | 09-25 20:59 | 同上 |
| 其他会话 tmp（st-c9-*、st-nightsweep-*、csx-* 等其余全部目录） | — | 夜间五队在飞，零接触零判罚 |

## 4. claim 检查（残留=0）

- `.ailocks/registry.json` 全文扫描 `st-finaldel`：0 命中。
- `python scripts/lock_files.py list`：`CLEAN — 无任何文件锁`。
- 结论：无残留 claim，无需 release。

## 5. 主区卫生快照（只读；他会话在飞件不判不罚不清理）

- `git status --porcelain | wc -l` = 1044（夜间五队与各收尾会话在途工作）。
- 战役总袋数 `git log --oneline --grep="st-finaldel" | wc -l` = 59。

## 6. 红线遵守

- 未动 `docs/_working/final_delivery_campaign/` 既有正式案卷；仅新增 `evidence_archive/` 子目录与本台账。
- 未使用 git checkout/restore/stash/clean/reset；删除仅对白名单路径逐个断言后执行。
- 本台账与归档件经 git_commit.py 正门提交留痕，写后进程外复核。
