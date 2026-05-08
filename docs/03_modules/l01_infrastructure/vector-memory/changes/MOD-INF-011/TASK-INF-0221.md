---
task_id: "TASK-INF-0221"
source_blueprint: "MOD-INF-011"
source_section: "§16 外部取证专家级终极审计 R4——6项致命漏洞 (F-VMS-701~706)"

title: "R4 致命漏洞关闭——嵌入质量实证/降级逃生舱/金丝雀验证/领域感知衰减/对抗投毒防御/系统自解释"
description: |
  关闭蓝图 §16 第四轮外部取证审计产生的 6 项致命漏洞 (F-VMS-701 ~ F-VMS-706)：
  F1 (致命): **嵌入质量领域假设未经实证验证**——BGE-M3 对 ZephyrAlpha 金融量化中文混合语料嵌入质量完全未经实证
    → 取 30 对等价对 + 30 对非等价对 → BGE-M3 embed → 计算 cosine similarity → 等价对 > 0.85 / 非等价对 < 0.5 → 差异显著 → 输出 EmpathyValidationReport
  F2 (致命): **无检索降级逃生舱**——VMS 是 AI 的唯一记忆通道但无检索质量降级替代方案
    → search() 返回结果 score < 置信度阈值 → AI 自动降级到：1) ripgrep 精确扫描 2) 直接读 AGENTS.md/蓝图原始 Markdown 3) 提示 Owner 4) 标记当前 session "VMS信任度"=LOW
  F3 (严重): **无部署/迁移前后回归金丝雀验证**——迁移前后 NDCG@5 比较无人执行
    → 50 条标准查询 snapshot Q_before → 迁移后 Q_after → NDCG@5 下降 > 10% → 迁移失败告警 / NDCG@5 上升 > 5% → 迁移成功
  F4 (严重): **知识衰减速率非领域感知**——统一衰减 λ 对所有 Collection 一视同仁
    → 每 Collection 独立 decay_rate: knowledge(0.02/day) / lessons(0.005/day) / decisions(0.003/day) / rules(0.0001/day)
  F5 (致命): **无对抗性检索投毒评估**——VMS 的排序完整性无防御机制
    → 写入时检测新向量是否异常接近现有高排名向量(similarity>0.99)→mark suspicious / MMR diversity排序 / periodic poisoning audit / 来源交叉验证
  F6 (严重): **无系统自解释与继承能力**——bus factor=1 终极继承问题
    → python -m zephyr.vector_memory describe / inheritance-guide.md(50行) / 设计决策-ADR-盲点编号链路追溯
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_quality_validator.py"
    description: "F1实证验证器——运行30+30等价/非等价对嵌入质量测试 + 输出 EmbeddingQualityValidationReport"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "追加 closes F2(检索降级逃生舱 search_degraded) / F3(金丝雀验证 canary_verify) / F4(领域感知衰减 per_collection_decay)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
    description: "追加 closes F4(Collection级decay_rate配置) / F5(投毒检测 detection_on_write)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
    description: "追加 closes F5(定期投毒审计 periodic_poisoning_audit)"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\inheritance-guide.md"
    description: "F6继承手册——VMS角色/8Collection/运行验证/影响分析/先修方案（50行以内）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_quality_validator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\inheritance-guide.md"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——EmbeddingQualityValidationReport / PoisoningScanResult / CanaryVerificationReport"
  - module_id: "ADR-0016"
    section: "§3"
    reason: "BGE-M3 embedding production contract——等价/非等价对测试的基线"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§16 F1-F6 6项致命漏洞完整定义——每项含漏洞本质/触发场景/前三轮覆盖状态/独立取证测试方案"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 25000
timeout_minutes: 120

acceptance_criteria:
  - "F1 closed: embedding_quality_validator.py 可独立运行——30+30对测试集嵌入→输出 report 含 avg_equiv_similarity/avg_non_equiv_similarity/discrimination_margin"
  - "F1 report: equiv 对平均 sim > 0.85 AND non-equiv 对平均 sim < 0.5 → PASS / 否则 WARNING"
  - "F2 closed: search_degraded(trigger: score_threshold_low) → 自动降级到 ripgrep 精确扫描 + 标记 session VMS_TRUST=LOW"
  - "F3 closed: canary_verify(): 50条查询 snapshot Q_before → Q_after → NDCG@5 变化 > -10% → ALARM"
  - "F4 closed: hybrid_retriever 在 RRF 阶段使用 Collection-dependent decay_rate: rules=0.0001/day, knowledge=0.02/day, lessons=0.005/day, decisions=0.003/day"
  - "F5 closed: 写入新向量时检测 similarity > 0.99 adjacency → mark suspicious + 不参与排序(disable_from_search temporarily)"
  - "F5 closed: periodic_poisoning_audit()——每月扫描 VMS 检测垄断排名（某向量对 N 个查询 rank=1）"
  - "F6 closed: python -m zephyr.vector_memory describe 输出 VMS self description"
  - "F6 closed: inheritance-guide.md 包含 50行以内继承人快速理解 VMS 的内容"
  - "F6 closed: 每个 design decision 在代码注释中链接到对应 ADR/盲点编号"

rollback_instructions: |
  1. F1 实证失败（等价对相似度不足）→ VMS 仍然可运行但设置 VMS_EMBEDDING_QUALITY=UNVERIFIED → 所有检索结果 trust_decay 额外降低 20%
  2. F2 逃生舱不触发 → 手动设置 VMS_TRUST=LOW 触发降级模式
  3. F5 投毒检测误杀正常数据 → 将 suspicious_flag=False → review队列归零
  4. 还原各模块文件至 R3 完成版本 → 删除 embedding_quality_validator.py / inheritance-guide.md
  5. 每个致命漏洞有独立 feature flag: VMS_FLAG_{F-VMS-70X}=enabled|disabled

depends_on:
  - "TASK-INF-0220"
blocked_by: []
status: "created"

tags_fn:
  - "infra"
  - "data"
  - "governance"
  - "security"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
