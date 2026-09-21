---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-HANDOFF-MAX
completes_when: Max 复审班签收（数字以 e2e_manual_run_report.md 终版为准）
---

# 交接包：给 Max 复审班的复查要点（丁线 st-dloop-20260921）

## 一句话终态
排班链路（大盘→板块→个股→做T）首次真跑通：9 棒事件链 8 棒本就已挂（对账改判），
唯一断棒 warroom 由总扳手补齐；regime 断供根因=供需阈值错位（非代码缺失）已补印修复；
验证环历史首行落地；两圈 E2E（09-18 历史+09-21 实时）台账新增行>0；零下单零挂表。

## 复审清单（按优先级）
1. **00_reuse_audit_ledger.md §4 阈值错位**：调度器日志三条"action=fresh 滞后=2/3日"零印制
   vs 编排器 regime_missing——核 _REGIME_STALE_DAYS=3 vs 蓝图 D1（>1交易日 fail-closed），
   治本申请单在 owner_gate_list.md B。
2. **中毒行修复路径**：daily_plan 三行 unresolvable 疤+未结算修订行 01M30BBDM6KB14HZ4H5TKZNF08
   （gaps_fixed_02）——核修订语义引用（标准"修订=新 judgment_id 追加取最新"）是否成立。
3. **总扳手合规**：MANUAL-ONLY/零自建幂等键/fail-open 边界（模块头 INVARIANTS）+5 单测；
   核对"薄委托"声称：逐段 grep 应见纯转发无平行逻辑。
4. **token 顺带收编申报**：batch_creation_tokens 按前缀扫描把 plan_engine/tests 下 18 个历史
   未登记文件一并插了 token（26 行全载 st-dloop-20260921 痕）——判定：幂等纯插入对他会话
   无害，手删热注册表风险更高故保留；Max 可判推翻（删行须走 CAS 工具非手改）。
5. **裁定引用勘误**：砍做T=#331 非 #304（撞号改号）；本班文档已按新口径，历史文档残留不回改。

## 已知残留（不阻断交付）
- 09-17/09-18 场次无计划行=验证环历史空洞（不伪造，已登记）；
- decision_daily 09-16 存在 44 行测试簇（他会话痕迹，本班未清理——DELETE 属 Owner 机械判定门）；
- pending_events.jsonl 两条 09-16 c4_batch_due 滞留（移交 C4 线，owner_gate_list.md H）；
- fw-tdm-current 一代 drift（少 097/027）：等 TDM staged 落地后 --check，本班未动。

## 提交物清单
- src/zephyr/plan_engine/daily_loop_master_switch.py（MOD-PLAN-033，depgraph node 14905528+翻译册）
- tests/plan_engine/test_daily_loop_master_switch.py（新增）
- docs/_working/daily_loop_campaign/ 六件（对账总账+三份缺口实证+路由表稿+Owner 门清单）+
  e2e_manual_run_report.md + 本交接包
- 注册表批：capability_canonical_file_registry.yaml（token 26 行）+ module_translation_registry.yaml（1 行）
