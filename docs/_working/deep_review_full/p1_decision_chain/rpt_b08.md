---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——WalkForward分析器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：WalkForward分析器（B08）

- 状态: **已审**
- 级别: P1｜类型: 切分内核（窗口泄漏重点专项）
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/walk_forward.py:88`（WalkForwardAnalyzer）
- 生产调用方: strategy_pipeline/fw_backtest.py:400-408（expanding 切 NAV，"locked_book_time_split 窗口内无再拟合"）；vectorized/event_driven 的 run_walk_forward_analysis 桥接（grep 生产调用方=0）
- 测试文件: tests/backtest/test_walk_forward.py（261 行 31 测试，本批运行全绿）
- 备注: —

## 1 对象快照

- 范围：三模式切分（rolling/anchored/expanding）、split 分发、whites_reality_check、_stationary_block_bootstrap。
- 排除项：fw_backtest 的 IS/WFA/OOS 证据组装逻辑（消费侧，长尾）。
- 材料包缺项声明：无（纯函数对象，材料自足）。
- 变更热力：12 commits，末次 2026-09-15。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **窗口泄漏专项：切分只保证索引不重叠，无 purge/embargo 能力**——train=[i,i+tw) test=[i+tw,i+tw+ow) 相邻无缝；若标签是 forward return（窗口 H>0），train 末端 H-1 个样本的标签窗口伸入 test 区间=信息泄漏。同库 cpcv.generate_cpcv_splits 已实现 t1 purge+embargo（B09），本件 API 无此参数——同概念双实现保护不对称，调用方无防泄漏工具可用 | walk_forward.py:101-189（切分无 t1/embargo 参数） vs cpcv.py:104-183 | P1 | 造 t1=i+5 的标签面板分别走 split() 与 generate_cpcv_splits(t1=…) 对比 train 末端与 test 首行标签重叠 |
| A | 泄漏的现实爆炸半径核验：生产消费方 fw_backtest 切的是**已定格 NAV 序列**（"窗口内无再拟合"，fw_backtest.py:426 caliber 声明）——无训练即无标签泄漏，现网实际暴露=0；暴露面在未来任何"逐折再拟合"的调用方（引擎桥接方法语义上支持）。泄漏风险=能力缺位而非现行事故 | fw_backtest.py:393-426;grep run_walk_forward_analysis 生产调用=0 | P1（降级依据） | 读 fw_backtest caliber 声明与 analyzer 用法 |
| A | **whites_reality_check 名实不符**：实现=单策略超额收益均值的 stationary bootstrap t 检验（recentered H0 bootstrap，块自举保自相关，环绕索引——单策略统计本身正确）；但 White (2000) RC 的核心=跨策略**max 统计量**的 bootstrap 分布（多重比较校正本体），无策略面板即无 RC。模块 docstring 与 INVARIANTS 声明"多重比较偏差校正"不成立 | walk_forward.py:8,220-244 vs 实现 :246-289 | P2 | 对照 White (2000) 定义：给 2+ 策略面板看 API 无法表达 max 统计 |
| A | WRC 随机性：rng=np.random.default_rng() 无种子——p 值 run-to-run 抖动，is_significant 在阈值附近可翻转（测试注释自认"bootstrap内rng无种子"并用精确零均值策略规避） | walk_forward.py:272;test_walk_forward.py:200 | P2 | 同输入跑 20 次看 p 值散布 |
| A | 切分数学核验：rolling 步进/边界、anchored 起点固定步长增长、expanding 忽略 step 以 test_window 增长（文档=行为，测试锁定）——三模式索引数学全对；`i+tw+ow<=n` 保证 test 满窗 | walk_forward.py:101-211 | 通过 | test_basic_folds 精确断言复核 |
| B | dates 输入零校验（乱序列表不排序直接切片）：docstring 声明"按时间升序"为隐式契约，乱序输入静默产出乱序 fold——上游给乱序 dates 时 WFA 结果整段错 | walk_forward.py:101-117（无排序/无断言） | P2 | 传乱序 dates 看切分静默错序 |
| C | 消费方=fw_backtest（真实）+两引擎桥接（死）；WRC 无生产调用方（grep whites_reality_check src/=0，仅测试）——统计检验能力空转 | grep whites_reality_check src/ | P3 | grep 命令见锚点 |
| D | 与 cpcv.py 的双实现关系：切分职责重叠（WFA 单路径 vs CPCV 多路径组合），purge/embargo 只在 CPCV 有——长期应统一到 cpcv 或 WFA 增参（规范预算） | cpcv.py vs walk_forward.py | P3（随轴A修复裁决） | — |
| E | 空数据/None fail-fast ✓（raise WalkForwardError）；数据不足返回空 folds（静默空，消费方 fw_backtest 需自判——其 :426 有 caliber 处理，长尾核） | walk_forward.py:116-117,124 | P3 | 短序列调 split 看空列表 |
| A.3 | 测试审查：31 项覆盖三模式边界/无泄漏（max(train)<min(test) 索引级）/WRC 显著双向/退化输入；**"无泄漏"断言仅索引级**，标签级泄漏（轴A首条）无测试——测试绿≠无泄漏的实证 | test_walk_forward.py:89-92,123-126,146-149 | P2 | 造 forward-return 标签跑 fold 验证 train 标签伸入 test |

## 3 SOTA 对照

- Walk-Forward 切分：**对等已有**——rolling/anchored/expanding 三模式与 Pardo《The Evaluation and Optimization of Trading Strategies》(Wiley, 2008) 经典 WF 定义一致。（来源：Pardo 2008 经典文献面，经 paperswithbacktest.com WF 课程页交叉引用，2026）
- purge/embargo：**立卡候选**——López de Prado (2018) Ch.7 要求所有时间序列 CV（含 WF）对重叠标签做 purge+embargo；本件缺位、同库 CPCV 已有——建议 WFA split 增加 t1/embargo 可选参对齐。（来源：López de Prado, Advances in Financial Machine Learning, Wiley 2018, Ch.7 "The Dangers of Cross-Validation"；paperswithbacktest.com/course/purged-k-fold-cross-validation, 2026）
- White's Reality Check：**驳回（现名）**——White (2000, Econometrica) RC 与 Hansen (2005) SPA 均为跨策略 max/劣策略筛选统计；本实现是单策略 bootstrap t 检验（更接近 Politis & Romano 块自举的均值检验），应更名"block-bootstrap significance test"或补 max 统计量。（来源：White 2000 "A Reality Check for Data Snooping", Econometrica 68(3)；检索面经 López de Prado 文献交叉引用，2026 核对）

## 4 缺陷清单

1. **[P1] 切分无 purge/embargo 能力（窗口泄漏防护缺位）**：现网暴露=0（fw_backtest 无再拟合），但引擎桥接语义支持逐折再拟合、未来调用方默认裸奔。建议修法：split() 增加可选 t1/embargo 参数（复用 cpcv 同款数学），docstring 强制声明"前视标签必须传 t1"；或消费侧强制走 cpcv。验证法：§2 轴A 首条。
2. **[P2] White's Reality Check 名实不符**：统计本体正确但"多重比较校正"声明不成立——决策链若据此宣称"过了 RC 校正"=虚牌。建议修法：更名+docstring 澄清单策略口径，或补 max-statistic。验证法：§2 轴A。
3. **[P2] WRC 无种子随机性**：p 值不可复现。建议修法：rng 可选参数默认固定种子+产物附种子。验证法：§2 轴A。
4. **[P2] dates 乱序静默错切**：建议修法：入口断言升序或内部排序。验证法：§2 轴B。
5. **[P3] WRC/桥接方法零生产调用方；空 folds 静默**。

## 5 挂起疑问

- fw_backtest 的 NAV 三段证据（IS/WFA/OOS）是否被决策门控（DecisionGate.check_wfa_stage）消费为"WFA 稳定性"证据——若是，其口径是"净值时间切片"而非逐折再拟合，与 DecisionGate 期待的 WFA 语义是否等价需收口方判定（影响 B08 缺陷 1 的实际优先级）。

## 6 完备性自评

六轴全查。长尾：①fw_backtest 证据组装与 DecisionGate 消费链（挂起疑问①）；②stationary bootstrap 块长 T^(1/3) 对高频自相关序列的适配性未数值验证；③expanding 模式与 anchored 仅步长不同的 API 冗余是否合并（规范预算）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
