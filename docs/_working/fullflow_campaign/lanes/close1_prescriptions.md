---
ttl: task_bound
completes_when: 收口车道 st-ff-close1 的两轮逐目录回归结论被总包采纳或转为裁定
---

# close1 处方与登记（车道 `st-ff-close1-20260918`）

> 本文件只收"我复跑过、能给出现场证据"的条目；未复跑的前手声明一律标"未验"。
> 表述纪律（#325）：不写"全绿/零问题"，只写"本轮检出 N 件通过且已被证明能红"。

## 1. 已修（属本车道写域）

### C-1 F06 E4 考试正对照被 R-055b 照出（HEAD 自带红，已修）
- 现场：`tests/backtest/test_f06_e4_wfa_exam.py::TestExamVerdictThreeLines::test_pass_all_stages_clean`
  在 `eb9e18f846` 上实跑 1 failed / 19 passed；否决理由原文
  `过拟合检测否决: 维度2(参数敏感性)未提供数据->不可判定->按不通过处理(R-055b); 维度3(泛化能力)...`。
- 取处方**甲（补灌维度 2/3）**，不取乙（把断言改成"不可上线"）：
  ① 该用例是 `TestExamVerdictThreeLines` 唯一的 `VERDICT_PASS` 正对照，乙等于删掉放行腿，
     `map_exam_verdict` 的 PASS 分支将再无覆盖 ⇒ 覆盖面净减少（放松方向）；
  ② "缺维必须否决"的牙齿已由三件既有专件持有（`test_overfitting_detector.py::TestDetect::
     test_no_dimensions_is_not_assessed_and_vetoed` / `test_rb_stats_validator_teeth.py::
     TestEvidenceSufficiencyGates::test_missing_dimensions_no_longer_pass_by_default` +
     `TestOverfittingDetectorFailClosedAfterR055b::test_omitted_dimensions_count_as_not_passed` /
     `test_strategy_validation_pipeline.py::TestPipelineHappyPath::
     test_minimal_request_is_vetoed_by_missing_dimensions`），在本文件重复钉是冗余。
- 顺带关一条假绿通道：旧夹具走 `map_exam_verdict` 的默认参数 `n_dims_evaluated=3`，
  等于替被测件谎报"三维已评满"；现按检测器实报的 `not_assessed_dimensions` 反推。
- 落地：`73ac06b1fe06075a0dc4a74d64d5e3d8cf4f363a`（1 文件 26+/3-，零外来文件）。
- 能红证据（变异台 `.runtime/tmp/st-ff-close1-20260918/mutate.py`，按字节改+还原，
  还原后 sha256 与原字节一致）：
  - **M1** 把 `overfitting_detector.detect()` 三处 `else` 分支改回旧语义（缺维=默认稳定）
    ⇒ 上述三件专件 **4 条用例全红**（`4 failed / 86 passed`），R-055b 的牙齿未被我修没；
    同批 `test_f06_e4_wfa_exam.py` 20 件在 M1 下仍绿 ⇒ 本车道修法与该争议语义**解耦**。
  - **M2** `PARAM_MAX_CHANGE_THRESHOLD 0.30→0.01` ⇒ `test_pass_all_stages_clean` 红，
    否决理由=维度2（"参数微调±10%导致Sharpe最大相对变化3.00%超过阈值1.00%"）
    ⇒ 证明补灌的维度2 数据真被消费，不是空断言。
  - **M3** `GEN_POSITIVE_RATIO_THRESHOLD 0.60→1.01` ⇒ 同件红，否决理由=维度3。

## 2. 登记（不属本车道写域 / 需总包或 Owner）

### P-1 ★ R-055b 把 **E4 正考件本身**静默改成"永远不通过 + 归因错误"（加严方向合法，但归因是假的）
- 现场（2026-09-19 探针，纯内存合成入参，零真库）：按 `scripts/backtest/f06_e4_wfa_exam.py`
  真实调用形状（只灌维度1、`n_dims=1`、四线全绿的"最有利幸存者"）跑 `map_exam_verdict` ⇒
  ```
  verdict = 不通过
  reasons = ['OOS阶段未通过(DSR落带=significant, OOS/IS比率=0.800); fail-closed判不通过']
  ```
  理由**与事实相反**：DSR 落带=significant、OOS/IS=0.800 ≥ 0.70，真实成因是"维度2/3 未供数"。
- 机制：`f06_e4_wfa_exam.py:463-468` 的"证据不足→存疑"腿挂在
  `if gate.overall_passed and not overfitting["is_overfitting"]` 之内；R-055b 后缺维即
  `is_overfitting=True`，于是该腿**永不触发**，控制流落到函数末尾的 FAIL 兜底分支。
  ⇒ 改变的是"**已毕业策略包的历史考试结论**"所在的那条判定路径（与 A17 同族），不是注释。
- 该文件自陈注释 `:459-460` 仍写"维度2/3 未评估 => **检测器按'稳定'计入**"——R-055b 后此句为假。
- 处方选项（**须总包裁定，本车道不动该文件**）：
  甲 让 `map_exam_verdict` 在缺维时显式走"证据不足→存疑"（读 `not_assessed_dimensions`，
     比末尾兜底更准，且保留"补维可升级"的通路）；
  乙 正考件补灌维度2/3（需参数扰动与跨时段实测数据 = 施工，不是改断言）；
  丙 维持现状但把归因文案改对（最低成本，仍不解决"存疑腿死码"）。
- 附：`scripts/backtest/f06_e4_wfa_exam.py` **不是任何 TDM 节点的 module_ref**
  （`grep -n 'f06_e4_wfa_exam' config/trading_decision_map.yaml` = 空）⇒ 修它**不触发** ALGO-NOTE-SYNC，
  不需要 TDM 授权（本条为总包省下"要不要开 TDM 口子"的一次判断）。

### P-2 `overfitting_adjudicator` 的跨模块口径声明已失效
- `src/zephyr/backtest/core/overfitting_adjudicator.py:517`：
  "未提供的检验器视为未检测(不参与否决), **与 overfitting_detector.detect 口径一致**"。
  R-055b 后两者**不再一致**（检测器=不可判定=否决，裁定器=不参与否决）。
- 该句是"同类件应对齐的口径指针"，留着会把下一位施工者往 fail-open 方向带。
  处方：要么把裁定器一起加严（同 #321 方向），要么把"口径一致"改成"口径不同，本件仍为缺位维默认放行"并挂登记。
  本车道未动（src 面 + 跨裁定语义，属总包）。
- **同族第二处（一并登记）**：`src/zephyr/backtest/implementations/event_driven_engine.py:439-441`
  `run_overfitting_detection` 的参数文档仍写"维度2/3 `None` 跳过"，Returns 也少列
  `not_assessed_dimensions`（真源已改口径）。
  ⇒ 本车道顺手核了钱路是否受累：**未受累**——`strict_overfitting_gate` 默认 `False`
  （`vectorized_engine.py:148`），两引擎的 raise 条件读的是 `BacktestResult.overfitting_flag`
  （`engine_base.py:100` 默认 `False`，实测该旗标并不由 `OverfittingDetector.detect` 产出），
  `regime_validation/c1_comparator.py:403-404` 更强制把它关成 False ⇒ 文档陈旧，无实害。
  附带观测（与本单无关，登记待排）：SIM-56"旗标产即必消"目前**没有生产者**（`overfitting_flag` 恒默认值）。

### P-3 ★★ **index 里此刻躺着一份把 R-055b + R-055c 双双退回旧语义的 `overfitting_detector.py` 快照**
- 实测（2026-09-19 00:0x）：
  ```
  git rev-parse HEAD:.../overfitting_detector.py   = 93e15463f7a74f4755b4cfbc1694664154d037aa
  git hash-object  <工作区同名文件>                 = 93e15463f7a74f4755b4cfbc1694664154d037aa   ← 与 HEAD 同
  git rev-parse    :<索引里的同名文件>              = 38a05572fc53f9eb53692d3b8edd8461d9d573a8   ← 唯一异类
  git diff --cached --numstat -- <该文件>           = 12 63
  ```
  staged 差异内容=删掉 `OOS_IS_RATIO_UPPER_BOUND`/`leak_suspected`/`not_assessed_dimensions`
  并把 detect 文档改回"未提供的维度视为未检测(默认稳定)" ⇒ **R-055b 与 R-055c 同时回退**（放松方向，#321 禁）。
- 定性：工作区已是 HEAD 字节、只有 index 是旧版 ⇒ 手册 §4 **B 型**（他会话陈旧快照滞留 index），
  不是有人正在重写该件。但**任何"整 index"式提交都会把它吸进提交面**（本役连坐先例多次）。
- 本车道处置：**只登记不代修**（宪法 §3.4 owner 责任制；`git restore --staged` 别人的在途条目不由我代做）。
  建议总包按 sid 查归属（`.ailocks/registry.json` + `commit_block_events.jsonl` 反查 staged 时点）。
- 与本车道的关系：我的修法对这份回退**免疫**（M1 变异下 `test_f06_e4_wfa_exam.py` 20 件仍绿），
  所以不会因它落地而二次翻红；但 P-1 的路径会随回退一并"退回旧语义"（考试重新可能判通过）。

### P-4 外来在途红现状（前手已登记，本车道按 §3.4 未代修）
- `tests/backtest/test_sim_paper_ledger.py::test_replay_pipeline_consistent`
  两轮 loopcheck 实况见 §3 表；归因证据在 z-rb-stats 自己的册
  （`lanes/rbstats_prescriptions.md` 处方 P-6：按字节 A/B 已证明与 regime 无关）。
  本车道两轮均按"外来在途红、§3.4 不代修"处理。

### P-5 环境/设施类观测（非测试面，登记给维护班）
- 提交侧：`DEPGRAPH-FRESHNESS WARN: depgraph scan 466min since last sync`
  —— 手册 §7 记的是">24h 阻断"，本条已在 7.8h 并向阻断线走；本车道未刷（`--force` 要 2-3 分钟且会改派生面）。
- 提交侧：`RECONCILER-HEALTH WARN: 10 critical in 24h`
  （`SECRET-REGISTRY-DRIFT: required_key_missing[REDIS_HOST/REDIS_PORT/REDIS_PASSWORD]` ×多条 +
  `GATE-WORKTREE-DRIFT-WATCHDOG: 78 件 NAMING_VIOLATION 连续失败 3 次放弃`）⇒ 均为门禁自身在途问题，不属本单。
- 提交堵点提醒：近 24h 371 次，TOP `CREATE-GUARD ×57`。

### P-6 ★★ MSG-STYLE 的"门禁自豁免"是**路径子串**匹配 ⇒ 任何路径含 `commit_gates/` 的文件都免于该门
- 判据体：`src/zephyr/gov_enforcement/commit_gates/msg_style_gate.py`（_check 循环内）
  ```python
  if "commit_gates/" in rel_path.replace("\\", "/"):
      continue  # 门禁文件自豁免
  ```
- 现场（本车道第 1 轮实测，**决定性**）：
  `tests/governance/commit_gates/test_msg_style_gate.py::TestGatewayIntegration::
  test_new_file_with_arrow_violation` / `::test_new_file_with_period_violation`
  - `--basetemp=.runtime/tmp/ff-recon/loopcheck_bt/commit_gates` ⇒ **2 failed / 32 passed**
  - `--basetemp=.runtime/tmp/st-ff-close1-20260918/btm` ⇒ **34 passed**
  同一条命令同一份代码，只差 tmp_path 落在哪个目录 ⇒
  被测的"新增违规文件"路径里含 `commit_gates/` 就被豁免 ⇒ `assert not passed` 红。
- 定性：**两条都是假红，但假的是被测门禁不是测试**——豁免面按子串判，
  意味着任何业务文件只要被放进名为 `commit_gates` 的目录（或临时/工作树路径里带这个串）
  就永久绕过 MSG-STYLE（`→`/中文句号 禁令）。这属 #273 反对的"过宽豁免面"。
- 处方（**收紧方向**，#321 允许，但动门禁源码 → 交总包/该门 owner）：
  自豁免改为**锚定仓库根的相对路径前缀**判定
  （`rel_path.startswith("src/zephyr/gov_enforcement/commit_gates/")`，
  或复用 `commit_gate_registry.is_test_exempt` 那种"路径段"口径），禁 `in` 子串。
- 本车道连带修：`.runtime/tmp/ff-recon/loopcheck.py` 的 basetemp 子目录名
  由"目录名本身"改成 `bt<序号>x<sha1前8位>`（哈希名不可能再撞任何子串豁免），
  并加 `--lane` 命名空间（pytest 起手会删 basetemp，两条车道共用同一根会互删对方 tmp_path）。

### P-7 ★ `test_key_hierarchy` 的"审计不落密钥材料"用**字面量子串黑名单**判 ⇒ 天然随机假红（已确定性复现）
- 判据体：`tests/security/access_control/test_key_hierarchy.py:182`
  `assert "dek" not in str(event.values()).lower() or "wrapped" in str(event.values()).lower()`
- 成因：`src/zephyr/security/access_control/key_hierarchy.py:170/237`
  `key_id = base64.urlsafe_b64encode(os.urandom(12))[:16].lower()` 是**随机串**，
  落在 `event.values()` 里 ⇒ 随机 key_id 含子串 `dek` 的概率 ≈ 14×64⁻³ ≈ 5.3e-5/钥，
  该用例每次跑 2 钥（dispatch+rotate）⇒ ≈1.1e-4/次。**单跑必绿、长跑必偶发红**。
- 确定性复现（非等运气）：探针插件 `.runtime/tmp/st-ff-close1-20260918/plug_dek.py`
  把 `os.urandom(12)` 钉成 `base64.urlsafe_b64decode(b'ADEKAAAAAAAAAAAA')`
  ⇒ key_id 恒为 `adekaaaaaaaaaaaa` ⇒ 该用例**每次红**：
  `PYTHONPATH=.runtime/tmp/st-ff-close1-20260918 python -m pytest
  tests/security/access_control/test_key_hierarchy.py::test_audit_events_for_dispatch_rotate_self_check
  -p plug_dek`（本车道实测 1 failed）。
  同时证明这是**假红**：钉住的那次运行里事件值只有 key_id/域/rotation_days，无任何密钥材料。
- 处方（属 `tests/security/access_control` owner 车道）：断言应查"已知的密钥材料字节
  （`hierarchy._dek_material` 的明文及其 base64/hex 变体）不得出现在事件里"，
  而不是查字面量 `"dek"`；或退一步至少钉住 `key_id` 的取值口径（`_KEY_ID_LEN` 截断后按字符集白名单校验）。
- 本车道未动该文件（非我写域，且改了要重跑 regime/security 全族）。

### P-8 整目录跑时 `test_errcode_consistency_gate::TestRealRepoPass::test_current_repo_is_clean` 会**随别的车道 staged 内容抖动**
- 第 1 轮整目录跑=红；随后单文件跑=11 passed；再整目录跑=绿。
- 机制：该用例观测面=**live git index**（`make_errcode_consistency_gate().check` 读 `git diff --cached`），
  此刻 index 里常年躺着上百项他会话 staged 内容 ⇒ 这条"真仓实证"用例的绿/红**不由本仓 HEAD 决定**。
- 处方（择一，属门禁 owner）：① 该用例改为对 **HEAD 树**实证（不读 index），
  ② 或按宪法 §3.1 改 own-diff 口径 + 外来违规降级为审计（与 `errcode-gate-global-jam-20260916` 治本同方向）。
- 本车道实测旁证：直接跑该门 `_check` 得
  `1 项存量违规（HEAD 基线已在，非本次引入）不阻断: unregistered_code=['ZA-INF-RT-ADM']`，`ok=True`。

### P-9 ★★★ **index 里躺着成批"R-055 系列落地之前的回退快照"，其中一条是对 teeth 测试的净删**（本单最高风险发现）
- 实测（2026-09-19 00:2x，全部 `git show :<path>` 只读比对）：

  | 路径 | index 行数 | HEAD 行数 | index 内 `R-055` 出现次数 | 判读 |
  |---|---|---|---|---|
  | `tests/backtest/test_rb_stats_validator_teeth.py` | **不在 index** | 307 | — | staged=**整件删除**（numstat `0 307`） |
  | `tests/backtest/test_overfitting_detector.py` | 246 | 313 | 0 | staged=**R-055b 之前**的旧版（删 67 行含三条牙齿用例） |
  | `scripts/backtest/f06_e4_wfa_exam.py` | 529 | 643 | 0 | staged=**RB-STATS-01 之前**的旧版（删掉 `n_dims_evaluated` 证据充分性闸） |
  | `src/zephyr/backtest/core/overfitting_detector.py` | blob `38a05572fc` | blob `93e15463f7` | 0 | staged=**R-055b+R-055c 双双回退**（见 P-3） |

  另有 `src/zephyr/backtest/core/decision_gate.py`(36 删) / `test_decision_gate.py`(35 删) /
  `src/zephyr/regime/regime_feature_builder.py`(74 删) /
  `tests/regime/test_cross_sectional_features.py`(87 删) /
  `tests/zephyr/data/test_silent_latch_before_delivery.py`(265 删) 同型（删除列 >20）。
- 危险在哪：**任何"整 index"式提交（含 `git add -A` 习惯、或网关吸收 staged）都会把 R-055/R-055b/R-055c/
  RB-STATS-01 四条已落地加严一次性抹掉**，而且方向是放松（#321 禁）。
  本役此前只按"~150 项外来 staged 内容"记账，**没人在过这批 staged 字节是回退而不是前进**。
- 旁证：`.ailocks/registry.json` 的 `locks` 此刻 **0 条** ⇒ 这 127 项 staged **没有任何在活 owner**。
- 处方（**须总包执行，本车道一律不动 index 里的外来条目**）：
  ① `git diff --cached --numstat` 按删除列排序取候选；
  ② 逐件 `git show :<f>` 与 `git show HEAD:<f>` 比字节，凡"index 版比 HEAD 旧且不含本役裁定字面量"者按 B 型处理
    = `git restore --staged -- <f>`（只动 index，工作区字节不受影响）；
  ③ 净删件（`test_rb_stats_validator_teeth.py`）单独查责任车道后再定。
- 复核命令（车道可直接跑，只读）：
  ```bash
  git diff --cached --numstat | awk '$3 ~ /\.py$/ && $2+0>20 {print $2"\t"$1"\t"$3}' | sort -rn
  git show :tests/backtest/test_overfitting_detector.py | grep -c R-055   # 0 ⇒ 旧快照
  python -c "import json;print(len(json.load(open('.ailocks/registry.json',encoding='utf-8'))['locks']))"
  ```

## 3. 两轮逐目录回归（Owner 硬要求：连续两轮 0 问题）

（结果表由本车道 loopcheck 实跑产出，脚本 `.runtime/tmp/ff-recon/loopcheck.py`，
 原始 jsonl/日志 `.runtime/tmp/st-ff-close1-20260918/round{1,2}.jsonl`，
 已同步冷库 `G:/zephyr_cold/st-ff-close1-20260918/`。）

### 3.0 脚本自证（跑第 1 轮之前的两步，按 R-067 病根）
| 步 | 命令 | 结果 |
|---|---|---|
| ① 已知绿小套件不背锅 | `loopcheck.py --only ai_layer` | rc=0，12 collected / 12 passed，1.14s |
| ①′ tmp_path 重灾区再证 | `loopcheck.py --only d3_metadata` | rc=0，190 collected / 190 passed（`--basetemp` 父目录已先建） |
| ② 整片红的嫌疑人排查 | 第 1 轮无"整片红"；3 条散红逐条单文件复现 | 全部单跑绿 ⇒ 定性见 §4（脚本/环境/随机），非被测面回归 |
| 反证（本车道自犯） | 两次手跑单文件忘 `mkdir -p` basetemp 父目录 | 复现了 R-067 的 `FileNotFoundError` 假故障 |
| | | ⇒ **判据固化**：任何单命令 `pytest --basetemp=X` 前必须先 `mkdir -p X的父目录`；本车道两次踩坑，无一例外是被测面清白。 |

### 3.1 第 1 轮（HEAD=`eb9e18f846` 起算，跑时 HEAD 已推进到 `73ac06b1fe`+，16 个目录）

| 目录 | rc | collected | passed | failed | error | skip+xfail | 耗时(s) |
|---|---|---|---|---|---|---|---|
| `tests/regime` | 0 | 1036 | 1036 | 0 | 0 | 0 | 47.6 |
| `tests/backtest` | 1 | 1833 | 1832 | 1 | 0 | 0 | 283.5 |
| `tests/governance/commit_gates` | 1 | 2584 | 2581 | 3 | 0 | 0 | 78.9 |
| `tests/plan_engine` | 0 | 732 | 732 | 0 | 0 | 0 | 12.7 |
| `tests/ex_core` | 0 | 1304 | 1303 | 0 | 0 | 1 | 25.7 |
| `tests/pf_alloc` | 0 | 401 | 401 | 0 | 0 | 0 | 24.2 |
| `tests/security` | 1 | 177 | 174 | 1 | 0 | 2 | 10.1 |
| `tests/model` | 0 | 883 | 882 | 0 | 0 | 1 | 13.0 |
| `tests/data` | 0 | 566 | 566 | 0 | 0 | 1 | 29.4 |
| `tests/strategy_factory` | 0 | 55 | 55 | 0 | 0 | 0 | 3.9 |
| `tests/ai_layer` | 0 | 12 | 12 | 0 | 0 | 0 | 2.6 |
| `tests/risk` | 0 | 1857 | 1857 | 0 | 0 | 1 | 73.9 |
| `tests/automation` | 0 | 375 | 349 | 0 | 0 | 26 | 72.2 |
| `tests/governance/d3_metadata` | 0 | 190 | 190 | 0 | 0 | 0 | 16.6 |
| `tests/strategy_pipeline` | 0 | 155 | 155 | 0 | 0 | 0 | 20.9 |
| `tests/governance/test_shared_yaml_utils_reexport.py` | 0 | 66 | 48 | 0 | 0 | 18 | 6.0 |
| **合计** | — | **12226** | **12173** | **5** | **0** | **48** | ≈841 |

清单变更（相对总包给的 14 项）：补 `tests/governance/d3_metadata`、`tests/strategy_pipeline`
（本役改过的面，原清单缺）⇒ 共 16 项。

### 3.2 两轮之间改了什么
1. **脚本**（`.runtime/tmp/ff-recon/loopcheck.py`，全部为"消假红/加可读性"，不改被测面）：
   - basetemp 子目录名 `目录名` → `bt<序号>x<sha1前8>`（消 P-6 类假红）＋ `--lane` 命名空间（防并发互删）；
   - 记录 `collected/passed/failed/error/skip` 计数与 `FAILED|ERROR` 清单，整目录 stdout 落 `<out>.<名>.log`；
   - `--only`（自证/复现用）、`--tb=line -rf`、`--timeout` 提到 5400s。
2. **被测面**：无。两轮之间唯一进入仓的改动是本车道第 1 笔（`73ac06b1fe`，测试夹具补灌维度2/3），
   它已在第 1 轮生效（第 1 轮 backtest 只剩 1 条红，即外来件）。
3. **登记**：P-6/P-7/P-8/P-9 四条写进本册（均非本车道写域，未代修）。

### 3.3 第 2 轮（同脚本、同清单、`--lane close1`，起算 HEAD≈`dd6d7ef16f`）

| 目录 | rc | collected | passed | failed | error | skip+xfail | 耗时(s) |
|---|---|---|---|---|---|---|---|
| `tests/regime` | 0 | 1036 | 1036 | 0 | 0 | 0 | 45.3 |
| `tests/backtest` | 1 | 1833 | 1832 | 1 | 0 | 0 | 282.0 |
| `tests/governance/commit_gates` | **0** | 2584 | 2584 | 0 | 0 | 0 | 90.5 |
| `tests/plan_engine` | 0 | 732 | 732 | 0 | 0 | 0 | 14.3 |
| `tests/ex_core` | 0 | 1304 | 1303 | 0 | 0 | 1 | 30.4 |
| `tests/pf_alloc` | 0 | 401 | 401 | 0 | 0 | 0 | 25.2 |
| `tests/security` | **0** | 177 | 175 | 0 | 0 | 2 | 10.7 |
| `tests/model` | 0 | 883 | 882 | 0 | 0 | 1 | 14.2 |
| `tests/data` | 0 | 566 | 566 | 0 | 0 | 1 | 30.2 |
| `tests/strategy_factory` | 0 | 55 | 55 | 0 | 0 | 0 | 7.4 |
| `tests/ai_layer` | 0 | 12 | 12 | 0 | 0 | 0 | 3.6 |
| `tests/risk` | 0 | 1857 | 1857 | 0 | 0 | 1 | 108.3 |
| `tests/automation` | 0 | 375 | 349 | 0 | 0 | 26 | 68.1 |
| `tests/governance/d3_metadata` | 0 | 190 | 190 | 0 | 0 | 0 | 15.9 |
| `tests/strategy_pipeline` | 0 | 155 | 155 | 0 | 0 | 0 | 20.2 |
| `tests/governance/test_shared_yaml_utils_reexport.py` | 0 | 66 | 48 | 0 | 0 | 18 | 7.1 |
| **合计** | — | **12226** | **12177** | **1** | **0** | **48** | ≈773 |

### 3.4 达标判定（按 #325 表述纪律）
- **本车道写域内**：连续两轮 0 问题（`tests/backtest/test_f06_e4_wfa_exam.py` 20 件在两轮各自目录里全通过，
  且被 M2/M3 变异证明"能红"）。
- **全清单口径**：**未达"连续两轮 0 问题"**——两轮都剩同 1 条：
  `tests/backtest/test_sim_paper_ledger.py::test_replay_pipeline_consistent`（外来在途红，任务书明令不代修）。
  如实写：**第 2 轮剩 1 条红**，且该条为前手已定责的外来件；除此之外 15/16 个目录两轮 rc=0。
- 第 1 轮的另外 4 条红全部在第 2 轮消失，逐条定性见下（**不是"自己好了"**：
  2 条由本车道改脚本消除（P-6），1 条定性为并发 index 抖动（P-8），1 条定性为测试自身随机写法（P-7，已确定性复现）。

### 3.5 剩余红与"第 1 轮红"逐条归因
| 用例 | 轮次 | 归因 | 依据 |
|---|---|---|---|
| `test_sim_paper_ledger.py::test_replay_pipeline_consistent` | 1、2 都红 | **外来在途**（z-rb-stats 定责，处方在其册 P-6） | 任务书+台账预告；本车道按 §3.4 不代修 |
| `test_msg_style_gate.py::TestGatewayIntegration::test_new_file_with_arrow_violation` | 1 红 2 绿 | **脚本自伤**（basetemp 目录名撞 MSG-STYLE 子串自豁免） | P-6 的 A/B：同命令换 basetemp 即翻转 |
| 同上 `::test_new_file_with_period_violation` | 1 红 2 绿 | 同上 | 同上 |
| `test_errcode_consistency_gate.py::TestRealRepoPass::test_current_repo_is_clean` | 1 红 2 绿 | **环境/并发**（观测面=live index，当时有别的车道 staged 件） | 单文件跑 11 passed；随后整目录再跑亦绿；门本身报"仅 1 项 HEAD 存量违规不阻断，ok=True" |
| `test_key_hierarchy.py::test_audit_events_for_dispatch_rotate_self_check` | 1 红 2 绿 | **随机假红（测试自身写法）**，非回归 | P-7：`os.urandom` 探针钉死 key_id ⇒ **必红**；未钉时 ≈1.1e-4/次 |

## 4. 未做 + 原因
- **未**把"连续两轮 0 问题"做到全清单口径：剩的 1 条是任务书明令不动的外来在途红。
- **未**代修 P-6/P-7/P-8 三条（门禁源码 / 他道测试文件）：不在本车道写域，且改门禁属"加严/放松需裁定"。
- **未**改 `scripts/backtest/f06_e4_wfa_exam.py`（P-1）：它是"已毕业策略包考试结论"的判定路径，
  数值/档位影响与 A17 同族，须总包或 Owner 定；本车道只出复现证据与三条可选处方。
- **未**动 index 里 P-9 那批回退快照：外来条目 owner 责任制（宪法 §3.4），只出只读取证与复核命令。
- **未**刷 depgraph（P-5）：`--force` 要 2-3 分钟且改派生面，非本单授权。
- **未**做 `config/trading_decision_map.yaml` 任何改动（任务书本单不授权；实测也不需要——
  我改的测试文件不是任何 TDM 节点的 module_ref）。

