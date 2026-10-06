---
ttl: task_bound
completes_when: W1-W4 全交付+GW 落地+晨报呈报后随战役归档
title: TDM 2.0 扩容+排班表对齐班 · 交付索引（st-tdm20-20260923）
owner: st-tdm20-20260923
session: st-tdm20-20260923
date: 2026-09-23
---

# TDM 2.0 扩容班 · 交付索引

| # | 件 | 说明 |
|---|---|---|
| 00 | [00_tdm20_ledger.md](00_tdm20_ledger.md) | 台账：输入真源/设计定案 D-1..D-8/直改主区登记/避让账 |
| 01 | [01_node_expansion_list.md](01_node_expansion_list.md) | W1 挖矿产物：44 节点+60 边设计清单+PQ 吸收计数（机生） |
| 03 | [03_pp001_slot_alignment.md](03_pp001_slot_alignment.md) | W3：PP-001 档位补齐+四层判定表契约对照+能力反查修复 |
| 04 | [04_chain_recon_report.md](04_chain_recon_report.md) | W4：chain_refs 双向对账首跑读数（只报不清，机生） |

## 同批落地（真源面，不在本目录）

- `config/trading_decision_map.yaml`：138→**182 节点**、194→**254 边**（L9 知识供给层+边语义四元组+旧边机械回填+activation 全覆盖）
- `src/zephyr/trading/decision_map.py`：边四元组字段+R43 分级校验+chain_refs 轴（R45）+容量
- `scripts/governance/generate_chain_registry.py`：chain_registry.yaml 生成器（873 链机生，禁手改）
- `scripts/governance/reconcile_chain_refs.py`：双向对账探测器（只报不清）
- `docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml`：机生值域真源
- `docs/02_enterprise_architecture/10_trading_map/`：图表册 9 册重渲染（含新 08 L9 册；FILE_PLAN 断因修复）
- `config/framework_plans.yaml`：PP-001 派生计划 sha 重刷（权重零变化）
- `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`：sector 反查盲区 2 条目
- `tests/trading/test_decision_map.py`：R43/四元组/chain 轴 10 例

## 前后对照

| 指标 | 前 | 后 |
|---|---|---|
| 决策职能节点 | 138 | **182**（目标 [150,250] ✓） |
| 边（全带四元组） | 0/194 | **254/254**（60 新边真 PIT 陈述+194 存量 legacy-unaudited 欠账显式） |
| 带档位节点 | 110 | **182/182**（2 处 on_demand 刻意覆盖保留） |
| chain_refs 轴 | 无 | 873 链值域在册；首跑引用 8/0 断链；575 有效链未吸收=探测器读数 |
| 板块反查面 | 七关键词全空 | sector/板块/行业轮动/rotation/板块数据 全命中 |
| 图表册 | 8 册（生成器已断，L0 批起 6 节点无家） | 9 册对账 182=182 ✓ |
