---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: P2 择要各项按归属车道并入施工或登记归档批后归档
---

# P2 择要施工卡 · 低成本高确定性修订面 → Q 道汇总分派

## ① 卡面处方（审计原文锚点）

总报告 §四 P2 要点（全量见各 lane 分报告 P2 段）逐项+归属：

| # | P2 项 | 来源 | 归属/处置 |
|---|---|---|---|
| 1 | 计数勘误三处：st-mastertc=172 系行计数实为 95 件；总清单"删 73 行"实为 72；bak 自报 136 实为 135 | lane_c §3/lane_g 口径定谳 | E/G 道随 P0-2/P0-6 勘误顺带（计数用字段不写死） |
| 2 | 机械读数声明一律附 snapshot commit 哈希（E8 型同日陈旧：6072df11ef 落笔时 F 号 0 命中→HEAD 140） | lane_h P1-4 | 制度面：各道台账引用读数时执行；零新 gate（内收） |
| 3 | C85 时钟语义统一（api_server:5398 注入 UTC vs config 窗声明本地时）+跨午夜窗恒 False | lane_e P2-5/6 | 登记移交 OBJ_R 修订窗（出厂关下无害，启用前必须统一） |
| 4 | C320 risk_tier_registry 补 fig15 域行或改口径 | lane_e P2-7 | R 道顺带（注册表行补齐=工程面，非净删）或登记 |
| 5 | C192 簇尺寸 13/7 更正+F033/F035 引证修正+“família”乱码清理+qid 附录化 | lane_f E5/P2-4 | E 道顺带（随 P1⑤ 窗） |
| 6 | 战役树归档批补 10 件 completes_when（6 block files+L3/L6 workbook+34_trigger_surface+p2_card_ledger+r5_exemption） | lane_h E17 | W5 归档批执行（05_block 已由 P1④ 卡顺带单点补） |
| 7 | 执行 r5_exemption.md 删除（moot 残留，删除条件自declared） | lane_h P2-7 | W5 归档批执行 |
| 8 | backfill_created_from_filename.py 一次性器与 retention_derived.py 归档批声明退役或转正 | lane_h §4 | W5 归档批执行 |
| 9 | "蒸发族"结论设机械前置：object DB 全量扫描读数必备（C473/C61 为模板、C129 为反例） | lane_f P2-6 | 制度面登记（晨会/宪法修订建议通道），零新 gate |
| 10 | G-D.4 点火前检查单增补：negatives.csv 写者+分层报告面+strategy_production_map 挂接 | lane_d P2-5 | 登记（波 12 点火前义务，READY_NOT_FIRED 态合法） |
| 11 | 环节总表"132 表 L22 起"指针修为 L16；C107 测试数口径统一（8 vs 16）；C161 卡面路径陈化（S1_ref_integrity） | lane_a P2/lane_g P2 | E/G 道顺带勘误 |
| 12 | capability 册并发 stomper 专项（token 行一夜被抹重插两次实证） | lane_d P2-7 | 登记呈报（L3/总包立专项面，非本役施工） |

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- P2-5 乱码面：C192 矩阵"（考 família 面）"在 HEAD（lane_f E5 复核面今夜未动）。
- P2-11 指针面：00_环节总表末触 6072df11ef 今夜未动——"L22 起"失真指针仍在。
- P2-6/7/8：10 件 completes_when 缺口与 r5_exemption.md 均在 HEAD 原位（master_tc_night 树今夜零触碰）。
- P2-1 计数面：交付报告"172"/总清单"删 73"均原位。

## ③ 上游依赖

各 P2 项依附其 P0/P1 主卡的施工窗（第 1/5/11 项随勘误窗；第 6/7/8 项随 W5 归档批），无独立上游。

## ④ 下游消费者

晨会（制度面 2/9/12 呈报）；W5 归档批（6/7/8 执行清单）；波 12 G-D.4 检查单（10）。

## ⑤ 冲突面

零独立冲突面——全部为顺带修订或登记项；禁为 P2 项单开队列袋（净零纪律：搭车施工）。

## ⑥ 残余与移交

P2 全量清单以各 lane 分报告原文为真源（本卡为择要分派视图，派生声明：不复制证据块，只做归属路由）——lane 报告归档时本卡随役。

## 自审闸三态

**GREEN（挖干）**——12 项全部有归属与处置口径，零悬空、零新 gate、零新 taxonomy。
