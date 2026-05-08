---
task_id: "TASK-INF-0220"
source_blueprint: "MOD-INF-011"
source_section: "§15 第三轮深度交叉审计——6大维度19盲点 (V-VMS-601~619)"

title: "R3 盲点关闭——19 项 API设计DX/向量可调试性/多模态嵌入质量/测试隔离/环境一致性/错误恢复粒度盲点"
description: |
  关闭蓝图 §15 第三轮审计产生的全部 19 个盲点 (V-VMS-601 ~ V-VMS-619)：
  R. API设计模式与开发体验 (4): V601 API版本化承诺 / V602 sync/async明确决策 / V603 空结果vs错误语义区分 / V604 幂等commit_strategy
  S. 向量数据可调试性 (3): V605 向量检视器 / V606 检索过程重放 / V607 嵌入差异对比
  T. 多模态嵌入质量 (4): V608 中英混合语料验证 / V609 极端短文本对策 / V610 Unicode规范化 / V611 Code+NL混合分块
  U. 测试替身与隔离 (3): V612 FakeVMS / V613 DeterministicEmbedder / V614 性能回归基准
  V. 环境一致性 (3): V615 VMS配置Schema / V616 dev/prod分离 / V617 模型文件SHA256校验
  W. 错误处理与恢复 (2): V618 VMS异常分层体系 / V619 异常消息中的恢复建议
  每个盲点在对应模块中关闭——代码注释 # closes V-VMS-6XX
  P0 8盲点优先关闭：V601/V602/V605/V608/V609/V615/V618
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vms_schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "追加 closes V601(API版本化@api_version装饰器)/V602(async公共API)/V603(空结果None vs VMSUnavailableError区分)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vms_schemas.py"
    description: "追加 closes V618(VMS异常分层:VMSError→VMSUnavailableError/VMSDataError/VMSConfigError/VMSAuthError) / V619(异常suggestion字段)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    description: "追加 closes V605(向量检视器 inspect <vector_id>)/V607(嵌入差异对比 embed_diff)/V608(100条中英混合test embeddings)/V609(短文本检出→语义上下文句嵌入)/V610(Unicode NFKC规范化)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_memory_fake_vms.py"
    description: "追加 closes V612(FakeVMS—in-memory dict存储+伪向量生成MakeDeterministicEmbedder)"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
    description: "追加 closes V613(DeterministicEmbedder for unit tests)/V614(性能benchmark regression)"
  - path: "D:\\ZephyrAlpha\\config\\vms\\vms_config.yaml"
    description: "追加 closes V615(pydantic配置Schema校验)/V616(VMS_ENV=dev|prod路径切换)/V617(模型文件SHA256校验)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\chunk_strategy_router.py"
    description: "追加 closes V611(Code Block+Markdown混合分块—ast-aware处理Python+Markdown语义混合)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vms_schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_memory_fake_vms.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\chunk_strategy_router.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
  - "D:\\ZephyrAlpha\\config\\vms\\vms_config.yaml"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——VMS异常分层体系(VMSError基类) / V615 vms_config Schema"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "config/vms/ 路径合规——VMS配置文件存放"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§15 R3 19盲点——API设计/向量调试/嵌入质量/测试隔离/环境一致性/错误粒度完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "全部 19 个盲点 V-VMS-601 ~ V-VMS-619 在对应模块中有 # closes V-VMS-6XX 注释"
  - "V601 closed: @api_version('1.0') 装饰器注册 InProcessVectorMemory 版本"
  - "V602 closed: async def search_async() 公共API + search_sync() 便 wrapper——CE集成使用async路径"
  - "V605 closed: python -m zephyr.vector_memory inspect <id> 输出原始内容/嵌入时间/provenance链/相似邻居top-5/Collection统计位置"
  - "V608 closed: 100条中英混合语料测试集 embedded → 同义判别准确率输出人工reviewable report"
  - "V609 closed: 检测短文本(<10字符)→ 嵌入其语义上下文句（从WriteTrace提取父级context）"
  - "V610 closed: 写入前 Unicode NFKC 规范化 + 全角→半角转换 + 去除零宽控制字符"
  - "V612 closed: FakeVMS 可替代真实 VMS——供 CE/Orc/FLE 单元测试使用"
  - "V615 closed: vms_config.yaml Pydantic Schema 校验——启动时 fail-fast 报告缺失配置"
  - "V618 closed: VMSError 异常分层——VMSUnavailableError(可重试) / VMSDataError / VMSConfigError / VMSAuthError"
  - "V619 closed: 异常消息包含 'suggestion: Wait 30s or run `vms health`'"

rollback_instructions: |
  1. @api_version 装饰器导致调用方版本冲突 → 增加 v1→v2 兼容适配（不撤销装饰器）
  2. 异常分层体系过于细导致捕获取舍错误 → 先回退到通用 VMSError → 逐步还原
  3. FakeVMS 行为与真实 VMS 不一致→记录差异并在 CI warning（不阻碍False negative）

depends_on:
  - "TASK-INF-0219"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
  - "governance"
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
