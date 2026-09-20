---
ttl: task_bound
completes_when: 本线终验红蓝通过
---

# 【总包乙·磁盘与 CH 线】施工指令（自包含，新对话整贴即用）

# sid：st-disk-ch-20260921 ｜ 落盘：docs/_working/disk_reorg_campaign/（沿用，a0 总令已在此）｜ 模型：Max 总包+Flash 分包
# 上位方案：docs/_working/unified_campaign/00_master_plan.md；**W1 起步须 Owner 签字单批文（o_owner_signature_sheet.md）**

## §0 使命
CH 瘦身到位+日志滚动永久自动化+冷储主库迁 F+G 镜像+备份 3-2-1+宿主清偿+vhdx 季度压缩机制化。终态=五盘容量对照表全绿+热层约 360G 稳态+全自动无人值守+dashboard 冷储检测绿+恢复演练通过。**数据安全第一公理：任何删除前必须有两份验证过的副本；drop 前必须行数 verify。**

## §1 冷启动（每 shell 必做）
同甲线配方（PATH 3.12/lock cleanup/reaper/session_worktree_start+心跳）。加：开工日**重跑探针刷新台账**（盘位/CH 内部/system.parts 水位/D 盘 df）——本指令所有数字为 2026-09-19/20 实测，执行日禁凭记忆。

## §2 真源读序
1. docs/_working/cold_backup_automation/00_master_plan.md（自动化方案 13 章——本线母方案）
2. docs/_working/disk_reorg_campaign/a0_master_order.md（收口六波总令 W1-W7 全文——**本指令即其执行令，含验收数字与避让清单，照执**）
3. docs/_working/cold_backup_automation/01_mining_findings.md（挖矿发现 9 缺口+8 意外）
4. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml（保留契约真源）
5. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md（冷库 SOP 三红线）
6. dataqa R1（docs/_working/dataqa_audit/ch_health_report.md）作 W1 前后对照基线
7. 并入任务真源：A10/A12/A13/A14 细节同在 dataqa 四报告（technical_indicator 1339 parts/1970 假日期 18 表/12 小表碎片/77 表未登记资产册）

## §3 波次（=a0 总令 W1-W7+并入项，按依赖排序）
- **W2 日志滚动永久化（最急，无需签字可先行方案落地）**：text_log level 调低+system log 表原生 TTL（trace/query_log 7 天、余 14 天）+max_size 轮转→低峰重启 CH【重启窗避让一切在飞夜跑，开工前查计划任务+SessionRegistry】→24h 复测膨胀<1G/天
- **W1 CH 库内清偿（签字后）**：尸体表（=包②A11 备份污染表，张数 12 vs 17 执行日实测仲裁）逐表 export Parquet 双副本（F+G）→行数 verify→凭批文 drop；欠账 24.9G 走 archiver archive-range；验收=内部空闲≥200G+尸体清零
- **W-并入（签字后同窗）**：1970 假日期 18 表 43.6 万行（PIT 关死或补真值，Owner 已批选项）；12 小表 parts 爆炸（写入端攒批+OPTIMIZE）；technical_indicator 1339 parts（等 dwm 回填停→独占窗 OPTIMIZE FINAL——**与 tilib dwm 收尾是同一件，先查其状态**）；77 表未登记资产册（生成器口径重建禁手工）
- **W3 冷储主库落 F**：E:\zephyr_cold_archive→F（robocopy+文件数/字节/5% hash 对账）→**引用 7+1 处同 commit 改齐**（清单在包④§2：archiver.py:69,732/asset_inventory/infrastructure_registry/registry_of_logs:808/services_registry:118-120/backup_config:88-89/data_retention_contract 核对）→dashboard 探针绿→E 侧留观 30 天
- **W4 F↔G 调换**：首查 /mnt/chbackup_local 物理身份（疑似 F:\ch_backup 映射——**核实前禁动 F 盘任何搬运**）→暂停 backup.ps1→vhdx 526G/db_dumps/offrepo 大镜像 F→G 对账→backup_config 更新→恢复实跑
- **W5 宿主清偿**：.runtime 45G 走 classify_workspace_wip；models/ 14.3G 先 rg 引用再处置；tmp_db_dumps 轮转；研报对账（E 侧删除挂 ≥2026-10-18）；验收=D 剩余≥60G
- **W6 vhdx 压缩（Owner 在场窗）**：F 新鲜备份前置→停 VM→Optimize-VHD Full→起 VM→全链健康探针→季度巡检自动化登记；验收=vhdx≤450G+内部≥150G
- **W7 终验红蓝**：五盘对照表+引用残留 rg 扫+搬运抽 hash 复测+备份恢复演练两次（G vhdx 分区+F parquet 分区）→交付报告

## §4 硬约束与坑（CH 26.6.1 实测）
- D 盘仅 28G（97% 满）——一切回填/备份/导出**前**先出清理方案；重 IO 只在 02:00-05:00 独占窗，互斥排程；CH 内存 7.15GiB 上限
- >50G 表 TRUNCATE 被 max_table_size_to_drop 保险丝拦：同 ?session_id 两连发（SET→SELECT 验证→TRUNCATE），禁全局关保险丝；zephyr_writer 无 TRUNCATE system.* 权限（RBAC 勿改），系统表用 default 超户
- CH 26.6：CREATE TABLE ORDER BY 多键必须元组 ORDER BY (a,b)；无 multiquery 参数；TSV 分区串 \' 转义先 strip
- 凭据唯一真源 config/.env.clickhouse；CH DDL 后必 system.columns 探针
- 长批任务必被 SIGTERM（实测 7 杀）：分片+每片独立 json+增量落盘+幂等 resume
- storage_tiering.py 纸面模块（CONSUMERS=scheduler 零引用）：本线开工首日内收裁定（接线进本方案滚动归档 reconciler 或退役 salvage），登记裁定号

## §5 验收与回执
每波=验收数字（见 a0 总令各 W 节）+前后对照（R1 基线）+红蓝抽验；回执六要素；自查两轮 0+终局红蓝一轮（W7 即全战役终局凭证）。

## §6 共享纪律
同甲线 §6 浓缩段（00_master_plan §8）+数据第一公理+禁 cron（事件触发，backup 成功事件链=合法先例）+搬运三步（robocopy→对账→引用改齐同 commit）。
