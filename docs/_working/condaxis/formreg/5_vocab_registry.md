---
ttl: task_bound
title: 环节[5] 词表登记——两态词表+四轴映射表+state_vocabulary_registry 登记路径
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep 实查）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 官方词表本体 SH-VOCAB-001 | src/zephyr/shared/vocab/market_state.py 实读：:1 SH-VOCAB-001；:50 MacroRegimeVocab（HMM 七态 r1-r4/r10-r12）；:66 EmotionCycleSixVocab（情绪六段）；:81 IntradayFiveVocab（盘中五态）；:107 AnchoredTierVocab（锚定四档） | ✅ 实查在产 | 全系统状态/情绪消费方 | 两态词表=**新增类**（禁改四类既有值）；"新增状态值必须先登记 state_vocabulary_registry"（:9-10 INVARIANTS/MODIFY-GUARD 实读） | ③+④ |
| 词表中央登记表 REG-STATE-VOCAB-001 | docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml 实读：:2 registry_id；:11 语义真源=docs/_working/vocab_legislation/01_official_state_vocabulary.md；:5 执法件=src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py；:33/:44/:55/:65 四官方轴（m.regime/e.cycle/e.intraday/s.anchored）；:88 vocabularies 主区块 **29 条 verbatim**（:94-95 注释实读） | ✅ 实查在产 | STATE-VOCAB-REGISTRY 提交门 | 两态登记走两处：official_ontology 加类（若入官方本体）或 vocabularies 加条（第 30 条）——P2 定位格 | ④ |
| 登记条目字段先例 | state_vocabulary_registry.yaml:99-113 实读（vocabulary_id/name_zh/axis/granularity/states/source/status/canonical_mapping/conflicts） | ✅ 实查在册 | 登记文书模板 | 两态条目照此字段集；canonical_mapping 写到四轴的映射 | ④ |
| 待校准映射先例（proposed） | state_vocabulary_registry.yaml:58-60 实读（IntradayFive approved_edges+proposed_edges：EUPHORIC→IGNITION proposed 待 Owner 校准）；market_state.py:98-104 INTRADAY_TO_SIX 同款 | ✅ 实查在册 | 映射表文书 | 两态→四轴映射中有争议格可标 proposed，但**默认应 adjudicated 后入册**（两态是新立法面，无历史包袱） | ③ |
| 跨轴撞号警示先例 | market_state.py:23-25 实读（AnchoredTier r1-r4 与 MacroRegime r1-r4 撞号近镜像，"禁止裸写 r1~r4 跨轴传递"）；:27-28 EXTREME_STATE_ALIASES 归一 | ✅ 实查在册 | 全消费方 | 两态新枚举名须避开 r 系（建议中文语义名或新前缀），登记 conflicts 字段预写撞号审查结论 | ③ |
| 两态词表 {单边↑/单边↓/横向/数据不可信} | 全仓 grep "两态" src 实读：c3_throttle_attribution.py:25（r4+r10 两态贡献=不同义）、closed_book_gate.py:34（门禁两态=不同义）、其余为无关命中——**形态两态零同义项存在** | ⬜ 空白待建 | [2][3][6] 输出字面量；考试条件轴 | 立法路径=语义真源（01_official_state_vocabulary.md）→market_state.py 常量→registry 登记，三处同批原子（P2） | ③+④ |
| 两态↔四轴映射表 | 无仓内对应件（INTRADAY_TO_SIX 为五态→六段单映射先例） | ⬜ 空白待建 | 跨轴消费（条件轴/考试卡） | 四轴=HMM 七态/锚定四档/情绪六段/盘中五态；映射是多对多非函数（单边↑∩r3 牛市趋势≠包含关系）——按"格语义"登记非按规则推导 | ②+③ |
| 灰度语义入册 | 无先例（现四轴均纯枚举无灰度语义位） | ⬜ 空白待建 | [3] 双轨 | 词表枚举×灰度连续量的组合口径（枚举+∈[0,1]）须在语义真源文书立格式先例 | ③+⑤ |
| "数据不可信"态 | 研究册 §13-7（个股可标注性过滤产物） | ⬜ 空白待建（本线留位） | 个股线姊妹车道 | 大盘线极少触发但枚举完整性要求入位；P2 确认入枚举 | ①上游 |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：market_state.py 四类既有词表、INTRADAY_TO_SIX 映射、EXTREME_STATE_ALIASES 归一机制、registry 29 条主区块（**合并=并集，禁覆盖禁抹条**，registry :96-97 注释实读）。
2. **扩展（加不改）**：market_state.py 新增两态词表类（零逻辑零 IO 纪律照抄）；registry vocabularies 追加第 30 条（或 official_ontology 新轴 m.form，P2 定位格）；entry_count 为派生标量由生成器重算（registry :8 计数铁律实读），**禁手改散文计数**。
3. **新建**：两态↔四轴映射表（含格语义注释）、灰度语义格式先例。
4. **禁**：第 30 套独立词表散落消费方（立法初衷=收编 28 套存量，研究册 §12.3"避免第 29 套"——现数 29 在册，两态入册后为 30 套收编完成态，非新散表）。

# 3. 施工要点（代码实读中的坑）

1. **三处同批原子**：语义真源（01_official_state_vocabulary.md）→代码常量（market_state.py）→机读登记（registry）真源方向立法件=语义真源、本册=机读、代码=镜像（registry :3-4 实读）——三处不同批=执法门与镜像漂移，STATE-VOCAB-REGISTRY 门会拦（values_locked=true 类"值不在册→拦"）。
2. **枚举名跨轴卫生**：r 系已双轴撞号在案（C1 冲突）；两态若用 "up/down/side/untrusted" 类 ASCII 名，须全仓 grep 复认零同形撞义后才定名（本轮 c3/closed_book 的"两态"异义命中即预演）。
3. **proposed 语义慎用**：INTRADAY_TO_SIX 的 EUPHORIC→IGNITION proposed 挂起多时（market_state.py:96-97 注释"挂起等 4 态收敛专项定论"）——两态映射表默认全格 adjudicated 呈批，不留 proposed 尾巴进 P3。
4. **映射是格语义不是规则**：两态↔七态映射（如"单边↑∩r3"）登记的是**经验格语义**（哪些组合在历史上出现过、各自占比），不是"r3→单边↑"的推导规则——推导规则会让两态层沦为七态层的函数，失去独立增量（D 族 3.3 两源分歧 21.09% 的教训：同名 rN 语义不同导致两源打架）。
5. **灰度语义位是格式先例**：现 registry 条目全部纯枚举——两态条目加灰度字段（如 grayscale_semantics: posterior|tstat）是 schema 首扩，P2 呈批须作为格式变更单独列明（schema_version 升版），禁静默塞字段。

# 4. 自审闸三态裁定

| 项 | 裁定 | 理由 |
|---|---|---|
| 两态词表类+registry 登记 | **施工** | STATE-VOCAB-REGISTRY 门强制（不登记=提交面违规）；三处原子成本=一次文书+一次常量件 |
| 两态↔四轴映射表 | **施工** | 跨轴消费（条件轴/考试卡）的查表基础；防 D 族式两源分歧复发 |
| 灰度语义格式先例 | **施工**（随 [3] 同批） | 双轨口径不入册则卡面声明无真源可引 |
| "数据不可信"枚举位 | **施工**（仅占位） | 枚举完整性；消费在个股线 |
| 个股可标注性过滤器本体 | **挂起排期** | 姊妹车道（SECTOR-CAMPAIGN/个股面）职责；本线只供枚举位与语义定义，解锁=个股线立项 |
