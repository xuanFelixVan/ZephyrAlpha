# [MODULE] zephyr.data.transport
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.transport.cross_border_dual
# [CONSUMERS] 装配层（crypto provider / 执行回传 注入）
# [STARTUP] imported
# [MATURITY] skeleton
# [INVARIANTS] 双线路热切换三感知（失败+吞吐+积压）; 切回纯时间驱动 60s 探测; 积压计数器饱和递减
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §7.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/zephyr/data/transport/test_cross_border_dual.py
# [A_module] module_id=CAND-CRYPTO-009 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""跨境网络双活传输层包（CAND-CRYPTO-009 / 94号 §7.2）。

导出：Cloudflare Tunnel 配置生成 + 双线路热切换状态机。
主线路=HTTPS 直连，备用=Cloudflare Tunnel；控制面走 CF、数据面正常直连、
异常自动降级 CF。
"""

from __future__ import annotations

from typing import Final

from zephyr.data.transport.cross_border_dual import (
    BucketStats,
    CloudflareTunnelSpec,
    CrossBorderDualTransport,
    DualPathConfig,
    SwitchEvent,
    TransportPath,
    render_cloudflared_config,
)

__all__: Final = [
    "BucketStats",
    "CloudflareTunnelSpec",
    "CrossBorderDualTransport",
    "DualPathConfig",
    "SwitchEvent",
    "TransportPath",
    "render_cloudflared_config",
]
