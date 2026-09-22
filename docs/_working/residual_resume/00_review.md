---
title: 残余挂账战役收尾复审结论（tc_08 卡第 2 节落盘）
created_at: 2026-09-22
session: st-residual-20260922
ttl: task_bound
---

# 残余挂账战役收尾复审结论

> 本件=tc_08 卡诊断的"形式收口三件全历史零记录"缺口的补齐件之一（复审面）。
> 证据等级逐条标 [亲验]（09-22 开工实测）；原始调查=2026-09-21 只读子代理取证。

## 1. 交接令世界观 vs 实测

| 原文声称 | 实测结论 | 证据 | 等级 |
|---|---|---|---|
| residual_resume/ 三件形式件 | 全无（本件与 01_plan.md 即补齐件） | 09-21 卡调查 + 09-22 ls 复测 | A |
| 总簿状态回写完成 | 未做：归档盒 00_master_ledger.md frontmatter 仍 campaign_running，九节点七空框 | Read 归档总簿 | A |
| T1① 旧路径 6 个 staged D | 挂至 09-22 由 st-residual-20260922 删除批落地（内容存续于归档盒） | git status + 归档盒 ls | A |
| T1② 红队加固 +31/-7 | 仍在（staged 防蒸发）但 R-072a 改判不落——落了激活 CRISIS_SHRINKAGE_FLOOR=0.05 改配额闸 | git diff HEAD --stat=+31/-7 | A |
| T1③ 接线批按新版重做 | pipeline_events.py 危机短路接线仍未落地（成品只在 G 盘冷库，落前先验哈希；A5 死会话遗产裁定归 Max） | grep crisis_block_check=0 | A |
| T1③ apply 三常量 | 09-22 已随批恢复注册（crisis_gate_log/sim_attribution_daily/cohort_daily_ledger） | git staged diff scripts/ch/apply_market_tables_ddl.py | A |
| T2 cohort 建表+任务 | schema+builder+13 测试在 HEAD；09-22 补齐 tasks.yaml 任务+internal provider 路由+品类注册表条目（本班）；**建表=Owner 门位仍待办** | tasks.yaml grep + 品类 YAML grep | A |
| T3 E6 纸面对冲腿 | 已落地（变形）：2a80340b51 落 paper_hedge_leg.py+config/paper_hedge.yaml（比例进 hedge 册非 crisis 册，实质等价） | git show --stat | A |
| T4 E7 告警 | 已落地：0808dd8757 落 alert_webhook_dispatch.py+config/alert_webhook.yaml（enabled:false fail-closed） | git show --stat | A |
| T5/Q1 两轮+红蓝 | 变形执行：fullflow R-072 两轮跑的是工作区字节；严格 HEAD 复跑（B21）未做 | COORDINATION_LEDGER 6.20 | A/B |
| O-1/O1/O2/凭据/期货通道 | 裁定#392 D 类打包批已全裁转正（ruling_registry HEAD 5267 行起五条目在册） | git show HEAD grep | A |

## 2. 遗留欠账（本复审后仍开）

1. pipeline_events 接线两段（crisis_block_check 短路+attribution_daily FIFO 末位）——等 A5 死会话遗产裁定。
2. cohort_daily_ledger CH 建表——Owner 门位（apply 三常量已就绪，建表即通）。
3. B21 严格 HEAD 两轮复跑+六环节端到端补课——本轮未做（需净窗）。
4. 红队加固 +31/-7 维持不落（R-072a），现场 staged 防蒸发。
