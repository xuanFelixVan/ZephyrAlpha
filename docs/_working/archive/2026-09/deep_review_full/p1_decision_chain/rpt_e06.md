---
ttl: task_bound
title: 深度审查报告——分批卖出（E06）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：分批卖出（E06）

- 状态: **已审**
- 级别: P1｜类型: 卖出族分批退出（#309 挂起族"分批"档）
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- **裁定#309 约束声明**：卖出族整族挂起（ruling_registry.yaml:3833-3839）——裁定明列"分批"属依赖就绪前不启用档；本件审查照常，施工受裁定约束（当前即不应接电）。
- 入口锚点: `src/zephyr/sell_decision/core/scaling_out.py:89(simple_scaling_out)`
- 接线现状（grep 实证）：包外零导入——引用仅包内（scaling_out_architect.py、take_profit_strategy.py）+测试；族级结构性空转同 E01。
- 测试文件: tests/sell_decision/test_scaling_out.py
- 材料包缺项: 42 号 memo §3.7 原伪代码未取（工程修正声明无法对源核验）

## 1 对象快照

- 范围：三步分批退出纯函数（1/3 止盈→保本→trailing）+ 显式状态入参（ScalingOutState）+ Decimal 精确算术。docstring 自述修复 42 号 §3.7 伪代码"Step2 永不可达"病（Step1/Step2 同判 RR>=1 且 Step1 先 return）。
- 测试覆盖概况：专测在位。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 显式状态机修复了源伪代码死分支：state 双布尔入参让 Step2 可达（:122 vs :131 条件互斥推进）；无隐藏状态+幂等可重放 INVARIANT 结构性兑现 | scaling_out.py:122-137 | 已查无（正面） | state 两态×RR 三档全组合调用 |
| A | **"1/3"实为 0.33**：_FIRST_TRANCHE_RATIO=0.33（:45）非 1/3=0.333…；100 股卖 33 剩 67，与"三等分"语义差 0.33%；且 0.33×quantity 可产生非整手股数（A 股卖出的 100 股整手约束在本层无处理，执行面职责但契约未声明余量处理） | scaling_out.py:44-45, :125 | P3 | quantity=Decimal(100) → SELL 33 |
| A | **trailing 参数与 E03 盈利区一致（22/2.0）但适用相型不一致**：E06 Step3 对 RR<1（尚未达 1:1、可能微利）的持仓也直接用盈利区紧 trailing（:139-149），而 E03 同状态持仓按 phase 用亏损区宽参数（10/3.0）——同仓喂两兄弟组件得两条不同止损线（checklist #4 双承载/"同一概念两处算"模式，42 号 §3.3 一份 spec 两处实现分化） | scaling_out.py:139-149 vs stop_loss_strategy.py:193-202 | **P2** | RR=0.5 持仓分别调两组件 diff 止损线 |
| A | **降级锚点与 E03 相反（本件是正确示范）**：ATR 缺失→highest×(1−8%)（:149，锚最高收盘，结构同主路）；E03 同名降级锚 entry×(1−8%)——同一 spec 条款两处锚点分化，E06 版无 E03 的"盈利期止损悬崖"缺陷（反证 E03 P1 修法应向本件看齐） | scaling_out.py:148-149 vs stop_loss_strategy.py:182-191 | P2（并入 E03 缺陷 1） | 对照两降级分支 |
| A | risk_reward 由调用方预算（:68 契约注释）：分母 entry−initial_stop=0（保本初始止损）时调用方侧除零——本件对 NaN/inf RR 无守卫（NaN≥1.0=False 跳 Step1 安全向；inf→立即卖 1/3） | scaling_out.py:68, :122 | P3 | rr=float("inf") 构造 |
| A | Decimal 精确算术+float→Decimal(str()) 转换（:140）——金额路径无量纲尾差；highest<=0 fail-closed raise（:141-145） | scaling_out.py:140-145 | 已查无（正面） | — |
| A.3 | 专测在位；Step1 重复调用语义（state 未翻转→重复 SELL 1/3 直至 quantity 耗尽 raise）预计未测——显式状态契约的调用方纪律无护栏 | scaling_out.py:122-128 | P3 | 同 state 连调三次 |
| B | 输入校验 fail-closed（quantity/entry 非正 raise :110-119；highest 非正 raise）；atr None/≤0 降级；无静默吞点 | scaling_out.py:110-149 | 已查无（正面） | — |
| C | 下游：动作无 symbol 标识（调用方映射）；"保本 MOVE_STOP"与"trailing 价"两动作落执行面后如何与 E03 止损线合并（谁覆盖谁）无契约——接电设计缺口 | scaling_out.py:79-87 | P3 | 读动作消费契约 |
| D | 兄弟：scaling_out_architect.py（231 行四模式状态机）与本件 simple 三步法并存——42 号 §3.7 的"80/20 过渡"声明（三步法替代 4 模式捕获 85% 收益），architect 保留为 legacy/对照——双实现共存有文档理由，接电时须裁决退役否则成孤儿×2 | 包内文件对照 | P3 | grep architect 调用方 |
| E | 重放/重入：纯函数+显式状态；重放安全依赖调用方如实回放 state——state 翻转动作（SELL 后置 first_tranche_sold=True）由调用方负责，本件不产"状态更新指令"动作（轻量契约边界） | scaling_out.py:71-77, :95 | P3 | — |
| E | A 股口径：整手约束/卖出费率不在本层；T+1 对分批时序无约束（卖旧仓不受 T+1 限制，前提非当日买）——前提校验在调用方 | 设计边界 | P3 | — |

## 3 SOTA 对照

1. **分批退出/部分止盈（对等已有）**：分批止盈+保本止损+移动止损三段式是趋势跟随实践成法（ATR trailing 实证源同 E03 §3-1：Quantified Strategies ATR Bands 33 年回测，2024，https://www.quantifiedstrategies.com/；partial profit-taking 常见组合实践）；"三步法捕获四模式 85% 收益"为项目内部回测结论（arrowalgo 2026-03，42 号 §3.7），外部无同源可比（自研精简声明，诚实）。
2. **ML 出口策略（驳回对标）**：学界 ML 出口（arXiv 2506.06356《Deep Learning Enhanced Multi-Day Turnover Quantitative Trading》，2025，https://arxiv.org/html/2506.06356v1）为另一重量级路线，与 MVP 三步法不构成替代关系——本项目按 80/20 过渡取简，判"驳回即改，保留 MVP"。
3. 结论：**对等已有**；族内双实现（architect vs simple）接电时需退役裁决。

## 4 缺陷清单

1. **[P2] 与 E03 的相型参数/降级锚点双分化**——证据 ：139-149 vs stop_loss_strategy.py:182-202；影响：同持仓两止损线（早利相紧 vs 宽、降级锚 highest vs entry），42 号 §3.3 一份 spec 两处实现；建议：以本件锚点结构为准修 E03（E03 缺陷 1 同批），并抽公共 trailing 计算函数单源化；验证法：RR=0.5 同仓两组件 diff。
2. **[P3] "1/3"=0.33 与整手余量**（:44-45, :125）——建议：Fraction(1,3) 或声明余量处理归执行面；验证法：quantity=100 演算。
3. **[P3] risk_reward 无 NaN/inf 守卫**（:68, :122）——建议：isfinite 校验 raise；验证法：inf 构造。
4. **[P3] state 翻转无护栏**（:122-128）——建议：动作附带 state_after 字段或文档强声明；验证法：同 state 连调。
5. **[P3] architect/simple 双实现共存**——接电时退役裁决登记；验证法：grep architect 生产调用。
6. **[P1-族级] 结构性孤儿**——并入 E01 族级发现（#309"分批"档不启用，现状合规）。

## 5 挂起疑问

1. 42 号 §3.7 原伪代码的 Step2 死分支是否如 docstring 所述（工程修正声明对源核验）？
2. 0.33 比例是 arrowalgo 实证原值还是 1/3 的 Decimal 截断？接电前与实证报告对数。
3. architect（四模式）退役时点——裁定#309"依赖达成评审"时一并裁决。

## 6 完备性自评

- 六轴全查：是（全量逐行）。长尾：①scaling_out_architect 本体未审（legacy 对照件，建议退役前补审或直接废弃）；②42 号 §3.7 原文；③arrowalgo 实证报告产物锚。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
