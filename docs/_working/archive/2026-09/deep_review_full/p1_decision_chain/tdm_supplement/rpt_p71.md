---
ttl: task_bound
title: 深度审查作业簿——信号收集与六桶分类
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：信号收集与六桶分类（P71）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/sell_decision/core/sell_signal_collector.py:224`（SellSignalCollector.collect:281）
- TDM 节点: TDM-X-S1-01（stage，config/trading_decision_map.yaml:3241，activation: continuous）
- 生产调用方: **零**——`SellSignalCollector(` 全仓仅自身 docstring（:228）；header 声明的 MOD-SELL-002 评分器/MOD-SELL-007 融合引擎/D-POSITION 零实际调用；唯一"消费"=breakout_failure_detector import 其枚举（P52 已审对象）
- 测试文件: tests/sell_decision/test_sell_signal_collector.py（19 测试，105 passed 同批）

## 1 对象快照

- 范围：SellSignalCollector 全文件（327 行）——8 类信号类型枚举（架构硬边界）+SellSignal 契约（confidence [0,1]/timeframe 四周期）+Provider 协议+注册聚合+四元键去重（保留最高 confidence）+故障隔离。
- 排除项：各域 provider 实现（D-SIGNAL/D-RISK/D-PF-CORE 声明侧）；SELL-02 评分/SELL-05 融合（下游）。
- 测试覆盖概况：去重/跨周期/排序/隔离覆盖；**无"provider 全体失败"输出无标记场景**（本报告轴 E 发现）。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **"六桶分类"零承载+两套分类学并存**：TDM-X-S1-01 声明「8 类信号源聚合去重（本模块已实现）→**按六桶分类：止损/止盈/目标/移动/时间/波动**（分类决定后续走哪条判定链+确认模式）」——本模块 8 类（FUNDAMENTAL/TECHNICAL/VOLUME_PRICE/MAIN_FORCE/RELATIVE_STRENGTH/OPPORTUNITY_COST/TIME_STOP/BREAKOUT_FAILURE）与六桶（risk/signal/target/trailing/time/volatility，X-S1 hub 注释）是**两套不同分类学**，模块无桶字段无映射表，全仓亦无六桶承载件；"分类决定确认模式（止损立即执行/止盈等收盘）"的语义零代码。8 类聚合去重+timeframe 共振底座本身实现合格 | config/trading_decision_map.yaml:3241-3270（六桶声明）+3229-3233（X-S1 hub 六桶） vs sell_signal_collector.py:79-110（8 类枚举）；grep 六桶/risk桶/trailing 全仓零命中 | P2 | 对照两分类学逐项 grep；确认无桶映射表 |
| E | **provider 故障静默缺信号（决策面盲区）**：collect 对单 provider 异常仅 error 日志（:304-311），返回列表**无完整性标记**（哪些类型查过/哪些失败）——卖出信号管道缺一类 provider（如风控强制卖出 provider 挂掉）时下游照常评分融合，**缺失的卖出信号=漏逃逸风险**且只埋在日志；对照 P59/P65 的 escalation/告警纪律，此处缺失面无显影机制。隔离本身正确，缺的是"部分失败"的输出契约 | sell_signal_collector.py:300-312 | P2 | 注册 2 provider 其一恒抛，collect 结果与单 provider 时不可区分（探针） |
| C | 孤儿死码（checklist #8）：零生产调用方；[MATURITY] production 与"管道入口无人接"矛盾；8 类 provider 全仓零注册（协议定义无实现者） | sell_signal_collector.py:7；grep 证据见上 | P2 | `grep -rn "SellSignalCollector(" src/ --include=*.py` |
| A | 去重/排序数学（已核）：四元键（symbol/type/direction/timeframe）保留 confidence 最高者；#208-④ 修正（跨周期不去重保共振）留痕清晰；confidence 降序输出；[0,1] 校验在 SellSignal.__post_init__ | sell_signal_collector.py:176-184,316-327 | —（已核） | — |
| A | REPLACE 枚举语义确认（联动 P52）：SellDirection.REPLACE=置换（卖A买B）（:100）——**证实 P52 的 direction=REPLACE 占位"持有"是危险近似**：本枚举语境 REPLACE 是真实卖出动作，接线后按 direction 分流必误触发 | sell_signal_collector.py:95-101 | P2（归 P52 缺陷 2 的证据补强） | 读枚举注释 |
| B | provider 契约 timeframe/metadata 无规范：UNKNOWN 默认值兼容旧源，但"共振评分"依赖 timeframe 标注质量——provider 忘标→全部 UNKNOWN→共振永不触发（去重修正 #208-④ 的对称风险），无 UNKNOWN 占比告警 | sell_signal_collector.py:103-110,159 | P3 | 全 UNKNOWN 信号跑去重看共振输入退化 |
| A(亮点) | 8 类架构硬边界+扩展需架构评审（防类型膨胀）；frozen 值对象；协议+callable 双注册形态；单 provider 故障不阻断其余（隔离面正确，缺完整性标记而已） | sell_signal_collector.py:79-92,192-216,300-312 | — | — |

## 3 SOTA 对照

- 卖出信号聚合+分类学分桶：**对等已有（结构）**——多源信号汇聚→分类→分级处理是量化卖出系统常规架构（Investopedia Exit Strategy/Stop-Loss 族词条，investopedia.com，2026，同 P61 引）；本模块 8 类与 TDM 六桶应合并为"源类型×处置桶"两级（业界常见两层：source taxonomy→action bucket），当前两层只有一层半。
- 跨周期共振（同类型多 timeframe 共存评分）：**对等已有**——多时间框架确认（MTF confirmation）是技术分析标准化实践（TradingView MTF 指标族 tradingview.com，2026）；#208-④ 的去重修正方向正确。
- provider 隔离：**对等已有**——聚合器故障隔离是管道工程常规；业界对"信号面完整性"通常配心跳/覆盖率监控（与 P59 告警纪律同构）——本模块缺该层（本报告轴 E 发现）。

## 4 缺陷清单

1. **[P2] 六桶分类+确认模式分派零承载、与 8 类源分类学未映射**。建议修法：施工批次补 source→bucket 映射表（静态映射可生成器产出，防手工漂移）+确认模式字段；或 TDM 节点改注"六桶=下游 S1-02/03 判定链的分桶语义，本模块只承载源分类"。验证法：§2 轴 D grep。
2. **[P2] provider 部分失败无完整性显影（漏卖信号盲区）**。建议修法：collect 返回附 failed_types/coverage 字段（或失败即告警路由）；下游融合对缺桶降权。验证法：单 provider 恒抛探针。
3. **[P2] 孤儿死码+provider 协议零实现者**。建议修法：接线批次注册各域 provider（风控 provider 优先——它承载数据面最强卖出信号）；接线前降 draft。验证法：grep。
4. **[P3] timeframe UNKNOWN 占比无监控**。建议修法：collect 汇总 UNKNOWN 占比入事件/日志。验证法：全 UNKNOWN 探针。

## 5 挂起疑问

- 8 类源与六桶的映射裁定权在 Owner（例如 ④主力出货→risk 桶还是 signal 桶影响确认模式）；映射表定稿后建议生成器产出防漂移。
- 风控强制卖出经收集器汇聚（docstring :198 自称"风控信号优先级更高也经收集器"）与 X-S1-06 绕过通道（强制清仓不经融合直执行）的边界——风控信号若走收集器就被融合延迟，与 S1-06"绕过一切评分"矛盾面待 Owner 澄清（影响 P73 审查视角）。

## 6 完备性自评

六轴全查（A 数学四问：去重键/排序/置信度校验全过（无统计公式）、边界=空结果/全失败/跨周期已测；B 上游=provider 契约已查（timeframe 缺口已记）；C 下游=零调用方判孤儿+REPLACE 语义外溢证据（归 P52）；D=与 TDM 六桶对账（主发现）+与 SELL-002/007 分工声明核读；E 五问：静默失败=provider 缺失盲区（已立）、假阳性=无、断供=无心跳、重复触发=collect 幂等、时序=now 注入）。长尾：①SELL-02 评分/SELL-05 融合未审（各自对象）；②各域 provider 未来实现的质量无从预审；③19 测试逐断言抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
