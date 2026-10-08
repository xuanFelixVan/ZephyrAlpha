---
ttl: task_bound
completes_when: 图级设施环节施工与验证闭环后随战役归档
title: 图9 E 图级设施 环节挖矿（机生 v1）
owner: ZephyrAlpha-Owner
session: st-map9-chief-20261008
---

# 图级设施（图9 环节挖矿·机生）

> 一句话定位：这张图自己有校验器和对抗测试守着，谁改坏了结构当场拦下
> 矿源：config/strategy_production_map.yaml（机读）+ fac9_03_facts.yaml（实测）| 机制台数：2

## 机制清单（机生表）

| node_id | 名称 | module_ref | build | 标签 |
|---|---|---|---|---|
| FAC-MAP-M-001 | 策略工厂图结构校验器（FACTORY-MAP 本图守卫） | MOD-BT-080 | built | 图有人守 |
| FAC-MAP-M-002 | 本图对抗测试件 | MOD-BT-081 | built | 图有人守 |

## 实测（图面 trigger_facts/consumers 已填台数）

- trigger_facts 有值：0/2；consumers 有值：2/2；病历挂载：0/2
- 逐台明细：见 fac9_03_facts.yaml（本件为导航层，INV-1 不复制内容）

## 病历（casebooks 挂载行）

- 本组无直接病历挂载（病历册 15 本全图分布见 fac9_01_report §六）

## 通水判定

- 入口：validator（PASS nodes=341 edges=17）+对抗测试 38 用例+MAP-ALIGNMENT 门+MAP-MOUNT 挂图申报门禁
- 实测：校验器 v0.3 三连加固（observed 值域/consumers 上限/图例校验）已落 HEAD

## 缺口与建议（只登记不施工）

- -
