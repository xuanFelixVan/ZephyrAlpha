# NOTE(P2W02): 并行会话 scaffold 时 eager import 可能先于类落地致包门面断链；
# 按 data_eng/__init__.py 在案可逆模式改守卫式导入（目标类落地即自愈）。
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_data_security/algo_flow/data_security__init__.yaml
"""

try:
    from zephyr.data_security.ai_masking_pipeline import AiMaskingPipeline
except ImportError:
    AiMaskingPipeline = None  # type: ignore[assignment]
try:
    from zephyr.data_security.data_access_auditor import DataAccessAuditor
except ImportError:
    DataAccessAuditor = None  # type: ignore[assignment]
try:
    from zephyr.data_security.data_masking_engine import DataMaskingEngine
except ImportError:
    DataMaskingEngine = None  # type: ignore[assignment]
# [BLUEPRINT] MOD-DATA_SEC | (pending)
# [MODULE] zephyr.data_security
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DATA_SEC | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2
[DEPRECATED] 2026-09-29 夜战 SW5（st-nightsweep-sw5-20260929）依 F128 案卷
    （docs/_working/fullconnect_campaign/k_frontend_docs/12_f128_data_security_masking.md）
    定罪：三件实体（data_masking_engine/data_access_auditor/ai_masking_pipeline）
    生产面零 import（AST PROD=0，连 TYPE_CHECKING 腿都无）、零动态挂载、零计划任务
    → 纯装饰，退役标记。
    successor：无直接继任——F88 LSG（LLM 输入输出防御）与 F105（密钥治理）经实核
    异域不同对象，不覆盖列级脱敏/访问审计能力；能力空缺语义转 known-gap 登记。
    是否补接线（LSG l1_input 前置+数据出口）或物理净删 = OWNER-GATE 登记，
    物理净删未执行。M1 机采 SourceType 消费腿经实核为同名假阳性（l1_input 自有枚举）。
    恢复条件：Owner 判"补接线"则撤销本标记，按 F128 缺1 先红样后接线。


# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = []

__all__.append("AiMaskingPipeline")

__all__.append("DataAccessAuditor")

__all__.append("DataMaskingEngine")
