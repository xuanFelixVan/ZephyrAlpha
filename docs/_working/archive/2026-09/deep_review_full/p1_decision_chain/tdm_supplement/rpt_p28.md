---
ttl: task_bound
title: 深度审查作业簿——催化剂识别
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：催化剂识别（P28）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/screening/event_driven_screener.py`
- TDM 节点: TDM-E-L2-09（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）
- 生产调用方: **0（全仓零 import；上游邻件 fine_scoring_engine.py:5 头注自证"经 2026-09-05 AI-08 审计实证未接线——接线待排期"）**
- 测试文件: `tests/signal_ashare/screening/test_event_driven_screener.py`（18 用例，本班次实跑 18/18 绿）

## 1 对象快照

185 行纯函数筛选器（MOD-SIG-049，选股漏斗第四层 ~50→~30）。三重门控：置信度 ≥0.7→利空 direction<0 剔除→极端反应 |reaction|>3% PEAD 反转剔除；另传导链风险 >0.7 剔除；保留者按 `1+direction×strength×2^(−age/半衰期)` 衰减权重降序截断至容量 30。skipped（无事件源）/degraded（仅剔利空）两降级路径。头注 [MATURITY] production 与"待接线"现实矛盾（checklist #8 同案）。测试覆盖：门控/降级/截断主路径，断言精确。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学四问①：指数衰减权重 `1+d×s×2^(−age/hl)` 形式正确（age≥0 时权重∈[1,2]）；半衰期按事件类查表与 memo §2.4 经验区间中点一致（EARNINGS 4d/MERGER 2d/POLICY 5d/GEO 10d 等） | event_driven_screener.py:65-72,124-128 | 通过 | 手算 age=hl→decay=0.5 |
| A 深度 | 边界②：**age_days 无非负校验——负年龄使 2^(+|age|/hl) 无界膨胀，实测 age=−50→权重 2897.3**；strength 无 [0,1] 校验（实测 strength=2→权重 3.0）；两者均为上游契约（:107"盘后事件 T+1 起算"）未防御，静默扭曲容量截断排序 | :104-107,124-128 | P3(接线期必修) | 本班次实跑：`_event_weight(EventImpactRecord(direction=1,strength=0.5,age_days=-50))`=2897.3 |
| A 深度 | 容量截断③：`sorted(key=(-weight, symbol))` 确定性平局裁决（:176）——同权重按 symbol 字典序，无随机性；checklist #1 无分母问题（breadth=positive/len 非统计口径漂移风险） | :176 | 通过 | — |
| A 深度 | A 股口径④：利空仅剔除不做空（宪章约束三）与 A 股单边多头机制一致；PEAD 极端反应不追涨（极端正向 20 日中位 −5.58% 反转）为 A 股打板/追高语境的经验值 | :21-24,163-165 | 通过 | — |
| B 上游 | checklist #6 断供：事件源断供→`event_source_ready=False`→skipped 直通全量放行+权重恒 1.0（:146-151）——**非恒 0 但"直通"是 memo 契约明文降级**（"没事件数据源就跳过"），与北向加零案不同：此处选择中性放行而非伪信号，方向正确；但直通=事件筛选层失效无统计留痕（skipped 标志有，告警无） | :146-151 | P3 | 传空事件源观察 skipped=True |
| C 下游 | **孤儿裁定：生产零调用方**（邻件头注互认未接线：fine_scoring_engine.py:5、causal_inference_engine.py:5"无 import 依赖"解耦设计）；MATURITY=production 虚标 vs 现实未接线——成熟度标签失实（V06/D15 同族案）；爆炸半径=漏斗第四层缺位，~50 直通 ~30 由他层代偿 | grep 证据 | P1(接线期)+P3(标签) | `grep -rn "from zephyr.signal_ashare.screening.event_driven_screener" src/ --include=*.py` |
| D 旁系 | checklist #4：无第二份事件衰减权重实现（grep `2^|halflife|event_halflife` 全仓唯一）；六类半衰期表与 intelligence/event_funnel.py 骨架的契约（方向/强度/年龄字段名）经头注互认一致（event_funnel.py:51）；algo_flow yaml 已外迁未逐条对账（长尾） | event_funnel.py:51 | 通过 | grep 对照 |
| E 对抗 | 五问：①静默失败=降级路径 skipped/degraded 均有标志字段但无日志/告警出口②假阳性=置信度门控把低置信事件"视为无事件"后**该股保留且权重 1.0**（:171 else 1.0）——无事件股与低置信事件股同权，语义自洽；conduction_risk 对无事件股也生效（:166-167 默认 0 不剔除，装配方必须显式置 0 才安全——隐式契约：未装配传导链风险的记录默认 0=安全侧，方向正确）③重触发幂等（纯函数）⑤时序=age_days 由上游负责，见 A 轴边界发现 | :146-151,163-171 | 通过（附 A 轴 P3） | — |
| F 新鲜度 | PEAD（post-earnings announcement drift）+ 极端反应反转剔除与行为金融文献方向一致（PEAD 经典 Ball&Brown 1968 谱系；A 股 PEAD 存在性有中文卖方研报独立验证——本条为方向性对照非数值背书）；事件衰减半衰期建模对齐业界事件驱动框架的 decay 处理=**对等已有** | WebSearch 2026-09-18（PEAD+extreme reversal family） | 通过 | — |

## 3 SOTA 对照

- 对等已有：PEAD 方向性利用+极端首日反应反转过滤，与学界 PEAD 谱系及 A 股量化实践方向一致。
- 对等已有：事件影响指数衰减（半衰期按事件类分档）为事件驱动选股常规处理。
- 立卡候选：事件半衰期 3-5/1-3/5-15 天等"经验区间"建议接线前用本项目事件表实证重估（源码:64 自declared"初拟待校准"）。
- 驳回：无。

## 4 缺陷清单

1. P1（接线期）：**零生产调用方孤儿+MATURITY=production 虚标**（checklist #8；V06/D15 同族"标签失实"案）。建议=接线或改标 testing；验证法=§2 C 轴 grep。
2. P3（接线期必修）：age_days<0 与 strength∉[0,1] 无防御→权重无界膨胀扭曲截断（实测 2897.3）；建议=入参 raise 对齐 ERROR_CONTRACT 风格；验证法=本班次实测命令见 §2。
3. P3：skipped/degraded 降级仅落 dataclass 标志，无告警通道——断供期事件层静默失效（#6 语义）；建议=接线时在编排层消费 skipped 标志告警。

## 5 挂起疑问

- conduction_risk 对"无事件标的"是否应生效（现设计：默认 0 不剔除，装配方显式给值才生效）——语义合理但头注未写明，建议接线裁定后在头注补契约。

## 6 完备性自评

六轴全查（F 走 PEAD 家族检索）。长尾：①algo_flow yaml（event_driven_screener.yaml）未逐条对账②置信度 0.7/极端 3%/传导 0.7 三阈值均初拟无校准记录③`EventImpactRecord.direction` 用 int（±1/0）而非枚举——调用方传 2 时权重膨胀 2 倍无校验，留接线期收紧。

## 7 收口裁定（收口方填）
