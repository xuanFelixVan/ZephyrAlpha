---
ttl: task_bound
---

# 清洁+补考+E2E 冒烟战役作业区（总包 st-cleanexam-20260918）

> Owner 通宵令 2026-09-18：③清洁三件（三层调查后执行）+⑥16 条补考+端到端模拟盘 100 股桥测试。
> 执行模式：线内先挖后干、线间并行流水；挖干判据=六向台账+自审闸三态；封矿后进施工。
> 红线：st-residual-20260917 战役 C1 三共享文件（pipeline_events.py/tasks.yaml/apply_market_tables_ddl.py）禁碰；其 E1-E7 作业簿禁碰。
> 事故注记：本目录遭 tdchain-sweep 会话多轮物理清扫（untracked 直删），各件再生后立即 git add+commit；ENV2 运行态已迁 .runtime/tmp 免疫区。
