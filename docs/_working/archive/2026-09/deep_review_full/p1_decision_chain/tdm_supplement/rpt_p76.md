---
ttl: task_bound
title: 深度审查作业簿——卖出闭环与退出效率
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：卖出闭环与退出效率（P76）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/sell_decision/core/sell_execution_quality_tracker.py:129`（evaluate_execution_quality）
- TDM 节点: TDM-X-S2-06（stage，config/trading_decision_map.yaml:3620，point: 盘后，D51/D72/D106 注释密集）
- 生产调用方: **零**——evaluate_execution_quality 全仓无调用（仅自身与包结构）；header 声明的 D-EX-CORE/MOD-SELL-011 AB 测试/D_RISK 零实际接线
- 测试文件: tests/sell_decision/test_sell_execution_quality_tracker.py（114 passed 同批）

## 1 对象快照

- 范围：evaluate_execution_quality 纯函数全文件（210 行）——卖出滑点度量：单笔滑点=(决策价−成交价)/决策价（正=卖亏）→权重加权平均→GOOD≤0.1%/ACCEPTABLE≤0.3%/DEGRADED 三级+超阈单笔留痕+预警字符串。
- 排除项：IS 三分解（延迟/冲击/机会成本，TDM 声明归执行成本轴=P53 域）；卖出理由六分类（本模块零承载，见轴 D）。
- 测试覆盖概况：滑点口径/分级/边界（空列表/零权重）覆盖好；无"负权重合计"边界外的场景缺口。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点核心三问（三率）与六分类复盘全零承载，模块只交付"执行滑点"一个子面**（对账主发现）：TDM-X-S2-06 声明「卖出后 N 日跟踪三率：**卖飞率**（卖后再创新高占比>30%=止损太紧）/**避损率**（卖出后继续跌占比）/**MFE 捕获率**（拿到行情百分比）」+「**六分类复盘**（止损/止盈/时间/逻辑/置换/恐慌）——PANIC 占比>10%=纪律失效告警（D72：健康占比应为 0）」+理由×结果交叉统计+信号 N 日前瞻跟踪分桶（任一桶 30 日避损率斜率降 30%→权重降档）+D106 迟滞带/连败阶梯/regime 开关冷却——**全部零代码**（模块无任何 N 日前瞻/价格后续/理由分类输入）；模块交付的滑点分级只是 D72 注释里"IS 三分解进执行成本轴"的一个执行面子集。decision_question"卖对了吗"实际无人回答 | config/trading_decision_map.yaml:3620-3700（三率/六分类/D72/D106） vs sell_execution_quality_tracker.py 全文（grep 卖飞/避损/MFE/PANIC/六分类 零命中） | P1 | 对照三率+六分类逐条 grep；确认无前瞻价格输入 |
| C | 孤儿死码（checklist #8，header [MATURITY] production 不实）：零调用方；"统计喂 F-C3 归因校准 S1 评分权重"出边（TDM :4337 X-S2-06→F-C3-01 feed 边）两端皆孤儿（P57 已审） | sell_execution_quality_tracker.py:5-7；grep 证据 | P2 | grep 三连 |
| A | 滑点数学（已核）：卖出口径 (decision−executed)/decision 正=卖亏 ✓（与 P53 的 arrival-price TCA 口径同族且方向显式）；加权平均 total_weight=0 时退化等权（防除零）；分级阈值 (0≤good≤acceptable) 校验；空输入返回 GOOD 空报告（语义可议：零成交给 GOOD 而非 N/A，P3 轻症） | sell_execution_quality_tracker.py:166-195 | —（已核） | — |
| A | 分级阈值未校准声明缺失：0.1%/0.3% 两线为经验默认（_DEFAULT_* 常量），对照 CST-ASTOCK-001 A 股卖出成本（佣金+印花税≈0.06-0.1% 起步）——ACCEPTABLE 0.3% 线的合理性依赖成本结构，无校准锚（checklist #15 问句轻触：默认数字无底层产物锚，但常量非裁定引用，轻症） | sell_execution_quality_tracker.py:56-57 | P3 | 对照 CST-ASTOCK-001 费率复算 |
| B | 决策价基准定义缺契约：decision_price 是"信号触发价/下单提交价/开盘决策价"三可——不同基准下滑点不可比（对照 P53 arrival-price=decision price 的多基准问题同族）；无基准类型字段 | sell_execution_quality_tracker.py:79-84 | P3 | 读字段注释确认无基准枚举 |
| E | 零成交→GOOD 分级可能掩盖"该卖没卖"（执行面空转被评 good）——与 P71 provider 失败盲区同族：无成交本身是信息，模块按无输入处理 | sell_execution_quality_tracker.py:169-178 | P3 | 空列表探针看 GOOD |
| A(亮点) | 滑点方向语义显式（卖出正=亏，P53 的 abs() 缺陷在此模块不存在）；权重加权+outlier 留痕+预警串；输入校验完备（价格正有限/权重非负）；frozen 报告 | sell_execution_quality_tracker.py:148-167,202-210 | — | — |

## 3 SOTA 对照

- 执行滑点度量（decision vs executed price）：**对等已有**——arrival-price 基准滑点是 TCA 标准面（Talos《Execution Insights Through TCA》talos.com，2026；ACA Group TCA acaglobal.com，2026，同 P53 引）；本模块口径与之一致且方向处理正确（P53 的 abs() 缺陷对照成立）。
- 卖出后 N 日前瞻三率（卖飞率/避损率/MFE 捕获率）：**对等已有（声明侧依据充分，实现缺位）**——卖出决策的事后评估（exit efficiency: opportunity cost of selling / MFE capture）是执行研究标准问句（FE Training portfolio management 教材 fe.training，2026，同 P57 引；Investopedia Exit Strategy 族，investopedia.com，2026）；TDM D72 的"信号前瞻跟踪分桶+斜率降档"设计在业界罕见（立卡候选：前瞻性好设计，值得按期施工）。
- PANIC 占比纪律监控：**对等已有（项目内自洽）**——行为纪律量化（恐慌交易占比告警）与 42 号 §3.11 A/B 校准流程配套；项目自有体系无外部对照必要。

## 4 缺陷清单

1. **[P1] 三率+六分类+前瞻分桶+冷却机制零承载，节点名实不符（"卖出闭环与退出效率"实际=卖出滑点度量）**。建议修法：施工批次补三率追踪（需卖出后 N 日价格回填管道+理由六分类必填枚举，D72 已给枚举），或节点拆注"滑点子面已建（本模块）/三率与六分类待建"；module_id 不变、声明先行修正。验证法：§2 轴 D grep。
2. **[P2] 孤儿（production header 不实）**。建议修法：随 X-S2 执行链接线批次+归因链（P57）同批接线；接线前降 draft。验证法：grep。
3. **[P3] 决策价基准无枚举+阈值无校准锚+空成交 GOOD 语义**。建议修法：加 benchmark_type 字段（signal/submit/open）；阈值挂 CST 校准批；空输入 grade 改 N/A 或加 warning。验证法：各自探针。

## 5 挂起疑问

- 三率追踪需要"卖出后 N 日行情回填"数据管道（谁存卖出事件+谁回填价格）——与 X-S2-01 执行链和 C3-01 归因链的接线顺序强耦合，建议收口方统一排期（X 流四件 P73/P74/P75/P76+P57 归因端）。
- 滑点分级与 P53 ExecutionQualityScorer（ex_sor 域四维评分）的双承载风险：两件同评"执行质量"但维度不同（滑点单维 vs 四维加权）——接线时须裁定唯一执行质量真源或显式分工（滑点=卖出域、四维=买入算法域），防两套 verdict 并行漂移。

## 6 完备性自评

六轴全查（A 数学四问：滑点公式/加权/退化路径逐个过、边界=空/零权重/越界已测；B 上游=SellFillRecord 契约已查（基准缺口已记）；C 下游=零调用方判孤儿；D=三率六分类对账（主发现）+与 P53 双承载风险登记；E 五问：静默失败=无成交评 GOOD、假阳性=无、断供=无、重复触发=纯函数幂等、时序=无时钟依赖。长尾：①MOD-SELL-011 AB 测试框架未审；②卖出理由六分类的录入端（42 号 §3.11）未审；③N 日前瞻回填管道不存在故三率可行性未验证。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
