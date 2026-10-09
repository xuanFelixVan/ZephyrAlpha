---
ttl: task_bound
completes_when: VM 压缩窗后核验步骤执行并回填结果（预期 BOTH_ABSENT 即本件闭环；复活则按 §3 处方呈 Owner）
title: E6 VM /root 两件残留评估卡（只评估绝不执行）
session: st-nightsweep2-nf2-20260930
---

# E6 · VM /root 两件残留评估卡

> 车道=第二夜总攻 W2-NF2 F 组补完（总筹 st-nightsweep-chief-20260929）。Owner 2026-09-30 裁定：**E6 只评估绝不执行**（ND_ledger 卡面同口径）。
> 证据真源=ND 车道 E6 卡（`.runtime/tmp/st-nightsweep-20260929/ND_ledger.yaml` §E6_VM_root两件残留，verdict=EVALUATED 已核销态），本件=其评估卡文件化转登（token 先行），零 VM 操作、零 SSH、零重启。

## 1. 两件残留（案源=st-metaq-gc-20260924 交接；93 册 F 案卷 X-45 / 95 册 §九 B）

| # | 路径（VM /root） | 体量 | 性质 |
|---|---|---|---|
| 1 | `/root/macro_data_broken_parts_bak_20260925` | 760K（188 个 0 字节空壳目录） | macro_data gc 施工残留 |
| 2 | `/root/macro_data.sql.bak_metaqgc_20260925` | 4.0K | 表结构元数据备份 |

## 2. 现状判定（以晚测为准）

- **09-27 01:3x-02:0x 实测**：`scripts/backup/ch_vm_ssh.py` 通道 CHANNEL_OK + **BOTH_ABSENT=两件已不在盘**，95 册已记核销（卡面前提过期）。
- **矛盾调解**：X-45 时点（更早）在盘 vs 95 册（更晚）BOTH_ABSENT——**以晚测为准=已删**；本卡评估结论=**无需删除动作**，只剩压缩窗后复核义务。

## 3. 压缩窗后核验步骤（待 VM 可达窗执行；禁今夜执行）

```bash
python scripts/backup/ch_vm_ssh.py --cmd "sudo -n ls -d /root/macro_data_broken_parts_bak_20260925 /root/macro_data.sql.bak_metaqgc_20260925"
```

- **预期**=`BOTH_ABSENT`（保持已删态）→ 本件闭环，回填本行即结。
- **若镜像恢复旧态复活**：删除命令=同通道 `sudo -n rm -rf /root/macro_data_broken_parts_bak_20260925 /root/macro_data.sql.bak_metaqgc_20260925`；**执行前置**=先复核 CH 数据完整性（销证权在 Owner 口径，dossier_F §89），且 rm 属 VM 内变更须 Owner 门位放行后再动手。 <!-- [GATE-SELFDOC:SHELL-DANGEROUS] 案卷引文（VM 复活预案转录），非操作指令；宪法 GATE-SELFDOC 行级标，shell 门 2026-10-09 平权腿 -->

## 4. 风险清单

1. **误删风险=低**（两件均为施工残留/元数据备份，非生产数据面；188 空壳目录零内容）。
2. **销证风险**：rm 前未复核 CH 完整性=销证权越权（Owner 口径 dossier_F §89）——故 §3 复活分支强制 Owner 门位前置。
3. **通道风险**：ch_vm_ssh.py 依赖 VM SSH 可达；压缩窗内禁 SSH（本卡全程遵守，零连接）。
4. **假绿风险**：`ls -d` 对不存在路径返回非零+stderr，判读须以 BOTH_ABSENT 字面回执为准，禁凭 exit code 单判。

## 5. 台账

- 评估结论：**EVALUATED（已核销态，压缩窗后复核义务在账）**。
- 本卡登记：st-nightsweep2-nf2-20260930，2026-09-30；token=night_sweep 前缀精确单文件通道（capability_canonical_file_registry 同批）。
