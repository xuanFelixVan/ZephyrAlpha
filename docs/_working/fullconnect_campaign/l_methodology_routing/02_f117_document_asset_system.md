---
ttl: task_bound
title: L12 案卷 F117 — 文档资产体系（目录册/统一资产索引/规则路径目录三件物接线四态）
session: zc-l12-20260927
---

# F117 文档资产体系（M 段横切 X2，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 全仓文档/资产文件（被动盘点对象）；生成器上游=directory_registry 维护流 + generate_rule_catalog.py + 统一资产索引机生器 |
| 下游消费 | 治理面：ROOR 普查（90 普查 §三）、对齐清单、资产健康审计（health B 76.1/orphan ~3.0%）；M0 X2 行"未归属"→本环节为骨架收编对象 |
| 自动化触发 | rule_catalog_registry：maintenance=auto、generated_at=2026-09-26T18:52:06Z（generate_rule_catalog.py 机生）；unified-asset-index：generated_by 字段在册——两件为机生；directory_registry 为手工+changelog 流 |
| 真源与注册表 | `docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml`（目录册）+ `data/asset_index/unified-asset-index.yaml`（统一资产索引）+ `docs/01.../catalogs/rule_catalog_registry.yaml`（PS-REG-018 规则路径目录） |
| 门禁与质量尺 | 静态清单禁手工维护（宪法 §9.5：条目列表+计数必须生成器产出）；字段化计数（summary.*）勿写死散文（宪法 §4.4） |
| 当前运行状态 | **黄绿（built 但登记面自漂移）**：三件物全在盘且两件机生在跑；directory_registry summary 与其 directories 列表数字不一致（见勘误 1）；总册"rule_catalog 256"已过时（实测 295，见勘误 2） |

## 二、子模块三级枚举（三件物 → 结构键 → 计数字段）

1. `directory_registry.yaml`：list 键 depends_on(3)/directories(87)/drawer_maturity(20)/changelog(3)；summary 字段组=total_directories=84、by_track{C42/B38/D2/uncat2}、by_top_level{config1/docs46/scripts12/src24}、with_index=36/without_index=46、frozen=1
2. `unified-asset-index.yaml`：键 generated_at/generated_by/total_assets=33249/by_category/by_directory/modules(53)/health(B 76.1)/orphan_risk(~3.0%)/summary
3. `rule_catalog_registry.yaml`（PS-REG-018，SSoT）：total_files=295、total_rules=61、tier_distribution{L0:21,L1:29,L2:11}、files 列表 295 条；机生器=scripts/governance/d3_metadata/generate_rule_catalog.py

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| 统一资产索引 | **已接线（built）** | total_assets=33249 与总册口径一致 ✅；summary 一句话健康自洽 |
| 规则路径目录 | **已接线（机生在跑）** | 09-26 机生时间戳 fresh；total_files=295 |
| 目录册 | **半接线（summary 漂移）** | directories 列表=87 条 vs summary.total_directories=**84**；by_top_level 合计=**83**；changelog 内文"total_registered 84->85"与 summary 84 并存——一册三账 |
| M0/总册口径 | **登记面过时** | 总册 F117 行/M0 X2 行"rule_catalog 256"——该册 09-26 机生后=295，256 为挖矿时点旧读数 |

## 骨架勘误

1. **directory_registry 一册三账**：列表 87 / summary.total_directories 84 / by_top_level 合计 83（by_track 合计恰=84）。总册 F117 行写"目录册 87"取的是列表长度。建议：不手改数字，重跑其生成/校验器令 summary 与列表收敛，再以字段引用改写总册口径（宪法 §4.4 计数用字段）。
2. **"rule_catalog 256"过时**：实测 total_files=295/total_rules=61（09-26 机生）。总册与 M0 X2 行的 256 为 09-25 时点读数——机生册引旧值=骨架侧静态快照必然漂移的实例，佐证"计数用字段不写死"。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | directory_registry summary↔列表↔changelog 三账不一致 | 定位其生成/校验器重跑收敛；收敛前任何"87/84"引用注明取数口径 | P1 |
| 2 | 总册 F117/M0 X2 行静态数字（256/33249/87）必然再漂移 | 总册行改"字段引用+查询命令"形态（同宪法 §4.4） | P2 |
| 3 | unified-asset-index 的 generated_by 生成器未入本卷复核其排班 | 归 M3 注册表族（X2 的 M0 扩展建议=M3 扩）对口复核 | P2 |

## 五、自审闸三态

**挖干（三件物结构与口径差）**：三册字段级实测 ✅ 漂移点逐条带数 ✅；**待裁**：无 Owner 门位事项；缺口 1 属注册表修复施工（归 M3 车道），非本卷裁决。

## 六、复跑命令

```bash
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml',encoding='utf-8'));print(len(d['directories']),d['summary']['total_directories'])"  # 87 84
python -c "import yaml;d=yaml.safe_load(open('data/asset_index/unified-asset-index.yaml',encoding='utf-8'));print(d['total_assets'],d['summary'])"
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml',encoding='utf-8'));print(d['total_files'],d['total_rules'],d['generated_at'])"  # 295 61 2026-09-26…
```
