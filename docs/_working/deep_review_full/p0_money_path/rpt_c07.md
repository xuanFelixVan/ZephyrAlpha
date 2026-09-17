---
oid: C07
title: VolTargetAllocator（vol_target_allocator MOD-BT-082，L1 大盘总闸；生产接线状态=显式审查项）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C07 vol_target_allocator（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/pf_alloc/core/vol_target_allocator.py:32`（vol_target_weight）、latest_weight:80、kelly_full_weight:85。
- 显式审查项结论：**生产接线状态=孤儿死码确认**（checklist#8，同族案例 wyckoff d57b379558 / pf_alloc d9c5f4bb12）。
- 排除项：无（96 行全读）。
- 测试覆盖：tests/pf_alloc/test_vol_target_allocator.py 13 passed（1.52s）——kelly 路径无 NaN 用例。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿判定（本对象显式审查项）**：vol_target_weight/latest_weight/kelly_full_weight 全仓零生产调用方（仅测试消费）；头注 [CONSUMERS]"TDM-E-L1 大盘总闸（UP-1）"无任何 import 证据，"策略工厂 E8 组装分配（未来）"自认未来时态；[STARTUP] manual。空转自建成（95f38d9cd0/ba47d30c9c 两 commit）至今 | grep 全仓零命中；vol_target_allocator.py:5-6,10 | **P1（孤儿确认）** | `grep -rn "vol_target_allocator\|vol_target_weight\|kelly_full_weight\|latest_weight" src/ scripts/ --include="*.py" \| grep -v test` |
| A | **kelly_full_weight NaN fail-open 到满仓**：`sigma <= 0` 对 NaN 为 False 过守卫；kelly=NaN；`min(max_weight, NaN)` 返 max_weight（首参）；`max(min_weight, max_weight)`=max_weight → **NaN σ 或 NaN E(R) 输出满仓 1.0**——与本件自declared不变量"不可测量=不满仓（窗口不足/波动率为零→min_weight）"（头注 :9）方向相反 | vol_target_allocator.py:85-96（:92 sigma<=0; :94 clamp 链） | **P1** | 实测：`kelly_full_weight(0.10, float('nan'))` → 1.0；`kelly_full_weight(float('nan'), 0.20)` → 1.0 |
| A | vol 路径 NaN 方向正确：pd.to_numeric coerce→NaN；rolling 全窗含 NaN→std NaN；0 波动 replace NaN；两级 clip 后 fillna(min_weight)——**NaN/窗口不足/零波动→min**，fail-closed 自洽 | :52-67 | 已查无 | 实测含 NaN 序列 latest=0.0（min=0 时） |
| A | 数学四问：K=target_vol/realized_vol 年化口径正确（std×√244）；EWMA span=5 平滑后二次 clip 抑换手；负收益率不影响（vol-only）；kelly_full=E/σ²×0.5 公式正确（含负 E→clamp min 正确） | :52-96 | 已查无 | 公式复核+13 测试 |
| A.3 | 测试审查：13 用例覆盖边界/平滑/零波动；**kelly 路径 NaN/Inf 零用例**——正是 fail-open 漏网点 | tests 文件 | P2（缺口） | grep nan 于测试文件 |
| B | 输入追源：returns/target_vol/预测 E(R)、σ 全由调用方注入——调用方不存在，契约悬空；车道 E 分布预测（σ 来源）质量无法终判 | 函数签名 | 随孤儿 | grep |
| C | 下游：零消费方→爆炸半径当前为零；"L1 大盘总闸"若按头注意图复活，NaN 洞=总闸在预测断供日满仓放行 | 同上 | 随 P1 | 同上 |
| D | 兄弟对查：①年化常数漂移——本件 ANNUALIZATION=244 vs regime_meta_allocator.TRADING_DAYS=252（同 pf_alloc 域内"年化交易日"两个真源）；②Kelly 第三处实现（另见 rpt_c04 §2 D）——三处 Kelly 无共享工具，本件 fail-open、C04 fail-noisy、口径各自为政；③头注 [DOMAIN] D_BACKTEST 但文件置于 pf_alloc/core/（域归属与物理路径不一致） | :29 vs regime_meta_allocator.py:90 | P2（合并/统一建议） | 两常量对照+grep |
| E | 静默失败面：NaN 满仓即静默失败点；latest_weight 空序列裸 IndexError（:80-81 iloc[-1]） | :79-81 | P3 | `latest_weight(pd.Series([],dtype=float))` → IndexError |
| E | 重复触发/时序：纯函数无状态无 IO 无 datetime.now（头注不变量，代码核实成立）——幂等天然成立 | 全文 | 已查无 | 阅读 |
| F | （见 §3） | | | |

## 3 SOTA 对照

- 波动率目标化（vol targeting）：**对等已有**——低波加仓/高波减仓改善风险调整收益、降低尾事件概率为既有实证结论。来源：[Quantpedia: An Introduction to Volatility Targeting](https://quantpedia.com)；[Alpha Architect: Volatility Targeting Improves Risk-Adjusted Returns](https://alphaarchitect.com)；[ECB FSR 2020](https://www.ecb.europa.eu/press/financial-stability-publications/fsr/focus/2020/html/ecb.fsrbox202005_02~f6616db9be.en.html)（负反馈面）。
- 快慢估计器选择：EWMA span=5 属快估计器，对齐"regime 切换期反应过慢=持续超险"的告诫（vol switching）。来源：[Man Group: Volatility is Back](https://www.man.com)（man.com）；[Quantpedia](https://quantpedia.com)（fast vs slow estimator）。
- 完整 Kelly 扩展（K=f×E/σ²）：公式对等（与 C04 同族，half 分数 0.5 一致）；**业界警示**：Kelly 对 E 估计误差极敏感、须分数化+保守缺省（本件 NaN 缺省方向违反此教训）。来源：[Wikipedia: Kelly criterion](https://en.wikipedia.org/wiki/Kelly_criterion)；[Matthew Downey: Why fractional Kelly](https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size.html)。
- 深度 2024-2025 学术对照（regime-switch+shrinkage 组合）检索 429 限流**受阻**，如实记。

## 4 缺陷清单（按严重级）

1. **[P1] 孤儿死码确认（显式审查项裁定）**。现状：零生产调用方，"L1 大盘总闸"消费关系无代码证据。影响：维护税+复活即踩 NaN 满仓洞。建议修法（三选一，Owner 裁定）：①登记退役（E8 未立项前）；②挂"预留死码"标记+MATURITY 降 experimental+头注绑定 E8 立项号；③接入 TDM-E-L1 真实链路。验证法：§2 C 行 grep 原样重放。
2. **[P1] kelly_full_weight NaN→满仓**。修法：入口 `math.isfinite(sigma) and math.isfinite(expected_return)` 否则 return min_weight（对齐本件"不可测量=不满仓"自declared语义）。验证法：§2 A 行两条单行复现，修复后应返 min_weight。
3. **[P2] kelly 路径测试 NaN 盲区**：补 NaN/Inf→min 断言。
4. **[P2] 年化常数 244 vs 252 域内漂移 + 三处 Kelly 实现无共享**：建议统一年化真源常量+Kelly 工具函数收敛（登记挖矿合并建议）。
5. **[P3]** latest_weight 空序列 IndexError；[DOMAIN] D_BACKTEST 与物理路径 pf_alloc/core 不一致。

## 5 挂起疑问

1. "TDM-E-L1 大盘总闸"消费关系是规划态还是曾接线后脱落（git log 仅 2 commit 均为建成，无脱落痕）——倾向从未接线，请 Owner 确认后走退役或立项。
2. ANNUALIZATION=244 的选择依据（A 股均值口径 243-244 vs 252）未在文件内留证——两常数统一时需裁一个。

## 6 完备性自评

六轴全查（对象仅 96 行，覆盖完整）。长尾：TDM 升级蓝图（708342357f 批准件）原文未取，E8/L1 规划意图按头注转述。
