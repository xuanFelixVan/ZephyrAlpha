---
ttl: task_bound
title: 环节⑤ 环境闸门——三级放行/水温响应与两态班对接面
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 环节⑤ 环境闸门读数（大盘两态×情绪水温→板块操作允许矩阵）

> **目标形态**（研究册 §1.2⑤）：大盘两态 × 情绪水温 → 板块操作允许矩阵；环境不允许=全信号降档。⑤是①-④全部输出的前置门。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|------|------------------|---------|--------|------|---------|
| sector_gate（三级放行+水温响应） | src/zephyr/signal_ashare/sector/sector_gate.py 全读（170 行三函数）：:17-31 设计说明（准入 gate v2.1：Top3 次日重合率 14.8% 板块一日游实证→降阈 0.70/0.90→0.60/0.80）；:82-88 _WATER_TEMP_TABLE（NEUTRAL 全权重/RISK_ON ×0.5/PANIC_REPAIR 仅改善象限+放宽/RISK_OFF 仅领先+收紧/CRASH 全拦截）；:117-150 admission_gate（CORE_HOT 直通/SECONDARY 次优+强度≥0.60/WILDCARD 超强个股≥0.80）；:153-169 apply_rrg_filter | 🔨 new（MOD-SIG-026 supplement，22 号 §3.1⑩⑪） | TDM-E-L2-05-2/L2-06-1 双挂；头注待 G05 漏斗准入层 | **水温档本身不判定**（头注明示归 regime 10 号/情绪周期 28 号）；阈值 v2.1"初拟待 G05 回测验证（spec §6 待裁定）" | ①水温上游 ②G05 漏斗/RRG 过滤 ③查表映射+三级门槛 ④已落码 ⑤- ⑥水温档输入⬜ |
| WaterTemp 五档→上游桥接 | sector_gate.py:54-61（NEUTRAL/RISK_ON/PANIC_REPAIR/RISK_OFF/CRASH）＋:55 注释"上游 regime 12 态+情绪周期 5 阶段桥接，本模块不判定" | 🔨 词表已闭合 | sector_gate 内部 | **桥接规则件不存在**（grep 桥接/映射零命中）：regime 12 态+情绪 5 阶段→WaterTemp 5 档的归并表⬜ | ①regime/情绪 ②gate ③归并映射 ④⬜ ⑤- ⑥上游在 |
| CONSENSUS_CLIMAX 双重抑制 | sector_gate.py:94-113（RISK_ON+共识高潮→weight 0.5×0.5=0.25）；高潮判定源=sector_rotation_state CONSENSUS_CLIMAX（rotation_state.py:55） | 🔨 已落码 | - | 跨件耦合（gate←rotation_state）已锚定，无缝 | ①rotation_state ②gate ③乘法抑制 ④已落 ⑤- ⑥- |
| sentiment_cycle（水温档真源候选一） | src/zephyr/signal_ashare/sentiment/sentiment_cycle.py:6-13（new；PHASE_DISCIPLINE/STRATEGY_DEPLOYMENT_MATRIX 覆盖全 5 阶段） | 🔨 new | TDM-E-L2-05-1 | 5 阶段→WaterTemp 5 档语义不同（冰点~退潮 vs NEUTRAL~CRASH），归并表同缺 | ①情绪序列 ②⑤环节 ③5 阶段 ④已落 ⑤- ⑥- |
| emotion_index（板块热度不回灌防循环） | src/zephyr/data/sector_state_pipeline.py:13-14（"偏好重映射消费 emotion_index@T close_final——晚于情绪班落库时点，无竞速"）＋alt_data/emotion_index_builder.py:7（experimental；板块热度不回灌防循环红线在头注） | ✅/🔨 落库链在产（builder experimental） | state_pipeline 偏好腿 | - | ①六成分 ②偏好重映射 ③滚动分位 ④已落 ⑤- ⑥- |
| 两态班输出（大盘腿） | 班外：st-formreg-20261013（00_inputs/formreg_survey_2026_10_13.md §12：condition_package 大盘腿升级、不另立平行条件轴） | ⬜ 班产待交 | ⑤ 大盘腿输入 | **对接面已约定未交货**：两态层输出作为 condition_package 大盘腿（formreg 册 §12.3-2） | ①regime 46py 复用 ②condition_package ③jump model 候选 ④班外 ⑤- ⑥7 维概率在 |
| 情绪输出契约 v0（L1-L4 四层） | 00_inputs/2026-10-13-sentiment-output-contract-research.md §7.1（L1 温度连续灰度→预算带/考试条件轴；L2 相位唯一词表=官方六段；L3 事件→大盘班拐点确认器；L4 预测面） | ⬜ 契约待批（v0 draft） | ⑤ 水温腿输入 | 契约未批→⑤的 L1 消费规格未冻结 | ①五层资产 ②预算带/条件轴 ③四层定义 ④⬜ ⑤- ⑥- |
| sector_ecology_judge（板块级市场状态） | src/zephyr/signal_ashare/core/sector_ecology_judge.py:6-16（design，MOD-SIG-143；三态 MAINLINE_CLEAR/CLIMAX/CHAOS 封闭；CLIMAX>MAINLINE_CLEAR>CHAOS 风险优先；阈值全部取自已锚定模块文档值非自创） | 🔨 design | TDM-E-L2-04；L3-06 环境开关（待接线） | 板块级三态≠大盘级两态——层级关系（⑤管大盘×水温，ecology 管板块生态）须在路由册写明防混 | ①candidates+rotation_state ②TDM-E-L2-04 ③封闭三态 ④已落码 ⑤- ⑥齐 |

## §2 与既有资产边界

- **复用**：sector_gate 三函数+ecology_judge 判定核+sentiment_cycle 全部原样；condition_package 分层口径（Owner 2026-09-23 夜裁①）原样——⑤不另立平行条件轴（formreg 册 §12.3-3 同纪律）。
- **换参**：gate 阈值 v2.1（0.60/0.80）从"初拟"换 G05 回测校准值（22 号 spec §6 待裁定项——施工时走考试卡流程，禁手工拍）；WaterTemp 归并表=换参级新件（词表归并非新算法）。
- **新建**：仅一件——**regime 12 态+情绪 5 阶段→WaterTemp 5 档归并表**（声明态规则数据落 YAML，对齐键=语义；待两态班与情绪契约交货后填值，架子可先立）。

## §3 施工要点

1. **三段归并链防串台**：大盘两态（formreg 班出）×情绪水温（sentiment 契约 L1/L2 出）×板块生态（ecology_judge 三态）——三源三层各有词表，⑤施工第一件事=三词表→WaterTemp 单归并表（防第 29 套词表，formreg 册 §12.3-3 原话同引）。
2. **gate 的"先 gate 后 weight"次序是硬语义**（:8 INVARIANTS + :19 设计说明）：三级门槛判定在前、水温降权在后——归并表施工禁把水温做成第四级 gate。
3. **14.8% 板块一日游实证**（:19-21）是阈值降档的唯一依据——G05 回测校准时的对照组基线，考试卡要带该数字出处。
4. **emotion_index 时序无竞速设计**（state_pipeline 头注：偏好腿消费 @T close_final 晚于情绪班落库）——⑤施工若引入盘中水温滚动（L1 盘中滚动可选），须重做时序竞速审查。
5. **CRASH 档阈值 1.01/1.01 的写法**是"结构性全拦截"实现（score∈[0,1] 恒小于阈值）——归并表禁复用该魔法数，显式 rrg_filter=NONE 已表达语义。

## §4 自审闸三态裁定

**裁定：施工**（归并表架子先行，值冻结挂两态班/情绪契约交货）——理由：⑤是五件套前置门且 gate 主件已落码（170 行三函数全读无坑），缺的只是上游归并——消灭"环境判断靠 Owner 盘中口令"的最后一处人工参与，终局有位。阈值校准（G05）与契约冻结依赖班外交货，按挂起排期纪律登记解锁条件。
