---
ttl: task_bound
title: "F08 冷库归档运维——F:/zephyr_cold Parquet 五重安全阀复飞案卷"
session: zc-l01-20260927
---

# F08 冷库归档运维（复飞案卷）

> 前序：M1 册 04_cold_storage.md 挖干+补挖波 09_f08_cold_storage_confirm.md（built 确认+三事收敛）；本卷=复核引用+勘误传递。

## 一、六向台账（引用 04/09 册，本日无翻案）

| 向 | 内容与实证 |
|---|---|
| 上游 | CH c1_market 老分区（archiver list 实测 2515 分区全"已验证+已删除"，最新批 2026-09-24 02:07 kline_etf_30min）+库外语料（altdata/研报/C4 PDF 缓存迁入） |
| 下游 | 长周期回测供料实证（drawers.jsonl 第 10 行 etf_lof_minute_history_20260924 5.47GB，2005 起历史段=回灌原料）；restore_partition 回灌（archiver.py:793） |
| 自动触发 | 归档=手动/事件 CLI（无常驻，宪法 §9.3 合规）；备份族三计划任务 Ready（本日 schtasks 复核：DailyBackup/WeeklyVMBackup/ZEPHYR-RESTORE-DRILL 全 Ready） |
| 真源注册表 | INFRA-STORE-003（infrastructure_registry）；手册=storage_map.md；manifest=F:/zephyr_cold/00_manifest/drawers.jsonl（09 册记 10 行 append-only）；保留合同=data_retention_contract.yaml；lifecycle 字段在 business_data_categories.yaml :27/:49 |
| 门禁质量尺 | 五重安全阀 v1.3.0：export→verify（件数+字节+5% 抽样 hash）→drop；数据第一公理（两副本/7 天留观/30 天冷储/immutable）；RULE-DATA-OPS 三步验证 |
| 运行状态 | **绿（built 确认成立，09 册收敛）**：机械活（2515 分区）+登记活（manifest 增长）+对账活（09-24 迁入注记带 sha256 对账） |

## 二、子模块三级枚举

1. 归档核：scripts/ch/archiver.py（920 行：archive-range/list/stats/restore/export-only；export :191/verify :383/drop :435 dry_run/restore :793）
2. 对账：rolling_archive_reconciler.py（备份成功钩子+shadow 只读禁 drop）；注意 09 册增补：G 侧保留窗内对账范围应只对 F（现无配置区分）
3. 抽屉体系：00_manifest/drawers.jsonl+20_raw(A-J)/30_corpus/50_archive(by_project 6 项)/40_migration
4. 相邻新环（L00 D-02）：**F127 data_eng（P1）**含 cold_data_archive_manager 等 16 py，与 F08 冷储交叠=姊妹定版卷自标勘误点。本卷登记：交叠判据待裁（同物性验证），F08 现役件（archiver 族）不受影响。

## 三、接线四态独立复核

- 总册：built（待深挖确认）/P2/D8。独立复核：**"待确认"已由 09 册全部收敛**——勘误⑪：总册 F08 状态列应升级为 `built（已确认，2026-09-25 补挖波）`（09 册 §六建议，本卷复核认可传递）。
- 勘误⑫（04 册 S1 判定反转传递）：drawers.jsonl G: 路径行=迁移前化石（append-only 不可改），04 册原修法"修正 manifest 行"撤销，改检索注。
- 勘误⑬：SOP §12 冷库盘符写 G:（3.7T）+末段路径 0xC2 0x81 转义损坏——与 F02 O5 同批修册，本日复核未修（仍在）。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| S1 | 归档触发自动化缺位（手动 CLI） | 施工：RETENTION lifecycle 表驱动月班候选单（dry_run 递 Owner），export/drop 仍 Owner 门 | P2 |
| S2 | G 侧只读保留窗 2026-10-21 到期处置 | 挂起+解锁=日历到期（04 册 S5 遗留清单） | P2 |
| S3 | by_project 快速膨胀无 TTL | 提请：RETENTION 契约补层（09 册 S8） | P2 |
| S4 | storage_tiering.py 已裁退役（裁定#383）未物理摘除 | 施工：按 WO 批次摘除+depgraph 重建 | P2 |
| S5 | SOP §12 盘符+损坏路径修册 | 施工（并入 F02 O5 同批） | P2 |

## 五、自审闸三态

挖干可施工（04/09 册双册+本卷无翻案复核）；S1/S4/S5 可施工；S2 挂起日历；S3 提请。总册判定沿用处已注明（built 确认传递）。

## 六、复跑命令

```bash
ls F:/zephyr_cold/ F:/zephyr_cold/00_manifest/ F:/zephyr_cold/50_archive/by_project/ 2>/dev/null
wc -l F:/zephyr_cold/00_manifest/drawers.jsonl
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python scripts/ch/archiver.py list | tail -3        # 最新归档批（只读）
grep -n "已退役" src/zephyr/data/storage_tiering.py  # 裁定#383
sed -n '7,10p' scripts/ch/archiver.py               # 三阶段头注
```
