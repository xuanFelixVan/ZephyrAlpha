---
created: 2026-09-30
ttl: task_bound
title: 图书馆#460 ②施工簿（A4 车道 st-circ-a4-20260930）
session: st-circ-a4-20260930
---

# 裁定#460 第②步施工台账（图书馆总口审计闭环）

> 骨架=00_skeleton.md 第3批（A4）。能力反查审计：`.runtime/lookup_audit/st-circ-a4-20260930.jsonl`
> （tool=capability_lookup.find，query="library lookup"）。claim 三件在册（lookup.py/SOP/canonical 册）。

## 四件套落地明细

1. **lookup `--session` 审计**：`src/zephyr/library/lookup.py`
   - `--session` 参数定义 :407-411；main() 审计接入 :413-433（四面 dispatch 收集 face/result_count，session 非空才调 `_write_cli_audit` :432）；`_write_cli_audit` :354-376（懒加载复用 `zephyr.governance.capability_lookup.write_lookup_audit_log`（真身 :297，capability_lookup.py:941 同款调用面），tool="zephyr.library.lookup"，双层 fail-open：被复用函数自身吞写入异常+本侧兜 import 失败）；`_run_main_query` 改返 `(rc, rows)` :314-350（退出码语义零变化，行列表供 result_count；全仓唯一调用面=main()，grep 实证）。
   - 无 `--session` 行为零变化（测试①锁定）；四面留痕 face 标记 main/backtest/feeds/commit_guide。
2. **copilot-instructions**：`.github/copilot-instructions.md`（5 行指针：AGENTS.md→llms.txt→FRONT_DOOR→lookup 总口→git_commit.py 正门；头格式对标 CODEOWNERS 注释头）。
3. **能力卡 #45**：`data/capability_cards/library_lookup.yaml`（字段结构照抄 embedding_router.yaml：module_id=MOD-LIB-003/capability_id=library-lookup/description/examples/input_schema+治理锚定头；yaml.safe_load 验过）。
4. **SOP 第四口**：`docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md` :891（A.3.1 三重验证下插一行子弹：图书馆总口必过；其余零触碰）。

## CREATE-GUARD 登记（canonical 册 creation_tokens，safe_write_text CAS 三枚）

- `data/capability_cards/library_lookup.yaml` → circ-a4-library-lookup-card-20260930
- `.github/copilot-instructions.md` → circ-a4-copilot-instructions-20260930
- `docs/_working/total_circulation_night/s3_library_step2.md` → circ-a4-library-step2-ledger-20260930
- 均带 merge_evaluation（#375 内收判据）；登记走外科脚本非 batch_creation_tokens.py（该脚本 .github 前缀会误吞 5 个存量未登记件，dry-run 实证弃用）。

## 测试读数

- 新增 `tests/library/test_lookup_session_audit.py` 6 例（零变化/留痕内容/fail-open/空白 session/零命中留痕/backtest face）全绿。
- `pytest tests/library/` = 199 passed / 2 failed / 4 skipped；43 例定向回归（session_audit+tombstone+entry_equivalence+smoke）全绿。

## 偏差与移交（非本车道修，登记让位）

1. **test_lookup_import_surface 2 败=环境漂移非本袋**：`-X importtime` 实测带 usercustomize=3706ms/1070 模块、`PYTHONNOUSERSITE=1`=373ms/282；gate_engine/defense_runner 重件 9 处命中全部经 usercustomize（LSG runtime_interceptor 引导链），禁用即 0 命中。HEAD 版 lookup.py 同机实测 448-845ms 同爆 220ms 预算（基线 2026-09-27 早于 usercustomize 落地+今夜多会话高负载）。处方归 usercustomize/基线册 owner：基线复测需 `PYTHONNOUSERSITE=1` 或基线口径含 site 引导。
2. **canonical 册连坐披露**：册文件含 st-menu-t1b1-20260930 staged 3 枚 token（quality 包迁址），同文件无法拆 hunk，本袋提交将连带落地；队列侧衍生漂移已有容忍（§2.6），落地后以 `git log -1` 核实归属披露。
3. 宪法 AGENTS.md 本夜等长替换在队（q-20260930-st-libuniv-0001），本车道零触碰。

## 执行留痕

- commit：见本文件同批 git_commit.py 落地记录（skeleton 00_skeleton.md 第3批 A4 行同步补 hash）。
