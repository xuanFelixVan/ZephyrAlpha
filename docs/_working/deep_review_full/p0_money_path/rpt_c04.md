---
oid: C04
title: 仓位定位引擎（position_sizing_engine MOD-POS-001，Kelly:357）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C04 PositionSizingEngine（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/position/core/position_sizing_engine.py:379`（size:414；Kelly:357-371）。
- 范围：Kelly 半仓+13 约束级联+降级等权+组合缩放+幂等键，944 行全读。
- 排除项：RiskLimits 结构定义（shared/contracts）。
- 测试覆盖：tests/position/test_position_sizing_engine.py 68 passed（3.15s）。
- 生产接线：**size() 零生产调用方**——grep 全仓仅 position/core/__init__.py（re-export）、single_name_cap_caliber.py（常量引用）、position_audit_logger.py:244（**docstring 用法示例，非代码**）。头注 [CONSUMERS] D-EX-CORE 无 import 证据。且现行装配链（C01→StrategyBook）头注明载"粗仓位不经 Kelly；禁用 Kelly/MVO"（strategy_book.py:8）——两套 sizing 哲学并存，生产现用非 Kelly 侧。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | Kelly 公式正确：f*=(bp−q)/b，p∈(0,1) 严校验（NaN p raise），b>0，f*≤0→0（不下注）；半 Kelly=0.5×f* | :357-371,640 | 已查无（公式本体） | 公式复核+68 测试 |
| A | **veto 保持现仓路径权重漏计**：C6/C11 否决且有现仓→返回 (keep-current target, weight=0.0)；size() 累加器 +=0.0 → plan.total_exposure 漏计该仓位、cash_reserve 多计全额 | :741-749,756-764（返回 0.0）、:456-457（累加）、:836（cash_reserve） | **P0 级缺陷（因对象未接线降记 P1）** | 实测复现：nav=1e7、current 80000 股@10、ADV=1e5、p=0.6/b=1.5 → C6 veto → plan.total_exposure=0.0、cash_reserve=10,000,000，而实际持仓 8% |
| A | CRISIS 态语义未实现：MARKET_REGIME_CAPS[CRISIS]=0.05 注释"仅减仓不开新"（:114），但 _resolve_market_context 只取 cap，CRISIS 下照开新仓至 5%；"不开新"仅 defensive_only 输入承担（无人传） | :114,469-484 | P2 | 构造 market_regime=CRISIS 输入→plan 含新开 delta>0 仓位 |
| A | 预筛永不否决：_prefilter 恒 return True（:626），`is None` 死分支（:500-501）；C6 精确否决在下游补位，功能面完整但"预筛"名不符实 | :595-626,499-501 | P3 | 阅读返回路径 |
| A | 100 股整手缺失：target_qty=int(weight×nav/price) 任意股数，非 100 倍数（A 股买入须整手）；卖出零股可，买入不可 | :542,738,876 | P2（接线前必修） | 检查任意输出 target_qty%100 |
| A | NaN target_weight：过校验（`NaN<0`=False）→ min(NaN,kelly) 返 NaN → int(NaN) 抛裸 ValueError（非 InvalidPositionInputError，异常契约破坏但方向=吵断非静默） | :943-944,644,542 | P3 | 单行复现 |
| B | 输入追源：nav/price/ADV/密度预测全由调用方注入（无调用方→契约悬空）；var_95/cvar_95/market_regime 无校验（NaN var → `NaN>thr` False→静默不降——与 C02 同型 fail-open） | :434,441 | P2 | NaN var_95 单行 |
| C | 下游：无生产消费方（见 §1）；PositionSizingPlan total_exposure 错账将直接传给 D-EX-CORE（头注宣称）——接线即错账 | :298-318 | 随 P0 缺陷 | 同上 |
| D | 兄弟对查：①单票 5% 口径双基（本件=策略 NAV 占比 vs C01 符号层=组合绝对占比，同名不同基，checklist#4 味）；②Kelly 三处实现并存：本件、vol_target_allocator.kelly_full_weight（C07，NaN fail-open 更烈）、core_satellite_allocator（核心 Kelly）——三处无共享工具，口径各自维护 | :188 vs single_name_cap_caliber.py:37-42 vs vol_target_allocator.py:88 | P2（合并建议） | 三文件对读 |
| D | 双哲学并存：MOD-POS-020 StrategyBook"禁用 Kelly"（粗仓位）vs MOD-POS-001 Kelly 精裁——分层设计本可自洽（粗+精两阶段），但精裁阶段无装配点，链断 | strategy_book.py:8 | P1（随孤儿） | grep 装配点 |
| E | 静默失败：C7 硬限仅 append check 不改仓（预筛 warn）+实际减仓在 :704-708 有承载——双点分离无丢失；rescale 对 veto-kept 仓位也会缩放（"保持现仓"被 C2 打破，语义冲突） | :799-809,863-887 | P2 | veto+超总仓场景复现 |
| E | 重复触发：idempotency_key=strategy:trade_date:hash(target_weights)（:927-932）——不含 nav/price/kelly 参数，同日同权重不同 nav 两轮同键，下游若按键去重将吞掉合法重算 | :927-932 | P3 | 两 nav 构造对比键 |
| F | （见 §3） | | | |

## 3 SOTA 对照

- Half-Kelly（half_kelly_factor=0.5）：**对等已有**——业界共识 25-50% 分数 Kelly，半 Kelly 保留约 75% 复利增长、波动近乎减半。来源：[Wikipedia: Kelly criterion](https://en.wikipedia.org/wiki/Kelly_criterion)；[Ryan O'Connell Finance: Kelly Criterion](https://ryanoconnellfinance.com/kelly-criterion/)（2024/2025 维护）；[PapersWithBacktest: Kelly Criterion Position Sizing](https://paperswithbacktest.com/course/kelly-criterion-position-sizing)；[Matthew Downey: Why fractional Kelly](https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size.html)。
- Kelly 估计误差敏感性（本件 p/b 直接吃密度预测点估计）：业界警示 full Kelly 对 edge 高估极敏感→分数化+收缩是正解；本件半 Kelly+VaR/CVaR 级联方向一致。来源同上（fractional Kelly 模拟链接）。
- 参与率/冲击成本否决（C6/C11 sqrt 模型）：家族对等（Almgren-Chriss 型 sqrt 冲击模型，系数 0.1 待 G04 校准自认）——检索限流未能补 2024-2025 文献，**部分受阻**。

## 4 缺陷清单（按严重级）

1. **[P1（接线即 P0）] veto 保持现仓 total_exposure/cash_reserve 错账**。现状：实测 total_exposure=0.0 而实持 8%（§2 A 行）。影响与爆炸半径：总暴露上限（C2）按少计分母缩放→实际超限；cash_reserve 虚增→现金约束失效；下游按错账执行=静默亏钱。当前无生产调用方，故降记 P1 并挂"复活即 P0"标签。建议修法：veto-keep 分支返回该仓位真实权重（current_qty×price/nav）计入累加器，并在 C2 缩放中豁免 veto-kept 或明示缩放语义。验证法：本报告 §2 首行单测脚本原样重放，期望 total_exposure≈0.08。
2. **[P1] 零生产调用方+双哲学断链**（checklist#8）：接线决策本身需 Owner 裁定（Kelly 精裁层是否进链、与 StrategyBook 禁 Kelly 口径如何衔接）。
3. **[P2]** CRISIS"不开新"未实现；NaN var/cvar 静默不降；整手缺失；rescale 打破 veto 语义。
4. **[P3]** 预筛死分支；NaN target_weight 异常类型；idempotency key 覆盖面；is_sector_rotation 死输入（:262 定义后零引用）。

## 5 挂起疑问

1. 68 测试全绿却存在 P0 级错账路径——veto-keep 分支大概率零测试覆盖（未见专项用例），收口复核时请确认。
2. Kelly 精裁层接线路线（进 C01 链哪一层）属架构裁定，本报告只登记不断案。
3. 基线漂移：本文件在 pf_alloc 域他会话施工范围外，漂移风险低；但 single_name_cap_caliber 若随口径统一施工变更，§2 D 行需重验。

## 6 完备性自评

六轴全查。长尾：blueprint.md/31号 §2.3.4 sizing_basis 归因语义未逐条对读（抽查 basis 级联自洽）；密度预测上游（车道 E）形态未知，p/b 质量轴 B 无法终判。
