---
ttl: task_bound
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-L6-001（暂编号）risk_redline 蓝图

## 定位

骨架 §9 实盘红线分级引擎 v0：纯函数规则执行器（零 IO 零时钟）。生命周期轴"实盘生产"站的安全底线设备。

## ALGO_FLOW

- I1: 组合日度记录 [{date, pnl_pct, market_crash}]（market_crash=L1 regime 门仲裁注入）
- I2: RedlineConfig（阈值默认=骨架 §9 v0 草案；生产前按组合回测分布校准+标准库 freeze）
- A1: 逐日黄线（≥2% 减半仓归因）
- A2: 日红线（≥4% 或超回测最差日 2x→清仓冻结）
- A3: 黑天鹅状态机（市场性暴跌开 2 日观察窗，窗内暂缓、越窗或非市场性→RED）
- A4: 周 -5%/月 -10% 红线
- O1: 动作列表 [{date, level: YELLOW/RED/GRACE, rule, detail}]

## 不变量

熔断≠下架（日内噪音不动整装）；GRACE 只对 β 不对 α；动作只是"建议执行器"的输入，实盘执行器施工待实盘开通。
