---
ttl: task_bound
title: M4 分册04 — PG meta_question 283 问登记与消费面
lane: m4_ai_layer
session: st-commitspeed-tbl-20260924
date: 2026-09-25
status: mined
---

# 04 — PG meta_question（283 问三态与消费面）

## 一、环节定义与边界

meta_question=原问题中央登记表（PG `meta_question` schema，3 表），chain_piling 战役产物、AI 层元问题层（L0）。写入唯一入口=`zephyr.governance.meta_question.registry.MetaQuestionRegistry`（registry.py 438 行+exam_ops.py 543 行 NO-GOD-CLASS 拆分件，MOD-CHAINPILE-METAQ）；只读导出=`snapshot.py`（165 行，机生 YAML 快照禁手工维护）。上游=挖矿链提问方；下游=考试循环（exam_loop 8 件）、月检机检（check_meta_question_status_band）、Owner 查账。

## 二、六向台账

| 向 | 实测证据 |
|---|---|
| 上游输入 | register 校验链（10§7.1：A 级必填→layer 枚举→五要素机检（降级口径）→查重→净零→q_id 机生）；审计双轨=meta_question_audit 行+JSONL 追加 |
| 下游消费 | snapshot CLI（`python -m zephyr.governance.meta_question.snapshot`，PG→registry_latest.yaml）；status band 月检（#24 monthly）；exam_loop（arbitration/exam_plan/ledger/reexam_scheduler/state_machine/writeback/event_codes 八件实存） |
| 自动化触发 | 全链 manual CLI（registry/snapshot/status_band 均 STARTUP manual+M11 豁免注记"按需机生非驻留进程"）；reconciler 事件触发纪律未涉本表 |
| 真源与注册表 | **PG 行=唯一真源**（snapshot 头 FORBID_MANUAL_EDIT_DECLARATION："机生件禁手工维护——真源=PG meta_question 表（RULE-SSOT）"）；设计契约=docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md §7 + 13_exam_backfill_loop_design.md §1.5 + 20_management_policy.md §2/§3 |
| 门禁与质量尺 | 状态枚举唯一真源=meta_question_statuses_vocabulary.yaml（load_vocabulary_values 动态加载，GATE-VOCAB 合规）；乐观锁 UPDATE...WHERE version=:expected（VersionConflictError）；审计 what 取自 AUDIT_WHAT_VOCAB 四族 SSOT 词表；q_id 墓碑不复用（全表 max+1 连号） |
| 当前运行状态 | **绿（带一处 OUT_OF_BAND 已知态）**。实测（read_only PG）：主表 283 行=answered 281+reexam 2；exam_result 335 行/283 distinct q_id（st-metaq 原考 285+st-metaq-gc 载体复考追加） |

## 三、283 问三态总计数（st-metaq-20260923 端到端总账 02_final_ledger.md §1，PG exam_result 与 results/ JSON 逐问一致）

| 三态 | 问数 | 占比 | 说明 |
|---|---|---|---|
| pass | 142 | 50.2% | 证据齐+过 threshold（登记核验 0.3-0.5 / 真算 0.8-1.0 置信） |
| fail | 45 | 15.9% | no_alpha=30（退役登记即闭环）+infra=15（大缺口 12/小修 2/审计改判并入 1） |
| insufficient | 96 | 33.9% | 闭卷窗零样本/管线未建审计对象不存在/口径不可机检（案由逐问登记） |
| 合计 | **283** | 100% | 主表 status 全部 answered（claimed_by=st-metaq-20260923） |

**增量（总账之后）**：st-metaq-gc-20260924 载体复考追加 exam_result 行（实测 335 行 vs 原考 285），含 supersedes 标记（如 PQ-0055 insufficient→fail 形态更正、PQ-0109 复判 insufficient）；主表 2 问转 reexam 态。

## 四、健康带机检实测（PQ-0099 执行体）

```
python scripts/governance/check_meta_question_status_band.py --regime campaign
→ total=283 | answered 281 (99.29%) | reexam 2 (0.71%)
→ VERDICT: OUT_OF_BAND：answered 99.29% > campaign 带占位上限 95%；单状态 99.29% > 帽 80%
→ 注记：campaign regime 数值待 Owner 裁定（PQ-0099 工作簿 §4 二选一：豁免窗 vs 双带），裁定须登记 ruling_registry
```
破带=**战役期预期态**（一次性应考后全表 answered），机检机制建成、数值留门位——与 fail 判定同源（PQ-0099 本身就是此题）。

## 五、消费面清单（谁在吃这 283 问）

1. **考试循环 exam_loop**（`src/zephyr/governance/meta_question/exam_loop/`）：exam_plan（判据源）/state_machine（13§1.5 合法边）/reexam_scheduler（复考排程，gc 复考即其产物）/arbitration/writeback/ledger/event_codes/config
2. **缺口分流作业簿**：fail 15 簿+insufficient 分流（docs/_working/meta_question_answers/gaps/），大缺口 12 待立项、小修 2 待施工
3. **退役登记**：30 问 no_alpha RETIREMENT_REGISTER（零调参翻案纪律）
4. **月检**：status band 机检（#24 monthly）+default 稳态带（answered 30-70% 且单状态≤80%）
5. **staged 落地面**：results/b1-b5 共 141 件 JSON+10 tests/governance/meta_question+8 exam_loop 模块全在 v4 staged 批内（本战役 staged 大盘 560 件的组成部分）

## 六、堵点与病灶

1. **campaign 带数值待裁定**：OUT_OF_BAND 长期悬置——每跑月检必 exit 1，"狼来了"钝化告警价值｜修法=Owner 按 PQ-0099 工作簿 §4 裁定并登记 ruling_registry 替换占位 95%｜待裁项
2. **exam_result 行 vs 主表口径差**：335 行/283 问（复考追加 supersedes 行）——消费者若按行数当问数会错；修法=消费侧一律 distinct q_id 或取 supersedes 链终态（snapshot 导出已按主表口径，exam_loop 内部口径须复查）｜本车道可提建议
3. **insufficient 96 问复考前置全在外部车道**：B 档管线未建/DS 册无条目/载体 schema 未部署（如 metaq_e1c 7 表从未部署）——修法归 M1 数据链/M2 回测链立项，metaq 侧仅登记复考触发条件
4. **audit JSONL 与 PG 行双轨**：849 audit rows（PQ-0098 探针实测）双真源漂移风险低（追加账），但无对账器——修法=轻量对账 CLI（与 snapshot 同模式）

## 七、自审闸三态

**挖干可施工（登记/快照/机检面）+待裁（campaign 带数值）**：六向全实证；三态计数双源一致（PG+results JSON）；带数值裁定=PQ-0099 工作簿 §4 二选一（建议：双 regime 双带，豁免窗易被战役常态化滥用）。

## 八、复核命令

```bash
python scripts/governance/check_meta_question_status_band.py --regime campaign   # 283/281/2 实测
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(read_only=True); cur=c.cursor(); cur.execute('SELECT status,count(*) FROM meta_question.meta_question GROUP BY status'); print(cur.fetchall()); cur.execute('SELECT count(*),count(distinct q_id) FROM meta_question.meta_question_exam_result'); print(cur.fetchall()); c.close()"
head -20 docs/_working/meta_question_answers/02_final_ledger.md
ls src/zephyr/governance/meta_question/exam_loop/
```
