---
task_id: "TASK-KB-0015"
source_blueprint: "MOD-KB-001"
source_section: "§5.11 五轨并行知识提取管道"

title: "五轨并行知识提取管道实现——Session Log→门禁阻断→决策记录→外部知识→差距巡检 五条自动管道"
description: |
  实现蓝图 §5.11 定义的五轨并行提取管道：(1)安装 install-hooks.py——自动安装 git post-commit hook（Session结束→auto-handoff-log.py 生成→知识切片→G1-G5→KE/KO）+ git pre-commit hook（阻断stderr→自动解析 FailureSignature→创建 KO A4 failure_pattern）；(2)实现 externals_detector.py——用 ARXIV_PATTERN / GITHUB_PATTERN regex 扫描 session log body→自动检测学术/GitHub链接→D0 四轮流水线 011 GLM→022 Kimi→033 Qwen→044 Opus→推送 Owner 审批 yes/no；(3)实现 decision_signal_detector.py——决策短语检测器：从聊天内容捕获"我们决定用X替代Y"→自动路由到轨道3→G1-G5入库。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\batch_ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\install_hooks.py"
    description: "新建——自动安装 post-commit hook（触发轨道1）+ pre-commit failure capture（触发轨道2）+ hook健康验证"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\externals_detector.py"
    description: "新建——扫描 session 日志body中的 arXiv/GitHub 链接→fetch_arxiv/fetch_github_readme→D0流水线→push owner审批"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decision_signal_detector.py"
    description: "新建——决策信号检测器——短语模式匹配：'我们决定'/'选X替代Y'/'ADR-XXX→ACCEPTED'→自动路由轨道3→KE入库"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\install_hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\externals_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decision_signal_detector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\.git\\hooks\\**"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2 模型"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建 .py 路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.11 完整定义五轨流程 + §5.13.2 三个触发器工程细节伪代码"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 60

acceptance_criteria:
  - "install_hooks.py 执行后 .git/hooks/post-commit 和 .git/hooks/pre-commit 文件存在且可执行"
  - "pre-commit hook stderr 被解析为 FailureSignature(error_type/root_cause/fix_method/time_cost_minutes) →自动存入 KO A4 failure_pattern"
  - "externals_detector.py 的正则 ARXIV_PATTERN 能匹配 https://arxiv.org/abs/2312.xxxxx"
  - "externals_detector.py 的 GITHUB_PATTERN 能匹配 https://github.com/owner/repo"
  - "auto_ingest_external() 抓取失败→静默跳过（不打扰Owner）"
  - "D0 产出 ko_drafts 非空→push Owner 'yes/no'"
  - "Owner 7d无回复→ko_drafts 自动过期清理"
  - "decision_signal_detector 能检测 '我们选X替代Y'/'ADR-XXX status→ACCEPTED'/bp version bump"

rollback_instructions: |
  1. 删除 src/zephyr/kb/install_hooks.py, externals_detector.py, decision_signal_detector.py
  2. 若 hooks 已安装——手动恢复 .git/hooks/ 到 install_hooks.py 执行前状态
  3. 若 KO 已产生——DELETE FROM knowledge_entries WHERE source_type='external_detect'

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
