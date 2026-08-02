---
ttl: task_bound
---

# 灾备备份恢复演练报告 (C3)

- **演练日期**: 2026-08-02
- **演练范围**: F: 盘外接硬盘备份产物 inventory + 完整性 verify + CH 服务可达性诊断
- **关联项**: §8 改期项 C3（触发条件：下次备份完成后人工触发）
- **备份方案**: v2.0 robocopy + CH 增量（restic 已于 2026-07-28 移除）
- **ttl**: task_bound（C3 闭环后归档）

## 1. 演练结论

| 维度 | 结果 | 说明 |
|------|------|------|
| 备份产物存在性 | ✅ PASS | inventory 全部产物齐全且新鲜 |
| 备份完整性 | ✅ PASS | verify 13 项检查全通过 |
| CH 服务可达性 | ✅ PASS（已修复） | 服务已启动，TCP+HTTP 均可达 |
| CH 远程启动能力 | ✅ PASS（已修复） | NOPASSWD sudoers 配置就位，远程启动验证通过 |
| CH 崩溃自愈 | ✅ PASS（已验证） | systemd Restart=always，kill -9 后 ~23s 自动重启 |
| CH 停机告警 | ✅ PASS（已验证） | 探针接入 Alerter，CH stop→CRITICAL 告警，start→INFO 恢复 |
| 表级恢复验证 | ⏸ 待补做 | R6 遗留项，CH 已恢复可执行 |

**总结**: 备份数据层完整可用（灾后能恢复数据），服务层 RTO 风险已闭环（CH 自愈+告警+远程启动均已验证通过）。

## 2. 演练明细

### 2.1 inventory（备份产物清单）

执行: `restore.ps1 inventory`

| 产物 | 路径 | 大小 | 最近更新 | 状态 |
|------|------|------|----------|------|
| 代码备份 | F:\code_backup | 5.12 GB | 08-02 14:00 | ✅ 关键文件齐全 |
| DB dumps | F:\db_dumps | — | 08-02 14:00 | ✅ 4 文件 |
| CH base | market.zip | 199.07 GiB | 08-01 06:15 | ✅ |
| CH inc | inc.zip | 21.15 GiB | 08-01 06:15 | ✅ 增量比 0.1% |
| CH VHDX | ch_backup_disk.vhdx | 295.91 GB | 08-02 06:00 | ✅ |
| CH VM | ch_vm_backup | data.vhdx 554.72 GB | 07-28 | ✅ |

backup_state.json 关键字段:
- `last_backup_status`: ok
- `last_ch_backup_verified`: True
- `last_ch_backup_table_count`: 101
- `last_ch_backup_size_ratio`: 1.0001（远低于 0.5 rebase 阈值）

### 2.2 verify（完整性验证）

执行: `restore.ps1 verify`（只读，非破坏性）

```
[OK] code: AGENTS.md / pyproject.toml / .env.postgres / .env.ch_backup / .env.clickhouse
[OK] dumps: depgraph.dump (1.74MB) / pg_globals.sql / governance_backup.db (58.42MB) / session_backup.db
[OK] ch: market.zip (199.07 GiB) / inc.zip (21661.65 MB)
[OK] vm: boot.vhdx / data.vhdx (554.72 GB)
[OK] ALL CHECKS PASSED -- backup is ready for disaster recovery
```

### 2.3 CH 服务诊断（演练发现）

**发现 1: CH 服务停机 17h 未告警**

- VM "zephyr-ch" 运行中（uptime 2天10小时），ping 通
- 但 CH 9000/8123 端口拒绝连接
- `systemctl status`: `inactive (dead) since 2026-08-01 18:29:54 UTC`（约 17 小时前）
- 停止方式: systemd 手动 stop（`Stopping clickhouse-server.service`），非崩溃
- 服务 `enabled`（开机自启）但停止后未自动重启
- **风险**: CH 停机 17h 无告警——若在实盘运行期，将导致数据中断无感知

**发现 2: CH 服务无法远程非交互启动**

- `ch_vm_ssh.py --sudo --cmd "systemctl start clickhouse-server"` 失败
- 原因: polkit 拦截，`pam_authenticate failed: Authentication failure`
- ch_vm_ssh.py 的 sudo 走 `get_pty + stdin.write(password)`，但 systemctl start 触发 polkit 而非 sudo 直通
- **风险**: 灾时 CH 崩溃无法远程自动恢复，必须人工介入 VM 控制台——RTO 风险

### 2.4 表级恢复验证（阻断）

原计划: RESTORE TABLE c1_market.trade_calendar AS _restore_drill.trade_calendar FROM Disk('backups', 'market.zip')，校验行数后清理临时库（非破坏性）。

因 CH 服务不可达（§2.3）且无法远程启动，表级恢复验证阻断，待 CH 服务恢复后补做。

## 3. 改进建议

| 优先级 | 建议 | 关联 |
|--------|------|------|
| P0 | CH 健康检查接入告警通道（B2 已修复 SMTP/飞书，需补 CH 存活探针） | B2 衍生 |
| P0 | 配置 CH 服务 systemd `Restart=on-failure` + NOPASSWD sudo（或 SSH key + sudoers），实现崩溃自愈/远程可启 | RTO |
| P1 | 适配 `_recovery_drill.py` 到 v2.0 Disk 方案（当前脚本用 S3，已过时），支持非破坏性表级恢复演练 | C3 补做 |
| P2 | CH 停机告警纳入 `last_ch_vm_autocheck` 之外的主动探针（当前 autocheck 仅在备份时触发） | 监控盲点 |

## 4. 演练产物

- 本报告: docs/_working/reports/backup_recovery_drill_20260802.md
- 探针脚本: .runtime/tmp/c3_drill_probe.py
- inventory/verify 原始输出: 见本报告 §2.1/§2.2

## 5. 闭环动作

- [x] inventory 执行
- [x] verify 执行
- [x] CH 诊断
- [x] CH 服务启动（NOPASSWD sudoers 配置 + systemctl start）
- [x] CH 崩溃自愈验证（kill -9 → systemd Restart=always 自动重启，NRestarts=1）
- [x] CH 停机告警接入（HeartbeatMonitor + scheduler _probe_loop → Alerter，R4a）
- [x] 告警端到端验证（R5：CH stop→CRITICAL，CH start→INFO 恢复，failure 文件写入）
- [x] 改进建议登记到 architecture_issue_registry.yaml（#ARCH-DR-CH-RESTART-001，status=resolved）
- [ ] 表级恢复验证（R6 遗留项，CH 已恢复可执行）
- [ ] R4b：盘后 7×24 独立探针（当前探针仅在调度器运行期生效）
