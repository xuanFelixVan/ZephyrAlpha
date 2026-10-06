---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_crypto —— TDM 币圈族（C-L1/L2/L3/L4，4 节点，全缺口）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.10（并入各 flow 判缺，本册单列）。
- 计数: 4 全 C，全 L4（无 module_ref、无 mounts、conf=untested）。
- 归属口径：这 4 枚在 00 §2 各 flow 表中扣除、集中于本册，保证 182 零重复计数。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 所在 flow | 类别 | 接线级 | 现状 | 行 |
|---|---|---|---|---|---|---|
| TDM-C-L1 | 币圈大盘总闸 | entry | C | L4 | 无模块无挂载；market=crypto | TDM:L4594 |
| TDM-C-L2 | 赛道选择 | entry | C | L4 | 同上 | TDM:L4616 |
| TDM-C-L3 | 币对选择 | entry | C | L4 | 同上 | TDM:L4637 |
| TDM-C-L4 | 币圈买卖点 | entry | C | L4 | 同上 | TDM:L4658 |

## 2. 缺口与可考性判定

- 全域 L 级缺口（H9 L5）：无 crypto 行情载荷、无 crypto 回测，全仓 grep 仅 backlog 提及（H9 §1.2 C-L1 证据）。
- 唯一图内锚点：L9-A15 源线·加密永续/费率（TDM:L5035，同为图纸）。
- **Owner 门位在案**：chief 02 §6 Owner 门位组含"F51 币圈退役"——币圈域存在"退役 vs 建设"的 Owner 级未决议题；本车道立场：在 Owner 裁定前，crypto 4 节点的缺口不排期、不备料，只登记。

## 3. 一句话修复建议

先请 Owner 裁 F51（退役 or 独立域立项）；若建设，按 L5 独立域走"行情载荷+回测+四节点全链"单独立项，禁搭 A 股考卷便车。

## 4. 交叉验证

- H9 §1.10 判定与计数口径一致（4 枚已计入其 §1.2/1.3/1.4 各节，本册单列不重复计）。
- chief B1 分组把 crypto 计入 ENV-08/09/10/11 各环节（其 L1=10/L2=30/L3=26/L4=16 均含 C）——两种口径对全集 182 无损，99 册双口径对平。
- SPM 全图无 crypto 专属节点（341 内 grep 无）——工厂侧连占位都没有，属两图共同空白。
