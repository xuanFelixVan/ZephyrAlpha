---
ttl: task_bound
title: F14 E1 想法进货编排（factory_intake_pipeline）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F14 · E1 想法进货编排（factory_intake_pipeline）

> 挖矿基册=01_strategy_factory/02_f14_e1_intake_orchestration.md（SF-A）。本卷=独立复核+09-26/27 增量。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | _LANE_SPECS 六行（factory_intake_pipeline.py:50-72，09-27 重读）：D/B/C/F/G/I；F=latest_grid_manifest() 动态解析 grid_*/manifest.csv（:75-79）；C2/C3 不在表 |
| 下游 | run_pipeline→three_high_screen.run_screen（E1D 首步）→可选 lane_b→E2 幂等消费六源 D/B/C/C2/G/I（intake_sources 组装，:135-146）→auto_construct（C/C2 公式轨，_CONSTRUCT_LANES :169 后）→race 计分板 |
| 自动触发 | 人工/会话：schtasks 09-27 零 factory 计划任务实证；最近一次编排事件=2026-09-26 10:27-10:29（E1D-20260926-102753→E2-20260926-102842→translator 10:29，台账时间戳互证，为一次手工进货班） |
| 真源注册表 | MOD-BT-154=path_ownership_map.yaml:15928,35409；图 9 FAC-E1 partial（strategy_production_map.yaml:66-81）；data_refs 仍挂"待定:c1_market.news_data"（F-AUDIT-BLIND-04）；tests/backtest/test_factory_intake_pipeline.py 在盘 |
| 门禁质量尺 | 编排不评分（INVARIANTS）；preflight_compute_gate 逐车道问闸（:82-96）；车道模块缺位 BLE001 降级不阻断（:138,143）；台账不可达 fail-closed |
| 运行状态 | 绿（本体）+黄（触发/覆盖）。09-26 编排真实跑通一轮（D 新批 20 行+新 E2 批）；grid 批 09-25/26 续跑 4 班（grid_20260925-111219..grid_20260926-230010，末班空壳） |

## 二、子模块三级枚举
1. **代码面**：_LANE_SPECS:50（六行；C3 未列）｜latest_grid_manifest:75｜preflight_compute_gate:82｜run_pipeline:99（D→可选 B→E2 六源→汇总 report）｜auto_construct（C/C2→159 桥+creation_token 批登记）｜_e2_passed_by_channel（CH fail-closed）｜race_scoreboard/cmd_race。
2. **注册表/文档面**：path_ownership_map:15928；FAC-E1 节点（store_refs=data/strategy_intake/ 永久）；设计出处=2026-09-13-strategy-factory-pipeline-discussion.md+2026-09-14-full-chain-factory-blueprint.md；docs/library/INDEX.md（21 行）零工厂条目——进货侧无图书馆面。
3. **数据面**：data/strategy_intake/ 台账族 09-27 实测——raw_manifest 597/screen_c2 597/lane_b 4/lane_c 16/lane_c2 8/lane_chain 10/three_high **60**/lane_g 0+seen 5/translated_manifest **8**/constructed_manifest 1/f06_survivors 1/c4_deferrals 321/grid_* 24 目录。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**：本体+六源消费实证；缺事件触发器、F 适配器、C3 挂载。
- E2 消费循环逐源核对（:135-146 重读）：D/B 静态+C/C2 try-import+G try-import+I 硬编码路径——**F 确不在循环**（recipe 适配器缺位维持）。
- **骨架勘误**：①总册 F14 行括注"C 车道重算力闸点待 E1C 施工"**已过时**——_LANE_SPECS C 行 local_gpu+E0 heavy 闸生效（码注 WO-⑤-06 09-18 修正），车道 C 已三批出货（09-14/15/22）；FAC-E1 algo_note 同句同病，建议下版图改。②总册/图 9 称"六车道"，实为**七车道声明面**（A 在图 9 有节点但不在编排表；C2 挂 C 名下；I 已在编排但图 9 无节点）——口径以 _LANE_SPECS 实码为准。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 全厂无事件触发器（09-19 后停滞、09-26 手工班再证） | schtasks 零工厂任务；进货=人工跑命令 | 挂起+解锁：触发器口径（日历收盘事件 vs 人工合法语义）须总筹/Owner 裁，跨 M5/SF | P1 |
| 2 | F 车道 recipe 适配器缺（E2 六问不适用） | :60-62 代码注释自认；f06_survivors 1 条走 MOD-BT-211 旁路 | 待裁：裁定"F 直考旁路 vs 补适配器"后改码或除名 | P1 |
| 3 | C3 未挂 _LANE_SPECS | mcts 零出货（lane_c3_candidates.csv 不存在） | 挂起：解锁=C3 首次真实出货后 2 行挂载 | P2 |
| 4 | FAC-E1 data_refs 挂"待定:news_data" | yaml 注释 F-AUDIT-BLIND-04 | 文档工：下版图收敛 | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核无新缺口；增量=09-26 手工班证明通路仍健康（非代码退化）；勘误两条（§三①②）已录。

## 六、复跑命令
```bash
python scripts/backtest/factory_intake_pipeline.py run --dry-run
python scripts/backtest/factory_intake_pipeline.py race      # 需 CH
sed -n '50,79p' scripts/backtest/factory_intake_pipeline.py  # 六行车道声明+F 动态解析
schtasks /query /fo csv | grep -iE "factory|lane|intake"; echo "(空=无事件触发器)"
python -m pytest tests/backtest/test_factory_intake_pipeline.py -q
```
