---
ttl: task_bound
doc_type: report
title: 深度审查报告——缠论结构识别（S07）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：缠论结构识别（S07）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/chanlun_structure.py:78`（ChanlunConfig）/ `:343`（analyze_chanlun 主入口）
- 生产调用方: strategy_signal/unified_pattern_engine.py:669（缠论腿收编）；该引擎再被 pattern_signal_runtime/pattern_event_store/pattern_win_rate_provider/scripts/data/pattern_event_backfill 等消费——**域内链最深的一件，非孤儿**
- 测试文件: tests/signal_ashare/test_chanlun_structure.py（15 用例，已审）
- 备注: 线段为自认 MVP 近似（非全规格特征序列法）；本报告按"结构描摹非交易信号"定位审

## 1 对象快照

- **范围**：`chanlun_structure.py` 全文 398 行——五级生成链：包含处理→顶底分型→严格笔→线段（MVP 近似）→中枢；全锚点回指原始 K 下标；纯函数 fail-closed。
- **排除项**：unified_pattern_engine 消费侧（仅核调用点 :669）；chart_pattern_registry PAT-CLL-001~012 其余形态（背驰/区间套未实现，:34 自认）。
- **测试覆盖概况**：包含合并开关、锯齿分型交替、成笔/不成笔、同类取极、三笔成段、中枢区间/无重叠、契约拒绝四件、JSON/frozen。信任度：**信任（盲区=歧义形态与等值边界）**。
- **材料包缺项声明**：无运行时证据包；chan.py/chanlun-pro 口径对照未完成（检索受阻，见轴 F）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 包含处理方向判定仅比 high（`up = merged[-1].high > merged[-2].high`），high 相等时默认向下合并；缠论方向判定通行做法结合前两根合并 K 高低点关系（chan.py 前向方向跟踪）——等值序列下合并方向可能与主流实现不一致（歧义形态之一） | chanlun_structure.py:190-192 | P3 | 构造 high 相等+low 递减序列对照 chan.py 输出（检索恢复后） |
| A | 分型判定严格不等号：中间 high 严格大于两侧才成顶（含 low 同高即不成）——等值边界（双顶同高）不成顶分型且无 notes 留痕；缠论对等值 K 处理各家实现分歧点（歧义形态之二），本件选择静默丢弃 | chanlun_structure.py:209-212 | P3 | 构造 [2,3,3,3,2] 型序列 → 无顶分型、无 notes |
| A | **严格笔跨距口径与注册表措辞存在解释分歧**：实现 `span = fx.pos - pending.pos + 1 ≥ 5`（合并 K **含两端点** → 中间独立 K 仅 3 根）；注册表 PAT-CLL-003 措辞"严格笔需**独立K线>=5**"+params `min_bi_klines: 5`——若按"独立 K=5"字面读法应 span≥7。两种读法差一档，与 chan.py `bi_strict` 的精确对齐未验证（检索受阻） | chanlun_structure.py:233,237 vs chart_pattern_registry.yaml:8932（algorithm_variant）/ :8935（params） | **P2（口径待裁定）** | 对照 chan.py Bi 模块 bi_strict 源码定义（GitHub）；或由 Owner 裁定项目口径字面义并回写注册表措辞 |
| A | `_build_strokes` 丢弃未成笔端点分型：反向分型跨距不足/价格倒挂时整体丢弃（:251），其后同类更极端分型可回补 pending——主流 MVP 做法一致；但"被丢弃分型与后续结构"可能产生与手工画笔不同的端点选择（歧义形态之三），MVP 定位下可接受 | chanlun_structure.py:226-251 | P3 | 构造跨距 4 的假分型夹层序列对照手工标注 |
| A | 线段 MVP 近似自认偏离全规格：终结判据="反向笔破前一反向笔端点"（:284-285,:300-301），非特征序列分型法；无缺口处理。docstring :28-30 与 INVARIANTS :8 均如实声明"轻量近似，非全规格"——诚实，但**输出语义与全规格缠论不可互换**，消费方（叠加层渲染）须知情 | chanlun_structure.py:262-316、:28-30 | P3（定位已声明） | 对照缠论原文第 62-65 课特征序列定义；构造缓破缓成序列对比 |
| A | 线段终结后 `i = j + 1` 起点连续性正确（破坏笔成为下一段首笔，方向交替保持）；中枢延伸=笔区间与 [ZD,ZG] 相交（:335）与 docstring 自洽；ZD<ZG 校验在案（:330）——数学主链自洽 | chanlun_structure.py:305-315、:322-340 | —（已查无） | test_segment_from_three_overlapping_bi / test_zhongshu_zone |
| A | **A 股口径正面**：一字板 high==low 合法（:374-376 仅拒 high<low）；连续一字板在包含处理中被正确合并（等值互含）→ 不产生假分型——涨停板一字板无量/无形态的口径处理正确 | chanlun_structure.py:187-188、:374-376 | —（正面） | 全等序列输入 → 单根合并 K、零分型零笔 |
| A.3 | 测试盲区：无等值边界/一字板序列/包含方向歧义用例；15 用例对主路径覆盖扎实；跨距边界（span=4 vs 5）无显式用例（test_tight_fractals_no_bi :98 未直接验 4/5 边界） | tests/signal_ashare/test_chanlun_structure.py 全文 | P3 | 补 span=4/5 边界用例（收口方施工） |
| B | 输入契约 fail-closed 完整（等长/根数/正有限/high≥low）；**隐式契约：序列须为可比时间粒度的连续 K 线**（断档/混周期未校验——合并与分型对时间间隔不敏感，跨档 K 照样合并） | chanlun_structure.py:362-376 | P3 | 构造日期断档序列 → 照常出结构无告警 |
| C | 下游：unified_pattern_engine.py:669 消费（`ChanlunConfig(min_bi_bars=self._cfg.chanlun_min_bi_bars)` 权重链）；引擎侧消费后进 pattern 事件链。**本链对 MVP 近似是否知情**：引擎头注 :4 标"缠论腿收编，testing"——已知情；渲染层（GAP-F-37 指数/个股页叠加）未接线 | unified_pattern_engine.py:4、:669 | P3 | 审 engine 配置 chanlun_min_bi_bars 默认值是否 ≥5 |
| C | 输出错位爆炸半径：本件输出"结构描摹数据非交易信号"（:34-35）——爆炸半径=叠加层渲染错+pattern 事件错标，非直接资金路径 | chanlun_structure.py:34-35 | P3（定位缓冲） | — |
| D | 兄弟实现盘点：全仓无第二份缠论实现（单承载 ✓）；chart_pattern_registry PAT-CLL-001/002 登记的"candidate 零代码"分型识别由本件承载（:20-21 声明）——注册表 code_path 仍空（:8930 `code_path: ""`）→ **注册表↔代码挂接漂移**（checklist#9 反向：有码无挂） | 全仓 grep；chart_pattern_registry.yaml:8930 | P3 | 注册表 code_path 应回填本件符号（收口方施工） |
| E | 静默失败面：等值边界静默丢弃（轴 A）、断档静默合并（轴 B）——均有 notes 机制可用但未用；无遥测；幂等纯函数 | chanlun_structure.py:378-388 | P3 | 造歧义输入看 notes 是否留痕 |
| E | 时序/竞态：无状态；重跑幂等；输出 frozen——已查无 | chanlun_structure.py:163-176 | — | test_frozen |
| F | 缠论笔/段/中枢识别 | **受阻**：WebSearch 限流（429）无法给出 chan.py/chanlun-pro 对照 URL；本件自述对齐二开源口径（:37-38）+缠中说禅 108 课第 62-65 课为体系真源（2006-2008 博客连载，无正式出版检索源）。**笔跨距口径 P2 裁定因此悬置** | 本战役检索记录 2026-09-18 | 检索恢复后核 chan.py Bi bi_strict 定义回填 §3 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 严格笔跨距（bi_strict） | **受阻**：对齐声称（chan.py/chanlun-pro）未验证——检索限流；已转入 §2 P2 口径裁定项 | 本战役检索记录 2026-09-18 |
| 线段特征序列法 | **驳回（全规格）+对等（MVP 定位）**：本件非特征序列法全规格实现，但 INVARIANTS/docstring 如实声明 MVP 近似——不构成"编造对等"，属显式降级实现 | chanlun_structure.py:28-30 自述（缠中说禅 108 课为体系真源） |
| 中文本土技术分析体系（缠论） | **对等已有（体系级）**：缠论为 A 股本土成熟流派，开源实现生态（chan.py/chanlun-pro）存在——具体 URL 因检索受阻未附，不作逐条对等断言 | 受阻记录同上 |

## 4 缺陷清单（按严重级排序）

1. **P2｜严格笔跨距口径"独立K线>=5"双解释未裁定**
   - 现状：实现 span 含端点 ≥5（中间独立 K=3）；注册表字面"独立K线>=5"可读作 span≥7；与 chan.py bi_strict 对齐未验证。
   - 证据：chanlun_structure.py:233,237；chart_pattern_registry.yaml:8932,8935。
   - 影响与爆炸半径：若口径应取更严读法，当前笔画得更碎→线段/中枢全体下移一级→叠加层与 pattern 事件全链结构偏移（系统性口径漂移，非崩溃）。
   - 建议修法：Owner 裁定项目口径（推荐以 chan.py bi_strict 为准并回写注册表措辞为"合并 K 含端点 ≥5"或改实现），补 4/5/7 边界测试。
   - 验证法：检索 chan.py Bi 源码对照 span 语义；或本地构造 span=5/6 序列人工判定何者符合预期画笔。
2. **P3｜等值边界静默丢弃（双顶同高不成顶）**：至少加 notes 留痕；验证法=[2,3,3,3,2] 序列无分型无 notes。
3. **P3｜包含处理方向判定仅比 high**：等值序列与主流实现可能不一致；验证法=对照 chan.py（检索恢复后）。
4. **P3｜注册表 code_path 空挂**（有码无挂）：回填 `zephyr.signal_ashare.chanlun_structure.analyze_chanlun`；验证法=对照 registry 条目。
5. **P3｜时间连续性未校验**：断档/混周期序列照常出结构；建议调用方约定或 loader 层校验；验证法=断档序列复跑。

## 5 挂起疑问

- chan.py `bi_strict` 的精确跨距定义（P2 裁定依据）待检索恢复。
- unified_pattern_engine 侧 chanlun_min_bi_bars 默认值未核（消费侧配置一并在 P2 裁定时对齐）。
- PAT-CLL-005/006（线段/中枢 registry 条目）与本件实现的 algorithm_status=pending_backtest 状态联动未核。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记；缠论为中文本土体系，英文检索族天然缺位，已按政策记录）。
- 长尾：①chan.py/chanlun-pro 逐口径对照；②unified_pattern_engine 消费侧深审（建议单列对象）；③歧义形态集（等值/共用K/跳空）变形测试用例族。
- 变更热力：1 commit（GAP-F-37 收口批），无返工史=低危。
- 测试审查结论：信任（主路径与契约覆盖扎实；盲区=歧义形态与跨距边界，与 P2/P3 对应）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
