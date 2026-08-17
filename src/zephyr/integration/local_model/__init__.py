# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md
# [MODULE] zephyr.integration.local_model
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cache_layer 子模块符号 1个
#   fields: CacheLayer
#   code: zephyr.integration.local_model.cache_layer
# - id: I2
#   name: deepseek_chat 子模块符号 1个
#   fields: DeepSeekChat
#   code: zephyr.integration.local_model.deepseek_chat
# - id: I3
#   name: embedding_router 子模块符号 1个
#   fields: EmbeddingRouter
#   code: zephyr.integration.local_model.embedding_router
# - id: I4
#   name: local_model_scheduler 子模块符号 1个
#   fields: LocalModelScheduler
#   code: zephyr.integration.local_model.local_model_scheduler
# - id: I5
#   name: ollama_chat 子模块符号 1个
#   fields: OllamaChat
#   code: zephyr.integration.local_model.ollama_chat
# - id: I6
#   name: ollama_embedding 子模块符号 1个
#   fields: OllamaEmbedder
#   code: zephyr.integration.local_model.ollama_embedding
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.integration.local_model.__init__
#   intro: MOD-INF-042 包入口
#   desc: MOD-INF-042 包入口，包级聚合再导出并声明 __all__（12项）
#   inputs: I1 I2 I3 I4 I5 I6
#   outputs: zephyr.integration.local_model 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（12项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.integration.local_model 包公共 API
#   name_en: __all__ 12项
#   intro: MOD-INF-042 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I5 --> A1
# I6 --> A1
# A1 --> O1
"""

from zephyr.integration.local_model.cache_layer import CacheLayer
from zephyr.integration.local_model.embedding_router import EmbeddingRouter
from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler
from zephyr.integration.local_model.ollama_chat import OllamaChat
from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder
from zephyr.integration.local_model.deepseek_chat import DeepSeekChat

__all__ = [
    "CacheLayer",
    "EmbeddingRouter",
    "LocalModelScheduler",
    "OllamaChat",
    "OllamaEmbedder",
    "DeepSeekChat",
    "cache_layer",
    "embedding_router",
    "local_model_scheduler",
    "ollama_chat",
    "ollama_embedding",
    "deepseek_chat",
]
