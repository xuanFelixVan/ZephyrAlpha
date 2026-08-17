# [TTL] permanent
"""

[A_module] module_id=MOD-BT-001 | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable

ZephyrAlpha — D_BACKTEST 回测引擎域

SSoT: docs/03_modules/_domain_backtest/blueprint.md (MOD-BT-001)

架构归属: D_BACKTEST域 (depgraph编号24)
架构决策: 回测引擎统一归口D_BACKTEST,消除research/intelligence/rollback多处置放

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: engine_base 引擎基类符号（类对象）
#   fields: BacktestEngineBase + BacktestResult + FactorDiscovery 三个类
#   code: zephyr.backtest.core.engine_base（__init__.py L11-15）
# - id: I2
#   name: vectorized_engine 向量化引擎符号（类对象）
#   fields: BacktestConfig + DefaultBacktestEngine 两个类
#   code: zephyr.backtest.implementations.vectorized_engine（__init__.py L16-19）
# - id: I3
#   name: io 回测产物存取符号（函数+数据类）
#   fields: BacktestSinkData/BacktestRunArtifact/ArtifactNotFoundError + save/get/list/build/sink 共8个符号
#   code: zephyr.backtest.io（__init__.py L21-30，#ARCH-047 新增）
# 层: 算法
# - id: A1
#   name_zh: ① 回测域包级再导出聚合
#   name_en: __init__（模块级 import + __all__）
#   intro: 把引擎基类、向量化引擎、io产物函数汇成 zephyr.backtest 统一入口
#   desc: 三组 from-import（L11-30）+ __all__ 18项导出清单（L32-52），含 core/io 等子包名；纯再导出无计算
#   inputs: I1 I2 I3
#   outputs: 统一公共API命名空间
# 层: 输出
# - id: O1
#   name_zh: zephyr.backtest 公共API面
#   name_en: __all__（18项）
#   intro: 对外暴露回测引擎基类/默认引擎/配置/产物存取全套符号
#   downstream: 无下游/内部使用（仓内无 from zephyr.backtest import 直接消费者；services/regime_validation 直接引用子模块，io产物经 backtest_result_sink 供前端 dashboard backtest_results 组件）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
# v1.3.0 新增 io/ 子包（#ARCH-047, 配合前端 Streamlit->Panel+HoloViz 重构）
from zephyr.backtest.io import (
    ArtifactNotFoundError,
    BacktestSinkData,
    BacktestRunArtifact,
    build_artifact_from_data,
    get_artifact,
    list_artifacts,
    save_artifact,
    sink_backtest_result,
)

__all__ = [
    "BacktestEngineBase",
    "BacktestResult",
    "FactorDiscovery",
    "BacktestConfig",
    "DefaultBacktestEngine",
    "core",
    "implementations",
    # v1.3.0 新增（#ARCH-047）
    "io",
    "BacktestSinkData",
    "BacktestRunArtifact",
    "ArtifactNotFoundError",
    "sink_backtest_result",
    "save_artifact",
    "get_artifact",
    "list_artifacts",
    "build_artifact_from_data",
]
