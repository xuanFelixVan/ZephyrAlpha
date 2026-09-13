# [TTL] task_bound
# [MODULE] tests.governance.rule_bridge.xt4_p11_probe
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""xt4_p11_probe.py — P1-1 伪造标记防御实弹验证夹具（红蓝 v4 前置）。

用途：复现红蓝 v3 c224e15d63 攻击向量（伪造 [GW: 标记经网关提交），
验证 FORGED-GW-MARKER gate P1-1 治本后当场拦截 + 堵点本归因。
验证完成后本文件随删除提交清理（task_bound，用后即焚）。
"""

x = 1
