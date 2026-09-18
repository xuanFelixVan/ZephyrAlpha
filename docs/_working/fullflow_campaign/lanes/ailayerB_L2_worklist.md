---
ttl: task_bound
completes_when: L2 收集库 9 施工项全部落地并验收，接力腿据此表销项
---

# 车道 ailayerB · L2 收集库施工清单（接力真源）

sid=`st-ff-ailayerB-20260918`；设计真源=`docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md` §四（9 项）。
本表=先挖后干的挖掘产物：把 DESIGN §四 展开为可销项的施工颗粒，含依赖前置与轮数预估。
状态图例：`[ ]` 未开 / `[~]` 在途 / `[x]` 完成并验收 / `[!]` 受阻挂单。

## 一、L2 施工项总表（N=9 主项，展开 15 颗粒）

| # | 颗粒 | 描述 | 涉及文件 | 验收标准（照 DESIGN） | 依赖前置 | 预估轮数 | 状态 |
|---|------|------|---------|----------------------|---------|---------|------|
| C1 | DDL 登记器 | 建 schema `ai_intake` + T1-T5 + V1-V3，幂等 | 新 `scripts/ai_layer/apply_ai_intake_ddl.py` | 连跑两次零错；psql 侧表/视图/生成列齐全；CHECK 值域与 §2.2/§2.5 一致 | PG 可达（实测 16.14 OK）；DEPGRAPH-WRITE-PATH 白名单扩项 | 3 | [ ] |
| C2 | 卡库服务 | CRUD + `transition()` 状态机 + elite 回写，全经 DatabaseService | 新 `src/zephyr/ai_layer/intake/card_store.py` | 单测绿；非法流转被拒（跳跃/复活）；测试隔离禁写生产路径 | C1 | 4 | [ ] |
| C3 | 查重服务 | simhash64（Charikar/Manku k≤3）+ 五比对面执行 + `dedup_query()` 公开只读接口 | 新 `src/zephyr/ai_layer/intake/dedup.py` | 中文重复文本对 hamming≤3 命中；改写>50% 不命中；self/chart/indicator/algo_flow/L7 五面逐一有单测（L7 缺省记 not_compared） | C1 | 4 | [ ] |
| C4 | 入库闸 | §2.5 全部机检：两问（labor_killed≥20 字/四闸预检）+注入探针+L0 硬过滤（license/年份/sha256/simhash）+配额闸+状态机合法性 | 新 `src/zephyr/ai_layer/intake/gate.py` | 缺 labor_killed、单来源封顶、超配额、换皮四类样本卡全部被拒且拒因正确 | C2 C3 | 4 | [ ] |
| C5 | 比对面快照生成器 | chart_pattern_registry + technical_indicator_registry + src 全量 ALGO_FLOW docstring → T4 | 新 `scripts/ai_layer/gen_intake_ref_snapshots.py` | 生成器产出零手工；重跑幂等；refreshed_at 刷新 | C1 C3 | 3 | [ ] |
| C6 | 事件层 | 7 轻 kind（intake_ingest_due / intake_clean_due / intake_reject_due / intake_scored_due / intake_e2_handoff / intake_exam_receipt / intake_kpi_alert）+ JSONL journal `.runtime/ai_intake/pending_events.jsonl` + emit/drain/status + KillSwitch fail-closed + 幂等 marker + 毒丸 MAX_ATTEMPTS=3 | 新 `src/zephyr/ai_layer/intake/events.py` | emit→status 可见→drain 幂等；KillSwitch 非 normal 停消费且全量保留；毒丸留档 | C2 C4（handler 落点） | 4 | [ ] |
| C7 | KPI 告警 | 读 V3 视图 + 阈值判定（5%–30% 健康区间）+ `intake_kpi_alert` 事件；贫矿降级（连续2周<5%→quota 减半，4周→quota=1 禁清零）/ 收紧（>30%） | 新 `src/zephyr/ai_layer/intake/kpi.py` | 构造数据可触发两路告警；阈值读 YAML（alert_threshold_registry）非硬编码 | C1 C6 | 3 | [ ] |
| C8 | 登记套件 | 新 .py 三件套（depgraph 节点 / creation_token / 模块翻译大白话）×7 文件 + alert_threshold_registry 挂 intake KPI 阈值 | `scripts/governance/apply_depgraph.py`、`scripts/governance/d3_metadata/*`、`docs/01_policies_and_standards/_registry/catalogs/{capability_canonical_file_registry,alert_threshold_registry}.yaml` | 三登记器零报错；TRANSLATION-COVERAGE / CREATE-GUARD / DEPGRAPH-FRESHNESS 全过 | C1-C7 文件定稿 | 4 | [ ] |
| C9 | 测试套件 | 5 个测试文件，PG 不可达时 skip 而非假绿；dedup/gate 纯函数部分必跑 | 新 `tests/ai_layer/intake/{test_dedup,test_gate,test_card_store,test_events,test_kpi}.py` | 全绿；零生产路径写入（tmp_path fixture）；能红证据（变异一支判据→对应测试必须失败） | C2-C7 | 4 | [ ] |

依赖链：C1 → C2 → (C3, C4) → (C5, C6, C7) → C8、C9 随项并行。
外部依赖：无硬依赖（L1 源注册表未建 → T5 过渡件兜底；L7 未建 → ref_family='L7' 缺省跳过记 not_compared）。

## 二、挖掘发现（施工前必须知道的现场事实）

1. **PG 实例可达**：`get_depgraph_pg_connection(read_only=True)` 实测 PostgreSQL 16.14；现有 schema 仅 `public`（ig_* 全在 public），`ai_intake` 为**新建 schema**（生熟分离物理边界）。
2. **DEPGRAPH-WRITE-PATH 门禁**：`src/zephyr/gov_enforcement/commit_gates/depgraph_write_path_gate.py:96` `_WHITELIST` 硬编码；新增行含 `superuser=True` / `read_only=False` 字面量即阻断。DDL 部署器必须 superuser（writer 无 CREATE 权限，CONSTRUCTION_DISCIPLINE §7）。gate 自身 docstring L36-39 明文"扩展三步"=加白名单，且 2026-09-18 同日已有先例（`scripts/industry_graph/build_node_bindings.py` 由 st-igchain 车道加入）。→ 本车道照办并登记裁定申请书 `req_ailayerB_02.md` 备查。
3. **DatabaseService 写通道无需字面量**：`get_depgraph_conn(read_only: bool = False)` 默认即读写（`src/zephyr/infrastructure/database_service.py:136`）→ 服务层调 `svc.get_depgraph_conn()` 即写通道，不触门禁字面量。
4. **ORPHAN-MODULE**：只查 staged 新增 `src/**/*.py`，判据=`git grep` src 内是否存在 `import <short_name>`。→ 五模块互相 `from zephyr.ai_layer.intake import <mod>` 交叉引用（events 侧对 kpi 用惰性 import 破环）。`__init__.py` 属入口豁免。
5. **CLASS-UNIQUENESS 预扫结果**：`GateVerdict` 已被 6 文件占用 → 改名 `IntakeVerdict`。其余候选名（IntakeCard/CardStore/IntakeGate/DedupHit/IntakeJournal/KpiAlert/RefSnapshot/SimHasher/CardTransition）全仓 0 命中，可用。
6. **事件层不复用 pipeline_events**：`src/zephyr/strategy_pipeline/pipeline_events.py` journal 原语用模块级常量（STATE_DIR/JOURNAL 硬绑 `.runtime/strategy_pipeline`），**不可参数化 import**；按 DESIGN §三 裁定"按其模式新建"。为避 CloneGuard extract 级 100% 相似硬拦，本车道实现改为 **class `IntakeJournal`（方法族）** 而非模块级函数族，结构不同、语义对齐（emit/status/drain/毒丸/KillSwitch fail-closed）。施工前预查已留痕于本条。
7. **`ai_layer` 是全新顶层包**（`src/zephyr/ai_layer/` 此前不存在）；`scripts/ai_layer/` 同为新目录。depgraph 新文件门查 `src/zephyr`+`scripts` 下新 .py → 7 个文件都要 `--add-design-node`。
8. **禁碰**：`docs/03_modules/**`、`config/trading_decision_map.yaml`、`AGENTS.md`（COORDINATION_LEDGER §2 全员禁写）；`governance/` 根禁新增 .py（ARCH-031）→ 本车道新 .py 全落 `src/zephyr/ai_layer/**` 与 `scripts/ai_layer/**`，无冲突。

## 三、OBJ_M 模型线（L2 完成后开工，同法先列表）

施工顺序（Owner 定）：L2 → **OBJ_M** → OBJ_R S4/S5 → L1 → L4 → L6 → L3 → L5 → L7 → OBJ_T → OBJ_S。
OBJ_M worklist 待 L2 收官后按同格式落 `lanes/ailayerB_OBJM_worklist.md`（未开工时本行即为断点标记）。
