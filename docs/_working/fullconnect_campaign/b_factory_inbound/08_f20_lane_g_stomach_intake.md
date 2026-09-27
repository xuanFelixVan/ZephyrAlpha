---
ttl: task_bound
title: F20 车道G·全网搜索进货（从胃点菜）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F20 · 车道G-全网搜索进货（lane_g_stomach_intake）

> 挖矿基册=01_strategy_factory/08_f20_lane_g_stomach_intake.md（SF-A）。本卷=独立复核+09-27 增量。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | docs/_working/automation/inbox/intel-*.md——09-27 复测**仍 1 份**（intel-20260916.md）；格式真源=intel_harvester.render_inbox（parse_inbox_entries :66-88） |
| 下游 | lane_g_candidates.csv **0 行**+lane_g_seen_urls.csv **5 行**（09-27 复测，batch=E1G-20260917-070016）；编排 E2 消费源 G（factory_intake_pipeline.py:141-143 try-import） |
| 自动触发 | 事件接线**仍未挂**（图 9 自认）；现态纯 manual；schtasks 09-27 零命中 |
| 真源注册表 | MOD-AUTO-E1G-001 **path_ownership_map 零命中**（grep -c=0，09-27 实证——"暂编号，挂单 H-01 解冻后重编"在案即未入册）；tests/backtest/test_lane_g_stomach_intake.py 在盘；图 9 FAC-E1G partial |
| 门禁质量尺 | 出生证 url+title 进 birth_source（:156-158）；内容寻址 id 跨批去重；seen log 原子语义（失败不标自愈重试 :193-217）；解析委托 B 车道（CLONE-GUARD 决议 :239-242）；宁缺禁硬凑 |
| 运行状态 | **黄（本体绿/双断流）**。唯一班=09-17（5 条目→0 假说）；此后上游胃侧零新班（F96 域）+本车道无触发——09-27 复测 inbox/seen/candidates 三数与基册全同，无任何变化 |

## 二、子模块三级枚举
1. **代码面**：lane_g_stomach_intake.py——parse_inbox_entries :66-88｜collect_inbox_entries :122-130｜run_intake :163-236。单件车道（解析/去重/出生证全委托 lane_b 实现，零克隆）。
2. **注册表/文档面**：path_ownership_map **无条目**（暂编号待重编=注册面缺口）；FAC-E1G（store_refs=lane_g_candidates.csv）；骨架 §4 P1"搜索设备 v0"（业务线代建，升级归 AI 层=F96 域）。
3. **数据面**：inbox 1 份（已消化）；seen 5 行（全 n_candidates=0）；candidates 0 行（表头态）。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**（消化本体 built；事件接线缺+上游断流）。
- **骨架勘误**：①总册 F20 行称核心模块路径含 "lane_g_stomach_intake.py" 而注册表列为 MOD-AUTO-E1G-001——本卷实证该 MOD 号在 path_ownership_map **零登记**，"真源注册表"向实为空悬；重编挂单 H-01 是唯一入册路径。②总册把 F20 上游标 F96——实证断流根因确在 F96 域（AI 层），本车道代码面无缺陷，跨线欠账口径与图 9 一致（车道 F=F06 节点补挂亦为跨线欠账，非本卷范围）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 上游胃断流（F96 搜索班停摆）→G 空转 | inbox 09-16 后零新班（09-27 复测仍 1 份） | 移交 KS-AI/F96 车道（跨组待裁）；G 侧无施工 | P1 |
| 2 | 事件接线未挂（inbox 落新班→自动消化） | 图 9 自认+零计划任务 | 施工：inbox 文件落盘哨兵→run（新文件到达=合法事件）；0.5-1 天；与 F14 触发器同裁口径 | P1 |
| 3 | MOD-AUTO-E1G-001 未入 path_ownership_map | grep -c=0 | 挂起+解锁：H-01 挂单解冻后重编入册 | P2 |
| 4 | 首班 0/5 假说（抽取率风险） | seen 5 行 n_candidates 全 0 | 观察项：连续 N 班 0 产时回看 prompt 召回率 | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核无新缺口（三数全同=零变化实证）；新增注册面欠账一条（§四.3）。

## 六、复跑命令
```bash
ls docs/_working/automation/inbox/intel-*.md | wc -l                 # 1
python -c "import csv;print(sum(1 for _ in csv.DictReader(open('data/strategy_intake/lane_g_seen_urls.csv',encoding='utf-8-sig'))))"   # 5
python scripts/backtest/lane_g_stomach_intake.py run --dry-run       # 幂等演练（应全 seen 跳过）
grep -c "MOD-AUTO-E1G-001" docs/03_modules/path_ownership_map.yaml   # 0=未入册
python -m pytest tests/backtest/test_lane_g_stomach_intake.py -q
```
