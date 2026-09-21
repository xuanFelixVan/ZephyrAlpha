---
ttl: task_bound
title: 深度审查作业簿——打板选股链
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：打板选股链（P37）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_core/strategies/daban_sleeve_strategy.py`
- TDM 节点: TDM-E-L3-07-1（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-L05-001，21 号 memo §3.5/§3.6 施工
- 生产调用方: **有：`pf_core/strategies/__init__.py:24,36`（lazy re-export）+ `framework_composer.py:1886`（daban-sleeve MemberPayloadRoute 路由注册）+ 自带默认持久化读源（DatabaseService reader 真读 c1_market.daban_engine_load，"产而不消"治理已接线）——非孤儿**
- 测试文件: `tests/pf_core/test_daban_sleeve_strategy.py` + `test_daban_sleeve_strategy_load.py`（51 用例，本班次实跑 51/51 绿）

## 1 对象快照

670 行 sleeve 组装策略：四引擎流水线（资格门 BM-SEL-22→游资情绪 23→量化强度 24→双引擎融合 25）×6 类决策优先级权重表→Top-N（≤10 硬约束）比例归一+max_single 截顶。工程纪律突出：PIT 双保险（SQL 谓词 trade_date<as_of + 代码级逐行剔除）、fallback 恰好一条 WARNING 点名披露、1970 哨兵防 CH 空表 max()、表名/列序真源 import 非复制、产而不消治本（默认持久化消费源）。测试覆盖：四引擎流水线/负载读源/PIT/回退披露。排除项：四引擎内部深审（P33 本批、其余各自域）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：`final_score=fused×priority` 与 21 号裁定表一致（:84-91 六类权重、中性→0 剔除）；归一化+截顶只减不增（:457-458）权重和≤1.0 不变量成立；Top-N 截断前 `score>0` 过滤（NaN score 落 False=静默剔除，fail-safe） | daban_sleeve_strategy.py:84-91,444-458 | 通过 | 手算 3 标的截顶场景 |
| A 深度 | **边界②实锤：`row_to_engine_payload` 仅查 None 不查 NaN——实测 stock_change_pct/seal_amount/market_breadth_ratio 喂 NaN 全部原样穿透（`float(nan) if x is not None else 0.0` 模式:523,516-518,528,531,546）→ 直入 P33 已实锤的 NaN 评分洞→fused=NaN→本层 `score>0` False=该股静默出局（无日志）**；数据面单字段 NaN=该标的当日无声消失；与 cap 字段的 `_maybe_positive`（:143-153 全防御）形成同函数族两种纪律的对照 | :143-153,516-531,543-548 | P2 | 本班次实测：`row_to_engine_payload({...,'stock_change_pct':float('nan')...})`→quant.stock_change_pct=nan |
| A 深度 | PIT③：SQL 谓词+代码级双保险（:319-321）、1970 哨兵（:291）、回退单条 WARNING（:325-341）——**当前最好的 PIT 纪律范本**；跨lane证据：TF07 已登记"日频消费←周频生产名义 DAG 边（周二至五回退上周事件日）"——本模块 fallback 披露机制正是该场景唯一防线，回退滞后天数日志可作运营监控指标 | :291,319-321,325-341 | 通过（附跨lan风险引用） | 跑 build_weight_panel_for_dates 造 T-1 缺分区观察 WARNING |
| B 上游 | checklist #6 断供：负载读空→显式 skipped WARNING 非静默零（:611-616）；读库异常→降级空行同分支（:284-286,310-312）——断供有痕；**上游生产节奏失配（TF07：周频生产 vs 日频消费）未在本模块显式感知**——仅靠事后 WARNING，无"分区滞后>N 天"升级告警 | :611-616 | P2(跨lan协同 TF07) | 对照 TF01-TF15 报告 TF07 行 |
| C 下游 | 输出权重面板被 composer 路由消费（:1886）→组合权重；`select()` 的 confidence=占位（权重和，:662-667 声明诚实"非定稿置信度"）；NaN 静默剔除的下游效应=sleeve 容量无故缩水（本应入选的涨停股消失）且无统计 | :662-667 | P3 | — |
| D 旁系 | checklist #4 双承载：`_DECISION_PRIORITY` 六类权重表（:84-91）与 21 号 memo L304-317 文档承载——文档↔代码逐值一致（已对码）；与 P33 的 6 类分类词表（主升龙头/二进三/...）字符串硬编码耦合（:493 `fusion_res.decision` 中文字符串查表）——枚举漂移=全表失效落 0（fail-safe 方向）但无编译期保护 | :84-91,493 | P3 | 对照 21 号 memo L308-315 |
| E 对抗 | 五问：①静默失败=NaN 静默出局（上述实锤）；其余降级/skipped 全有日志②假阳性=资格门可选跳过（selector 缺省=不设门，:507-509 声明为挖矿 LUE-1 实证的契约决定）——payload 路径恒无资格门，机构输入缺失时 sleeve 无第二道防线（已文档化取舍）③断供=断供有痕④重触发幂等（面板函数纯读）⑤时序=PIT 双保险+回退披露，时序攻击面最全 | :507-509 | P2(同 NaN 案) | — |
| F 新鲜度 | 打板/涨停板情绪周期策略为 A 股本土特色玩法，英文文献无对应物（中文卖方金工与游资研究为独立矿脉，policy §F.2 认可）；四引擎集成+优先级加权排序为工程组合创新；**对等已有（本土矿脉）** | 本土语境结论（英文 SOTA 不适用声明） | 通过（声明式） | — |

## 3 SOTA 对照

- 对等已有（本土）：涨停板情绪周期选股为 A 股特色域，四引擎组装实现完整；无英文 SOTA 对照面（不适用声明）。
- 立卡候选：分区滞后升级告警（fallback WARNING→连续 N 日滞后升级 WARNING+晨报）——与 TF07 挂起项合流。

## 4 缺陷清单

1. P2：**payload 构建 NaN 穿透（实测三字段）×P33 NaN 评分洞=复合静默剔除链**——建议 `row_to_engine_payload` 复用 `_maybe_positive`/新增 `_maybe_finite` 统一清洗（NaN→省略键交引擎默认），并在剔除时 debug 留痕；验证法=本班次实测一行（§2 A 轴）。
2. P2（跨lan）：上游 daban_load 生产节奏与日频消费失配（TF07 已挂起晨报置顶）——本模块仅事后 WARNING 无升级机制；建议与 TF07 合并裁定（生产侧治本优先）；验证法=对照 TF07 报告。
3. P3：决策词表中文字符串硬编码查表（:493）无枚举保护；P3：占位置信度=权重和（声明诚实但语义弱）。

## 5 挂起疑问

- `select()` 接口（SignalInput 路径）在 composer 链路中是否实际被调用（面板路径已证活跃，select 直调路径 grep 未见生产消费）——若死路径建议标注。

## 6 完备性自评

六轴全查（F 本土不适用声明）。长尾：①四引擎中 youzi/fusion/selector 三件未深审（非本批对象）②c1_market.daban_engine_load 表数据质量画像未做③max_single=0.15 与资金分配层（C01-C05 域）的单票上限是否同源未对账。

## 7 收口裁定（收口方填）
