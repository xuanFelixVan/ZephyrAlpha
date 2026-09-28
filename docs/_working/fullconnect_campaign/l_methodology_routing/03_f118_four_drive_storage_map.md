---
ttl: task_bound
title: L12 案卷 F118 — 四盘存储地图（D 生产/F 冷储/G 备份/离场 3-2-1 真源接线四态）
session: zc-l12-20260927
---

# F118 四盘存储地图（M 段横切 X3，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 磁盘重整战役 a3 定案（Owner 2026-09-21，task_bound 已过期不追——手册头注"永久知识以本手册为准"）；infrastructure_registry.yaml INFRA-STORE-003 条目（架构登记真源） |
| 下游消费 | F08 冷库（F:/zephyr_cold）与 F09 备份链（G:/backup）以本手册为"怎么用"面真源；任何"找冷库/找备份/判数据在哪块盘"任务 |
| 自动化触发 | 非运行件（文档真源）；其描述的备份/离场动作的自动化面归 F09（备份链）——M5 补挖波本日实测该链**黄**（见三） |
| 真源与注册表 | `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md`（module_id=MOD-INF-043，version 1.0.0，design_maturity=production，last_updated 2026-09-23）↔ INFRA-STORE-003（infrastructure_registry）双锚 |
| 门禁与质量尺 | 永久手册 ttl=permanent；关键词锚点（冷库/冷储/备份/backup/四盘/storage）供反查；数据第一公理铁律在册（§3） |
| 当前运行状态 | **文档面绿 / 所指系统面黄**：手册四盘分工在册；但所指备份链 09-25 实测 verdict=failed+git bundle 短路判据疑影（M5 补挖波 §3·1/§三.4，待裁 R2） |

## 二、子模块三级枚举（册族 → 盘位 → 落点）

1. 同目录四件（disaster_recovery_backup/）：`storage_map.md`（本卷主锚）+ `backup_inventory.md` + `dr_runbook.md` + `blueprint.md` + `index.md`
2. 四盘分工（storage_map.md §1 一句话版）：
   - **D=生产**：工作区+CH 热层，唯一活跃写入面
   - **F=冷储专项**（纯冷库）：`F:/zephyr_cold`——CH 老分区 Parquet 冷库+研报原文，只进不改
   - **G=备份总仓**：`G:/backup`——vault/db_dumps/git_bundles/offrepo/ch_vm_backup 五目录一套完整备份
   - **offsite=离场盘**：Owner 手动月度第三块盘离场（手册=docs/_working/disk_reorg_campaign/offsite_monthly_manual.md，≥2T 专盘建议）
3. 组合判定：**3-2-1**（3 副本 D+G+离场 / 2 介质内置+USB / 1 离场）；§2 关键词→落点速查表 + §4 遗留待办指针（截至 2026-09-23）

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| storage_map.md 手册本体 | **已接线（built）** | MOD-INF-043 production；四盘表/铁律/速查齐；与 INFRA-STORE-003 互锚 |
| M0"与 D9 同件，建议同车道"注记 | **登记事实成立** | X3 行原文；本卷不重挖 D9（备份链环节归其车道），只核真源面 |
| 所指备份链（G 盘五目录产出） | **半接线（黄）** | M5 补挖波 09-25 实测：verdict=failed+9.1h 长跑+267014 僵尸疑影；git bundle 4 天未刷=短路判据把 age 3.67 天判"fresh"（阈值语义非缺陷，→该波待裁 R4）；重跑授权=该波 R2（c→a 序，Owner 门位候选） |
| offsite 离场腿 | **登记态（人工）** | 手册明示 Owner 手动月度；无自动化诉求（3-2-1 的"1 离场"按设计即人工） |

## 骨架勘误

1. 总册 F118 行状态=built 无括注，但**其下游 F09 备份链本日为黄**（M5 补挖波降级红后部分回收）——"地图真源 built"与"地图所指系统运行黄"两态并存，F118 行宜加括注"所指备份链运行态归 F09 复核"，防全流通判定把存储面误读全绿。
2. M0 X3 行"未归属"——F118 已在总册收编为独立环节（M0 后新增段），X3 旧注记已被替代，无遗留动作。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 备份链 verdict=failed+bundle 短路判据 | 按 M5 补挖波 R2（c→a 序：先观测位后非交易日重跑）+R4（阈值语义裁定）处置；归备份车道，Owner 门位候选 | P1 |
| 2 | storage_map §4 遗留待办指针停留在 09-23 | 下次备份链施工批后顺手刷新指针节 | P2 |
| 3 | 四盘水位/容量台账（reaper watermark 面）与四盘地图无互引 | 备份车道把 watermark 读数接进 inventory 报表 | P2 |

## 五、自审闸三态

**挖干（四盘真源面）**：MOD-INF-043/INFRA-STORE-003 双锚 ✅ 四盘落点逐盘带路径 ✅；**待裁**：备份链重跑授权（R2，Owner/生产数据面）——归 F09 车道非本卷。

## 六、复跑命令

```bash
sed -n '27,50p' docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md   # 四盘表+3-2-1
grep -n "module_id\|design_maturity" docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md | head -2  # MOD-INF-043/production
grep -n "INFRA-STORE-003" docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml | head -2
# 备份链运行态（state/report json）归 F09 车道复跑，本卷不触生产数据
```
