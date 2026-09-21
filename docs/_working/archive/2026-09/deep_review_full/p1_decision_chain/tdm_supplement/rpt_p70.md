---
ttl: task_bound
title: 深度审查作业簿——护盘资产定向加仓白名单
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：护盘资产定向加仓白名单（P70）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/defensive_asset_whitelist.py:236`（evaluate_defensive_addition）
- TDM 节点: TDM-X-R1-03（stage，config/trading_decision_map.yaml:3202，D114 proposed 假说+ai_autonomy: paper）
- 生产调用方: **零**（仅包导出 position/core/__init__.py:43,56；header 自认 design+待接线；默认 enabled=False 休眠=D114 铁律）
- 测试文件: tests/position/test_defensive_asset_whitelist.py（105 passed 同批）

## 1 对象快照

- 范围：evaluate_defensive_addition 纯函数全文件（327 行）——熔断期窄门裁决：休眠门（enabled=False 恒拒）→方向门（只买）→白名单门（T1 宽基 ETF/T2 银行高股息）→状态门（仅 L2/L3）→信号门（D110 超跌反转或国家队明牌）→分批门（≤3 笔+第 2/3 笔确认收复）→预算闸（min(尾部弹药，总资金 10%)，每笔 1/3）。
- 排除项：KDJ/量比指标计算（调用方算好传入，:141 自划界）；D107 尾部弹药预算真源；drawdown_state_machine（熔断级上游）。
- 测试覆盖概况：九门短路/预算边界/Decimal 纪律覆盖好；无"第 2/3 笔信号门须再次全过"的组合场景（confirm 与信号门交互）。
- 材料包缺项声明：运行时证据包未取（design+休眠态）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| B | **CircuitLevel"真源指针"为幽灵引用（checklist #9 同族）**：枚举注释自称「真源=X-R1-01 drawdown_state_machine，本模块只消费不判定」（:54-55）——但 drawdown_state_machine 全文**无 L0-L4 枚举**（只有 NORMAL/WARN/DANGER/CRISIS/KILL 六态）；L-taxonomy 的 L1"日亏≥2% 禁加仓"等语义只存在于 TDM yaml 文本——"向内收禁第二定义"的目标未达成，L-taxonomy 实际真源=本模块这份转述+TDM 文本双份（P67 再 import 之，形成 文本→本件→P67 链）；且链上无人生产 L 级（P69 主发现的下游体现） | defensive_asset_whitelist.py:54-61 vs drawdown_state_machine.py:94-117（六态枚举无 L 级） | P2 | 并排读两枚举；grep L0-L4 在 drawdown_state_machine 零命中 |
| A | 分批/预算数学（已核）：cap=min(reserve_budget, capital×10%)；每笔=cap×1/3 ROUND_DOWN；3 笔恰好用尽 cap；remaining 减法精确；末笔 min(amount,remaining) 防超——Decimal 全程，无精度尾差；预算上限校验 (0,0.10] 锁死 D114 区间 | defensive_asset_whitelist.py:300-320,123-126 | —（已核） | — |
| A | 门②信号门第 2/3 笔不强制重验：TDM 分批门语义「第 2/3 笔必须**'确认收复'（三重门再次全过）**才放行」（config/trading_decision_map.yaml:3214-3216）——本模块第 2/3 笔只查 confirm_recovered 旗标+信号门仍跑（门②在门③前，仍生效）——信号门确实每次都跑 ✓，但"三重门再次全过"中的**状态门**（仍在 L2/L3）也跑 ✓——复核：门序休眠→方向→白名单→状态→信号→分批，第 2 笔时全链重走，confirm 只是附加旗标——语义实现正确（撤销本行疑虑，记录核读过程） | defensive_asset_whitelist.py:250-299；config/trading_decision_map.yaml:3214 | —（已核） | L2→L4 状态变化后第 2 笔请求看 LEVEL_GATE_FAIL |
| A | 白名单默认清单硬编码代码（DEFAULT_TIER1/2 :100-103，自注"经验拍定，config 可注入；启用前须随回测批核定"）——含具体代码 510300/510500/512100/510880/512800/512890：白名单来源固化（蓝图铁律）本应"来源固化"，硬编码在 .py 而非 YAML/配置真源，启用批时须迁移 config 注入（已自认，登记提醒） | defensive_asset_whitelist.py:100-103 | P3 | 读常量注释 |
| D | 与 TDM 声明的差异点：仓位"上限总资金 5-10%"（TDM :3208）vs 模块锁死 (0,0.10] 且默认 0.10（取上限）——TDM 写"5-10% 默认取上限 10%"一致 ✓；D110 信号阈值（KDJ J<-10/量比>2/无系统性利空）与 TDM 注释一致 ✓；"国家队明牌=ETF 天量成交/官方增持公告"枚举一致 ✓ | defensive_asset_whitelist.py:23-29,113-118 vs config/trading_decision_map.yaml:3202-3230 | —（已核） | — |
| E | 休眠铁律 fail-closed（enabled=False 恒 DORMANT，门 0 先于一切，:255-259）——对抗面最优设计：误启用需显式 config+回测批；方向门防 SELL 误入（白名单只买）；Decimal 拒 float/int/bool | defensive_asset_whitelist.py:255-264,204-207 | —（已防） | — |
| A(亮点) | 九 reason_code 全短路可审计；frozen 三件套同输入同输出；budget 负值/零资本/负分笔全拒；休眠门设计是 D114 纪律的机械化范本 | defensive_asset_whitelist.py:86-97,250-259 | — | — |

## 3 SOTA 对照

- 危机期定向护盘买入（国家托底信号+宽基 ETF 优先）：**对等已有（项目内实证链完整）**——TDM 注释已引 JFQA 2023/La Trobe 2025（NT 买入降波动 3.45-5.65%）、2026 半年报证金借道宽基 ETF 维稳实证、财联社九次出手七次见底复盘——项目侧证据链密度高于本报告可补充的外部源；外部同构实践=危机 alpha/逆势 ETF 吸筹文献（Alpha Architect 危机信号族 alphaarchitect.com，2019-2026，同 P59 引）。
- "政策底≠市场底"分批+确认铁律：**对等已有**——左侧买入分批与确认加码是仓位管理共识（Investopedia Scaling In，investopedia.com，2026，同 P60 引）；滞后 40 天~半年的历史量化（财联社复盘，经 TDM 转引）为 A 股特有实证。
- 熔断期例外买入通道（窄门）：**对等已有**——prop/机构风控在 daily limit 锁死期普遍禁开新仓、无买入例外（ClearEdge，clearedge.trading，2026，同 P69 引）——本项目的 L2/L3 窄门是**反共识的进取设计**（有 D114 证据链背书+休眠铁律约束），定位清晰：proposed 假说待回测。

## 4 缺陷清单

1. **[P2] CircuitLevel 真源指针幽灵化+L-taxonomy 无代码生产者**（与 P69 主发现联动）。建议修法：L-taxonomy 枚举迁往判定轴唯一真源（P69 修复裁定的承载件），本件 import 之；或改注释如实声明"真源=TDM-X-R1-01 文本"。验证法：并排读两文件枚举。
2. **[P3] 白名单默认清单硬编码 .py**。建议修法：启用回测批时迁 config/YAML 真源（自注已在案，防过期）。验证法：读常量。
3. **[P3] 国家队信号枚举二值化（NONE/两类）**：ETF 天量成交的"天量"阈值（多少倍量）无字段/无阈值——信号质量判定全推调用方，接线时须补量化定义（TDM 注释"ETF 成交量天量检测需 ETF 日线数据登记"已在案）。验证法：读 ReversalSignal/nt_signal 契约。

## 5 挂起疑问

- D110"超跌反转"与"国家队明牌"满足其一即放行——两信号质量不对称（前者技术性、后者政策性），是否需要加权或双确认，回测批设计时定。
- 窄门放行后的存量管理（TDM invalidation："窄门条件消失→停止后续批次，存量按 X 流管理"）无代码承载——第 2/3 笔的状态门会自然拦（L4 恒拒），但"信号失效停批"依赖调用方停止请求——编排契约待接线时书面化。

## 6 完备性自评

六轴全查（A 数学四问：cap/min/三分/ROUND_DOWN 逐个过、边界=零预算/满笔数/末笔截断已测；B 上游=ReversalSignal/nt_signal/reserve_budget 契约已查（天量阈值缺口已记）；C 下游=零调用方判孤儿（design+休眠诚实）；D=与 TDM 逐条对账基本一致+与 P67 CircuitLevel 共享链核查（主发现）；E 五问：静默失败=无（全显式 reason_code）、假阳性=无、断供=休眠铁律（已防）、重复触发=纯函数幂等、时序=无时钟依赖）。长尾：①D107 尾部弹药预算真源未审；②D110 指标计算端（KDJ/量比）未审；③ETF 日线数据源登记欠账（TDM 已记）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
