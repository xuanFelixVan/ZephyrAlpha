---
ttl: task_bound
title: 深度审查报告——个股精评分引擎（S03）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：个股精评分引擎（S03）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/fine_scoring_engine.py:52`（FineScoreConfig）/ `:146`（score_fine 主入口）
- 生产调用方: **零**（`score_fine(` 全仓 src/scripts 零调用；screening_funnel_report.py:58 仅 import FineScoreResult 类型，candidate_pool_aggregator.py:160 为"姿态镜像零 import"）
- 测试文件: tests/signal_ashare/test_fine_scoring_engine.py（14 测试，已审）
- 备注: header :7 标 MATURITY=production 与 :5 "未接线"自相矛盾（见轴 D-2）；密度要素鸭子类型契约经源侧核对无符号歧义

## 1 对象快照

- **范围**：`fine_scoring_engine.py` 全文 169 行——选股漏斗第三层（~300→~50）：四维基础加权（价值 40/动量 30/质量 20/情绪 10）×(1+状态偏移 clamp ±10%) + 主力×0.20 − 拥挤×0.10 − 密度扣分×0.15 → 横截面 Z-score → Top-N。
- **排除项**：conditional_density_predictor（密度生产方，仅核对其输出契约符号）；event_driven_screener（第四层，未接线）。
- **测试覆盖概况**：公式显式验算（含注释逐项算式）、regime clamp、拥挤/密度扣分、8 态置 0、降级等权、并列/空输入。信任度：**信任（有明确盲区：NaN/重复 symbol/值域）**。
- **材料包缺项声明**：无运行时证据包（未接线无日志）；数据画像缺（未接线无从画像）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **单条 NaN 毒化全横截面且排名静默退化为插入序**：任一记录任一字段 NaN → mean/std 全 NaN → `std < 1e-12` 为 False → 全体 z=NaN；排序 key `(-zs, -raws, s)` 中 NaN≠NaN 使元组比较恒 False → sorted 视全部相等 → 稳定排序回退插入序（**非 docstring 承诺的"按 raw 降序兜底"**） | fine_scoring_engine.py:163-167 | **P1** | `score_fine([_rec("B",base_momentum_score=90), _rec("A",base_momentum_score=float("nan")), _rec("C",base_momentum_score=10)], top_n=3)` → top[0] 是 "B"（插入序首）而非按 raw 的任何合理序；且全部 z_score=NaN 无异常 |
| A | 无输入值域校验：base_* / main_force / crowding 任意负值/超 100/inf 直接参与合成，raw 无界（对照同域 S02 有 fail-closed 契约，本件零契约）；Z-score 对离群值敏感（单条极端 raw 会压扁其余 z） | fine_scoring_engine.py:75-88（Record 无 post_init 校验）、:130-143 | P2 | `composite_raw_score(_rec("A", base_value_score=-9999))` → 无异常，raw 极负 → 横截面 z 全体失真 |
| A | 密度扣分公式量纲：neg_skewness×10 + excess_kurtosis×5 + forward_var_pct 三项量纲不同硬加权——经验拍定（memo §3.6 ③ 契约值，:53 自认"G09 校准"待做）；生产方契约核对：neg_skewness=max(0,−skew)≥0、excess_kurtosis=max(0,k−3)≥0、forward_var_pct=abs(VaR95)×100 均非负，**无符号 bug** | fine_scoring_engine.py:109-117 vs conditional_density_predictor.py:76,99-101 | P3（待校准登记） | 对照 conditional_density_predictor.density_summary 构造值验算 penalty |
| A | 重复 symbol 静默覆盖：`raws = {r.symbol: ...}` 字典推导，同 symbol 后条覆盖前条，N 静默缩水，无告警 | fine_scoring_engine.py:161 | P3 | `score_fine([_rec("A",base_momentum_score=10), _rec("A",base_momentum_score=90)])` → len=1 且取 90 分版 |
| A.3 | 测试盲区：无 NaN 用例（P1 正是盲区）、无重复 symbol、无值域越界；现有 14 用例公式验算注释详实、断言精确到近似值——质量良好但覆盖面窄于契约面 | tests/signal_ashare/test_fine_scoring_engine.py 全文 | P2（随 P1 修复补测） | 搜测试文件无 nan/float("nan") 用例 |
| B | 密度摘要鸭子类型契约三属性名有生产方锚点（conditional_density_predictor.density_summary）；但缺字段时 AttributeError（ERROR_CONTRACT :13 自认"由调用方兜底"）→ 装配层职责转嫁，接线时易静默炸 | fine_scoring_engine.py:13、:117 | P3 | 构造缺 excess_kurtosis 的 stub 调 compute_density_penalty → AttributeError |
| B | regime_shift 无值域检查（靠 clamp 兜底，好）；cfg 四维权重和≠1 无校验（手工注入错权重静默漂移） | fine_scoring_engine.py:64-72、:130-135 | P3 | `FineScoreConfig(weight_value=0.9)` 注入 → 无异常，合成口径静默变 |
| C | **孤儿裁定**：`score_fine` 生产调用方=0。header :5 自认"event_driven_screener 未接线（AI-08 审计实证）"；漏斗链上游 coarse_screening_funnel（S08 单审）同样未接线。**定性：设计件全漏斗未通电**，当前对决策链零影响 | 全仓 grep `score_fine(` 零命中；fine_scoring_engine.py:5 | P2 | grep 命令同左 |
| C | 下游（未来 BM-SEL-19/sleeve 排序）消费 z_score 还是 raw_score 未约定——z 是横截面相对分（逐日不可跨日比较），误存库跨日比较会假信号 | fine_scoring_engine.py:97-98 | P3 | 接线设计评审项 |
| D | **MATURITY 标签漂移**：header :7 `MATURITY production` vs :5 "未接线——接线待排期"。production 名不符实（AI-08 :5 已做双侧诚实化但漏改 maturity 字段）——downstream 治理（按 maturity 分级的审计频率/人机门位）会错配 | fine_scoring_engine.py:7 vs :5 | P3 | 对照两行即证 |
| D | 兄弟实现：candidate_pool_aggregator.py:160 "ScoredEntry 姿态镜像（零 import）"——刻意镜像避免耦合，字段（symbol/z_score/rank）需与本件漂移监控（当前一致）；degraded 等权路径与 composite 主路径双承载（有显式 degraded 标志，可接受） | candidate_pool_aggregator.py:160 | P3 | 对照两处字段名 |
| E | 静默失败族：NaN 毒化（P1）、重复覆盖、权重漂移均无告警通道；纯函数无遥测（与 S01 同病，接线时统一补） | fine_scoring_engine.py:159-169 | P2（随接线补） | 造 NaN 输入观察零异常 |
| E | 幂等/时序：纯函数确定性（排序含 symbol 决胜）、无墙钟、无竞态——**已查无** | fine_scoring_engine.py:167 | — | test_zscore_zero_when_tie 佐证确定性 |
| F | 受阻：个股横截面 Z-score 精选范式未单独检索（本战役 2 次检索额度：1 次成功用于板块轮动族、1 次限流受阻）；知识注不作实证：横截面 z-score 标准化+Top-N 是多因子选股教科书标准步骤 | 检索额度已用（2026-09-18 实录） | 受阻 | 收口方如需可补检"cross-sectional z-score standardization factor investing" |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 横截面 Z-score + Top-N 精选 | **受阻**（检索额度已尽；范式本身教科书级无争议） | 本战役检索记录 2026-09-18 |
| 六要素扣分制合成（基础加权×状态偏移+主力−拥挤−密度） | **对等已有**：与多因子合成"加权重+风险调整扣分"惯例同构；权重均显式声明待校准（G09），非终值 | 本件 :53 自述（内部契约，不引外部权威） |

## 4 缺陷清单（按严重级排序）

1. **P1｜NaN 毒化横截面 + 排名静默退化为插入序**
   - 现状：无 isfinite 校验；一个 NaN 使全体 z=NaN；`-zs` 元组比较恒 False → sorted 全"相等" → 稳定排序回退插入序，与 docstring :155 "按 raw 降序兜底"承诺不符。
   - 证据：fine_scoring_engine.py:163-167。
   - 影响与爆炸半径：接线后上游任一字段缺数填 NaN（pandas 链路常态）→ Top-50 = 输入列表前 50 条，z 全 NaN → 精筛完全失效且静默（决策链 P1 级：选股池错而不报错）。
   - 建议修法：(a) Record.__post_init__ 或 score_fine 入口 isfinite 校验 fail-closed（对齐 S02 契约风格）；(b) std NaN 分支并入"置 0+raw 兜底"路径；(c) 补 NaN 用例。
   - 验证法：§2 轴 A 行验证法单行命令复跑。
2. **P2｜输入零值域校验**：负分/超 100/inf 静默参与——接线前补契约校验或文档明示"调用方保证"；验证法=越界输入无异常。
3. **P2｜未通电孤儿链**：score_fine 零调用方+MATURITY=production 名不符实——治理错配+空转；建议改 MATURITY=design 或接线；验证法=grep `score_fine(`。
4. **P3｜重复 symbol 静默覆盖**：加重复检测断言或告警；验证法=双同 symbol 输入 len=1。
5. **P3｜权重和与量纲经验值未校准**（G09 待办登记，非缺陷）；验证法=memo §3.6 对照。

## 5 挂起疑问

- BM-SEL-18 memo §3.6 ③ 原文与 :20-22 权重契约逐条核对未做（收口方抽查）。
- forward_var_pct 量纲（abs(VaR95)×100）假设 VaR95 为小数形式——若生产方将来改传百分数会 ×100 放大，鸭子类型契约未锁单位（隐式契约未文档化，deep_review_policy 轴 B.2 判据命中）。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记）。
- 长尾：①memo 原文核对；②BM-SEL-13 密度预测器本体的算法审查（另对象）；③漏斗四层全链接线形态（尚不存在）。
- 变更热力：6 commits，但逐条核对全为锚点补登/平铺搬家/表头诚实化（5cba5f4039 等），无算法返工——热力属治理性非算法性，低危。
- 测试审查结论：信任（公式验算型测试质量好；盲区=NaN/重复/越界，恰为 P1/P2 所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
