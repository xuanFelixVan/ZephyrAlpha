---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# W2T2_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# W2-T2 考试链收口车道台账（sid=st-nightsweep2-t2-20260930，总筹=st-nightsweep-chief-20260929）
session: st-nightsweep2-t2-20260930
created: '2026-09-30'
chief: st-nightsweep-chief-20260929
authorization_chain:
  - Owner 2026-09-30 夜令："C组……把他们前置条件全部打通，然后来完成他们"
  - 裁定#435（B案判据声明通道落册，机读键追加同 commit 原子）
  - 裁定#446（T1 成绩单定稿追认：3698 有效+2 可审计阴性守恒）
  - 声明件 docs/_working/night_sweep/c_exam/flag2_declaration_b.md（W-173 式声明通道）

cards:
  - id: W2T2-C1-mining
    verdict: DONE
    evidence: >
      挖矿结论：C3 已落 yaml breakeven_cost_gate v2 块+声明件，缺=active 指针+消费代码。
      判据真源=案卷 review_ext_data_and_backtest.md §3.2（P1-P5/三态/幸存者域）。
      c* 求解面发现：引擎 _net_line 线性成本线（net(c)=gross-turnover*(15+2c)/1e4，
      COMM=2.5/STAMP=10/SLIPPAGE_BP=5）⇒ Sharpe(c)=0 ⟺ mean(net(c))=0 ⟹ 闭式解
      c*=ref+mean_net*1e4/(2*avg_turnover)，与年化口径四条强制（√244/ddof/Lo/停牌剔）
      无关=普查免重放（net_returns.parquet 3698 格逐日序列+manifest avg_turnover）。

  - id: W2T2-C2-yaml-pointer
    verdict: DONE-LANDED(fb892e86)
    evidence: >
      config/exam_scale_cost_gate.yaml 文件尾追加 cost_gate_active 块
      （active_version='2.0.0'/fallback='1'/launch_gate_scope=[p1,p2]）；
      git diff 删行数=0（v1/v2 既有键零删改自证）；safe_write_text CAS 写入。

  - id: W2T2-C3-gate-code
    verdict: DONE-LANDED(fb892e86)
    evidence: >
      exam_cost_gate.py 追加五道门机器面：BreakevenGateConfig（40bp 锚/层 n>=30/
      bisect tol 0.1，__post_init__ 校验）/BreakevenGateVerdict（三态+分位数+K/N+池）/
      breakeven_cost_star_from_net_line（闭式解，钳零/越界/退化分池）/
      solve_breakeven_cost_star（案卷 §3.2 二伪代码逐行）+monotonic_grid_violations/
      evaluate_breakeven_cost_gate（P1 幸存者中位/P2 定义分布 P10（钳零并入=Sharpe>=0
      语义锚）/P3 层键缺席或层 n<30=INDETERM/P4 规模重放缺席=INDETERM（线性恒零读数
      禁充测量=反橡皮图章）/P5 四字段缺=INDETERM；FAIL 枚举=P1-P4，案卷五原文）。
      v1 三门判定原样保留=回退面。

  - id: W2T2-C4-sentinel-wiring
    verdict: DONE-LANDED(fb892e86)
    evidence: >
      t1_t2_handover.py：load_cost_gate_params 读 cost_gate_active（指针缺席/非 2.x=
      回退 v1 逐键零漂移，9 件既有 v1 测试全绿实证）；新增 _criterion_cost_gate_breakeven：
      全量普查（3698 序列出生证逐格校验 |Δ|<=6e-4 全过；尾行=裁定#446 阴性 2 格守恒）；
      判据键 cost_gate_spot 机读面稳定；v1 并列读数（重放缓存零重放重算）随 verdict 留证。

  - id: W2T2-C5-tests
    verdict: DONE
    evidence: >
      45/45 绿=exam_cost_gate 32（闭式解≡二分解/分池/五门双向/三态聚合/配置校验）
      + handover 13（v1 回退零漂移 9+v2 双向 GREEN_DRYRUN/VERDICT_RED+出生证篡改
      fail-closed+阴性尾行映射）。ruff check+format 双连全过（4 文件）。

  - id: W2T2-C6-prereg-pointer
    verdict: ADVANCED(decision=not-touched)
    evidence: >
      search_space_prereg.yaml 无版本指针位；且哨兵 prereg_hash_drift 垃圾线=
      跑中改 prereg 即作废重开（冻结语义），今晚发车自爆；active 指针唯一真源=
      exam_scale_cost_gate.yaml#cost_gate_active（哨兵实际消费面），另加指针=双头真源。
      条件性步骤按"若无则不加"纪律跳过。

  - id: W2T2-C7-sentinel-rerun
    verdict: DONE(7/7 GREEN_DRYRUN)
    evidence: >
      哨兵 v2 面重跑 grid_20260926-024947：all_green=True blocking=[] garbage=[]。
      七项：manifest_points=3700✓ dead_zero=0/0/0✓ degraded=0✓ negatives=3700 守恒✓
      n_eff=19✓ cost_gate_spot(v2)✓ dsr=deferred✓。

  - id: W2T2-C8-v1v2-parallel
    verdict: DONE
    evidence: >
      同一 T1 数据并列读数（verdict criteria.cost_gate_spot.measured.v1_parallel 留证）：
      v1 旧尺（抽 50 格五档全存活）=RED ok20/bad30（(1-p)^50 恒假结构）；
      v2 尺：N=3700，幸存者 K=2204（K/N=59.57%），幸存者有效 c* 中位=53.08bp>=40
      P1 PASS；定义分布（含 1276 钳零）P10=0bp>=0 P2 PASS；越界池 218（>200bp 单列）；
      退化池 0。换尺非掩过：K/N 与全量分位数随 verdict 强制披露。

  - id: W2T2-C9-t2-launch
    verdict: ADVANCED(E0 gate deferred→loop armed)
    evidence: >
      首发被 E0 问闸拒：gate_deny_trading_hours（交易日 09:00-15:30=light_only，
      禁硬闯=宪法级）。subspace 已落盘（t2_subspace.json expected_points=24，cap=900
      不绑定，S1-S4 冻结算法确定性产出，非本车道改域）。已挂后台发车循环
      （.runtime/logs/w2t2_launch_loop.log，每 600s 重试，哨兵幂等+claim 防双发，
      15:30 闸开即 LAUNCHED 自停）。

  - id: W2T2-C10-preexisting-issue
    verdict: REGISTERED(不代修)
    evidence: >
      E0 链 subprocess reader 线程 UnicodeDecodeError（utf-8 解码 GBK 字节 0xbb，
      compute_window_gate→batch_window_preflight 链内既有面，非本车道改动；
      门判定不受影响=时间窗决策）。留痕供维护班清账。

launch_status:
  first_attempt: 'DEFERRED:E0_gate(gate_deny_trading_hours)'
  loop: .runtime/logs/w2t2_launch_loop.log
  expected_run_dir: data/strategy_intake/grid_t2_<ts>（执行器落盘）
  monitor: 每 20 分钟看 manifest 行数增长
```
