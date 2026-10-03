---
ttl: task_bound
completes_when: join checker 落地（施工清单#9）并首跑产出全模块归属总表后，本设计稿转归档
title: 覆盖账本 v2·join checker 设计稿（裁定#481 分母的执行规格）
owner: ZephyrAlpha-Owner
---

# join checker 设计稿 v1（GLM-5.3 出稿，Flash 照稿施工）

## 0. 法定口径（裁定#481，禁改）

- 主账记账单元：src/zephyr/**.py（__init__.py 仅空壳者并入父包计数；非空者独立计）+ scripts/**.py + src/zephyr/frontend/**.{js,html} ≈5,200
- 辅账（记数不追责）：tests/**、docs/**
- 验收不等式：主账每单元 ∈（任一纵轴图直接挂载 ∪ 挂载单元的依赖传递闭包）∨ 判罚（入图/退役）

## 1. 输入真源（四路）

| 真源 | 读法 | 产出键 |
|---|---|---|
| depgraph（PG dep_* 表） | DatabaseService 查 nodes 表 file_path→module_id | file↔MOD-* 双射基表 |
| 纵轴图 YAML ×6 | GOMAP/TDM/FACTORY/图11/12/13，正则提取挂载键（dotted/路径/MOD-*） | 图→挂载集合 |
| 依赖边 | depgraph import 边（或 generate_governance_map 的 scan() 同源逻辑） | 闭包计算输入 |
| scripts manifest | scripts/script-manifest.yaml（机生全量） | scripts 记账 |

## 2. join 规则（三段）

1. **键归一**：图挂载键三形态（zephyr.a.b、src/zephyr/a/b.py、MOD-XXX）统一归一到 file_path；MOD-* 经 depgraph 基表反查，查无=键悬空（单独报，禁静默丢弃）。
2. **归属判定**：file 有直接挂载→直接归属；无→沿依赖闭包找最近挂载祖先→闭包归属（图上标 derived）；闭包内无任何挂载→孤儿候选。
3. **多图归一**：一文件挂多图合法（公共服务），归属表列全量图列表；孤儿判定只看"是否全集为空"。

## 3. 输出 schema（归属总表，机生禁手填）

```yaml
accounting_units_total: N
by_map: {GOMAP: x, TDM: y, ...}        # 直接挂载数
closure_derived: z                      # 闭包归属数
orphans:                                # 两不沾清单
  - file: src/zephyr/...
    cluster_hint: <顶级包.子包>          # 簇分组线索
    evidence: {imports_in: 0, imported_by: 0, last_commit: <date>}
units:                                  # 全量明细（每单元一行）
  - file: ...
    maps_direct: [GOMAP, TDM]
    maps_derived: [FIG12]
    status: direct|derived|orphan
```

## 4. 边界 case 裁定（预答，Flash 遇到按此办）

| case | 裁定 |
|---|---|
| __init__.py 空壳 | 并入父包，不单独计 |
| 一文件多图 | 合法，maps_direct 列全 |
| 键悬空（MOD-* 查无文件） | 报 dangling_keys 段，禁静默 |
| tests 文件 import 主账文件 | 不影响主账归属（辅账不回流） |
| scripts 无 MOD 键 | scripts 记账走 script-manifest+图 scripts 字段直接 join |
| 生成器自身 | 计入 GOMAP 挂载（治理域） |

## 5. 施工与验收

- 落位 scripts/governance/d5_architecture/generators/（新 .py 走 14 字段头+token+CREATE-GUARD）
- 输出两件：归属总表 YAML（docs/_working/map_build/30_attribution_table.yaml）+孤儿簇报告 md
- 接入 align_all 新节（exit>0 on orphan 超阈，阈值首跑后随填充班递降）
- 验收=首跑产出+红蓝（伪造孤儿/悬空键/闭包环三攻击样例全红拦）
