---
ttl: task_bound
doc_type: report
title: 深度审查报告——个股信号强度（S06）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：个股信号强度（S06）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/stock_signal_strength.py:82`（StrengthConfig）/ `:214`（compose_strength 主入口）
- 生产调用方: **零**（grep compose_strength/stock_signal_strength 全仓 src/scripts 仅自身；GAP-F-39 消费位未接线）
- 测试文件: tests/signal_ashare/test_stock_signal_strength.py（15 用例，已审）
- 备注: 关键发现（全零量→NaN）已经 Python 3.12.8 实跑复现

## 1 对象快照

- **范围**：`stock_signal_strength.py` 全文 298 行——MACD/RSI/量能/均线/AI NLP 五维归一 [0,100] 加权合成（可用维重归一）+ 五档标签；纯函数零 DB/LLM。
- **排除项**：AI NLP 上游（注入式契约，不审生产方）；GAP-F-31 指数级共振（S10 单审）。
- **测试覆盖概况**：五维齐全性、方向性、NLP 重归一、契约拒绝（短根数/不等长/负价/负量/NLP 越界/负权重/全零权重）、确定性、frozen、JSON。信任度：**信任（盲区=零量 NaN 与复权口径）**。
- **材料包缺项声明**：无运行时证据包（未接线）；真实个股序列数据画像缺。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **全零量序列（长期停牌股合法输入）→ strength=NaN、label="弱" 静默**（实跑复现）：`np.mean(v[-5:])/np.mean(v[-20:])` = 0/0 = NaN → tanh(NaN)=NaN → 末尾 clamp 对 NaN 无效 → strength=nan；标签比较全 False → "弱"。ERROR_CONTRACT 声称 fail-closed 但 `v>=0` 校验放行全零量——**A 股停牌股剔除口径缺失**（任务书六轴"停牌股剔除"正中；checklist#7 同族） | stock_signal_strength.py:188（除法）、:244-245（v≥0 校验）、:281/:292（clamp 对 NaN 无效）、:207-211（label 兜底"弱"） | **P1** | 实跑：`compose_strength([10.0+0.05*i for i in range(35)],[0.0]*35)` → RuntimeWarning + `strength=nan label=弱`（无异常） |
| A | RSI Wilder 实现正确（SMA 种子+Wilder 平滑、avg_loss=0 边界处理、clamp）；量能四档有界；均线四档有界；合成凸组合 ∈[0,100]——数学主链健全 | stock_signal_strength.py:170-204、:287-289 | —（已查无） | test_uptrend/downtrend、test_deterministic |
| A | MACD EMA 种子偏差：`_ema` 以首值作种子（out[0]=arr[0]），min_bars=35 时 EMA26/DEA9 远未收敛（教科书 warmup≈3×period≈78 根）→ hist 有偏；:95 自认"35 兜底"但未提示偏差幅度 | stock_signal_strength.py:152-167、:95 | P3 | 对照 35 根 vs 120 根同趋势序列的 hist_pct 差 |
| A | 复权口径未约定：closes 注入序列若不复权，除权日跳变同时打歪 MACD/RSI/量比方向/均线四维——docstring 与校验均未要求复权口径（checklist#7 前科：不复权假收益 818d676b3a） | stock_signal_strength.py:23-31（口径表无复权条款）、:224 | **P2** | 构造除权日 -10% 跳变序列 → 五维明细全翻转（对照前复权版） |
| A.3 | 测试盲区：无全零量/停牌用例（P1 正中）、无除权跳变用例、无 35 根下限的 EMA 收敛性检查；其余 15 用例契约覆盖扎实 | tests/signal_ashare/test_stock_signal_strength.py 全文 | P2（随 P1 修复补测） | 搜测试无 zeros(35)/停牌用例 |
| B | 输入契约：等长/正价/非负量/NLP 越界 fail-closed（好）；但"量=0 是否合法"语义未定义（承接 P1）；closes 复权口径未文档化（隐式契约，deep_review_policy 轴 B.2 判据命中） | stock_signal_strength.py:13、:224-247 | P2 | 同上两条 |
| B | den=0 兜底 strength=50（:289）：config 可注入四基础维全 0 权重+NLP 缺省 → den=0 → 静默中性 50，无 notes 留痕（对齐 S04 的"权重全零不出伪分"纪律，本件弱一档） | stock_signal_strength.py:287-289 | P3 | `StrengthConfig(w_macd=0,w_rsi=0,w_volume=0,w_ma=0)` + NLP None → 50 无告警 |
| C | **孤儿裁定**：生产调用方=0，GAP-F-39 消费位（个股决策卡/看板强度列）未接线；MATURITY=testing 诚实。接线前对决策链零影响 | 全仓 grep 零命中；stock_signal_strength.py:5、:7 | P2 | grep 命令实录 |
| C | 下游消费契约未定义：strength/label 的看板展示口径（NaN 显示什么）无约定——P1 的爆炸半径延接管线日 | stock_signal_strength.py:135-143 | P3 | 接线施工单验收项 |
| D | 兄弟件：GAP-F-31 指数级共振评分（index_resonance_scorer，S10 单审）同族"多维加权合成 0-100"——两件合成范式同构（可用维重归一），口径声明各自独立，暂无重复实现（一个指数级一个个股级） | stock_signal_strength.py:37、index_resonance_scorer.py | —（结构健康） | 两文件对照 |
| E | 静默失败族：NaN 链（P1）+den=0 兜底（P3）均无 notes/告警；纯函数无遥测（接线时统一补）；幂等确定性已测（好） | stock_signal_strength.py:287-297 | P2（随接线补） | 实跑见 P1 验证法 |
| E | 时序/竞态：纯函数无状态；PIT=仅用注入序列末态（声明 :8）——已查无 | stock_signal_strength.py:8 | — | test_deterministic |
| F | 五维技术信号加权合成 | **受阻**：检索额度已尽；知识注不作实证：RSI/MACD/量价合成是经典技术分析组合范式（Wilder 1978 RSI 原始定义与本件实现一致） | 本战役检索记录 2026-09-18 | 收口方补检可选 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| RSI(14) Wilder 平滑 | **对等已有**：实现与 Wilder 1978 原始算法定义一致（SMA 种子+递推平滑），边界（全涨全跌）处理正确 | J. Welles Wilder, *New Concepts in Technical Trading Systems*, 1978（经典文献，训练语料高频收录，非检索实证——按受阻口径附注） |
| sigmoid/tanh 归一合成五维 | **受阻**（额度已尽；范式常见） | 本战役检索记录 2026-09-18 |

## 4 缺陷清单（按严重级排序）

1. **P1｜全零量（停牌股）→ NaN 强度+"弱"标签静默输出**
   - 现状：v≥0 校验放行全零量 → 0/0=NaN 全链传播 → clamp/标签比较对 NaN 全失效 → label="弱"。
   - 证据：stock_signal_strength.py:188、:244-245、:292、:207-211；实跑复现输出在案。
   - 影响与爆炸半径：停牌股是 A 股常态场景——接线后每只停牌股输出"NaN 分+弱标签"静默进看板/决策卡；若下游聚合强度均值，NaN 毒化聚合（与 S03 同族传播）。
   - 建议修法：(a) volumes 全零或 vol_long 均量=0 → ValueError fail-closed（或返回 available=False 维度走重归一并 notes 留痕）；(b) 合成前对 dim score isfinite 断言；(c) 补停牌用例。
   - 验证法：§2 P1 行单行命令复跑（RuntimeWarning+nan 实证）。
2. **P2｜复权口径未约定**：输入契约文档化"前复权收盘+复权成交量"或在入口校验除权跳变（与 checklist#7 前科对齐）；验证法=构造除权跳变序列对照。
3. **P2｜孤儿未接线**：GAP-F-39 位接线时须带停牌/除权集成测试；验证法=grep。
4. **P3｜EMA 种子偏差（35 根下限）**：文档提示偏差或提高 min_bars 至收敛安全值；验证法=35 vs 120 根对照。
5. **P3｜den=0 静默中性兜底**：加 notes 留痕对齐 S04 纪律；验证法=全零权重配置复跑。

## 5 挂起疑问

- AI NLP 注入分的生产方与口径（哪家的情感分、映射到 [0,100] 的协议）未定——接线前须落上游契约。
- 五维权重初拍值（0.25/0.20/0.20/0.20/0.15）待实盘标定（自认 :21，非缺陷）。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记；A 轴含实跑复证）。
- 长尾：①NLP 上游契约；②看板消费侧展示审查；③与 S10 同族范式的权重口径对照（两件各自独立设计，无合并必要）。
- 变更热力：1 commit（创建批），无返工史=低危。
- 测试审查结论：信任（契约拒绝矩阵完整；盲区=零量 NaN/复权，恰为 P1/P2 所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
