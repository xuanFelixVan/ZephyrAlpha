---
ttl: task_bound
doc_type: report
title: 深度审查报告——粗筛漏斗（S08）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：粗筛漏斗（S08）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/screening/coarse_screening_funnel.py:44`（CoarseScreenConfig）/ `:84`（screen_coarse 主入口）
- 生产调用方: **零**（grep screen_coarse/CoarseScreenRecord 全仓 src/scripts 仅自身；tiered_screening_filter/screening_funnel_report 仅 header 注释提及）
- 测试文件: tests/signal_ashare/screening/test_coarse_screening_funnel.py（10 用例，已审）
- 备注: 与 S03 同批设计态漏斗件（f5be8921db 波次3）；header :7 MATURITY=production 与 :5 "未接线"矛盾（同 S03 病）

## 1 对象快照

- **范围**：`coarse_screening_funnel.py` 全文 132 行——五维布尔/门槛式初筛（~1200→~300）+ liquidity 容量截断；纯函数。
- **排除项**：BM-SEL-02/03/05 与 C-011/C-021 上游布尔产出方（注入式契约）；fine_scoring_engine（S03 已审）。
- **测试覆盖概况**：全过/逐维排除/量比与板块边界/容量截断/同分确定性/capacity 契约/降级直通/空输入。信任度：**信任（盲区=缺数据默认放行语义）**。
- **材料包缺项声明**：无运行时证据包；无数据画像（纯函数）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **缺数据默认放行（fail-open）**：字段默认值即"通过"——volume_ratio=999.0>1.5 过、turnover_rate_pct=999.0 过、sector_strength_rank_pct=0.0（0=最强档！）≤0.30 过、三布尔默认 True 全过。上游任一维断供/调用方漏填 → 该股**静默全过五关**进精筛，与 excluded/notes 无任何留痕——**checklist#6 断供问句的正答反面：断供时恒通过而非恒 0 或报错**（S04 资金腿断供→缺维降级、S01 缺数→missing 计票，全域 fail-closed 基调下本件唯一 fail-open） | coarse_screening_funnel.py:64-71（默认值）、:104-121（门槛判定） | **P1** | `screen_coarse([CoarseScreenRecord(symbol="X")])` → kept=("X",) 且 excluded={}（零字段股票全过五关，无任何标记） |
| A | 门槛严格性混用无文档：量比 `<=` 排除（恰 1.5 排除）、换手 `<` 排除（恰等于下限通过）、板块排名 `>` 排除（恰等于上限通过）——三档语义各异且 docstring 未声明 | coarse_screening_funnel.py:107-114 | P3 | test_volume_ratio_boundary/test_sector_rank_boundary 已固化行为（:44,:50）但无统一约定说明 |
| A | 容量截断数学健全：liquidity 降序+symbol 升序决胜（确定性 ✓，:125）；被截断不入 excluded（语义区分规则排除 vs 容量淘汰，:93-94 已声明 ✓）；truncated 标志独立（:81） | coarse_screening_funnel.py:123-131 | —（已查无） | test_over_capacity_truncated_by_liquidity / test_same_liquidity_deterministic_order |
| A | 重复 symbol：kept 元组可含重复、excluded dict 键覆盖——漏斗上游应唯一，无去重防线 | coarse_screening_funnel.py:101-128 | P3 | 双同 symbol 输入 → kept 两同名 |
| A.3 | 测试盲区：无"缺字段默认放行"用例（P1 正中盲区——`CoarseScreenRecord(symbol=...)` 最小构造恰是 fail-open 展示）；边界已有两处 ✓ | tests/signal_ashare/screening/test_coarse_screening_funnel.py:21（test_all_pass_kept 用显式全过字段，未测零字段） | P2（随 P1 修复补测） | 最小构造记录跑一遍即证 |
| B | 输入五维为上游布尔/标量注入：**无"未知/缺数"表达**（布尔无 None、标量用 999.0 哨兵非语义化）——上游隐式契约"必须先算好再注入"未文档化，缺数表达缺失是 P1 根因 | coarse_screening_funnel.py:60-72 | P2 | 对照 S04 SectorFactorInput 的 None=缺数设计 |
| C | **孤儿裁定**：生产调用方=0；漏斗三层（SIG-046/047/048）全链未通电（S03 同判）；header :7 MATURITY=production 名不符实（:5 自认未接线）。**MATURITY 标签漂移第 3 例**（S03/S05/S08 同族——建议收口方一并治理） | 全仓 grep 零调用方；coarse_screening_funnel.py:5、:7 | P2 | grep 命令实录 |
| C | 下游消费语义：degraded=True 全量放行时"算力风险告警由调用方负责"（:25）——告警义务转嫁且无接口承载（无 callback/返回告警通道），接线日易漏 | coarse_screening_funnel.py:25 | P3 | 接线施工单验收项 |
| D | 兄弟件：tiered_screening_filter（MOD-SIG-046 第一层）与 screening_funnel_report——三层漏斗架构分工清晰无重复实现；本件与 S03 共同构成 L2→L3 交接（kept symbols→精筛记录），交接字段契约（symbol→FineScoreRecord）无集成测试 | coarse_screening_funnel.py:4-5 | P3 | 审接线批的漏斗全链测试 |
| E | 静默失败面：P1 即主静默面；truncated 标志存在但无告警通道；幂等纯函数确定性 ✓——其余已查无 | coarse_screening_funnel.py 全文 | P2（并入 P1 治理） | — |
| F | 门槛式初筛+流动性容量控制 | **受阻**：检索额度已尽；知识注不作实证：量比/换手/板块排名门槛初筛是选股漏斗常见做法，流动性截断为工程约束非学术口径 | 本战役检索记录 2026-09-18 | 可选补检 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 多维门槛初筛漏斗 | **受阻**（检索额度已尽；工程范式无争议） | 本战役检索记录 2026-09-18 |
| 容量截断确定性排序 | **对等已有**：确定性排序（-liquidity, symbol）与项目全域 tie-break 约定一致（内部约定自洽） | 本件 :125 |

## 4 缺陷清单（按严重级排序）

1. **P1｜缺数据默认放行（fail-open），断供静默全过**
   - 现状：五维字段默认值=通过值；上游断供/漏填 → 股票无痕通过初筛；无"缺数"表达。
   - 证据：coarse_screening_funnel.py:64-71、:104-121；最小构造验证法在案。
   - 影响与爆炸半径：接线后上游任一布尔腿断供 → 漏斗第二层静默失效（~1200 全量过闸）→ 精筛算力超载+垃圾候选进决策卡；"漏斗变直通"不报错（checklist#6 D10 同族：断供不改行为只改质量）。
   - 建议修法：(a) 布尔改 `bool | None`（None=缺数→记 excluded["dim:missing:*"] 或独立 missing 计数）；(b) 标量删除 999.0 哨兵改 None 显式缺数；(c) 缺数超阈值 → 触发 degraded 语义；(d) 补零字段用例。
   - 验证法：`python -c "from zephyr.signal_ashare.screening.coarse_screening_funnel import *; r=screen_coarse([CoarseScreenRecord(symbol='X')]); print(r.kept, r.excluded, r.truncated)"` → `('X',) {} False`。
2. **P2｜MATURITY=production 标签漂移（第 3 例，与 S03/S05 同族）**：改 design/testing 或接线；验证法=header 两行对照。
3. **P3｜门槛严格性三档混用**：统一约定或文档化；验证法=边界测试对照。
4. **P3｜重复 symbol 无防线**；验证法=双同名输入。
5. **P3｜degraded 告警义务转嫁无承载**；验证法=接线施工单。

## 5 挂起疑问

- 21 号 memo §3.6 ② 原文的五维门槛定义与本件阈值（1.5/0.30/300）一致性未逐条核（收口方抽查）。
- 量比 999.0 哨兵是否曾为"上游无法计算"的约定值（若是，P1 修复时须同步上游装配层）。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记）。
- 长尾：①memo 原文核对；②三层漏斗全链接线设计审查（尚未存在）；③上游 BM-SEL-02/03/05 布尔产出方本体。
- 变更热力：6 commits 全为锚点/搬家/表头诚实化（与 S03 同族治理性变更），无算法返工=低危。
- 测试审查结论：信任（边界与确定性覆盖好；盲区=最小构造 fail-open，恰为 P1）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
