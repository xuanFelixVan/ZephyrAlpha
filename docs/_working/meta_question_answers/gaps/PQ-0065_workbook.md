---
ttl: task_bound
completes_when: CKG 降级/换源/补救三选一裁定执行后随总包归档
title: PQ-0065 fail 作业簿（审计改判 infra·并入 WO-007）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-24
---

# PQ-0065 CKG 边一致率 fail 作业簿（薄册·主册=WO-007 并案）

## 0. fail 定性（两类区分铁律）
初判 no_alpha（退役册曾列），Phase 2 审计改判 **infra**：CKG 产品-产品边与研报线抽取边一致率 1/81=1.23%（剔除 76 条自并入边防自证）≪70% 阈值——属**数据产品质量缺口**而非"因子无预测力"，且题面自带处置条款（"低于则 CKG 降级为结构先验"）。verdict=fail 不变，处置走降级裁定非退役。

## 1-5. 五环节（要点）
数据源：CKG 2021（supplies_to 57,069 事件）+研报线抽取边（ig_edge）｜入库：ig_fact 264,072 行｜机制：一致性交叉验证｜挂图：CKG→ig_chain 结构先验降级路径｜消费方：L2 传导图谱。

## 6. 三态自审闸
大缺口（并入 WO-007）：降级/换源/补救三选一属 Owner 裁定（阈值语义与图谱路线）。

## 7. 封矿声明
未知项=0。证据链：results/PQ-0065.json（含两轮独立复现）+审计改判注记+PG exam_result 追加行。主册=[WORKORDER_MASTER.md](WORKORDER_MASTER.md)#WO-007。
