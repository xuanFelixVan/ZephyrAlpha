---
ttl: task_bound
completes_when: 接力车道据本表销完 L2 余项并完成 OBJ_M 主干
---

# 车道 aibase · 接力说明（sid=st-ff-aibase-20260918，2026-09-18 20:1x）

## 0. 一句话
L2 九项里 **C1/C2/C3/C4/C5/C6/C7/C8 全部落地并已入队提交**（q-20260918-st-ff-aibase-20260918-0001，14 文件），
C9 测试 5 文件**只完成 2 个**（conftest + test_dedup），OBJ_M 及后续 9 本**未开工**，只出派工图。

## 1. 已落盘勿回退（逐文件）
| 文件 | 状态 | 本会话做过什么（勿重复/勿回退） |
|---|---|---|
| `scripts/ai_layer/apply_ai_intake_ddl.py` | 在队 | SQL_SEED_DOMAIN 提常量（原函数内 f-string INSERT 触 NO-BARE-SQL）；`--verify` 实测 OK；PG 上 schema 已真部署 |
| `src/zephyr/ai_layer/intake/card_store.py` | 在队 | 9 处 `SQL_X: Final=` → `SQL_X =`（AnnAssign 不被 gate 豁免）；**遗留缺陷**：`IntakeCard` 读模型不暴露 novelty/mechanism |
| `src/zephyr/ai_layer/intake/dedup.py` | 在队 | 5 处同上；**遗留缺陷见 req_aibase_02（k=3 对短卡失效）** |
| `src/zephyr/ai_layer/intake/gate.py` | 在队 | 1 处同上；**新增** `candidate_from_mapping()` + `run_ingest()`（L1 staging→过闸→入库回执） |
| `src/zephyr/ai_layer/intake/events.py` | 在队 | `intake_ingest_due` 原返 `ingest_runner_not_wired`（假通道），已真接 `run_ingest`；`IntakeJournal` 新增 `schema` 参数并透传 CardStore |
| `src/zephyr/ai_layer/intake/kpi.py` | 在队 | 4 处 SQL 常量同上；阈值现可读（THD-INTAKE-001..004 已入 alert_threshold_registry） |
| `scripts/ai_layer/gen_intake_ref_snapshots.py` | 在队 | 已实跑两遍：3595 条真指纹入 T4（chart287/indicator102/algoflow3206） |
| `docs/01.../catalogs/alert_threshold_registry.yaml` | 在队 | +4 条 THD-INTAKE（safe_write_text CAS，entries 38→42） |
| `docs/01.../catalogs/capability_canonical_file_registry.yaml` | 在队 | 9 个 creation_token 批次登记 |
| `docs/01.../catalogs/module_translation_registry.yaml` | 在队 | 9 模块 name-zh + plain-zh 登记（主仓跑，entries=7133） |
| `tests/ai_layer/intake/conftest.py` + `test_dedup.py` | 在队 | 12 passed（含 known-gap 钉） |
| `adjudications/req_aibase_01_init_basename.md` / `req_aibase_02_simhash_k3_short_text.md` | 已 staged 未提交 | 交 Max/Owner |

## 2. C9 余项（3 个文件，内容已定，照抄即可）
- `test_gate.py`：闸机检矩阵（labor 六态/四闸缺键/provenance/单来源封顶 cap_stage=L1/来源不足拒/data_eng quality_gaps/
  license 六态含 lgpl 只标 read_only_limited 不拒/年份六态含 2000 与 3000 边界/`candidate_from_mapping` 忽略未知键/
  超配额拒（在 `test_schema` 插 T5 daily_quota=0）/被拒零副作用 `stage_of() is None`/`run_ingest` 拒缺失与坏 JSON）。
- `test_card_store.py`：状态机 LEGAL 5 边 + ILLEGAL 8 边 + 入 rejected 5 边 + unknown stage + 同态 noop；
  `render/parse_simhash` 回环与越界 ValueError；`CardStore(schema='public')` 拒；
  insert/get/transition 回环 + 跳跃 RuntimeError + 缺卡 RuntimeError；rejected 终态禁复活；
  **record_score 四人同格→rank 1,2,3 active / 4 benched**；主键冲突；`count_today_by_source`/`list_by_stage`。
- `test_events.py`：7 kind 常量等值；emit 先落盘（读 JOURNAL_NAME 文本）；未知 kind/缺必填键/错挂 handler 三拒；
  drain 幂等（二次 processed==[] 且 handler 只被调一次）；毒丸 MAX_ATTEMPTS=3 后 `status()['poison']` 含该 id
  且幸存事件仍在 pending，`purge_poison` 返回 True；KillSwitch **不翻转生产闸**，改断言
  `drain()['stop_reason'] == (None if probe_kill_switch()[0] else why)`；ingest 坏 staging 计入 failed 不静默成功。
- `test_kpi.py`：`load_kpi_thresholds()` 生产值==(5.0,30.0,2,4)；**tmp YAML 换值即变**（证非硬编码）；缺条目 fail-closed；
  `evaluate_series` 健康带空/连2周 DEMOTE/连4周 LONGTAIL/>30 TIGHTEN/None 不判；`test_schema` 构造 6 卡（5 rejected+1 L0）
  → V3 视图 cards_total==6 且 rates_by_domain 出数。
- 跑法：`python -m pytest tests/ai_layer/intake/<f> -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" --basetemp=.runtime/tmp/ff-aibase-pc`

## 3. 变异证据（能红证明，§3.4）
本轮未做全量变异批；**已内建一条自证红的钉**：`test_known_gap_single_edit_escapes_k3` —— 任何人把
`HAMMING_K` 改大或对短文本放宽，该测试即红。补齐 C9 三文件后请对 `check_labor_killed` 长度阈值与
`check_stage_transition` 前进一步判据各做一次变异（改 → 必须红 → 按字节还原）。

## 4. 下一步（按 Owner 序）
OBJ_M 模型线（worklist 未出，先挖后干照 ailayerB 格式落 `lanes/ailayerB_OBJM_worklist.md`）→ OBJ_R S4/S5 → L1 → L4 → L6 → L3 → L5 → L7 → OBJ_T → OBJ_S。
派工图=`lanes/aibase_dispatch_map.md`。

## 5. R-019 复跑结论（供后续车道少走弯路）
- worklist 声称"已登记 `req_ailayerB_02.md` 备查" → **实测不存在**（adjudications/ 仅 tdchainJ×3 + wiresafe×1）。
- worklist 声称 C1-C7 未开工 → **实测 7 个 .py 已在盘（untracked）且 PG schema 已真部署**（含 `ai_intake_test_smoke`/`_smoke2` 两个残留测试 schema 未清）。
- 三项登记（token/翻译/depgraph）实测 **0 命中** → 本车道补做。
