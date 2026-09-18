---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——PIT管理器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：PIT管理器（B05）

- 状态: **已审**
- 级别: P0｜类型: PIT 内核（PIT 失守=回测全虚的重点专项）
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/pit_manager.py:74`（PITConfig）；PITManager :134
- 生产调用方: **仅 data_handler（其自身是孤儿，见 B04）**；grep apply_embargo/as_of_join 生产消费=0。同族平行实现 `src/zephyr/data/pit_query.py` 承载真实生产查询
- 测试文件: tests/backtest/test_pit_manager.py（353 行 32 测试，本批运行全绿；含真日历 vs BDay 假期边界断言，强度高）
- 备注: 重点审 embargo 切断——结论：**能力正确但生产链路空转，且与数据层 embargo 双承载漂移**

## 1 对象快照

- 范围：as_of_join（三公理）、apply_embargo（BDay/真日历双口径）、pit_consistency_test、check_survivorship_bias、_embargo_cutoff_by_calendar。
- 排除项：pit_query.py SQL 细节（只按 embargo 口径对照）；PitUniverseProvider（B02 已审）。
- 材料包缺项声明：真实财务表 announce_date 覆盖率画像缺（CH 不可达）。
- 变更热力：14 commits，末次 2026-09-15。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **embargo 双承载漂移（pattern #4 同族）**：本件 embargo=BDay 近似或注入交易日历回数（默认 5 交易日）；data 层 pit_query.py 自带 `- INTERVAL N DAY` 自然日回退且**默认 0=不回退**。同一"PIT embargo"概念两个真源、两种日历口径、两个默认值。grep 实证 **PITQueryConfig(embargo_days=…) 全仓零调用方传值**——生产财务 PIT 查询实际 embargo=0（无隔离），而本件默认 5 闲置 | pit_manager.py:53,82,263-266 vs pit_query.py:142-147,185-193;grep "embargo_days=" 调用方=0 | P1 | `grep -rn "PITQueryConfig(" src/ --include="*.py"` 核实无传参；读 pit_query.py:142-147 默认值 |
| C | **apply_embargo/as_of_join 生产链路空转**：本件唯一潜在消费方 data_handler 是孤儿（B04 §4.1）；生产 PIT 防护实际由 engine 层 PitUniverseProvider（B02）+stk_limit PIT 行（B03）+pit_query 锚点哨兵（D1 裁定）承担。"PIT 失守=回测全虚"的守门能力在本件结构性未接线 | pit_manager.py:5（CONSUMERS=data_handler）;grep apply_embargo src/ 仅 pit_query 注释引用 | P1（结构性） | grep 见锚点；确认三处实际承载方各自在位 |
| A | as_of_join 三公理实现核验：泄漏防护 (av<=q & ev<=q) 双闸 ✓；版本对齐仅在显式 available_time 列时 dedupe keep-last ✓（未提供版本列时不做假 dedupe，语义诚实）；instrument 列名词表单真源 ✓ | pit_manager.py:161-216,59 | 通过 | test_leakage_guard/test_version_alignment_latest_available |
| A | embargo 截止数学：真日历锚定 `searchsorted(current,'right')-1` 取 ≤current 最近交易日、cutoff=锚点前第 embargo 个交易日、日历不足回退首交易日前一日、无法锚定 NaT 全拦（fail-closed）——边界完备 | pit_manager.py:95-131 | 通过 | test_holiday_not_counted_with_calendar/test_calendar_stricter_than_bday_across_holiday |
| A | pit_consistency_test 相对偏差分母=\|train\|+1e-12 单边：train≈0 时任何微小 bt 值即爆炸偏差（保守方向：宁可误报不一致）——方向安全，语义注明即可 | pit_manager.py:331-337 | P3 | test_zero_train_value_epsilon_guard 已锁行为 |
| A | check_survivorship_bias coverage_ratio 分母=全部历史标的：短窗口回测对长历史全集必然低覆盖率（指标语义偏警报器），has_delisted/missing_delisted 两字段才是判定主体 | pit_manager.py:390-407 | P3 | test_missing_delisted_flagged |
| B | 输入全靠调用方注入（纯 pandas 无库连）——trading_calendar 不注入时 BDay 近似对 A 股长假（国庆 7 天）偏松：BDay5≈自然日 7 天，cutoff 比真日历晚→放行更多近端数据（泄漏窗口略宽）；docstring 已声明"长假窗口较 BDay 更严"的对比关系 | pit_manager.py:239-243,263-266 | P2 | 同一区间分别注入真日历与 None 对比 safe 行数（测试已有断言） |
| E | NaT cutoff 时 mask=ev<=NaT 全 False → 全拦（fail-closed 正确）；data 空/缺列 raise PITError（fail-fast 正确） | pit_manager.py:127,257-260 | 通过 | — |
| A.3 | 测试审查：32 项全绿，边界（假期/空表/NaT/epsilon）断言精确到值——**信任**；缺口=as_of_join 多标的 dedupe 的 group_cols 命中多候选列（symbol+ticker 并存）场景无测试 | tests/backtest/test_pit_manager.py:46-149,286-301 | P3 | 造 symbol+ticker 双列 frame 看 dedupe 键扩展行为 |

## 3 SOTA 对照

- purge+embargo 语义：**对等已有**——与 López de Prado《Advances in Financial Machine Learning》(Wiley, 2018) Ch.7/Ch.12 的 purging（标签重叠剔除）+embargo（test 末端隔离带）定义一致；本件 apply_embargo 只做 embargo 半边、purge 半边在 cpcv.py（B09）——同库两半分置，合并使用才完整（as_of_join 补时点轴）。（来源：López de Prado, quantresearch.org；Purged K-Fold CV, paperswithbacktest.com, 2026）
- trading_calendar 注入式 embargo（禁 cron/硬日历依赖）：**对等已有**——与 qlib/开源 PIT 实现的 calendar 注入惯例一致。（来源：eslazarev/purged-cross-validation, github.com, 2020-2026 维护面）

## 4 缺陷清单

1. **[P1] embargo 双承载漂移+生产默认零隔离**：pit_query 默认 embargo_days=0 且零调用方传值，本件默认 5 交易日闲置；日历口径（自然日 vs 交易日）也不一致。建议修法：裁定单一真源（建议 pit_query 默认改读本件 PITConfig 语义并设非零默认，或强制调用方显式传——fail-closed）；统一日历口径。验证法：§2 轴D grep。
2. **[P1·结构性] PITManager 生产链路空转**：守门能力未被任何生产路径消费（data_handler 孤儿）。建议修法：随 B04 裁决一并处置（接线或明确声明本件为"库能力+测试基准"，把生产 PIT 承载点写进 ROOR/能力卡）。验证法：§2 轴C。
3. **[P2] BDay 近似长假偏松**：A 股国庆/春节窗口 embargo 放行比真日历多。建议修法：生产调用强制注入真交易日历（trading_calendar.py 已存在可接）。验证法：§2 轴B。
4. **[P3] 一致性测试分母单边/coverage_ratio 语义**：注明用途即可，不改数学。

## 5 挂起疑问

- 生产 PIT 的实际承载点有三（engine 层 universe/stk_limit PIT 行/pit_query 哨兵）+本件闲置：PIT 防护的"地图"没有单一视图——建议收口方在 ROOR 或能力卡登记四点分工，防止"以为有 manager 兜底"的错觉（本报告判定当前真实防线=引擎层+数据层哨兵，非本件）。

## 6 完备性自评

六轴全查。长尾：①pit_query.py 全文细审（归数据域对象，本报告只做 embargo 口径对照）；②真实 announce_date 数据画像缺；③trading_calendar.py 注入链未审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
