---
ttl: task_bound
title: "CH 实弹批六件——VM 离线阻塞移交账"
session: st-finaldel-chief-20260930
---

# CH 实弹批六件——VM 离线阻塞移交账（2026-09-30）

> Owner 已批（裁定#431 内 CH 实弹三件+补数+8 张空壳表 DROP）。执行窗勘验：172.24.30.100 tcp:9000 / http:8123 **双路关闭（VM 未开机）**，本车道零生产写入安全收兵。按 Ollama 先例 AI 不代开机器——**VM 开机后任意班次按下表执行即可，全部材料已备**。

| # | 事项 | 状态 | 材料与移交 |
|---|---|---|---|
| 1 | apply_market_tables_ddl --apply | 待 VM | 三步验证框架在本表；DDL 清单脚本 --dry-run 即得 |
| 2 | intake_ledger_recon rebuild | 待 VM | 处方=F16 卷（fullconnect b 段）；优先新表+对账切换 |
| 3 | #20 realtime 换源（东财→腾讯） | 待 VM | 方案件在 M4 工单 C45 族；旧源配置注释保底可回滚 |
| 4 | gap134 补齐（sector_constituent 880+881 主轴） | 待 VM | 真源裁定=裁定#431+universe_registry v1.2.4（UNI-SECTOR-880-001）；写入前 dump 快照 |
| 5 | C344 补 4 日期（8225 票·日） | 待 VM | known_data_gaps.yaml 在册；治本码件在 .worktrees/st-zmaster2-20260926 |
| 6 | 空壳表 DROP（权威口径 13 张确证 0 行） | 待 VM | 行数/判定 CSV+JSON+l2_tick DDL 导出=G:/zephyr_cold/retire_c267_20260930/shell_tables_c1_market/；移交凭证=同目录 HANDOVER_TO_C_LANE.json（五步清单）；每张三步验证不过即跳 |

执行纪律：逐件三步验证（必要性/真实性/可逆性）留证到本账追加节；写入前快照；验证不过即跳登记。
