---
ttl: task_bound
title: L09 案卷 F92 — 原问题账本（PG meta_question 三表；entry_count=0 空转的真相=ROOR 册页字段失同步）
session: zc-l09-20260927
---

# F92 原问题账本（J 段 A7，骨架态=partial/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | register 校验链（A 级必填→layer 枚举→五要素机检→查重→净零→q_id 墓碑机生 max+1 连号）；写入唯一入口=MetaQuestionRegistry（registry.py 438 行+exam_ops.py 543 行拆分件） |
| 下游消费 | snapshot CLI（PG→registry_latest.yaml 机生）；exam_loop 八件（见 §二）；月检 status band 机检（本日实跑 OUT_OF_BAND exit 1）；缺口分流簿+退役登记（M4-04 §五） |
| 自动化触发 | 全链 manual CLI（registry/snapshot/status_band 均 STARTUP manual+M11 豁免注记）；reexam_scheduler 复考排程为 exam_loop 内组件（gc 班复考即其产物） |
| 真源与注册表 | **PG 行=唯一真源**（meta_question 三表；snapshot 头 FORBID_MANUAL_EDIT 声明）；ROOR REG-METAQ-001（registry_of_registries.yaml:833-842）：physical_path=快照，counting_rule="快照头部 row_count 字段"，**entry_count: 0（:838，本日实读）** |
| 门禁与质量尺 | 状态词表唯一真源=meta_question_statuses_vocabulary.yaml（GATE-VOCAB 动态加载）；乐观锁 version 冲突检测；审计双轨=PG audit 行+JSONL 追加（无对账器，M4-04 §六.4） |
| 当前运行状态 | **黄（账本本体绿、册页字段红、月检狼来了）**：PG 主表 283 行（281 answered+2 reexam）、exam_result **337 行/283 distinct q_id**（较 M4 的 335 又 +2，复考在继续）；快照 row_count=283 正确；唯 ROOR entry_count=0 失同步 |

## 二、子模块三级枚举（src/zephyr/governance/meta_question/ 实扫 4+8 件）

1. 写入面：`meta_question_registry.py`（438 行）+`exam_ops.py`（543 行，NO-GOD-CLASS 拆分件）。
2. 导出面：`snapshot.py`（165 行机生，"再生成即全量对账"声明在快照头）。
3. 考试循环 `exam_loop/` 八件：exam_plan（判据源）/exam_lifecycle（合法边状态机）/reexam_scheduler/arbitration/ledger/writeback/event_codes/config。
4. PG 三表：meta_question 主表 283 行；meta_question_exam_result 337 行/283 问；meta_question_audit（M4 探针 849 行口径）。
5. 快照产物：`docs/_working/chain_piling_campaign/snapshots/registry_latest.yaml`（generated 2026-09-22，row_count: 283）。

## 三、接线四态独立复核（含 §1.4"entry_count=0 空转"专查）

- **账本本体=绿**：PG 283 问三态（pass 142/fail 45/insufficient 96，M4 总账口径）+复考边活（exam_result 337 行仍在长）——**账本不是空转**。
- **ROOR 册页=失同步（空转实体）**：REG-METAQ-001 `entry_count: 0` vs 其自声明 counting_rule"快照头部 row_count"=283 vs PG=283——**三方两值，漂移在 ROOR 册页字段**：快照再生（09-22）后无人回填 ROOR，且无 reconciler 消费该字段。wiring_gap §1.4 括注"entry_count=0 空转"应读作**册页元数据空转，非账本空转**。
- **月检机检=在岗但狼来了**：本日实跑 campaign 带 OUT_OF_BAND exit 1（answered 99.29%>95% 帽、单状态 99.29%>80% 帽）——战役期预期态，占位数值待 Owner 裁定（PQ-0099 工作簿 §4），每跑必红钝化告警。
- **exam_loop=建成有流量**：复考追加行为证（335→337）；state_machine 件名勘误见下。

## 骨架勘误

1. **骨架括注"partial（entry_count=0 空转）"语义勘误**：entry_count=0 是 ROOR REG-METAQ-001 册页字段未随快照（row_count=283）/PG（283 行）同步——空转在登记元数据轴，账本本体有 283 问+复考流量。骨架按此读会误判整环节为空壳。
2. exam_loop 文件名勘误：M4 分册04 记 `state_machine.py`，本日实盘为 **exam_lifecycle.py**（st-metaq-gc-20260924 接手班重投批内更名，git --follow 实证 ef9e118ae75）。
3. exam_result 行数时点更新：M4 记 335，本日 337（+2 复考行）——账本活性旁证。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | ROOR REG-METAQ-001 entry_count=0 失同步且无回填机制 | 短期=手工改正一次（热文件走 safe_write_text+CAS）；治本=ROOR entry_count 纳入 reconciler 对账（ROOR 76vs77 同源问题族，裁-1 关联） | P1 |
| 2 | campaign 带占位 95% 未裁定，月检常态化 exit 1 | Owner 按 PQ-0099 §4 裁定（建议双 regime 双带）并登记 ruling | P1 |
| 3 | insufficient 96 问复考前置全在外部车道（管线未建/schema 未部署） | 归 M1/M2 立项，metaq 侧仅登记触发条件 | P2 |
| 4 | 审计 PG 行+JSONL 双轨无对账器 | 轻量对账 CLI（与 snapshot 同模式） | P2 |

## 五、自审闸三态

**挖干（PG/快照/ROOR 三方独立取证+月检实跑+文件名 git 考古）✅；待裁（缺口#1 治本路线归 ROOR 对账族、缺口#2 数值裁定归 Owner）；待挖（exam_loop 八件逐件深挖——M4-04 已覆盖主干，本卷不重复）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
sed -n '833,842p' docs/registry_of_registries.yaml                   # entry_count: 0 在 :838
head -5 docs/_working/chain_piling_campaign/snapshots/registry_latest.yaml  # row_count: 283
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(read_only=True); cur=c.cursor(); cur.execute('SELECT status,count(*) FROM meta_question.meta_question GROUP BY status'); print(cur.fetchall()); cur.execute('SELECT count(*),count(distinct q_id) FROM meta_question.meta_question_exam_result'); print(cur.fetchall()); c.close()"
python scripts/governance/check_meta_question_status_band.py --regime campaign 2>&1 | tail -3   # OUT_OF_BAND
ls src/zephyr/governance/meta_question/exam_loop/                    # exam_lifecycle.py 非 state_machine.py
```
