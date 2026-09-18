---
ttl: task_bound
doc_type: report
title: 深度审查报告——板块强度聚合器（S02）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：板块强度聚合器（S02）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/core/sector_strength_aggregator.py:85`（aggregate_sector_strength）/ `:139`（select_candidate_pool）
- 生产调用方: `core/sector_strength_wiring.py:188,197`（wire_from_report，唯一生产路径）；wiring 自身生产调用方=0（仅 `core/__init__.py:26-30` 门面导出）
- 测试文件: tests/signal_ashare/sector/test_sector_strength_aggregator.py（已入库，已审）；**他会话在途**：tests/signal_ashare/test_sector_strength_aggregator.py（untracked，当前 **0 字节空文件**，2026-09-14 时间戳）
- 备注: 他会话在途新测试文件（sector_strength_aggregator/sector_ecology_judge/sector_strength_wiring 三件 untracked）——按现状审：空文件不计测试覆盖，收口时注意两份同名测试并存风险

## 1 对象快照

- **范围**：`sector_strength_aggregator.py` 全文 192 行——单板块四路子分等权合成（0.25×4）+ 市场级调节（clamp ±10）→ composite clamp [0,100]；跨板块 Top-ceil(15%) 候选池截取。纯函数零 IO、frozen、fail-closed。
- **排除项**：`sector_strength_wiring.py`（rank 归一适配层，MOD-SIG-144，不在本对象边界；其零生产调用方事实作为轴 C 证据引用）；`sector_ecology_judge.py`（MOD-SIG-143，另件）。
- **测试覆盖概况**：24 断言覆盖负值/NaN/权重不归一/调节越界/空池/平票稳定序/JSON 往返/无墙钟。信任度：**信任（一处把越界 clamp 固化为预期行为，见轴 A-1）**。
- **材料包缺项声明**：无运行时证据包（wiring 链无生产触发者）；数据画像缺（子分分布无从画像）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **上界缺失+契约矛盾**：header INVARIANTS 宣称"输入越界/缺失维度/NaN → SectorStrengthInputError（fail-closed）"，但 `_validate_score` 只拒负值与非有限，**>100 静默放行**；composite clamp [0,100] 掩盖越界，且输出子分保留原值（structure_score=120 与 composite=100 自相矛盾）。测试 test_score_above_100_clamped 把 clamp 固化为预期——契约与实现二选一，当前声明是假的 | sector_strength_aggregator.py:8（INVARIANTS）vs :76-82（无上界检查）、:127（clamp）；test :76-78 | **P1** | `aggregate_sector_strength("X",150,50,50,50)` → 不抛错，composite=75、structure_score=150（0.25×150 越界权重直接计入合成） |
| A | 候选池截取 ceil 语义：N<20 时有效比例 >15%（如 N=7→2 个=28.6%），N=1 时 100%——"Top-15%"节点语义在小截面口径放大；docstring 已如实写 ceil（:143），非漂移属设计，但小截面日（如板块数骤减）池子相对放宽 | sector_strength_aggregator.py:156（max(1, ceil(N×ratio))） | P3 | `select_candidate_pool([7 个])` 数 in_candidate_pool=2 |
| A | 并列排名边界：composite 平分跨 n_pool 切线时按板块名 Unicode 序决定入选（非业务序）；确定性有保障且 docstring 声明（:152-155），但中文板块名排序对决策不可解释——平分周发生在同分板块簇（等权+rank 归一输入下并不罕见） | sector_strength_aggregator.py:152-155 | P3 | 构造两板块同 composite，观察 AA 先入池（测试 :97-101 已固化该行为） |
| A.3 | 测试缺全 NaN 边界外的"inf"用例与 weights 长度≠4 用例（zip 截断后 sum≠1 会以"权重不归一"兜底报错——行为正确但属误报性兜底，非显式校验）；空字符串板块名已覆盖 | test_sector_strength_aggregator.py 全文 | P3 | `aggregate_sector_strength("X",50,50,50,50,weights=(0.5,0.5))` → 报"权重不归一"而非"长度非法" |
| B | 上游契约：四路子分应为 0-100（docstring :99），唯一生产路径 wiring 层先做 rank 归一 0-100（sector_strength_wiring.py:83 _percentile_scores）→ 走 wiring 有保障；**绕过 wiring 的直接调用方无任何保障**（同 P1 上界问题）。market_adjustment 注入方=L2-01-5 market_forecast_fusion（接线链上由 wiring 映射涨停分档，BREADTH_CLIMAX_MAP） | sector_strength_aggregator.py:99；sector_strength_wiring.py:83-101 | P2 | 审 wiring 调用点 :188 实参来源 |
| B | build_sector_strengths 缺键 → 裸 KeyError，违反本件 ERROR_CONTRACT（只承诺 SectorStrengthInputError） | sector_strength_aggregator.py:174-192（r["structure_score"] 直取） | P3 | `build_sector_strengths([{"sector":"X"}])` → KeyError 而非 SectorStrengthInputError |
| C | **下游链**：本件→wiring（wire_from_report :188-197）→WiringResult（池+生态+notes）→IDX-02 板块页（声明）。但 **wiring 自身生产调用方=0**（grep wire_from_report 仅 core/__init__.py 门面导出）→ 整条 L2-01 链在 src/scripts 内无最终触发者；`[CONSUMERS]` 的 TDM-E-L2-06/L3 自认"待接线"（:5）诚实。爆炸半径：候选池错→板块候选池错→决策链偏移（P1 级），当前未通电 | 全仓 grep wire_from_report 仅 core/__init__.py:27 | P2 | grep 命令同左 |
| C | 空板块序列 → select_candidate_pool 返回 []（:150-151）不报错——"当日无板块候选"语义合理，但下游（未来 IDX-02/候选池）须有空池告警约定，当前无 | sector_strength_aggregator.py:150-151 | P3 | `select_candidate_pool([]) == []`（测试 :94-95 固化） |
| D | 兄弟实现盘点：candidate_pool_aggregator（个股池聚合，无 ceil/15% 同构逻辑——口径不同源，无重复实现）；tiered_screening_filter/screening_funnel_report 仅引用 fine_scoring/coarse 漏斗不引本件。**本件 Top-N 截取逻辑在仓内无双份承载**——已查无漂移 | 全仓 grep select_candidate_pool/build_sector_strengths | —（已查无） | grep 命令 |
| E | 静默失败：越界子分静默 clamp（同 P1）；NaN/负值 fail-closed 抛错（好）；market_adjustment 先 clamp ±10 再合成（:122-125），越界调节静默收编——合同只说"调节越界抛错"（docstring :107）与实现 clamp 矛盾（同 P1 族，测试 :66-74 固化 clamp） | sector_strength_aggregator.py:107 vs :125 | P3（并入 P1 修） | `aggregate_sector_strength("X",50,50,50,50,market_adjustment=50)` → adj=10 不抛 |
| E | 幂等/时序：纯函数无状态，重跑安全；无墙钟（测试 :138-140 固化）；无竞态面 | sector_strength_aggregator.py 全文 | —（已查无） | test_deterministic/test_no_wall_clock |
| F | **对等已有**：板块动量/相对强度排序取 Top-N 是成熟范式——本件"composite 降序 Top-15% 候选池"与业界 sector momentum rotational 策略同构；等权 0.25×4 最大熵先验+显式可注入+待 IC 重校路线与无 IC 起步惯例一致 | Quantpedia《Sector Momentum – Rotational System》（quantpedia.com，发布方 Quantpedia，2020 年前后收录）；SSRN《Dynamic Sector Rotation Strategy》（papers.ssrn.com/abstract=4573209，2023）；SSGA《Sector Momentum Map》（ssga.com，机构洞察） | 对等已有 | 访问上述 URL 对照 Top-N sector momentum 定义 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| Top-15% 板块强度候选池 | **对等已有**：sector momentum Top-N 轮动为业界标准做法，本件同构且参数（15%/ceil/保底1）显式可配置 | [Quantpedia — Sector Momentum Rotational System](https://quantpedia.com/strategies/sector-momentum-rotational-system)，Quantpedia；[SSRN 4573209 — Dynamic Sector Rotation Strategy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573209)，SSRN，2023；[SSGA — Guide to Sector Momentum Map](https://www.ssga.com/nl/nl/intermediary/insights/guide-to-sector-momentum-map)，State Street |
| 四路等权 0.25×4 先验 | **对等已有**：无 IC 证据时等权为最大熵标准起步，IC 积累后加权校准路线正确（自述 :27-29）；无需立卡 | 同上 + 本件 :8 |
| A 股语境板块合成特有处理（涨停分档映射高潮分） | **驳回立卡必要**：属项目自有口径（sector_breadth 既有分档），业界无可直接对照项，保留现状 | sector_strength_wiring.py:50-57 |

## 4 缺陷清单（按严重级排序）

1. **P1｜输入上界缺失+ERROR_CONTRACT/INVARIANTS 与实现矛盾**（越界声明 fail-closed 实则 clamp 放行；调节越界同病）
   - 现状：`_validate_score` 只查 `fv < 0` 与非有限；>100 通过；composite clamp 吞信息；输出子分与 composite 不自洽；docstring :107 承诺"调节越界抛错"但实现 clamp。
   - 证据：sector_strength_aggregator.py:8、:76-82、:107、:125、:127；test :66-78 固化了 clamp 行为。
   - 影响与爆炸半径：绕过 wiring 的调用方注入原始分（0-100 契约外）→ composite 静默扭曲排序 → 候选池成员错 → 板块候选决策偏移（P1 决策链）；契约文档失效会误导后续施工。
   - 建议修法：二选一并全链对齐——(a) 上界 100 显式 fail-closed（改 INVARIANTS 兑现）；或 (b) 声明改为"越界 clamp+输出保留原值"并把测试注释升级为契约条款；同时修 :107 调节越界措辞。
   - 验证法：`python -c "from zephyr.signal_ashare.core.sector_strength_aggregator import aggregate_sector_strength as f; s=f('X',150,50,50,50); print(s.structure_score, s.composite)"` → 150 75（不抛错）。
2. **P2｜整条 L2-01 生产链无最终触发者**（wiring 无生产调用方）——通电前本件对决策零影响，通电时必须带链路集成测试（含 0-100 契约保障依赖 wiring 归一的断言）；验证法=grep wire_from_report。
3. **P3｜build_sector_strengths 裸 KeyError 违反自家 ERROR_CONTRACT**：包一层 SectorStrengthInputError；验证法=缺键 dict 调用观察异常类型。
4. **P3｜小截面 ceil 放大+平票名字序**：登记口径备忘（非缺陷，防"Top-15%"字面误解）；验证法=N=7 输入数池子。
5. **P3｜weights 长度非 4 无显式校验**（靠归一检查兜底）；验证法=2 元 weights 报错文案。

## 5 挂起疑问

- **他会话在途**：tests/signal_ashare/test_sector_strength_aggregator.py（untracked，0 字节）与已入库 sector/ 版同名并存——收口时若他批落库同名文件将产生两份承载（checklist#4），须裁定保留哪份。
- wiring 层 `_percentile_scores` 的 rank 归一公式（平均秩/竞争秩？并列如何处理）未在本对象边界内深审——建议该件单独过审时查并列秩口径（与 S02 平票名序衔接）。
- `sector_ecology_judge`（MOD-SIG-143）为他会话在途伴生件，未审。

## 6 完备性自评

- 六轴全查：是（F 轴 3 条对照，2 条带 URL）。
- 长尾：①wiring 适配层深审（建议单列对象）；②sector_ecology_judge；③L2-01 地图节点锚点原文核对。
- 变更热力：2 commits（创建+src 平铺重构搬家，无算法返工史）=低危。
- 测试审查结论：信任（24 断言强度足够、无日期依赖；一处把越界 clamp 固化为预期需随 P1 修复同步改）。
- 在途干扰备注：他会话 3 个 untracked 测试文件按现状审，其中本对象同名测试为空文件，不影响本轮结论。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
