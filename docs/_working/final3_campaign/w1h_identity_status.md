---
ttl: task_bound
title: W1-H 身份键地基（WP1）核验与收尾状态——st-ramp-wp1b 遗留件亲验报告+移交登记
session: st-final3-20260919
date: 2026-09-19
status: verified_handover
---

# W1-H 身份键地基（WP1）核验与收尾状态

> 结论先行：**WP1 施工面已全部落地 dev，无施工尾巴**。剩余项全部是门位待裁（Max/Owner）
> 或下游 WP（WP2/3/4）范围，本战役波次不移交施工、只移交裁决与排期。本件=核验报告。

## 1. 判死证据（st-ramp-wp1b-20260919 可接手）[亲验]

- `git worktree list`：无 st-ramp-wp1b 工棚（19 行清单逐行核对）。
- `.runtime/session_registry.json`：ramp 条目 **0**（在册仅 st-final3-20260919）。
- `git status` 对 `src/zephyr/infrastructure/rollback/rollback_verifier.py`：干净，无未提交改动。
- `lock_files.py cleanup` = CLEAN；runtime 面 grep st-ramp-wp1b 零残留 claim。
- 其回执已由总包入库：`docs/_working/rule_audit_campaign/CONSTRUCTION_LEDGER.md` L1513-1846；
  原始探针/RECEIPT 仍在 `.runtime/tmp/st-ramp-wp1b-20260919/`（**24h TTL 风险**，正文已入 tracked 册，探针属过程仪器可失）。

## 2. 完成度对照真源 WP1 卡（gate-identity-root-fix-plan §WP1）

| 处方项 | 状态 | 载体 |
|---|---|---|
| 改1 `heal_db_consistency` 按活库实列重写（`passed` 非 `result`；`gate_run_id` 定位；不吞异常） | **已落地** | `ee54c976f1`（dev 祖先亲验） |
| 改2 `clean_pycache` 三重护栏（is_relative_to/仓根标记/先验后删，命中拒删抛 `PycacheGuardError`） | **已落地** | `413edaff0e`（dev 祖先亲验） |
| 改3 `src/data/drift_audit/drift_events.db` 取证 | **已入库**（R-A19/R-A20/R-A21） | `05686e10e2`（st-fullflow 承接入库；取证车道 st-ramp-wp1c） |
| 不做：`gate_persistence.persist_gate_decision` INSERT | 遵守未触碰 | 回执逐条对处方表 |

## 3. 红证亲验（本次复跑，非转抄）[亲验]

1. 改2 护栏探针复跑 `.runtime/tmp/st-ramp-wp1b-20260919/_pycache_guard_probe.py`：
   改前（HEAD 副本）临时树 2 个 `__pycache__` 被真删（removed=2）；改后抛
   `PycacheGuardError: …缺 ['.git','AGENTS.md'] 任一标记`，目录清单删除前后 8 项逐项相同（零删除）。PROBE_EXIT=0。
2. 改1 红蓝探针复跑 `_redblue_probe.py`：S2 改前 `tasks.status READY→FAILED` 被真写（C-0 地雷实锤），
   改后两种模式均 0 改写；S3 幻影表 `gates(gate_id,result)` 改前假绿 `gates_fixed=1`，
   改后抛 `HealRefusedError: no such column: gate_run_id`。REDBLUE_EXIT=0。
3. `PYTHONPATH=src python -m pytest tests/rollback/ -q` = **708 passed / 7 xfailed / 2 xpassed**（139s），
   与回执批2 后数字逐字一致。
4. 现值复核：`src/data/drift_audit/drift_events.db`（+shm/wal）**仍在**（删除属门位第②类，待 Owner，符合预期）；
   root 误解析仍是活体：`src/zephyr/gov_enforcement/rule_enforcement/drift_detector.py:59`
   `_PROJECT_ROOT = dirname×4(__file__)` ⇒ 落 `D:\ZephyrAlpha\src`（R-A20 结论现测成立）。

## 4. 身份键现值实测（移交下游波次的分母基线）[亲验，governance.db mode=ro]

- `gate_registry.yaml` distinct gate_id = **169**。
- `gate_runs` distinct = 844，∩ gate_registry = **0**；`gates` distinct = 1008，∩ gate_registry = **0**。
- `gate_trigger_log` **不存在** ⇒ WP2（持久触发台账+记放行+强制归因）未落地。
- ⇒ "三命名空间映射表产出、交集>0"**不是 WP1 的验收项**（真源 WP1 卡=修两个坏写入端+改3 取证），
  属 WP2→WP3→WP4 链；W1-H 不越权代建（总方案 §6：改门禁执行链=Max 门位）。上表即下游开工基线。

## 5. 待裁清单移交（全部已有明确受理人，非本战役施工项）

| # | 事项 | 受理 |
|---|---|---|
| 1 | 改3 收尾 F-1(删野库)+F-2(修 root 派生 137 处/异常 23 处) 同批判序 | **Owner 门位**（第②类删文件；R-A20：只删库不改 root 必复发） |
| 2 | 回执④.1 fail_open_register 口径不匹配（已取"抛出"分支） | Max |
| 3 | 回执④.2 `max_rows` 出厂默认（无唯一现场来源，未自拍） | Max |
| 4 | 回执④.3 `passed NOT IN (0,1)` 不可达分支去留 | Max（与 WP16 并案） |
| 5 | 回执④.6 "活库列名校验+删除护栏"能力卡登记与否 | 总包/Max |
| 6 | 回执④.7 护栏②是否加 REPO_ROOT 真源第四护栏 | Max（与 R-A19/R-A20 并案） |
| 7 | RULING-REFERENCE 门禁不分"引用/报告缺号"（取证车道三次被咬） | Max（门禁语义=门位） |

## 6. W1-H 战线终态

- 施工收尾：**无事可做**（改1/改2 已在 dev，工作区干净，工棚已不存在，claim 已释放）。
- 核验红证：**全部通过**（§3 四项）。
- 工棚收尾半句（台账 W1-H 原文"st-ramp-wp1b 件+工棚收尾"）：工棚本体不存在，无拆除对象；
  W9-6② 的 auditdoc-v4/ruledisp 两条工棚属另一任务，不在本件范围。
- 移交：§5 七项待裁已有受理人；下游施工=WP2（波2），基线见 §4。
