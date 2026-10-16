---
doc_type: mine_fullchain_index
title: 全链路挖矿封矿索引（机生）
created: 2026-10-15
session: mine-fullchain-seal-20261015
creation_token: mine-fullchain-seal-20261015-index
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
ttl: task_bound
method_note: 文档数/三态统计/top3 全部由脚本对 174 本子文档机械 grep 计数（自审闸节内表格行逐格归一 pass/warn/fail，粗体与带括注判词先归一再数），禁手数；覆盖锚=各本 frontmatter（skeleton_row/node_id/step_id/segment_id）或段文件名规则映射回骨架 §2 行 ID。
---

# 00 封矿索引（2026-10-15 封矿时点，机生）

## 1. 覆盖核验（骨架 172 环节行 vs 9 段 174 本）

骨架 §2 共 172 行（业务主链 85=策略生产 10+卡生命 13+交易决策 14+当日运营 48；数据链 22；治理链 20；交付链 45=图11 28+图14 17）。机械比对结果：**172/172 行各有宿主本，零缺行、零重复锚**。

| 段目录 | 骨架行数（口径） | 文档数 | 差值说明 |
|---|---|---|---|
| factory_strategy | 10（§2.1 FAC-E0..E9） | 10 | — |
| card_lifecycle | 13（§2.2 D15-S1..S13） | 13 | — |
| tdm_trade_decision | 14（§2.3 四 flow 一级环节） | 14 | — |
| daily_ops_am | 26（§2.4 前半：A 盘前 12+B 盘中 14） | 26 | — |
| daily_ops_pm | 22（§2.4 后半：C 盘后 12+D 夜窗 10） | 23 | +1 gap 件 SD13-G03（图13 骨架外 gap 节点，六向台账+自审闸齐备），并入宿主段，如实记 |
| data_chain | 22（§2.5 DSC-01..21） | 22 | — |
| governance_chain | 20（§2.6：D16 立法流 6+GOMAP 七族 7+nav 七段 7） | 20 | — |
| delivery_fig11 | 28（§2.7 图11：S 9+C 13+D 6） | 29 | +1 gap 件 D11-G01_G02_gap_verify（图11 骨架外双 gap 核实专档），并入宿主段，如实记 |
| construction_fig14 | 17（§2.7 图14 D14-01..17） | 17 | — |
| **合计** | **172** | **174** | 172 环节本+2 gap 件 |

## 2. 三态统计与最红项（自审闸格机械数）

| 段目录 | 文档数 | pass | warn | fail | 最红项 top3（fail 数序，格注 F/W/P） |
|---|---|---|---|---|---|
| tdm_trade_decision | 14 | 80 | 3 | 1 | TDM-F-C1(1F/0W/5P)、TDM-X-S1(0F/2W/4P)、TDM-P-P1(0F/1W/5P) |
| factory_strategy | 10 | 41 | 18 | 1 | FAC-E5(1F/3W/2P)、FAC-E1(0F/3W/3P)、FAC-E9(0F/3W/3P) |
| card_lifecycle | 13 | 24 | 34 | 20 | D15-S13(4F/2W/0P)、D15-S9(4F/1W/1P)、D15-S11(3F/2W/1P) |
| daily_ops_am | 26 | 98 | 38 | 20 | D13-09(5F/1W/0P)、D13-13(3F/1W/2P)、D13-16(2F/2W/2P) |
| daily_ops_pm | 23 | 63 | 53 | 22 | D13-31(5F/1W/0P)、D13-G03(5F/1W/0P)、D13-29(4F/2W/0P) |
| data_chain | 22 | 79 | 49 | 4 | DSC-18(1F/3W/2P)、DSC-02(1F/2W/3P)、DSC-15(1F/2W/3P) |
| governance_chain | 20 | 96 | 23 | 1 | NAV-2(1F/1W/4P)、D16-S2(0F/2W/4P)、GOMAP-L0(0F/2W/4P) |
| delivery_fig11 | 29 | 148 | 17 | 3 | D11-C02(1F/2W/3P)、D11-S05(1F/1W/4P)、D11-D05(1F/0W/5P) |
| construction_fig14 | 17 | 62 | 26 | 14 | D14-02(3F/2W/1P)、D14-11(3F/2W/1P)、D14-04(2F/2W/2P) |
| **合计** | **174** | **691** | **261** | **86** | — |

格数守恒：173 本含 6 格自审闸，合计 1038 格=173×6（691+261+86）；唯一例外=D11-G01_G02_gap_verify 专档（无自审闸，见 §3 例外记）。含≥1 个 fail 格的本=45；三态全 pass 的本=39。fail 最重五本：D13-G03/D13-31/D13-09（各 5F）、D13-29/D15-S13（各 4F）。

## 3. 封矿裁定（三条件逐一判定）

1. **覆盖完整（172 行各有归宿）**：PASS。172/172 行机械锚定宿主本，零缺行、零重复；2 本 gap 件并入宿主段（骨架 §3 本就登记其为图自报骨架外缺口件），如实记。
2. **每本含六向台账**：PASS（环节本口径）。172 本环节本+D13-G03 gap 件共 173 本六向台账六向俱全（机械查"输入/输出/SSOT/代码/门禁/自动化"六向在位）；唯一例外=D11-G01_G02_gap_verify 系双 gap 核实专档（结论：G01 维持成立、G02 实质已修复仅图注未回写），非环节本，不适用环节本六向台账格式——例外如实记，不计缺。
3. **每本含自审闸三态**：PASS（环节本口径）。同口径 173 本各含 6 格 pass/warn/fail 三态表；fail 86 格是挖矿产出的真实记录（封矿条件是结构齐备，非全绿），top 红已列入 §2 供后续清账排序。

**判定：SEALED**（附 1 件例外记于条件②③；骨架两处计数漂移已按矿工回报+书记员机械复核追加至 00_skeleton.md 末节「勘误 2026-10-15 封矿时点」，只追加不改正文）。

## 4. 遗留清账指针（不阻封矿）

- fail 重灾段：card_lifecycle（20F/13 本，宿主册 experiment_registry 缺位族）、daily_ops 两段（42F，gap/未接线族）、construction_fig14（14F，unwired 族）——与骨架 §3 各图自报缺口同根，宜按 P2 缺口收口批推进。
- D11-G01/G02：G02 图注未回写（代码侧已收口），下批触图时一并翻转。
- 勘误两处（TDM 节点计数、91→107 门）待骨架下批修订时落入正文。
