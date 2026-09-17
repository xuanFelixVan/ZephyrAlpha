---
ttl: task_bound
title: E2E 冒烟段一执行记录（零委托）
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918
date: 2026-09-18
status: seg1_done
---

# 段一执行记录（S1-S6，零委托）

> 执行件：.runtime/tmp/cleanexam_e2e_seg1.py。全程零委托、零下单 API 路径触碰。

| # | 断言 | 结果 | 证据 |
|---|---|---|---|
| P1 | 模拟终端进程 | PASS | XtItClient PID 26196 Path=E:\国金QMT交易端模拟in.x64\XtItClient.exe |
| P2 | 账户三方一致 | PASS | env sim=8886156677/real=8887871993 = ENV_CONFIG 两槽 |
| P3 | live 槽未启用 | PASS | live.account='' |
| P4 | HTTP 桥 18901 | PASS | TCP connect ok |
| P5 | 熔断无激活 | PASS | active_switches()=[]（进程内存态语义） |
| P6 | 桥装配连接 | PASS | connect_all()={'qmt_sim': True} |
| P7 | 资金镜像 | FAIL（夜间镜像零值） | Account.csv 账号状态=正常但可用金额=0.00，mtime=09-17 20:50——官方导出夜间不刷新，非账户异常；段二 T1 重验 |
| S5 | prev_close | PASS | 510300 昨收 4.523，拟委托价(跌停)=4.07 |

段二放行条件：P1-P6 重跑全 PASS；P7 重验 cash>489 否则 EXIT_FUND；P9 无残留单。
修复留痕：v1 两处 bug（GBK 编码/symbol 后缀）已修重跑。
