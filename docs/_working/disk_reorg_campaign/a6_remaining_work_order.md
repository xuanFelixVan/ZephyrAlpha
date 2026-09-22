---
ttl: task_bound
---

# 【续班令】磁盘重整+冷储备份自动化——剩余工作清单（2026-09-22 交接定稿）
# sid 建议：st-diskreorg-close-20260922 ｜ 落盘：docs/_working/disk_reorg_campaign/ ｜ 接手=对账续做，禁重复施工
# 前序会话：st-disk-ch-20260921（施工主力，a5 终局报告）+ st-disk-final-20260922（#399 废表终局，commit 345516da8c0）+ st-diskreorg-knowledge-20260922（知识固化 3/4）

## §0 项目背景（60 秒版）

ZephyrAlpha=Owner 个人量化交易系统，100% AI 开发，仓库 D:\ZephyrAlpha，宪法 AGENTS.md 全程有效。Windows 宿主+HyperV 虚拟机 zephyr-ch 跑 ClickHouse 26.6.1。**四盘分工（Owner 定案，地图=infrastructure_registry INFRA-STORE-003）**：D=NVMe 生产（项目仓+CH 虚拟机 data.vhdx 热层）；E=SATA SSD 软件+热数据；F=USB-SSD **冷储专项**（纯冷库，主库=F:/zephyr_cold）；G=USB-HDD **备份总仓**（G:/backup 一套完整备份+CH 第二备份链 ch_backup_disk2.vhdx+F 冷储夜镜像）；offsite=Owner 月度手动第三块盘（3-2-1 达标）。**数据第一公理：任何删除前两份验证副本+行数 verify；源目录最后删且留观 7-30 天。**

## §1 已完成（勿重做，证据在 a1/a3/a5）

- 勘察+方案 v2+总令+施工清单+开工令全套（a0-a4）；Owner 六项签字全落（2026-09-21）
- CH 系统日志 145G 清偿（09-19）+ TTL 永久化（information+7/14 天，24h 复测 1.2G/天 ✓）
- 冷储主库落 F：E 117.6G+G 抽屉库 95,188 件对账 PASS；引用 7+1 处改齐（commit 6684ba5d83）
- 尸体表 17/17 已 DROP（裁定 #399，st-disk-final，释放 32.96GiB，亲验库内全清）
- 滚动归档自动化上线：契约 v1.3.0+rolling_archive_reconciler.py 挂 STAGE 4b（三档实弹+红蓝三注入全绿）
- 备份总仓落 G：working_vault 1,156,584 件种子对账 PASS/db_dumps 14 天版本化/git_bundles/offrepo/STAGE 3d 冷储夜镜像；CH 双链热挂零停机（F 主链 526G+G 第二链 452G，inc 71G+base 266.6G 双链基线齐）
- 宿主清偿 D=58-61G；offsite 手册落档；恢复演练三次+对账复验全 PASS
- 知识固化 3/4：INFRA-STORE-003 地图条目已立（YAML 验证绿）/MOD-INF-043 蓝图 v3.0.0/宪法 §7 存储分工行（等长替换 140 行不变）

## §2 剩余任务清单（本令=全部待办；按触发排序）

### A. 知识固化收尾（阶段 9-④，随时可做）
capability_canonical_file_registry 登记关键词（冷库/冷储/备份/backup/四盘/storage→INFRA-STORE-003）+ROOR 挂接+permanent 手册提炼（a3 安全通则+保留清除清单 17 行挂 MOD-INF-043 域）+图书馆办卡。**注意：capability 册 tilib 队在飞竞写——token 同批走、撞锁等 5 分钟。**

### B. 2026-09-28 到期：F:\working_vault 旧副本删除（200.7G）
先复核 G:\backup\working_vault 对账记录（a3 4.2 PASS 在案）→ 删 F 旧副本（F 回收 200G）。

### C. 2026-10-05 触发：阶段 5（双写稳定 14 天期满）
①ch_backup_disk.vhdx（F 主链）退役评估——G 第二链连续 14 天增量完整即可摘盘（停 VM→SCSI 摘除→G 归档或删，F 回收 526G）；②ch_vm_backup B 瘦身（F 原件 591.57G→配置级轻备份）；③**G 三份 ch_vm_backup 去重（增补 4.9）**：G:\backup\、G:\zephyr_backup_mirror\、G:\zephyr_cold\ 下三份 591.57G 等值副本，三方 hash 确认后删冗余（预期 G 剩余 342G→2100G+，9.2% 红线解除）；④F:\offrepo_backup 旧镜像 136.6G+F:\db_dumps 0.36G 旧件核等清理；⑤G:\zephyr_cold\zephyr_cold 嵌套 274.49G 对照 manifest 解析归位。

### D. 日历删除（三笔，到期即执行）
10-18 研报 E 侧删（84.7G，对账已核 29,998=29,998）；10-20 E:\zephyr_cold_archive 留观删（117.6G）；10-21 G:\zephyr_cold 原抽屉库删（只读留观期满）。

### E. 阶段 7 vhdx 压缩（等 Owner 点名窗，唯一到场项）
预检单在盘（vhdx_precheck_20260921.md）+剧本=vhdx_quarterly_notice_design.md。流程：停 VM→管理员 Optimize-VHD -Path D:\HyperV\VMs\zephyr-ch\data.vhdx -Mode Full→起 VM→健康探针→验收 vhdx≤450G+D 显著回升（当前 D=57.9G，压缩后预期 200G+）。季度巡检已挂 STAGE 4b 自动提醒。

### F. 阶段 8 终验收尾（C/E 完成后）
8.1 五盘容量前后对照表+CH 热层体量对账；8.3 搬运抽 hash 复测（每类 10 件）；8.5 红蓝一轮；8.6 临时件清+GitCommitGateway 全落地+终局交付报告。

### G. 观察项（下次巡检核，非本令必做）
①CH system.disks 里 backups2 盘显示 0/0（双链实测可用 fetch_perf 103 行，复核显示异常即可）②E 盘被他会话回吃（a5 班后 252G→现 60.9G，查明写入方）③TI 自动归档解锁=等甲线 C-5/批10 回落公告 ④models/15G 迁移=等 ml 线路径批 ⑤PG dump exit 1=已移交备份维护批 ⑥G:\backup\offrepo 273.62G 比迁移前 137G 翻倍（疑合法增长含 cold_archive 新家，核一次）⑦G:\zephyr_cold\zephyr_cold 嵌套 274.49G 解析（并入 C-⑤）

### H. 暂存批落地（开工第一批）
本线 4 文件已暂存未 commit（Owner 签字内容在内）：AGENTS.md（宪法存储分工行，**Max/Owner 复验**）/blueprint.md v3.0.0/infrastructure_registry.yaml（INFRA-STORE-003）/a4_go_signal.md。命令：`python scripts/git_commit.py --session <sid> --files AGENTS.md,docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md,docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml,docs/_working/disk_reorg_campaign/a4_go_signal.md --enqueue`。注意宪法改动挂【M：Max/Owner 复验】标记。

## §3 待裁定/待复验状态

1. 宪法存储分工行=待 Max/Owner 复验（唯一门位项）；2. offrepo 翻倍核结果若异常再报；3. **无其他待裁定**——六项签字已全落，废表已经 #399 消化。

## §4 真源读序（接手 60 分钟）

1. docs/_working/disk_reorg_campaign/a3_safe_construction_checklist.md（执行本体+勾选状态）
2. docs/_working/disk_reorg_campaign/a5_delivery_report.md（前序终局报告+9 条等待项）
3. docs/_working/disk_reorg_campaign/a1_ledger.md（过程台账）
4. docs/_working/disk_reorg_campaign/a4_go_signal.md（开工令+增补 4.9 去重批/清理项/阶段 9）
5. docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml INFRA-STORE-002/003（存储地图）
6. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml（v1.3.0 保留规则）
7. scripts/backup/{backup_config.yaml,backup.ps1,backup_reconciler.py,restore.ps1,backup_ch_vm.ps1}+scripts/ch/{archiver.py,rolling_archive_reconciler.py,waste_table_scanner.py}
8. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md（冷库三红线）
9. docs/_working/dataqa_audit_20260920/ 四报告（R1 基线）

## §5 硬事实（2026-09-19/22 实测；执行日重跑探针刷新）

五盘（09-22）：C 59/D 57.9/E 60.9/F 186/G 342.2 free。CH VM default 盘空闲 153.9G；业务活跃 406.7G=热层（tick 141.8+TI 184.9+分钟线族+小表）——TI 184.9G 含待甲线回落排除段；系统日志 6.81G（TTL 生效）。CH 凭据=config/.env.clickhouse（default 超户操作系统表；>50G TRUNCATE 保险丝 session 两连发；无 multiquery；TSV 转义 strip 反斜杠）。冷储：F:\zephyr_cold 主库（研报 90,243+Parquet 2,213 条 manifest）+G:\zephyr_cold\60_mirror 夜镜像+G 原库留观至 10-21。文本坑：Git Bash 无 pgrep/heredoc 吞字符多行 python 落文件再跑；CH TSV 元组分区带 \' 转义。

## §6 纪律

提交唯一正门 scripts/git_commit.py --enqueue --files 白名单；改前 claim（TTL 30 分钟）毕后 release；热文件 safe_write_text+CAS 写后进程外核实；.md 带 ttl 字母开头 snake_case；新件 CREATE-GUARD token 同批；禁 git add -A/.；禁 cron（事件触发，STAGE 4b 先例）；数据库操作走 DatabaseService/archiver 通道；长批 session keeper（.runtime/tmp/diskch/session_keeper.py 模式）。避让：三队目录+capability 册（tilib 竞写）+ruling_registry/gate_registry/tasks.yaml/AGENTS.md 本体之外的宪法改动需【M】+data/strategy_intake/**/data/crypto/**/docs/03_modules/**（蓝图更新除外，本令已授权）。
回执六要素+证据等级[亲验]/[转报]/[推断]；每阶段自审连续两轮 0 问题；禁虚报。

## §7 断点续班

进度全落 a1_ledger.md；本令+a1 即可接手。全部完成后：终局交付报告（终极目标逐条对账+五盘容量前后对照表+等待项归零表）+本目录随战役归档（a3/a4/a5/a6 按归档门禁办卡）。
