---
ttl: task_bound
---

# L-B TI 线作业簿（重建版 v2，代理全文存档=agent_fa49c9ab transcript）

根因：full_refresh（周一 03:00，分钟唯一生产者，窗口锚月初⇒调度补不到 9 月）三杀梯次停产——09-21 写通道单批失败（1m/5m 停）/09-22/23 收割+僵尸（15/30m 停）/09-29 调度器重启击杀（60m 停 09-28/120m 停 09-29）。死信回灌必败=cols_clause=null 活表序截列错位。

终裁：批9/批10 考古翻案（+39 指标/volume 量纲治本/夜跑每夜清 state 全量重算=文档化契约演进非 bug）→回填解冻。主跑：ti_minute_recalc.py 锚 09-01 全分钟串行 ~20-25h（与调度惯例同锚保预热）；校准污染已清（FINAL 40 键复原）。验收=水位断言+audit_technical_indicator_coverage+indicator_reader 冒烟。结构性修复卡（Owner 门位批）：per-period 拆分+运行保障+缺口感知锚。

## 九、主跑收官（10-01 17:19，实跑 10h）

START=09-01 全分钟周期主回填 **ALL DONE**：累计写入 28,091,859 行（1min 2809 万/5min 314 万/15min 97 万/30min 65 万/60min 52 万/120min 47 万量级含重算覆盖）。**验收三件套全 PASS**：①水位断言=七交易日×全周期（1min 971 万/5min 191 万/15min 71 万/30min 42 万/60min 31 万/120min 13 万/daily 9 万）；②audit_technical_indicator_coverage=AUDIT PASS（214 在产列，fractal 事件族豁免合规）；③冒烟=09-28 1min 000001 全 241 bar×五大类列全非空。源窗口无数据风险=0（幂等可重跑）。**L-B 线闭环。**
