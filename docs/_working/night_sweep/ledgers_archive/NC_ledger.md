---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# NC_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# NC C组考试链前置打通车道 · 台账（st-nightsweep2-nc-20260930）
# 总筹=st-nightsweep-chief-20260929 · 避让图=00_orchestration.md §二（零违碰：lane-p 引擎/gpu_core 未触碰）
# 授权链=Owner 2026-09-30 "打通 C 组前置"（声明通道；冻结判据零改值；ruling 写入=本夜授权面）
session: st-nightsweep2-nc-20260930
date: '2026-09-30'
items:
  - id: C3
    card: ⚑-2② B案落册·最大前置
    verdict: DONE-LANED
    evidence:
      - 声明件 docs/_working/night_sweep/c_exam/flag2_declaration_b.md（换尺不降标三证/新旧判据对照/功效 n≈82 vs NIST 97 vs 180-194 引用）
      - config/exam_scale_cost_gate.yaml 追加 breakeven_cost_gate v2.0.0（旧四块逐键零改值自证 OK，survival_floor=0 禁改照旧）
      - 裁定#435（ruling_registry 在册）+ #ARCH-368 载体（PROTECTED-PATHS 正门标记，#ARCH-367 先例同款）
      - 落地 commit=887c662d（C3 补投）+裁定#435 随 5f7510ef 先期在 HEAD
      - 披露：首登遭 07:4x 队列落盘崩溃回滚波及一次（声明件+gate v2 块+token 被清），已同内容重建重投
  - id: C2
    card: T1 定稿追认登记
    verdict: DONE-LANED
    evidence:
      - 裁定#446（原登#436撞号改号核订，#419→#420 先例；撞号对方=st-nightclean 的 W12 翻面条目）
      - summary.json finalization 标注 FINALIZED_BY_OWNER_REF（3698+2 配方内生阴性，对拍三证净值哈希 342432347427）
      - 首投 commit=5f7510ef；改号后随 8223ba84bd 落地
  - id: C4
    card: 哨兵重跑→T2 发车
    verdict: ADVANCED
    state: 哨兵修复落地+真重放跑通 6/7 判据绿+垃圾线零命中；唯一 RED=cost_gate_spot（30/50 旧抽样判据结构性不可过）→ T2 不发车（禁硬闯）
    evidence:
      - 集成断点修复：gpup1 cf16fa43fd _load_engine 升 9 元组、哨兵调用方漏改致重放腿 ValueError——补解包零判据变更，7 测绿，commit=2befc2cb
      - 真重放 verdict（grid_20260926-024947/handover_verdict.yaml）：manifest_points/dead_zero/degraded/negatives/n_eff/dsr 全绿，cost_gate_spot 20/50 ok（bad=30 全在 40bp 档<survival_floor(0)）
      - RED 归因：旧抽样口径=Owner 已裁 B 案替换对象（裁定#435）；哨兵消费面接线 B 案=另波；prereg_hash_drift=基线重建语义（W-173 4970433e97 合法变更）非篡改
      - next: B 案判定面接线（哨兵/判定书消费 breakeven_cost_gate v2 键）后哨兵可转绿发车
  - id: C5
    card: 上岗规则 v1 保守激活
    verdict: DONE-LANED
    evidence:
      - 填充方案件 state_matrix_fill_plan_v1.md（T1 Top-12 全长仓轮动=无防御 sleeve 结构性事实）
      - TDM euphoria/distribution 两格 mounted_reason 追加 C5 禁用标记（R41 首词合法，mounted 零自填零删除），DECISION-MAP gate 同批过
      - dry-run 核证：r 态折算机证 euphoria/distribution 不可达；fw-tdm-current activation 实测（euphoria 仅 daban-sleeve/distribution 空）；条件共振 R2 判据=保持现状机械面可运行
      - Owner 格/上岗规则生效裁定（P5）/IBT-D01（P3）=非我能施工面，如实挂等待
      - 落地 commit=f8d56a09；stale claim st-chief7w-20260927（pid=0）按宪法 §2.7 精准释放留痕
  - id: C7
    card: 成本口径对账尺
    verdict: DONE-LANED
    evidence:
      - scripts/backtest/cost_accounting_ruler.py（MOD-BT-COST-RULER）：六判据 R1 佣金五处同值/R2 实盘印花三处万5/R3 考尺档在册/R4 C345 差异锁值/R5 vectorized 单一真源/R6 规模维缺席红证固化——ALL_PASS（红证固化语义）
      - 四件实测底座：佣金 0.0000854 恰 5 处字面量（matching_logic/optimizer/t0_cost_model/simulation_broker/pnl_calculator）；考尺 STAMP_BP=10.0 vs 实盘侧 0.0005；_net_line 无规模参数；tiers_bp vs 标定分层双真源
      - 10 测绿 + token + 翻译词条 + depgraph 节点在册；落地 commit=9a3c8bb1
      - 数值整改=⚑-2 生效后另波（本尺只量不改）
  - id: C8
    card: W-178 真源落地
    verdict: DONE-LANED
    evidence:
      - 真源声明 w178_truth_source_declaration.md（FROZEN_BY_OWNER_REF：选股=sector_constituent 595/概念 375 辅助展示/读法铁律/映射表立项 board_pair_mapping 股票级对齐+去重律）
      - known 差异清单 K1-K6（134 板有行情无成分/成分表滞后/PIT 深度 6 日/两族股票池规模差/96 板无名/概念独有 1）
      - strict 案卷 §E 翻面注记（数值零改动）；裁定#447（原登#437撞号改号）+裁定#431⑥ 同向互补
      - 落地 commit=8223ba84bd；与 #431⑥ 数字 reconciled：#431⑥=行业族定向（729 行情面），本声明=真源表定向（595 成分面）
  - id: C9
    card: 三小件
    verdict: DONE-LANED
    evidence:
      - 时帽 12h 追认（仅约束调度层，src/scripts 零消费点现状如实，暂不装牙齿）
      - 补-1 OWNER-GATE：不翻旗（实盘桥=资金门位+判别器波3前置+93册推荐乙）；落点留痕=qmt_file_bridge_broker.py:605 UNKNOWN 分支+tradability_preflight.py:191，Owner 裁甲后一次改动即可
      - 补-2 排期登记：等 Owner 一句话（牵 freeze_manifest 38 条），排波 3 后窗，未批不动契约
      - 裁定#438 打包登记，随 8223ba84bd 落地
  - id: C6
    card: 波12 前置推进
    verdict: ADVANCED
    state: 五条件逐条实测报告落册；c4 全解（#435）/c2 上游解（#447）/c3 证据在册；c1 词表脱节未满足（tasks 表 verified 零命中=2597/2597 非我能施工面）；点火维持 WAITING 另呈批线
    evidence:
      - 报告件 wave12_five_conditions_status.md（c1 tasks 表实测分布/c2 880 判据 vs 现值 729/595 对账素材/c3 4970433e97/c4 #435/c5 f6e288fc54）
      - 队列 q-0010 在队消化
incidents:
  - 撞号：裁定#436/#437 与 st-nightclean 并发撞号（我读册快照早于其落地）→ 改号核订 #446/#447（#419→#420 先例），全部引用同步（summary.json/w178 两件/wave12 报告/ARCH-368 related_rulings）
  - 队列环境故障窗：07:11 起 landing 子进程 9 会话 14+ 袋同因死亡（WinError 233+三向合并同键异容）——我方 8 袋死（q-0001~0008），改号解合并死因+队列复活后 q-0009 重投成功（8223ba84bd）；直提正门在窗内经 st-c9-final 实证后我方用于 A-D 批
  - 崩溃回滚波及：首登面（声明件/gate v2/哨兵修复/2 token/1 词条）遭工作树回滚，全部同内容重建重投
  - 并发覆写：#ARCH-368 议题条目首登遭冲（813→811），重登+披露在条目内
discipline_checks:
  - 预注册冻结判据零改值：exam_scale_cost_gate 旧键+search_space_prereg+survival_floor 逐键自证不变
  - 避让图零违碰：lane-p/d/gpu/lane 文件零触碰（哨兵修复=本车道工具 t1_t2_handover.py）
  - 实盘四禁：零实盘动作；补-1 不翻旗（Owner 门位）
  - safe_write_text CAS 用于全部热册写入；每批 commit 后 git log 核归属
```
