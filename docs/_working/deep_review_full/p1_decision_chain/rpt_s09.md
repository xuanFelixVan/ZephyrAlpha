---
ttl: task_bound
doc_type: report
title: 深度审查报告——趋势线支撑压力（S09）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：趋势线支撑压力（S09）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/trendline_sr_detector.py:63`（TrendSRConfig）/ `:190`（analyze_trend_sr 主入口）
- 生产调用方: strategy_signal/unified_pattern_engine.py:717（支撑阻力腿收编）；叠加层渲染位（GAP-F-33 指数详情页）未接线
- 测试文件: tests/signal_ashare/test_trendline_sr_detector.py（10 用例，已审）
- 备注: MVP 规则版自认初拍值待标定；颗粒度裁定（复用 regime 不成立）留痕在 header :20-23

## 1 对象快照

- **范围**：`trendline_sr_detector.py` 全文 274 行——分形极值（±k 满窗）→ 价位聚类（容差%）→ 支撑/压力（现价下方/上方最近位）→ 趋势线（最近两同向极值连线）；纯函数观测层。
- **排除项**：unified_pattern_engine 消费侧（仅核调用点 :717）；regime_detector（MOD-REGIME-001，复用裁定已核查不成立）。
- **测试覆盖概况**：聚类触点/支撑压力方位/日期附着/单侧缺位/两向趋势线/不足降级/无极值/契约拒绝/JSON。信任度：**信任（盲区=NaN 与 max_levels 截断交互）**。
- **材料包缺项声明**：无运行时证据包；真实指数序列的聚类容差敏感性未画像。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **NaN 价格穿透 fail-closed 契约**：校验 `float(v) <= 0` 对 NaN 为 False → NaN high/low/close 全部放行 → 分形判定 `== max(...)` 恒 False → 输出空 levels+notes"无分形极值"，与"价格非法→ValueError"的 ERROR_CONTRACT :13 不符（静默降级非 fail-closed） | trendline_sr_detector.py:210-212、:13 | P3 | `analyze_trend_sr([SRBar("d1",float("nan"),1.0,1.0)]*5)` → 无异常、degraded=False、空 levels |
| A | **support/resistance 在 max_levels 截断之后选取**：levels 先按触点数降序截 10 再选最近位——若最近支撑因触点少被截掉 → support=None 或错位（"最近位"语义让位于"触点数 Top10"语义） | trendline_sr_detector.py:236-242（截断 :237 在选取 :239-242 之前） | P2 | 构造 11 个位：远端高位多触点+近端少触点被截 → support 与全量计算结果不一致 |
| A | 聚类为顺序贪心（按价格排序+运行均值容差）：链式合并可能（A 吸 B 后均值移向 C）且均值在插入前计算——确定性有保障（排序键固定），但聚类结果对容差敏感、非全局最优；MVP 可接受 | trendline_sr_detector.py:141-151 | P3 | 容差 1.4/1.5/1.6 三档对照聚类数 |
| A | 趋势线仅取**最近两个**同向极值，斜率不合即放弃（不回溯更早锚点对）——"最近两低点斜率非正，上升趋势线不出"（notes 留痕 ✓）。真实指数常见"最近两低点走平但更早两点成线"场景漏报——MVP 声明一致，登记局限 | trendline_sr_detector.py:248-265 | P3（已声明局限） | 构造三低点（前两点成线、后两点走平）→ 无 uptrend 线 |
| A | 角色反转处理正确：低点簇整体高于现价 → 判 resistance（:231-234），符合支撑压力互换惯例；单侧缺位 None+notes 不硬编（:243-246 ✓ 兑现 INVARIANTS） | trendline_sr_detector.py:230-246 | —（正面） | test_no_level_one_side |
| A | 分形判定严格不等+唯一性（count==1）→ 并列极值都不判（宁缺勿伪）——与满窗策略一致，保守正确 | trendline_sr_detector.py:129-132 | —（正面） | 双同高序列无分形 |
| A.3 | 测试盲区：NaN 用例缺（P3-1）、max_levels 截断×最近位交互缺（P2-1）、date 升序未校验也无测试；现有 10 用例对主路径与契约覆盖良好 | tests/signal_ashare/test_trendline_sr_detector.py 全文 | P3 | 补用例（收口方施工） |
| B | 输入契约：date 升序/ISO 格式为**未校验隐式契约**（dates 排序用字符串比较 :155，非 ISO 格式会乱序 first/last_date）；high/low/close 正数 fail-closed（NaN 漏洞见轴 A） | trendline_sr_detector.py:155、:197 | P3 | 传 MM/DD 格式日期看 first/last_date 乱序 |
| B | 上游断供行为：bars 不足 → degraded=True 不出伪线（:215-219 ✓ 兑现"数据不足不出伪线"）；无极值 → 空+notes——**断供语义全域最健康的一档**（checklist#6 正面样本） | trendline_sr_detector.py:215-223 | —（正面） | test_insufficient_bars_degraded |
| C | 下游：unified_pattern_engine.py:717 消费（`TrendSRConfig()` 默认配置）+ 渲染位未接线；engine 侧"testing"标注知情（头注 :4） | unified_pattern_engine.py:4、:717 | P3 | 审 engine 消费是否依赖 support/resistance 非 None（None 语义对齐） |
| C | 爆炸半径：渲染错位/pattern 事件错标，非资金路径（观测层定位缓冲） | trendline_sr_detector.py:106 | P3（定位缓冲） | — |
| D | 兄弟盘点：全仓无第二份趋势线/SR 实现（GAP-F-33 裁定独立新建留痕 :20-23，双份承载已预防 ✓）；与 S07 缠论（笔端点≈分形极值）概念相邻但算法不同源，无合并必要 | 全仓 grep；trendline_sr_detector.py:20-23 | —（已查无） | grep 实录 |
| E | 静默失败面：NaN 静默空结果（轴 A）；日期乱序静默；其余 fail-closed/degraded 路径健康；幂等纯函数 | trendline_sr_detector.py 全文 | P3 | 同轴 A 验证法 |
| F | 分形+聚类支撑压力+两锚点趋势线 | **受阻**：检索额度已尽；知识注不作实证：pivots/zone 支撑压力与趋势线是经典 TA 内容，聚类容差法与集群枢轴（clustered pivots）惯例同构 | 本战役检索记录 2026-09-18 | 可选补检"support resistance clustering algorithm" |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 价位聚类（容差%均值口径）支撑压力 | **受阻**（额度已尽；范式经典无争议） | 本战役检索记录 2026-09-18 |
| 分形满窗极值（Bill Williams fractal 同构 ±k） | **对等已有**：±k 满窗+严格不等与经典 fractal 定义一致（k=2 即标准五 bar 分形） | 经典 TA 定义（训练语料高频，非检索实证，按受阻口径附注） |
| 两锚点直线趋势线 | **对等已有**：两点连线+方向校验是趋势线最小实现；未做"多锚点最优拟合"属 MVP 声明范围 | 本件 :32-34 自述 |

## 4 缺陷清单（按严重级排序）

1. **P2｜max_levels 截断先于最近位选取**——触点少的近端位可被截掉致 support/resistance 错位/缺失
   - 现状：:237 截断在 :239-242 选取之前；"最近位"语义受"触点 Top10"约束。
   - 证据：trendline_sr_detector.py:236-242。
   - 影响与爆炸半径：复杂盘整区（位多）时指数页支撑压力渲染错位；pattern engine 消费侧若以 support 非 None 为前提则连带错标。
   - 建议修法：support/resistance 先在全量 levels 上选取，再做展示截断（两列表分离）。
   - 验证法：构造 12 个位（近端 1 触点+远端多触点）对照截断前后 support。
2. **P3｜NaN 穿透契约**：校验补 `isfinite`；验证法=NaN 输入无异常实证。
3. **P3｜date 升序/ISO 未校验**（字符串排序隐式依赖）；验证法=非 ISO 日期乱序复现。
4. **P3｜趋势线不回溯更早锚点**（已声明 MVP 局限，登记不修）；验证法=三低点构造。
5. **P3｜贪心聚类容差敏感**（登记，标定时用真实指数序列画像）；验证法=容差三档对照。

## 5 挂起疑问

- unified_pattern_engine 消费 support/resistance 的 None 处理与 distance_pct 符号约定是否对齐（engine 侧单审时核）。
- tolerance_pct=1.5 对指数点位的经验合理性（3000 点 ±45 点簇）待实盘标定（自认初拍）。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记）。
- 长尾：①engine 消费侧深审；②真实指数序列聚类画像；③与缠论笔端点的概念对照（无代码耦合，仅概念相邻）。
- 变更热力：2 commits（创建+搬家），无返工=低危。
- 测试审查结论：信任（主路径+契约+降级覆盖好；盲区=NaN/截断交互，与 P2/P3 对应）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
