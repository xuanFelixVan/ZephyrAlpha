---
campaign: matrix-20261007
lane: st-mx07-RD（红队车道）
status: done（18 车道成果对抗审计完毕；P0=0，P1=1，P2=4，P3=6；只攻不修零代码改动）
ttl: task_bound
created: 2026-10-08
authorization: 总包 st-mx07-chief 红队派单｜审计基线=git 38a92658ae..HEAD（120 commits）
note: 本件为审计留档非施工件；creation_token 登记随 chief token 袋（同 W4 先例）。所有行号/哈希为审计时点（HEAD=a7d9f91950）快照。
---

# red_team_findings_v1 — 矩阵战役 2026-10-07 夜战红队审计报告（st-mx07-RD）

> 攻击面：①对拍造假（L5/L3/L4/W1）②门禁绕过 ③PIT 泄漏（L8/W3/L2/W2/L11）④并发冲突。
> 纪律：只攻不修——本报告零生产/测试代码改动；复跑仅写 `.runtime/tmp/mx07_redteam/`。

## 0. 一页结论

- **状态：FINDINGS 11 项（P0=0 / P1=1 / P2=4 / P3=6）**。
- 最高危：**P1-1 W3 主批物理删除 15 条 TREND/MOM 注册册条目，其中 5 条考试 verdict=pass**——无裁定授权、无 retired 墓碑、"零丢失"宣称与册面事实相悖。
- 对拍四件（L5/L3/L4/W1）**未发现造假**：容差/注入缝/守恒断言/披露口径全部属实，L5 复跑 438/438 复现。
- PIT 五件（L8/W3/L2/W2/L11）**未发现前视**：freeze 时间链自洽、参照窗=卡明文授权、SMA200 同日特征合规、滤波因果、进池阈值=裁定冻结常量。
- 门禁面：无伪造 GW 标记、无 src→tests 反向依赖、新 .py 零禁用模式、抽查 token 全在册。

## 1. P1 发现（1 项）

### P1-1【面4 归属+净零】W3 主批 4faf0517e8 物理删除 15 条 TREND/MOM 注册册条目，其中 5 条 verdict=pass，无裁定授权、无墓碑

- **攻击面**：面 4 并发冲突（误删他班成果）+ 宪法 §4 净零内收判据。
- **位置**：`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml`（该 commit 内 -510/+28 行；窗口内唯一触碰该册的提交）。
- **证据原文**：
  - 条目计数：base 38a92658ae=143 条 `- indicator_id:` → 4faf0517e8 后=128 → HEAD=128（`git show <rev>:<册> | grep -c "^- indicator_id:"`）。
  - 真删清单（base∪HEAD 集合差，15 条）：`IND-MOM-013`、`IND-MOM-028`、`IND-TREND-003/004/018/020/022/023/024/026/028/029/030/031/032`。
  - 考试 verdict（`docs/_working/fexam/indicator_exam_scores_v1.yaml`）：**IND-MOM-013 `verdict: pass`（|ic_5d|=0.0234>=线0.02）**、IND-MOM-028=pass、IND-TREND-022/031/032=pass（共 5 pass）；其余 10 条=rework。0 条=retire。
  - 裁定授权缺失：`ruling_registry.yaml:4283-4289` 裁定#489① 范围=6 件 retired（MOM-032/036、REV-003、VOL-016、VOLUME-015、TREND-036，**以 status:retired 墓碑落地**）+CYC 4 件留观改考——15 条 TREND/MOM 删除不在其列；未检索到任何覆盖该批"物理净删"的裁定。
  - 机制不一致：同窗 6 件退役用"status: retired+evidence 注释"墓碑（册 :1184 等 6 处在案），此 15 条被整条删除、册内零痕迹。
- **影响**：5 条判活（pass）指标从永久注册册无声消失，重建防护（check_file_canonical/防重建语义）失效；"他会话在途退役治理批"的真实处置意图不可考；若该批原计划是"带墓碑退役"（同 6 件机制），则 W3 携带落地=误删他班未落地成果的墓碑形态。
- **披露现状（缓解）**：commit body 与 `DISPATCH_BLOCKERS.md:27` 均有 `[allow-mass-deletion]` 旗+归属披露（"他会话在途退役治理批……如实携带零丢失"）；git 历史可恢复。
- **"零丢失"宣称证伪点**：注册册（permanent 域）层面 15 条零痕迹；考试证据 `docs/_working/fexam/indicator_exam_scores_v1.yaml` 位于临时区（task_bound TTL），permanent 域证据链断裂。
- **处方建议（不修，呈 Owner）**：①核定该批删除的授权链（哪条裁定/哪条车道批令）；②若属误删，按 `git show 38a92658ae:<册>` 恢复 15 条并按裁定#489 同款补 status/evidence 墓碑；③更正 W3 消息与 blockers 中"零丢失"表述。

## 2. P2 发现（4 项）

### P2-1【面4】bootstrap 三件套：index 删除态+工作区未跟踪副本并存（blockers 已登记，危害面=仅误提交）

- **位置**：index 内 `D src/zephyr/backtest/accel/bootstrap_kernel.py`、`D tests/backtest/test_bootstrap_kernel_wiring.py`、`D src/zephyr/backtest/accel/__init__.py`、`D docs/03_modules/_domain_backtest/algo_flow/{accel__init__,bootstrap_kernel}.yaml`；工作区同路径 `??` 未跟踪。
- **证据**：`git cat-file -e HEAD:src/zephyr/backtest/accel/bootstrap_kernel.py` 通过（HEAD 完好，393 行）；工作区副本与 HEAD **逐字节一致**（`git show HEAD:… | diff - <worktree>` 双件 IDENTICAL）。
- **影响**：现 index 若被整体 commit，将从 HEAD 删除核真源+wiring 测试共 666 行，而 `e2_stationary_bootstrap`/`correlation_block_bootstrap`/wiring 测试的 import 面断裂（新 clone/CI 即红）。危害=仅潜在误提交，非现行损坏。
- **处方建议**：总包收口时显式 `git reset` 该五路径或先恢复 index 一致再走 git_commit.py；禁裸 `git commit -a`。

### P2-2【面2 纪律】"x" 垃圾提交消息落治理文档

- **位置**：commit `78d22f15589`（2026-10-08 05:40），subject 仅 `x`。
- **证据**：`git log -1 --pretty=format:%B 78d22f15589` → 正文仅 "x"+网关尾注；触碰 `docs/.../commit_guide_sources/landing_journey_registry.yaml` + `commit_navigation_playbook.md` 两治理件。
- **影响**：非绕门（有 `[GW:st-entrance-gate-20261007:q-…-0024]` 正规尾注），但提交消息纪律违反——治理件变更意图不可审计。
- **处方建议**：补 amend 或留痕说明；后续网关对 subject 长度/词盲区加软门。

### P2-3【面1 L5】"全列对拍 438/438" 的实际独立验证面仅物化层+7 指标族（已披露但读数易误读）

- **位置**：`src/zephyr/factor/technical_indicators/panelized_indicators.py:305-316`——vec 路径对未列入 `_SHADOW_COMPUTE`（:242-248，仅 cci/aroon/aroonosc/connorsrsi/rvgi 5 个）的指标**原样调用生产类 compute**；另有 trend._wma/_linreg_endpoint 经 `_PatchedHelpers` 换向量实现。
- **证据**：`compute_indicator_matrix` docstring 自述"递推族……原样复用生产 compute"；即 ~135 个指标两路径同代码，对拍恒真。
- **影响**：非造假（docstring/INVARIANTS 披露在案，且真收益=物化层 51.7-64.6x 已独立验证）；但"438/438 列 |Δ|≤1e-9 全等"作为验收读数传播时，易被误读为"全指标向量化等价已证"。实际独立等价验证面=物化层+5 shadow 指标+WMA/HMA/INERTIA 三列。
- **处方建议**：留档册 rowvec_promotion_v1.md 验收段加一行"恒真列占比"披露；后续指标逐个改向量化时逐个补真对拍。

### P2-4【面3 W3】解盲前 freeze 证据本体落 24h TTL staging，未归档 permanent 域

- **位置**：`.runtime/sessions/st-mx07-W3/staging/cond_exam_freeze_v1.json`（mtime 10-08 13:32；`cond_exam_freeze_ref_v1.json` 同）。
- **证据**：freeze JSON 含 N_fam=11/K_eff={3,4,2,2}/stratum_day_counts（236/层）；产出 `docs/_working/fexam/indicator_conditional_exam_scores_v1.yaml:10` 仅记 `family_size: 11`。时间链自洽：预注册卡 commit dfcc8ec9 12:58 → 数据缓存 pkl 13:31（`load_data` 原始面板缓存，非 IC）→ freeze 13:32 → 产出 13:33（`generated_at_utc: '2026-10-08 05:33:…+00:00'`）。
- **影响**：`.runtime/sessions/<sid>/staging/` 24h TTL 回收后，"解盲前冻结"的物理证据只剩留档册转述（cyc_conditional_exam_v1.md:12）与产出 yaml 的 family_size 字段；卡片 §5.2"写入产出文件"的字面要求部分达成（族大小在、层计数不在）。
- **处方建议**：fexam 类考场的 freeze JSON 按 L10 卡先例 promote 进 `docs/_working/fexam/`（或考试产出 yaml 内嵌全字段），TTL 前抢救。

## 3. P3 发现（6 项）

1. **【面1 L5 单测】容差口径内不一致**：`tests/zephyr/factor/technical_indicators/test_panelized_indicators.py:54` 用 `atol=1e-7`（linreg_endpoint 闭式参照），与文件头 `:3`"对拍口径与 parity_check 一致：数值 |Δ|≤1e-9"矛盾。参照为独立数学形式，1e-7 有合理性但与自述口径不符；真机对拍 harness 仍为 1e-9 兜底。另 `:108` `_build_row_reference` 为生产 `_build_row` 的手工复制（非 import 真源），当前逐字一致、存在漂移风险。
2. **【面1 W1】qty 公式理论 1ulp 缝未入语义缝披露**：legacy `t0_material_line.py:162` `int(notional/buy_fill//100)*100`（Python float `//`=fmod 法）vs fast `t0_material_line_fast.py:413-414` `np.floor(notional/buy_fill/100.0)*100`——两者在除法近整数边界可差 1 ulp（一手 100 股）。实测对拍全绿未触发；披露段（parity harness :191-204）只覆盖 Decimal 扫描比较缝，未覆盖此缝。
3. **【面3 L2】`sma_regime_fallback` 的 `.bfill()`**（`scripts/backtest/fexam/ch_data.py:210`）：代理序列前 200 日（1990-91 预热期）体制态由未来首有效值回填。考试窗 2005+ 不受影响，纯理论前视；建议改显式 NaN 起点或注释声明。
4. **【面4】capability 册热文件审计期间被并发重写**：审计中段（≈16:10）worktree 册面 sector-surface 等 mx07 token 一度不可见，16:12 册被他会话重写后 token 集恢复；当前 worktree vs HEAD token 集合差=1（`tail3-workbook-00-workbook-20261007` 缺，属 tail3 会话在途面）。留观察，勿代修（owner 责任制）。
5. **【面2】W6 `a7d9f91950` 的 `[allow-mass-deletion:capability 册净删=PG-wins…洗净未入账手插条目]` 与 diff 不符**：该 commit 对 capability 册 diff=+7/-0（0 条 token 删除）——删除发生在 ledger/worktree 面（相对 HEAD 无净删），旗声明超范围，稀释 allow-mass-deletion 旗语义。细读"账本真源无删"可自洽，但旗+短语"净删"易误读。
6. **【面3 L8】`emotion_linkage_exam.py:375` 判定分支 dead code**：`report["pit_verdict"]` 只能取 `conditional_clean`/`dirty`（:370），`elif passed and pit_verdict=="clean"` 的"合格"分支不可达（永远落入"有条件合格"）。方向保守无害，建议清理。

## 4. CLEAN 面（攻击未破，存证）

- **面1 对拍四件**：
  - L5 `parity_check.py`：TOL=1e-9 属实（:61），逐列无跳过/无提前退出（compare_rows :116-170）；同输入注入缝=同一 `sym_data` 对象喂两路径（:220-221），生产链不原地变异（`_compute_all_indicators` 返回新 merged，provider :2057）；windowvec 激活+还原双向断言（:206-208）。**复跑实证：2 标的×250 根 → 438/438 PASS，物化段 51.7x/64.6x**（`.runtime/tmp/mx07_redteam/l5_rerun/parity_table.tsv`）。
  - L3 `tests/backtest/test_bootstrap_kernel_wiring.py`：同索引注入+`seam.calls==1` 守恒断言（:127-129）+TOL=1e-9（:28）；WRC 镜像 `_ref_wrc_boot`（:36-43）与迁移前真源 `dd98757ab4^:src/zephyr/backtest/core/walk_forward.py:274-280` 逐式一致（ddof=1/零方差置 0/均值÷(s_std/√n) 全同）；scripts 侧 re-export 为薄门面单真源（`scripts/backtest/fexam/bootstrap_gpu/kernel.py:27` import 自 src 核），无双真源漂移。
  - L4 `layered_backtest.py`：纯 pandas 后备可达（`use_kernel=False` 显式参 :95-104）；`parity_end_to_end` 参照侧显式走后备防核对核自比（:295 注释）；qcut 复刻（layer_lookup :125-157）+Kahan 均值（:160-175）逐位实证留档。
  - W1 `t0_material_line_parity.py`：0 FAIL 口径=规范化输入逐位==（INVARIANTS :9 明文），raw Decimal ±1ulp 缝由披露段如实计数（:191-204，+5 对=0.044% 留档 §3/§4）；numba 核 `t0_material_line_fast.py:185-248` 运算序与 legacy `run_model_m0`（t0_material_line.py:120-170）逐式一致（one_bar→low_bars→zero_price→触档扫描→收盘强平）。**披露诚实性：成立**（"按字面满足"的自我定位+双窗读数全数留档）。
- **面2 门禁**：120 提交扫描无外来 `[GW:<他session>]` 标记（全部=本会话 id，与 FORGED-GW-MARKER 门/`forged_gw_marker_gate.py:193` 语义相符）；`src/scripts → tests` 零反向 import；今晚新 .py 十件扫 `datetime.now()/time.time()/utcnow/裸 subprocess/裸 duckdb.connect` 零命中；表名全部走 TableRegistry。token 在册核验：wq_alpha_87 三件（册 :58677/:42945/:9506）、sector 双件（sector-surface-20261008/sector-wiring-doc-…，HEAD 与 worktree 均在）、L8 两件（:51172/:52440）、L11 paper_pool_gate（:64209）、cyc prereg 卡（:42335）——全绿。
- **面3 PIT**：L8 `fwd5_off=close.shift(-5)/close.shift(-1)-1`（t+1 起 5 日，:121）+信号 ts=15:10 收盘后+PIT a/b/c 实测+快照器 append-only（同名拒写 :134/manifest 只追加 :161/pit 读径 created≤asof :179-191）。W3 相位分层只用 t 日 CYC 值（卡 §2 无前视论证与实现一致）、HAC 恰按卡调用（:193）、`r5=close.shift(-5)/close-1`（:430）标准前瞻标签；参照窗=卡 §7 明文授权 report-only（freeze_ref 244 日/层在案），非二次窗口违规。L2 SMA200=rolling(200) 含当日同日特征（:208-209），无 shift 缺失。W2 前向滤波 t 只用 ≤t 观测、一次窗口叙事自洽（hmm_v3_exam_v1.md §5:65-72）。L11 阈值=裁定#489③ 冻结常量（paper_pool_gate.py:59-63），DSR 数学全委托 SSOT（deflated_sharpe_calculator），fail-closed 退化态不放大行。
- **面4 其余**：10 条 retired（6+4）evidence 指向核验：CYC 4 条→`indicator_conditional_exam_scores_v1.yaml`+`cyc_conditional_prereg_v1.md@dfcc8ec9` 均真实存在；10-07 六条→裁定#489（ruling_registry:4275 在册）+`indicator_exam_scores_v1.yaml` 存在。W5 提交归属披露（278f283636c）与文件清单一致。

## 5. 审计方法与限制

- 基线：`git log 38a92658ae..HEAD`（120 commits，全量 subject 扫描+重点 commit 全 body/ diff 级核验）。
- 复跑：L5 parity（后台实跑，CH 只读，产物 `.runtime/tmp/mx07_redteam/l5_rerun/`）；W1/W3 数值复跑未做（CH 全窗成本高，以代码级逐式比对+留档读数交叉代替——W1 全窗 v2 读数 `.runtime/tmp/st_mx07_w1/` 可后续抽查）。
- 限制：capability 册为热文件，工作区态随时被他会话重写（P3-4 即审计中实测一次）；P1-1 的"他会话在途批"原意图无法从仓内证据完全复原，已按"注册册事实+verdict 事实+裁定范围"三重机械证据固定。
