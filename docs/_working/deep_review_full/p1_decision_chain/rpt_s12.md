---
ttl: task_bound
doc_type: report
title: 深度审查报告——市场生命周期相位（S12）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：市场生命周期相位（S12）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/market_lifecycle_phase.py:97`（LifecyclePhaseConfig 相邻）/ `:180`（detect_lifecycle_phase 主入口）/ `:321`（sense 加载封装）
- 生产调用方: **零**（grep detect_lifecycle_phase/MarketLifecyclePhaseSensor 全仓 src/scripts 仅自身；calendar_effects_model.py:26 仅 docstring 分工声明，非 import）
- 测试文件: tests/signal_ashare/test_market_lifecycle_phase.py（17 用例，已审）
- 备注: header :7 MATURITY=production 与 :5 "待下游风控节流层"矛盾——本批第 5 例标签漂移（S03/S05/S08/S11 同族）

## 1 对象快照

- **范围**：`market_lifecycle_phase.py` 全文 330 行——板块新高占比快慢线（5/20）× 水位阈（10%）2×2 → 春夏秋冬 4 相位 + 季节约束（冬禁抄底/秋强制离场）+ 置信度（含指数 MA60 一致性调整）；纯函数与 DB 加载隔离。
- **排除项**：market_sector_kline/market_index_kline 表本体；情绪周期（28 号）/regime（10 号）兄弟件（边界消歧声明 :30-33 仅核对声明存在）。
- **测试覆盖概况**：17 用例。信任度：**信任（盲区=序列对齐与断档）**。
- **材料包缺项声明**：无运行时证据包；板块新高占比真实分布未画像。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 新高定义自洽但**等值并入语义未文档化**：窗口含当日 → `close >= window_max` 中 close==max 即新高（并列新高计数）——整理期/同值期并列新高会系统性抬高占比（分母不变、分子虚增）；与 S05 波动率分位"常数序列=1.0"同族语义，本件未见文档声明 | market_lifecycle_phase.py:155-156、:166-168 | P3 | 构造多板块同值序列 → 占比=1.0 → SUMMER（高水位上行） |
| A | **closes 与 nh_ratios 无日期对齐校验**：指数一致性调整用 `closes[-1] >= ma(closes,60)`，与 nh 序列末端日期可以错期（两序列独立加载独立截尾）——错期比较时一致性 ±0.1 调整失去意义且无告警 | market_lifecycle_phase.py:222-227、:275-296（两腿独立加载） | P2 | 假 query_fn 让 nh 截至 T、index 截至 T-90 → 无告警出快照 |
| A | 2×2 分类完备封闭（4 象限全覆盖、约束映射封闭）；边界 slow==0.10 判高位与 docstring "≥10%" 一致；置信度公式有界 ∈[0,1]（0.4+0.6·base 封顶、±0.1 后 clamp）——数学主链健全 | market_lifecycle_phase.py:134-146、:216-228 | —（已查无，正面） | test 文件四季用例 |
| A | compute_nh_ratio_series 按注入序处理（**升序契约未校验**：乱序注入时 trailing 窗口错乱静默出错误占比） | market_lifecycle_phase.py:153-169 | P3 | 乱序 rows 注入 → 对照升序结果差异 |
| A.3 | 测试盲区：无错期对齐用例（P2-1）、无乱序注入用例、无等值新高用例；17 用例覆盖四季映射/约束/置信度契约 | tests/signal_ashare/test_market_lifecycle_phase.py | P3 | 补用例（收口方施工） |
| B | **SQL .format 字符串插值**（同 S05 病）：违反"参数化查询禁 f-string 插值"项目约定（对照 S04/S10 合规例）；start/end/symbol 可注入 | market_lifecycle_phase.py:70-80、:281、:305-307 | P2 | 对照 S04 mainline_probability.py:97 参数化模式 |
| B | **loader 丢日期列+无新鲜度检查**（同 S05 病）：load_nh_ratio_series 返回纯占比序列（日期抛弃）、index end 默认 2099——断更时拿旧数据照常出季节判定并驱动"秋季强制离场"类约束——**约束型输出配 stale 数据=错误禁为/放行**，checklist#6 正中且本件输出语义（禁为约束）放大了后果 | market_lifecycle_phase.py:275-296、:302、:321-330 | **P2** | 假 query_fn 返回半年前数据 → 无告警出 constraint |
| B | 断供正面：查询空 → MarketLifecycleDataError fail-closed（含 nh 序列空二次检查 :294-295，比 S05 多一道） | market_lifecycle_phase.py:291-295 | —（正面） | test 文件空查询用例 |
| C | **孤儿裁定**：生产调用方=0（calendar_effects_model 仅 docstring 提及分工）；下游风控节流层（消费 forbid_bottom_fishing/force_exit 的"禁为"约束）未接线——**约束型输出无人消费=当前对决策链零影响** | 全仓 grep 零调用方；market_lifecycle_phase.py:5、:7 | P2 | grep 命令实录 |
| C | 爆炸半径预判：接线后本件输出直接是**禁为约束**（冬季禁抄底/秋季强制离场）——错季判定的后果是"该抄底被禁/该离场未离"，比一般状态描摹更重；接线时 confidence 门槛与约束触发条件必须显式定义（当前无"低置信不出约束"机制——confidence 0.3 也照样发 force_exit=True） | market_lifecycle_phase.py:141-146、:230-237 | **P2** | 造低置信输入 → constraint 仍 full 发放（无门槛） |
| D | 三兄弟边界消歧声明清晰（情绪周期 28 号/regime 10 号/本件：输入源×时间尺度×消费方式三维区分，:30-33）——文档级防混用正面记录；**但 S05 与 S12 为同构复制模板**（load_index_closes/_resolve_query_fn/_resolve_table/SQL 构造近乎逐行相同）——模板级双承载（checklist#4）：S05 的 P2 类发现（.format/stale/丢日期）在本件全部复现即是证据，建议抽共享 loader 基类 | market_lifecycle_phase.py:30-33、:298-319 vs market_state_sensor.py:304-342 | P3 | diff 两文件 loader 段 |
| E | 静默失败面：stale-data（P2-1）+ 错期对齐（P2-2）为主；坏行 warning 跳过（同 S05）；幂等纯函数 ✓——已查无其余 | market_lifecycle_phase.py:283-290 | P2（并入 P2 族） | — |
| E | 时序：PIT 由 SQL ≤end 控制（end 默认 2099=不过滤）；days_in_season 逐日重建（:207-214）O(n·window) 可接受；无墙钟——已查无 | market_lifecycle_phase.py:205-214 | — | — |
| F | 市场生命周期四阶段（春夏秋冬） | **受阻**：检索额度已尽；知识注不作实证：与 Stan Weinstein 四阶段（Stage 1-4 base/advance/top/decline）同构的高水位×趋势 2×2 规则化变体；"新高占比"作为宽度指标是 dissecting breadth 的常见做法 | 本战役检索记录 2026-09-18 | 收口方可补检"Stan Weinstein stage analysis market breadth" |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 四阶段生命周期 2×2 规则化 | **受阻**（额度已尽；与 Weinstein 阶段分析族同构的知识注不作实证） | 本战役检索记录 2026-09-18 |
| 板块新高占比（new-high breadth） | **受阻**（同上；口径自洽性已在本报告轴 A 核验） | 本战役检索记录 2026-09-18 |
| 阈值初拟+实盘标定纪律 | **对等已有**（0.10/5/20/60 显式声明待标定，与全域"初拟阈值"惯例一致） | 本件 :35 自述 |

## 4 缺陷清单（按严重级排序）

1. **P2｜约束型输出无置信度门槛 + stale/错期数据静默（三合一）**
   - 现状：force_exit/forbid_bottom_fishing 全置信度发放（无门槛）；序列无新鲜度检查（end=2099）；两腿无日期对齐校验。
   - 证据：market_lifecycle_phase.py:141-146、:222-227、:302、:275-296。
   - 影响与爆炸半径：接线后本件是**唯一发"禁为约束"的传感器**——旧数据/错期数据下"秋季强制离场"误发或该发不发，直接约束下游操作（本批语义最重的一件，虽然当前未接线）。
   - 建议修法：(a) 约束发放加 confidence 门槛（低置信 → constraint 全 False + notes）；(b) 加载后校验两腿末端日期一致且距今 ≤N 日；(c) SQL 参数化；(d) 保留日期列。
   - 验证法：假 query_fn 旧数据/错期数据复跑 sense 观察无告警出约束。
2. **P2｜SQL .format 插值违反项目约定**（同 S05）；验证法=对照 S04 参数化模式。
3. **P2｜孤儿未接线+MATURITY=production 标签漂移（第 5 例）**；验证法=grep。
4. **P3｜S05/S12 loader 模板级复制**：抽共享基类或加双件对账测试（本件发现多为 S05 同族复现的根因）；验证法=diff 两 loader 段。
5. **P3｜等值新高并入/乱序注入未校验**；验证法=§2 对应行。

## 5 挂起疑问

- 下游"风控节流层"（消费季节约束的层）在地图/规划中的形态——当前不存在，接线设计时须带本报告 §4.1 门槛要求。
- 90 号备忘录 §22.4 真源原文与 2×2 边界（≥10%、快慢线 5/20）一致性未逐条核。
- high_window=250 的新高窗口与板块成分变动（指数调样）的交互未考虑（成分变更日伪新高/伪非新高）。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记）。
- 长尾：①90 号 §22.4 原文核对；②风控节流层接线设计（未存在）；③板块成分变更对新高占比的影响画像。
- 变更热力：4 commits（创建+搬家+锚点批），无算法返工=低危。
- 测试审查结论：信任（17 用例四季映射+约束+契约覆盖好；盲区=对齐/stale，恰为 P2 族所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
