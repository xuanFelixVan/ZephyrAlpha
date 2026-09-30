---
ttl: task_bound
title: "NB1 附带快速复核：B11 windows_service / B15 空壳表 / B16 blueprint（一段话裁定）"
session: st-nightsweep2-nb1-20260930
updated: 2026-09-30
---

# B11/B15/B16 附带快速复核（一段话每条）

- **B11 windows_service（src/zephyr/trading/windows_service.py，118 行）——保留，非退役对象**。蓝图背书（auto_runtime_core §3.1）、M02/M10 双豁免在册（SCM 停止事件=事件驱动合规）、trading/__init__ 导出+runtime_config CONSUMERS 头在链，是 `sc create ZephyrAlpha` 的服务化部署入口。当前实际部署走 reaper 计划任务路线，服务路线处于"备而未用"——若 Owner 判服务路线废止属部署方针变更（Owner 门），代码本体不动。

- **B15 空壳表——已在执行流，复核维持"先归档后 DROP"**。wave3 strict 权威口径=13 张确证 0 行（G:/zephyr_cold/retire_c267_20260930/shell_tables_c1_market/ 有 DDL+行数 CSV 凭证），C267b 已归档并移交 C 道（HANDOVER_TO_C_LANE.json，CH 双端口不可达未代开机）。两点修正：①etf_benchmark 已翻案（fresh 读数 2370 行恢复，workorders_data_exam_factory.md:40）必须移出净删名单；②edb_data 是"accepted known-gap"非垃圾——若 B5 宏观复活处方启用 FRED/akshare 直灌路径，它可作灌入目标复活或按 R5 退役，二选一随 B5 卡裁定。

- **B16 blueprint（docs/03_modules/**/blueprint.md，实测 548 份）——整族保留，"空壳蓝图"另立分诊卡**。蓝图体系是设计真源层：模块头 [MODIFY-GUARD]/[BLUEPRINT] 锚点指向它，删蓝图=断 MODIFY-GUARD 真源链（违反 SSOT）。真正候选是"有蓝图无实现且永不落位"的空壳子集——属"注册表净删"Owner 门域，应按 domain 分册产分诊清单（机生清单禁手工维护），本夜不计入退役基数。
