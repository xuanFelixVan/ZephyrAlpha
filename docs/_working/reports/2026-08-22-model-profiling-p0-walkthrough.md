---
ttl: task_bound
---

# 模型画像流水线 Phase 0 手动链路验证报告（06号文 §4 Phase 0）

- 日期：2026-08-22
- 工单：18号清单 §6 波3-06（GP0 退出项 E0-5 之一）
- 设计真源：`docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/06_model_profiling_pipeline.md` §4 Phase 0（P0-1~P0-5）
- 范围纪律：未执行 git；未写注册表 yaml；src 零改动（全部实测 PASS，无需小修）；一次性验证脚本置 `.runtime/tmp/`，用完即删；mock/fixture 产物验证后已清理，数据目录恢复原状。

## 环境基线（2026-08-22 实测）

- Python 3.12.8，`zephyr` 包可 import（src layout 已入路径）
- **Ollama 离线**：`http://localhost:11434/api/tags` 连接超时（Invoke-RestMethod 实测）——真实 Quick 考试（`--model`）不可执行，P0-3 按工单预案降级

## 逐项结论

| 步骤 | 验收标准 | 结果 | 说明 |
|---|---|:---:|---|
| P0-1 | `TaskGate().load_passports()` 返回 7 | **PASS** | 实测返回 7 |
| P0-2 | 门控三样例与护照内容一致 | **PASS** | 三样例全部命中期望值 |
| P0-3 | 手动 Quick 考试生成 quick_profiles/&lt;model&gt;.json | **PASS（降级实证）** | Ollama 离线 → 降级为两段实证（零推断 CLI + mock 注入全链路落盘回读） |
| P0-4 | 盘点 data/model_learning/ 与 data/model_profiles/ | **PASS** | 盘点完成，与 06号文 §2.4 口径一致（1 处小幅更正，见观察项 O4） |
| P0-5 | CLI `history` 能读历史记录 | **PASS** | 空历史/非空双分支均实证，EXIT=0 |

**Phase 0 总结：5/5 PASS（其中 P0-3 为降级实证）。无 FAIL 项，无小修。**

---

## P0-1：护照加载

命令：`python .runtime/tmp/p0_verify_gate.py`（一次性脚本，已删）

```
[P0-1] load_passports() -> 7
[P0-1] loaded model_ids: ['deepseek-v4-flash-non-thinking', 'deepseek-v4-flash-thinking',
 'deepseek-v4-pro-non-thinking', 'deepseek-v4-pro-thinking',
 'qwen2.5-coder:14b', 'qwen3-coder:30b', 'qwen3:8b']
[P0-1] PASS (expected 7)
```

证据要点：`data/brain/passports/` 落盘 7 份 JSON 全部经 `CapabilityPassport.list_all()`→`load()` 链加载成功，模型族覆盖与 06号文 §2.4 护照清单一致。

## P0-2：门控三样例

同一脚本逐样例调用 `can_dispatch`（判定逻辑：无护照→`no_passport`；无 depth→`no_depth_data`；能力未考→`capability_not_tested`；`pass_=false`→`low_accuracy: <failure_reason>`）：

```
[P0-2] can_dispatch('qwen3:8b', 'naming_suggest')  -> (True, 'ok')                                        PASS
[P0-2] can_dispatch('qwen3:8b', 'code_fix')        -> (False, 'low_accuracy: low_precision_below_threshold') PASS
[P0-2] can_dispatch('deepseek-r1:8b', 'naming_suggest') -> (False, 'no_passport')                          PASS
```

与护照内容交叉核对（`data/brain/passports/qwen3_8b.json` 全文读取）：`naming_suggest.pass_=true`（f1=0.556）、`code_fix.pass_=false`（f1=0.353，`failure_reason=low_precision_below_threshold`）——门控输出与落盘数据严格一致；`deepseek-r1:8b` 无护照（06号文已实测纠正：无 deepseek-r1 系列护照），正确拦截。

## P0-3：手动 Quick 考试（降级实证）

**降级原因**：Ollama 本机离线（实测超时），`scripts/quick_profile.py --model <m>` 的真实推断路径不可执行。按工单预案降级为两段实证，链路可走通已证实，分数无意义不采信。

**段 1 — 零推断 CLI 链路**：`python scripts/quick_profile.py --from-passport qwen3:8b` → EXIT=0，完整打印能力轮廓（9 能力）/幻觉九维/成本明细/岗位推荐 Top3 报告。
注：`--from-passport` 是「视图」模式，只打印不落盘（`_profile_from_passport` 无 `save()` 调用）；落盘仅在真实 Quick 考试路径（`_run_quick_exam` 内 `profile.save()`）。

**段 2 — mock 注入全链路**：FakeChat 替身（满足 `_infer` 的 `chat.inference(capability, prompt) -> dict` 契约）注入 `ExamOrchestrator`，实跑 `run_quick_exam()`（31 能力 × 1 代表题 + 幻觉检测，全部 mock 秒级完成）：

```
[P0-3] run_quick_exam OK: overall_grade=F score=0.15
[P0-3] capabilities graded: 31
[P0-3] saved -> D:\ZephyrAlpha\data\brain\quick_profiles\mock-p0-ollama-offline.json  exists=True
[P0-3] QuickProfile.load('mock-p0-ollama-offline') -> OK
[P0-3] reloaded: exam_mode=quick caps=31 hallu_overall=0.000
[P0-3] cleanup: removed mock artifact mock-p0-ollama-offline.json
```

即：考试主控 → QuickProfile 构造 → `save()` 落盘 `quick_profiles/<model>.json` → `load()` 回读，全链路走通。mock 产物验证后已删除，`data/brain/quick_profiles/` 恢复原状（仅既有 `qwen3_8b.json`）。

**注记保留**：QuickProfile 不带 HMAC 签名（`capability_passport.py` 实测，`save()` 无签名段）——它是轻量画像视图，非门控真源；转正式护照须跑 Standard 考试。

## P0-4：数据目录盘点

| 目录 | 实测内容（2026-08-22） | 一句话结论 |
|---|---|---|
| `data/model_learning/` | 仅 `task-model-matrix.json`（1 份） | `matrix: {}` 空矩阵 + `benchmark_baseline`（M1~M4/M6~M11 共 10 维 × qwen3:8b / deepseek-r1:8b 基准分）+ `saved_at=2026-06-23`——运行时表现数据尚未回流，与 06号文 §2.1 判断一致 |
| `data/model_profiles/` | 目录存在，**完全为空**（0 文件） | 24 个 0 字节 `.tmp` 残留清除后无正式 `.jsonl` 产出，与 06号文 §2.4「当前无正式 .jsonl」一致 |
| `data/brain/quick_profiles/`（附带核对） | 仅 `qwen3_8b.json`（4015 字节） | 与 06号文 §2.4 一致 |

## P0-5：画像 CLI `history` 子命令

命令：`python -m zephyr.intelligence.model_profiling.cli history`（cwd=仓根）

- **空历史分支**（现状）：输出 `暂无 benchmark 历史记录。`，EXIT=0。
- **非空分支**（临时 fixture 实证）：投入 1 行 JSON 的 `benchmark_20260822_p0fixture.jsonl` 后输出——

```
  Benchmark 历史记录 (1 次)
  20260822_p0fixture  ->  1 models, 0.1KB
```

解析逻辑（record_count 计数 / size_kb 计算 / 时间戳提取）工作正常，EXIT=0。fixture 验证后已删除。

## 小修清单

**无。** P0-1~P0-5 全部实测通过，未发现需要修复的测试错误或明显 bug。

## 观察项登记（非 FAIL，不修，供后续 Phase 参考）

| # | 观察 | 定性 | 处置建议 |
|---|---|---|---|
| O1 | Ollama 离线导致真实 Quick 考试不可跑，P0-3 只能降级实证 | 环境状态，非缺陷 | 夜间/空闲时段启动 Ollama 后可补跑一次真实 `--model qwen3:8b`（5-8min） |
| O2 | `CapabilityPassport.list_all()` 将文件名所有 `_` 转 `:`，故 `gate.passports` 的 key 为 `qwen3-coder:30b`/`qwen2.5-coder:14b`（冒号版），而护照内 `model_id` 字段为 `qwen3-coder_30b`/`qwen2.5-coder_14b`（下划线版）——同一对象两种 ID 口径；若下游拿 `passport.model_id` 回调 `has_passport()/can_dispatch()` 会 miss 返回 `no_passport` | 潜在 ID 口径隐患；当前 [CONSUMERS] 空无消费方，不影响 P0 验收 | Phase 2 接 dispatch 链前统一 ID 口径（建议以护照内 `model_id` 字段为准），属行为变更需随消费方接入一起做 |
| O3 | mock 考试期间 case_assembler 输出 5 条降级日志（`文件缺失，降级占位: scripts/governance/verify_schema_health.py 等`、`路径越白名单: git_commit_gateway.py`） | 题库组装器健壮性 fallback 日志，非错误 | 登记；题库引用文件清单与实际仓库状态的核账归 MOD-INF-036 维护侧 |
| O4 | `task-model-matrix.json` baseline 实测为 M1~M4/M6~M11 共 **10 维**（缺 M5）；06号文 §2.4 记为「M1~M7」 | 文档小口径差 | 06号文下次刷新时按实测更正 |
| O5 | `run_quick_exam` 实跑覆盖 **31** 能力（`CAPABILITIES` 清单），06号文/脚本 docstring 记 29 | 代码已扩展（v3.0.5 新增能力），文档滞后 | 06号文下次刷新时更正 |
| O6 | `cli.py cmd_history` 用相对路径 `Path("data/model_profiles")`，依赖 cwd=仓根 | 与项目「仓根运行」约定一致，非缺陷 | 不处理 |

## 产物与清理

- 一次性脚本：`.runtime/tmp/p0_verify_gate.py`、`.runtime/tmp/p0_mock_quick_exam.py`、`.runtime/tmp/p0_from_passport_out.txt`——验证完成后全部删除。
- mock QuickProfile `mock-p0-ollama-offline.json`、history fixture `benchmark_20260822_p0fixture.jsonl`——验证后立即删除，数据目录恢复原状。
- src/ 与 data/ 下无任何残留改动。
