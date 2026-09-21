---
ttl: task_bound
status: active
title: "Offsite 异地副本月度手册（Owner 第三块盘离场制）"
owner: ZephyrAlpha-Owner
created: "2026-09-21"
session: st-disk-ch-20260921
issue: OFFSITE-MANUAL-A3-6.6
promote_note: 长期运营手册——内容随 a3 阶段5 完成后晋升永久区（docs/01_policies_and_standards/sop/）或并入 backup_config 文档面
---

# Offsite 异地副本月度手册（裁定#380⑥ Owner 自办制的操作载体）

> 架构定案（a3，Owner 2026-09-21 拍板）：D=生产；F=冷储专项（纯冷库）；G=备份总仓（一套完整备份）；
> **offsite=Owner 手动月度拿第三块盘离场**。本组合=标准 3-2-1（3 副本 D+G+离场 / 2 介质 / 1 离场）。
> G 留家值班不拔走；第三块盘专做离场副本。

## 1. 你需要的东西

- 第三块盘（**建议采购**，容量 ≥2T，USB 3.0 以上；G 是 4T，离场副本只需覆盖"一套完整备份"+冷库镜像，2T 够用）
- 拷贝用的电脑 = 本机（本手册全部命令可直接粘贴）

## 2. 月度流程（每月一次，建议月初第一个周末，约半天）

### 第 1 步：把第三块盘插到本机，确认盘符（假设是 H:）

```
以文件管理器或 diskpart 确认盘符，下文用 H: 代替；若盘符不同请替换。
```

### 第 2 步：拷贝"一套完整备份"（G:\backup → H:\backup）

```
robocopy G:\backup H:\backup /E /COPY:DAT /MT:8 /R:2 /W:5 /NFL /NDL /NP
```

内容=working_vault 代码快照 + db_dumps 数据库快照 + git_bundles 全史 + offrepo 关键资产镜像。
首次全量（约 60-190G，视 working_vault 当月体积）；之后每月增量，通常 10-30 分钟。

### 第 3 步：拷贝冷库镜像（G:\zephyr_cold\60_mirror → H:\cold_mirror）

```
robocopy G:\zephyr_cold\60_mirror H:\cold_mirror /E /COPY:DAT /MT:8 /R:2 /W:5 /NFL /NDL /NP
```

冷库 Parquet 主镜像（百 G 级）；月度增量同样只拷新分区，分钟级。

### 第 4 步（可选但建议）：带走前抽验 3 个文件

从 H 盘任意抽 3 个文件（一个 .bundle、一个 db_dumps 里的文件、一个冷库 parquet），
和 G 盘对应文件比一下大小一致即可（严格校验用 certutil -hashfile 比 SHA256）。

### 第 5 步：拿离场

第三块盘拔下，放到**离家地点**（办公室/亲人家/银行保险箱任一）。
防的是：火灾/水淹/进贼/勒索软件同时毁掉 D+F+G 的极端情况。

### 第 6 步：回来登记（下次插盘前）

在本目录 `offsite_rotation_log.md` 追加一行：
`YYYY-MM-DD ｜ 拷贝完成 ｜ 盘容量剩余 xxG ｜ 上次离场地点 ｜ 备注`
（首次使用时创建该文件，格式照抄本行。）

## 3. 红线与注意

1. **G 盘永远不拔走**——它是家里值班的全量备份，拔走期间家里只剩单链。
2. 第三块盘**只读为主**：每月被 robocopy 更新，平时锁抽屉，不接日常电脑。
3. 拷贝当月如果 backup.ps1 有失败告警（晨报/仪表盘红），先修备份再拷离场——离场垃圾进=离场垃圾出。
4. 第三块盘离场期间本机任何操作都不影响它；它就是"上个月的快照"，这是设计特性不是过期。
5. 若第三块盘未采购：本手册先挂起，G 单链+D/F 双链维持现状（2-1-1，缺离场腿），采购后从第 1 步起用。

## 4. 什么情况下该立刻多跑一次（加演）

- 大版本发布/大迁移落地当周（如备份总仓刚迁 G）
- 听闻本地极端天气预警前
- G 盘报过 SMART 告警或拷贝报错后（用加演验证 G 本体是否还可靠）
