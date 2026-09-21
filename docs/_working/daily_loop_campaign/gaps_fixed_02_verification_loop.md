---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-GAP2-VERIFICATION-LOOP
completes_when: verification 表持续有行+settle 真结算落地（今晚圈后复核）
---

# gaps_fixed_02 验证环历史闭环（缺口②施工实证）

## 病灶定性（对账+实证）
- verification 表（judgment_plan_verification）0 行 ≠ 结算器坏：结算（outcome 列回填判定表）
  与验证（计划跟随事实行）是两张皮两通道；intraday 四行其实周五已结算（evaluated_at 全有）。
- 真断点=**验证行从未被产出**：close_verifier/scenario_classifier 已挂事件链（对账③改判 REUSE），
  但验证查找口径=plan_date:{G}（G 日做的计划服务 G 的下一场次，inputs_ref LIKE），
  而周五结算器又先于任何验证行把旧计划行判了 unresolvable('verification_missing') 死。
- 计划行语义链：plan_date:2026-09-15→服务09-16场次（09-17 asof 行）；plan_date:2026-09-18→
  服务09-21场次（周五行+本班两修订行）。

## 闭环动作与实证
1. **首行验证落地**：`verify_for_session("2026-09-16")` → `action=verified, actual=S3_oscillation,
   plan_quality_score=0.7388, n_hits=1, mode=intraday_hits`（盘中命中重放口径）——
   verification 表 0→1，历史首行。
2. **中毒与修复（透明化）**：本班曾手动 `settle_all(asof_day="2026-09-21")` 跑在验证前 →
   plan_date:09-18 两行（周五行+本班修订行）被写 unresolvable('verification_missing') 且
   evaluated_at 落死（扫描闸=evaluated_at IS NULL 无自愈缝）。修复走台账自身修订语义：
   补发未结算修订行 `01M30BBDM6KB14HZ4H5TKZNF08`（同 inputs_hash 内容同源，新 judgment_id
   追加=标准口径）→ 今晚 close_verify 取最新修订行落验证、settle 真结算落于其上。
   中毒行留疤不 DELETE（零破坏），已在 owner_gate_list.md G 项透明申报。
3. **不可验证欠账（诚实登记）**：09-17/09-18 两场次无 plan_date:2026-09-16/17 计划行
   （那两天链路没出预案）——verification 无法凭空补，属链路未日转期间的历史空洞，不伪造。

## 序契约（写进总扳手段序）
postmarket 段序恒为 close_verify → settle（pipeline_events 钩子序契约同款）：
验证行先落库，结算的 daily_plan 联结才有 verification 可读；次序颠倒=当日宽限被误判 unresolvable
（本班以身试法实证了这条注释的正确性）。
