---
ttl: task_bound
title: ADJ 案卷·emoreplay 复职批验收就绪度（qid/分支/10 测/悬空引用）
---

# ADJ · emoreplay 复职批验收

## ① 一句话问的是什么

情绪指数全历史回放班（st-emoreplay-20260923）的两袋早已阵亡、11 件内容至今在盘不入 HEAD——问的是：**这份复职批现在能不能判"已批待执行"，以及验收清单缺哪几项**。

## ② 现状实测

### 2.1 在哪个 qid / 分支

| 项 | 实测值 |
|---|---|
| 袋 1 | `.runtime/commit_queue/dead/q-20260923-st-emoreplay-20260923-0001.json`，created 09-23 20:10:17，dead_at 09-23 20:21:49，11 件 |
| 袋 2 | `q-20260923-st-emoreplay-20260923-0002.json`，created 09-23 20:42:38，dead_at 09-23 21:10:29，11 件 |
| 分支 | 两袋 `branch: dev`；`base_head` 字段=**None（未记录）**——重投时无法机械核对基线，属登记缺陷 |
| 会话分支 | `git branch -a` 实测存在本地分支 `session/st-emoreplay-20260923`（`+` 前缀=已被某 worktree 占用） |
| worktree | `.worktrees/` 下**无** st-emoreplay 目录（实测 `ls .worktrees/ | grep -i emoreplay` 无匹配）→ 会话 worktree 已回收 |

### 2.2 两袋死因（互不相同，实测 dead_reason 原文）

1. 袋 0001 = `DIRECTORY-CONTRACT 阻断`：`docs/_working/emotion_line/gpu_emotion_condition_matrix_v1.meta.json` 扩展名 `.json` 不在 `_working` 允许清单（`.csv/.html/.md/.yaml`），触 DCR-005+DCR-008。
   → 袋 0002 已把该件改名为 `…meta.yaml`（实测两袋文件清单对比），**死因 1 已在袋 2 内自愈**。
2. 袋 0002 = `TRANSLATION-COVERAGE 阻断`：`新建 .py 缺合格 plain_zh 大白话简介 —— src/zephyr/alt_data/emotion_index_replay.py`。
   → 实测当前册 `module_translation_registry.yaml` **已有 1 条** `module_path: src/zephyr/alt_data/emotion_index_replay.py`（grep 计数=1）。**但"在册"不等于"在册且 plain_zh 合格"**——本班未逐字段核该条目是否含合格 plain_zh（缺一项硬证据，见 §⑥）。

### 2.3 10 项测试现状（实测跑通）

- 测试件：`tests/alt_data/test_emotion_index_replay.py`，实测 `grep -c "^def test_"` = **10**，用例名：`test_slice_reader_byte_equivalence / test_join_shape_bypasses_slice / test_replay_rows_bit_identical_to_builder / test_replay_skips_none_days / test_partition_chunks_respects_cap / test_write_replay_rows_chunks_executes / test_write_replay_rows_skips_live_keys / test_verify_equivalence_red_signal / test_pit_live_value_check_green_and_red / test_empty_wide_fetch_fail_visible`。
- 本地实跑：`python -m pytest tests/alt_data/test_emotion_index_replay.py -q` → **10 passed in 119.19s**（2026-09-25 21:4x 实测，全绿）。
  - 坑登记：加 `-p no:cacheprovider` 会 `INTERNALERROR`（`pyproject.toml` 配了 `cache_dir` 且 `filterwarnings=["error",...]`，禁用插件后该键成 unknown option 被升级为 error）。复跑勿带该旗。
- 件态实测：`src/zephyr/alt_data/emotion_index_replay.py`、`tests/alt_data/test_emotion_index_replay.py`、`docs/_working/emotion_line/gpu_emotion_condition_matrix_v1.csv` 三件均 **HEAD=NO / 主区盘=yes** → 全批 11 件仍是"盘上在途、HEAD 查无"。

### 2.4 悬空引用复查方法（可复算，四条）

1. **在册不在库型**（最重要）：册里引用了路径、HEAD 里却没有该文件 → 任何按册加载的消费者运行时炸。
   方法：对 `capability_canonical_file_registry.yaml`、`module_translation_registry.yaml` 逐条 `git cat-file -e HEAD:<path>`；本次实测 `capability_canonical_file_registry.yaml:5146` 已引用 `src/zephyr/alt_data/emotion_index_replay.py`，而 HEAD 无此文件 → **该引用是随本批同袋落地的（袋内含该册）**，所以只要整批落齐即闭合；**若拆袋单落注册册=制造悬空引用**。
2. **符号级断裂型**：本批 4 个代码件互相引用（`emotion_index_replay.py` ← `schemas/categories/market/market_emotion_index.py` source 列 ← `scripts/ch/apply_market_tables_ddl.py`）。
   方法：`python -c "import <module>"` 逐个冒烟 + `ruff check <file>`；再对 schema 侧跑 `scripts/ch/verify_schema_truth.py`（该件在仓，实测存在）。
3. **文档口径型**：袋内含 `docs/_working/emotion_line/history_replay_report_v1.md` 与 `index.md`，其中任何"已落库/已复职"陈述须以 HEAD 为准复核。
   方法：报数字必回 `ch_reader.query` 实测，且判"无数据"前换 reader 复核（本仓 `ch_writer.query` 出错返回空串不抛）。
4. **重放幂等型**：`test_write_replay_rows_skips_live_keys` 已把"不覆盖在产 live 键"钉成测试（用例名即证据，实测），复职重灌前须确认该测试仍绿（本卷实跑已绿）。

### 2.5 验收清单完备度判定

| 判据 | 现状 | 依据 |
|---|---|---|
| 死因清零 | 部分（DCR 已自愈；TRANSLATION 待核 plain_zh 质量） | 2.2 |
| 测试本地全绿 | ✅ 10/10 | 2.3 |
| 内容件与 HEAD 无冲突 | 未测（本班未做 11 件 blob↔HEAD 漂移比对） | 缺证据 |
| 注册册同批原子 | ⚠️ 必须与内容件同袋（见 2.4-1） | 实测引用态 |
| 落库面（CH 表/source 列 DDL） | 未测 | 缺证据 |
| 分支基线可核 | ❌ `base_head=None` | 2.1 |
| Owner 批文在册 | 07 号文 C2 第 7 行记"emoreplay 处方① ✅ 已批"，但该文档**不在 HEAD**（实测 `git cat-file -e HEAD:…07_pending_work_master_list.md` 失败），且 rulling_registry 最新条=**#413**、**无 emoreplay 专项裁定条目**（实测 231 条全册扫） | 照写：查无即查无 |

## ③ 可选路径

**路径 A：判"已批待执行"，直接重投（11 件一袋，含两册）**
- 代价：低（测试全绿、内容件齐）；须补 plain_zh 核验一步。
- 不可逆点：**DDL/落库面若含 `apply_market_tables_ddl.py` 的 source 列新增**，落地即触库；本卷未测该 DDL 的幂等与可逆性（RULE-DATA-OPS 三步验证未做）→ 该路径把"文件落地"与"数据面变更"混在一次提交里。

**路径 B：拆两袋——先落代码+测试+文档（9 件），DDL/落库另批走数据操作门**
- 代价：多一轮；且必须把两个注册册留在**代码袋**（否则 2.4-1 悬空引用）。
- 不可逆点：无（DDL 单独可逆性更好评估）。

**路径 C：判"未批"，先补正式批文再动**
- 代价：多等一次总筹/Owner；好处：批文可机判（ruling 条目+`approved_paths`）。
- 不可逆点：无。

## ④ 专业对照（外部论据，URL+发布方+年份；链接均经本车道 2026-09-25 检索存活核验）

1. **验收清单必须事前定义、逐条勾核，"能跑"不等于"完成"**：Atlassian Agile 指南《What is the Definition of Done?》（Atlassian，页面更新 2026-08）把 DoD 定义为"一组约定标准，全部满足才可声明工作完成"，并强调未逐条核验的完成声明会造成隐性技术债——对应本卷 §2.5 表里两项"缺证据"。
   - https://www.atlassian.com/agile/project-management/definition-of-done
2. **测试须自足、不得依赖外部/生产状态（hermetic）**：TensorFlow 官方《Testing best practices》（Google/TensorFlow 项目文档，2021 起）要求测试不读写外部共享状态、可重复执行；与宪法 §9.6"测试禁写生产路径、输出一律 tmp_path"同构，也是本卷"10 测全绿"可信的前提核验点。
   - https://www.tensorflow.org/community/contribute/tests
   （两条来源独立：项目管理厂商指南 / 开源框架官方测试规范。）

## ⑤ 风险（做错的最坏情形）

- **资金安全：低但非零**。`emotion_index_replay` 是**历史回放器**（写 `consensus`/`emotion` 类研究表），不触执行单源；但 2.2/2.4 显示它会**写 CH 表**（`test_write_replay_rows_*` 两例即写路径）。最坏情形=复职重灌覆盖在产 live 键 → 情绪轴真值被历史重放值改写 → 下游情绪因子/相位判定带脏数。缓解证据=该行为已被 `test_write_replay_rows_skips_live_keys` 钉住（实测通过）。
- 拆袋错序风险：注册册先行而代码件后落 → 悬空引用触发 REFERENCE-INTEGRITY/FK 红，全仓提交被连坐（本仓先例见 HANDOVER 血泪配方第 9 条）。
- 判"已批"的合规风险：07 号文不在 HEAD、ruling 册查无专项条目 → 若据 07 号文宣布"Owner 已批"，属**署名无正式通道凭据**（宪法 §9.11：对话内口头不构成门禁豁免）。

## ⑥ 解锁依赖（缺的硬证据）

1. `module_translation_registry.yaml` 那条 emotion_index_replay 条目的 **plain_zh 是否"合格"**（gate 的合格判据未读，须核 gate 实现或直跑该门）。
2. 11 件 blob ↔ 当前 HEAD 的漂移比对（本班未做；0033 卷同款方法可直接复用）。
3. `apply_market_tables_ddl.py` 对 `market_emotion_index` 的 source 列变更是否**幂等+可逆**（RULE-DATA-OPS 三步验证）。
4. 复职批的验收判据条目（17 号文是否有 emotion 线专属判据——17 号文在盘但本车道未逐条比对）。
5. 会话分支 `session/st-emoreplay-20260923` 相对 HEAD 的独有提交清单（`base_head=None` 的替代取证路径）。

## ⑦ 一句话推荐（推荐待总筹拍）

推荐 **B + 判"可批不可执行"**：即认可"复职方向已定、测试就绪（10/10 实测绿）"，但**先补 §⑥-1/2/3 三项证据、并把 DDL/落库拆成独立批走数据操作门**；不建议现在就判"已批待执行"，因为批文正式通道查无（ruling 册无专项条目）且写库面可逆性未证。
