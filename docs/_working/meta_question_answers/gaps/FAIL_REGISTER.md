---
ttl: task_bound
completes_when: 15 infra 簿施工闭环/转工单 + 30 no_alpha Owner 追认后随总包归档
title: fail 总登记册（45 问·两类分型）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-23
---

# fail 总登记册（增补令#5 两类区分）

## A. fail_type=infra（15 问·数据缺失/管线断/机制未建·已建作业簿）

| q_id | 作业簿 | 三态裁定 | 案由一句 |
|------|--------|----------|----------|
| PQ-0004 | gaps/PQ-0004_workbook.md | 大缺口 | degraded_check 关闸依赖 W4 源线谱 YAML 化+降级桩换真检 |
| PQ-0012 | gaps/PQ-0012_workbook.md | 大缺口 | hfq vs raw×adj_factor 二选一重算=712 万行 L 级跨域管线，禁调容差 |
| PQ-0018 | gaps/PQ-0018_workbook.md | 大缺口 | 节点↔板块映射册+聚合规则设计，需 Owner 裁两口径主从 |
| PQ-0062 | gaps/PQ-0062_workbook.md | 大缺口 | 接线已在位（registry.py _append_jsonl 已挂），剩存量回放+对账器 |
| PQ-0064 | gaps/PQ-0064_workbook.md | 大缺口 | 三源补挂+写入器+2,225 合并节点收敛 |
| PQ-0065 | gaps/PQ-0065_workbook.md | 未裁定 |  |
| PQ-0067 | gaps/PQ-0067_workbook.md | 大缺口 | 行业层载体+三词系对齐册（可与 0078 合批；附 PQ-0065 降级即退役选项） |
| PQ-0068 | gaps/PQ-0068_workbook.md | 大缺口 | 产品同义词册(M)+PIT 语义写入规则；机械上限约 5%≪30% |
| PQ-0072 | gaps/PQ-0072_workbook.md | 大缺口 | 事件版本载体选型+DDL+回填 11.3 万条；换口径无效已实证 |
| PQ-0078 | gaps/PQ-0078_workbook.md | 大缺口 | io_edge 挂接 DDL 二选一+153 部门映射册（与 0067 合批） |
| PQ-0099 | gaps/PQ-0099_workbook.md | 大缺口 | 考后极性反转：answered=100% 仍破带（静态终态），需复考对账器或 Owner 裁 regime 带 |
| PQ-0102 | gaps/PQ-0102_workbook.md | 大缺口 | 第三道对账线 S 级但前置 JSONL 轨未建+哈希规范化须立法 |
| PQ-0131 | gaps/PQ-0131_workbook.md | 大缺口 | 随 PQ-0012 工单合并施工，U4 切面判据随单落地 |
| PQ-0172 | gaps/PQ-0172_workbook.md | 小修 | DS 册 coverage 补注+known_data_gaps 1-2 条+U3 收窄 <30 行配置 |
| PQ-0196 | gaps/PQ-0196_workbook.md | 小修 | 02 册 U3 两行改『日批积累』，无消费方需小时级 |

## B. fail_type=no_alpha（30 问·因子无预测力·退役标记总册）

全clist见 [RETIREMENT_REGISTER.md](RETIREMENT_REGISTER.md)。禁施工，Owner 追认前冻结。

## 施工纪律（增补令#3）

- 全部 15 簿已封矿（未知项=0）；施工代码在簿三态裁定为『小修』且明早 09:00 git 解冻后经 GitCommitGateway 正门落地；『大缺口』写工单转总指挥分流，本班不施工。