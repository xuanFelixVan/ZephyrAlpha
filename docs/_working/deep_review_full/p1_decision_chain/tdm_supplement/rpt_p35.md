---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——顺位排序
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：顺位排序（P35）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/selection_confidence.py`
- TDM 节点: TDM-E-L3-05（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；节点名"顺位排序"与文件实为"sleeve 差异化 confidence 计算器"——名实差距见 §5
- 生产调用方: **0（全仓 grep 仅自命中；头注 [CONSUMERS]"待 G08/G09/G10 sleeve SelectionResult 接线"）**
- 测试文件: `tests/signal_fundamental/test_selection_confidence.py`（17 用例，本班次实跑 17/17 绿）

## 1 对象快照

147 行纯函数模块（MOD-SIG-141，21 号 memo §3.5/§3.6）：sleeve 差异化 confidence——打板=阶段置信×信号强度；多因子=IC 共识代理（收缩登记：mean_ic/0.05 满分×(1-离散度折扣≤50%)，因子数<3→0）；事件=LLM gate×PEAD gate（|reaction|>3% 衰减 0.1）+事件类型阈值表（earnings 0.70/ma 0.75/policy 0.65/breaking 0.70，未知类型回退默认 0.7）+阈值表 validate。收缩实现/待校准均为声明诚实。测试覆盖：三路径主分支+validate。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：三路径公式均为乘法链/查表，输出 [0,1]；IC 共识代理 strength=clip(mean_ic/0.05)（负 IC→0 保守）、rel_dispersion=std/\|mean\| 封顶 1（:144-147）数学自洽；PEAD 衰减 0.1 与 P28 极端反应阈值 3% 口径一致（跨族对齐已查无漂移） | selection_confidence.py:53-54,106-109,144-147 | 通过 | 逐式手算 |
| A 深度 | **边界②实锤：Python min/max 的 NaN 语义洞——`max(0,min(1,nan))=1.0`，实测 `compute_event_confidence(nan,·)`=1.0、`compute_daban_confidence(nan,·)`=1.0、`compute_multifactor_confidence([nan×3])`=0.5——NaN 输入映射为高/中置信（fail-open）；同模块 `event_passes_confidence_filter(nan)`=False（拒绝）——同族两语义互相矛盾**；触发剧本=上游情绪/IC 管道任一 NaN → 打板/事件 sleeve 高置信放行 | selection_confidence.py:106,121-122,144-147 | P2(接线期必修) | 本班次实测四命令见 §4 |
| A 深度 | 边界③：因子数<min_factors→0.0、空序列→0.0（:138-140）共识不足不自评=正确保守；未知事件类型回退默认阈值（:93）方向=宁严勿宽声明诚实 | :93,138-140 | 通过 | — |
| B 上游 | checklist #6 断供：纯标量输入无数据源；llm_confidence/event_day_reaction 上游契约（[-1,1]% 反应）无显式校验——NaN 洞即上游契约缺口的表现；IC 序列方向（正=做多强度）未校验符号约定 | :82-109 | P3 | — |
| C 下游 | **孤儿裁定：生产零调用方**（头注"待 G08/G09/G10 sleeve SelectionResult 接线"声明诚实）；接线后 confidence 直供 SelectionResult 顺位排序——NaN→1.0 的 fail-open 在排序场景=毒股置顶，爆炸半径=基本面 sleeve 全选股面 | grep 证据 | P1(接线期)+P2(NaN) | `grep -rn "compute_daban_confidence\|compute_event_confidence" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：PEAD 阈值 3% 与 P28 extreme_reaction_pct=3.0 双处常量承载（:53 vs event_driven_screener.py:92）——**同值不同源，改一漏一漂移风险**（本件 PEAD_EXTREME_REACTION_THRESHOLD 与 P28 config 默认值无 import 关系）；事件类型阈值表（4 类）与 P28 EventCategory 六类枚举口径不同（earnings/ma/policy/breaking vs EARNINGS/MERGER/POLICY/SUDDEN/IPO/GEO）——**两处事件分类法未对齐，跨层过滤语义裂缝** | selection_confidence.py:45-50 vs event_driven_screener.py:53-60,92 | P2 | 对照两表键集合 |
| E 对抗 | 五问：①静默失败=NaN→1.0 即静默失败（无异常无日志）②假阳性=NaN 高置信放行实锤③断供=N/A④重触发幂等⑤时序=N/A | :106-147 | P2(同上) | — |
| F 新鲜度 | IC 共识代理（收缩 surrogate）为模型置信度代理的常规工程手法，声明"待 G09 接真 surrogate（AlphaSchema 路线）"留白合理；PEAD 反转门与学界/A 股实践方向一致（对照见 rpt_p28 F 轴同族检索）；**对等已有** | 对等结论（PEAD 族 URL 见 rpt_p28 §3） | 通过 | — |

## 3 SOTA 对照

- 对等已有：PEAD 门控（同 P28 结论）；IC 共识→置信度映射为工程代理无文献对照面，收缩声明诚实。
- 立卡候选：无新增（真 surrogate 为既有规划项 G09）。

## 4 缺陷清单

1. P2：**NaN fail-open 三函数洞（实测 1.0/1.0/0.5）+ 与 filter 函数 NaN=拒绝的族内语义矛盾**——建议统一 NaN→0.0（宁勿宽）或 raise；验证法：`compute_event_confidence(float('nan'),0.0)`→1.0、`compute_daban_confidence(float('nan'))`→1.0、`compute_multifactor_confidence([float('nan')]*3)`→0.5。
2. P2：PEAD 3% 阈值与 P28 双处承载+事件类型两套分类法（4 键 vs 6 枚举）未对齐——接线时统一真源（建议 P28 为真源，本件 import）；验证法=对照两文件常量。
3. P1（接线期）：零生产调用方孤儿；验证法=§2 C 轴 grep。

## 5 挂起疑问

- TDM 节点名"顺位排序"（排序语义）映射到本件（confidence 计算，无排序逻辑）是否恰当——排序承载件（SelectionResult 排序器）未见，建议收口方核对 TDM module_ref。

## 6 完备性自评

六轴全查（F 同族复用 P28 检索结论）。长尾：①多因子 IC 输入的产生方（factor 包 IC 计算器）未追源②事件类型键小写命名 vs P28 大写枚举的映射层缺失③17 测试无 NaN case。

## 7 收口裁定（收口方填）
