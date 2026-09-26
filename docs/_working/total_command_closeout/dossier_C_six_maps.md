---
ttl: task_bound
---
# 案卷 C — 全景图六图战役（st-mapbuild-20260924）机械实测

- 生成时刻口径：主区 dev HEAD=`54622bbbf4`；worktree 分支 session/st-mapbuild-20260924 HEAD=`cb6b4bfc0e128e1312f0b12cacfb25175e42c959`。
- 落地定义：`git show HEAD:<path>` / `git ls-tree -r --name-only HEAD` 命中=在 HEAD。
- 本文件只记录实测读数，不含裁定。

## 主表 v1（条目 1~4 初读）

| # | 声称 | 命令 | 实测读数 | 态 |
|---|------|------|---------|-----|
| 1a | 六图已完工、唯一欠"落地" | `git ls-tree -r --name-only HEAD \| grep -c "docs/_working/map_build/"` | `1`（仅 `docs/_working/map_build/02_skeleton_writeback.md`） | 与声称不符 |
| 1b | 五图 × 6 类件在 HEAD | `git ls-tree -r --name-only HEAD \| grep -c -F <path>`（30 件全测） | 30/30 命中数=**0**；HEAD 树内无任何 `generate_<m>.py` / `validate_<m>.py` / `<m>_gate.py` / `test_<m>_adversarial.py` / `test_<m>_gate.py` / `config/<m>.yaml` | 全部未落地 |
| 1c | 件在盘位置 | `ls`＋`git -C <wt> status --porcelain`（真实路径：`config/<m>.yaml`、`scripts/governance/d5_architecture/{generators,validators}/…`、`src/zephyr/gov_enforcement/commit_gates/<m>_gate.py`、`tests/governance/{d5_architecture,commit_gates}/…`） | 33 个 `??`（未跟踪）件包含：5 个 `config/<m>.yaml`、5 个 generate_*、5 个 validate_*（含 `validate_construction_steps.py`，construction_workflow 无同名 validator）、5 个 `*_gate.py`、5 个 test_*_adversarial、5 个 test_*_gate、`scripts/governance/next_ruling_id.py`、`tests/governance/test_next_ruling_id.py`、`docs/01_.../vocabularies/card_state_vocabulary.yaml`、`docs/_working/map_build/` | 仅 worktree 盘上有，且全为未跟踪态（未 staged、未 commit） |
| 2a | 工作现场存在、条目≈94 | `git -C .aidrafts/st-mapbuild-20260924 status --porcelain \| wc -l` | **272**（238 ` M` + 34 `??`） | 数值不符（272 vs 94） |
| 2b | 现场未被回退 | `git -C <wt> rev-parse HEAD` vs `git rev-parse session/st-mapbuild-20260924` | 两者相同（`cb6b4bfc0e`），指针未被重置 | 一致 |
| 2c | 分支有自有工作 | `git merge-base dev session/…` / `git rev-list --left-right --count dev...session/…` | merge-base=`cb6b4bfc0e`=分支 HEAD；`dev...session` = **237 / 0** | 分支相对 dev 零自有 commit（落后 237） |
| 2d | 分支 vs dev 差异面 | `git -C <wt> diff --name-only dev...HEAD \| wc -l` | `0` | 无已提交差异 |
| 3a | 队列袋 pending 7 = 0036~0042 | `ls .runtime/commit_queue/dead \| grep -c mapbuild` | dead 目录 **33** 个 mapbuild 袋（含 0036/0037/0039）；done 2 个（0017/0024） | dead 数不符（33 vs 26）；pending 待复核 |
| 4a | 备份份数 46 / code 24+ | `find .runtime/tmp/mapbuild/backup -path "*map_build*" -type f \| wc -l`；`find .runtime/tmp/mapbuild/backup/code -type f \| wc -l` | map_build 面 **46**；code 面 **25**；backup 总文件 72 | map_build 相符 |
| 4b | 重放器/脚本在否 | `ls .runtime/tmp/mapbuild` | `apply_mapbuild.py`、`land2.py`、`LEDGER.md`、`FINAL_BLOCKERS.md`、`backup_code.py`、`do_backup.py`、`fix_and_requeue.py`、`fix_docs.py` 均在（未运行） | 存在 |

## 追加段 A（条目 3~7，实测）

### 条目 3 该役队列袋现状
命令：`ls .runtime/commit_queue/{pending,dead,done} | grep -i mapbuild`；`python -c "json.load(...)"` 逐袋摘 dead_reason。

| # | 声称 | 实测读数 | 态 |
|---|------|---------|-----|
| 3-1 | pending 7 = 0036~0042 | `pending/` 目录内 mapbuild 袋 **0 个**；0036/0037/0038/0039/0040/0041/0042 **全部在 dead/** | 不符：无 pending，七袋皆死 |
| 3-2 | dead 26 | dead/ 下 mapbuild 袋 **33**（0006–0015、0018–0022、0025–0042；缺 0001–0005、0016、0017、0023、0024） | 不符（33 vs 26） |
| 3-3 | done 2 = 0017/0024 | done/ 恰 2 件：`q-20260924-…-0017`、`q-20260925-…-0024` | 相符 |
| 3-4 | dead_reason 签名归类（33 袋） | TRANSLATION-COVERAGE **11**（新建 .py 缺 plain_zh，计数 1/3/5/9/10 不等）｜CREATE-GUARD 无 creation_token **8**｜GATE-PRECOMMIT-RUN（gate-naming / 冲突标记）**2**｜landing 注册表项基底不可知 **2**｜REFERENCE-INTEGRITY RULING-REFERENCE 悬空 **2**｜REFERENCE-INTEGRITY ARCH-REFERENCE 悬空 **1**｜cascade_stale **1**｜TTL-METADATA **1**｜CAPABILITY-LOOKUP-REQUIRED **1**｜CLAIM_REQUIRED_VIOLATION **1**｜LandingEnvironmentError（REAL-KEY-REFERENCE gate 3/102 加载失败，裁定#351 fail-closed）**1**｜WorktreePunchThroughError EV-02（主仓 HEAD 93e55f2f46→16d58a652d）**1**｜快照基底冲突 align_all.py **1** | 多签名，非单一"own-scope 缺陷" |
| 3-5 | done 0017 真实落地 | landed_id=`9de51e673f`，`git merge-base --is-ancestor … HEAD`=**YES**；该 commit 实含 5 件：`capability_canonical_file_registry.yaml`、`docs/_working/audit_fix/{audit_fix_ledger.md,lanes/lane_l1_commit_base.md}`、`docs/_working/map_build/02_skeleton_writeback.md`、`scripts/governance/commit_queue_landing.py`、`tests/governance/test_commit_queue_base_head.py`（跨会话混袋） | 落地（非纯六图件） |
| 3-6 | done 0024 真实落地 | landed_id=`613dcc4f9c`，is-ancestor=**YES**；仅 1 件 `capability_canonical_file_registry.yaml` | 落地（token 册，无图件） |
| 3-7 | 六图产物有任何落地袋 | 两件 done 袋文件清单中**无** config/generator/validator/gate/test 任一六图件；HEAD 中 map_build 仅 1 件且与 worktree 盘面**逐字节同**（`diff` rc=0，各 60 行） | 六图产物零落地 |

### 条目 4 备份与重放器（只读，未执行）
| # | 声称 | 命令 | 实测读数 | 态 |
|---|------|------|---------|-----|
| 4-1 | backup/map_build 46 份 | `find .runtime/tmp/mapbuild/backup -path "*map_build*" -type f \| wc -l` | **46** | 相符 |
| 4-2 | backup/code 24+ 件 | `find .runtime/tmp/mapbuild/backup/code -type f \| wc -l` | **25**（backup 总 72 文件） | 相符 |
| 4-3 | 重放器在否 | `ls .runtime/tmp/mapbuild` | `apply_mapbuild.py` 在；`land2.py`、`LEDGER.md`、`FINAL_BLOCKERS.md`、`do_backup.py`、`backup_code.py`、`fix_and_requeue.py`、`fix_docs.py` 在；`preflight.py` **未见**（LEDGER 另引 `trust_check.py`、`writeback_inventory.md`，本目录 `ls` 未见） | 部分缺失 |
| 4-4 | 卡点自述 | `cat FINAL_BLOCKERS.md`（8 行） | 自述两点拦阻：A `PROTECTED-PATHS`（ruling_registry 受保护，需 `[ARCH-APPROVAL:<issue>]` 或活跃裁定 approved_paths，明示"不自造/不借用他人 ARCH-issue 号伪造授权"，留待 Owner 门位）；B `WORKTREE-REQUIRED`（`commit_queue.py enqueue` 无 `--allow-non-worktree`，正解 `git_commit.py --enqueue --allow-non-worktree`）；C 图14 CLI 剩 1 结构红=CV-11（政策 §2.3 缺 Step 3.5 行）、图15 实例面 9 红属预期（宿主未迁移，CV-HOST 把关）；D 已删 worktree 内被拷入的 `.env.postgres` | 自述卡点≠"唯一 own-scope 缺陷"（自述为两门+结构红） |
| 4-5 | LEDGER 自述 | `head -60 .runtime/tmp/mapbuild/LEDGER.md` | 记"成品双份（worktree 原件+backup 33 件）"、重放实测 unchanged=33、采信三查（未在册裁定号引用 0）、在队袋 0003/0004/0005、待办 7 条、外部约束（队首字母序位次 15/44→54） | 与盘上 46/25 读数不一致（33 vs 72） |

### 条目 5 五图结构校验器实跑（worktree 内，PYTHONPATH 自证通过）
自证：`export PYTHONPATH="$PWD/src"` → `python -c "import zephyr;print(zephyr.__file__)"` = `D:\ZephyrAlpha\.aidrafts\st-mapbuild-20260924\src\zephyr\__init__.py`（三次跑均自证，读数口径可用）。

| 图 | 命令 | rc | 末行读数 |
|----|------|----|---------|
| 图11 dev_delivery_map | `validate_dev_delivery_map.py --map config/dev_delivery_map.yaml` | **0** | `PASS: 结构校验通过（nodes=30 edges=31 production=26 structure=4 gap=2）`（前有 `CH 配置文件不存在 …config\.env.clickhouse（CH 连接将失败）`） |
| 图12 data_supply_chain_map | 同型 | **0** | `WARN: CH 表锚 30 个未核验（allow_unverified 放行）` + `PASS …（nodes=43 edges=62 production=10 structure=33 gap=15 骨架✅=10）` |
| 图13 trading_day_cycle_map | 同型 | **0** | `PASS …（nodes=48 edges=64 segments={A:13,B:14,C:12,D:9} production=14 structure=34 gap=4 module_id=42/42 dangling=16）` |
| 图15 strategy_card_lifecycle_map | 同型 | **1** | `FAILED: 9 个违规（结构+实例）`；含 CV-08C×2（MIDVAL-20260919-TOP10 成员 1≠n_eff 10；T0-PRERG 成员 2≠n_eff 1）、CV-10×2（ALGO-VWAP-03 frozen≠red；P3-E1C-09 frozen≠suspended）、CV-17（T0-MATRIX-VWAP-CEILING 真源卡件不在盘 `docs/_working/t0_matrix/t0_ceiling_prereg_card.md`）等 |
| 图14 construction | `validate_construction_steps.py --map config/construction_workflow_map.yaml` | **2** | 该脚本无 `--map` 参（`unrecognized arguments`）；CLI 实参=`--steps/--policy/--anchors-from/--anchors-only/--skip-live/--json/--root`。按 `--steps` 重跑读数见追加段 B |
| 取号器 | `python scripts/governance/next_ruling_id.py --verify --json`（worktree 内） | **0** | `registry.entry_count=233, max_registered=415, distinct_numeric_stems=222, gap_count=193`；warnings=`队列目录不存在（worktree 场景属预期）`⇒ 在途感知=0 |

### 条目 6 测试规模声称验真
| # | 声称 | 命令 | 实测读数 | 态 |
|---|------|------|---------|-----|
| 6-1 | 本地验绿约 531 例 | worktree 内 `pytest -q tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py` | **45 passed in 49.68s**（collected 45） | 单文件实测绿 |
| 6-2 | 六图相关用例总量 | 11 件 `--collect-only -q`（不跑） | 对抗 5 件=45+125+114+60+70=**414**；gate 5 件=22+27+22+34+20=**125**；10 件合并跑 collected **539**；另 `tests/governance/test_next_ruling_id.py`=**27**（合并 566） | 539 ≈ 声称 531（差 +8）；未含 fig14/15 其它测试面 |
| 6-3 | 图14/图15 红蓝对抗测试文件在否 | `ls tests/governance/d5_architecture` | 存在 `test_construction_workflow_map_adversarial.py`（60 例）、`test_strategy_card_lifecycle_map_adversarial.py`（70 例）；`tests/governance/commit_gates/` 存在对应 `test_*_gate.py`（34/20 例）；全为未跟踪态 | 在（仅 worktree 盘） |

### 条目 7 裁定号 414/415 验真
| # | 声称 | 命令 | 实测读数 | 态 |
|---|------|------|---------|-----|
| 7-1 | 新增裁定 414 号（HEAD 册查无）/#415 | `git show HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` → 取 `ruling_id` 尾部 | HEAD 册 231 条 `- ruling_id:`，号尾=409/410/411/412/**413**；`grep -nE "裁定 41 号（HEAD 册查无）[45]\b"` 命中 **0** | 414/415 不在 HEAD |
| 7-2 | 414/415 被谁占 | `git grep -n "裁定 414 号（HEAD 册查无）\|裁定 415 号（HEAD 册查无）" HEAD` | 全 HEAD 树命中 **0**（无任何在册件引用之） | 无占用者 |
| 7-3 | worktree 是否已写入 | `grep -nE "裁定 41 号（HEAD 册查无）[45]" .aidrafts/…/ruling_registry.yaml` | 命中 `5728:- ruling_id: "裁定 414 号（HEAD 册查无）"`、`5762:- ruling_id: "裁定 415 号（HEAD 册查无）"`、`5789`（"战役侧让号重编为 裁定 414 号（HEAD 册查无）（已落地侧不回改）…"）、`5800` related_rulings 含 #414；WT 册 233 条，max=415 | 写入=在 worktree 未跟踪修改面，未落地 |
| 7-4 | 主区册与 HEAD 是否分叉 | `git diff --stat HEAD -- <ruling_registry>`（主区） | 无输出（主区册=HEAD 面） | 未分叉 |
| 7-5 | 悬空引用后果（盘上事实） | 33 袋 dead_reason | `REFERENCE-INTEGRITY 阻断: [RULING-REFERENCE] 新增 裁定#NNN 悬空引用（RULING_REFERENCE_VIOLATION）`×2 袋（0033、0040，涉 `docs/01_policies_and_standards/sop/governance…`）；另有 `[ARCH-REFERENCE] ARCH-NNN 悬空`×1 袋（0021，涉 fig12_datachain） | 取号未落地与悬空引用拦截同向并存 |

## 追加段 B（条目 5 补测 + 8~12，实测）

### 条目 5 补：图14 校验器正确 CLI
| 命令 | rc | 读数 |
|------|----|------|
| `validate_construction_steps.py --steps config/construction_workflow_map.yaml`（worktree 内，PYTHONPATH 自证=该 worktree src） | **0** | `PASS: 步骤锚校验通过（steps=17 automated=4 inspection=4 manual=21 gap=12 production=6 anchor_source=proposal）`（前带 `CH 配置文件不存在 …config\.env.clickhouse`） |
| `validate_construction_steps.py --map config/construction_workflow_map.yaml` | **2** | argparse `unrecognized arguments: --map …`（无 `--map` 参，实参见 `--steps/--policy/--anchors-from/--anchors-only/--skip-live/--json/--root`）⇒ FINAL_BLOCKERS 所称"图14 剩 1 结构红 CV-11"在本次 `--steps` 跑中**未复现**（读数为 PASS） |
| `validate_strategy_card_lifecycle_map.py`（图15）全 ERROR 行枚举 | **1** | 恰 **9 条 error**＋大量 warn：`CV-06 T0-CONDITIONAL`（命中复活授权 裁定#331,#399 而 revives 缺省，X13）、`CV-08 X09`（hypothesis_key=vwap_reversion_t0 双卡 ALGO-VWAP-03/T0-PRERG-01）、`CV-08B T0-PRERG-01`（verdict=RED 证据件 vwap_exam_report.md 实属 ALGO-VWAP-03，F-07）、`CV-08C ×3`（族 FPOOL-20260919-TOP20 成员 1≠n_eff 6；MIDVAL-20260919-TOP10 1≠10；T0-PRERG 2≠1）、`CV-10 ×2`（ALGO-VWAP-03 frozen≠red；P3-E1C-09 frozen≠suspended）、`CV-17 ×1`（T0-MATRIX-VWAP-CEILING 真源卡件不在盘）。warn 面：`CV-08A` 无 hypothesis_key **44** 条、`CV-08D` n_eff 未声明 **16** 条 |

### 条目 8 图15 的"9 处真红"与不在盘卡件
| # | 声称 | 命令 | 实测读数 | 态 |
|---|------|------|---------|-----|
| 8-1 | 9 处真红="真源卡件不在盘"的 9 条 | 上表全枚举 | 9 条红中**仅 1 条**属"真源卡件不在盘"（CV-17）；余 8 条为族账/双卡/三元错绑/镜像冲突/复活缺 revives 六签名 | 归类与声称不符 |
| 8-2 | 不在盘卡件指针 | `ls docs/_working/t0_matrix/`、`git log --all -- <卡路径>` | `docs/_working/t0_matrix/t0_ceiling_prereg_card.md`（目录实存 9 件：FINAL_REPORT/LEDGER/REDEVID/T0_SCHEME_MATRIX/reconcile_pack×2/t0_ceiling_daily.csv/t0_ceiling_result.yaml/t0_ceiling_verdict.md，**无该卡**）；`git log --all` 命中 0（从未入库）。规格另记第二张 `docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md`（同样不在盘，`90_card_state_registry_spec.md:159`、`:240` RC-18） | 两张卡件均不在盘 |
| 8-3 | 被哪些生产件引为判据真源 | `grep -rn "t0_ceiling_prereg_card\|t0_conditional_v3_prereg_card" src scripts` | `scripts/audit/t0_ceiling_capacity_exam.py:1`（[BLUEPRINT]）、`:7`、`:273`；`scripts/audit/t0_gpu_condition_pack.py:1`；`scripts/audit/t0_six_phase_materialize.py:1` ⇒ 3 个 production 脚本、5 处引用 | 幽灵真源引用面实测 |
| 8-4 | 案卷面记录 | `grep -n "CV-17\|不在盘" fig15_cardlife/*` | `fig15_cardlife/90_card_state_registry_spec.md:159`（两张卡"实测 git log --all 从未出现"⇒指纹无从计算即 error）、`:240` RC-18、`91_registry_host_proposal.yaml:119`（D15-G06 面：run 档案整目录 gitignored）、`:290 truth_source_missing: true`、`:376`（REG-STATE-VOCAB-001 physical_path 件在本会话分支不在盘）、`:423`（CV-17 腿 nature=数据真缺陷）；fig15 簿合计 2511 行（6 件：00/01/02/03/90/91） | 案卷自述与实跑同向 |
| 8-5 | `.gitignore` 第 586 行忽略 `data/backtest_artifacts/` | `git show HEAD:.gitignore \| sed -n '586p'` | 第 586 行 = **`data/backtest_artifacts/`**（上 2 行为 2026-09-02 裁定注释"回测产物…可重跑再生产物"） | 相符 |
| 8-6 | 判定书实存件数（只 ls/wc） | `find data/backtest_artifacts -type f` | 总 **1016** 文件；按后缀 json 368 / parquet 265 / yaml 193 / **md 189** / tsv 1；文件名含 verdict/judgment/判定 的 **154**；`git ls-files data/backtest_artifacts` = **1**（`bt-8607ffc2.json`，在册-却-被忽略态） | 读数交付 |

### 条目 9 卡状态登记面迁移
| # | 声称 | 命令 | 实测读数 | 态 |
|---|------|------|---------|-----|
| 9-1 | card_state_vocabulary 在 HEAD | `git ls-tree -r --name-only HEAD \| grep -c card_state_vocabulary` | **0**；worktree 盘上实存 4527 B（13 值受控词表，声明 experiment_registry 与图15 校验器必须 `load_vocabulary_values` 动态加载、禁硬编码） | 未落地（仅 worktree 未跟踪） |
| 9-2 | ROOR 补条 | `grep -n card_state_vocabulary <ROOR>` | worktree 版 `docs/registry_of_registries.yaml:264` 已登 physical_path；HEAD 版命中 **0** | 未落地 |
| 9-3 | schema 2.1→2.2 | python 解析两版 experiment_registry | HEAD：`schema_version: 2.1`、`version: 1.1.3`、`entry_schema` 68 键（无 card_state）、`experiments` **11** 条（0 条有 card_state）；worktree：`schema_version: 2.2`、`version: 1.2.0`、`entry_schema` 92 键（含 card_state）、`experiments` **67** 条、有 card_state 的 **56** 条（frozen 51/red 2/sealed 1/suspended 1/candidate 1，None 11）；worktree 该件未提交状态=相对其 HEAD **M**（`+1565/-3`） | 版本推进属实，回填在盘不在册（HEAD） |
| 9-4 | "89 张卡回填" | python 解析 `config/strategy_card_lifecycle_map.yaml` 的 `counts` | `cards_total: 89`、`registered_entries_in_ledger: 56`、`corpus_files_registered: 56`、`state_undeclared_headless: 29`、`by_state {candidate:1,draft:1,frozen:53,sealed:1}`、`needs_adjudication: 2`；`card_ledger` 实条 56 | 89=卡面总数（含 29 无头），回填实为 **56** 条 |

### 条目 10 共享写域热册冲突面
命令：worktree 内 `git diff --stat dev..session/st-mapbuild-20260924 -- <p>`（记 A）与 `git diff --stat HEAD -- <p>`（记 B，=本役未提交写面）。

| 文件 | A：分支↔dev 已分叉 | B：worktree 盘↔其 HEAD | 热册性（多班共写） |
|------|-------------------|----------------------|-------------------|
| `…/catalogs/ruling_registry.yaml` | 1 file, +4/−71 | **+145/−4** | 热（GW/裁定班共用）；HEAD 面主区未分叉（主区册=HEAD） |
| `…/catalogs/capability_canonical_file_registry.yaml` | 1 file, −5417 | **+345** | 热（CREATE-GUARD token 册，本役 33 袋中 2 袋已落地即此册） |
| `…/catalogs/module_translation_registry.yaml` | 1 file, +154/−1154 | **+128** | 热（TRANSLATION-COVERAGE 真源，11 袋死因即此） |
| `…/catalogs/in_process_gate_registry.yaml` | 1 file, +5/−32 | +1/−1 | 热（门禁注册） |
| `…/catalogs/experiment_registry.yaml` | 未分叉（空） | **+1565/−3** | 中（本役独占写面大） |
| `…/vocabularies/card_state_vocabulary.yaml` | 未分叉（空，dev 无此件） | 空（worktree 中为 `??` 未跟踪） | 新册，ROOR/index.md 连带 |
| `docs/registry_of_registries.yaml`（ROOR） | 未分叉 | **+20/−8** | 热（注册表总目） |
| `…/governance_sop/alignment_checklist.md` | 未分叉 | **+15/−1** | 热（挂轴，多班共写） |
| `…/construction_sop/construction_workflow_policy.md` | 未分叉 | **+1** | 热（07 域 15 步真源） |
| `…/generators/align_all.py` | 1 file, +37/−104 | **+74/−4** | 热（单入口对齐器，0022 袋死因即此路径冲突） |
| `src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py` | 未分叉 | **+10** | 热（九图挂 gate） |
| `scripts/governance/d5_architecture/validators/blueprint/panorama_alignment_gate.py` | 不存在 | 不存在 | —（真路径为上一行） |

补充：`git diff --name-only HEAD` 在该 worktree 覆盖 238 个 ` M`，绝大多数是 `docs/03_modules/**/blueprint.md`、`project_handbook/*`、`_cross_layer/*` 等派生文档面（与 HEAD 面差异由"分支落后 dev 237 commit + 本役再跑生成器"两因叠加，非全部本役自有写面）。

### 条目 11 align_all 环境缺陷（主区，只跑到报错）
| 项 | 读数 |
|----|------|
| 命令 | `python scripts/governance/d5_architecture/generators/align_all.py`（主区，跑 2 次） |
| 真实退出码 | **1**（`REAL_RC=1`；首次因管道 tail 读到 0，属读数陷阱，已改正） |
| 失败签名 | 末段 `❌ 硬阻断: 10 个硬问题（域不一致=0, 幽灵锚点=0, frontend_map fail=0, decision_map error=0, factory_map error=0, **gomap error=10**）须修复后才能施工！` ＋ `⚠️ 软问题: 1002 个 warn`；10 条硬=GOMAP 机生层漂移（`scripts/governance/meta_question/wo006/probe_source_c_ths.py`、`wo_a2legs/{_probe,probe_backfill_sources,probe_tdx_cfg_coverage,probe_unmatched_880_identity,register_reaper_keep}.py`、`check_meta_question_audit_reconcile.py`、`wo_intake_reconcile/{generate_source_line_register,intake_batch,replay_audit_to_jsonl}.py` "scan() 重建新增，yaml 未刷新"）＋ 另处 `FAIL: S11 违规 9 条` |
| PG 相关 | 输出中**无** psycopg/PG 连接失败签名；`config/.env.clickhouse` 加载成功、`ClickHouse 连接已建立 host=172.24.30.100`（writer/reader 各 1）⇒ 主区跑不通的实测原因是 GOMAP 机生层漂移（内容级），不是 PG 配置缺失（未取证到 PG） |
| 副产物（本矿工越界副作用，如实报） | 第 1 次跑写入 `docs/02_enterprise_architecture/03_governance_reports/panorama_alignment_overview.md`（该件被 `.gitignore:549` 忽略，`git status` 不显）；跑后主区 `git status` 显示 `M architecture_model/index.yaml`（+1/−1）、`M config/governance_operations_map.yaml`（+1568/−1562）。主区原有 467 项脏面（他班在途），此两件是否本跑新增**未能前置留证**，口径待核 |

### 条目 12 path_ownership 漂移（乙-8）
| 项 | 读数 |
|----|------|
| 在册态 | `docs/03_modules/path_ownership_map.yaml:65` `path: 'src/zephyr/plan_engine/next_day_forecaster.py'` → `owner_blueprint: 'MOD-PLAN-029'`、`claim_type: 'depgraph_node'`、`declared_in: ''`、**`existence: '未实现'`**、`ownership_judgment: '本模块'` |
| 磁盘实存 | `src/zephyr/plan_engine/next_day_forecaster.py` 实存，19191 B，mtime 2026-09-18 21:32；件头 `# [MODULE] zephyr.plan_engine.next_day_forecaster`、`# [TESTS] tests/plan_engine/test_next_day_forecaster.py` |
| dloop 直调 | `src/zephyr/plan_engine/daily_loop_master_switch.py:198` `from zephyr.plan_engine.next_day_forecaster import maybe_emit_next_day_forecast`；`src/zephyr/strategy_pipeline/pipeline_events.py:1047`（事件链 import）；`src/zephyr/plan_engine/__init__.py:80` `from … import NextDayForecaster`；测试引用 `tests/strategy_pipeline/test_pipeline_events.py:45`、`tests/plan_engine/test_next_day_forecaster.py` |
| 其它在册面 | `…/catalogs/module_translation_registry.yaml:54855`、`…/catalogs/capability_canonical_file_registry.yaml:32775-32778`（token `auto-scaffold-next_day_forecaster-20260917`）、`state_vocabulary_registry.yaml:319`（source `…:41`）均在册 |
| 投影件漂移 | 主区 `docs/03_modules/path_ownership_map.yaml` 相对 HEAD 有 1 行改动（他班在途）；worktree 内该件相对其 HEAD 无改动 | ⇒ `existence: 未实现` 与"磁盘实存 + dloop 直调 + 测试在册"三面冲突 |

## 追加段 C（条目 1 三态明细 + 挂轴/注册面实测）

### 六图件三态表（HEAD / 主区盘面 / worktree 盘面）
真实路径模板：`config/<m>.yaml`、`scripts/governance/d5_architecture/generators/generate_<m>.py`、`scripts/governance/d5_architecture/validators/validate_<m>.py`、`src/zephyr/gov_enforcement/commit_gates/<m>_gate.py`、`tests/governance/d5_architecture/test_<m>_adversarial.py`、`tests/governance/commit_gates/test_<m>_gate.py`。

| 件族 | 图11 dev_delivery | 图12 data_supply_chain | 图13 trading_day_cycle | 图14 construction_workflow | 图15 strategy_card_lifecycle |
|------|------|------|------|------|------|
| `config/<m>.yaml` | 仅 worktree 盘（未跟踪） | 同 | 同 | 同 | 同 |
| `generate_<m>.py` | 仅 worktree 盘（未跟踪） | 同 | 同 | 同 | 同 |
| `validate_<m>.py` | 仅 worktree 盘（未跟踪） | 同 | 同 | 名为 `validate_construction_steps.py`，仅 worktree 盘（未跟踪） | 同 |
| `<m>_gate.py` | 仅 worktree 盘（未跟踪） | 同 | 同 | 同 | 同 |
| `test_<m>_adversarial.py` | 仅 worktree 盘（未跟踪） | 同 | 同 | 同 | 同 |
| `test_<m>_gate.py` | 仅 worktree 盘（未跟踪） | 同 | 同 | 同 | 同 |

- 30 件在 HEAD 命中数一律 **0**；主区工作树（`D:\ZephyrAlpha` 盘面）命中也一律 **0**（`ls config`、`ls src/zephyr/gov_enforcement/commit_gates`、两处 `ls tests/...` 全空，`scripts/governance/next_ruling_id.py` 主区亦无）。
- 案卷面 `docs/_working/map_build/`：HEAD 仅 1 件（`02_skeleton_writeback.md`，与 worktree 盘逐字节同）；worktree 盘另有 5 件顶层 + fig11~fig16 六子目录共 41 件（fig11 9 / fig12 9 / fig13 11 / fig14 5 / fig15 5 / fig16 2），全部 `??` 未跟踪。
- 图16（ruling）在 LEDGER 中自述"判**不建**"，仅 `fig16_ruling/00_skeleton.md`＋`91_wordlist_and_roor_proposal.md`。

### 挂轴与在册面（全部只在 worktree 未提交面）
| 项 | 命令 | 实测读数 |
|----|------|---------|
| align_all 挂载 | `git -C <wt> diff HEAD -- …/align_all.py` | 新增 5 行图目录（"第十一图…dev_delivery_map / 第十二图…data_supply_chain_map / 第十三图…trading_day_cycle_map / 第十四图…validate_construction_steps↔construction_workflow_map / 第十五图…strategy_card_lifecycle_map"），含注释"图14 校验器模块名与图名不同构"；净 +74/−4 |
| panorama gate 挂载 | `git -C <wt> diff HEAD -- src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py` | 新增 5 组 `("<MAP>-MAP", "<m>_gate", "_check")` 子检查登记（挂 MAP-ALIGNMENT 聚合台，不建独立 gate）；净 +10 |
| in_process_gate_registry | `git diff HEAD -- …/in_process_gate_registry.yaml` | `MAP-ALIGNMENT.files_trigger` 由 3 项扩到 18 项（注入 5 个 `config/<m>.yaml`＋5 validator＋5 generator）；净 +1/−1。HEAD 面该册六图命中数=**0** |
| gate_registry.yaml（HEAD） | `git ls-tree` 定位 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` | 存在，但六图名在 HEAD 各册命中 0 |
| alignment_checklist | `git show HEAD:…/alignment_checklist.md \| grep -icE "<六图名>"` = **0**；worktree 面 +15/−1 | worktree 新增 5 行图目录，**逐行以"裁定 414 号（HEAD 册查无）/#415"为升级依据**（如"图 11，2026-09-24 十一图升级 裁定 414 号（HEAD 册查无）"、"图 14/15 … 裁定 415 号（HEAD 册查无）"）——HEAD 无此二号 ⇒ 在册挂轴文本对未落地裁定号的引用 |
| module_translation_registry | `git diff HEAD` 新增 `+- module_path:` | 覆盖 5 图的 generate_/validate_/_gate 三类新 .py（净 +128）——HEAD 面缺，故 11 袋死于 TRANSLATION-COVERAGE |
| capability_canonical_file_registry | `git diff HEAD` 新增 `+- file: docs/_working/map_build/…` `capability: map_build` | 净 +345；HEAD 已含 55 条 map_build 宿主（done 袋 0017/0024 落地结果），未含六图 .py 与 46 份案卷全量 |
| ruling_registry 新增 | `git -C <wt> diff HEAD -- …/ruling_registry.yaml \| grep "^+- ruling_id"` | 相对其**陈旧 HEAD**列出 +411/+412/+413/+414/+415；其中 411/412/413 已在 dev（属基点陈旧噪声），真实自有新增=**414/415** 两号（未落地） |

## 新增发现（盘上实况，非声称项）
1. worktree 分支基点 `cb6b4bfc0e` 落后 dev **237 个 commit**，分支零自有 commit；其 `git log -5` 顶端是 st-cleanup/st-audit-all/st-library 等**他班**消息 ⇒ "session 分支"从未有过本役提交，全部成果活在未跟踪/未提交工作面。
2. worktree 的 272 脏项 = 238 ` M` + 34 `??`；` M` 中六图自有写面集中在 8 个热册＋2 个 policy/挂轴件，其余为 `docs/03_modules/**/blueprint.md`、`project_handbook/*` 等派生再生面（与基点陈旧混合，无法机械切分）。
3. 33 封 dead 袋签名共 **13 类**（TRANSLATION-COVERAGE 11、CREATE-GUARD 8、GATE-PRECOMMIT-RUN 2、基底不可知 2、RULING-REFERENCE 2、ARCH-REFERENCE 1、cascade_stale 1、TTL-METADATA 1、CAPABILITY-LOOKUP-REQUIRED 1、CLAIM_REQUIRED 1、LandingEnvironmentError 1、WorktreePunchThroughError 1、快照基底冲突 1）；其中 `WorktreePunchThroughError`（0029）自述主仓 HEAD 被 `reset` 从 `93e55f2f46` 移到 `16d58a652d`，`LandingEnvironmentError`（0020）自述 3/102 gate 加载失败 fail-closed。
4. done 袋 0017 的落地 commit `9de51e673f` 实含 6 件（跨 `audit_fix/`、`commit_queue_landing.py`、`tests/governance/test_commit_queue_base_head.py`），非纯六图袋。
5. 图15 校验器的 9 条红里有 5 条（CV-08C×3、CV-08、CV-08B）落在 `config/strategy_card_lifecycle_map.yaml` 自带 `counts` 的口径上：`cards_total=89 / registered_entries_in_ledger=56 / state_undeclared_headless=29 / needs_adjudication=2`。
6. 图15 的 `registry_host=experiment_registry`、`registry_host_path=docs/…/experiment_registry.yaml`、`schema_version: 0.2`（图件自身），锚块/词表来源现态指向 `91_*` 提案件（`anchor_source=proposal`、`registry_host=proposed`）——即宿主迁移仍处"提案装载"态。
7. 主区跑 align_all 的真实硬阻断是 GOMAP 机生层漂移 10 条（他班未刷新 `generate_governance_map.py` 的产物），与六图无关；CH 可连通、无 PG 报错取证。
8. 图13 校验 PASS 行仍带 `dangling=16`、图12 带 `WARN: CH 表锚 30 个未核验（allow_unverified 放行）`——rc=0 不等于锚全部核验。
9. 本矿工越界副作用：第 1 次 `align_all.py`（主区）写 `docs/02_enterprise_architecture/03_governance_reports/panorama_alignment_overview.md`（被 `.gitignore:549` 忽略，不进 status）；跑后主区显示 `M architecture_model/index.yaml`(+1/−1) 与 `M config/governance_operations_map.yaml`(+1568/−1562)，是否为本次跑新增未能前置留证（主区原本已有 467 项脏面）。未做 git 写操作、未清理、未修改他册。

## top 5 与交接书不符处
1. **落地态**：交接书"六图已完工、唯一欠落地"→ 实测六图 30 个施工件 + 46 份案卷 **在 HEAD/主区盘面全为 0**，全为 worktree 未跟踪；HEAD 仅 1 份 `02_skeleton_writeback.md`（经 done 袋 0017 落地，且该 commit 系跨会话混袋）。
2. **队列袋**：声称 pending 7（0036~0042）/ dead 26 → 实测 pending **0**，0036~0042 **七袋全在 dead**，dead 共 **33**、done 2（0017/0024 落地属实）。
3. **卡点性质**：声称"被一个 own-scope 缺陷卡住"→ 实测 13 类不同死因，含 TRANSLATION-COVERAGE 11、CREATE-GUARD 8 与两条 landing 结构性异常（打穿复核 / 基底不可知）；FINAL_BLOCKERS 自述亦为 PROTECTED-PATHS＋WORKTREE-REQUIRED 两门。
4. **现场规模**：声称 ≈94 条 → 实测 **272** 条；且分支基点落后 dev 237、零自有 commit，`diff dev...HEAD = 0`。
5. **数字口径**：531 例 → 六图 10 件实测 collected **539**（单文件 test_dev_delivery_map_adversarial 45 passed 实跑绿）；裁定 #414/#415 仅存于 worktree 册（HEAD max=413、全 HEAD 零引用）；"89 张卡回填"实为 89=卡面总数、在册回填 **56**、无头 29；图14 用 `--steps` 跑读数为 PASS（FINAL_BLOCKERS 自述的 CV-11 红未复现）；`preflight.py`/`trust_check.py` 等 LEDGER 引用件未见于备份目录。

## 追加段 D（条目 3 CLI 正门读数，机读原文）

命令：`python scripts/commit_queue.py status --session st-mapbuild-20260924 --no-bootstrap`（RC=0，输出 JSON）

| 字段 | 实测值 |
|------|--------|
| `counts` | `pending=0, processing=0, done=2, dead=33` |
| `total` | 35（items 的 state 集 = {dead, done}，无 pending/processing） |
| `lease` | `{"present": false}` |
| `head` | `null`（该役在队首无占位） |
| `daemon` | `{"online": true}` |
| done 两件 | 0017→landed_id `9de51e673f…`、0024→`613dcc4f9c…`（与追加段 A 3-5/3-6 一致，两者 `git merge-base --is-ancestor … HEAD` 均 YES） |

关键 dead_reason 原文补录（逐字，机读面）：
- `q-…-0040`：`REFERENCE-INTEGRITY 阻断: [RULING-REFERENCE] 新增 裁定#NNN 悬空引用（RULING_REFERENCE_VIOLATION）——以下文件引用了 ruling_registry.yaml 中未登记的编号：\n  - docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md: 裁定 414 号（HEAD 册查无）, 裁定 415 号（HEAD 册查无）`（尾注原文："本门禁只检测新增引用，历史悬空引用不阻断"）⇒ **未落地的 414/415 与被同一门拦下的挂轴文本互为因果，实测闭环**。
- `q-…-0038`：`TRANSLATION-COVERAGE: 1 个新建 .py … 详情: 无 plain_zh 简介[scripts/governance/next_ruling_id.py]`（取号器自身即缺翻译条目）。
- `q-…-0039`：`[landing] 注册表项基底不可知（base_head 与 base_blob 皆无）——拒绝以 6d0025002359^ 猜基底做合并（09-24 热册被吃病根）`。
- `q-…-0042`：`CREATE-GUARD 无 creation_token … ['docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml', 'docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml']`（两张 91 号提案件本身无 token）。
- `q-…-0006`：`cascade_stale …（stale_by=q-20260924-st-audit-fix-20260924-0022）`（他班袋致本役袋作废）。

## 无法判定 / 缺口

1. 交接书原文未盘到（本案卷只见到 `00_campaign_brief.md`/`01_lane_workplan.md`/`99_pending_owner.md`/LEDGER/FINAL_BLOCKERS 等自述件），"声称≈94 / 531 / pending 7 / dead 26 / 89 回填"等数系任务书转述，逐条对照已给。
2. worktree 的 238 ` M` 中"本役自有写面" vs "分支落后 237 commit 的对照噪声"未能机械分离（HEAD 基点≠dev tip）。
3. `preflight.py`、`trust_check.py`、`writeback_inventory.md`（LEDGER 引用）在 `.runtime/tmp/mapbuild/` 顶层 `ls` 未见，未能判定是否曾存在。
4. LEDGER 自述"backup 33 件 + sha manifest"与实数（map_build 面 46 / code 面 25 / 总 72）不同，sha manifest 件本身未定位。
5. 主区 align_all 是否**只因** PG 缺失而失败：无 PG 报错证据，读数指向 GOMAP 机生层漂移；PG 配置件实存性未查（超出本条命令）。
6. `docs/_working/total_command_closeout/` 主表其它册（A/B/D）与本案卷的交叉一致性未查。

