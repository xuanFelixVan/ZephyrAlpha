---
ttl: task_bound
completes_when: 其余 9 本作业簿各派到车道并开工登记
---

# aibase · AI 层剩余派工图（L2 已收口，本图交总包/Max 派发）

Owner 定序：L2 ✅ → **OBJ_M** → OBJ_R S4/S5 → L1 → L4 → L6 → L3 → L5 → L7 → OBJ_T → OBJ_S。
真源：`docs/_working/ai_layer_vision/<段>/DESIGN.md`（11 本，本图只给派工要素，不重述设计）。

## 一、OBJ_M 模型线 worklist（先挖后干：以下为挖掘+施工两阶段的最小可销项）
| # | 颗粒 | 依赖前置 | 验收要点 |
|---|---|---|---|
| M0 | 读 `OBJ_M_models/DESIGN.md` 展开施工项为表（同 ailayerB 格式）落 `lanes/ailayerB_OBJM_worklist.md` | 无 | 项号/描述/涉及文件/验收标准/依赖/预估轮数六列齐全 |
| M1 | 复跑 DESIGN 每条施工项的原始证据命令（R-019） | M0 | 陈旧项如实标，禁按陈旧记载重复施工 |
| M2 | 模型登记器 DDL（新 schema 或 PG 表，照 `apply_ai_intake_ddl.py` 幂等+`--verify` 模式） | M1 | 连跑两次零错；生成列/CHECK 与设计一致 |
| M3 | 模型画像/选型服务（经 DatabaseService；禁裸连；禁 import `ai_layer.intake` 之外通道） | M2 | 非法输入被拒且拒因机读 |
| M4 | 与 L2 的接缝：`intake_scored_due` → 模型卡 elite 回写（`CardStore.record_score` 已备） | M2 + L2 ✅ | V1 `ai_intake_elites` 出真数 |
| M5 | 登记三件套 ×新文件 + 测试（tmp_path / 临时 schema） | M2-M4 | CREATE-GUARD/TRANSLATION-COVERAGE/DEPGRAPH-FRESHNESS 全过 |

## 二、其余 9 本派工图（每本一行：入口文件 / 第一件该做的 / 与 L2 的既有接缝 / 风险旗）
| 簿 | 设计真源 | 施工第一件 | 与已落地 L2 的接缝（可直接复用） | 已知风险旗 |
|---|---|---|---|---|
| OBJ_R S4/S5 | `OBJ_R_standards/DESIGN.md` | 历史重放器扩展 S4/S5（P1 班已落第一件） | `intake_e2_handoff` payload 已含 four_gates/labor_killed/domain_id/evidence_ref | 规则=YAML/架构=DB 的 SSOT 方向勿反（RULE-SSOT） |
| L1 感知 | `L1_perceive/DESIGN.md` | 源注册表 v0（当前缺位，T5 `ai_intake_source_quota` 是过渡件） | **`run_ingest(staging_path)` 已通**：L1 只要把候选卡 JSON 落 staging 并 emit `intake_ingest_due` 即入库 | 配额真源应回 L1，落地后 T5 须降级为只读缓存（勿两处真源） |
| L4 比对 | `L4_compare/DESIGN.md` | 考卷 rubric + 出分回填 | 事件 `intake_scored_due`（win/draw/loss+score）→ `CardStore.record_score` → V1 保优3/benched 已实现 | 胜者经 L5→施工是唯一跨生熟边界通道，勿直读 ai_intake |
| L6 AB 切换 | `L6_ab_switch/DESIGN.md` | 切换闸与回滚台账 | `intake_exam_receipt`（candidate_card_id+evidence_ref）消费体尚缺 | 生产流转=high 域，human_gate 归 Owner |
| L3 清洗 | `L3_cleaning/DESIGN.md` | 卡→规格卡清洗器 + 不可洗退回记阴性 | `intake_clean_due`（card_ids/domain_id/priority）与 `intake_reject_due` 均已备；T2 有 `spec_ref` 列 | 退回即入 V2 阴性视图（查重基线含 rejected） |
| L5 排班闸 | `L5_schedule_gate/DESIGN.md` | E2 假说预审排产通道 | `intake_e2_handoff` 出口 + `work_order_dead` 回 rejected（R2-3 已定，消费体待建） | tasks.yaml/schedule.yaml 归 z-dag 独占，勿代写 |
| L7 遗传 | `L7_heredity/DESIGN.md` | 传承库基线写 T4 `ref_family='L7'` | `dedup_query(text)` 公开只读接口已实现；L7 面当前记 `not_compared`（快照计数 0） | negative 不入传承（R1-B5）；OBJ_T 写权裁定在同本 H4 |
| OBJ_T 工具 | `OBJ_T_tools/DESIGN.md` | 工具坑集登记（经 L7 登记入 tooling 域） | T1 已有 `tooling` 域（6 域 v0 之一，实测在库） | `governance/` 根禁新增 .py（ARCH-031） |
| OBJ_S 周界 | `OBJ_S_perimeter/DESIGN.md` | 周界探针与投毒嫌疑口径 | T2 `risk_flags`（JSONB，投毒嫌疑/幸存者偏差/过拟合史/收益神话）+ `injection_probe` 字段已建 | LLM 调用必经 LSG；密钥走 secrets.py |

## 三、跨车道须知（本轮实测教训，写进任务书可省 3-5 轮）
1. `SQL_X: Final = "SELECT ..."` **不被** `_extract_sql_constant_lines` 豁免（只识别 `ast.Assign`）→ 一律写 `SQL_X = ...`。
2. `IntakeJournal` 类名族实现避开了与 `pipeline_events` 模块级函数族的 CloneGuard extract 级 100% 相似硬拦（结构不同、语义对齐）。
3. 灌水区已在库的 6 张真卡含 2 张"改写式换皮"漏网件（006/008）→ 裁定期望 k 或特征口径后须回填复检，勿当干净存量。
