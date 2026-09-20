---
ttl: task_bound
completes_when: 本线终验红蓝通过+五盘对照表全绿
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-V1-LINE-B
---

# 【总包乙·磁盘与 CH 线】施工指令 v1.0（自包含，新对话整贴即用）

# sid：st-disk-ch-20260921 ｜ 落盘：docs/_working/disk_reorg_campaign/（沿用，a0 总令已在此）｜ 模型：Max 总包+Flash 分包（WO-5..11 领单）
# 上位方案：docs/_working/unified_campaign/00_master_plan_v1_0.md（§4 三档时序制+冲突矩阵=本线强制协议）；台账/处方/派工单同目录

## §0 使命
CH 瘦身到位+日志滚动永久自动化+冷储主库迁 F+G 镜像+备份 3-2-1+宿主清偿+vhdx 季度压缩机制化。终态=五盘对照表全绿+热层约 360G 稳态+全自动无人值守+dashboard 冷储检测绿+恢复演练通过。**数据安全第一公理：任何删除前必须有两份验证过的副本；drop 前必须行数 verify。**

## §1 冷启动
同甲线配方（PATH 3.12/lock cleanup/reaper/session 注册+心跳）。加：开工日**重跑探针刷新台账**（盘位/CH 内部/system.parts 水位/D 盘 df）——本指令数字为 2026-09-19/20 实测（D 盘 29G/97% 满、CH 内部空闲约 151G、TI 1181 parts 漂移中），执行日禁凭记忆。**开工首件=storage_tiering.py 纸面模块内收裁定**（CONSUMERS=scheduler 零引用——接线进滚动归档 reconciler 或退役 salvage，登记裁定号，宪法 §4 四判据）。

## §2 真源读序
1. docs/_working/cold_backup_automation/00_master_plan.md（自动化方案 13 章——本线母方案）
2. docs/_working/disk_reorg_campaign/a0_master_order.md（收口六波总令 W1-W7 全文——**本指令即其执行令，含验收数字与避让清单，照执**）
3. docs/_working/cold_backup_automation/01_mining_findings.md（挖矿 9 缺口+8 意外）
4. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml（保留契约真源）
5. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md（冷库 SOP 三红线）
6. dataqa R1（docs/_working/dataqa_audit/ch_health_report.md）作 W1 前后对照基线；A10/A12/A13/A14 细节同四报告
7. **CH 实况自查**：system.parts/error_log 近 24h/D 盘 df/夜跑 log（C-5 修复前 TI OPTIMIZE 勿动）/t_timing_window_board.md 声明窗

## §3 三档时序制（裁定#378③——本线核心协议，全文=00_master_plan_v1_0 §4）
- **闪断**（W2 重启）：任意低峰整点窗；避开 00:00-05:00 计划任务带（02:30 夜跑等逐个 schtasks 实查）与甲在途批；声明板登记 ≥30 分钟。
- **独占窗 02:00-05:00**（W1/W-并入/欠账 archive-range/TI OPTIMIZE）：重 IO 互斥排队（声明板登记序）；**W1 前置于甲一切大规模回填**（D 盘硬闸协议）；TI OPTIMIZE 与甲批10 回填同表互斥，且前置=C-5 夜跑修复健康。
- **全局冻结**（W6 vhdx）：停 VM 甲丙全停（SessionRegistry 空+甲挂起确认）；Owner 在场窗。
- 声明板=docs/_working/unified_campaign/t_timing_window_board.md；乙线是主要声明方，甲线 >30min 批次禁横跨 active 窗。

## §4 波次（=a0 总令 W1-W7+并入项，按依赖与三档排序）
- **W2 日志滚动永久化（最急，无需签字可先行，WO-5）**：text_log level 调低+system log 表原生 TTL（trace/query_log 7 天、余 14 天）+max_size 轮转→闪断窗重启→24h 复测膨胀<1G/天（151G 余量 2-3 个月窗）
- **W1 CH 库内清偿（签字①批后·独占窗·Owner 在场，WO-6）**：尸体表（=A11，张数 12vs17 执行日实测仲裁）逐表 export Parquet 双副本（F+G）→行数 verify→凭批文 drop；欠账 24.9G 走 archiver archive-range；验收=内部空闲≥200G+尸体清零
- **W-并入（签字②批后同窗，WO-6）**：1970 十八表 PIT 关死/补真值；12 小表 OPTIMIZE FINAL；TI 1339→1181 parts（等 C-5 修复+parts 回落→独占窗 OPTIMIZE FINAL，与批10 互斥排队）；77 表资产册重建归丙 WO-13
- **W3 冷储主库落 F（WO-7）**：E:\zephyr_cold_archive→F（robocopy+文件数/字节/5% hash 对账）→引用 7+1 处同 commit 改齐（archiver.py:69,732/asset_inventory:139/infrastructure_registry:200-203/registry_of_logs:808/services_registry:118-120/backup_config:88-89/data_retention_contract 核对）→dashboard 探针绿→E 侧留观 30 天；G:\zephyr_cold 整体迁 F 同配方
- **W4 F↔G 调换（WO-8）**：首查 /mnt/chbackup_local 物理身份（**核实前禁动 F 盘任何搬运**）→声明板登记暂停 backup.ps1→vhdx 526G/db_dumps/offrepo 大镜像 F→G 对账→backup_config 更新→恢复实跑
- **W5 宿主清偿（WO-9，两段拆跑）**：段一=签字后任意低峰（.runtime 45G 走 classify_workspace_wip 流程禁肉眼判罚；models/ 14.3G 先 rg 引用；tmp_db_dumps 轮转；小目录三层验证）；段二=研报 E 侧删挂 ≥2026-10-18；验收=D 剩余≥60G
- **W6 vhdx 压缩（Owner 在场·全局冻结，WO-10）**：F 新鲜备份前置→停 VM→Optimize-VHD Full→起 VM→全链健康探针→季度巡检自动化登记；验收=vhdx≤450G+内部≥150G
- **W7 终验红蓝（WO-11，全战役终局凭证）**：五盘对照表+引用残留 rg 扫+搬运抽 hash 复测+备份恢复演练两次（G vhdx 分区+F parquet 分区）→交付报告

## §5 硬约束与坑（CH 26.6.1 实测）
D 盘 29G（97%）——一切回填/备份/导出前先出清理方案，导出全走 F+G 禁落 D；CH 内存 7.15GiB 上限；>50G 表 TRUNCATE 保险丝=?session_id 两连发（SET→SELECT 验证→TRUNCATE），禁全局关；zephyr_writer 无 TRUNCATE system.* 权限（RBAC 勿改），系统表用 default 超户；CH 26.6 CREATE TABLE ORDER BY 多键必须元组 (a,b)；无 multiquery；TSV 分区串 \' 转义先 strip；凭据唯一真源 config/.env.clickhouse；CH DDL 后必 system.columns 探针；长批任务必被 SIGTERM（七杀实测）：分片+每片独立 json+增量落盘+幂等 resume；禁 cron（事件触发，backup 成功事件链=合法先例）。

## §6 验收与回执
每波=验收数字（a0 总令各 W 节）+前后对照（R1 基线）+红蓝抽验；回执六要素；自查两轮 0+终局红蓝一轮（W7=全战役终局凭证）。

## §7 共享纪律
同甲线 §6 浓缩段（00_master_plan_v1_0 §10 全文适用）+数据第一公理+搬运三步（robocopy→对账→引用改齐同 commit）。
