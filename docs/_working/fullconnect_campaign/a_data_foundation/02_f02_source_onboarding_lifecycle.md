---
ttl: task_bound
title: "F02 数据源接入生命周期——上架流水线编排断链复飞案卷"
session: zc-l01-20260927
---

# F02 数据源接入生命周期（复飞案卷）

> 前序：M1 补挖波 07_f02_source_onboarding.md（st-ailayer-fullflow-d）七段×机械件对照已挖干；本卷=四态独立复核+当日增量。

## 一、六向台账（锚点引 07 册+今日补验）

| 向 | 内容与实证 |
|---|---|
| 上游 | 需求两入口（骨架 ⬜ 中类/消费端缺口）+胃 F96 情报（总册 DAG F31→F02）；三教训催生（SOP 头注 2026-09-17） |
| 下游 | tasks.yaml 271 任务→schedule 槽位→business_data_categories 品类→data_asset_registry 295 datasets（F11 挂接义务） |
| 自动触发 | **无编排器**（automation 骨架工段③"全链最大空地"原文在案）；零散件自动化各段见 07 册 §三对照表 |
| 真源注册表 | SOP=data_ops_sop/data_source_onboarding_sop.md v1.1.0；候选册=docs/_working/altdata_line/10_data_source_candidates.yaml（32 条：27 candidate/1 integrated/1 graduated/3 rejected）；源资产册=data_sources_registry.yaml v2.6.0 |
| 门禁质量尺 | 门禁收缩中：DATA-TASK-COMPLETENESS 2026-09-23 退役（gate_registry.yaml:2054-2056，w5_1 条 2）；validate_tasks_yaml 仅 WARN；disabled_reason 硬拦=src 零实件（SOP §7 声称失真） |
| 运行状态 | **黄（通量真实但人肉编排）**。毕业两单实活（DS-CAND-000 股东户数/DS-CAND-011 Hyperliquid）；st-emomine 批（2026-09-23，git a9818b2ef2）=八件手工串接范例 |

## 二、子模块三级枚举

1. 候选面：10_data_source_candidates.yaml（32 条）→毕业联动 data_sources_registry.yaml（跨两册手工，O4）
2. 建表面：schemas/categories/*.py+scripts/ch/apply_*_ddl.py 25 件+verify()（最强环，DDL-as-Code）
3. 接入面：capability 三闸（capability_validator/capability_semantic_gate/capability_symbol_gate，scheduler.py:1647-1685 运行时消费）
4. 验收面：failures/{date}_{task_id}.json 留痕（alerter.py:140 写/alert_webhook_dispatch.py:17 消费）；supply_sentinel 腿探活
5. 退役面：#ARCH-351 退役映射表缺位（architecture_issue_registry.yaml:22342-22360）；DS-IFIND 迁移范式注释留痕在档

## 三、接线四态独立复核

- 总册：partial（流水线串接=工段③最大空地）/P0/D2。独立复核：**partial 成立且定性精确**——非零件断链，是编排断链（07 册结论本卷复核认可）。
- 当日增量勘误③：07 册记 SOP §12 盘符过时（G:）+路径文本损坏（0xC2 0x81 转义事故）——本卷复核该 SOP 现行文本仍在（修册件未落地），登记为待施工非新病灶。
- 关联：姊妹定版卷 L00 §二 B-8 判 data_asset_registry 并入 F11（挂轴对象清单），F02 下游义务面与 F11 同账——两卷不重复立册，F11 卷为准。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| O1 | 工段③编排器缺位（十环人肉串接） | 施工：onboard_wizard 单入口向导（复用零散件纯编排壳，3-5 天） | P0 |
| O2 | fallback_sources 登记时强制真空（退役门后无替代） | 施工：并入 O1 硬校验+SOP §6.2 措辞修 | P1 |
| O3 | disabled_reason 硬拦零实件 | 施工：并入 O1+修 SOP | P1 |
| O4 | 毕业回写两册滞后（DS-CAND-000 状态 integrated 未升级） | 施工：并入 O1 联动 | P2 |
| O5 | SOP §12 盘符+路径损坏修册 | 施工（safe_write_text） | P2 |
| O6 | 验收三查无自动判定器 | 挂起+解锁=与 F11 卷 T2 对账器合并立项 | P2 |

## 五、自审闸三态

挖干可施工（07 册+本卷复核；O1-O5 可施工报总筹排期；O6 挂起）。非新裁定。

## 六、复跑命令

```bash
grep -c "cand_id:" docs/_working/altdata_line/10_data_source_candidates.yaml   # 32
sed -n '2054,2056p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
grep -rn "disabled_reason" src/zephyr/data --include="*.py" | grep -v __pycache__   # 零命中
sed -n '18p' docs/_working/automation/20260917_fullauto_skeleton_v1.md
git log --since=2026-09-17 --oneline -- src/zephyr/data/config/tasks.yaml | head -5
```
