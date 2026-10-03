---
ttl: task_bound
completes_when: 图15 立项过 Owner 批（或否决）后转正式施工批文，本卡归档
title: 图15 策略卡生命周期图·立项卡（状态机形态）
owner: ZephyrAlpha-Owner
---

# 图15 策略卡生命周期图 立项卡

## 1. 一句话定位

一个策略假设的一生：预注册（立军令状）→开测→考卷 RED/GREEN→重判一次→封卡 SEALED→复活唯一口=预注册新卡——状态机全景图化。

## 2. 四道门过审（裁定#409）

| 门 | 论证 | 判 |
|---|---|---|
| ①独立触发+终点 | 触发=新策略假设立项；终点=封卡/复活新卡。横跨数月生命期，非单次流程 | PASS |
| ②跨模块交接 | prereg 卡（docs）→考试引擎（C4/成本门/E7 换手门）→trial_ledger N 台账→experiment_registry→裁定册（#363/#399/#304）。四处真源三种介质 | PASS |
| ③不被现有图覆盖 | 工厂图（图9）管"车间流水线"（候选→批量生产）；本图管"单卡一生"（状态机）。工业类比：产线图 vs 工件随件卡。E4 考试咽喉在图9 是站点，在本图是状态迁移触发器 | PASS |
| ④机生真源 | 现状=卡状态散在 md 头+experiment_registry 枚举+trial_ledger 计数，**无单一登记面**——前置件：卡状态登记面（见 §3） | 条件 PASS |

## 3. 前置施工件：卡状态登记面（schema）

- 登记面=experiment_registry.yaml 扩枚举（禁新册，净零）：
  `card_state: preregistered | testing | judged_RED | judged_GREEN | rejudged | SEALED | reborn(ref=新卡id)`
- 迁移合法性表（机生校验）：preregistered→testing（开测）→judged_*（考卷）→rejudged（仅一次，#363）→SEALED（封卡）→reborn（唯一复活口=新 prereg 卡，#399/#304）；非法迁移=校验器红
- 既有裁定合法性：#363 重判一次/#399 复活新卡/#304 复活窄考——迁移表必须与裁定册一致（RULING-REFERENCE 同步）

## 4. 图形态

- **状态机图**（非 DAG）：状态=枚举值，边=迁移+触发器（考试引擎）+门（裁定号）
- 生成器：generate_card_lifecycle_map.py，输入=登记面枚举+迁移表+裁定册解析
- MOD 总线挂载：考试引擎/成本门/trial_ledger/experiment_registry 域模块
- 大白话锚：军令状→上考场→判卷→（最多一次申诉）→封棺→投胎须重立军令状

## 5. 立项裁定建议

**建议立**：策略治理是核心资产，状态三处分裂已实际造成判读成本；风险=登记面扩枚举需 experiment_registry owner 会话协调，迁移表与裁定册的同步靠 RULING-REFERENCE 门保证。
