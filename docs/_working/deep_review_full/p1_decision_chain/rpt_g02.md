---
ttl: task_bound
doc_type: report
title: 深度审查报告——G02 基本面选股漏斗（selection_funnel 薄适配层）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：G02 基本面选股漏斗（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 管线（BM-SEL-16/17/18 三层漏斗薄适配层）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/selection_funnel.py:93(FunnelSymbolRecord)(:319 run_selection_funnel)`
- 生产调用方: **零**（grep 全仓无 import/调用；header [CONSUMERS]"待 G08/G09/G10 sleeve 接线"自认）——共享骨架 selection_funnel_skeleton 另有真实消费方 tiered_screening_filter，但**本适配层**自身未接线
- 测试文件: tests/signal_fundamental/test_selection_funnel.py（存在）
- 变更热力: 2026 年 8 commits（中低热；SIGNAL-ARCH-001 归并重构期）
- 材料包缺项: 真实候选池数据画像缺（容量链 7000→1200→300→50 未实证）

## 1 对象快照

归并裁定落地件：层序/接口/数据流唯一真源=signal_ashare/screening/selection_funnel_skeleton.py（MOD-SIG-086），本件只保留域记录类型、阈值常量与钩子装配。**数学全部委托骨架**——本审将骨架一并读完做数学四问（范围声明：骨架本体归 MOD-SIG-086，此处只出与 G02 口径相关的判定）。排除项：tiered_screening_filter（A 股域姊妹适配层，D 轴对照已做）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿（模式#8，已声明型）**：本适配层生产调用方=0；docstring/CONSUMERS 自认待 G08/G09/G10 接线 | selection_funnel.py:5; grep | P2 | grep 生产 import（已做） |
| A | 数学四问-第一层四排除：优先级物理（涨跌停/停牌/ST）→门禁（次新<30d）→分级（成交额<500万→extra AUM≤100万）→概率（弃庄>0.95）✓ 与 memo §3.6① 口径一致；degraded=True 时仅物理排除（ST 也放行）——文档声明 ✓ 但语义易误读 | skeleton:156-200; selection_funnel.py:34-35, 246-249 | ✓ 查无（P3 语义留档） | 造 degraded 记录含 ST 看保留 |
| A | 数学四问-第二层五维：技术/量比（排除 ≤1.5 与 memo"量比>1.5"一致）/换手（0=不强制）/板块（>30% 排除）/主力/状态 顺序执行 ✓；容量截断按流动性降序+symbol 字典序确定性 ✓（本域不注入 capacity，不截断=文档一致） | skeleton:240-289; selection_funnel.py:262-263 | ✓ 查无 | 对照 memo 阈值常量 |
| A | 数学四问-第三层六要素合成：raw=base(0.4/0.3/0.2/0.1 加权 0-100 分)×(1+shift∈±0.1)+0.20·main_force−0.10·crowding−0.15·(skew×10+kurt×5+var_pct)+0——**隐含量纲假设**：density_penalty 极端峰度（kurt≈10→罚 50+）可超 100 尺度使 raw 为负；z-score 排名对全体同尺度变换稳健但受极值方差膨胀影响 | skeleton:348-371, 334-345; selection_funnel.py:229 | P3（隐含假设登记） | 造 kurt=10 记录看 raw 为负+全体 z 收缩 |
| A | Z-score：总体方差（÷n）、std<1e-12 全置 0 按 raw 兜底 ✓；rank 用 (−z,−raw,position/symbol) 三键稳定 ✓；top_n≤0/空→空 ✓ | skeleton:384-408 | ✓ 查无 | 全同分输入看 z=0 兜底 |
| A | 漏斗单调不变量：chain 中 screened 输入=graded.kept 子集、scored 输入=screened.kept 子集（kept 逐层传递+同名后写覆盖双域同口径 ✓）——独立三层函数调用不强制单调（构造方责任，chain 入口已保证） | skeleton:425-442, 414-421 | ✓ 查无 | chain 输出断言 ⊇ 链 |
| B | **北交所防呆纯文档**：run_selection_funnel docstring 把"市场=沪深硬过滤"责任压给 records 构造方（2026-09-09 Owner 裁定：ST 名单北交所缺失的替代防呆），函数无运行时校验——构造方失职时北交所票带病入精筛（fail-open） | selection_funnel.py:329-335 | P2 | 构造含 92 段代码 records 跑 chain，看无任何拦截 |
| D | **阈值双轨**：screen_preliminary 独立入口可传阈值覆盖参数（:268-270），chain 入口锁死模块常量（:347-353）——同一概念两处承载，覆盖面不一致 | selection_funnel.py:264-287 vs 337-363 | P3 | 两入口传不同 volume_ratio_min 对比行为 |
| D | tie_break="stable"（本域）vs "symbol"（A 股域）✓ 已文档化分工；本域同分保持输入序=消费方记录顺序敏感（上游排序变更即换名单，无锚） | :29, 311; skeleton:73-74 | P3 | 对读两域适配层 |
| A.3 | 测试存在；断言强度未逐条审（时间盒，记长尾） | tests/signal_fundamental/test_selection_funnel.py | P3 | 抽读 |

## 3 SOTA 对照

- 三层漏斗结构（粗排→门槛筛→综合评分 TopN）为多因子选股常规范式，无单一权威外部源——**受阻未搜**；21 号 memo §3.6 为仓内真源（对等对照=内部裁定）。
- 中文卖方金工的多因子打分-漏斗体系为独立矿脉——受阻未搜（检索预算已用于 WQ101/保形/TA-Lib）。

## 4 缺陷清单

1. **P2 孤儿（已声明型）**：适配层未接线；接线时注意 chain 与单层函数阈值双轨收敛。验证法：grep。
2. **P2 北交所 fail-open 防呆**：文档契约无运行时兜底。建议：入口对 symbol 前缀（92/43/83/87/4/8 段）断言或告警日志。验证法：§2 B 行构造法。
3. **P3 组**：六要素量纲假设登记、阈值双轨、tie_break 顺序敏感、degraded 含放行 ST 的语义留档。

## 5 挂起疑问

- G08/G09/G10 sleeve 接线排期与 CapacityTruncation（A 股域 ~300 截断）在 fundamental 域是否永不启用的裁定确认（当前不注入=漏斗容量链实际 7000→50 无 ~300 级收敛层）。

## 6 完备性自评

六轴全查（F 受阻记）。数学四问经骨架全读覆盖（排除/评分/标准化/边界逐项）。长尾：①tests 断言强度；②FunnelSymbolRecord 默认值方向性安全审查（list_days=9999/amount=1e12 默认全过=构造缺字段时 fail-open——与 ERROR_CONTRACT :13"dataclass 默认值兜底"声明一致，但方向性偏松，登记）：**补充发现 P3**——默认值全部朝"放行"方向（technical_pass=True 等），构造方漏字段=该维度失效，建议接线时强制显式构造。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
