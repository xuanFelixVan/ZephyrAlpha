---
task_id: "TASK-KB-0033"
source_blueprint: "MOD-KB-001"
source_section: "§12 施工指引 + §12.5 E2E测试约定"

title: "施工指引执行工具开发——easy_validate/quick_lookup/snippet_builder + E2E端到端测试全体系"
description: |
  实现蓝图 §12 定义的三项施工工具 + §12.5 E2E测试约定：(1)easy_validate.py——一键验证所有KE的完整性——扫描MD files(必填字段完整/body长度200-2000/分类一致)→输出 report.txt + MARK 哪些KE需要人工复审；(2)quick_lookup.py——按category查KE + 快捷 list→JSON/YAML output→`python -m src.zephyr.kb.quick_lookup --category A2 --format yaml`；(3)snippet_builder.py——从KE文本提取"代码片段 block"→构建Python代码补全——输出 think_block（不是要生成而是摘取原 KE 中的 code fences）；(4)§12.5 E2E端到端测试全体系——tests/e2e/目录含4个测试文件 + Golden Dataset(10条GQ-001~010) + 3个session_log_fixture + CI workflow(.github/workflows/kb-e2e.yml) + eval_harness(可独立运行)。6场景覆盖矩阵：全链路G1→G5 | G1→G5+recall | 噪音过滤 | 冷启动引导 | 事务回滚 | Golden Dataset回归。RAGAS指标：per-query min_context_precision≥0.60~0.70（对齐蓝图 §12.5 Golden Dataset定义）。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\easy_validate.py"
    description: "新建——一键validator——扫描全KE→输出report.txt"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\quick_lookup.py"
    description: "新建——category→JSON/YAML 快捷查询"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\snippet_builder.py"
    description: "新建——摘取KE中的code fences→拼接成think_block"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\eval_harness.py"
    description: "新建——E2E评估工具——python -m zephyr.kb.eval_harness --golden tests/e2e/golden_dataset/queries.yaml"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\conftest.py"
    description: "新建——E2E fixtures：临时ChromaDB+SQLite+MD环境"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\test_full_pipeline.py"
    description: "新建——全链路G1→G5→recall闭环测试"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\test_bootstrap_pipeline.py"
    description: "新建——冷启动引导全链路测试（§4.5）"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\test_batch_rollback.py"
    description: "新建——事务写入+回滚全链路测试（§7.9）"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\queries.yaml"
    description: "新建——Golden Dataset：10条{query, expected_ke_ids, min_context_precision}"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\session_log_fixtures\\session_bugfix.md"
    description: "新建——bug修复session fixture"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\session_log_fixtures\\session_decision.md"
    description: "新建——架构决策session fixture"
  - path: "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\session_log_fixtures\\session_chat.md"
    description: "新建——噪音对话session fixture"
  - path: "D:\\ZephyrAlpha\\.github\\workflows\\kb-e2e.yml"
    description: "新建——KB E2E CI workflow（on push paths: src/zephyr/kb/**, docs/08_knowledge/**, tests/e2e/**）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\easy_validate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\quick_lookup.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\snippet_builder.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\eval_harness.py"
  - "D:\\ZephyrAlpha\\tests\\e2e\\conftest.py"
  - "D:\\ZephyrAlpha\\tests\\e2e\\test_full_pipeline.py"
  - "D:\\ZephyrAlpha\\tests\\e2e\\test_bootstrap_pipeline.py"
  - "D:\\ZephyrAlpha\\tests\\e2e\\test_batch_rollback.py"
  - "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\queries.yaml"
  - "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\session_log_fixtures\\session_bugfix.md"
  - "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\session_log_fixtures\\session_decision.md"
  - "D:\\ZephyrAlpha\\tests\\e2e\\golden_dataset\\session_log_fixtures\\session_chat.md"
  - "D:\\ZephyrAlpha\\.github\\workflows\\kb-e2e.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§12 施工工具定义 + §12.5 E2E测试约定—— RAGAS指标 85%+ >50 KB KEs benchmark"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 18000
timeout_minutes: 60

acceptance_criteria:
  - "easy_validate.py——扫描全KE——输出 report.txt——✓ valid / ⚠ human_review——标注具体不符合项"
  - "quick_lookup.py `--category B4`→JSON 输出 {'results':[{KeEntry}]}"
  - "snippet_builder.py 提取 code fence (```python...```) → ignore 非python fences"
  - "E2E场景1 全链路G1→G5——python -m pytest tests/e2e/test_full_pipeline.py -v——输入session_bugfix.md → 产生≥1条VERIFIED KE"
  - "E2E场景2 G1→G5+recall——输入session_decision.md → recall可检索新KE → Context Precision≥0.60"
  - "E2E场景3 噪音过滤——输入session_chat.md → 新KE数量<3（85%对话应为噪音）"
  - "E2E场景4 冷启动引导——空ChromaDB+空SQLite → bootstrap产生≥10 KE → MVKB三项全满足"
  - "E2E场景5 事务回滚——50条含1条恶意KE的batch → 全部回滚 → batch status=ROLLED_BACK"
  - "E2E场景6 Golden Dataset——python -m zephyr.kb.eval_harness --golden tests/e2e/golden_dataset/queries.yaml——10条查询全链路输出一致→回归无退化"
  - "CI workflow——.github/workflows/kb-e2e.yml——on push to kb/**→自动运行全E2E套件" 

rollback_instructions: |
  1. 删除 src/zephyr/kb/easy_validate.py, quick_lookup.py, snippet_builder.py, eval_harness.py
  2. 删除 tests/e2e/ 整个目录
  3. 删除 .github/workflows/kb-e2e.yml

depends_on: ["TASK-KB-0011"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
