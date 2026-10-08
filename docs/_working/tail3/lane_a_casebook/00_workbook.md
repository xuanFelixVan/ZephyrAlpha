---
created: 2026-10-08
session: st-t3a-casebook
ttl: task_bound
completes_when: 新裁定落册 ruling_registry（同 commit 原子）+casebook_registry 注记 006-008=reserved_void+伪造占用红蓝显红+两轮检查零问题
---

# 车道A·CASEBOOK 空号作废 作业簿（st-t3a-casebook）

> **Owner 已批裁定原文**：「006/007/008 因处方遗失作废，永不回填，新册从下一新号顺延」
> **任务**：①ruling_registry 登记新裁定（RULE-RULING 同 commit 原子：空号作废+理由=E-12 处方遗失/blob 考古已尽/勿造假凑数原则）；②casebook_registry 加注记段：006-008=作废空号（reserved_void），下一新册号顺延不补；③红蓝：伪造试图占用 006 的册条目→注记机制必须显红；连续两轮检查零问题。

## 1. 挖矿台账（六向，每向≥1 发现或"已查无"）

| 向 | 发现/已查无 | 证据锚 |
|---|---|---|
| ①上游（案册授号机制源头） | 授号=挂图 SOP §3 机规1"册号"载体（Owner 2026-10-04 批 st-vm12e-20261004 上户口）；条目增删随裁定批走 | 册头注释 L2-4 |
| ②下游（消费者/校验门） | 消费面=纵向地图家族 casebooks 字段唯一反查册；治理类库豁免 TDM 交叉轴（tests/trading/test_decision_map.py::TestNewRegistryGate._GOVERNANCE_EXEMPT）；无既有 reserved_void 校验器（已查无→本车道补防重门测试） | 册头注释 L6-8+grep |
| ③算法/机制（编号生成与校验逻辑） | 编号=CASEBOOK-NNN 顺序授号；无机生（maintenance: manual 低频）；006-008 曾于 2026-10-07「补授」重建（E-12 处方原件随 f2z §六配方遗失，凭 chief 记录重建） | 册体 006-008 条目内注 |
| ④后端（册存储/同步面） | 纯 YAML 册（rules 数据=YAML 真源，无 DB 双轨）；热册写面=CAS+裁定同批 | ROOR/册头 schema |
| ⑤前端（展示/报表面） | 已查无（无独立前端面） | — |
| ⑥数据字段（现有编号/字段） | 现册=001-008 号段+outside_registry 段；006=supply_sentinel gap 台账/007=采集打卡账本/008=归档清单（三本均 10-07 补授重建，即本裁定作废对象） | 册体尾 30 行 |

**交叉验证重大发现（2026-10-08 03:3x）**：st-acure-20261008-chief 已在途本案——casebook_registry 工作区已带头注「2026-10-08 裁定#492（Owner 批）：006/007/008 作废 reserved_void…详见册尾注记段」，但①册尾 reserved_void 段未落②裁定#492 未进 ruling_registry 盘面（盘面顶=#487，其工作区在途 #490/#491）。判定=chief 施工中未完，**本车道按「同文件他队在编→登记排队后置再编辑；他队已完成→交叉验证加固而非重做」纪律转后置位**：等 chief 落地后做三方核验（头注↔册尾段↔#492 条目）+补 reserved_void 防重门测试（伪造占 006 显红）。

挖干裁定（自审闸三态）：**施工（后置协防位）**——六向已挖干；chief 在途面等待落地窗口后交叉验证+测试补强，不重做不并行写。

## 2. 施工记录

- [x] ~~ruling_registry 新裁定登记~~ → **改判**：chief 在途批已含（#490/#491 在其工作区，#492 为其 casebook 头注所引）；本车道不重复授号（防同号双登事故）
- [ ] casebook_registry 注记段 → chief 落地后三方核验（头注/册尾 reserved_void/裁定#492 同批原子）
- [ ] reserved_void 防重门测试（tests/，伪造占用 006 显红；chief 落地后按实际注记格式落件）
- [ ] 两轮循环检查零问题

## 3. 红蓝战果

（待填）

## 4. OPEN_QUESTIONS

（空=无）
