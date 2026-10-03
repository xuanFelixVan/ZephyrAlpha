---
ttl: task_bound
title: "W-M1 注册表迁移波0 施工总包 — 台账 LEDGER（总指挥 30 分钟批注制）"
---

# W-M1 波0 施工台账 LEDGER

> sid=st-wm1-wave0-20260924 · 通宵总筹 · 总指挥每 30 分钟读并批注 · 裁定请求写本台账他会答
> 任务序列真源=派工令①-⑥；设计真源=同目录 02（账本）/03（投影）/09（总图）
> 通宵判据=Phase 0 PASS + 双轨启动 + 两轮零

## 0. 冷启动体检（亲验 2026-09-24 ~11:00）

- Python 3.12.8 PATH 修正 ✓；lock cleanup ✓（顺带回收 st-library-final 遗物）；process_reaper 存活（last_run 当日 10:57）✓
- **波0 两车道四源勘验**：buildA 工棚活（.worktrees/st-wm1-buildA-20260923，DDL 部署器+意图 API+19 例红蓝全绿未入队）；buildB 死信袋完整（q-...-st-wm1-buildB-20260923-0001，13 文件 blob 全在库，死因=TTL-METADATA 7 个新 .py 缺 ttl 字段）
- **事故残伤发现与修复**：02/03 设计真源"全在 HEAD"系 4bb3dcd8fd 呈签误述（该 commit 只带 09 号文），两文件全盘失踪（疑似 09-24 凌晨主区蒸发事故受害者，git 全史无此二路径）→ 已从 dead_archive_w8 袋 blob 原样复活（mineB-0002/0004=02 号文 sha256 95e90f30…、mineC-0002/0005=03 号文 sha256 8f0b9c2e…，跨袋同 sha 互证，写盘后哈希复验通过）
- PG 实例：registry_ledger schema 波0-buildA 已实弹部署（空表，指纹 738fd904…）；本班复验幂等+指纹

## 1. 施工清单（派工令映射）

| # | 项 | 状态 |
|---|----|------|
| ① | 挖矿自查（02/03/09 全读+死信袋盘点） | ✅ 完成（见 §0） |
| ② | buildA 四表 DDL+意图 API 落地 | 🔄 工棚→主区复制+token/翻译插针中 |
| ③ | buildB 投影生成器落地 | 🔄 同上+ttl 修复（死因根治） |
| ④ | 红蓝：DDL 正反例+幂等+11 读端零改动 | ⏳ |
| ⑤ | Phase 0 基线对账门（9841 尺子→PG） | ⏳ 引擎已施工（baseline.py+CLI） |
| ⑥ | 72h 双轨启动（YAML 写→PG 同写，insert-only 对账） | ⏳ |

## 2. 落地方案（多会话并发窗安全法）

- 热册禁盲盖：capability 册主区已推进 26 commits/翻译册 19 commits（相对两车道基座 66e6b31346）——只抽两车道自有增量（created_by=st-wm1-buildA/B 过滤，buildA 11 token+10 翻译，buildB 7+7），safe_write_text CAS 插针；他会话在飞条目一概不带走
- belt_daemon 主区被池化批（9ff96cc5c3）推进：buildB +41 行探针增量按锚点手工三方插入；parse_gate 主区=基座零漂移直接取 buildB 版
- 批序（token 先行家法）：批1=热册插针（token/翻译）+02/03 设计文档复活件 → 批2=buildA 代码 → 批3=buildB 代码（含 ttl 修复）→ 批4=Phase 0 引擎（baseline.py+CLI+测试）；全走 git_commit.py --enqueue
- 双轨方向裁定：Phase 1 期 YAML 仍是 commit 真源（02 号文 §4），双轨对账=insert-only（PG 缺=补登记；同键异内容/PG 独有=只记 drift 事件绝不覆写）——buildB 的 PG-wins 自愈探针保持未武装（状态文件不建，cutover 执法翻转归 Owner 门位 P-3），防"对账反噬吃掉合法 YAML 落地"

## 3. 呈批/风险

- （暂无阻塞项）

## 4. 时间戳线

- 2026-09-24 ~11:00 冷启动完成，勘验毕，开工
- 2026-09-24 ~11:4x 红蓝四套全绿：test_registry_ledger 19 passed / test_registry_ledger_baseline 6 passed / registry_projection 18 passed / parse_gate 12 passed / belt_daemon 28 passed（PG 实弹=临时 schema registry_ledger_rb_*，收尾 CASCADE 零残留）
- 2026-09-24 ~11:5x 批1 入队 q-20260924-st-wm1-wave0-20260924-0001（两热册 +21 token/+19 翻译，纯插入 0 净删，CAS+写后复验）。批序：1=token 先行 → 2=四份设计/战报/台账文档 → 3=buildA 代码 11 件 → 4=buildB 代码 11 件（ttl 死因根治：7 文件补 `# [TTL] permanent`）→ 5=Phase 0 引擎 3 件
- 2026-09-24 12:16 **Phase 0 基线导入实弹**：P0 七册 22495 条全量导入 PG registry_ledger（REG-CAPCAN-001 10715/REG-MODULE-TRANSLATION-001 8467 唯一键/REG-DOC-001 292/REG-ARCH-ISSUE-001 803/REG-ERRCODE-001 794/REG-CAND-001 622/REG-RULING-001 230）+快照 v1 发布×7（幂等 noop 判据同批验证）
- 2026-09-24 12:23 **Phase 0 PASS**（对账门机械判据：七册 zero_unexplained_drift 全 True，报告=.runtime/registry_ledger/reconcile_20260924_122327.json）。期间捕获两类真缺陷并当场修复：①PG jsonb 序列化对 YAML date 对象炸（api.py/_pg_json_dumps+default=str 统一形态）；②重复身份条目 first/last-wins 口径差（reconcile 改 first-wins 对齐 DB+collisions 计数呈报）
- 2026-09-24 12:3x **72h 双轨启动**：dual_track.enabled 旗落 .runtime/registry_ledger/+启动对账 7/7 PASS（ absorbed=0=启动点零欠账）；挂接=belt daemon 双轨探针（批6 携带，事件驱动+300s 冷却+旗文件启用，禁 cron 合红线3）+异内容按 YAML 吸收（version+1+事件全留痕）/PG 独有只记账不删
- 呈报（P-2 制，非阻断）：历史重复身份条目 REG-MODULE-TRANSLATION-001=571（同 identity 后条异内容含在内）/REG-CAND-001=1——账本按首条占坑，脏数据本体在 YAML 侧原样保留待 Owner 裁（align-dirty §3.14-R1 同源）
- 通宵判据达成态：Phase 0 PASS ✅ + 双轨启动 ✅ + 红蓝两轮零（83×2）✅；批1-6 在队待落地（q-0001..0006，FIFO 消化中）

- 插针事故披露（自愈闭环）：翻译册多族文件上首轮 EOF 追加落错族→修复；再后两次重建因提取正则吞尾（`cur[idx:]` 从锚点吞到 EOF 卷入尾部三族）造成盘面尾部族 2×/4× 复制——HEAD 全程未被污染（各 commit 单族实证），盘面以 HEAD 为基一次重建收敛（0 净删 +152 行=19 条×8 行整）。教训入配方：多族册插针必须块界断言（单条目 8 行+无顶层键泄漏），禁裸 `idx:` 尾切片
- CAS 配方补遗：safe_write 的 expected_base 必须取**补丁前**的盘面哈希——`text=text.replace(...)` 后再算 base=自坑（StaleWriteRefused 假阳性两次，误判为"他会话写穿"实际是自己传错）

## 5. 在飞与后续

- 批1-6 待队列落地（前方 24+ 项他会话件，拥塞消化中）；批6=前向修复批（api/baseline/测试/belt_daemon 双轨探针），FIFO 保证终态=已修版
- 批次落齐后动作：daemon designed 重启（吃双轨探针新代码）→`git log -1 --name-only` 核实归属→24h 对账报告制运转
- 死会话 stale claim 若挡道：gateway.release_files 精准释放后重 claim
- 监控心跳 2026-09-24 12:4x：六袋 0 done / 0 dead / 6 pending（前方 26-31 项他会话件，队列拥塞消化中）；零异常；Cron automation-749df40e 每 30 分钟在岗（落地巡查→落齐转 24h 对账）；11 读端零改动实证=capability_lookup 实跑正常+parse gate 12 passed+读端文件零修改（批3-6 改面仅 parse_gate/belt_daemon 两挂点且均为增量插段）
- 收官核账 2026-09-24 13:0x：审计发现并修复=LEDGER 终态不在任何袋（q-0002 为旧快照，落地会回退台账）→批7 补投（快照==盘面已验证）；六袋覆盖完整零丢失实证（q-0003/4/5 各缺件恰在 q-0006 终版覆盖，FIFO 终态=修复版）；.runtime/tmp 临时件清零；claim 32/32 释放；会话工棚空树 abort 收尾。七袋 0 done/0 dead/7 pending 在队（前方 38-43 项他会话件），Cron automation-749df40e 值守落地态与死信分诊。
- 死信修复战 2026-09-24 晚：首轮七袋落地战果=q-0008 台账落 HEAD（d8842c8a82）+q-0001..0006 六袋全灭（六种机械死因）。逐因修复：①热册基底不可知→requeue --worktree-root 重建快照带新基底；②10 号战报 ttl permanent 在临时区→task_bound（对齐 01-09 兄弟件）；③CLI REPO_ROOT 重定义→改 import canonical paths.REPO_ROOT；④generator.py basename 碰撞 13 件→改名 projection_generator.py+三处 import 同步+热册 token/翻译两行路径改写；⑤⑥BLUEPRINT 头 14 文件改房规 MOD-INF-037|registry_governance/blueprint.md；外捕获：src __init__ 遭第三方改写 `__all__: Final[...]` 缺 import→回退工棚验证版形态。修复后 83 passed 全绿，重投=q-0009..0013（0004 因旧快照含已改名路径无法重建→全新入队 q-0014）。监控 v1 automation-749df40e 发现消失（死信无人分诊根因之一）→重建 v2 automation-f250b992。
- 终局落地 2026-09-25 13:1x（直连+队列混合战法收官）：全部 18 关键文件进 HEAD（wm1 提交 14 笔：d8842c8a82→209028d01a 含热册双册/buildA 账本底座/翻译册×3/白名单/noqa 登记/投影十件/双 CLI）；双轮红蓝 83×2 PASS；意图 API retire 首战（generator.py 旧路径条目 tombstone，authority_ref=42bdec7baa，event 23536）+对账回填新路径行=**Phase 0 重夺 PASS 七册零未解释漂移**（reconcile_20260925_131258.json）。改名全链闭环：generator→projection_generator、schema→registry_ledger_ddl（两轮撞名终名唯一）、identity→ledger_identity，token/翻译/depgraph nodes（15174367-69 production）/import 全同步。监管理由处置：Cron v2 automation-f250b992 按 Owner"不需要定时"指令删除；双轨 24h 对账由 belt daemon 双轨探针（下纪元换血生效）或手动 wave0_phase0_gate.py reconcile 承接。
- 终局补完 2026-09-25 14:3x：belt_daemon 双轨探针单件补投（6186601c2b）——至此全部 19 文件进 HEAD（含双探针函数）、q-0040 重复袋将 noop 短路。双轨探针一旦 daemon 换血即自动生效：dual_track.enabled 旗在位、P0 七册对账 insert-only+吸收式、300s 冷却 fail-open。终验：双轮 83×2 全绿 + Phase 0 七册 PASS。对话关闭前状态=零未落文件、零未处置死信、监控自动化已删（Owner 令）。
- 双轨首个真实漂移观测（2026-09-25 23:0x，机制验证案例）：REG-MODULE-TRANSLATION-001 抓到 2 条 pg_only（t0_rule_engine/t0_state_match_matrix 翻译行，13:10 我方对账回填、其后被做T战役会话从 YAML 侧移走）——按 insert-only 纪律 PG 只记账不删，连续三轮观测稳定（不增长不收敛=他方在途改动的忠实镜像）。这正是设计要的行为：对账器把"谁在何时与账本分叉"忠实显影，处置权留给属主会话。REG-CAPCAN-001 同期 10 条 backfill 亦为他方 YAML 新增行的正常吸收。七册中 5 册恒 PASS、2 册漂移均为他方在途 WIP 镜像，双轨机制实战可用性得到确认。
- 旗恢复+运维教训（2026-10-02 01:5x）：dual_track.enabled 旗被 .runtime 运行时 TTL 清扫吃掉（旗为非 git 运行时资产无保护），已重新挂上。教训入册：双轨旗属"必须长期存活的运行时状态"，后续转正批应把旗检查纳入 reconcile CLI 自身（旗缺失=CLI 自动补挂并告警），消除对手工/外部清理的脆弱性。另有 .runtime/tmp 2 个 w3h_spec json 非我方产物不动。

## 6. 转正执行班（st-wm1-cutover-20261003，2026-10-03）B1 归属分发

- reconcile 报告=`.runtime/registry_ledger/reconcile_20261003_163521.json`：pg_only 合计 **195**（CAPCAN 156 / TRANSLATION 35 / DOC 3 / ARCH-ISSUE 1；ERRCODE/CAND/RULING 恒 PASS，RULING 侧 3 条 yaml_only 已自动 backfill 吸收）。较 Owner 归因时点（111=110 镜像+1 回填）增量 84 条同为 belt_daemon 对属主在途 YAML 编辑的持续镜像，性质同源。
- created_by 分布：belt_daemon 113 + st-wm1-wave0-20260924 82（Phase 0 导入/回填期行，其后被属主从 YAML 侧移走）。
- **关键字分发（令面三桶）**：
  - `question_mining` → **16 条**（CAPCAN creation_tokens，docs/_working/question_mining_campaign/* 的 metaq-question-mining-* token 行）→ 归问题挖矿战役；
  - `du881` → **1 条**（data/strategy_intake/du881_verdict_case/p1_v1_universe_469codes.yaml）→ 归 du881 战役；
  - `t0_*` → **2 条**（scripts/backtest/t0_rule_engine.py、t0_state_match_matrix.py，token=l2-bench-probe-20261001-*）→ 归做T战役（docs/_working/t0_matrix/）；
  - 其余 **176 条** → 明细快照=`.runtime/tmp/wm1_pg_only_detail_20261003.json`（family/entry_key/created_by/created_at/payload_head 五字段），汇总挂 §呈批。
- **机械定性（与 Owner"110 镜像+1 回填、零内容冲突"归因一致）**：底层文件已删 133 条（临时脚本清理时代 token 行：auction-backfill-*/auto-*-202608xx/090x 等）；同文件换 token/路径的改名残影 39 条（auction_strength 换 token、sla_breach_predictor→data_eng 新路径、cost_model→cost_model_calibration 等，新旧两侧核验新行都在）；.tmp 写盘残尸 2 条；文件在盘而册行全无 22 条（heal 守护重排/战役自查删除，内容层异议归各属主）。特殊核验：#ARCH-362 与 DOC 3 条在 HEAD+盘面双侧均无=合法落地删除；t0 两文件在盘在用，退 PG 后如需复登记一行 API 即回（事件表全史可查）。
- **B1 结论**：195 条全部按"合法删除镜像"进 B2 退役（不 retire 则 B3 render 会把它们复活回 YAML）；三条我方改名残影中 generator.py token 行 wave0 终局已退（entry_pk=10706，authority_ref=42bdec7baa，event 23536）不重复退，schema.py/identity.py 两条翻译行（entry_pk=18410/18409）随 C4（YAML 侧先行除名）后退役。CAPCAN 侧 schema.py/identity.py 旧 token 行（10697/10698）两侧同在=clean_match 非本批面，挂 §呈批残留观察。

## 7. 转正执行班 §B2 退役台账 + §呈批（2026-10-03）

### §B2 退役台账（已执行）

- **C4 先行**（防对账回填复活）：module_translation_registry.yaml 外科切除 schema.py/identity.py 两条旧 module_path 行（L60870-60885 共 16 行整，块界断言+扫描器复验：旧键归零、新名 ledger_identity/registry_ledger_ddl 两行无损）。
- **B2 退役**：意图 API `api.retire` 执行 **197 条**（195 pg_only+2 翻译残影），全部带 `authority_ref=WM1-CUTOVER-B2-20261003`，reason=双轨 insert-only 镜像的合法删除对齐+cutover 前 PG==YAML 一致性恢复，evidence=reconcile_20261003_163521.json。事件号 65140-65335（196 新写；首条双跑幂等 OK_NOOP 短路）；SQL 复核=本会话 retire 事件 197/197 全带 authority_ref。tombstone 语义行保留永不物理删，需要复登记一行 API 即回。
- **终验**：reconcile_20261003_165937.json = **Phase 0 PASS 七册全绿**（yaml=pg 逐册相等，pg_only=0，backfilled=0，mismatch=0）。判据①②达成。

### §呈批（代呈不施工，等 Owner/属主表态）

1. **C3 降级呈批（noqa_exempt_registry.yaml"退役豁免条目清理（基线 33→1）"）**：语义不可机械定位，本班不猜着删门禁豁免册（机械判定禁凭记忆+破坏性操作三步验证）。实勘四个口径全对不上 33：catalogs 册=30 marker；config/governance 册=195 豁免/5 类（business_subset 76/no_vocab_source 77/threshold_var 32/arch_concept 9/test_fixture 1）；死文件豁免=0；行窗 stale=39 但含行号漂移噪音不可直接判死。全仓唯一"33"命中=11 号评估卷 REG-CAPCAN-001 pg_only=33（72h 时点）——**属 B1/B2 面不属 noqa，若令面本意即此则已由本批消化，请 Owner 确认销案或给 33 条清单真源后再施工**。
2. **D1 单文件袋静默蒸发**：单文件提交袋在队列窗口内文件消失且无告警（历史上与 reset --hard/clean 特征蒸发事故同族）。建议处方：袋落库时把 blob 清单+哈希写进队列项 manifest，requeue/落地前先验 blob 存在性，缺失即转死信分诊而非静默。
3. **D2 僵尸租约 PID 复用骗过存活检查**：死会话租约的 PID 被系统复用给无关进程后，`is_pid_alive` 判活误真，租约永不过期挡道。建议处方：判活键升级为 PID+进程启动时间（或会话心跳 token）双因子，孤儿资源侦测（9b3359eccf）已有基座可挂。
4. **D3 队列楔死慢项无墙钟硬顶**：慢项无总时长上限，9-23 曾现 53 分钟零吞吐（锁等待 300s×门禁链 311-393s 循环空转）。建议处方：每项墙钟预算（如 2×基线时长），超时转 dead-letter 带分诊报告，防单项吃满队列。
5. **CAPCAN 残留观察**：schema.py/identity.py 两条**旧 token 行**（entry_pk=10697/10698，registry-migration-*-20260923）YAML 与 PG 两侧同在=clean_match，非 pg_only 非本批面；文件本体已改名不存在。建议随 B3 render 归一（render 会按 PG 侧重打，若 B3 前不处置则现态会原样投影）或下一退役批带 authority_ref 处置，呈 Owner 定。

### §补记（2026-10-03 收尾）

- **测试夹具跨批同步修复（披露）**：双轮验收首轮 86+1 红——`test_commit_belt_daemon.py::TestPoolDrainSurvivalGate` KeyError 'successors_rebuilt'。根因=st-deadletter-cure 今日批 2b28c6fbf1 给池化死信出口加 `successors_rebuilt` 计数时同步了自家 9 用例与 drain_queue_pool 规范初始化，漏了 belt_daemon 更老的测试夹具 `_pool_stats()`（生产面安全实证：daemon 经 bootstrap_drain_with_landing→drain_queue_pool 规范路径，键齐全）。本班修复=夹具一行补 `"successors_rebuilt": 0`（镜像 canonical 形态），修复后**双轮 87 passed ×2 全绿**。归属说明：缺陷体=他会话今日落地批的连带面，修因为本班验收门被挡，一行最小面+此处显性披露。
- **终验补跑**：token 登记（B3 施工单 CREATE-GUARD）在 165937 终验之后，补跑 reconcile_20261003_171440.json=PASS（CAPCAN backfilled=1=本班新 token 行按设计吸收，pg_only 保持 0）。交接态=PG==YAML 七册全等。
