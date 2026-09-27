---
ttl: task_bound
title: F15 车道A·社区货源（聚宽 597 条人工版）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F15 · 车道A-社区货源

> 挖矿基册=01_strategy_factory/03_f15_lane_a_community.md（SF-A）。本卷=独立复核+09-27 增量。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | 本地源码目录 E:\数据下载\qmt聚宽策略\2020-2026聚宽600条源码（strategy_intake_inventory.py:48 _DEFAULT_SRC，盘外依赖） |
| 下游 | raw_manifest.csv→normalized/<year>/ 归一副本→screen_c2.csv→intake_load_screen_c2.py 幂等灌 c1_backtest.strategy_screen→C4 翻译批（35 条人工验收集=translated/ 命名件源头） |
| 自动触发 | 无：人工收货+一次性盘点；Scrapling 爬虫=design_refs 候选零代码；schtasks 零命中（09-27） |
| 真源注册表 | MOD-BT-035=path_ownership_map.yaml:35444（grep 实证）；图 9 FAC-E1A **built**（strategy_production_map.yaml:83-98）；SOP 真源=backtest_system_sop/sop_c_strategy_library_intake.md §1 |
| 门禁质量尺 | 破损记 unreadable 不猜测（inventory:108-109）；原文件只读；md5_12 内容指纹判重；产物落 gitignore 区（可再生） |
| 运行状态 | 绿（存量）/停（增量）。09-27 复测 raw_manifest **597** 行、screen_c2 **597** 行（381 candidate/216 excluded，基册口径无变化）——09-12 后仍零新增 |

## 二、子模块三级枚举
1. **代码面**：strategy_intake_inventory.py（inventory C1 :78-128、_decode 四编码兜底 :58-65、平台启发式 :51-55）｜intake_load_screen_c2.py（幂等灌表 :24-）。两件之外无他。
2. **注册表/文档面**：path_ownership_map:35444；FAC-E1A（store_refs=normalized/ 永久盘面留存，git 不跟踪）；sop_c_strategy_library_intake.md；图 9 design_refs=Scrapling 爬虫候选。
3. **数据面**：data/strategy_intake/{raw_manifest,screen_c2}.csv 各 597 行；normalized/ 年度子目录（09-12 后未动，mtime 实证）。

## 三、接线四态独立复核
- 图 9 四态 built → **维持 built（人工版口径）**；inventory 四件（盘点/归一/粗筛/灌表）全实证。
- **骨架勘误**：无新勘误。总册 F15 行、清单 §1.4（F15 不在 partial 名单）、SF-A 三方一致，本卷复核认同。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 增量断流：09-12 后零收货 | raw_manifest 597 行无新批；无爬虫无事件 | 低配施工（inventory 增量模式 ≈0.5 天）或爬虫立项（2-3 天，Owner 批） | P2 |
| 2 | _DEFAULT_SRC 盘外硬编码（E:\ 数据目录） | inventory:48；换机即断 | 施工：缺省值改配置项 ≈0.5 天 | P2 |
| 3 | 归一副本与 manifest 双写无事务 | 基册 §四.3；未见事故 | 挂起：inventory 可重跑自愈，观察项 | P2 |

## 五、自审闸三态
- **三态：built（人工版口径）**。沿用基册+复核无新缺口（597/597 复测一致）；自动化口径差什么=爬虫+增量模式+收货事件接 F14。

## 六、复跑命令
```bash
python -c "import csv;rs=list(csv.DictReader(open('data/strategy_intake/raw_manifest.csv',encoding='utf-8-sig')));print(len(rs))"
python -c "import csv;rs=list(csv.DictReader(open('data/strategy_intake/screen_c2.csv',encoding='utf-8-sig')));print(len(rs))"
python scripts/backtest/strategy_intake_inventory.py --dry-run --src "E:\\数据下载\\qmt聚宽策略\\2020-2026聚宽600条源码"
```
