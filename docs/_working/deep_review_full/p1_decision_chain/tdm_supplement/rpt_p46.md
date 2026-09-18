---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——龙虎榜席位追踪
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：龙虎榜席位追踪（P46）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/limit_up/seat_pattern_analyzer.py`
- TDM 节点: TDM-E-L3-12-2（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-SIG-056/CAND-SEAT-001 MVP；v0.1 裁剪声明诚实（维度3/4/6 留 v0.2）
- 生产调用方: **0（grep 仅包 `limit_up/__init__.py:7` `__all__` 登记+邻件 lhb_premium_analyzer.py:29 正交声明；头注 [CONSUMERS] 自declared"MVP 阶段无"）**
- 测试文件: `tests/signal_ashare/limit_up/test_seat_pattern_analyzer.py`（17 用例，本班次实跑 17/17 绿）

## 1 对象快照

348 行三件套分析器（席位画像/席位联动/跟随信号）：seat_registry.yaml 15 席位档案精确名+别名匹配（未命中回退 provider 粗分类）；联动=类型共现四标签+买一买二集中度；跟随信号=基准 50 分加减分制（机构+15/知名游资+10/量化主导−20/散户主导−15/独食−10/资金力度±10/结构±5→long≥60/avoid≤40）。数据契约 pydantic 校验（金额 ge=0/排名 1-5）；空数据/多票多日混入 fail-closed 或 degraded=True 不臆造（:8 不变量落地）。测试覆盖：三件套+降级+契约违规。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：加减分制封闭可追溯（reasons 理由链 :124 全程留痕）；净买占比/集中度公式正确；三档方向阈值单调（60/40）；score 钳制 [0,100]（:303） | seat_pattern_analyzer.py:250-310 | 通过 | 分数路径手推 |
| A 深度 | 分母语义②：strong/weak_net_buy_ratio（10%/5%）分母=`Σ(top5 buy+sell)`（:337）而非个股全天成交额——"净买入占比>10% 强势"实际是"占龙虎榜五席买卖和"占比，口径与 seat_registry 框架"资金力度"维的本意是否一致无标定记录；分母选择对阈值有效性一阶影响 | :142-143,337,285-291 | P3 | 对照 seat_registry.yaml §seat_analysis_framework 维度2 定义 |
| A 深度 | 边界③：NaN net_amount 可过 pydantic（无 ge 约束字段 :85）→ 加减分条件全 False→score 恒 50=静默 NEUTRAL（毒数据伪装中性，非 degraded）——与"无数据 degraded=True"纪律相比 NaN 走了静默通道 | :85,264-291 | P3 | 造 NaN net_amount 记录观察 NEUTRAL+degraded=False |
| B 上游 | checklist #6 断供：records 注入（DS-080 东财口径 :33）；registry 缺失/坏 YAML→warning+空档案降级（:162-170）——**seat_registry 全空=全部席位 unknown 回退 provider 粗分类，画像降级无 degraded 标记**（registry 断供与数据断供的降级不对称：后者有 degraded 前者只有日志） | :162-170 | P3 | 移走 registry 路径观察 profiles.matched_registry 全 False |
| C 下游 | **孤儿裁定：生产零调用方**（候选消费方 daban 类策略/席位溢价因子均未接线）；爆炸半径=跟随信号误用→打板接力误跟（avoid→long 方向错误=次日接盘）；degraded 标志语义清晰（信号不可用于决策 :135） | grep 证据 | P1(接线期) | `grep -rn "SeatPatternAnalyzer(" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：与 lhb_premium_analyzer（P10 域，席位溢价）正交声明互认（:29-30"056 管谁在买/溢价管溢价"）；席位类型词表（institution/youzi/quant/northbound/retail/connect/broker）与 P45 四线（主力/机构/散户/游资）为两套分类法——**席位分类 vs 资金线分类无映射桥**（跨件对账时须统一或映射）；seat_registry.yaml 单点承载正确（YAML 真源） | lhb_premium_analyzer.py:29-30 | P3 | 对照两分类词表 |
| E 对抗 | 五问：①静默失败=NaN→NEUTRAL（上述）；registry 断供仅日志②假阳性=知名游资跟风——registry 15 席位白名单+风格字段 null（:34"history_win_rate/avg_premium 当前 null"）=**风格匹配用 style 白名单但胜率数据缺位，+10 分无实证背书**③断供=degraded 纪律好④重触发幂等⑤时序=单日快照无时序面 | :34,267-274 | P3 | 查 seat_registry.yaml 胜率字段 |
| F 新鲜度 | 龙虎榜席位跟随为 A 股本土独有信息面（交易所披露制度产物，英文文献无对应物——S05/policy §F.2 中文研报独立矿脉）；"主力资金=大单分类噪声明代理"的教训同样适用于席位身份识别精度（registry 覆盖 15 席 vs 全市场营业部数万=覆盖率极低，未命中即 unknown 主导）；**对等已有（本土语境，声明式）** | 本土结论；分类噪声对照见 rpt_p45 F 轴 URL（Tsinghua PBCSF） | 通过（声明式） | — |

## 3 SOTA 对照

- 对等已有：席位身份/联动/跟随三段式为 A 股龙虎榜数据工程常规；无英文 SOTA 对照面（不适用声明）。
- 立卡候选：registry 胜率字段回填（history_win_rate）+席位覆盖率统计——v0.2 规划项与维度6 连续性同批。

## 4 缺陷清单

1. P1（接线期）：零生产调用方孤儿（头注自declared MVP 无消费方）；验证法=§2 C 轴 grep。
2. P3：NaN net_amount 静默 NEUTRAL 通道（与 degraded 纪律不对称）——建议 pydantic 加 allow_inf_nan=False；验证法=§2 A 轴构造。
3. P3：net_buy_ratio 分母=top5 买卖和（非全天成交额）的口径未在 seat_registry 框架层标定；registry 断供降级无 degraded 标记。

## 5 挂起疑问

- DS-080（market_data.lhb_detail）东财口径 ingest（JOB-076）与 SeatRecord 字段契约的映射对账未做（provider_seat_type 三值粗分类的映射质量未知）。

## 6 完备性自评

六轴全查（F 本土声明式+同族复用 P45 检索）。长尾：①seat_registry.yaml 15 席位档案内容本身未审（数据件非代码）②评分权重（+15/−20 等）无标定依据③17 测试无 NaN/registry 缺失 case。

## 7 收口裁定（收口方填）
