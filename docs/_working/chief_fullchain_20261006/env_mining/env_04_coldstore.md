---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_04_coldstore.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-04 冷备 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/data_supply_chain_map.yaml segments[S4_coldstore]；血肉卷=docs/_working/map_build/fig12_datachain/04_冷备灾备与分层.md
- **职责一句话**：契约决策→滚动归档/手动归档→镜像灾备（全项目唯一含不可逆删除的日常面）
- **节点清单（9）**：DSC-10A 手动CLI归档(built)｜DSC-10B 滚动归档事件触发器(built)｜DSC-11 灾备双链备份(built)｜DSC-HB 交接B热→冷(built)｜DSC-12 冷热分层/压缩决策(partial)｜DSC-HC 交接C冷→恢复(partial)｜DSC-GAP-ARCHIVE-AUDIT 零抽检零restore(pending)｜DSC-GAP-CODEBACKUP 代码快照腿failed(pending)｜DSC-GAP-MIRROR /MIR删镜像P0(pending)
- **状态分布**：built=4 / partial=2 / pending=3（与 counts.segment_S4_coldstore=9 合）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 全网/外部 | 判定 |
|---|---|---|---|
| ①上游 | 边：DSC-04/06→DSC-HB（超线分区+当日备份回执=准入门）→DSC-10A/10B/11；DSC-12→DSC-10B（契约参数驱动：batch_max_partitions=3/circuit_breaker_failures=3，src 侧真源 docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml §rolling_archive，本批涉他队 claim 区只读未逐条展开）；DSC-11→DSC-10B trigger（backup.ps1 STAGE 4b 成功事件钩子，scripts/backup/backup.ps1:1064-1073 实锚） | — | signal |
| ②下游 | 恢复侧消费方 grep：scripts/backup/restore_drill.py、scripts/ch/_recovery_drill.py、scripts/ops/r6_restore_via_vm.py＋archiver restore 子命令（scripts/ch/archiver.py:903）。冷库 manifest 实锚核验：F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl mtime=**2026-09-28 17:10**（较图读数 09-24 有推进；国庆窗+第二链维修期滞后待判）；data/databases/rolling_archive_state.json mtime=**2026-09-21 15:37**——与 manifest 差 7 日，**台账冲突（P-1）仍成立且加深** | — | signal |
| ③算法机制 | archiver 五子命令在码（scripts/ch/archiver.py:874-903 archive/archive-range/export/list/stats/restore，export→verify→drop 顺序控制非事务）；rolling_archive_reconciler 五阀在码（scripts/ch/rolling_archive_reconciler.py:241 批限量/:267 熔断失败数/:320 kill_switch/:247 skip 带 reason 进 result 结构——但仅内存 result，4b stdout/audit-trail 无独立 jsonl 落档＝"skip 留痕零持久"精确化）；事件触发声明在件头（:25/:29 "不新增任何 schtasks/Timer/sleep-loop，backup_daily_trigger.ps1 为合法先例"） | 3-2-1 备份与定期 restore 演练=业界标配；删前探测（/L probe）=robocopy 删除传播防护的正统做法，与本仓新闸同构 | signal |
| ④后端代码 | src/：storage_tiering.py（src/zephyr/data/__init__.py:32 有 re-export import＝包级接线痕迹；ufl_deterministic_layer.py:4/:32、offline_store.py:41、api_server.py:2057 均为语义引用不 import——裁定#383 纸面退役判词维持）；data_compression_archiver.py 零调用方复核成立（全仓仅生成器文案提及）。scripts/：archiver.py、rolling_archive_reconciler.py、backup.ps1、backup_reconciler.py、backup_config.yaml、restore_drill.py。tests/：backup 域专项 test 未命中＝登记。**P0 重大新证**：backup.ps1 v2.1 头注（:13-14 "old robocopy /MIR single mirror propagated deletions (2026-09-14 docs/_working deletion incident)"）＋"先数后删"闸已落地（:141-152 /L probe 统计 would_purge 后才放行）；相关 HEAD commit 5d5398e8482 "[存储治本·删除传播与取件裁决] 唯一夜镜像的 /MIR 加'先数后删'闸"——**图 GAP-MIRROR 判词"防护只在未提交工作树里成立"已过时** | — | signal（登记滞后） |
| ⑤前端呈现（只登记不施工） | src/zephyr/frontend/dashboard/api_server.py:2057 冷层 tier 登记位（空 dict，"冷层启用迁表后在此登记"）＝分层决策的前端挂点已在册但未启用 | — | noise（登记） |
| ⑥数据字段 | 最新报告 logs/backup_report_20261005_224345.json 逐字段实读：g_mirror.targets 只剩 zephyr_cold 一项、would_purge=0、robocopy_exit=1/status=ok（P0 三要素全部转绿）；code_backup status=ok failures=0 vanished=0（09-25 的 failed 已自愈；rotated=[] 按当日 run 模式解读=待验证）；databases.clickhouse.status=**skipped**（skip 语义显式非失败，与图 fallback 判词一致）；stage_timeline 九阶段全录。10-05 单日三份报告（190405/193702/224345）＋HEAD commit 4e719ff8723 "第二链日检 09-28 第4/14天：12:26 轮卡死 19h 根因=exclude_dirs 漏 .worktrees"＝灾备链处活跃维修期 | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛，且产出两条图判词过时证据（MIRROR 已修、CODEBACKUP 已自愈）＋一条加深证据（state.json 与 manifest 时差 7 日）。
- **未挖长尾清单**：(a) data_retention_contract.yaml 逐条分层线参数核验（他队 claim 区，本批只读未逐条）；(b) restore_drill 计划任务今日运行态（Get-ScheduledTaskInfo 复核未做＝待验证）；(c) G:/backup 夜镜像 14 天日检的剩余天数（第 4/14 天后的推进）。
- **🌑不可得清点**：①10-05 三连发报告的触发者（手动/日检修复轮，无触发源留痕字段）；②rotated=[] 语义（该 run 无到期轮换 vs 轮换腿静默空转，二选一不可判）。

## §3 挖后自审闸三态裁定

**方案封矿（已建成执行面）＋ 施工（恢复验证一项）＋ 登记改判（两项）**

- **封矿**：DSC-10A/10B/11/HB 执行面——归档 export→verify→drop、事件触发五阀、四阶段备份链、"先数后删"闸全部落地且无人工参与位置（人工门位仅剩 10A 的"该不该跑"决策=契约允许的 manual 档）。终局里冷备就是这套形态，无新位置。
- **施工**：GAP-ARCHIVE-AUDIT——周期抽检＋端到端 restore 演练常态化（restore_drill.py 在码、计划任务从未运行的判词待复核）。终局量尺：删过原件的冷档"今天还可读"必须由机器周期证明，不能靠人记得——这是本段唯一剩余的人工位置，有位置故施工。注意：演练调度禁 cron/Timer（宪法红线），须事件触发或并入既有备份链阶段。
- **登记改判（非施工）**：①GAP-MIRROR P0→改判已修复待退役（证据：backup.ps1:141-152 删前计数闸＋最新报告 targets 单目标 would_purge=0＋HEAD commit 5d5398e；图 as_of 10-04 判词滞后）；②GAP-CODEBACKUP→改判观察（最新报告 code_backup ok/0/0，需连续绿读数后退役；10-05 维修期的多发报告属第二链日检工程）。
- **挂起**：DSC-12 决策件（rolling_archive_state.json 台账冲突 P-1 的归因）——解锁条件=skip 留痕 jsonl 落地（ENV-05 域 DSC-10B 施工项）后按留痕重判谁在动 drop。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：S4 九节点+交接三格（map:1858-2575） | signal | 10A/10B 拆行理由、12=决策非并列环节、HC 人工案卷形态全录 |
| 2 | 代码轮：archiver 五子命令/五阀/backup.ps1 STAGE4b+删除闸行号核验 | signal | **P0 防护已落地**（v2.1 头注+/L probe would_purge 闸）；skip reason 在 result 结构但无持久化留痕＝精确化原判词 |
| 3 | 消费方轮：restore 侧四件＋冷库 manifest/state mtime＋最新备份报告逐字段 | signal | manifest 09-28/state 09-21 时差 7 日=P-1 加深；targets 单目标+would_purge=0+code_backup ok＝两条 gap 判词过时 |
| 4 | 外搜轮：3-2-1/删前探测业界口径 | signal | /L probe 防删除传播为正统做法；定期 restore 演练为标配短板本仓亦然 |
