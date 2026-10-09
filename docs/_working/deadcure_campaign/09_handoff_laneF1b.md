---
ttl: task_bound
completes_when: 车道F-1b 出具 tests 恢复终报并回销 07 残余索引
---
# 交割单 · 死信清偿专案 → 施工总队（两条，2026-10-09 总统筹裁定）

## 交割一：P0 tests 树被删未补 → 车道 **F-1b**（裁定原文：先对新家去重→逐族修 import→跑绿才投）

- **事实**：删除提交 `6324c9e0f6fd`（10-05，「旧路径删除袋1/3」）正文自述"内容真身=终装袋 0030-0044 新路径面…内容零删失"；
  实测 HEAD `tests/` 由该提交父树 **4089 件 → 现 2003 件**，逐字节能对上者仅 **407 件(10%)**，
  彻底无同名无同字节者 **2089 件**；全语料去重后"从未在任何 ref 出现过"的缺失路径 **2456 件**，其中 `tests/` **2203 件**（`tests/gov` 1322 为最大块）。
- **清单**：`05_tests_restore_manifest.yaml`（2325 条缺失路径 × 袋 × blob_ref × sha256 × 谱系三档）。
- **可恢复性已实测**（省一遍取证）：2325 条 `py_compile` ok=2324/fail=1；
  随机 60 件 pure_move 落主区未跟踪态跑 `pytest --collect-only -q -c py.ini` = **289 items、0 collect error**；
  同批实跑 ERROR 集中 1 件（`tests/gov/governance/meta_question/test_exam_loop_writeback.py`，缺 PG/live 账本夹具）；
  7 件跑 `gate_prerun`：内容硬阻断仅 CLAIM-REQUIRED（程序性），DOC-HEADER/MODULE-ID/CLONEGUARD/CAPABILITY-OVERLAP 全 PASS。
- **本专案为何不投**：控制实验显示 HEAD 自身在 `tests/gov/governance/d5_architecture/` 已有 1 件 collection ERROR
  （`test_generate_backtest_coverage_ledger.py` ModuleNotFoundError）→"投下即绿"不成立；按开工总纪律 #6 先跑绿才投，归施工。
- **三条禁止**：①禁对这批袋 `requeue --from-bag` 整袋盲重投（实测 82%＝1397 袋属 regression_risk，91.5% 条目无 `base_blob`，
  整档覆盖会毁 HEAD 演进内容——实例：某袋 `macro_regime_sensor.py` 仍是上溯 4 级找仓库根的旧写法，HEAD 已含 G-1 修复）；
  ②禁清 `blobs/`（唯一字节载体）；③禁把 `.corrupt-husk`/`.bak-orig` 当证据件。
- **回归本专案的钩子**：F-1b 消费完后，`07_residual_bags_index.yaml`（1350 袋 × 簇）交回本专案做**二次裁定**
  （被超集取代→②归档；仍缺→续工单；总统筹裁定第 3 条"不许永久蹲坑"由此闭环）。

## 交割二：热册整档快照互踩 → 车道 **A-12**（P1 立项）

- 实弹证据与本专案自伤三次的时间线、已验证的 `token 先行落地+内容随后` 配方、两条处方（册面行级增量正门／门禁改读 PG 意图账本）
  全在 `08_hot_registry_eviction_evidence.md`。
- 面积读数：dead/ 语料 **541 袋**袋内含热册文件；`batch_creation_tokens.py` 写前自检在陈旧快照期**全域拒写**（原文摘录在册）。

## 附带指路（不另立题）

- F-1 十二把回归尺的 blob 源材料：`06_f1_ruler_blob_sources.yaml`（15 把尺 × 394 条位点，含 sha256）。

---

## 追加交割（Owner 批文 2026-10-09）：G1+G3 = 图9/四图族 24 袋 → 车道 B/B-1 并袋三方合并

- 生成锚点 HEAD=`f4190db9ef33`；批文原文：「40 件全批 A：G1+G3 交总队并袋，其余专车直投；G9/G10 也 A」
- **为什么必须并袋**：G1 20 件全部改同一文件 `config/strategy_production_map.yaml`（跨 st-map9-chief / st-cure-p01 / st-map9-f4 三班接力，互为重投后继）；G3 4 件改四张图册。同文件多班各投＝互相回退，须由车道 B 做**统一三方合并**（并与 B-1 的 b-606 分支面合流）。
- 本专案动作：**只交割不直投**；24 袋留 dead/ 原位（一步 `requeue --from-bag` 通道不断），逐件 blob 与 sha256 如下。

### 逐件面（按未落地文件去重：同一路径取最新袋）

**G1（20 袋）**
**G3（4 袋）**
- `config/data_supply_chain_map.yaml` ← 袋 `q-20261008-st-gomap-chief-20261004-0035`（st-gomap-chief-20261004，2026-10-08T05:57，组 G3）
  - blob：`blobs/a980bd9c338b3898796585780ac24b95707ac2b2a40c937e998f0e31a5cca851`｜sha256 `a980bd9c338b389879658578…`｜blob 在盘=True
  - 原文要点：[st-gomap-chief-20261004][全流通L1+L2新袋] 吸收施工(boot_hooks自检+budget不变式)+六图族批(GOMAP终刷423+DSC四字段全满+SPM编码归一+图16立法边+图11入边+panorama);12件从b-606工作树快照;ghost/NOQA连环
- `config/dev_delivery_map.yaml` ← 袋 `q-20261008-st-gomap-chief-20261004-0035`（st-gomap-chief-20261004，2026-10-08T05:57，组 G3）
  - blob：`blobs/1ac5125aa6355184adbc26345ff9e7f6d8f1c99021dd52a510e9839e160724e7`｜sha256 `1ac5125aa6355184adbc2634…`｜blob 在盘=True
  - 原文要点：[st-gomap-chief-20261004][全流通L1+L2新袋] 吸收施工(boot_hooks自检+budget不变式)+六图族批(GOMAP终刷423+DSC四字段全满+SPM编码归一+图16立法边+图11入边+panorama);12件从b-606工作树快照;ghost/NOQA连环
- `config/governance_legislation_map.yaml` ← 袋 `q-20261008-st-gomap-chief-20261004-0035`（st-gomap-chief-20261004，2026-10-08T05:57，组 G3）
  - blob：`blobs/8f93d14566fd8fc2bdc4642b5ebde5782851e237e1981630a2e457b6ccc2d399`｜sha256 `8f93d14566fd8fc2bdc4642b…`｜blob 在盘=True
  - 原文要点：[st-gomap-chief-20261004][全流通L1+L2新袋] 吸收施工(boot_hooks自检+budget不变式)+六图族批(GOMAP终刷423+DSC四字段全满+SPM编码归一+图16立法边+图11入边+panorama);12件从b-606工作树快照;ghost/NOQA连环
- `config/governance_operations_map.yaml` ← 袋 `q-20261008-st-gomap-chief-20261004-0035`（st-gomap-chief-20261004，2026-10-08T05:57，组 G3）
  - blob：`blobs/628c1825fb2d3d80e8b2168791902d8ed55a36b05d918a7db1bb6882a349085e`｜sha256 `628c1825fb2d3d80e8b21687…`｜blob 在盘=True
  - 原文要点：[st-gomap-chief-20261004][全流通L1+L2新袋] 吸收施工(boot_hooks自检+budget不变式)+六图族批(GOMAP终刷423+DSC四字段全满+SPM编码归一+图16立法边+图11入边+panorama);12件从b-606工作树快照;ghost/NOQA连环
- `config/panorama_master_map.yaml` ← 袋 `q-20261008-st-gomap-chief-20261004-0035`（st-gomap-chief-20261004，2026-10-08T05:57，组 G3）
  - blob：`blobs/c7f99b5e3ec43ac352e2c753e0f50928d6af8aa22f88d64823e4056cad5eda19`｜sha256 `c7f99b5e3ec43ac352e2c753…`｜blob 在盘=True
  - 原文要点：[st-gomap-chief-20261004][全流通L1+L2新袋] 吸收施工(boot_hooks自检+budget不变式)+六图族批(GOMAP终刷423+DSC四字段全满+SPM编码归一+图16立法边+图11入边+panorama);12件从b-606工作树快照;ghost/NOQA连环
- `config/strategy_production_map.yaml` ← 袋 `q-20261008-st-map9-chief-20261008-0009`（st-map9-chief-20261008，2026-10-08T21:02，组 G1）
  - blob：`blobs/c4f96ddcf13642cfb9e826abfd0e88f98f960aa6621c198767f080eb67d7ade3`｜sha256 `c4f96ddcf13642cfb9e826ab…`｜blob 在盘=True
  - 原文要点：[st-map9-chief][图手术终版+ownership册再生成·重投] 替死袋 0006：FAC-E1F 车道节点晨间风暴被回滚后重补（2.4 欠账销账第三次）+14 术式手术面（E7M008→INF-072 等，盘面幸存）+ownership 再生成（t0 三件户口+八台归属）——vali
- `docs/03_modules/path_ownership_map.yaml` ← 袋 `q-20261008-st-map9-chief-20261008-0009`（st-map9-chief-20261008，2026-10-08T21:02，组 G1）
  - blob：`blobs/aaec9b25e90cf543621be58104edff65d580549297b71b68fa83fd845f2563bd`｜sha256 `aaec9b25e90cf543621be581…`｜blob 在盘=True
  - 原文要点：[st-map9-chief][图手术终版+ownership册再生成·重投] 替死袋 0006：FAC-E1F 车道节点晨间风暴被回滚后重补（2.4 欠账销账第三次）+14 术式手术面（E7M008→INF-072 等，盘面幸存）+ownership 再生成（t0 三件户口+八台归属）——vali

- 去重后待合并真源文件数：**7**；袋数 **24**。
- 取回式样：`python -c "import pathlib,hashlib;b=pathlib.Path('.runtime/commit_queue/<blob_ref>').read_bytes();assert hashlib.sha256(b).hexdigest()=='<sha256>';open('<path>','wb').write(b)"`
- 合并纪律：以 HEAD 现值为基，逐术式（applied/kept 计数、FAC-E1F、2.4 欠账、ownership 册）行级并入，**禁整档快照覆盖**；投前先跑 `validate_strategy_production_map.py`（须 PASS nodes=341 或按当期在册数）+ ALGO-NOTE-SYNC 同日戳。
