---
ttl: task_bound
completes_when: 施工总队按工单恢复 tests 树并逐族跑出绿色读数后闭环
---
# P0 · tests 树被删而未补：HEAD 缺 ≈2,200 件测试，内容真身在死信袋里（零考古可恢复）

## 一、事实链（逐条实测，命令可复跑）

1. 2026-10-05 commit `6324c9e0f6f`（st-tests-chief-20261004「旧路径删除袋1/3」）删除 `tests/` 下 129 旧一级目录，
   正文自述 **"内容真身=终装袋 0030-0044 新路径面……内容零删失"**。
2. 实测 HEAD(dev) `tests/`=**2003** 件；该删除提交父树 `tests/`=**4089** 件。
   按字节对拍：删除前内容今天仍在 HEAD 任意路径的只有 **407 件(10%)**；再按 basename 兼容改名计 1593 件；
   **余 2089 件字节与同名皆无＝彻底不在盘面**（含 `tests/ai/test_l08_human_ai_interface.py`、
   `tests/ai_layer/redline/test_sev_router.py`、`tests/data/data/test_news_collector.py` 等，逐条见清单）。
3. 它点名的"终装袋 0030-0044"**整批躺在 dead/**：tests-chief 族 159 袋合计 22,663 个 absent_in_head 文件条目。
4. 全语料去重后 HEAD 现缺且从未在任何 ref 出现过的路径=**2,456 件**，其中 tests/ **2,203 件**
   （tests/gov 1322｜tests/research 394｜tests/infra 208｜tests/data 128｜tests/ai 108）。
5. 从死信 blob 可恢复的缺失测试路径=**2,325 件**；来源不止 tests-chief：
   st-cure-p05 717／p05b 563／p10 461／p01 250／p09 159／p12b 111（=10-06 清偿战役重投班自己死成死信）。

## 二、可恢复性实测（本专案已跑，非推演）

- blob 取回逐件 sha256 自校验 + `py_compile`：2,325 件 **ok=2,324 fail=1**。
- 60 件随机 pure-move 落主区未跟踪态跑 `pytest --collect-only -q -c py.ini`：**289 items collected，0 collect error**。
- 同 60 件实跑：ERROR 集中 **1 件**（`tests/gov/governance/meta_question/test_exam_loop_writeback.py`，夹具依赖 PG/live 账本），其余 59 件无 import/collection 故障。
- 门禁试点（7 件 `tests/gov/governance/d5_architecture/`）`gate_prerun`：**内容硬阻断仅 CLAIM-REQUIRED 1 条（程序性）**；
  DOC-HEADER-SUITE/MODULE-ID/CLONEGUARD/CAPABILITY-OVERLAP/IMPORT-INTEGRITY 全 PASS；环境信号 COMMIT-SCOPE 以 `--allow-multi-domain` 留痕可通。

## 三、本专案为何不直接落地（诚实申报，非偷懒）

控制实验：主区对 HEAD 已有的同目录文件跑 collect，**HEAD 自身在该目录已有 1 件 collection ERROR**
（`test_generate_backtest_coverage_ledger.py` ModuleNotFoundError）→ "恢复即绿"不成立，需逐族修 sys.path/import。
开工总纪律 #6「先对 HEAD 跑绿才投」优先于"清零数字"：盲投 2,325 件未跑绿测试=把红灯引进全量测试面，属连坐扩面。

## 四、工单（车道F 零考古起点）

1. 清单：`.runtime/tmp/st-deadcure-20261009/common/tests_restore_manifest.json`
   —— 每件含：缺失新路径／可提供它的最新死信袋 qid／blob_ref+blob_sha256／与删除前原文谱系分类。
2. 三档优先级：**pure_move 313**（逐位等于删除前原文，最无争议，先补）→ **edited_move 1,843**（搬家时改过 import，须族内跑绿）→ **novel 52**（全新测试，无原文可对拍，须单独判）。
3. 配方：按族每袋 ≤300 件 → blob 取回落新路径 → `lock_files.py acquire` 逐件 claim → `gate_prerun` 到内容硬阻断 0 →
   `commit_queue.py enqueue --session <活sid> --worktree-root <车道>` → 落地后 `git show HEAD:<path>` 验真 + 族内 pytest 实跑读数入台账。
4. 禁止项：**禁对这批袋 `requeue --from-bag` 整袋盲重投**（大袋同时含 content_diff 件，盲投回退 HEAD 已演进内容——
   本专案实测 1,397 袋属此回归风险，占存量 82%）；禁清 `blobs/`；禁把 `.corrupt-husk` 当证据。
5. 配套：`common/f1_ruler_sources.json`=车道F 十二把回归尺的 blob 源材料指路（394 条目/15 把尺）。
