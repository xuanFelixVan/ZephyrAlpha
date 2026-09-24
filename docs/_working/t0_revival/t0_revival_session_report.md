---
ttl: task_bound
rule_form: data
verifiability: manual
title: 做T复活轴+词表立法班 端到端交付报告（st-t0-revival-20260922，三分包全终态）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-22
session: st-t0-revival-20260922
---

# 做T 复活轴+词表立法班 · 交付报告（三分包全落地）

> 依据：通宵执行令（sid=st-t0-revival-20260922）+ 裁定#399 二（做T复活改裁）+ #398 五（词表三批点）+ #398 四（R4 卡）。
> 施工形态：纯文档+判据脚本批（降级申请→主区被热册蒸发逼停后**切 session worktree 施工**，宪法 RULE-WORKTREE 正门）；commit 走 GitCommitGateway（直连+队列混合，死信 2 条处置见 §4）。

## 1. 三清单

### ① 裁定清单（本班消费/登记的裁定）

| 裁定 | 用法 |
|---|---|
| #399 二 | 本班总授权：R4 由"只登记不重建"改"重建判据+条件化做T复活轴施工"（分包1/2 执行依据） |
| #398 五① | 词表立法第一步（分包3 执行依据）；五②（4态收敛）与五③（五态映射挂起）本班不动 |
| #331/#386 | 边界口径：砍旧形态/禁复试图救——本班全部产物零状态变更，未触碰 |
| #398 四-R4 | 原裁定（被 #399 二改裁），R4 卡 A 选项文本=分包1 施工蓝本 |
| 裁定册登记 | #398/#399 原为他会话 staged 未落地批文，本班按 RULE-RULING 同 commit 原子随批落地（worktree 内） |

### ② 执行清单（产物→commit）

| 分包 | 产物 | 状态 |
|---|---|---|
| 1 cost_trio 判据重建 | scripts/audit/cost_trio_exam.py（判据住 scripts，目录契约 DCR-005 合规）+ docs/_working/kimi_audit/lane_reports/{cost_trio_reexam_report.md, cost_trio_result.yaml, cost_trio_pairs.csv} | commit=分包1 批（见 §3 hash 表） |
| 2 条件化做T 复活轴 | docs/_working/t0_revival/t0_conditional_prereg_card.md（frozen）+ scripts/audit/t0_conditional_e4_exam.py + t0_conditional_e4_verdict.md + t0_conditional_e4_result.yaml | commit=分包2 批 |
| 3 词表立法第一步 | docs/_working/vocab_legislation/01_official_state_vocabulary.md + 02_state_vocabulary_mapping_register.md + construction_workflow_policy.md Step5 出厂纪律一条 | commit=ab89a56b |
| 登记面 | creation_token 9 条（cost_trio_exam/t0_conditional/state_vocab_leg 三 capability 组）+ 翻译册 2 条（两判据脚本） | 随分包 commit |

**分包1 核心结果**：判据重建后与 P6/biz2 快照**五值逐位一致**（24 对/0 净正/0≥30bp/毛 −9.2bp/毛 p50 −5.13bp）——配对规则重建成功的强证据；净价差口径差（−40.4 vs 旧 −45.0）=min5 抬升是否折入硬成本，已对账披露；verdict=**INSUFFICIENT_SAMPLES**（土规）。
**分包2 核心结果**：T0-CONDITIONAL 卡 frozen（状态门=宏观 vol_pct>0.700 或 r3/r12 的 T-1 PIT + 情绪门 TDM 六段 ignition/expansion/euphoria；判据复用 cost_trio；五态 fail-closed）；E4 首轮 verdict=**INSUFFICIENT_SAMPLES**（宏观门命中 8<30；情绪门六段无持久化历史=unevaluable，禁 fear_greed 异轴顶替；诚实观察=门内毛 −5.5bp 优于对照 −11.05bp，方向同 H1 但样本无意义）。
**分包3 核心结果**：四轴官方词表+命名空间立法；实测 34 套存量逐套映射登记（数量对账 34vs28 差异如实披露=C2 归类边界+W1 官方模块普查后新建）；C1/C2/C11/方向陷阱四类重点消解裁定落册；出厂纪律挂 Step5 验收清单。

### ③ 复查清单（复核命令，Owner 可独立重放）

```bash
# 分包1：判据基线复现（只读材料，产物仅 docs 区）
python scripts/audit/cost_trio_exam.py
# 预期：n_symbol_day_pairs=24 / 0 净正 / 0≥30bp / 毛 −9.2bp / verdict=INSUFFICIENT_SAMPLES

# 分包2：E4 首轮 verdict 重放（需 CH 只读）
python scripts/audit/t0_conditional_e4_exam.py
# 预期：n_gate_pairs=8 → INSUFFICIENT_SAMPLES；emotion_gate.available=false

# 分包3：登记册抽查
grep -c 'C11\|撞名' docs/_working/vocab_legislation/02_state_vocabulary_mapping_register.md
grep -n '状态词表出厂纪律' docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
```

**证据等级**（红证/黄证自评）：分包1 基线五值逐位复现=**红证**（机器判据+历史快照对账）；分包2 E4 verdict=**红证**（frozen 卡+脚本机械执行+全量披露）；分包3=**黄证**（人工普查行号锚，普查底稿无第二独立来源；登记册生成器化已列为后续项）；词表普查=黄证（子代理实测，行号可抽查但未双盲复核）。

## 2. 卡先行与零行为变更审计（任务书红线扫描）

- 卡 frozen 先于取数：t0_conditional_prereg_card.md 落盘时间先于 e4 考试首次运行（mtime 链可核）；禁裸跑回测=遵守（考试仅消费既有 D 后流水，无新回测产物）；
- 零行为变更：src/ 零改动；存量枚举原位保留；construction_workflow_policy 仅追加一节验收条款；
- 避让红线：未碰丁域代码/sim-launch/integrated-bt 在飞产物；未接实盘不下单；查库全只读；
- 判据灭失免疫：全部判据/考试件落 docs/scripts，.runtime/tmp 零判据件。

## 3. commit 终态表（收官时若队列仍在消化以 git log 为准）

| 批 | 内容 | hash（worktree 分支 session/st-t0-revival-20260922） |
|---|---|---|
| 分包3 | 词表立法两件+出厂纪律+裁定册 | ab89a56bd2 |
| 分包1 | cost_trio 判据重建+token+翻译册+裁定册 | 见 git log（本报告随批） |
| 分包2 | 预注册卡+E4 考试件+verdict | 见 git log（本报告随批） |

## 4. 过程披露（灰区动作，全部留痕）

1. **热册蒸发实锤复证**：主区 capability_canonical_file_registry.yaml 在我会话窗口内被他会话（st-residual）以陈旧基底整体覆写两次，我插入的 token 两次被蒸发（safe_write.jsonl 审计+worktree/index sha 错位取证在案）——与记忆 kline-volume-unit-cure-20260922 的"主区改注册表必死"复证同向。处置=全部登记面动作迁 session worktree 执行。
2. **手工拼接两次弄坏 registry YAML**（已当场从 index 恢复，净损害=0：坏版本未 commit、未被他读兜走）；教训已吸收=热册一律走 batch_creation_tokens 工具链，禁手拼。
3. **队列死信 2 条**（q-0001/q-0002）：worktree 本地队列无法创建 landing 环境（serializer 分支被主区占用=结构性死锁）——改直连落地，死信留在 worktree 本地队列（不污染主区队列），留档备查。
4. 主区降级直改申请已登记（纯文档+判据脚本批，并行协调政策 §10），实际执行升级为 worktree 施工（更严不更松）。

## 5. 残余与移交

- **丁线情绪六段持久化**：sentiment_panel 无六段标签 → T0-CONDITIONAL 情绪门 unevaluable；接线义务移交 data 线（表设计+TDM 六段日更落库），接线后 e4 考试原样重跑自动升双门。
- **样本积累**：等新回测产物入库（D 后流水增量），cost_trio 与 E4 考试原样重跑，禁改卡。
- **登记册生成器化**：词表映射登记册首册为人工普查版，生成器（symbol 扫描→登记册 diff）列为后续施工候选（宪法 §9.5）。
- **队列结构性死锁**：worktree 会话 enqueue 落 worktree 本地队列且无法 landing——移交治理线（建议：worktree 会话一律 --no-auto-enqueue 直连，或 worktree 本地队列 landing 复用主区 serializer）。
- 7 条 claim 于会话收尾 release；staging 成果已全部 commit 无 promote 依赖。
