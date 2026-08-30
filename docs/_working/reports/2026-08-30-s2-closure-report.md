---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=report · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-30 · topic=regime_s2_closure · scope=07_trading_decision_architecture · completes_when=S2 校准专项 roadmap A1 残余四件全部闭环后归档。

# S2 校准专项收尾批次报告（roadmap A1 残余，2026-08-30）

> **上游**：[S2 walk-forward 验证报告 2026-08-29](2026-08-29-s2-walkforward-validation.md)（Owner 选项 1 裁定落产，commit c5c23036）；14 号 v0.5.3 / 13 号 v0.4.2。
> **执行范围**：① B4 全量重跑（A1+B4+A2+B1）② design_match 裁定（Owner 授权 AI 自裁定通道）③ known_data_gaps.yaml 补登 ④ 14/13 号文档回写 ⑤ 2015/2020 valuation 勘探。
> **实证环境**：ClickHouse 172.24.30.100（c1_market）；`python scripts/tests/run_phase2_validation.py`（真实数据，enable_overlay=True / enable_full_risk=True）；临时探针 .runtime/（用完即删）。

---

## 一、B4 全量重跑结果（A1/B4/A2/B1 四项）

**翻 true 前全量跑**（2026-08-30 07:29，JSON: runtime/phase2_reports/phase2_full_20260830_072935.json）：

| 验证器 | 结果 | 关键指标 |
|---|---|---|
| A1 样本充足性 | **PASS** | 3733 样本 / 4 态 / 最少态 r3=555 天（14.9%）；r1 1029(27.6%) / r2 1395(37.4%) / r4 754(20.2%)；log-lik=-17248.81；degraded=False |
| B4 转换触发 | **PASS 3/3** | S1 3/3（2015 Δ=+1d / 2020 Δ=+0d / 2024 Δ=+2d，均 trigger）；S2 三事件 design_match=false 不计分母（口径见 §二） |
| A2 过拟合 | **PASS** | IS_acc=55.7% / OOS_acc=58.1% / OOS/IS=1.042 / KL=13.05（Hungarian 全特征对齐）；IS=1918 / OOS=1815 |
| B1 概率校准 | **PASS** | ECE=5.4% / 校准误差 9.4% / 最大桶误差 13.8% / n=214 / forward=20d |
| **综合** | **PASS** | overall_pass=True |

**关键过程发现**：B4 对 design_match=false 事件在匹配前即排除（b4_transition_accuracy.py L294-307），报告中的"✗ 未触发"是排除占位符而非真实匹配结论——故翻 true 裁定前先做 walk-forward 实证探针（§二）。

**翻 true 后确认跑**（--first-batch，2026-08-30 07:44，JSON: phase2_a1b4_20260830_074431.json）：**B4 PASS(4/4, 100%)**——S1 3/3 + S2 1/1（EVT-2024-RECOVERY ✓ 触发日=2024-09-27 Δ=+3d stage=confirm）；A1 同前 PASS。regime 域测试 244 用例全绿（tests/regime/phase2 + tests/regime/features）。

## 二、design_match 裁定（AI 自裁定通道）

**裁定结论：低置信部分通过——EVT-2024-RECOVERY design_match 翻 true；EVT-2015/2020 维持 false 并补边界注记。**

**裁定过程**（裁定树：2024 命中 + 2015/2020 有边界注记 → 翻 true；三事件全未命中 → 不翻）：

1. **权威盲点识别**：B4 全量跑对三事件仅显示排除占位符，无法回答"若翻 true 是否命中"。用探针复刻 Phase2Runner._collect_daily_transitions 同参 walk-forward（train_years=5 / detect_window=60 / QE refit / 校准器启用），收集 _last_transitions 后筛三事件 ±7 交易日窗口：
   - **EVT-2024-RECOVERY**：confirm **triggered=True** 于 09-27(Δ=+3d, total=307.5) / 09-30(+4d, 325.4) / 10-08(+5d, 324.4) / 10-09 / 10-10(380.0)——**B4 ±5 窗口内 3 天命中**，confirm ∈ expected_stage。维度实证（dump ±10 窗口）：capitulation 峰值 90(10-10)→73.1(10-15)≥60；valuation 路 A 产出 80(09-13~09-30)→60(10-08 起)；fund 50-70、policy 40-80 同日在位。
   - **EVT-2020-RECOVERY**：±7 窗口全部 stage=none。trigger 卡 capitulation——主峰在 03-23 疫情底（窗口峰值 40.2@03-27），距 04-10 事件日 12+ 交易日，decayed_max（halflife=10，日衰减 ×0.933）到事件日仅 21.6，**超 halflife=10 物理极限**；confirm 卡 fund≤25 / valuation 事件日 0（§三判定为正确信号）。
   - **EVT-2015-RECOVERY**：±7 窗口全部 stage=none。capitulation 全程 0.0（主峰在 08-24~26 真实底部，距 09-15 事件日 14+ 交易日，亦超衰减物理极限）；confirm 卡 fund=0（P1-E4 跨工程项）。
2. **对照裁定条件**："至少 2024 事件命中"✅（权威 B4 口径实证 confirm Δ=+3d）；"其余两事件有边界注记"✅（事件日滞后超 halflife=10 物理极限 + fund=0 跨工程项，注记落 historical_events.yaml 行内 + 本报告）。
3. **翻 true 范围裁定**：仅 2024 翻 true，2015/2020 维持 false。理由：design_match 语义是"事件类型在当前模型设计域内且验证实证命中"——对实证未命中事件翻 true 会使 B4 变 4/6 FAIL（0.667<0.75），且标签失实；2015/2020 不命中的归因已从"设计域不符"收窄为"事件标注时点 vs 信号物理可达性"（14 号开放问题 3），维持 false + 边界注记是 design_match 机制的既定合规用法。

**低置信注记（如实登记）**：capitulation 组合 MC 置换 p=0.87 未过预注册门槛（验证报告 §三，DSR N=17 备案）；three_yang v2_index OOS 命中 0%（维持辅助维定位，strong_confirm 三事件均不可达）；S2 trigger 阶段三事件均未触发（2024 走 confirm 路径命中）。本裁定为"低置信部分通过"，非"验证通过"。

## 三、2015/2020 valuation 勘探结论

**方法**：直查 c1_market.index_valuation_daily（000300），对照生产路径 s2_valuation_score_fundamental（CAPE 分位 <10%→80/<25%→60/<40%→40）。

| 事件 | 事件日 cape_5y / cape_5y_pct | 窗口最低分位 | 判定 |
|---|---|---|---|
| EVT-2015（09-15） | 13.42 / **0.340** | 0.267（08-26 真实底部） | **0 分是正确信号**——泡沫顶急跌后 CAPE 分位仍 27-53%，未达 <25% 低估线；窗口内 <0.40 日已正确产出 40 分 |
| EVT-2020（04-10） | 13.98 / **0.448** | 0.298（03-23 疫情底） | **0 分是正确信号**——事件日已反弹两周分位回升至 45%；底部当日 0.298 已正确产出 40 分档（dump 实证 03-27~04-01 估值 40） |
| EVT-2024 对照（09-24） | 10.51 / **0.020** | 0.0003（09-13） | 深度低估实证：80→60 分产出正确 |

**结论：2015/2020 valuation 0 分非数据缺口，是"非深度低估"的正确信号。** 数据连续性 2010-2026 完整（000300 年均 ~487 行）。

**勘探附带发现的真实数据缺口**（已登记 known_data_gaps.yaml）：
1. `erp`/`erp_pct` **全表 NULL**（000300 8009/8009、000905 4047/4047 行）——ERP=1/PE−10Y 国债计算管道从未施工，路 A 的 ERP 加分项（最高 +10）不可用（2015-09/2020-04 PE≈12 估算 ERP≈5.0%/5.7%，若有可 +5~+10，但不改 confirm 判定——fund=0 才是主堵点）。条目 `index_valuation_daily_erp_not_computed`，status=accepted。
2. **同键双行**（原始 akshare_csindex 行 cape 全空 + CAPE 回填行并存，cape NULL 5138/8009）+ schema 注释列示的 399006 实际 0 行；消费端 FINAL+drop_duplicates 兜底实证有效。条目 `index_valuation_daily_duplicate_rows`，status=monitoring。

## 四、文档/配置改动清单

| 文件 | 改动 |
|---|---|
| `src/zephyr/regime/validation/phase2/historical_events.yaml` | EVT-2024-RECOVERY design_match false→true（含实证注记）；EVT-2015/2020 维持 false、注记更新为"超 halflife=10 物理极限 + fund=0 跨工程项"边界口径；头部 design_match 演变注释更新；last_updated→2026-08-30 |
| `src/zephyr/data/config/known_data_gaps.yaml` | 新增 2 条目（erp 全空 accepted / 双行+399006 monitoring），保持既有格式 |
| `docs/.../14_regime_s2_diagnosis.md`（v0.5.2→0.5.3） | §4.1 回写 capitulation 终值（precrisis_z+close_pos+pct250+decayed_max，halflife=10/lookback=20/trigger≥60 未动）+ 六层验收 + wavg/decayed_max 数值边界勘正；§4.2 回写路 A 已建成接线 + 2015/2020 0 分=正确信号 + 开放问题 2 关闭；§4.4b 回写 three_yang v2_index（d5=-15%）+ IS 12.9%/OOS 0%；§7 修订记录登记 |
| `docs/.../13_regime_phase3_engineering_plan.md`（v0.4.1→0.4.2） | frontmatter status draft→active（升级条件达成：P1-E9 完成 + B4 S2 翻 true）+ status→active 注记（含低置信注记） |

## 五、遇到的问题与处理

1. **B4 报告对排除事件显示"未触发"占位符**（非真实匹配）——通过复刻 walk-forward 的实证探针补齐证据，避免基于占位符误裁。
2. **同文件并行编辑竞态**：historical_events.yaml 首批 3 处编辑中 2 处被并发覆盖丢失（git diff 实证只剩注释块+日期），发现后串行重做并复核加载结果。教训：同一文件的多处编辑必须串行。
3. **dump_s2_scores.py 阈值陈旧**（vix 40 / 无 breadth_thrust 析取 / strong_confirm three_yang≥1）与 regime_detector 现行配置（vix 30 / keys_or_gte / three_yang≥2）不同源——本批以探针+B4 官方输出为准，dump 仅用于维度值观察；阈值同源化留待后续（非本批范围）。
4. **首次翻 true 后确认跑**因问题 2 的丢改实际跑的仍是旧 YAML（3/3），修正后重跑得 4/4——所有结论以最终 run（phase2_a1b4_20260830_074431.json）为准。

## 六、遗留事项（非本批范围）

- 2015/2020 事件标注审视（expected_stage/事件日时点 vs 信号物理可达性）→ 14 号开放问题 3，需 Owner/后续专项裁定。
- fund=0（2015 confirm 必要条件最后缺口）→ P1-E4 跨工程项。
- ERP/PB/破净率/巴菲特指标管道（二期）→ known_data_gaps 已登记。
- dump_s2_scores.py 阈值与 regime_detector 同源化。
