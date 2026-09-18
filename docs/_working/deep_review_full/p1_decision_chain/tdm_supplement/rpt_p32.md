---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——Universe构建与剔除
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Universe构建与剔除（P32）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/instrument_master.py`
- TDM 节点: TDM-E-L3-01（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；90 号 Phase2 交付物
- 生产调用方: **0（grep 仅自命中+reference_data_manager.py:25 头注互认文本；头注自declared"盘前 xtdata 同步脚本接线待排期"）**
- 测试文件: `tests/data/test_instrument_master.py`（9 用例，本班次实跑 9/9 绿）

## 1 对象快照

125 行轻量 IM（MOD-DATA-069，裁定 90 号 §18 v2.0.0）：两份 ClickHouse DDL 常量（主表 ReplacingMergeTree(updated_at) ORDER BY symbol + ST 状态 PIT 子表 ORDER BY (symbol, effective_date)）+ 必填字段集 + `normalize_instrument_row` 行规范化（必填缺失/exchange∈{SH,SZ,BJ}/board∈{main,star,gem,bse} 校验，min_order_unit 按板块派生 main/gem/bse=100、star=200）。范围界定：**仅模块本体，Universe 构建筛选逻辑本身不在此文件**（TDM 节点 E-L3-01 的"构建与剔除"语义由未来接线层承载——节点映射与文件能力存在名实差距，见 D 轴）。测试覆盖：必填/非法枚举/默认派生。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：无算法公式；DDL 设计=ReplacingMergeTree 版本列去重与项目 PIT 语义一致（:44 注释）；ST PIT 子表 (symbol, effective_date) 排序键支持追溯查询（裁定③防幸存者偏差）设计正确 | instrument_master.py:45-76 | 通过 | — |
| A 深度 | 边界②：必填缺失/非法 exchange/非法 board 全 ValueError（:111-120）；但 **security_type 未做枚举校验**（DDL 注释声明 stock/etf/lof/reits/cb 枚举 :49，ERROR_CONTRACT:13 称"非法枚举→ValueError"——枚举校验只覆盖 exchange/board 两个，security_type 裸过）=契约与实现差距 | :13,49,111-120 | P3 | `normalize_instrument_row({'symbol':'X','exchange':'SH','security_type':'bogus','board':'main','list_date':'2020-01-01'})` 观察 ValueError=否 |
| A 深度 | A 股口径③：**board→min_order_unit 映射按板块一刀切（:91-96），科创板 ETF（588xxx，100 股申报）若 board=star 会被派生 200 股=废单风险**；现无接线未爆发；另 gem 涨跌幅 20% 与 main 10% 在注释"±10%/20%/30%"三值四板块的简写下无机械承载（涨跌幅表未实现，消费方各自为政风险） | :24,50,91-96 | P2(接线期) | 构造 board=star+security_type=etf 行观察 min_order_unit=200 |
| B 上游 | checklist #6 断供：模块无数据源依赖（DDL+纯函数），断供不适用；上游=盘前 xtdata 同步脚本（未建）——字段映射契约（"数据源字段已映射为 IM 字段名" :104）为隐式约定无映射表，接线时漂移风险 | :99-110 | P3 | — |
| C 下游 | **孤儿裁定：生产零调用方**（头注自declared 接线待排期+B-007 宪章纪律挂 Owner）；universe_registry eligibility 联动（#15）同为规划态；爆炸半径=Universe 层缺位由消费方自行判断板块/ST/上市日期 | :5-6,29-30 | P1(接线期) | `grep -rn "normalize_instrument_row\|INSTRUMENT_MASTER_DDL" src/ scripts/ --include=*.py` |
| D 旁系 | checklist #4 双承载：reference_data_manager.py:25 头注声明查重裁定（IM 为轻量唯一承载）——双承载嫌疑裁定=无（有查重裁定留痕）；板块/涨跌幅知识在 tradability_preflight（P42）等处另有承载，待该对象审查时交叉核对 | reference_data_manager.py:25 | 通过 | 交叉读 P42 报告 |
| E 对抗 | 五问：①静默失败=normalize 派生默认值无留痕（min_order_unit 被补默认时无标记区分显式/派生）②假阳性=security_type 不校验（见 A 轴）③断供=N/A④重触发幂等（纯函数）⑤时序=updated_at 由写入方填，DDL 无 DEFAULT now()——由调用方负责，契约未写 | :123-124 | P3 | — |
| F 新鲜度 | 轻量 IM 最小字段集 vs 机构级 200+ 字段证券主档：轻量路线与开源证券数据基建实践（如 tushare/akshare 字段子集+自建 PIT）对等；无独立统计算法=**对等已有（工程选型）**，无 SOTA 立卡点 | 受限对等结论（工程选型无学术对照面）；检索预算已投 Cohen-Frazzini/PEAD/供应链族 | 通过（选型对等） | — |

## 3 SOTA 对照

- 对等已有：轻量最小字段集+ST PIT 子表为 A 股量化自建证券主档的常规做法（ST 状态 PIT 防幸存者偏差为本地化正确设计）。
- 立卡候选：涨跌幅/最小申报单位规则表结构化（board×security_type 二维）——接线时顺路建，避免 588ETF 类废单。
- 驳回：无。

## 4 缺陷清单

1. P2（接线期必修）：board→min_order_unit 一刀切映射对 star 板 ETF（588xxx 100 股申报）派生错误值→下单废单；建议=映射键改 (board, security_type) 二维；验证法=`normalize_instrument_row({...,'board':'star','security_type':'etf'})` 观察 200。
2. P1（接线期）：零生产调用方孤儿（头注诚实 declared"接线待排期"）；Universe 构建/剔除本体（筛选规则）尚无承载文件——TDM 节点名实差距需接线层补齐；验证法=§2 C 轴 grep。
3. P3：security_type 枚举零校验 vs ERROR_CONTRACT"非法枚举→ValueError"名实差；P3：DDL `updated_at DateTime` 无时区无精度（全仓 data 域 DDL 同族模式，与 RULE-SCHEMA-TZ"DateTime64(3)+显式时区"口径存在家族级差距——宜族级统一裁定非单件修）。

## 5 挂起疑问

- TDM-E-L3-01 节点"Universe构建与剔除"映射到本文件是否恰当（本件只承载主档数据面，筛选逻辑面空缺）——建议收口方核对 TDM 节点 module_ref 语义。

## 6 完备性自评

六轴全查（F 为工程选型对等结论+检索预算约束声明）。长尾：①DDL 未在真实 CH 实例 apply 验证（无接线）②北交所 30% 涨跌幅与 bse=100 股申报的边界（超额卖出零股一次性）未承载③float_shares 更新频率/来源未约定。

## 7 收口裁定（收口方填）
