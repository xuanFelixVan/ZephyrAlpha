---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
created: 2026-08-31
---

> ## 结案报告（2026-10-14 由 st-wkcure-chief-20261013 核验）
> **总结论：已结案（机生派生快照、无自有工作包；生成器在仓可复跑，唯一读数缺口 MOD-SIG-110 属 frontend_map.yaml 真源侧挂接义务，不阻本文书结案）**
> **✅ 已完成（逐条，每条带可回溯证据）**
> - 生成器存在且可复跑：证据=ls 实测命中 scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py（GEN-OK）。
> - 四类对账口径 A/B/C/D 全部建成并有具体读数：证据=本文正文 §A-§D 表+统计段实测读数 A0/B1/C0/D0，功能点总数 359、前端覆盖模块 21。
> - 已取代两本手工缺口总账的派生链在册：证据=正文派生物声明（真源=frontend_map.yaml+depgraph 三字段）；capability_canonical_file_registry.yaml 收录本件（git grep -l 命中）。
> **⚠️ 未完成（逐条）**
> - 文书本体无剩余工作包（机生件，随真源重派生）。附注一：下表头旧章（2026-10-06 st-workingchief-20261006 报告）L11-42 为"一字一行"残章格式损伤，内容仍可辨（结论=已结案，与本次实测一致），重盖归总包"坏章全扫重盖"台账处理，本核验未改动旧章一行。
> - 附注二：B 类唯一缺口 MOD-SIG-110（声明 has_frontend=yes 但未挂功能点）修复义务在 frontend_map.yaml 真源侧——属他役开口项，注册在他役不阻结案。
> **与归档孪生件的裁定**：根面 vs archive/2026-09/c_class_scattered/ 同名件——diff 实测全部 43 行差异均为根面独有的 2026-10-06 旧结案章（含残章），正文/表体逐字节相同，差异非实质；建议=真身留根面（根面=超集，含后续核验痕迹；机生件本可重派生，归档孪生可退役）。
> **核验方式**：全文读；ls 验生成器；diff 根面 vs 孪生逐字节比对（43 行差异定位）；git log -1 实测最后改动=2026-10-07；git grep -l 引用面（注册表+chief 台账均收录）；HEAD=b05345f8e6
> **证据等级**：A=实测可复现（生成器存在、diff、引用面均命令命中）
> **处置建议**：可归档（archive/2026-10）——机生快照非活输入；如担心漂移可注明"随需重派生"

> ## 结案报告（2026-10-06 由 st-workingchief-20261006 核验）
> **总结论：已结案（机生派生快照，非待办载体；A/B/C/D 四类缺口 0/1/0/0，唯一缺口 MOD-SIG-110 归 frontend_map.yaml 真源治理）**
> **✅ 已完成（摘录）**
> - ①生成器活账落地并取代两本手工缺口总账；②四类对账口径 A-D 全部建成；③生成器 scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py 在仓可复跑
> **⚠️ 未完成**
> - 无（MOD-SIG-110 挂接缺口的修复义务在真源侧，非本文件）
> **核验方式**：全文读+生成器存在性核验+与 2026-08-22 总账未结案章交叉对轴（两账不矛盾）
> **处置建议**：保留（机生件，可随时重派生）


> **派生物声明**：本文件由 `scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py` 自动生成，**禁止手工修改**（手改会被下次派生覆盖）。真源=frontend_map.yaml + depgraph nodes 前端覆盖三字段。取代对象：两本手工缺口总账（2026-08-22 正向/反向账）——过渡期双跑对照，Owner 裁定后总账停手工维护。

# 前端缺口视图（派生活账） · 2026-09-17 10:25 中国标准时间

## A. 前端有 → 后端没有（0 项：frontend_map 功能点 backend_ref 空）

| 功能点 | 页面 | 名称 | 状态 |
|---|---|---|---|

## B. 后端有 → 前端没有（1 项：has_frontend=yes/planned 但 frontend_ref 空）

| 模块 | has_frontend | 说明 |
|---|---|---|
| MOD-SIG-110 | yes | 声明有前端但未挂功能点 |

## C. 悬空引用（0 项：frontend_ref 指向 frontend_map 不存在的功能点）

| 模块 | 悬空引用 |
|---|---|

## D. 对账异常（0 项：has_frontend=no 但未填理由）


## 统计

- frontend_map 功能点总数: 359
- depgraph 已声明前端覆盖模块数: 21
- A/B/C/D 四类缺口: 0 / 1 / 0 / 0
